import pandas as pd
from pandas.plotting import autocorrelation_plot
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chisquare, stats, norm, linregress
from statsmodels.sandbox.stats.runs import runstest_1samp
from itertools import combinations
import math

# Load CSV
df = pd.read_csv('hit5_clean_deduped.csv')
draws = df[number_columns].values

number_columns = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
all_numbers = pd.concat([df[col] for col in number_columns], ignore_index=True)

frequency = all_numbers.value_counts().sort_index()
frequency_df = frequency.reset_index().rename(columns={'index': 'Number', 0: 'Frequency'})
frequency_df = frequency_df.sort_values(by='count', ascending=False)
print(frequency_df.to_string(index=False))

# Hot/cold:
all_numbers = pd.Series(draws.flatten())
frequency = all_numbers.value_counts().sort_index()
mean_freq = frequency.mean()
std_freq = frequency.std()
hot = frequency[frequency > mean_freq + std_freq]
cold = frequency[frequency < mean_freq - std_freq]
print("Hot numbers (more frequent):", hot.to_dict())
print("Cold numbers (less frequent):", cold.to_dict())

summary = {
    'Total draws': len(df),                         # Number of draw rows
    'Total numbers': all_numbers.count(),           # Total numbers drawn (draws x 5)
    'Mean': all_numbers.mean(),                     # Average drawn number
    'Median': all_numbers.median(),                 # Middle value (after sorting)
    'Standard Deviation': all_numbers.std(),        # Spread of data
    'Minimum': all_numbers.min(),                   # Smallest drawn number
    'Maximum': all_numbers.max(),                   # Largest drawn number
    '25% Quantile': all_numbers.quantile(0.25),     # Lower quartile
    '75% Quantile': all_numbers.quantile(0.75),     # Upper quartile
    'Mode': all_numbers.mode().tolist()             # Most common drawn number(s)
}

print(f"Total Draws: {summary['Total draws']}")
print(f"Total numbers: {summary['Total numbers']}")
print(f"Mean: {summary['Mean']}")
print(f"Median: {summary['Median']}")
print(f"Standard Deviation: {summary['Standard Deviation']}")
print(f"Minimum: {summary['Minimum']}")
print(f"Maximum: {summary['Maximum']}")
print(f"25% Quantile': {summary['25% Quantile']}")
print(f"75% Quantile': {summary['75% Quantile']}")
print(f"Mode: {summary['Mode']}")

# Consecutive Numbers
consecutive_draws = [(np.diff(np.sort(row)) == 1).sum() for row in draws]
total_with_consecutive = sum(x > 0 for x in consecutive_draws)
max_consecutive = max(consecutive_draws)
percent_with_consecutive = 100 * total_with_consecutive / len(draws)
print(f"Draws with at least one pair of consecutive numbers: {total_with_consecutive}")
print(f"Max pairs of consecutive numbers in any draw: {max_consecutive}")
print(f"Percent of draws with at least one consecutive pair: {percent_with_consecutive:.1f}%")

# Temporal pattern: diff between same positions
diff_matrix = np.diff(draws, axis=0)
mean_diff = diff_matrix.mean()
std_diff = diff_matrix.std()
print(f"Mean gap/difference between same column in sequential draws: {mean_diff:.2f}")
print(f"Standard deviation of difference: {std_diff:.2f}")

all_possible_numbers = range(1, 43)
all_numbers = pd.concat([df[col] for col in number_columns], ignore_index=True)
empirical_probs = all_numbers.value_counts(normalize=True).reindex(all_possible_numbers, fill_value=0)
theoretical_prob = 1/42  # For 42 possible numbers
prob_df = pd.DataFrame({
    "Number": all_possible_numbers,
    "Empirical Probability": empirical_probs.values,
    "Theoretical Probability": theoretical_prob
})
display(prob_df.head(10))

# plot all probabilities
prob_df.plot(x="Number", y=["Empirical Probability", "Theoretical Probability"], kind="bar", figsize=(12,5))
plt.title("Empirical vs Theoretical Probability by Number")
plt.show()

positions = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
number_to_analyze = 12  # Example (change to any number you want)

plt.figure(figsize=(14, 8))

for pos in positions:
    # Binary column: did number_to_analyze appear at this position for each draw?
    col_indicator = (df_date[pos] == number_to_analyze).astype(int)
    trend = col_indicator.cumsum()
    plt.plot(df_date['Date'], trend, label=pos)

plt.xlabel('Draw Date')
plt.ylabel(f'Cumulative Appearances of {number_to_analyze}')
plt.title(f'Per-Position Cumulative Trend for Number {number_to_analyze}')
plt.legend()
plt.tight_layout()
plt.show()

