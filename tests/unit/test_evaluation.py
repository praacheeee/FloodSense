import numpy as np
import pandas as pd
from src.evaluation.evaluate import (
    compute_metrics,
    format_classification_report,
    confusion_matrix_to_dataframe,
)


def test_compute_metrics_perfect():
    y_true = ["A", "B", "A", "C"]
    y_pred = ["A", "B", "A", "C"]
    labels = ["A", "B", "C"]

    res = compute_metrics(y_true, y_pred, labels)
    assert res["accuracy"] == 1.0
    assert res["macro_f1"] == 1.0
    assert res["weighted_f1"] == 1.0
    assert res["per_class"]["A"]["precision"] == 1.0
    assert res["per_class"]["A"]["support"] == 2
    assert res["confusion_matrix"] == [[2, 0, 0], [0, 1, 0], [0, 0, 1]]


def test_compute_metrics_imperfect():
    y_true = ["A", "B", "A", "B"]
    y_pred = ["A", "A", "A", "B"]
    labels = ["A", "B"]

    res = compute_metrics(y_true, y_pred, labels)
    assert res["accuracy"] == 0.75
    assert res["per_class"]["A"]["support"] == 2
    assert res["per_class"]["B"]["support"] == 2


def test_confusion_matrix_to_dataframe():
    cm = [[2, 1], [0, 3]]
    labels = ["cat1", "cat2"]
    df = confusion_matrix_to_dataframe(cm, labels)
    assert isinstance(df, pd.DataFrame)
    assert df.loc["cat1", "cat1"] == 2
    assert df.loc["cat1", "cat2"] == 1
