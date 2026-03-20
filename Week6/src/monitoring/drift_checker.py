import pandas as pd
import json

# Use final.csv (unscaled) as the reference, not X_train.csv
TRAIN_PATH = "src/data/processed/final.csv"
LOG_PATH   = "src/prediction_logs.csv"

# Drift threshold — tweak per feature as needed
THRESHOLDS = {
    "Pclass": 0.3,
    "Age":    5.0,
    "SibSp":  0.3,
    "Parch":  0.3,
    "Fare":   5.0,
}
DEFAULT_THRESHOLD = 1.0


def load_data():
    train = pd.read_csv(TRAIN_PATH)
    logs  = pd.read_csv(LOG_PATH)
    return train, logs


def check_drift(train, logs):

    print("\nChecking Data Drift...\n")

    inputs = logs["input"].apply(json.loads).apply(pd.Series)

    # Only check columns that appear in both training data and production logs
    common_cols = [
        col for col in train.select_dtypes(include="number").columns
        if col in inputs.columns
    ]

    any_drift = False

    for col in common_cols:

        train_mean = train[col].mean()
        train_std  = train[col].std()
        prod_mean  = inputs[col].mean()
        diff       = abs(train_mean - prod_mean)
        threshold  = THRESHOLDS.get(col, DEFAULT_THRESHOLD)
        status     = "⚠️  DRIFT" if diff > threshold else "✅  OK"

        if diff > threshold:
            any_drift = True

        print(f"{col:<20} train_mean={train_mean:>8.3f}  "
              f"prod_mean={prod_mean:>8.3f}  "
              f"diff={diff:>7.4f}  "
              f"(threshold={threshold})  {status}")

    print()
    if any_drift:
        print("⚠️  Drift detected — consider retraining the model.")
    else:
        print("✅  No significant drift detected.")


def main():
    train, logs = load_data()
    check_drift(train, logs)


if __name__ == "__main__":
    main()