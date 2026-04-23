import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    ConfusionMatrixDisplay
)

from sklearn.neural_network import MLPClassifier

from xgboost import XGBClassifier

import matplotlib.pyplot as plt


DATA_PATH = "src/data/processed/"
MODEL_PATH = "src/models/best_model.pkl"
METRICS_PATH = "src/evaluation/metrics.json"


# Load datasets
def load_data():

    X_train = pd.read_csv(DATA_PATH + "X_train.csv")
    X_test = pd.read_csv(DATA_PATH + "X_test.csv")

    y_train = pd.read_csv(DATA_PATH + "y_train.csv").values.ravel()
    y_test = pd.read_csv(DATA_PATH + "y_test.csv").values.ravel()

    y_train = (y_train > 0).astype(int)
    y_test = (y_test > 0).astype(int)

    return X_train, X_test, y_train, y_test


# Define models
def get_models():

    models = {
        "LogisticRegression": LogisticRegression(max_iter=2000),

        "RandomForest": RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42
        ),

        "XGBoost": XGBClassifier(
            eval_metric="logloss",
            use_label_encoder=False
        ),

        "NeuralNetwork": MLPClassifier(
            hidden_layer_sizes=(64, 32),
            max_iter=500
        )
    }

    return models


# Cross Validation
def cross_validate_models(models, X_train, y_train):

    cv_results = {}

    for name, model in models.items():

        scores = cross_val_score(
            model,
            X_train,
            y_train,
            cv=5,
            scoring="accuracy"
        )

        cv_results[name] = scores.mean()

        print(f"{name} CV Accuracy: {scores.mean():.4f}")

    return cv_results


# Train + Evaluate
def evaluate_models(models, X_train, X_test, y_train, y_test):

    results = {}

    for name, model in models.items():

        print(f"\nTraining {name}")

        model.fit(X_train, y_train)

        preds = model.predict(X_test)

        probs = model.predict_proba(X_test)[:,1]

        metrics = {
            "accuracy": accuracy_score(y_test, preds),
            "precision": precision_score(y_test, preds),
            "recall": recall_score(y_test, preds),
            "f1_score": f1_score(y_test, preds),
            "roc_auc": roc_auc_score(y_test, probs)
        }

        results[name] = {
            "model": model,
            "metrics": metrics
        }

        print(metrics)

    return results


# Select best model
def select_best_model(results):

    best_model_name = None
    best_score = 0

    for name, data in results.items():

        f1 = data["metrics"]["f1_score"]

        if f1 > best_score:

            best_score = f1
            best_model_name = name

    print(f"\nBest Model: {best_model_name}")

    return best_model_name


# Save best model
def save_model(model):

    Path("src/models").mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    print("Best model saved.")


# Save metrics
def save_metrics(results):

    metrics_dict = {}

    for name, data in results.items():

        metrics_dict[name] = data["metrics"]

    Path("src/evaluation").mkdir(parents=True, exist_ok=True)

    with open(METRICS_PATH, "w") as f:
        json.dump(metrics_dict, f, indent=4)

    print("Metrics saved.")


# Plot confusion matrix
def plot_confusion_matrix(model, X_test, y_test):

    preds = model.predict(X_test)

    cm = confusion_matrix(y_test, preds)

    disp = ConfusionMatrixDisplay(confusion_matrix=cm)

    disp.plot()

    Path("src/evaluation").mkdir(parents=True, exist_ok=True)

    plt.savefig("src/evaluation/confusion_matrix.png")

    print("Confusion matrix saved.")


# MAIN
def main():

    X_train, X_test, y_train, y_test = load_data()

    models = get_models()

    print("\nRunning Cross Validation")

    cross_validate_models(models, X_train, y_train)

    results = evaluate_models(models, X_train, X_test, y_train, y_test)

    best_model_name = select_best_model(results)

    best_model = results[best_model_name]["model"]

    save_model(best_model)

    save_metrics(results)

    plot_confusion_matrix(best_model, X_test, y_test)


if __name__ == "__main__":
    main()