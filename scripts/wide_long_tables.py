import pandas as pd

# 1) Load
df = pd.read_csv("data/hit5_all_history.csv")

# 2) Parse date, create draw_id
df["Date"] = pd.to_datetime(df["Date"], format="%a, %b %d, %Y")
df = df.sort_values("Date")
df["draw_id"] = range(1, len(df) + 1)

# 3) Rename to Tableau‑friendly names
df = df.rename(columns={
    "Date": "draw_date",
    "Num1": "ball1",
    "Num2": "ball2",
    "Num3": "ball3",
    "Num4": "ball4",
    "Num5": "ball5",
})

# 4) Row‑level features
df["ball_min"] = df[["ball1", "ball2", "ball3", "ball4", "ball5"]].min(axis=1)
df["ball_max"] = df[["ball1", "ball2", "ball3", "ball4", "ball5"]].max(axis=1)
df["ball_sum"] = df[["ball1", "ball2", "ball3", "ball4", "ball5"]].sum(axis=1)

balls = ["ball1", "ball2", "ball3", "ball4", "ball5"]
df["odd_count"] = df[balls].apply(lambda r: sum(v % 2 == 1 for v in r), axis=1)
df["low_count"] = df[balls].apply(lambda r: sum(v <= 21 for v in r), axis=1)

# 5) Save wide table for Tableau
df.to_csv("data/hit5_draws_wide.csv", index=False)

long = (
    df.melt(
        id_vars=["draw_id", "draw_date"],
        value_vars=["ball1", "ball2", "ball3", "ball4", "ball5"],
        var_name="position",
        value_name="number_drawn",
    )
)
long["position"] = long["position"].str.extract(r"(\d+)").astype(int)

long.to_csv("data/hit5_draws_long.csv", index=False)