# 30 day window


window = 30  # rolling window size
positions = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
number_to_analyze = 12  # Example: change to any number

plt.figure(figsize=(14,8))
for pos in positions:
    indicator = (df_date[pos] == number_to_analyze).astype(int)
    rolling_freq = indicator.rolling(window=window, min_periods=1).sum()
    plt.plot(df['Date'], rolling_freq, label=pos)

plt.xlabel('Draw Date')
plt.ylabel(f'Rolling {window}-Draw Frequency for {number_to_analyze}')
plt.title(f'Rolling {window}-Draw Frequency by Position: Number {number_to_analyze}')
plt.legend()
plt.tight_layout()
plt.show()

# Randomness
# Example: Use median to convert numbers to 0/1 (above/below median)

median = all_numbers.median()
binary_seq = (all_numbers > median).astype(int)
z_stat, p_val = runstest_1samp(binary_seq, correction=True)
print(f"Runs test z-statistic: {z_stat:.2f}")
print(f"p-value: {p_val:.4f}")
if p_val < 0.05:
    print('Sequence shows non-randomness (reject H0).')
else:
    print('Sequence order appears random (cannot reject H0).')

df = pd.read_csv('hit5_clean_deduped.csv')
positions = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']

print("Lag-1 Serial Correlation by Position:")
for pos in positions:
    seq = df[pos].dropna()
    corr = seq.autocorr(lag=1)
    # Test for significance
    n = len(seq)
    if abs(corr) < 1:  # avoid divide by zero
        z = corr * np.sqrt((n-2) / (1 - corr**2))
        p_value = 2 * (1 - norm.cdf(abs(z)))
    else:
        z, p_value = np.nan, np.nan
    print(f"{pos}: r={corr:.3f}, z-score={z:.2f}, p-value={p_value:.4f}")
    if p_value < 0.05:
        print(f"  Significant correlation detected in {pos}. (Reject H0 of independence)")
    else:
        print(f"  No significant correlation in {pos}. (Cannot reject H0, sequence appears independent)")

all_possible_numbers = range(1, 43)
longest_gap = {}

# For each number, determine the largest interval between appearances
for num in all_possible_numbers:
    # Locate every row where num appears
    hits = df[number_columns].apply(lambda row: num in row.values, axis=1)
    hit_indices = np.where(hits)[0]
    if len(hit_indices) > 0:
        # Calculate gaps between each occurrence
        gaps = np.diff(hit_indices)
        max_gap = gaps.max() if len(gaps) > 0 else len(df) - 1
        # Consider from last hit to end
        last_gap = len(df) - 1 - hit_indices[-1]
        # Consider from start to first hit
        first_gap = hit_indices[0]
        overall_max = max(max_gap, last_gap, first_gap)
    else:
        overall_max = len(df)  # never appeared
    longest_gap[num] = overall_max

# Convert to DataFrame and (optional) save to CSV
longest_gap_df = pd.DataFrame(list(longest_gap.items()), columns=['Number', 'Longest Gap'])
longest_gap_df = longest_gap_df.sort_values('Longest Gap', ascending=False)
longest_gap_df.to_csv('hit5_longest_gaps.csv', index=False)

# Display top 15
print(longest_gap_df.head(15).to_string(index=False))

gap_dict = {}

for num in all_possible_numbers:
    hits = df[number_columns].apply(lambda row: num in row.values, axis=1)
    hit_indices = np.where(hits)[0]
    if len(hit_indices) > 1:
        gaps = np.diff(hit_indices)
        avg_gap = gaps.mean() if len(gaps) > 0 else np.nan
        gap_dict[num] = avg_gap
    else:
        gap_dict[num] = np.nan  # Not enough data for gap calculation

average_gap_df = pd.DataFrame(list(gap_dict.items()), columns=['Number', 'Average Gap'])
print(average_gap_df.to_string(index=False))

# Overall average of gaps for all numbers:
overall_avg_gap = average_gap_df['Average Gap'].mean()
print(f'Overall average gap for all numbers: {overall_avg_gap:.2f}')


# Trends in the sum of all numbers

df['sum_win'] = df[['Num1', 'Num2', 'Num3', 'Num4', 'Num5']].sum(axis=1)

 If you have a date column
plt.figure(figsize=(14, 6))
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])
    plt.plot(df['Date'], df['sum_win'], label='Sum of Winning Numbers', color='slateblue')
else:
    plt.plot(df.index, df['sum_win'], label='Sum of Winning Numbers', color='slateblue')
