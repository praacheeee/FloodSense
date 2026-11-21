"""
Training and Model Comparison Pipeline for HumAID Flood Disaster Tweets.

Trains and evaluates 3 TF-IDF based models on the preserved flood HumAID dataset:
1. Logistic Regression with class weighting
2. LinearSVC with class weighting
3. Complement Naive Bayes

Model selection is strictly performed using Macro-F1 on the validation (dev) split.
The selected model is calibrated using Platt scaling (CalibratedClassifierCV)
to produce reliable probability estimates without fabrication, and finally
evaluated on the untouched held-out test split.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from src.evaluation.evaluate import (
    compute_metrics,
    confusion_matrix_to_dataframe,
    format_classification_report,
)
from src.preprocessing.preprocess import normalize_text


def load_dataset_splits(data_dir: Path) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Load train, dev, and test JSON files without modifying them."""
    train_file = data_dir / "train.json"
    dev_file = data_dir / "dev.json"
    test_file = data_dir / "test.json"

    for file_path in [train_file, dev_file, test_file]:
        if not file_path.exists():
            raise FileNotFoundError(f"Required split not found: {file_path}")

    with open(train_file, "r", encoding="utf-8") as f:
        train_data = json.load(f)
    with open(dev_file, "r", encoding="utf-8") as f:
        dev_data = json.load(f)
    with open(test_file, "r", encoding="utf-8") as f:
        test_data = json.load(f)

    return train_data, dev_data, test_data


