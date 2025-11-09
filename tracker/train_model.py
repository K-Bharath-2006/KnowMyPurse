import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils import resample
from sklearn.metrics import classification_report
import joblib

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'personal_finance_tracker_dataset.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'expense_model.pkl')

# Load dataset
data = pd.read_csv(CSV_PATH, parse_dates=['date'])

# Map categories to 4 groups
def map_category(cat):
    cat = str(cat).lower()
    if 'food' in cat or 'dining' in cat:
        return 'food'
    elif 'travel' in cat or 'transportation' in cat:
        return 'travel'
    elif 'medical' in cat or 'healthcare' in cat or 'insurance' in cat:
        return 'medical'
    else:
        return 'others'

data['category_group'] = data['category'].apply(map_category)

# Aggregate weekly expenses
data['week'] = data['date'].dt.isocalendar().week
data['year'] = data['date'].dt.year

weekly = data.groupby(['year','week','user_id','monthly_income','category_group'])['monthly_expense_total'].sum().reset_index()

weekly_expense = weekly.pivot_table(
    index=['year','week','user_id','monthly_income'],
    columns='category_group',
    values='monthly_expense_total',
    aggfunc='sum',
    fill_value=0
).reset_index()

for col in ['food','travel','medical','others']:
    if col not in weekly_expense.columns:
        weekly_expense[col] = 0

# Weekly budget
weekly_expense['weekly_budget'] = weekly_expense['monthly_income'] / 4

# Normalize by weekly budget
for col in ['food','travel','medical','others']:
    weekly_expense[col] = weekly_expense[col] / weekly_expense['weekly_budget']

# Label
def label_status(row):
    total_ratio = row[['food','travel','medical','others']].sum()
    if total_ratio > 1.05:
        return 'Overspending'
    elif total_ratio < 0.75:
        return 'Under Budget'
    else:
        return 'Balanced'

weekly_expense['status'] = weekly_expense.apply(label_status, axis=1)

# Upsample minority classes
majority_label = weekly_expense['status'].value_counts().idxmax()
df_majority = weekly_expense[weekly_expense['status'] == majority_label]
df_minority = weekly_expense[weekly_expense['status'] != majority_label]

if not df_minority.empty and len(df_majority) > 0:
    df_minority_upsampled = resample(df_minority, replace=True, n_samples=len(df_majority), random_state=42)
    balanced_data = pd.concat([df_majority, df_minority_upsampled])
else:
    balanced_data = weekly_expense.copy()

balanced_data = balanced_data.sample(frac=1, random_state=42)

# Features & labels
X = balanced_data[['food','travel','medical','others']]
y = balanced_data['status']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# Train RandomForest
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))
print(f"Model Accuracy: {clf.score(X_test, y_test)*100:.2f}%")

# Save model
joblib.dump(clf, MODEL_PATH)
print(f"Model saved at '{MODEL_PATH}'")
