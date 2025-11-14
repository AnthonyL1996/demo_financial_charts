#!/usr/bin/env python3
"""
Model Training Script
Trains XGBoost models from Parquet data files.

Usage:
    python train_from_parquet.py --ticker SPY --timeframe daily --data-dir /data
    python train_from_parquet.py --ticker SPY --timeframe all --data-dir /data
    python train_from_parquet.py --ticker QQQ --timeframe weekly
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb
import joblib
from loguru import logger

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config.config import settings, get_xgboost_params, get_feature_columns, init_directories
from services.feature_engineering import add_all_features, create_labels


def find_parquet_file(data_dir: Path, ticker: str, timeframe: str) -> Optional[Path]:
    """
    Find Parquet file for given ticker and timeframe.

    Args:
        data_dir: Directory containing Parquet files
        ticker: Stock ticker
        timeframe: 'daily' or 'weekly'

    Returns:
        Path to Parquet file or None if not found
    """
    # Look for files matching pattern
    pattern = f"{ticker}_{timeframe}_*.parquet"
    files = list(data_dir.glob(pattern))

    if not files:
        # Try alternative pattern
        pattern = f"{ticker}_*.parquet"
        files = [f for f in data_dir.glob(pattern) if timeframe in f.name.lower()]

    if not files:
        logger.error(f"No Parquet file found for {ticker} ({timeframe}) in {data_dir}")
        logger.info(f"Looking for pattern: {pattern}")
        return None

    # Use the most recent file if multiple found
    if len(files) > 1:
        logger.warning(f"Found {len(files)} files, using most recent")
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    logger.info(f"Found data file: {files[0].name}")
    return files[0]


def load_and_prepare_data(
    filepath: Path,
    feature_columns: List[str],
) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """
    Load Parquet file and prepare data for training.

    Args:
        filepath: Path to Parquet file
        feature_columns: List of feature column names

    Returns:
        Tuple of (DataFrame, X features, y labels)
    """
    logger.info(f"Loading data from {filepath}...")

    # Load Parquet file
    df = pd.read_parquet(filepath)
    logger.info(f"Loaded {len(df)} rows")
    logger.info(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

    # Add technical indicators
    logger.info("Calculating technical indicators...")
    df = add_all_features(df)

    # Create labels (target variable)
    logger.info("Creating target labels...")
    df["target"] = create_labels(df, forward_periods=5, threshold=0.02)

    # Remove rows with NaN in target
    df = df.dropna(subset=["target"])
    logger.info(f"After removing NaN: {len(df)} rows")

    # Verify all features exist
    missing_features = [col for col in feature_columns if col not in df.columns]
    if missing_features:
        raise ValueError(f"Missing features: {missing_features}")

    # Extract features and labels
    X = df[feature_columns].values
    y = df["target"].values

    # Check class distribution
    unique, counts = np.unique(y, return_counts=True)
    class_dist = dict(zip(unique, counts))
    logger.info(f"Class distribution: {class_dist}")

    if len(unique) < 2:
        raise ValueError("Need at least 2 classes for classification")

    # Check for class imbalance
    minority_class = min(counts)
    majority_class = max(counts)
    imbalance_ratio = majority_class / minority_class

    if imbalance_ratio > 3:
        logger.warning(f"Class imbalance detected: {imbalance_ratio:.2f}:1 ratio")
        logger.warning("Consider using scale_pos_weight parameter")

    return df, X, y


def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    params: dict,
) -> Tuple[xgb.XGBClassifier, dict]:
    """
    Train XGBoost model and evaluate performance.

    Args:
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        y_test: Test labels
        params: XGBoost hyperparameters

    Returns:
        Tuple of (trained model, metrics dict)
    """
    logger.info("Training XGBoost model...")
    logger.info(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")

    # Calculate scale_pos_weight for imbalanced data
    unique, counts = np.unique(y_train, return_counts=True)
    if len(unique) == 2:
        scale_pos_weight = counts[0] / counts[1]
        params["scale_pos_weight"] = scale_pos_weight
        logger.info(f"Using scale_pos_weight: {scale_pos_weight:.2f}")

    # Create and train model
    model = xgb.XGBClassifier(**params)

    # Train with early stopping
    eval_set = [(X_train, y_train), (X_test, y_test)]
    model.fit(
        X_train,
        y_train,
        eval_set=eval_set,
        verbose=False,
    )

    # Make predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    # Calculate metrics
    train_accuracy = accuracy_score(y_train, y_train_pred)
    test_accuracy = accuracy_score(y_test, y_test_pred)

    logger.info(f"Training accuracy: {train_accuracy:.4f}")
    logger.info(f"Validation accuracy: {test_accuracy:.4f}")

    # Calculate win rate (for trading context)
    y_test_proba = model.predict_proba(X_test)
    confident_buys = y_test_proba[:, 1] > settings.BUY_THRESHOLD
    if confident_buys.sum() > 0:
        win_rate = y_test[confident_buys].mean()
        logger.info(f"Win rate (confident buys > {settings.BUY_THRESHOLD}): {win_rate:.2%}")
    else:
        win_rate = 0.0
        logger.warning("No confident buy signals generated")

    # Print classification report
    logger.info("\nClassification Report (Test Set):")
    print(classification_report(y_test, y_test_pred, target_names=["Down", "Up"]))

    # Print confusion matrix
    cm = confusion_matrix(y_test, y_test_pred)
    logger.info("\nConfusion Matrix:")
    logger.info(f"                 Predicted Down  Predicted Up")
    logger.info(f"Actual Down      {cm[0][0]:8d}      {cm[0][1]:8d}")
    logger.info(f"Actual Up        {cm[1][0]:8d}      {cm[1][1]:8d}")

    # Calculate Sharpe-like metric (simplified)
    # This is a rough approximation - real Sharpe requires actual returns
    returns = np.where(y_test_pred == 1, 1, -1) * np.where(y_test == 1, 1, -1)
    sharpe = returns.mean() / (returns.std() + 1e-6) * np.sqrt(252)  # Annualized

    logger.info(f"\nApproximate Sharpe Ratio: {sharpe:.2f}")

    metrics = {
        "train_accuracy": train_accuracy,
        "test_accuracy": test_accuracy,
        "win_rate": win_rate,
        "sharpe_approx": sharpe,
        "n_train": len(X_train),
        "n_test": len(X_test),
    }

    return model, metrics


def save_model(
    model: xgb.XGBClassifier,
    ticker: str,
    timeframe: str,
    metrics: dict,
    output_dir: Path,
) -> Path:
    """
    Save trained model to disk.

    Args:
        model: Trained XGBoost model
        ticker: Stock ticker
        timeframe: 'daily' or 'weekly'
        metrics: Performance metrics
        output_dir: Directory to save model

    Returns:
        Path to saved model
    """
    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"xgboost_{timeframe}_{ticker.lower()}_{settings.MODEL_VERSION}_{timestamp}.pkl"
    filepath = output_dir / filename

    # Save model
    model_data = {
        "model": model,
        "ticker": ticker,
        "timeframe": timeframe,
        "metrics": metrics,
        "feature_columns": get_feature_columns(),
        "version": settings.MODEL_VERSION,
        "trained_at": datetime.now().isoformat(),
        "config": {
            "buy_threshold": settings.BUY_THRESHOLD,
            "sell_threshold": settings.SELL_THRESHOLD,
        },
    }

    joblib.dump(model_data, filepath)
    logger.success(f"Model saved to: {filepath}")

    # Also save to 'current' directory for easy access
    current_dir = output_dir / "current"
    current_dir.mkdir(exist_ok=True)
    current_filename = f"xgboost_{timeframe}_{ticker.lower()}.pkl"
    current_filepath = current_dir / current_filename
    joblib.dump(model_data, current_filepath)
    logger.info(f"Model also saved to: {current_filepath}")

    return filepath


def cross_validate_model(X: np.ndarray, y: np.ndarray, params: dict, cv: int = 5) -> None:
    """
    Perform cross-validation to assess model stability.

    Args:
        X: Features
        y: Labels
        params: Model parameters
        cv: Number of cross-validation folds
    """
    logger.info(f"\nPerforming {cv}-fold cross-validation...")

    model = xgb.XGBClassifier(**params)
    scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")

    logger.info(f"CV Accuracy: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
    logger.info(f"Individual fold scores: {scores}")

    if scores.std() > 0.1:
        logger.warning("High variance in CV scores - model may be unstable")


def print_training_summary(results: dict) -> None:
    """Print formatted training summary."""
    logger.info("\n" + "=" * 60)
    logger.info("📊 TRAINING SUMMARY")
    logger.info("=" * 60)

    for timeframe, data in results.items():
        if data["success"]:
            metrics = data["metrics"]
            logger.info(f"\n{timeframe.upper()}:")
            logger.info(f"  ✅ Training completed successfully")
            logger.info(f"  📈 Validation Accuracy: {metrics['test_accuracy']:.2%}")
            logger.info(f"  📊 Win Rate: {metrics['win_rate']:.2%}")
            logger.info(f"  📉 Approx Sharpe: {metrics['sharpe_approx']:.2f}")
            logger.info(f"  💾 Model saved: {data['model_path'].name}")
        else:
            logger.error(f"\n{timeframe.upper()}:")
            logger.error(f"  ❌ Training failed: {data.get('error', 'Unknown error')}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Train ML models from Parquet data")

    parser.add_argument(
        "--ticker",
        type=str,
        required=True,
        help="Stock ticker (e.g., SPY, AAPL)",
    )
    parser.add_argument(
        "--timeframe",
        type=str,
        required=True,
        choices=["daily", "weekly", "monthly", "all"],
        help="Timeframe to train (or 'all' for daily+weekly)",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=str(settings.DATA_DIR),
        help=f"Directory containing Parquet files (default: {settings.DATA_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(settings.MODELS_DIR),
        help=f"Directory to save models (default: {settings.MODELS_DIR})",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Test set size (default: 0.2)",
    )
    parser.add_argument(
        "--cross-validate",
        action="store_true",
        help="Perform cross-validation",
    )

    args = parser.parse_args()

    # Initialize directories
    init_directories()
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)

    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        sys.exit(1)

    ticker = args.ticker.upper()
    logger.info(f"\n{'=' * 60}")
    logger.info(f"Training ML Model for {ticker}")
    logger.info(f"{'=' * 60}")

    # Get feature columns
    feature_columns = get_feature_columns()
    logger.info(f"Using {len(feature_columns)} features")

    # Determine timeframes to train
    if args.timeframe == "all":
        timeframes = ["daily", "weekly"]
    else:
        timeframes = [args.timeframe]

    # Train each timeframe
    results = {}
    for timeframe in timeframes:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Training {timeframe.upper()} model")
        logger.info(f"{'=' * 60}")

        try:
            # Find data file
            filepath = find_parquet_file(data_dir, ticker, timeframe)
            if filepath is None:
                results[timeframe] = {"success": False, "error": "Data file not found"}
                continue

            # Load and prepare data
            df, X, y = load_and_prepare_data(filepath, feature_columns)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=args.test_size,
                random_state=settings.RANDOM_STATE,
                stratify=y,
            )

            # Get model parameters
            params = get_xgboost_params()

            # Perform cross-validation if requested
            if args.cross_validate:
                cross_validate_model(X, y, params)

            # Train model
            model, metrics = train_model(X_train, y_train, X_test, y_test, params)

            # Save model
            model_path = save_model(model, ticker, timeframe, metrics, output_dir)

            results[timeframe] = {
                "success": True,
                "metrics": metrics,
                "model_path": model_path,
            }

        except Exception as e:
            logger.error(f"Error training {timeframe} model: {str(e)}")
            logger.exception(e)
            results[timeframe] = {"success": False, "error": str(e)}

    # Print summary
    print_training_summary(results)

    # Exit with error if any training failed
    if not all(r["success"] for r in results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
