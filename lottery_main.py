import pandas as pd
import numpy as np
from itertools import combinations
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score

### ------- DATA & CATEGORIZATION UTILITIES -------

def load_draw_data(file="hit5_clean_deduped.csv"):
    df = pd.read_csv(file)
    number_columns = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
    return df, number_columns

def get_hot_warm_cold(df, number_columns):
    all_possible_numbers = range(1, 43)
    gap_list = {}
    for num in all_possible_numbers:
        gaps = []
        indices = df[number_columns].apply(lambda row: num in row.values, axis=1)
        hit_indices = list(np.where(indices)[0])
        if not hit_indices: continue
        for i in range(len(hit_indices)):
            if i == 0: gaps.append(hit_indices[i])
            else: gaps.append(hit_indices[i] - hit_indices[i-1])
        gap_list[num] = gaps
    mean_gaps = {num: np.mean(gaps) for num, gaps in gap_list.items()}
    mean_gap_series = pd.Series(mean_gaps)
    avg_gap = mean_gap_series.mean()
    std_gap = mean_gap_series.std()
    hot = mean_gap_series[mean_gap_series < (avg_gap - std_gap)].index.tolist()
    warm = mean_gap_series[(mean_gap_series >= (avg_gap - std_gap)) & (mean_gap_series <= (avg_gap + std_gap))].index.tolist()
    cold = mean_gap_series[mean_gap_series > (avg_gap + std_gap)].index.tolist()
    return hot, warm, cold

def recent_hits(df, number_columns, n=2):
    return set(df[number_columns].tail(n).values.flatten())

def draws_set(df, number_columns):
    return set(tuple(sorted(row)) for row in df[number_columns].values)

### ------- STRATEGY COMBO GENERATION -------

def build_mixed_combos(hot, warm, cold, N_hot=1, N_warm=3, N_cold=1):
    warm_combos = list(combinations(warm, N_warm))
    hot_combos = list(combinations(hot, N_hot))
    cold_combos = list(combinations(cold, N_cold))
    combos = []
    for w in warm_combos:
        for h in hot_combos:
            for c in cold_combos:
                combo = tuple(sorted(list(w) + list(h) + list(c)))
                combos.append(combo)
    return combos

def valid_even_odd(combo):
    evens = sum(n % 2 == 0 for n in combo)
    odds = len(combo) - evens
    return (evens == 2 and odds == 3) or (evens == 3 and odds == 2)

def has_3_consecutive(combo):
    sorted_combo = sorted(combo)
    for i in range(len(sorted_combo)-2):
        if sorted_combo[i]+1 == sorted_combo[i+1] and sorted_combo[i]+2 == sorted_combo[i+2]:
            return True
    return False

def filter_combos(combos, draws_set, recent_hits, sum_range):
    filtered = []
    for combo in combos:
        if any(n in recent_hits for n in combo): continue
        s = sum(combo)
        if not (sum_range[0] <= s <= sum_range[1]): continue
        if not valid_even_odd(combo): continue
        if has_3_consecutive(combo): continue
        if tuple(sorted(combo)) in draws_set: continue
        filtered.append(combo)
    return filtered

### ------- BACKTEST/ML (OPTIONAL) -------

def build_features(df, number_columns):
    all_possible_numbers = range(1, 43)
    feature_rows = []
    for i in range(10, len(df)-1):
        prev_window = df[number_columns].iloc[:i]
        this_draw = set(df.loc[i+1, number_columns])
        for n in all_possible_numbers:
            freq = prev_window.apply(lambda row: n in row.values, axis=1).sum()
            last_hit = prev_window.apply(lambda row: n in row.values, axis=1)[::-1].idxmax()
            gap = i - last_hit if last_hit >= 0 else i
            window_freq = prev_window.tail(20).apply(lambda row: n in row.values, axis=1).sum()
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
            # Category (optional, should pass from get_hot_warm_cold)
            category = 1  # default warm; customize as needed
            label = int(n in this_draw)
            feature_rows.append({
                'draw': i, 'number': n, 'freq': freq, 'gap': gap,
                'window_freq': window_freq, 'category': category, 'label': label
            })
    features_df = pd.DataFrame(feature_rows)
    return features_df

def backtest_classifier(features_df, feature_cols=['freq','gap','window_freq','category'], label_col='label'):
    split_pt = int(features_df['draw'].max() * 0.8)
    train = features_df[features_df['draw'] < split_pt]
    test  = features_df[features_df['draw'] >= split_pt]
    X_train = train[feature_cols]
    y_train = train[label_col]
    X_test  = test[feature_cols]
    y_test  = test[label_col]
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    pred = clf.predict(X_test)
    proba = clf.predict_proba(X_test)[:,1]
    print(classification_report(y_test, pred, digits=2))
    print("AUC:", roc_auc_score(y_test, proba))
    importance = dict(zip(X_train.columns, clf.feature_importances_))
    print("Feature Importances:", importance)
    return clf

### ------- EXAMPLE MAIN WORKFLOW -------

def main():
    df, number_columns = load_draw_data()
    hot, warm, cold = get_hot_warm_cold(df, number_columns)
    mixed_combos = build_mixed_combos(hot, warm, cold, N_hot=1, N_warm=3, N_cold=1)

    sum_mean = df[number_columns].sum(axis=1).mean()
    sum_std = df[number_columns].sum(axis=1).std()
    sum_range = (sum_mean - sum_std, sum_mean + sum_std)
    r_hits = recent_hits(df, number_columns)
    d_set = draws_set(df, number_columns)
    valid_combos = filter_combos(mixed_combos, d_set, r_hits, sum_range)
    print(f"Total valid combos after filtering: {len(valid_combos)}")
    print("Sample combos:", valid_combos[:5])

    # Optional: Backtest ML
    # features_df = build_features(df, number_columns)
    # backtest_classifier(features_df)
    
if __name__ == "__main__":
    main()
