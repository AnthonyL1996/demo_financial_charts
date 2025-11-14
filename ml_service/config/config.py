"""
ML Service Configuration
Contains all configuration parameters for training, data ingestion, and model serving.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with validation."""

    # Directories
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = BASE_DIR / "models"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # API Settings
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=5000, env="API_PORT")
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Model Training Parameters
    TRAIN_TEST_SPLIT: float = 0.8
    RANDOM_STATE: int = 42
    N_ESTIMATORS: int = 200
    MAX_DEPTH: int = 6
    LEARNING_RATE: float = 0.1
    MIN_CHILD_WEIGHT: int = 1
    SUBSAMPLE: float = 0.8
    COLSAMPLE_BYTREE: float = 0.8
    GAMMA: float = 0.0
    REG_ALPHA: float = 0.0
    REG_LAMBDA: float = 1.0

    # Feature Engineering
    SMA_PERIODS: List[int] = [20, 50, 200]
    EMA_PERIODS: List[int] = [12, 26]
    RSI_PERIOD: int = 14
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    BB_PERIOD: int = 20
    BB_STD: float = 2.0
    ATR_PERIOD: int = 14

    # Data Ingestion
    DEFAULT_START_DATE: str = "2020-01-01"
    DEFAULT_END_DATE: str = "2024-11-14"
    DATA_INTERVAL: str = "1d"  # 1d, 1wk, 1mo

    # Prediction Thresholds
    BUY_THRESHOLD: float = 0.6
    SELL_THRESHOLD: float = 0.6
    MIN_CONFIDENCE: float = 0.5

    # Model Versioning
    MODEL_VERSION: str = "v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Model hyperparameters dictionary
def get_xgboost_params() -> Dict[str, Any]:
    """Get XGBoost hyperparameters."""
    return {
        "n_estimators": settings.N_ESTIMATORS,
        "max_depth": settings.MAX_DEPTH,
        "learning_rate": settings.LEARNING_RATE,
        "min_child_weight": settings.MIN_CHILD_WEIGHT,
        "subsample": settings.SUBSAMPLE,
        "colsample_bytree": settings.COLSAMPLE_BYTREE,
        "gamma": settings.GAMMA,
        "reg_alpha": settings.REG_ALPHA,
        "reg_lambda": settings.REG_LAMBDA,
        "random_state": settings.RANDOM_STATE,
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "tree_method": "hist",
        "verbosity": 1,
    }


# Feature list
def get_feature_columns() -> List[str]:
    """Get list of feature columns for model training."""
    features = []

    # Moving averages
    for period in settings.SMA_PERIODS:
        features.append(f"sma_{period}")

    for period in settings.EMA_PERIODS:
        features.append(f"ema_{period}")

    # Technical indicators
    features.extend(
        [
            f"rsi_{settings.RSI_PERIOD}",
            "macd",
            "macd_signal",
            "macd_diff",
            f"bb_upper_{settings.BB_PERIOD}",
            f"bb_middle_{settings.BB_PERIOD}",
            f"bb_lower_{settings.BB_PERIOD}",
            "bb_width",
            f"atr_{settings.ATR_PERIOD}",
            "volume_sma_20",
            "volume_ratio",
        ]
    )

    # Price-based features
    features.extend(
        [
            "returns",
            "log_returns",
            "high_low_range",
            "close_open_ratio",
        ]
    )

    return features


# Ensure directories exist
def init_directories():
    """Create necessary directories if they don't exist."""
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    (settings.MODELS_DIR / "current").mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # Test configuration
    print("ML Service Configuration")
    print("=" * 50)
    print(f"Base Directory: {settings.BASE_DIR}")
    print(f"Data Directory: {settings.DATA_DIR}")
    print(f"Models Directory: {settings.MODELS_DIR}")
    print(f"API Host: {settings.API_HOST}:{settings.API_PORT}")
    print(f"\nXGBoost Parameters:")
    for key, value in get_xgboost_params().items():
        print(f"  {key}: {value}")
    print(f"\nFeatures ({len(get_feature_columns())}):")
    for feature in get_feature_columns():
        print(f"  - {feature}")
