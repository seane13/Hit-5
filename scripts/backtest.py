import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_curve, auc
import matplotlib.pyplot as plt

# --- Config ---
DATA_PATH = 'data/hit5_clean_deduped.csv'
NUMBER_COLUMNS = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
all_possible_numbers = list(range(1, 43))

# --- Feature creation for a single number ---
def make_features(train_df, number):
    freq = train_df[NUMBER_COLUMNS].apply(lambda row: number in row.values, axis=1).sum()
    last_hit = train_df[NUMBER_COLUMNS].apply(lambda row: number in row.values, axis=1)[::-1]
    last_idx = np.where(last_hit.values)[0]
    gap = len(train_df) - last_idx[0] if len(last_idx) else len(train_df)
    window_freq = train_df[NUMBER_COLUMNS].tail(20).apply(lambda row: number in row.values, axis=1).sum()
    # Mean gap stat
    indices = train_df[NUMBER_COLUMNS].apply(lambda row: number in row.values, axis=1)
    hit_indices = np.where(indices.values)[0]
    gaps = [hit_indices[0]] + [hit_indices[j] - hit_indices[j-1] for j in range(1, len(hit_indices))] if len(hit_indices) else []
    mean_gap = np.mean(gaps) if gaps else len(train_df)
    avg_gap, std_gap = 8.26, 1.76
    category = 'warm'
    if mean_gap < (avg_gap - std_gap): category = 'hot'
    elif mean_gap > (avg_gap + std_gap): category = 'cold'
    category_code = {'hot':2, 'warm':1, 'cold':0}[category]
    return [freq, gap, window_freq, category_code]

# --- Load data ---
df = pd.read_csv(DATA_PATH)
train_idx = int(len(df) * 0.8)

# --- Build training data ---
train_features, train_labels = [], []
for i in range(10, train_idx):
    prev_window = df[NUMBER_COLUMNS].iloc[:i]
    next_draw = set(df.loc[i, NUMBER_COLUMNS])
    for n in all_possible_numbers:
        train_features.append(make_features(prev_window, n))
        train_labels.append(int(n in next_draw))

# --- Build test data ---
test_features, test_labels = [], []
for i in range(train_idx, len(df)-1):
    prev_window = df[NUMBER_COLUMNS].iloc[:i]
    next_draw = set(df.loc[i+1, NUMBER_COLUMNS])
    for n in all_possible_numbers:
        test_features.append(make_features(prev_window, n))
        test_labels.append(int(n in next_draw))

train_features = np.array(train_features)
test_features = np.array(test_features)

# --- Fit balanced classifier ---
clf = RandomForestClassifier(
    n_estimators=100,
    class_weight='balanced',
    random_state=42
)
clf.fit(train_features, train_labels)

# --- Predictions and probabilities ---
preds = clf.predict(test_features)
probas = clf.predict_proba(test_features)[:, 1]  # Probability of class "1"

# --- Classification report ---
print(classification_report(test_labels, preds))

# --- Compute and print AUC ---
auc_val = auc(*roc_curve(test_labels, probas)[:2])
print(f"AUC: {auc_val}")

# --- Feature importances ---
feat_names = ['freq', 'gap', 'window_freq', 'category_code']
importances = dict(zip(feat_names, clf.feature_importances_))
print("Feature importances:", importances)

# --- ROC Curve plot ---
fpr, tpr, _ = roc_curve(test_labels, probas)
roc_auc = auc(fpr, tpr)
plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random classifier')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate (Recall)')
plt.title('Receiver Operating Characteristic (ROC)')
plt.legend(loc='lower right')
plt.savefig('plots/ROC.png')
plt.show()

# --- Threshold tuning example ---
for thresh in [0.5, 0.3, 0.1]:
    tuned_preds = (probas > thresh).astype(int)
    print(f"\n=== Threshold {thresh} ===")
    print(classification_report(test_labels, tuned_preds))
