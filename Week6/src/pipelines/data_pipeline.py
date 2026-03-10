import pandas as pd
import numpy as np
from pathlib import Path

RAW_DATA_PATH = "src/data/raw/titanic.csv"
PROCESSED_DATA_PATH = "src/data/processed/final.csv"


def load_data():
    print("Loading dataset...")
    df = pd.read_csv(RAW_DATA_PATH)
    return df


def clean_data(df):

    print("Cleaning data...")

    # Remove duplicates
    df = df.drop_duplicates()

    # Fill numeric missing values
    df = df.fillna(df.median(numeric_only=True))

    # Fill categorical missing values
    df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])

    # Drop cabin (too many missing values)
    df = df.drop(columns=["Cabin"])

    return df


def remove_outliers(df):

    print("Removing outliers...")

    numeric_cols = df.select_dtypes(include=np.number).columns

    for col in numeric_cols:

        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        df = df[(df[col] >= lower) & (df[col] <= upper)]

    return df


def save_data(df):

    Path("data/processed").mkdir(parents=True, exist_ok=True)

    df.to_csv(PROCESSED_DATA_PATH, index=False)

    print("Processed dataset saved.")


def main():

    df = load_data()

    df = clean_data(df)

    df = remove_outliers(df)

    save_data(df)


if __name__ == "__main__":
    main()