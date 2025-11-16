import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
plt.style.use('seaborn-v0_8-darkgrid')

# Frequency plot with number annotations
def plot_number_frequency(freq_dict, title="Number Frequency", xlabel="Number", ylabel="Draws"):
    """
    Plots number frequencies, labeling each bar with its number and frequency count.
    """
    numbers = list(freq_dict.keys())
    counts = list(freq_dict.values())
    plt.figure(figsize=(12, 5))
    bars = plt.bar(numbers, counts, color="dodgerblue")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    for bar, num, count in zip(bars, numbers, counts):
        plt.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.5,  # Just above the bar
            f"{num}\n({count})",  # Number and count on two lines
            ha='center', va='bottom', fontsize=10
        )
    plt.tight_layout()
    plt.show()

# Hot/Warm/Cold plot with categories and number annotations
def plot_hot_warm_cold(freq_dict, hot, warm, cold, title="Hot/Warm/Cold Number Frequency"):
    numbers = sorted(freq_dict.keys())
    counts = [freq_dict[n] for n in numbers]
    colors = [
        'orangered' if n in hot else ('skyblue' if n in cold else 'khaki')
        for n in numbers
    ]
    fig, ax = plt.subplots(figsize=(14, 5))
    bars = ax.bar(numbers, counts, color=colors, edgecolor="k")
    ax.set_xlabel('Number')
    ax.set_ylabel('Frequency')
    ax.set_title(title)
    # Add color legend
    legend_elements = [
        Patch(facecolor='orangered', edgecolor='k', label='Hot'),
        Patch(facecolor='khaki', edgecolor='k', label='Warm'),
        Patch(facecolor='skyblue', edgecolor='k', label='Cold')
    ]
    ax.legend(handles=legend_elements)
    # Annotate each bar with the number
    for bar, n in zip(bars, numbers):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.5,
                str(n),
                ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    plt.show()

def plot_residuals_heatmap(freq_dict, n_numbers, n_draws, expected_per_number, title="Standardized Residuals Heatmap"):
    """
    Plots a heatmap of standardized residuals for each number (Observed - Expected) / sqrt(Expected).
    freq_dict: {number: count}
    n_numbers: total unique numbers (e.g. 42)
    n_draws: total number of draws
    expected_per_number: expected frequency for each number
    """
    numbers = np.arange(1, n_numbers+1)
    observed = np.array([freq_dict.get(i, 0) for i in numbers])
    expected = np.full_like(observed, expected_per_number)
    residuals = (observed - expected) / np.sqrt(expected)
    plt.figure(figsize=(14, 5))
    sns.heatmap([residuals], annot=True, fmt=".1f", cmap="coolwarm", cbar=True, xticklabels=numbers, yticklabels=[""])
    plt.title(title)
    plt.xlabel("Number")
    plt.tight_layout()
    plt.show()

def plot_gap_histogram(gaps_dict, title="Gap Length Distribution", bins=15):
    """
    Plots a histogram of all gap lengths from a dictionary.
    gaps_dict: {number: [gap1, gap2, ...]}
    """
    # Flatten the list of gaps for all numbers
    all_gaps = [gap for gaps in gaps_dict.values() for gap in gaps if gap is not None and np.isfinite(gap)]
    plt.figure(figsize=(8, 4))
    plt.hist(all_gaps, bins=bins, color="slateblue", edgecolor="k", alpha=0.8)
    plt.xlabel("Gap Length (draws between appearances)")
    plt.ylabel("Frequency")
    plt.title(title)
    plt.tight_layout()
    plt.show()

def plot_gap_length_per_number(gaps_dict, title="Gap Lengths by Number"):
    # Create DataFrame: each row = gap, each col = number
    data = {num: gaps for num, gaps in gaps_dict.items() if gaps}
    df = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in data.items()]))
    plt.figure(figsize=(18, 6))
    df.boxplot()
    plt.xlabel("Number")
    plt.ylabel("Gap Length")
    plt.title(title)
    plt.tight_layout()
    plt.show()

def plot_sum_trend(df, number_columns, window=20, title="Sum Trend of Drawn Numbers"):
    """
    Plots the sum of numbers drawn for each draw, with a rolling mean overlay.
    df: DataFrame containing the draws
    number_columns: List of columns with number values
    window: Rolling mean window size (default 20)
    """
    sums = df[number_columns].sum(axis=1)
    rolling = sums.rolling(window).mean()
    plt.figure(figsize=(12, 5))
    plt.plot(sums.index, sums, label="Sum per Draw", color="gray", alpha=0.3)
    plt.plot(rolling.index, rolling, label=f"Rolling Mean (window={window})", color="crimson", linewidth=2)
    plt.xlabel("Draw Index")
    plt.ylabel("Sum of Numbers")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()
