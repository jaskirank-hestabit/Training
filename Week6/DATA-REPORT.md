# Data Pipeline & Exploratory Data Analysis Report

## Project: Titanic Dataset Analysis

# Dataset Information

Dataset Used: **Titanic Passenger Dataset**

The dataset contains passenger information from the Titanic disaster and is commonly used for machine learning classification problems.

## Key Features

| Feature | Description |
|------|------|
| PassengerId | Unique passenger identifier |
| Survived | Target variable (0 = No, 1 = Yes) |
| Pclass | Passenger class |
| Name | Passenger name |
| Sex | Gender |
| Age | Passenger age |
| SibSp | Number of siblings/spouses aboard |
| Parch | Number of parents/children aboard |
| Ticket | Ticket number |
| Fare | Ticket price |
| Cabin | Cabin number |
| Embarked | Port of embarkation |

Target variable: **Survived**

---

# Environment Setup

## 1. Create Virtual Environment

```bash
python3 -m venv venv
```

## 2. Activate Virtual Environment

```bash
source venv/bin/activate
```

Your terminal should show:

```
(venv)
```

## 3. Install Required Libraries

```bash
pip install pandas numpy matplotlib seaborn scikit-learn jupyter missingno
```

Save dependencies:

```bash
pip freeze > requirements.txt
```

---

# Data Pipeline

Pipeline file:

```
pipelines/data_pipeline.py
```

## Pipeline Responsibilities

The pipeline performs the following tasks:

1. Load raw dataset  
2. Remove duplicates  
3. Handle missing values  
4. Detect and remove outliers  
5. Save processed dataset  

---

## Run Data Pipeline

Execute the pipeline:

```bash
python pipelines/data_pipeline.py
```

Output:

```
Loading dataset...
Cleaning data...
Removing outliers...
Processed dataset saved.
```

Generated file:

```
data/processed/final.csv
```

---

# Data Cleaning Strategy

## 1. Duplicate Removal

Duplicate records are removed using:

```python
df.drop_duplicates()
```

---

## 2. Handling Missing Values

Numeric columns are filled using median values:

```python
df.fillna(df.median(numeric_only=True))
```

Categorical columns such as **Embarked** are filled using **mode**.

The **Cabin** column contains a large number of missing values and may be removed during preprocessing.

---

## 3. Outlier Detection

Outliers are detected using the Interquartile Range (IQR) method.

Formula:

```
IQR = Q3 - Q1
Lower Bound = Q1 - 1.5 * IQR
Upper Bound = Q3 + 1.5 * IQR
```

Values outside these bounds are removed.

---

# Exploratory Data Analysis (EDA)

EDA notebook location:

```
notebooks/EDA.ipynb
```

Run Jupyter Notebook:

```bash
jupyter notebook
```

Then open:

```
notebooks/EDA.ipynb
```

---

# Visualizations Generated

The notebook generates the following analyses.

---

## Missing Values Heatmap

Generated using:

```python
missingno.heatmap()
```

Purpose:

- Identify columns with missing data
- Visualize missing value distribution

---

## Correlation Matrix

Generated using:

```python
sns.heatmap()
```

Purpose:

- Understand relationships between numeric variables
- Detect feature correlations

---

## Feature Distributions

Generated using:

```python
df.hist()
```

Purpose:

- Analyze feature distributions
- Identify skewed variables
- Detect potential outliers

---

## Target Distribution

Generated using:

```python
sns.countplot()
```

Purpose:

- Analyze class distribution
- Understand survival imbalance

---

# Outputs Generated

The pipeline produces the following artifacts:

| File | Description |
|-----|-----|
| data/processed/final.csv | Cleaned dataset |
| notebooks/EDA.ipynb | Exploratory analysis |
| pipelines/data_pipeline.py | Data processing pipeline |
| DATA-REPORT.md | Project documentation |

---

# Key Observations

- The dataset contains missing values primarily in the **Cabin column**.
- Numeric missing values were handled using **median imputation**.
- Outliers were detected using **IQR filtering**.
- Survival distribution indicates **class imbalance** between survived and non-survived passengers.
