import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_selection import mutual_info_classif
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression

DATA_PATH = "src/data/processed/final.csv"


def load_data():

    df = pd.read_csv(DATA_PATH)

    df = df.drop(columns=["Name", "Ticket", "PassengerId"])

    df = pd.get_dummies(df)

    y = df["Survived"]

    X = df.drop(columns=["Survived"])

    return X, y


def mutual_information(X, y):

    mi = mutual_info_classif(X, y)

    mi_scores = pd.Series(mi, index=X.columns)

    mi_scores.sort_values(ascending=False).plot.bar(figsize=(12,6))

    plt.title("Feature Importance (Mutual Information)")

    plt.xticks(rotation=60, ha="right")

    plt.tight_layout()

    plt.savefig("src/features/plots/feature_importance.png", dpi=300)

    print("Feature importance plot saved")


def rfe_selection(X, y):

    model = LogisticRegression(max_iter=1000)

    rfe = RFE(model, n_features_to_select=10)

    rfe.fit(X, y)

    selected_features = X.columns[rfe.support_]

    print("Selected Features:")

    print(selected_features)


def main():

    X, y = load_data()

    mutual_information(X, y)

    rfe_selection(X, y)


if __name__ == "__main__":
    main()