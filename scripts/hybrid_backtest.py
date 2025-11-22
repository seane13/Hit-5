import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from utils.pool_select import select_pool
from sklearn.ensemble import RandomForestClassifier

# --- Config ---
DATA_PATH = 'data/hit5_clean_deduped.csv'
NUMBER_COLUMNS = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
GAP_N_COLD = 15         # Increase pool size for ML selection
POOL_SIZE = 21          # Final number of candidates for ML
TEST_WINDOW = 180       # Last N draws for comparison

# --- Load data ---
df = pd.read_csv(DATA_PATH)
all_possible_numbers = list(range(1, 43))

# --- Feature creation for one number ---
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
    # Simple hot/warm/cold encoding
    avg_gap, std_gap = 8.26, 1.76
    category = 'warm'
    if mean_gap < (avg_gap - std_gap): category = 'hot'
    elif mean_gap > (avg_gap + std_gap): category = 'cold'
    category_code = {'hot':2, 'warm':1, 'cold':0}[category]
    return [freq, gap, window_freq, category_code]

# --- Train ML model on initial draws (80%) ---
train_idx = int(len(df) * 0.8)
train_features, train_labels = [], []
for i in range(10, train_idx):
    prev_window = df[NUMBER_COLUMNS].iloc[:i]
    next_draw = set(df.loc[i, NUMBER_COLUMNS])
    for n in all_possible_numbers:
        train_features.append(make_features(prev_window, n))
        train_labels.append(int(n in next_draw))
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(train_features, train_labels)

# --- Hybrid backtest ---
results = []
for i in range(train_idx, len(df)-1):
    prev_window = df[NUMBER_COLUMNS].iloc[:i]
    # Domain pool: use select_pool, populate pool to fixed POOL_SIZE
    pool = list(select_pool(prev_window, NUMBER_COLUMNS, gap_n_cold=GAP_N_COLD))
    # If < POOL_SIZE, fill with remaining hot/warm/cold numbers (simplified)
    if len(pool) < POOL_SIZE:
        gap_counts = [(n, prev_window[NUMBER_COLUMNS].apply(lambda row: n in row.values, axis=1).sum()) for n in all_possible_numbers if n not in pool]
        gap_counts.sort(key=lambda t: t[1])
        pool += [num for num, _ in gap_counts[:POOL_SIZE-len(pool)]]
    pool = pool[:POOL_SIZE] # Final pool trimmed to POOL_SIZE
    test_draw = set(df.loc[i+1, NUMBER_COLUMNS])
    features = [make_features(prev_window, n) for n in pool]
    proba = clf.predict_proba(features)[:, 1]
    # Pick top 5 by ML probability
    top_idx = np.argsort(proba)[-5:][::-1]
    combo = [pool[j] for j in top_idx]
    matches = set(combo) & test_draw
    all_in_draw = set(combo) == test_draw
    results.append({
        'draw_idx': i+1,
        'pool_size': len(pool),
        'combo': combo,
        'test_draw': test_draw,
        'matched': len(matches),
        'perfect_hit': all_in_draw
    })
results_df = pd.DataFrame(results)

# --- Random pool baseline ---
np.random.seed(42)
random_results = []
for i in range(train_idx, len(df)-1):
    test_draw = set(df.loc[i+1, NUMBER_COLUMNS])
    combo = np.random.choice(all_possible_numbers, 5, replace=False)
    matches = set(combo) & test_draw
    all_in_draw = set(combo) == test_draw
    random_results.append({
        'draw_idx': i+1,
        'combo': combo,
        'test_draw': test_draw,
        'matched': len(matches),
        'perfect_hit': all_in_draw
    })
random_df = pd.DataFrame(random_results)

# --- Print results ---
def print_distribution(results_df, label):
    print(f"\n=== {label} ===")
    print(f"Hybrid coverage (perfect 5/5 match): {results_df['perfect_hit'].mean()*100:.2f}%")
    print(f"Average matches per draw: {results_df['matched'].mean():.2f}")
    print("Distribution of match counts:")
    counts = results_df['matched'].value_counts().sort_index()
    for k, v in counts.items():
        print(f"{k} match{'es' if k != 1 else ''}: {v} times")

# --- Pure ML Backtest ---
pureml_results = []
for i in range(train_idx, len(df)-1):
    prev_window = df[NUMBER_COLUMNS].iloc[:i]
    test_draw = set(df.loc[i+1, NUMBER_COLUMNS])
    # Features for all numbers
    all_features = [make_features(prev_window, n) for n in all_possible_numbers]
    # ML probabilities
    proba = clf.predict_proba(all_features)[:, 1]
    top_idx = np.argsort(proba)[-5:][::-1]
    combo = [all_possible_numbers[j] for j in top_idx]
    matches = set(combo) & test_draw
    all_in_draw = set(combo) == test_draw
    pureml_results.append({
        'draw_idx': i+1,
        'combo': combo,
        'test_draw': test_draw,
        'matched': len(matches),
        'perfect_hit': all_in_draw
    })
pureml_df = pd.DataFrame(pureml_results)

# --- Print Comparison ---
def print_distribution(results_df, label):
    print(f"\n=== {label} ===")
    print(f"Perfect 5/5 match coverage: {results_df['perfect_hit'].mean()*100:.2f}%")
    print(f"Average matches per draw: {results_df['matched'].mean():.2f}")
    print("Distribution of match counts:")
    counts = results_df['matched'].value_counts().sort_index()
    for k, v in counts.items():
        print(f"{k} match{'es' if k != 1 else ''}: {v} times")

print_distribution(results_df, "Hybrid ML + Domain Pool")
print_distribution(pureml_df, "Pure ML (All Numbers)")
print_distribution(random_df, "Random Pool Baseline")
