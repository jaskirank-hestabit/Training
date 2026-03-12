import pandas as pd
import optuna
import json
import joblib
from pathlib import Path

from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score

DATA_PATH = "src/data/processed/"
RESULT_PATH = "src/tuning/results.json"
MODEL_PATH = "src/models/tuned_model.pkl"


# -------------------------
# Load datasets
# -------------------------
def load_data():

    X_train = pd.read_csv(DATA_PATH + "X_train.csv")
    y_train = pd.read_csv(DATA_PATH + "y_train.csv").values.ravel()

    y_train = (y_train > 0).astype(int)

    return X_train, y_train


# -------------------------
# Optuna objective
# -------------------------
def objective(trial):

    X_train, y_train = load_data()

    params = {

        "n_estimators": trial.suggest_int("n_estimators", 100, 500),

        "max_depth": trial.suggest_int("max_depth", 3, 10),

        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),

        "subsample": trial.suggest_float("subsample", 0.6, 1.0),

        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),

        "gamma": trial.suggest_float("gamma", 0, 5)

    }

    model = XGBClassifier(
        **params,
        eval_metric="logloss",
        use_label_encoder=False,
        random_state=42
    )

    score = cross_val_score(
        model,
        X_train,
        y_train,
        cv=5,
        scoring="f1"
    ).mean()

    return score


# -------------------------
# Run tuning
# -------------------------
def run_optimization():

    study = optuna.create_study(direction="maximize")

    study.optimize(objective, n_trials=50)

    print("Best params:", study.best_params)

    return study


# -------------------------
# Train tuned model
# -------------------------
def train_best_model(best_params):

    X_train, y_train = load_data()

    model = XGBClassifier(
        **best_params,
        eval_metric="logloss",
        use_label_encoder=False
    )

    model.fit(X_train, y_train)

    Path("src/models").mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    print("Tuned model saved")

    return model


# -------------------------
# Save results
# -------------------------
def save_results(study):

    Path("src/tuning").mkdir(parents=True, exist_ok=True)

    results = {
        "best_params": study.best_params,
        "best_score": study.best_value
    }

    with open(RESULT_PATH, "w") as f:
        json.dump(results, f, indent=4)

    print("Tuning results saved")


# -------------------------
# MAIN
# -------------------------
def main():

    study = run_optimization()

    best_params = study.best_params

    train_best_model(best_params)

    save_results(study)


if __name__ == "__main__":
    main()