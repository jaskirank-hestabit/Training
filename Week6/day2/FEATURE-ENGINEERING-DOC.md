# Day 2 — Feature Engineering & Feature Selection

## Overview

This stage of the project focuses on transforming raw processed data into meaningful machine learning features. The goal is to improve model performance by creating useful derived features, encoding categorical variables, normalizing numerical values, and selecting the most important features.

This pipeline builds on the output of **Day 1 (Data Pipeline + EDA)** and produces datasets ready for model training.

---

# Topics Covered

## 1. Categorical Encoding

Categorical variables must be converted into numerical form before they can be used in machine learning models.

Common encoding techniques:

- **OneHot Encoding**
- Label Encoding
- Target Encoding

In this project we used:

```
pandas.get_dummies()
```

Example:

```
Sex → Sex_male, Sex_female
Embarked → Embarked_C, Embarked_Q, Embarked_S
```

---

## 2. Numerical Feature Transformations

Numerical features can be transformed to improve model learning.

Examples:

- Log transformation
- Square root transformation
- Power transformation
- Polynomial features

Example used in this project:

```
FareLog = log(1 + Fare)
AgeSquared = Age²
```

---

## 3. Feature Engineering

Feature engineering creates **new informative features from existing data**.

### Features created in this project

| Feature | Description |
|------|------|
| FamilySize | Total family members aboard |
| IsAlone | Whether passenger traveled alone |
| FarePerPerson | Ticket fare divided by family size |
| AgeGroup | Passenger age category |
| Title | Title extracted from passenger name |
| TicketLength | Length of ticket number |
| FareLog | Log transformation of fare |
| AgeSquared | Age squared feature |
| FamilyFare | Family size multiplied by fare |
| AgeClass | Interaction between age and passenger class |

Total engineered features: **10+**

---

## 4. Feature Scaling

Numerical features are normalized using:

```
StandardScaler
```

This ensures all features have:

```
Mean = 0
Standard Deviation = 1
```

Scaling improves the performance of many machine learning algorithms.

---

## 5. Train-Test Split

The dataset is divided into:

| Dataset | Purpose |
|------|------|
| X_train | Features used for model training |
| y_train | Target labels for training |
| X_test | Features used for evaluation |
| y_test | Target labels for evaluation |

Split ratio used:

```
80% Training
20% Testing
```

This prevents the model from overfitting and ensures proper evaluation.

---

## 6. Feature Selection

Feature selection identifies the most important variables.

Methods used:

### Mutual Information

Measures dependency between features and target variable.

```
mutual_info_classif()
```

Produces a **feature importance plot**.

---

### Recursive Feature Elimination (RFE)

RFE iteratively removes less important features using a machine learning model.

Model used:

```
Logistic Regression
```

Selected top **10 most important features**.

---

# Running the Feature Engineering Pipeline

## 1. Activate Python Virtual Environment

```
source venv/bin/activate
```

---

## 2. Run Feature Engineering Pipeline

This script:

- Loads processed dataset
- Creates engineered features
- Encodes categorical variables
- Scales numerical features
- Splits dataset into train/test
- Saves datasets

Run:

```
python src/features/build_features.py
```

Outputs generated:

```
src/data/processed/
    X_train.csv
    X_test.csv
    y_train.csv
    y_test.csv
```

And:

```
src/features/feature_list.json
```

---

## 3. Run Feature Selection

This script performs:

- Mutual Information feature importance
- Recursive Feature Elimination (RFE)

Run:

```
python src/features/feature_selector.py
```

Output generated:

```
src/features/plots/feature_importance.png
```

---

# Pipeline Flow

```
Day 1
data_pipeline.py
      |
data/processed/final.csv

Day 2
build_features.py
      |
Feature Engineering
      |
Train-Test Split
      |
feature_selector.py
      |
Feature Importance
```

---

# Deliverables

| File | Description |
|------|------|
| build_features.py | Feature engineering pipeline |
| feature_selector.py | Feature selection implementation |
| feature_list.json | List of engineered features |
| FEATURE-ENGINEERING-DOC.md | Documentation for feature engineering pipeline |