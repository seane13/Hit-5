import pandas as pd
import re

# Read the file as a single column (since the real delimiters seem off)
with open('hit5_historical_numbers.csv', 'r') as f:
    lines = f.readlines()

hit5_draws = []
# A Hit 5 line will have exactly 5 numbers (all 1–42), optionally a date at start
# We'll use regex to match those
number_pat = re.compile(r'(0?[1-4]?\d)[ ,]*(0?[1-4]?\d)[ ,]*(0?[1-4]?\d)[ ,]*(0?[1-4]?\d)[ ,]*(0?[1-4]?\d)\b')

for line in lines:
    # Exclude lines with "POWER PLAY", "$", or extra numbers
    if "POWER PLAY" in line or "," not in line:
        continue
    match = number_pat.search(line)
    if match:
        nums = match.groups()
        nums = [int(n) for n in nums if 1 <= int(n) <= 42]
        if len(nums) == 5:
            hit5_draws.append(nums)

# Save as clean DataFrame
df = pd.DataFrame(hit5_draws, columns=['Num1', 'Num2', 'Num3', 'Num4', 'Num5'])
df.to_csv('hit5_cleaned.csv', index=False)
print(f"Extracted {len(hit5_draws)} Hit 5 draws to hit5_cleaned.csv.")
