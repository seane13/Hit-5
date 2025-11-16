import re
import pandas as pd

lines = []
with open("hit5_historical_numbers.csv") as f:
    for line in f:
        # Skip lines containing 'POWER PLAY' or containing too many numbers
        if "POWER PLAY" in line:
            continue
        # Match lines with exactly 5 numbers between 1 and 42 (allowing spaces or commas)
        numbers = re.findall(r'\b([1-9]|1\d|2\d|3\d|4[0-2])\b', line)
        if len(numbers) == 5:
            lines.append(numbers)

df = pd.DataFrame(lines, columns=["Num1","Num2","Num3","Num4","Num5"])
df.to_csv("hit5_cleaned.csv", index=False)
print(f"Extracted {len(lines)} Hit 5 draws to hit5_cleaned.csv")
