import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, classification_report

# Load data
df = pd.read_csv('hit5_clean_deduped.csv')
number_columns = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
all_possible_numbers = range(1, 43)

# Build a feature table: Each row = (draw_idx, number), columns = features
feature_rows = []
for i in range(10, len(df)-1):  # start at 10 to enable window-based stats
    prev_window = df[number_columns].iloc[:i]
    this_draw = set(df.loc[i+1, number_columns])  # next draw (for label)
    for n in all_possible_numbers:
        # Features
        freq = prev_window.apply(lambda row: n in row.values, axis=1).sum()  # freq up to this draw
        last_hit = prev_window.apply(lambda row: n in row.values, axis=1)[::-1].idxmax()
        gap = i - last_hit if last_hit >= 0 else i
        window_freq = prev_window.tail(20).apply(lambda row: n in row.values, axis=1).sum()
        # Hot/Warm/Cold category by mean gap (precomputed)
        gaps = []
        indices = prev_window.apply(lambda row: n in row.values, axis=1)
        hit_indices = list(np.where(indices)[0])
        if hit_indices:
            for j in range(len(hit_indices)):
                if j == 0: gaps.append(hit_indices[j])
                else: gaps.append(hit_indices[j] - hit_indices[j-1])
            mean_gap = np.mean(gaps)
        else:
            mean_gap = i
        # Assign category
        category = 'warm'
        avg_gap = 8.26
        std_gap = 1.76
        if mean_gap < (avg_gap - std_gap): category = 'hot'
        elif mean_gap > (avg_gap + std_gap): category = 'cold'
        # Label: was n in NEXT draw?
        label = int(n in this_draw)
        feature_rows.append({
            'draw': i,
            'number': n,
            'freq': freq,
            'gap': gap,
            'window_freq': window_freq,
            'category': category,
            'label': label
        })

features_df = pd.DataFrame(feature_rows)

# Encode category
features_df['category_code'] = features_df['category'].map({'hot': 2, 'warm': 1, 'cold': 0})

# Train/test split
train = features_df[features_df['draw'] < int(features_df['draw'].max() * 0.8)]
test  = features_df[features_df['draw'] >= int(features_df['draw'].max() * 0.8)]

X_train = train[['freq','gap','window_freq','category_code']]
y_train = train['label']
X_test  = test[['freq','gap','window_freq','category_code']]
y_test  = test['label']

# Train simple model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)
pred = clf.predict(X_test)
proba = clf.predict_proba(X_test)[:,1]

print(classification_report(y_test, pred, digits=2))
print("AUC:", roc_auc_score(y_test, proba))
feature_importance = dict(zip(X_train.columns, clf.feature_importances_))
print("Feature importances:", feature_importance)
