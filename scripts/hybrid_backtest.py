import pandas as pd
import numpy as np
from utils.pool_select import select_pool
from utils.lottery_stats import number_frequency, calculate_gaps, get_hot_warm_cold
from sklearn.ensemble import RandomForestClassifier
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Config ---
DATA_PATH = 'data/hit5_clean_deduped.csv'
NUMBER_COLUMNS = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
GAP_N_COLD = 5
TEST_WINDOW = 100  # Adjust as needed

# --- Load and prep data ---
df = pd.read_csv(DATA_PATH)
all_possible_numbers = range(1, 43)

# --- Helper: feature creation for 1 draw ---
def make_features(train_df, number):
    freq = train_df[NUMBER_COLUMNS].apply(lambda row: number in row.values, axis=1).sum()
    last_hit = train_df[NUMBER_COLUMNS].apply(lambda row: number in row.values, axis=1)[::-1].idxmax()
    gap = len(train_df) - last_hit if last_hit >= 0 else len(train_df)
    window_freq = train_df[NUMBER_COLUMNS].tail(20).apply(lambda row: number in row.values, axis=1).sum()
    # Optionally: add more features here as discussed
    # Hot/Warm/Cold category
    gaps = []
    indices = train_df[NUMBER_COLUMNS].apply(lambda row: number in row.values, axis=1)
    hit_indices = list(np.where(indices)[0])
    if hit_indices:
        for j in range(len(hit_indices)):
            if j == 0:
                gaps.append(hit_indices[j])
            else:
                gaps.append(hit_indices[j] - hit_indices[j-1])
        mean_gap = np.mean(gaps)
    else:
        mean_gap = len(train_df)
    category = 'warm'
    avg_gap, std_gap = 8.26, 1.76  # Use dataset-wide stats or precompute
    if mean_gap < (avg_gap - std_gap): category = 'hot'
    elif mean_gap > (avg_gap + std_gap): category = 'cold'
    category_code = {'hot':2, 'warm':1, 'cold':0}[category]
    return [freq, gap, window_freq, category_code]

# --- Train ML model on initial window ---
train_idx = int(len(df) * 0.8)
train_feature_rows = []
train_label_rows = []
for i in range(10, train_idx):
    prev_window = df[NUMBER_COLUMNS].iloc[:i]
    next_draw = set(df.loc[i, NUMBER_COLUMNS])
    for n in all_possible_numbers:
        features = make_features(prev_window, n)
        train_feature_rows.append(features)
        train_label_rows.append(int(n in next_draw))
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(train_feature_rows, train_label_rows)

# --- Hybrid backtest: for each test draw, use shared pool AND ML ---
results = []
for i in range(train_idx, len(df)-1):
    prev_window = df[NUMBER_COLUMNS].iloc[:i]
    pool = select_pool(prev_window, NUMBER_COLUMNS, GAP_N_COLD)
    test_draw = set(df.loc[i+1, NUMBER_COLUMNS])
    features = [make_features(prev_window, n) for n in pool]
    pool_numbers = list(pool)
    proba = clf.predict_proba(features)[:, 1]
    # --- Hybrid selection: pick top K pool numbers by ML probability ---
    # For example, pick 5 most probable pool numbers as the candidate combo:
    top_idx = np.argsort(proba)[-5:][::-1]
    combo = [pool_numbers[j] for j in top_idx]
    matches = set(combo) & test_draw
    all_in_draw = set(combo) == test_draw
    results.append({
        'draw_idx': i+1,
        'combo': combo,
        'test_draw': test_draw,
        'matched': len(matches),
        'perfect_hit': all_in_draw
    })

# --- Analyze hybrid results ---
results_df = pd.DataFrame(results)
print("Hybrid coverage (perfect 5/5 match):", results_df['perfect_hit'].mean())
print("Average matches per draw:", results_df['matched'].mean())
print(results_df['matched'].value_counts().sort_index())
