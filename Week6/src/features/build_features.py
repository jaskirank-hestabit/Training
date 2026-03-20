# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# import json
# import joblib
# from pathlib import Path

# DATA_PATH = "src/data/processed/final.csv"


# def load_data():
#     df = pd.read_csv(DATA_PATH)
#     return df


# def create_features(df):

#     # Family size
#     df["FamilySize"] = df["SibSp"] + df["Parch"] + 1

#     # Is alone
#     df["IsAlone"] = (df["FamilySize"] == 1).astype(int)

#     # Fare per person
#     df["FarePerPerson"] = df["Fare"] / df["FamilySize"]

#     # Age groups
#     df["AgeGroup"] = pd.cut(
#         df["Age"],
#         bins=[0, 12, 18, 35, 60, 100],
#         labels=["Child", "Teen", "YoungAdult", "Adult", "Senior"]
#     )

#     # Title extraction
#     df["Title"] = df["Name"].str.extract(" ([A-Za-z]+)\.", expand=False)

#     # Ticket length
#     df["TicketLength"] = df["Ticket"].astype(str).apply(len)

#     # Fare log transformation
#     df["FareLog"] = np.log1p(df["Fare"])

#     # Age squared
#     df["AgeSquared"] = df["Age"] ** 2

#     # Family interaction
#     df["FamilyFare"] = df["FamilySize"] * df["Fare"]

#     # Age * class interaction
#     df["AgeClass"] = df["Age"] * df["Pclass"]

#     return df


# def encode_features(df):

#     categorical_cols = ["Sex", "Embarked", "Title", "AgeGroup"]

#     df = pd.get_dummies(df, columns=categorical_cols)

#     return df


# def scale_features(df):
#     scaler = StandardScaler()
#     numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
#     df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

#     # Save scaler and the column list it was fit on
#     Path("src/models").mkdir(parents=True, exist_ok=True)
#     joblib.dump(scaler, "src/models/scaler.pkl")

#     with open("src/features/numeric_cols.json", "w") as f:
#         json.dump(numeric_cols, f, indent=4)

#     return df


# def split_data(df):

#     y = df["Survived"]

#     X = df.drop(columns=["Survived", "Name", "Ticket", "PassengerId"])

#     X_train, X_test, y_train, y_test = train_test_split(
#         X,
#         y,
#         test_size=0.2,
#         random_state=42
#     )

#     return X_train, X_test, y_train, y_test


# def save_datasets(X_train, X_test, y_train, y_test):

#     Path("src/data/processed").mkdir(parents=True, exist_ok=True)

#     X_train.to_csv("src/data/processed/X_train.csv", index=False)
#     X_test.to_csv("src/data/processed/X_test.csv", index=False)

#     y_train.to_csv("src/data/processed/y_train.csv", index=False)
#     y_test.to_csv("src/data/processed/y_test.csv", index=False)

#     print("Train/Test datasets saved")


# def save_feature_list(X):

#     feature_list = list(X.columns)

#     with open("src/features/feature_list.json", "w") as f:
#         json.dump(feature_list, f, indent=4)


# def main():

#     df = load_data()

#     df = create_features(df)

#     df = encode_features(df)

#     df = scale_features(df)

#     X_train, X_test, y_train, y_test = split_data(df)

#     save_datasets(X_train, X_test, y_train, y_test)

#     save_feature_list(X_train)

#     print("Feature engineering completed")


# if __name__ == "__main__":
#     main()





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
    df["Title"]       = df["Name"].str.extract(r" ([A-Za-z]+)\.", expand=False)
    df["TicketLength"] = df["Ticket"].astype(str).apply(len)
    df["FareLog"]     = np.log1p(df["Fare"])
    df["AgeSquared"]  = df["Age"] ** 2
    df["FamilyFare"]  = df["FamilySize"] * df["Fare"]
    df["AgeClass"]    = df["Age"] * df["Pclass"]
    return df


def encode_features(df):
    categorical_cols = ["Sex", "Embarked", "Title", "AgeGroup"]
    df = pd.get_dummies(df, columns=categorical_cols)
    return df


def split_data(df):
    y = df["Survived"]
    # Drop target + columns not used as features
    X = df.drop(columns=["Survived", "Name", "Ticket", "PassengerId"])
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test


def scale_features(X_train, X_test):
    """
    Fit scaler on X_train only (no leakage), then transform both splits.
    Save the scaler and the exact column list for use in the API.
    """
    scaler = StandardScaler()
    numeric_cols = X_train.select_dtypes(include=np.number).columns.tolist()

    X_train[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
    X_test[numeric_cols]  = scaler.transform(X_test[numeric_cols])

    # Persist scaler + column list — API needs both
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
    X_test.to_csv("src/data/processed/X_test.csv",  index=False)
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

    # Split FIRST — so PassengerId and Survived are gone
    X_train, X_test, y_train, y_test = split_data(df)

    # Scale AFTER split — fit on X_train only, no leakage
    X_train, X_test = scale_features(X_train, X_test)

    save_datasets(X_train, X_test, y_train, y_test)
    save_feature_list(X_train)

    print("Feature engineering completed")


if __name__ == "__main__":
    main()