def run_pipeline(project_root: Path) -> Dict:
    data_dir = project_root / "data" / "external" / "humAID"
    models_dir = project_root / "models"
    reports_dir = project_root / "reports" / "evaluation"

    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    print("Loading datasets...")
    train_data, dev_data, test_data = load_dataset_splits(data_dir)

    print(f"Dataset sizes -> Train: {len(train_data)}, Dev: {len(dev_data)}, Test: {len(test_data)}")

    X_train = [d["tweet_text"] for d in train_data]
    y_train = [d["class_label"] for d in train_data]

    X_dev = [d["tweet_text"] for d in dev_data]
    y_dev = [d["class_label"] for d in dev_data]

    X_test = [d["tweet_text"] for d in test_data]
    y_test = [d["class_label"] for d in test_data]

    labels = sorted(list(set(y_train)))
    print(f"Identified {len(labels)} classes: {labels}")

    # Vectorizer configuration
    vectorizer_params = {
        "ngram_range": (1, 2),
        "min_df": 2,
        "sublinear_tf": True,
    }
    vectorizer = TfidfVectorizer(
        preprocessor=normalize_text,
        ngram_range=vectorizer_params["ngram_range"],
        min_df=vectorizer_params["min_df"],
        sublinear_tf=vectorizer_params["sublinear_tf"],
    )

    print("Fitting TF-IDF vectorizer on training data...")
    X_train_vec = vectorizer.fit_transform(X_train)
    X_dev_vec = vectorizer.transform(X_dev)
    X_test_vec = vectorizer.transform(X_test)
    print(f"TF-IDF vocabulary size: {X_train_vec.shape[1]}")

    # Candidate models
    candidate_configs = {
        "logistic_regression": {
            "name": "Logistic Regression (balanced)",
            "estimator": LogisticRegression(
                class_weight="balanced",
                max_iter=1000,
                random_state=42,
                solver="lbfgs",
                C=1.0,
            ),
            "hyperparameters": {
                "class_weight": "balanced",
                "max_iter": 1000,
                "random_state": 42,
                "solver": "lbfgs",
                "C": 1.0,
            },
        },
        "linear_svc": {
            "name": "LinearSVC (balanced)",
            "estimator": LinearSVC(
                class_weight="balanced",
                random_state=42,
                max_iter=2000,
                C=1.0,
            ),
            "hyperparameters": {
                "class_weight": "balanced",
                "random_state": 42,
                "max_iter": 2000,
                "C": 1.0,
            },
        },
        "complement_nb": {
            "name": "Complement Naive Bayes",
            "estimator": ComplementNB(alpha=1.0),
            "hyperparameters": {
                "alpha": 1.0,
            },
        },
    }

    validation_results = {}
    best_model_key = None
    best_macro_f1 = -1.0

    print("\n--- Training and Validating Candidates ---")
    for key, config in candidate_configs.items():
        print(f"\nTraining {config['name']}...")
        model = config["estimator"]
        model.fit(X_train_vec, y_train)

        dev_preds = model.predict(X_dev_vec)
        metrics = compute_metrics(y_dev, list(dev_preds), labels)
        metrics["model_name"] = config["name"]
        metrics["hyperparameters"] = config["hyperparameters"]

        validation_results[key] = metrics
        print(f"-> Accuracy: {metrics['accuracy']:.4f}")
        print(f"-> Macro-F1: {metrics['macro_f1']:.4f}")
        print(f"-> Weighted-F1: {metrics['weighted_f1']:.4f}")

        if metrics["macro_f1"] > best_macro_f1:
            best_macro_f1 = metrics["macro_f1"]
            best_model_key = key

    print(f"\nSelected best candidate based on Dev Macro-F1: {candidate_configs[best_model_key]['name']} (Macro-F1: {best_macro_f1:.4f})")

    # Save validation comparison report
    val_report_path = reports_dir / "model_comparison_validation.json"
    with open(val_report_path, "w", encoding="utf-8") as f:
        json.dump(validation_results, f, indent=2)
    print(f"Validation comparison saved to: {val_report_path}")

    # Build production pipeline with proper probability calibration for LinearSVC
    print("\nCalibrating selected model for probability estimation...")
    raw_best_estimator = candidate_configs[best_model_key]["estimator"]

    if best_model_key == "linear_svc":
        # CalibratedClassifierCV uses Platt scaling with 5-fold cross-validation on train data
        calibrated_estimator = CalibratedClassifierCV(
            estimator=LinearSVC(class_weight="balanced", random_state=42, max_iter=2000, C=1.0),
            cv=5,
        )
        calibrated_estimator.fit(X_train_vec, y_train)
        final_estimator = calibrated_estimator
    else:
        final_estimator = raw_best_estimator

    # Create end-to-end scikit-learn Pipeline
    full_pipeline = Pipeline([
        ("tfidf", vectorizer),
        ("classifier", final_estimator),
    ])

    # Save the fitted pipeline
    pipeline_save_path = models_dir / "humaid_classifier_pipeline.joblib"
    joblib.dump(full_pipeline, pipeline_save_path)
    print(f"Fitted pipeline saved to: {pipeline_save_path}")

    # Save configuration & metadata
    config_metadata = {
        "model_key": best_model_key,
        "model_name": candidate_configs[best_model_key]["name"],
        "is_calibrated": (best_model_key == "linear_svc"),
        "calibration_method": "Platt scaling (CalibratedClassifierCV, cv=5)" if best_model_key == "linear_svc" else "N/A",
        "hyperparameters": candidate_configs[best_model_key]["hyperparameters"],
        "vectorizer_parameters": vectorizer_params,
        "vocabulary_size": int(X_train_vec.shape[1]),
        "class_labels": labels,
        "dataset_splits": {
            "train": len(train_data),
            "dev": len(dev_data),
            "test": len(test_data),
        },
        "selection_metric": "validation_macro_f1",
        "validation_macro_f1": best_macro_f1,
        "scope_restriction": "HumAID humanitarian communication categories (not severity ratings)",
    }
    config_save_path = models_dir / "model_config.json"
    with open(config_save_path, "w", encoding="utf-8") as f:
        json.dump(config_metadata, f, indent=2)
    print(f"Model configuration saved to: {config_save_path}")

    # Evaluate on the held-out test split
    print("\n--- Evaluating Selected Model on Held-out Test Split ---")
    test_preds = full_pipeline.predict(X_test)
    test_metrics = compute_metrics(y_test, list(test_preds), labels)
    test_metrics["model_name"] = candidate_configs[best_model_key]["name"]
    test_metrics["is_calibrated"] = (best_model_key == "linear_svc")

    print(f"Test Accuracy: {test_metrics['accuracy']:.4f}")
    print(f"Test Macro-F1: {test_metrics['macro_f1']:.4f}")
    print(f"Test Weighted-F1: {test_metrics['weighted_f1']:.4f}")

    # Save test evaluation report (JSON)
    test_report_path = reports_dir / "test_evaluation_report.json"
    with open(test_report_path, "w", encoding="utf-8") as f:
        json.dump(test_metrics, f, indent=2)
    print(f"Test evaluation report saved to: {test_report_path}")

    # Save test confusion matrix (CSV)
    cm_df = confusion_matrix_to_dataframe(test_metrics["confusion_matrix"], labels)
    cm_csv_path = reports_dir / "confusion_matrix_test.csv"
    cm_df.to_csv(cm_csv_path)
    print(f"Test confusion matrix CSV saved to: {cm_csv_path}")

    # Save human-readable classification report (TXT)
    report_txt = format_classification_report(y_test, list(test_preds), labels)
    report_txt_path = reports_dir / "classification_report_test.txt"
    with open(report_txt_path, "w", encoding="utf-8") as f:
        f.write(report_txt)
    print(f"Test classification report TXT saved to: {report_txt_path}")

    return {
        "best_model_key": best_model_key,
        "best_macro_f1": best_macro_f1,
        "validation_results": validation_results,
        "test_metrics": test_metrics,
        "classification_report_txt": report_txt,
    }


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    run_pipeline(project_root)
