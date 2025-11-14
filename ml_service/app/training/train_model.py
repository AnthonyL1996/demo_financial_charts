"""
Model training script

Train XGBoost models for all timeframes
"""
import argparse
import logging
import sys
from pathlib import Path
import joblib
from datetime import datetime

from app.training.walk_forward_validator import WalkForwardValidator
from config.config import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'training_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)


def train_and_validate_model(
    ticker: str,
    timeframe: str,
    validate: bool = True,
    save_model: bool = True
):
    """
    Train and optionally validate a model for a specific timeframe

    Args:
        ticker: Stock ticker symbol
        timeframe: Timeframe (daily, weekly, monthly)
        validate: Whether to run walk-forward validation
        save_model: Whether to save the final model

    Returns:
        Validation results (if validate=True) or trained model
    """
    validator = WalkForwardValidator()

    # Run walk-forward validation
    if validate:
        logger.info(f"\n{'='*80}")
        logger.info(f"VALIDATING MODEL: {ticker} - {timeframe.upper()}")
        logger.info(f"{'='*80}\n")

        results = validator.run_validation(
            ticker=ticker,
            timeframe=timeframe,
            validation_type='both',  # Both rolling and anchored
            start_year=2015,
            end_year=2024
        )

        # Check if validation passed
        rolling_passed = results.get('rolling', {}).get('passed', False)
        anchored_passed = results.get('anchored', {}).get('passed', False)

        if not rolling_passed and not anchored_passed:
            logger.warning(
                f"⚠️  Model for {timeframe} failed validation (Sharpe < 0.5). "
                f"Consider tuning hyperparameters or features."
            )

        # Print decision
        logger.info(f"\n{'='*80}")
        if rolling_passed or anchored_passed:
            logger.info(f"✅ VALIDATION PASSED for {timeframe}")
        else:
            logger.info(f"❌ VALIDATION FAILED for {timeframe}")
        logger.info(f"{'='*80}\n")

    # Train final model
    if save_model:
        logger.info(f"\n{'='*80}")
        logger.info(f"TRAINING FINAL MODEL: {ticker} - {timeframe.upper()}")
        logger.info(f"{'='*80}\n")

        final_model = validator.train_final_model(
            ticker=ticker,
            timeframe=timeframe,
            train_end_year=2023  # Use all data up to 2023 for final model
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


def train_all_timeframes(ticker: str = "SPY", validate: bool = True):
    """
    Train models for all timeframes

    Args:
        ticker: Stock ticker symbol
        validate: Whether to run validation
    """
    logger.info(f"\n{'#'*80}")
    logger.info(f"# TRAINING ALL TIMEFRAME MODELS FOR {ticker}")
    logger.info(f"{'#'*80}\n")

    timeframes = ['daily', 'weekly', 'monthly']
    results = {}

    for timeframe in timeframes:
        try:
            result = train_and_validate_model(
                ticker=ticker,
                timeframe=timeframe,
                validate=validate,
                save_model=True
            )
            results[timeframe] = result

        except Exception as e:
            logger.error(f"Failed to train {timeframe} model: {e}", exc_info=True)
            results[timeframe] = {'error': str(e)}

    # Final summary
    logger.info(f"\n{'#'*80}")
    logger.info(f"# TRAINING COMPLETE")
    logger.info(f"{'#'*80}\n")

    for timeframe, result in results.items():
        if isinstance(result, dict) and 'error' in result:
            logger.info(f"  {timeframe.upper()}: ❌ FAILED - {result['error']}")
        else:
            logger.info(f"  {timeframe.upper()}: ✅ SUCCESS")

    return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Train XGBoost stock prediction models')

    parser.add_argument(
        '--ticker',
        type=str,
        default='SPY',
        help='Stock ticker symbol (default: SPY)'
    )

    parser.add_argument(
        '--timeframe',
        type=str,
        choices=['daily', 'weekly', 'monthly', 'all'],
        default='all',
        help='Timeframe to train (default: all)'
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

    # Train models
    if args.timeframe == 'all':
        train_all_timeframes(
            ticker=args.ticker,
            validate=not args.no_validate
        )
    else:
        train_and_validate_model(
            ticker=args.ticker,
            timeframe=args.timeframe,
            validate=not args.no_validate,
            save_model=not args.no_save
        )


if __name__ == '__main__':
    main()