plt.xlabel('Draw Date')
plt.ylabel('Sum of Winning Numbers')
plt.title('Trend in the Sum of All Winning Numbers')
plt.legend()
plt.tight_layout()
plt.show()

# Use draw number instead of index for safe calculation
trend_corr = df['sum_win'].corr(pd.Series(range(len(df))))
print(f'Correlation (sum vs. draw order): {trend_corr:.3f}')

trend_stats = {
    'mean_sum': df['sum_win'].mean(),
    'std_sum': df['sum_win'].std(),
    'min_sum': df['sum_win'].min(),
    'max_sum': df['sum_win'].max(),
    'trend_correlation': trend_corr
}
print(trend_stats)

# looking for trends or shifts in sums
# add sum column
df['sum_win'] = df[number_columns].sum(axis=1)
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')


window = 30  # Adjust window size as needed
df['rolling_mean'] = df['sum_win'].rolling(window=window, min_periods=1).mean()

plt.figure(figsize=(14,6))
if 'Date' in df.columns:
    x_vals = df['Date']
else:
    x_vals = df.index
plt.plot(x_vals, df['sum_win'], alpha=0.4, label='Sum of Winning Numbers')
plt.plot(x_vals, df['rolling_mean'], color='red', label=f'{window}-Draw Rolling Mean')
plt.title('Sum of Winning Numbers & Trend (Rolling Mean)')
plt.legend()
plt.tight_layout()
plt.show()

x = np.arange(len(df))
y = df['sum_win'].values
slope, intercept, r_value, p_value, std_err = linregress(x, y)
print(f'Trend: slope={slope:.3f}, p={p_value:.3g}')
if p_value < 0.05:
    print('Significant trend detected.')
    if slope > 0:
        print('Upward trend.')
    else:
        print('Downward trend.')
else:
    print('No significant trend detected.')

autocorrelation_plot(df['sum_win'])
plt.title('Autocorrelation of Sum of Winning Numbers')
plt.show()

min_sum = df['sum_win'].min()
max_sum = df['sum_win'].max()
mean_sum = df['sum_win'].mean()
print(f"Minimum Sum of wining numbers: {min_sum}")
print(f"max_sum Sum of wining numbers: {max_sum}")
print(f"mean_sum Sum of wining numbers:{mean_sum}")

day_to_day_changes = df['sum_win'].diff().dropna()
mean_change = day_to_day_changes.mean()
std_change = day_to_day_changes.std()
print(f" Day to day changes: \n{day_to_day_changes}")
print(f" Mean change: {mean_change}")
print(f" Standard Deviation change: {std_change}")

corr_lag1 = df['sum_win'].autocorr(lag=1)
print(f"Day to day correlation: {corr_lag1}")

# Average range of sums
window = 10
rolling_range = df['sum_win'].rolling(window=window).apply(lambda x: x.max() - x.min(), raw=True)
avg_range = rolling_range.dropna().mean()
print(f'Average range (window={window}): {avg_range:.2f}')

# Predicted not to win by frequency
freq = all_numbers.value_counts().reindex(range(1, 43), fill_value=0)
not_winning = freq.nsmallest(21).index.tolist()
print("Predicted not to win:", not_winning)

gaps = {}
for num in range(1, 43):
    hits = df[number_columns].apply(lambda row: num in row.values, axis=1)
    hit_indices = np.where(hits)[0]
    if len(hit_indices) > 0:
        gaps[num] = len(df) - 1 - hit_indices[-1]
    else:
        gaps[num] = len(df)
gap_since_last_hit = pd.Series(gaps)

rolling_window = 30
rolling_freq = {}
for num in range(1, 43):
    recent_hits = df[number_columns].tail(rolling_window).apply(lambda row: num in row.values, axis=1)
    rolling_freq[num] = recent_hits.sum()
rolling_freq = pd.Series(rolling_freq)

frequency_norm = (frequency - frequency.min()) / (frequency.max() - frequency.min())
gap_norm = (gap_since_last_hit - gap_since_last_hit.min()) / (gap_since_last_hit.max() - gap_since_last_hit.min())
rolling_norm = (rolling_freq - rolling_freq.min()) / (rolling_freq.max() - rolling_freq.min())

score = (1 - frequency_norm) + gap_norm + (1 - rolling_norm)
ranked = score.sort_values(ascending=False)
print("Predicted not to win:", ranked.head(21).index.tolist())

# total number of combos using half of the available numbers
n = 21  # half the lottery pool
k = 5   # picks per draw

total_combinations = math.comb(n, k)
print(f"Total number of 5-number combinations from 21 numbers: {total_combinations}")
