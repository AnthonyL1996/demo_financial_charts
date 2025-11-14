"""
Metrics calculation utilities
"""
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)
from typing import Dict, Any, List


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_pred_proba: np.ndarray) -> Dict[str, float]:
    """
    Calculate ML classification metrics

    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_pred_proba: Predicted probabilities

    Returns:
        Dictionary of metrics
    """
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1_score': f1_score(y_true, y_pred, zero_division=0),
    }

    # AUC only if we have both classes
    if len(np.unique(y_true)) > 1:
        metrics['auc'] = roc_auc_score(y_true, y_pred_proba)
    else:
        metrics['auc'] = 0.0

    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    metrics['true_positives'] = int(tp)
    metrics['false_positives'] = int(fp)
    metrics['true_negatives'] = int(tn)
    metrics['false_negatives'] = int(fn)

    return metrics


def calculate_trading_metrics(
    predictions: np.ndarray,
    probabilities: np.ndarray,
    actual_returns: np.ndarray,
    confidence_threshold: float = 0.6,
    initial_capital: float = 10000.0
) -> Dict[str, Any]:
    """
    Calculate trading performance metrics

    Args:
        predictions: Binary predictions (1 = buy, 0 = no trade)
        probabilities: Prediction confidence scores
        actual_returns: Actual forward returns
        confidence_threshold: Minimum confidence to take trade
        initial_capital: Starting capital

    Returns:
        Dictionary of trading metrics
    """
    # Filter trades by confidence threshold
    trade_mask = (predictions == 1) & (probabilities >= confidence_threshold)
    trade_returns = actual_returns[trade_mask]

    if len(trade_returns) == 0:
        return {
            'num_trades': 0,
            'total_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'profit_factor': 0.0,
            'equity_curve': [initial_capital]
        }

    # Build equity curve
    equity_curve = [initial_capital]
    for ret in trade_returns:
        equity_curve.append(equity_curve[-1] * (1 + ret))

    # Total return
    total_return = (equity_curve[-1] / initial_capital - 1) * 100

    # Sharpe ratio (annualized)
    if len(trade_returns) > 1 and np.std(trade_returns) > 0:
        sharpe_ratio = (np.mean(trade_returns) / np.std(trade_returns)) * np.sqrt(252)
    else:
        sharpe_ratio = 0.0

    # Max drawdown
    peak = np.maximum.accumulate(equity_curve)
    drawdown = (np.array(equity_curve) - peak) / peak
    max_drawdown = np.min(drawdown) * 100

    # Win/loss analysis
    wins = trade_returns[trade_returns > 0]
    losses = trade_returns[trade_returns < 0]

    win_rate = len(wins) / len(trade_returns) * 100 if len(trade_returns) > 0 else 0
    avg_win = np.mean(wins) * 100 if len(wins) > 0 else 0
    avg_loss = np.mean(losses) * 100 if len(losses) > 0 else 0

    # Profit factor
    total_wins = np.sum(wins) if len(wins) > 0 else 0
    total_losses = abs(np.sum(losses)) if len(losses) > 0 else 0
    profit_factor = total_wins / total_losses if total_losses > 0 else 0

    return {
        'num_trades': len(trade_returns),
        'total_return': round(total_return, 2),
        'sharpe_ratio': round(sharpe_ratio, 2),
        'max_drawdown': round(max_drawdown, 2),
        'win_rate': round(win_rate, 1),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'profit_factor': round(profit_factor, 2),
        'equity_curve': equity_curve
    }


def calculate_summary_stats(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate summary statistics across multiple folds

    Args:
        results: List of fold results

    Returns:
        Summary statistics
    """
    if not results:
        return {}

    metrics_to_avg = [
        'accuracy', 'precision', 'recall', 'f1_score', 'auc',
        'total_return', 'sharpe_ratio', 'win_rate'
    ]

    summary = {
        'num_folds': len(results),
    }

    # Calculate averages
    for metric in metrics_to_avg:
        values = [r.get(metric, 0) for r in results]
        summary[f'avg_{metric}'] = round(np.mean(values), 3)
        summary[f'std_{metric}'] = round(np.std(values), 3)

    # Best and worst years
    if 'total_return' in results[0]:
        summary['best_fold'] = max(results, key=lambda x: x.get('total_return', -np.inf))
        summary['worst_fold'] = min(results, key=lambda x: x.get('total_return', np.inf))

        # Consistency (% of profitable years)
        profitable = sum(1 for r in results if r.get('total_return', 0) > 0)
        summary['consistency'] = round(profitable / len(results) * 100, 1)

    return summary
