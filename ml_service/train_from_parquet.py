#!/usr/bin/env python
"""
Training script for XGBoost models using Parquet data files

Usage:
    python train_from_parquet.py --ticker SPY --timeframe daily --data-dir /path/to/parquet
    python train_from_parquet.py --ticker QQQ --timeframe weekly --data-dir /path/to/parquet
    python train_from_parquet.py --ticker ORCL --timeframe all --data-dir /path/to/parquet
"""
import argparse
import logging
import sys
from pathlib import Path
import joblib
from datetime import datetime

# Add ml_service to path
sys.path.insert(0, str(Path(__file__).parent))

from app.training.parquet_data_loader import ParquetDataLoader
from app.features.technical_features import TechnicalFeatureEngineer
from app.training.label_generator import LabelGenerator
from app.training.walk_forward_validator import WalkForwardValidator, RollingWalkForward
from config.config import config
import xgboost as xgb
import pandas as pd
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'training_parquet_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)


def train_and_validate_model(
    ticker: str,
    timeframe: str,
    data_dir: str,
    validate: bool = True,
    save_model: bool = True
):
    """
    Train and validate model using Parquet data

    Args:
        ticker: Stock ticker symbol
        timeframe: Timeframe (daily, weekly)
        data_dir: Directory containing Parquet files
        validate: Whether to run walk-forward validation
        save_model: Whether to save the final model
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"TRAINING MODEL: {ticker} - {timeframe.upper()}")
    logger.info(f"Data source: Parquet files in {data_dir}")
    logger.info(f"{'='*80}\n")

    # Initialize components
    data_loader = ParquetDataLoader(data_dir=data_dir)
    feature_engineer = TechnicalFeatureEngineer()
    label_generator = LabelGenerator()

    # Load data
    logger.info(f"Loading {timeframe} data for {ticker}...")
    raw_data = data_loader.load_data(
        ticker=ticker,
        timeframe=timeframe,
        start_date=config.training.start_date,
        end_date=config.training.end_date
    )

    if raw_data.empty:
        logger.error(f"No data loaded for {ticker}")
        return None

    logger.info(f"Loaded {len(raw_data)} rows")
    logger.info(f"Date range: {raw_data['date'].min()} to {raw_data['date'].max()}")

    # Feature engineering
    logger.info("Generating technical features...")
    data_with_features = feature_engineer.create_features(raw_data)

    if data_with_features.empty:
        logger.error("Feature generation failed")
        return None

    logger.info(f"Features generated: {len(data_with_features)} rows")

    # Label generation
    logger.info("Generating labels...")
    dataset = label_generator.create_labels(data_with_features, timeframe)

    if dataset.empty:
        logger.error("Label generation failed")
        return None

    logger.info(f"Dataset ready: {len(dataset)} samples")

    # Validation
    if validate:
        logger.info(f"\n{'='*80}")
        logger.info("WALK-FORWARD VALIDATION")
        logger.info(f"{'='*80}\n")

        results = run_walk_forward_validation(
            dataset=dataset,
            feature_engineer=feature_engineer,
            timeframe=timeframe
        )

        # Check if passed
        rolling_passed = results['summary'].get('avg_sharpe_ratio', 0) > 0.5

        logger.info(f"\n{'='*80}")
        if rolling_passed:
            logger.info(f"✅ VALIDATION PASSED for {timeframe}")
        else:
            logger.info(f"❌ VALIDATION FAILED for {timeframe}")
            logger.warning("Model Sharpe ratio < 0.5. Consider tuning hyperparameters.")
        logger.info(f"{'='*80}\n")

    # Train final model
    if save_model:
        logger.info(f"\n{'='*80}")
        logger.info(f"TRAINING FINAL MODEL")
        logger.info(f"{'='*80}\n")

        final_model = train_final_model(
            dataset=dataset,
            feature_engineer=feature_engineer,
            timeframe=timeframe,
            ticker=ticker
        )

        # Save model
        model_dir = Path(config.api.model_path)
        model_dir.mkdir(parents=True, exist_ok=True)

        model_filename = f"xgboost_{timeframe}_{ticker.lower()}_v1.pkl"
        model_path = model_dir / model_filename

        joblib.dump(final_model, model_path)
        logger.info(f"✅ Model saved to: {model_path}")

        return final_model

    return results if validate else None


def run_walk_forward_validation(
    dataset: pd.DataFrame,
    feature_engineer: TechnicalFeatureEngineer,
    timeframe: str
) -> dict:
    """
    Run rolling window walk-forward validation

    Args:
        dataset: Prepared dataset with features and labels
        feature_engineer: Feature engineer instance
        timeframe: Timeframe string

    Returns:
        Validation results
    """
    # Determine date range from data
    min_year = dataset['year'].min()
    max_year = dataset['year'].max()

    logger.info(f"Data range: {min_year}-{max_year}")

    # Adjust validation parameters based on available data
    available_years = max_year - min_year
    train_window = min(config.training.train_window_years, available_years - 1)

    logger.info(f"Using {train_window}-year training window")

    rolling = RollingWalkForward(train_window_years=train_window)

    fold_results = []
    feature_cols = feature_engineer.get_feature_names(dataset)

    first_test_year = min_year + train_window

    for fold in rolling.split(dataset, start_year=min_year, end_year=max_year):
        logger.info(f"\nFold: Train[{fold['train_period']}] → Test[{fold['test_year']}]")

        # Separate features and labels
        X_train = fold['train'][feature_cols].values
        y_train = fold['train']['label'].values

        X_test = fold['test'][feature_cols].values
        y_test = fold['test']['label'].values

        # Train model
        model = xgb.XGBClassifier(**config.model.to_dict())

        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            early_stopping_rounds=config.model.early_stopping_rounds,
            verbose=False
        )

        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]

        # Calculate metrics
        from app.utils.metrics import calculate_metrics, calculate_trading_metrics

        ml_metrics = calculate_metrics(y_test, y_pred, y_pred_proba)

        actual_returns = fold['test']['forward_return'].values
        trading_metrics = calculate_trading_metrics(
            predictions=y_pred,
            probabilities=y_pred_proba,
            actual_returns=actual_returns,
            confidence_threshold=config.backtest.confidence_threshold,
            initial_capital=config.backtest.initial_capital
        )

        # Feature importance
        feature_importance = feature_engineer.get_feature_importance_dict(model, feature_cols)
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]

        fold_result = {
            'test_year': fold['test_year'],
            'train_period': fold['train_period'],
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            **ml_metrics,
            **trading_metrics,
            'top_features': top_features
        }

        fold_results.append(fold_result)

        # Print fold summary
        logger.info(
            f"  ML: Acc={ml_metrics['accuracy']:.3f} | "
            f"Prec={ml_metrics['precision']:.3f} | "
            f"AUC={ml_metrics['auc']:.3f}"
        )
        logger.info(
            f"  Trading: Return={trading_metrics['total_return']:>6.1f}% | "
            f"Sharpe={trading_metrics['sharpe_ratio']:>5.2f} | "
            f"Win Rate={trading_metrics['win_rate']:>5.1f}%"
        )

    # Summary
    from app.utils.metrics import calculate_summary_stats

    summary = calculate_summary_stats(fold_results)

    logger.info(f"\n{'='*80}")
    logger.info("VALIDATION SUMMARY")
    logger.info(f"{'='*80}")
    logger.info(f"Folds: {summary['num_folds']}")
    logger.info(f"ML: Accuracy={summary['avg_accuracy']:.3f} ± {summary['std_accuracy']:.3f}")
    logger.info(f"Trading: Avg Return={summary['avg_total_return']:.1f}% | Sharpe={summary['avg_sharpe_ratio']:.2f}")
    logger.info(f"Best Year: {summary['best_fold']['test_year']} ({summary['best_fold']['total_return']:.1f}%)")
    logger.info(f"Worst Year: {summary['worst_fold']['test_year']} ({summary['worst_fold']['total_return']:.1f}%)")

    return {'folds': fold_results, 'summary': summary}


def train_final_model(
    dataset: pd.DataFrame,
    feature_engineer: TechnicalFeatureEngineer,
    timeframe: str,
    ticker: str
) -> xgb.XGBClassifier:
    """
    Train final production model

    Args:
        dataset: Prepared dataset
        feature_engineer: Feature engineer
        timeframe: Timeframe
        ticker: Ticker symbol

    Returns:
        Trained model
    """
    # Use all data up to 2023 for training
    train_data = dataset[dataset['year'] <= 2023]

    logger.info(f"Training on {len(train_data)} samples (up to 2023)")

    # Get features
    feature_cols = feature_engineer.get_feature_names(train_data)

    X_train = train_data[feature_cols].values
    y_train = train_data['label'].values

    # Train model
    model = xgb.XGBClassifier(**config.model.to_dict())
    model.fit(X_train, y_train, verbose=True)

    # Feature importance
    feature_importance = feature_engineer.get_feature_importance_dict(model, feature_cols)
    top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]

    logger.info("\nTop 10 Features:")
    for i, (feature, importance) in enumerate(top_features, 1):
        logger.info(f"  {i}. {feature}: {importance:.4f}")

    return model


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Train XGBoost models from Parquet data')

    parser.add_argument(
        '--ticker',
        type=str,
        default='SPY',
        help='Stock ticker symbol (default: SPY)'
    )

    parser.add_argument(
        '--timeframe',
        type=str,
        choices=['daily', 'weekly', 'all'],
        default='all',
        help='Timeframe to train (default: all)'
    )

    parser.add_argument(
        '--data-dir',
        type=str,
        required=True,
        help='Directory containing Parquet files'
    )

    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip walk-forward validation'
    )

    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save final model'
    )

    args = parser.parse_args()

    # Verify data directory exists
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return 1

    # Train models
    if args.timeframe == 'all':
        for timeframe in ['daily', 'weekly']:
            try:
                train_and_validate_model(
                    ticker=args.ticker,
                    timeframe=timeframe,
                    data_dir=str(data_dir),
                    validate=not args.no_validate,
                    save_model=not args.no_save
                )
            except Exception as e:
                logger.error(f"Failed to train {timeframe} model: {e}", exc_info=True)

    else:
        train_and_validate_model(
            ticker=args.ticker,
            timeframe=args.timeframe,
            data_dir=str(data_dir),
            validate=not args.no_validate,
            save_model=not args.no_save
        )

    logger.info("\n✅ Training complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
