import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import json
import joblib
from pathlib import Path

DATA_PATH = "src/data/processed/final.csv"


def load_data():
    df = pd.read_csv(DATA_PATH)
    return df


def create_features(df):
    df["FamilySize"]    = df["SibSp"] + df["Parch"] + 1
    df["IsAlone"]       = (df["FamilySize"] == 1).astype(int)
    df["FarePerPerson"] = df["Fare"] / df["FamilySize"]
    df["AgeGroup"]      = pd.cut(
        df["Age"],
        bins=[0, 12, 18, 35, 60, 100],
        labels=["Child", "Teen", "YoungAdult", "Adult", "Senior"]
    )
    df["Title"]        = df["Name"].str.extract(r" ([A-Za-z]+)\.", expand=False)
    df["TicketLength"] = df["Ticket"].astype(str).apply(len)
    df["FareLog"]      = np.log1p(df["Fare"])
    df["AgeSquared"]   = df["Age"] ** 2
    df["FamilyFare"]   = df["FamilySize"] * df["Fare"]
    df["AgeClass"]     = df["Age"] * df["Pclass"]
    return df


def encode_features(df):
    categorical_cols = ["Sex", "Embarked", "Title", "AgeGroup"]
    df = pd.get_dummies(df, columns=categorical_cols)
    return df


def split_data(df):
    y = df["Survived"]
    X = df.drop(columns=["Survived", "Name", "Ticket", "PassengerId"])
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test


def scale_features(X_train, X_test):

    X_train = X_train.copy()
    X_test  = X_test.copy()

    scaler = StandardScaler()
    numeric_cols = X_train.select_dtypes(include=np.number).columns.tolist()

    X_train[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
    X_test[numeric_cols]  = scaler.transform(X_test[numeric_cols])

    Path("src/models").mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, "src/models/scaler.pkl")

    Path("src/features").mkdir(parents=True, exist_ok=True)
    with open("src/features/numeric_cols.json", "w") as f:
        json.dump(numeric_cols, f, indent=4)

    print(f"Scaler saved. Numeric cols: {numeric_cols}")
    return X_train, X_test


def save_datasets(X_train, X_test, y_train, y_test):
    Path("src/data/processed").mkdir(parents=True, exist_ok=True)
    X_train.to_csv("src/data/processed/X_train.csv", index=False)
    X_test.to_csv("src/data/processed/X_test.csv",   index=False)
    y_train.to_csv("src/data/processed/y_train.csv", index=False)
    y_test.to_csv("src/data/processed/y_test.csv",   index=False)
    print("Train/Test datasets saved")


def save_feature_list(X_train):
    feature_list = list(X_train.columns)
    with open("src/features/feature_list.json", "w") as f:
        json.dump(feature_list, f, indent=4)
    print(f"Feature list saved: {len(feature_list)} features")


def main():
    df = load_data()
    df = create_features(df)
    df = encode_features(df)

    X_train, X_test, y_train, y_test = split_data(df)

    X_train, X_test = scale_features(X_train, X_test)

    save_datasets(X_train, X_test, y_train, y_test)
    save_feature_list(X_train)

    print("Feature engineering completed")


if __name__ == "__main__":
    main()