import pandas as pd
from bs4 import BeautifulSoup
import requests

BASE = "https://www.walottery.com/WinningNumbers/PastDrawings.aspx"
HIST_PATH = "data/hit5_all_history.csv"


def fetch_recent_days(n_days: int = 30):
    """
    Fetch recent Hit 5 draws for the last n_days from WA Lottery.

    Returns:
        List of [Date, Num1, Num2, Num3, Num4, Num5] rows.
    """
    params = {
        "gamename": "hit5",
        "unittype": "day",
        "unitcount": n_days,
    }
    r = requests.get(BASE, params=params)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    for date_tag in soup.find_all("p", class_="h2-like"):
        draw_date = date_tag.get_text(strip=True)

        # Climb up to the table that contains this draw
        tbl = (
            date_tag
            .find_parent("th")
            .find_parent("tr")
            .find_parent("thead")
            .find_parent("table")
        )

        # Some tables have multiple game-balls tds; handle all, avoid duplicates
        for balls_td in tbl.find_all("td", class_="game-balls"):
            nums = [li.get_text(strip=True) for li in balls_td.find_all("li")]
            # Filter out non-number tokens and keep only 1–42
            nums = [n for n in nums if n.isdigit() and 1 <= int(n) <= 42]
            if len(nums) == 5:
                row = [draw_date] + nums
                if row not in results:
                    results.append(row)

    return results


if __name__ == "__main__":
    # Load existing full-history file
    hist = pd.read_csv(HIST_PATH)

    # Scrape recent draws (e.g., last 30 days)
    recent_rows = fetch_recent_days(1)
    recent = pd.DataFrame(
        recent_rows,
        columns=["Date", "Num1", "Num2", "Num3", "Num4", "Num5"],
    )

    # Combine, de-duplicate, and sort
    combined = (
        pd.concat([hist, recent], ignore_index=True)
          .drop_duplicates(subset=["Date", "Num1", "Num2", "Num3", "Num4", "Num5"])
          .sort_values("Date")
    )

    combined.to_csv(HIST_PATH, index=False)
    print(f"After update: {len(combined)} draws")
