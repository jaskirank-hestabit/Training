import pandas as pd
import numpy as np
from pathlib import Path

RAW_DATA_PATH = "src/data/raw/titanic.csv"
PROCESSED_DATA_PATH = "src/data/processed/final.csv"

CONTINUOUS_COLS = ["Age", "Fare"]


def load_data():
    print("Loading dataset...")
    df = pd.read_csv(RAW_DATA_PATH)
    return df


def clean_data(df):
    print("Cleaning data...")

    # Remove duplicates
    df = df.drop_duplicates()

    # Fill numeric missing values with median (robust to outliers)
    df = df.fillna(df.median(numeric_only=True))

    # Fill categorical missing values with mode
    df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])

    # Drop Cabin — 77 % missing, imputing would invent data
    df = df.drop(columns=["Cabin"])

    return df


def remove_outliers(df):
    print("Removing outliers...")

    for col in CONTINUOUS_COLS:

        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        before = len(df)
        df = df[(df[col] >= lower) & (df[col] <= upper)]
        after  = len(df)

        print(f"  {col}: removed {before - after} outlier rows "
              f"(kept range [{lower:.2f}, {upper:.2f}])")

    return df


def save_data(df):
    Path("src/data/processed").mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"Processed dataset saved → {PROCESSED_DATA_PATH}")
    print(f"Final shape: {df.shape}")


def main():
    df = load_data()
    df = clean_data(df)
    df = remove_outliers(df)
    save_data(df)


if __name__ == "__main__":
    main()