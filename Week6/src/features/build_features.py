import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import json
from pathlib import Path

DATA_PATH = "src/data/processed/final.csv"


def load_data():
    df = pd.read_csv(DATA_PATH)
    return df


def create_features(df):

    # Family size
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1

    # Is alone
    df["IsAlone"] = (df["FamilySize"] == 1).astype(int)

    # Fare per person
    df["FarePerPerson"] = df["Fare"] / df["FamilySize"]

    # Age groups
    df["AgeGroup"] = pd.cut(
        df["Age"],
        bins=[0, 12, 18, 35, 60, 100],
        labels=["Child", "Teen", "YoungAdult", "Adult", "Senior"]
    )

    # Title extraction
    df["Title"] = df["Name"].str.extract(" ([A-Za-z]+)\.", expand=False)

    # Ticket length
    df["TicketLength"] = df["Ticket"].astype(str).apply(len)

    # Fare log transformation
    df["FareLog"] = np.log1p(df["Fare"])

    # Age squared
    df["AgeSquared"] = df["Age"] ** 2

    # Family interaction
    df["FamilyFare"] = df["FamilySize"] * df["Fare"]

    # Age * class interaction
    df["AgeClass"] = df["Age"] * df["Pclass"]

    return df


def encode_features(df):

    categorical_cols = ["Sex", "Embarked", "Title", "AgeGroup"]

    df = pd.get_dummies(df, columns=categorical_cols)

    return df


def scale_features(df):

    scaler = StandardScaler()

    numeric_cols = df.select_dtypes(include=np.number).columns

    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    return df


def split_data(df):

    y = df["Survived"]

    X = df.drop(columns=["Survived", "Name", "Ticket", "PassengerId"])

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    return X_train, X_test, y_train, y_test


def save_datasets(X_train, X_test, y_train, y_test):

    Path("src/data/processed").mkdir(parents=True, exist_ok=True)

    X_train.to_csv("src/data/processed/X_train.csv", index=False)
    X_test.to_csv("src/data/processed/X_test.csv", index=False)

    y_train.to_csv("src/data/processed/y_train.csv", index=False)
    y_test.to_csv("src/data/processed/y_test.csv", index=False)

    print("Train/Test datasets saved")


def save_feature_list(X):

    feature_list = list(X.columns)

    with open("src/features/feature_list.json", "w") as f:
        json.dump(feature_list, f, indent=4)


def main():

    df = load_data()

    df = create_features(df)

    df = encode_features(df)

    df = scale_features(df)

    X_train, X_test, y_train, y_test = split_data(df)

    save_datasets(X_train, X_test, y_train, y_test)

    save_feature_list(X_train)

    print("Feature engineering completed")


if __name__ == "__main__":
    main()