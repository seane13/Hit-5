import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

plt.style.use('seaborn-v0_8-darkgrid')  # Nice default style

def plot_number_frequency(freq_dict, title="Number Frequency", xlabel="Number", ylabel="Draws"):
    """
    freq_dict: {number: count}
    """
    numbers = list(freq_dict.keys())
    counts = list(freq_dict.values())
    plt.figure(figsize=(10, 5))
    plt.bar(numbers, counts, color="dodgerblue")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.show()


def plot_gap_histogram(gaps_dict, title="Gap Histogram", bins=15):
    """
    gaps_dict: {number: [gap1, gap2, ...]}
    Plots all gaps together as one histogram.
    """
    all_gaps = [gap for gaps in gaps_dict.values() for gap in gaps if gap is not None]
    plt.figure(figsize=(8, 4))
    plt.hist(all_gaps, bins=bins, color="slateblue", edgecolor="k", alpha=0.7)
    plt.xlabel("Gap Length")
    plt.ylabel("Frequency")
    plt.title(title)
    plt.tight_layout()
    plt.show()


def plot_sum_trend(df, number_columns, window=20):
    """
    Plots the rolling average sum of drawn numbers by draw order.
    """
    sums = df[number_columns].sum(axis=1)
    rolling = sums.rolling(window).mean()
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(sums)), sums, label="Sum of numbers", alpha=0.3)
    plt.plot(range(len(rolling)), rolling, label=f"Rolling Mean ({window})", color="crimson")
    plt.xlabel("Draw Index")
    plt.ylabel("Sum of Numbers")
    plt.title("Rolling Trend of Draw Sums")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_hot_warm_cold(freq_dict, hot, warm, cold, title="Hot/Warm/Cold Number Frequency"):
    """
    freq_dict: {number: count}
    hot, warm, cold: lists of numbers
    Different color for each category.
    """
    numbers = sorted(freq_dict.keys())
    counts = [freq_dict[n] for n in numbers]
    colors = []
    for n in numbers:
        if n in hot:
            colors.append("orangered")
        elif n in cold:
            colors.append("skyblue")
        else:
            colors.append("khaki")
    plt.figure(figsize=(12, 5))
    plt.bar(numbers, counts, color=colors, edgecolor="k")
    plt.xlabel("Number")
    plt.ylabel("Frequency")
    plt.title(title)
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='orangered', edgecolor='k', label='Hot'),
                      Patch(facecolor='khaki', edgecolor='k', label='Warm'),
                      Patch(facecolor='skyblue', edgecolor='k', label='Cold')]
    plt.legend(handles=legend_elements)
    plt.tight_layout()
    plt.show()
