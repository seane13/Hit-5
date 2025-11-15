import pandas as pd
import numpy as np
from itertools import combinations

# Load draw data
df = pd.read_csv('hit5_clean_deduped.csv')
number_columns = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
all_possible_numbers = range(1, 43)

# --- Hot/Warm/Cold Gaps calculation ---
gap_list = {}
for num in all_possible_numbers:
    gaps = []
    indices = df[number_columns].apply(lambda row: num in row.values, axis=1)
    hit_indices = list(np.where(indices)[0])
    if not hit_indices:
        continue
    for i in range(len(hit_indices)):
        if i == 0:
            gaps.append(hit_indices[i])
        else:
            gaps.append(hit_indices[i] - hit_indices[i-1])
    gap_list[num] = gaps

mean_gaps = {num: np.mean(gaps) for num, gaps in gap_list.items()}
mean_gap_series = pd.Series(mean_gaps)
avg_gap = mean_gap_series.mean()
std_gap = mean_gap_series.std()

hot = mean_gap_series[mean_gap_series < (avg_gap - std_gap)].index.tolist()
warm = mean_gap_series[(mean_gap_series >= (avg_gap - std_gap)) & (mean_gap_series <= (avg_gap + std_gap))].index.tolist()
cold = mean_gap_series[mean_gap_series > (avg_gap + std_gap)].index.tolist()

# --- Score calculation (frequency, gap, recent rolling frequency) ---
all_numbers = pd.concat([df[col] for col in number_columns], ignore_index=True)
frequency = all_numbers.value_counts().reindex(all_possible_numbers, fill_value=0)
gaps = {}
for num in all_possible_numbers:
    hits = df[number_columns].apply(lambda row: num in row.values, axis=1)
    hit_indices = np.where(hits)[0]
    if len(hit_indices) > 0:
        gaps[num] = len(df) - 1 - hit_indices[-1]
    else:
        gaps[num] = len(df)
gap_since_last_hit = pd.Series(gaps)

rolling_window = 30
rolling_freq = {}
for num in all_possible_numbers:
    recent_hits = df[number_columns].tail(rolling_window).apply(lambda row: num in row.values, axis=1)
    rolling_freq[num] = recent_hits.sum()
rolling_freq = pd.Series(rolling_freq)

frequency_norm = (frequency - frequency.min()) / (frequency.max() - frequency.min())
gap_norm = (gap_since_last_hit - gap_since_last_hit.min()) / (gap_since_last_hit.max() - gap_since_last_hit.min())
rolling_norm = (rolling_freq - rolling_freq.min()) / (rolling_freq.max() - rolling_freq.min())

score = (1 - frequency_norm) + gap_norm + (1 - rolling_norm)

# --- Filtering and Combo Generation ---
recent_hits = set(df[number_columns].tail(2).values.flatten())

def valid_recent(combo):
    return all(n not in recent_hits for n in combo)

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

must_include = set() # e.g. {3, 27}
def includes_must_have(combo):
    if not must_include: return True
    return all(n in combo for n in must_include)

draws_set = set(tuple(sorted(row)) for row in df[number_columns].values)
winning_sums = df[number_columns].sum(axis=1)
sum_mean = winning_sums.mean()
sum_std = winning_sums.std()
sum_min, sum_max = sum_mean - sum_std, sum_mean + sum_std

# --- Compose combos for 3 warm, 1 hot, 1 cold
N_hot = 1
N_warm = 3
N_cold = 1

warm_combos = list(combinations(warm, N_warm))
hot_combos = list(combinations(hot, N_hot))
cold_combos = list(combinations(cold, N_cold))

final_combos = []
for warm_group in warm_combos:
    for hot_group in hot_combos:
        for cold_group in cold_combos:
            combo = tuple(sorted(list(warm_group) + list(hot_group) + list(cold_group)))
            final_combos.append(combo)

# --- Filter and Score Combos ---
filtered_scored_combos = []
for combo in final_combos:
    if not valid_recent(combo): continue
    if not includes_must_have(combo): continue
    if not (sum_min <= sum(combo) <= sum_max): continue
    if not valid_even_odd(combo): continue
    if has_3_consecutive(combo): continue
    if tuple(sorted(combo)) in draws_set: continue
    combo_score = sum(score.get(n, 0) for n in combo)
    filtered_scored_combos.append((combo, combo_score))

# --- Sort and output
top_100 = sorted(filtered_scored_combos, key=lambda x: x[1], reverse=True)[:100]
print(f'Number of balanced, filtered combos: {len(top_100)}')
for combo, combo_score in top_100[:5]:
    print(combo, combo_score)
