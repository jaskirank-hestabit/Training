import pandas as pd
import shap
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

DATA_PATH = "src/data/processed/"
MODEL_PATH = "src/models/tuned_model.pkl"


# -------------------------
# Load data
# -------------------------
def load_data():

    X_train = pd.read_csv(DATA_PATH + "X_train.csv")
    X_test = pd.read_csv(DATA_PATH + "X_test.csv")

    y_test = pd.read_csv(DATA_PATH + "y_test.csv").values.ravel()
    y_test = (y_test > 0).astype(int)

    return X_train, X_test, y_test


# -------------------------
# SHAP analysis
# -------------------------
def shap_summary(model, X_train):

    explainer = shap.TreeExplainer(model)

    shap_values = explainer.shap_values(X_train)

    shap.summary_plot(shap_values, X_train, show=False)

    plt.savefig("src/evaluation/shap_summary.png")

    print("SHAP summary saved")


# -------------------------
# Feature importance
# -------------------------
def plot_feature_importance(model, X_train):

    importance = model.feature_importances_

    feat_imp = pd.Series(importance, index=X_train.columns)

    feat_imp.sort_values(ascending=False)[:15].plot.bar()

    plt.title("Feature Importance")

    plt.tight_layout()

    plt.savefig("src/evaluation/feature_importance.png")

    print("Feature importance saved")


# -------------------------
# Error analysis
# -------------------------
def error_analysis(model, X_test, y_test):

    preds = model.predict(X_test)

    cm = confusion_matrix(y_test, preds)

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues"
    )

    plt.title("Error Analysis Heatmap")

    plt.xlabel("Predicted")

    plt.ylabel("Actual")

    plt.savefig("src/evaluation/error_heatmap.png")

    print("Error analysis heatmap saved")


# -------------------------
# MAIN
# -------------------------
def main():

    X_train, X_test, y_test = load_data()

    model = joblib.load(MODEL_PATH)

    shap_summary(model, X_train)

    plot_feature_importance(model, X_train)

    error_analysis(model, X_test, y_test)


if __name__ == "__main__":
    main()