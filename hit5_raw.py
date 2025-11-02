import re
import pandas as pd

# If you paste your data into 'hit5_raw.txt'
with open('hit5_raw.txt') as f:
    data = f.read()

results = []
draw_blocks = re.split(r"\n\s*\n", data)  # Split on blank lines, each block is one draw

for block in draw_blocks:
    # Extract date (may need to adjust pattern for other formats)
    date = re.search(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+\w+\s+\d{1,2},\s+\d{4}", block)
    nums = re.findall(r'\b([0-9]{2})\b', block)
    if date and len(nums) == 5:
        results.append([date.group(0)] + nums)

df = pd.DataFrame(results, columns=["Date", "Num1", "Num2", "Num3", "Num4", "Num5"])
df.to_csv("hit5_formatted.csv", index=False)
print(f"Saved {len(results)} draws to hit5_formatted.csv")
