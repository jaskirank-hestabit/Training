# Model Interpretation Report

## Hyperparameter Tuning

Optuna was used to optimize the XGBoost model.

Objective:
Maximize F1 score using 5-fold cross validation.

Best Parameters:
Stored in /src/tuning/results.json

Result:
The tuned model improved performance compared to baseline models.


## Feature Importance

Top important features for survival prediction:

1. Sex
2. Pclass
3. Fare
4. Age
5. FamilySize

This aligns with domain understanding:
Women and higher-class passengers had higher survival rates.


## SHAP Analysis

SHAP values were used to interpret individual feature contributions.

Key observations:

• Female passengers strongly increase survival probability  
• Higher passenger class increases survival  
• Larger family size has mixed effect  


## Error Analysis

Error heatmap shows model confusion between:

True Survivors vs Predicted Non-survivors.

Possible reasons:

• Missing contextual features
• Passenger group interactions


## Bias / Variance

Cross validation vs test score comparison indicates:

Low variance
Moderate bias

Model generalizes well on unseen data.