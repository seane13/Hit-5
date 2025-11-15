from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

options = Options()
# For debugging, you can comment this out to see the browser
# options.add_argument("--headless")
service = Service(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 20)

all_data = []

try:
    driver.get("https://walottery.com/winningnumbers/pastdrawings.aspx")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav.nav-games li[data-game]")))
    hit5_tab = driver.find_element(By.CSS_SELECTOR, "nav.nav-games li[data-game='hit5']")
    driver.execute_script("arguments[0].click();", hit5_tab)
    time.sleep(2)

    # Select date/period from the amount menu
    period_select = Select(driver.find_element(By.CSS_SELECTOR, "select[aria-label='Amount Of Drawings Menu']"))
    period_select.select_by_visible_text("Past 180 Days")
    time.sleep(2)

    # Scrape table rows
    trs = driver.find_elements(By.XPATH, '//table[contains(@class,"table-viewport-small")]//tr')
    print(f"Found {len(trs)} table rows.")

    # --- DEBUG PRINTS: Output text content of the first 20 rows ---
    for i, tr in enumerate(trs[:20]):
        print(f"Row {i+1}: {tr.get_attribute('outerHTML')}")


    # --- Uncomment below to enable normal extraction once the row format is confirmed ---
    # current_date = ""
    # for tr in trs:
    #     try:
    #         ths = tr.find_elements(By.TAG_NAME, "th")
    #         for th in ths:
    #             p = th.find_elements(By.TAG_NAME, "p")
    #             for item in p:
    #                 if 'h2-like' in item.get_attribute('class'):
    #                     current_date = item.text.strip()
    #         td_gameballs = None
    #         try:
    #             td_gameballs = tr.find_element(By.CLASS_NAME, "game-balls")
    #         except Exception:
    #             continue
    #         balls = td_gameballs.find_elements(By.TAG_NAME, "li")
    #         nums = [li.text.strip() for li in balls if li.text.strip().isdigit()]
    #         if len(nums) == 5 and all(0 < int(n) <= 42 for n in nums):
    #             all_data.append([current_date] + nums)
    #     except Exception:
    #         continue

finally:
    driver.quit()

# --- Uncomment below to save after extraction logic is confirmed ---
# df = pd.DataFrame(all_data, columns=["Date", "Num1", "Num2", "Num3", "Num4", "Num5"])
# df.to_csv("hit5_historical_cleaned.csv", index=False)
# print(f"Saved {len(all_data)} Hit 5 draws to hit5_historical_cleaned.csv")
