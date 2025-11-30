import pandas as pd

# Load your CSV (replace with your file path, e.g., Hit5 data)
df = pd.read_csv('data/hit5_all_history.csv')

# Export to TXT (customize sep for space-delimited if needed, e.g., sep=' ')
df.to_csv('data/hit5_all_history.txt', index=False, header=True)  # index=False skips row numbers
