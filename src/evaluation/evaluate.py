"""Evaluation utilities for FloodSense HumAID classification."""

from typing import Any, Dict, List
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)


def compute_metrics(
    y_true: List[str],
    y_pred: List[str],
    labels: List[str]
) -> Dict[str, Any]:
    """
    Compute comprehensive classification metrics.

    Includes:
    - Overall accuracy
    - Macro-F1 and Weighted-F1
    - Per-class precision, recall, F1, and support
    - Confusion matrix
    """
    accuracy = float(accuracy_score(y_true, y_pred))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )

    per_class = {}
    for idx, label in enumerate(labels):
        per_class[label] = {
            "precision": round(float(precision[idx]), 4),
            "recall": round(float(recall[idx]), 4),
            "f1_score": round(float(f1[idx]), 4),
            "support": int(support[idx]),
        }

    cm = confusion_matrix(y_true, y_pred, labels=labels)

    return {
        "accuracy": round(accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "per_class": per_class,
        "confusion_matrix": cm.tolist(),
        "labels": labels,
    }


def format_classification_report(
    y_true: List[str],
    y_pred: List[str],
    labels: List[str]
) -> str:
    """Generate human-readable scikit-learn classification report."""
    return classification_report(
        y_true,
        y_pred,
        labels=labels,
        digits=4,
        zero_division=0
    )


def confusion_matrix_to_dataframe(
    cm_list: List[List[int]],
    labels: List[str]
) -> pd.DataFrame:
    """Convert confusion matrix list to labeled pandas DataFrame."""
    return pd.DataFrame(cm_list, index=labels, columns=labels)
