from bs4 import BeautifulSoup
import pandas as pd

with open('Past_180.html') as f:
    soup = BeautifulSoup(f, 'html.parser')

draws = []
dates = soup.find_all('p', class_='h2-like')

for date_tag in dates:
    # date string
    date_str = date_tag.get_text(strip=True)
    # find the next 'td' with class 'game-balls' after this date
    td = date_tag.find_parent('th').find_parent('tr').find_next_sibling('tr')
    if td:
        game_balls_td = td.find('td', class_='game-balls')
        if game_balls_td:
            nums = [li.get_text(strip=True) for li in game_balls_td.find_all('li')]
            # Only take draws with exactly 5 numbers in range 1–42
            nums = [n for n in nums if n.isdigit() and 1 <= int(n) <= 42]
            if len(nums) == 5:
                draws.append([date_str]+nums)

df = pd.DataFrame(draws, columns=["Date", "Num1", "Num2", "Num3", "Num4", "Num5"])
df.to_csv("hit5_clean_manual.csv", index=False)
print(f"Extracted {len(draws)} Hit 5 draws to hit5_clean_manual.csv")
