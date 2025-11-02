from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# --- CONFIGURATION ---

# Path to your chromedriver, if not in PATH:
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'  # Update if needed

# Target range; adjust years as needed
START_YEAR = 2007
END_YEAR = 2025

# --- SCRIPT START ---

options = Options()
# options.add_argument("--headless")  # Run without opening browser window
options.add_argument("--disable-gpu")  # Recommended for headless mode stability

service = Service(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

all_data = []

try:
    for year in range(START_YEAR, END_YEAR + 1):
        url = f"https://walottery.com/WinningNumbers/PastDrawings.aspx?unittype=year&unitcount={year}&game=hit5"
        print(f"Processing year: {year}")
        driver.get(url)
        time.sleep(3)  # Allow dynamic content to load
        print(driver.page_source[:5000])  # Limit printout for sanity


        tables = driver.find_elements(By.TAG_NAME, 'table')
        if not tables:
            print(f"No tables found for {year}")
            continue

        # Usually one of the first tables on the page
        for table in tables:
            rows = table.find_elements(By.TAG_NAME, 'tr')
            # Skip header row
            for row in rows[1:]:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 6:  # Check for enough columns
                    record = {
                        "Date": cols[0].text.strip(),
                        "Number1": cols[1].text.strip(),
                        "Number2": cols[2].text.strip(),
                        "Number3": cols[3].text.strip(),
                        "Number4": cols[4].text.strip(),
                        "Number5": cols[5].text.strip()
                    }
                    all_data.append(record)
        print(f"Year {year} complete. Total draws so far: {len(all_data)}")

finally:
    driver.quit()

# --- SAVE DATA ---
df = pd.DataFrame(all_data)
df.drop_duplicates(inplace=True)
df.to_csv("hit5_historical_numbers.csv", index=False)
print("All done. Data saved to hit5_historical_numbers.csv")
