"""
Configuration for ML Service
"""
import os
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    database: str = os.getenv("DB_NAME", "jdb_trading")
    user: str = os.getenv("DB_USER", "jdb")
    password: str = os.getenv("DB_PASSWORD", "password")

    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class ModelConfig:
    """XGBoost model hyperparameters"""
    n_estimators: int = 200
    max_depth: int = 6
    learning_rate: float = 0.05
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    objective: str = 'binary:logistic'
    eval_metric: str = 'logloss'
    early_stopping_rounds: int = 20
    random_state: int = 42

    def to_dict(self) -> Dict[str, Any]:
        return {
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'learning_rate': self.learning_rate,
            'subsample': self.subsample,
            'colsample_bytree': self.colsample_bytree,
            'objective': self.objective,
            'eval_metric': self.eval_metric,
            'random_state': self.random_state
        }


@dataclass
class TrainingConfig:
    """Training pipeline configuration"""
    # Data settings
    start_date: str = "2015-01-01"
    end_date: str = "2024-12-31"
    min_samples: int = 200

    # Walk-forward validation
    train_window_years: int = 5
    validation_window_years: int = 1

    # Label generation
    daily_horizon_days: int = 30
    daily_threshold: float = 0.05  # 5% return

    weekly_horizon_days: int = 60
    weekly_threshold: float = 0.10  # 10% return

    monthly_horizon_days: int = 365
    monthly_threshold: float = 0.20  # 20% return

    # Feature engineering
    ma_periods: list = None
    rsi_period: int = 14
    bb_period: int = 20
    bb_std: int = 2
    atr_period: int = 14
    volume_ma_period: int = 20

    def __post_init__(self):
        if self.ma_periods is None:
            self.ma_periods = [20, 50, 200]


@dataclass
class BacktestConfig:
    """Backtesting configuration"""
    initial_capital: float = 10000.0
    confidence_threshold: float = 0.6  # Only trade if confidence > 60%
    max_position_size: float = 1.0  # 100% of capital per trade
    commission: float = 0.0  # No commission for stocks (many brokers offer free trades)
    slippage: float = 0.001  # 0.1% slippage


@dataclass
class APIConfig:
    """API server configuration"""
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "5000"))
    debug: bool = os.getenv("FLASK_ENV", "production") == "development"
    model_path: str = os.getenv("MODEL_PATH", "/app/models")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:8080")

    @property
    def cors_origins_list(self) -> list:
        return self.cors_origins.split(",")


class Config:
    """Main configuration class"""
    def __init__(self):
        self.database = DatabaseConfig()
        self.model = ModelConfig()
        self.training = TrainingConfig()
        self.backtest = BacktestConfig()
        self.api = APIConfig()


# Global config instance
config = Config()
