import pandas as pd
import numpy as np

# 1. Calculate scores for each number and select top 21 for pool
# [code that computes 'score' as shown above]
scored_pool = top_21_numbers_based_on_score

# 2. Get numbers drawn in last 2 draws
recent_hits = set(df[['Num1', 'Num2', 'Num3', 'Num4', 'Num5']].tail(2).values.flatten())

def valid_recent(combo):
    return all(n not in recent_hits for n in combo)


# Step 1: Categorize numbers into hot, warm, and cold (as before)

df = pd.read_csv('hit5_clean_deduped.csv')
number_columns = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
all_possible_numbers = range(1, 43)

# Calculate mean gap for each number
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

# Step 2: Build your final pool (for example, 3 warm, 1 hot, 1 cold per combo)
from itertools import combinations, product

# Example: draw 3 warm, 1 hot, 1 cold per pick (change counts as desired)
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

# (This will generate all valid 5-number combos based on your selected category counts. You may want to randomly sample if the sets get too large.)

# Step 3: Apply your custom filters to each combo
# Add your previously defined functions (such as valid_recent, not in past winners, sum range, even/odd ratio, no 3-consecutive, etc.). Filter final_combos using those rules.

# Get numbers from last 2 draws
recent_hits = set(df[['Num1', 'Num2', 'Num3', 'Num4', 'Num5']].tail(2).values.flatten())

# def valid_recent(combo):
#     # Returns True if none of the combo numbers were picked in the last 2 draws
#     return all(n not in recent_hits for n in combo)

# Now filter final_combos with your usual checks
filtered_combos = []
for combo in final_combos:
    if not valid_recent(combo): continue
    if not valid_even_odd(combo): continue
    if has_3_consecutive(combo): continue
    if tuple(sorted(combo)) in draws_set: continue  # Exclude past winners
    filtered_combos.append(combo)
print(f"Number of balanced combos: {len(filtered_combos)}")
print("Sample of balanced combos:", filtered_combos[:5])