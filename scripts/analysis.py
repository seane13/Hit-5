import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.lottery_stats import (
    calculate_gaps, number_frequency, get_hot_warm_cold,
    longest_gap_per_number, recent_hits
)
from utils.viz import (
    plot_number_frequency, plot_gap_histogram,
    plot_hot_warm_cold, plot_sum_trend
)
from statsmodels.sandbox.stats.runs import runstest_1samp
from scipy.stats import linregress, norm
from utils.viz import plot_residuals_heatmap, plot_gap_length_per_number

# --- Load Data ---
DATA_PATH = 'data/hit5_clean_deduped.csv'
NUMBER_COLUMNS = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
df = pd.read_csv(DATA_PATH)
all_numbers = pd.Series(df[NUMBER_COLUMNS].values.flatten())

# --- General Odds Analysis ---
def odds_hit5_single_ticket():
    n_total = 42
    combo_size = 5
    total_combos = math.comb(n_total, combo_size)
    odds = 1 / total_combos
    print(f"Total possible Hit 5 tickets: {total_combos:,}")
    print(f"Odds of winning with one ticket: 1 in {total_combos:,} ({odds:.8f})\n")

def odds_hit5_pool(pool_size=21):
    combo_size = 5
    pool_combos = math.comb(pool_size, combo_size)
    odds = 1 / pool_combos
    print(f"Pool size: {pool_size}")
    print(f"Number of 5-number combos from pool: {pool_combos:,}")
    print(f"Odds of jackpot if you play every possible combo from pool: 1 in {pool_combos:,} ({odds:.8f})")
    print("(Note: Only if the pool contains all 5 drawn numbers)\n")

# Show for pick 5, then domain pool of 21
odds_hit5_single_ticket()
odds_hit5_pool(pool_size=21)

# --- Frequency Analysis ---
freq = number_frequency(df, NUMBER_COLUMNS)
mean_freq = np.mean(list(freq.values()))
std_freq = np.std(list(freq.values()))
hot, warm, cold = get_hot_warm_cold(df, NUMBER_COLUMNS)
print(f"Hot numbers (more frequent): {hot}")
print(f"Warm numbers (average frequency): {warm}")
print(f"Cold numbers (less frequent): {cold}")
plot_number_frequency(freq, title="Number Frequency in Draws")

# --- Standardized Residuals ---
N_NUMBERS = 42  # update this if your lottery has a different range
EXPECTED = len(df) * 5 / N_NUMBERS  # 5 numbers per draw, N draws
plot_residuals_heatmap(freq, n_numbers=N_NUMBERS, n_draws=len(df), expected_per_number=EXPECTED, title="Standardized Residuals (Chi-Square Test)")

# --- Summary Statistics ---
print(f"Total Draws: {len(df)}")
print(f"Mean number drawn: {all_numbers.mean():.2f}")
print(f"Median: {all_numbers.median():.2f}")
print(f"Standard deviation: {all_numbers.std():.2f}")
print(f"Minimum: {all_numbers.min()}")
print(f"Maximum: {all_numbers.max()}")
print(f"Mode(s): {all_numbers.mode().tolist()}")

# --- Consecutive Numbers ---
count_consec = sum(np.any(np.diff(sorted(row)) == 1) for row in df[NUMBER_COLUMNS].values)
percent_consec = 100 * count_consec / len(df)
print(f"Draws with at least one consecutive pair: {count_consec}")
print(f"Percent with consecutive pair: {percent_consec:.1f}%")

# --- Gap Analysis ---
gaps = calculate_gaps(df, NUMBER_COLUMNS)
plot_gap_histogram(gaps)
longest_gaps = longest_gap_per_number(gaps)
print(f"Longest gaps per number: {dict(list(longest_gaps.items())[:10])}")
plot_gap_length_per_number(gaps, title="Gap Lengths by Number")

# --- Empirical vs Theoretical Probability ---
prob_df = pd.DataFrame({
    "Number": range(1, 43),
    "Empirical Probability": pd.Series(freq) / len(df),
    "Theoretical Probability": [5/42] * 42
})
prob_df.plot(x="Number", y=["Empirical Probability", "Theoretical Probability"], kind="bar", figsize=(12,5))
plt.title("Empirical vs. Theoretical Probability by Number")
plt.tight_layout()
plt.show()

# --- Temporal Pattern Analysis ---
sum_win = df[NUMBER_COLUMNS].sum(axis=1)
plot_sum_trend(df, NUMBER_COLUMNS)

# --- Runs Test for Randomness ---
median = all_numbers.median()
binary_seq = (all_numbers > median).astype(int)
z_stat, p_val = runstest_1samp(binary_seq, correction=True)
print(f"Runs test z-statistic: {z_stat:.2f}, p-value: {p_val:.4f}")
if p_val < 0.05:
    print("Reject H0: Sequence shows non-randomness.")
else:
    print("Fail to reject H0: Sequence appears random.")

# --- Serial Correlation ---
for col in NUMBER_COLUMNS:
    series = df[col].dropna()
    if hasattr(series, "autocorr"):
        corr = series.autocorr(lag=1)
        print(f"Lag-1 serial correlation for {col}: {corr:.3f}")

# --- Longest/Average Gap DataFrames ---
longest_gap_df = pd.DataFrame(list(longest_gaps.items()), columns=["Number", "Longest Gap"])
print(longest_gap_df.head())
gap_avgs = {num: np.mean(g) if g else np.nan for num, g in gaps.items()}
avg_gap_df = pd.DataFrame(list(gap_avgs.items()), columns=["Number", "Average Gap"])
print(avg_gap_df.head())

# --- Sums & Trends ---
x = np.arange(len(sum_win))
slope, intercept, rvalue, pvalue, stderr = linregress(x, sum_win)
print(f"Sum trend slope: {slope:.3f}, p-value: {pvalue:.3g}")
if pvalue < 0.05:
    print(f"Significant trend detected: {'Upward' if slope > 0 else 'Downward'}")
else:
    print("No significant trend detected.")
