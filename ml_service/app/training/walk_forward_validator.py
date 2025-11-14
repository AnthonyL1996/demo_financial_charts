"""
Walk-forward validation for time-series ML models
"""
import pandas as pd
import numpy as np
import xgboost as xgb
from typing import Generator, Dict, Any, List, Literal
import logging
from datetime import datetime

from app.utils.metrics import calculate_metrics, calculate_trading_metrics, calculate_summary_stats
from app.features.technical_features import TechnicalFeatureEngineer
from app.training.label_generator import LabelGenerator
from app.training.data_loader import DataLoader
from config.config import config

logger = logging.getLogger(__name__)


class RollingWalkForward:
    """
    Rolling window walk-forward validation
    Train window is FIXED size and ROLLS forward
    """

    def __init__(self, train_window_years: int = 5, test_window_years: int = 1):
        """
        Initialize rolling walk-forward splitter

        Args:
            train_window_years: Size of training window in years
            test_window_years: Size of test window in years
        """
        self.train_window = train_window_years
        self.test_window = test_window_years

    def split(
        self,
        data: pd.DataFrame,
        start_year: int = 2015,
        end_year: int = 2024
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Generate train/test splits

        Args:
            data: DataFrame with 'year' column
            start_year: First year of data
            end_year: Last year of data

        Yields:
            Dictionary with train/test splits and metadata
        """
        first_test_year = start_year + self.train_window

        for test_year in range(first_test_year, end_year + 1):
            train_start = test_year - self.train_window
            train_end = test_year - 1

            train_data = data[
                (data['year'] >= train_start) &
                (data['year'] <= train_end)
            ].copy()

            test_data = data[data['year'] == test_year].copy()

            if len(train_data) == 0 or len(test_data) == 0:
                logger.warning(f"Skipping year {test_year}: insufficient data")
                continue

            yield {
                'train': train_data,
                'test': test_data,
                'test_year': test_year,
                'train_period': f"{train_start}-{train_end}",
                'train_start': train_start,
                'train_end': train_end
            }


class AnchoredWalkForward:
    """
    Anchored walk-forward validation
    Train window GROWS over time (anchored to start date)
    """

    def __init__(self, anchor_year: int = 2015):
        """
        Initialize anchored walk-forward splitter

        Args:
            anchor_year: Year to anchor training window to
        """
        self.anchor = anchor_year

    def split(
        self,
        data: pd.DataFrame,
        test_years: List[int]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Generate train/test splits

        Args:
            data: DataFrame with 'year' column
            test_years: List of years to test on

        Yields:
            Dictionary with train/test splits and metadata
        """
        for test_year in test_years:
            train_data = data[
                (data['year'] >= self.anchor) &
                (data['year'] < test_year)
            ].copy()

            test_data = data[data['year'] == test_year].copy()

            if len(train_data) == 0 or len(test_data) == 0:
                logger.warning(f"Skipping year {test_year}: insufficient data")
                continue

            yield {
                'train': train_data,
                'test': test_data,
                'test_year': test_year,
                'train_period': f"{self.anchor}-{test_year-1}",
                'train_start': self.anchor,
                'train_end': test_year - 1
            }


class WalkForwardValidator:
    """
    Complete walk-forward validation pipeline
    """

    def __init__(self):
        """Initialize validator with all required components"""
        self.data_loader = DataLoader()
        self.feature_engineer = TechnicalFeatureEngineer()
        self.label_generator = LabelGenerator()

        logger.info("WalkForwardValidator initialized")

    def run_validation(
        self,
        ticker: str,
        timeframe: Literal['daily', 'weekly', 'monthly'] = 'daily',
        validation_type: Literal['rolling', 'anchored', 'both'] = 'rolling',
        start_year: int = 2015,
        end_year: int = 2024
    ) -> Dict[str, Any]:
        """
        Run complete walk-forward validation

        Args:
            ticker: Stock ticker symbol
            timeframe: Data timeframe
            validation_type: Type of validation (rolling, anchored, or both)
            start_year: Start year for data
            end_year: End year for data

        Returns:
            Dictionary with validation results
        """
        logger.info("="*70)
        logger.info(f"WALK-FORWARD VALIDATION: {ticker} ({timeframe})")
        logger.info("="*70)

        # 1. Load and prepare data
        dataset = self._prepare_dataset(ticker, timeframe)

        if dataset.empty:
            logger.error(f"Failed to prepare dataset for {ticker}")
            return {'error': 'Dataset preparation failed'}

        # 2. Run validation based on type
        results = {}

        if validation_type in ['rolling', 'both']:
            logger.info("\n" + "="*70)
            logger.info("ROLLING WINDOW VALIDATION")
            logger.info("="*70)
            results['rolling'] = self._run_rolling_validation(
                dataset, start_year, end_year, timeframe
            )

        if validation_type in ['anchored', 'both']:
            logger.info("\n" + "="*70)
            logger.info("ANCHORED WINDOW VALIDATION")
            logger.info("="*70)
            results['anchored'] = self._run_anchored_validation(
                dataset, start_year, end_year, timeframe
            )

        # 3. Print summary
        self._print_validation_summary(results, validation_type)

        return results

    def _prepare_dataset(
        self,
        ticker: str,
        timeframe: Literal['daily', 'weekly', 'monthly']
    ) -> pd.DataFrame:
        """
        Load data, engineer features, generate labels

        Args:
            ticker: Stock ticker
            timeframe: Data timeframe

        Returns:
            Complete dataset ready for training
        """
        logger.info(f"Preparing dataset for {ticker} ({timeframe})...")

        # Load raw data
        raw_data = self.data_loader.load_data(ticker, timeframe)

        if raw_data.empty:
            logger.error(f"No data loaded for {ticker}")
            return pd.DataFrame()

        # Generate technical features
        data_with_features = self.feature_engineer.create_features(raw_data)

        if data_with_features.empty:
            logger.error("Feature generation failed")
            return pd.DataFrame()

        # Generate labels
        dataset = self.label_generator.create_labels(data_with_features, timeframe)

        if dataset.empty:
            logger.error("Label generation failed")
            return pd.DataFrame()

        logger.info(f"Dataset prepared: {len(dataset)} samples")
        return dataset

    def _run_rolling_validation(
        self,
        dataset: pd.DataFrame,
        start_year: int,
        end_year: int,
        timeframe: str
    ) -> Dict[str, Any]:
        """Run rolling window validation"""
        rolling = RollingWalkForward(
            train_window_years=config.training.train_window_years,
            test_window_years=config.training.validation_window_years
        )

        fold_results = []

        for fold in rolling.split(dataset, start_year, end_year):
            result = self._train_and_evaluate_fold(fold, timeframe)
            fold_results.append(result)
            self._print_fold_result(result)

        summary = calculate_summary_stats(fold_results)

        return {
            'folds': fold_results,
            'summary': summary,
            'passed': summary.get('avg_sharpe_ratio', 0) > 0.5
        }

    def _run_anchored_validation(
        self,
        dataset: pd.DataFrame,
        start_year: int,
        end_year: int,
        timeframe: str
    ) -> Dict[str, Any]:
        """Run anchored window validation"""
        test_years = range(start_year + config.training.train_window_years, end_year + 1)

        anchored = AnchoredWalkForward(anchor_year=start_year)

        fold_results = []

        for fold in anchored.split(dataset, test_years):
            result = self._train_and_evaluate_fold(fold, timeframe)
            fold_results.append(result)
            self._print_fold_result(result)

        summary = calculate_summary_stats(fold_results)

        return {
            'folds': fold_results,
            'summary': summary,
            'passed': summary.get('avg_sharpe_ratio', 0) > 0.5
        }

    def _train_and_evaluate_fold(
        self,
        fold: Dict[str, Any],
        timeframe: str
    ) -> Dict[str, Any]:
        """
        Train model and evaluate on a single fold

        Args:
            fold: Dictionary with train/test data
            timeframe: Data timeframe

        Returns:
            Dictionary with fold results
        """
        # Get feature columns
        feature_cols = self.feature_engineer.get_feature_names(fold['train'])

        # Separate features and labels
        X_train = fold['train'][feature_cols].values
        y_train = fold['train']['label'].values

        X_test = fold['test'][feature_cols].values
        y_test = fold['test']['label'].values

        # Train XGBoost model
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

        # ML Metrics
        ml_metrics = calculate_metrics(y_test, y_pred, y_pred_proba)

        # Trading Metrics
        actual_returns = fold['test']['forward_return'].values
        trading_metrics = calculate_trading_metrics(
            predictions=y_pred,
            probabilities=y_pred_proba,
            actual_returns=actual_returns,
            confidence_threshold=config.backtest.confidence_threshold,
            initial_capital=config.backtest.initial_capital
        )

        # Feature importance
        feature_importance = self.feature_engineer.get_feature_importance_dict(
            model, feature_cols
        )
        top_features = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            'test_year': fold['test_year'],
            'train_period': fold['train_period'],
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            **ml_metrics,
            **trading_metrics,
            'top_features': top_features
        }

    def _print_fold_result(self, result: Dict[str, Any]):
        """Print results for a single fold"""
        logger.info(
            f"\n{result['test_year']}: Train[{result['train_period']}] "
            f"({result['train_samples']} samples) → Test ({result['test_samples']} samples)"
        )
        logger.info(
            f"  ML Metrics: Accuracy={result['accuracy']:.3f} | "
            f"Precision={result['precision']:.3f} | "
            f"Recall={result['recall']:.3f} | "
            f"AUC={result['auc']:.3f}"
        )
        logger.info(
            f"  Trading:    Return={result['total_return']:>6.1f}% | "
            f"Sharpe={result['sharpe_ratio']:>5.2f} | "
            f"Drawdown={result['max_drawdown']:>6.1f}% | "
            f"Win Rate={result['win_rate']:>5.1f}%"
        )
        logger.info(
            f"  Trades:     {result['num_trades']} trades | "
            f"Avg Win={result['avg_win']:.2f}% | "
            f"Avg Loss={result['avg_loss']:.2f}%"
        )

    def _print_validation_summary(
        self,
        results: Dict[str, Any],
        validation_type: str
    ):
        """Print overall validation summary"""
        logger.info("\n" + "="*70)
        logger.info("VALIDATION SUMMARY")
        logger.info("="*70)

        for vtype in ['rolling', 'anchored']:
            if vtype not in results:
                continue

            summary = results[vtype]['summary']

            logger.info(f"\n{vtype.upper()} WINDOW:")
            logger.info(f"  Folds: {summary.get('num_folds', 0)}")
            logger.info(
                f"  ML Performance: "
                f"Accuracy={summary.get('avg_accuracy', 0):.3f} ± {summary.get('std_accuracy', 0):.3f} | "
                f"Precision={summary.get('avg_precision', 0):.3f} | "
                f"AUC={summary.get('avg_auc', 0):.3f}"
            )
            logger.info(
                f"  Trading:        "
                f"Avg Return={summary.get('avg_total_return', 0):.1f}% | "
                f"Sharpe={summary.get('avg_sharpe_ratio', 0):.2f} | "
                f"Win Rate={summary.get('avg_win_rate', 0):.1f}%"
            )

            if 'best_fold' in summary and 'worst_fold' in summary:
                logger.info(
                    f"  Best Year:      {summary['best_fold']['test_year']} "
                    f"({summary['best_fold']['total_return']:.1f}%)"
                )
                logger.info(
                    f"  Worst Year:     {summary['worst_fold']['test_year']} "
                    f"({summary['worst_fold']['total_return']:.1f}%)"
                )
                logger.info(
                    f"  Consistency:    {summary.get('consistency', 0):.1f}% "
                    f"(profitable years)"
                )

            # Pass/fail
            passed = results[vtype]['passed']
            status = "✅ PASSED" if passed else "❌ FAILED"
            logger.info(f"  Status: {status} (Sharpe > 0.5)")

    def train_final_model(
        self,
        ticker: str,
        timeframe: Literal['daily', 'weekly', 'monthly'],
        train_end_year: int = 2023
    ) -> xgb.XGBClassifier:
        """
        Train final production model using all data up to train_end_year

        Args:
            ticker: Stock ticker
            timeframe: Data timeframe
            train_end_year: Last year to include in training

        Returns:
            Trained XGBoost model
        """
        logger.info("="*70)
        logger.info(f"TRAINING FINAL MODEL: {ticker} ({timeframe})")
        logger.info("="*70)

        # Prepare dataset
        dataset = self._prepare_dataset(ticker, timeframe)

        if dataset.empty:
            raise ValueError(f"Failed to prepare dataset for {ticker}")

        # Use all data up to train_end_year
        train_data = dataset[dataset['year'] <= train_end_year]

        logger.info(f"Training on {len(train_data)} samples (up to {train_end_year})")

        # Get features
        feature_cols = self.feature_engineer.get_feature_names(train_data)

        X_train = train_data[feature_cols].values
        y_train = train_data['label'].values

        # Train model
        model = xgb.XGBClassifier(**config.model.to_dict())

        model.fit(X_train, y_train, verbose=True)

        logger.info("Final model trained successfully")

        # Print top features
        feature_importance = self.feature_engineer.get_feature_importance_dict(
            model, feature_cols
        )
        top_features = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        logger.info("\nTop 10 Features:")
        for i, (feature, importance) in enumerate(top_features, 1):
            logger.info(f"  {i}. {feature}: {importance:.4f}")

        return model
