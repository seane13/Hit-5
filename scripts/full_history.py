import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import date

BASE = "https://www.walottery.com/WinningNumbers/PastDrawings.aspx"

def fetch_year(year: int):
    params = {
        "gamename": "hit5",
        "unittype": "year",
        "unitcount": year,
    }
    r = requests.get(BASE, params=params)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    for date_tag in soup.find_all('p', class_='h2-like'):
        draw_date = date_tag.get_text(strip=True)
        tbl = date_tag.find_parent('th').find_parent('tr').find_parent('thead').find_parent('table')
        for balls_td in tbl.find_all('td', class_='game-balls'):
            nums = [li.get_text(strip=True) for li in balls_td.find_all('li')]
            nums = [n for n in nums if n.isdigit() and 1 <= int(n) <= 42]
            if len(nums) == 5:
                row = [draw_date] + nums
                if row not in results:
                    results.append(row)
    return results

all_results = []
for year in range(2007, date.today().year + 1):
    year_rows = fetch_year(year)
    all_results.extend(year_rows)

df = pd.DataFrame(all_results, columns=["Date", "Num1", "Num2", "Num3", "Num4", "Num5"])
df = df.drop_duplicates().sort_values("Date")
df.to_csv("data/hit5_all_history.csv", index=False)
print(f"Total draws scraped: {len(df)}")
