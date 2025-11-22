from bs4 import BeautifulSoup
import pandas as pd
import requests

URL = "https://www.walottery.com/WinningNumbers/PastDrawings.aspx?gamename=hit5&unittype=day&unitcount=180"
r = requests.get(URL)
r.raise_for_status()  # This will raise an error if the request failed
soup = BeautifulSoup(r.text, 'html.parser')
# Save HTML
# with open("data/past_180.html", "w", encoding=r.encoding) as f:
#     f.write(r.text)

# # Parse HTML with BeautifulSoup
# soup = BeautifulSoup(r.text, 'html.parser')  # <--

# with open('data/past_180.html') as f:
#     soup = BeautifulSoup(f, 'html.parser')

results = []
# Find all dates
for date_tag in soup.find_all('p', class_='h2-like'):
    date = date_tag.get_text(strip=True)
    # Look for closest table (small or large) after date
    tbl = date_tag.find_parent('th').find_parent('tr').find_parent('thead').find_parent('table')
    # Some tables have numbers in first row <td class="game-balls">
    balls_td = tbl.find('td', class_='game-balls')
    if balls_td:
        numbers = [li.get_text(strip=True) for li in balls_td.find_all('li')]
        numbers = [n for n in numbers if n.isdigit() and 1 <= int(n) <= 42] # Only real numbers
        if len(numbers) == 5:
            results.append([date] + numbers)
    # Some tables (large) may have game-balls in <td class="game-balls" rowspan>
    for balls_td in tbl.find_all('td', class_='game-balls'):
        numbers = [li.get_text(strip=True) for li in balls_td.find_all('li')]
        numbers = [n for n in numbers if n.isdigit() and 1 <= int(n) <= 42]
        if len(numbers) == 5:
            if [date]+numbers not in results:
                results.append([date]+numbers)

df = pd.DataFrame(results, columns=["Date", "Num1", "Num2", "Num3", "Num4", "Num5"])
df.to_csv("data/hit5_clean_manual.csv", index=False)
print(f"Extracted {len(results)} draws to hit5_clean_manual.csv")
