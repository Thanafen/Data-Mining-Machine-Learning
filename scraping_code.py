#install imports

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
import time
import random
import csv
import sys

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = uc.Chrome(options=options, version_main=145)
    except Exception as e:
        print(f"Failed to start Chrome: {e}")
        print("Tip: Delete the folder %appdata%/undetected_chromedriver and try again.")
        sys.exit()

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver

def scrape_trustpilot_reviews(driver, company, page_no):
    url = f"https://www.trustpilot.com/review/{company}?page={page_no}"
    
    #Try the page up to 3 times
    for attempt in range(3):
        print(f"Scraping {company} - Page {page_no} (Attempt {attempt+1})")
        driver.get(url)
        
        #Random delay to emulate human behavior
        time.sleep(random.uniform(6.0, 10.0)) 

        #Scroll to load dynamic content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            #Check for block/challenge
            if "challenge" in driver.title.lower() or "blocked" in driver.title.lower():
                print("BLOCK DETECTED")
                print("Wait 20 seconds...")
                time.sleep(20)
                continue 

            reviews_list = driver.find_element(By.XPATH, "//div[@data-reviews-list-start='true']")
            reviews = reviews_list.find_elements(By.TAG_NAME, "article")

            data = []
            for review in reviews:
                try:
                    title = review.find_element(By.XPATH, ".//h2[@data-service-review-title-typography='true']").text
                    rating = review.find_element(By.XPATH, ".//div[@data-service-review-rating]").get_attribute('data-service-review-rating')
                    
                    try:
                        content = review.find_element(By.XPATH, ".//p[@data-service-review-text-typography='true']").text
                    except:
                        content = ""

                    data.append([title, rating, content])
                except:
                    continue 

            if data:
                return data
                
        except Exception as e:
            print(f"Element not found on page {page_no}. Content might be blocked.")
            time.sleep(5)
            
    return []


company = "ilmakiage.co.uk"
filename = "review_data.csv"
driver = get_driver()

try:
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        csv_file = csv.writer(file)
        if file.tell() == 0:
            csv_file.writerow(['title', 'rating', 'review'])

        #Loop through pages (switch the range parameters manually, more than 10 at a time triggers detection)
        for page in range(1, 10): 
            page_data = scrape_trustpilot_reviews(driver, company, page)
            
            if page_data:
                csv_file.writerows(page_data)
                print(f"Successfully saved {len(page_data)} reviews from page {page}")
            else:
                print(f"Failed to retrieve page {page} after multiple attempts.")
                # Optional: break or wait longer
            
            #Adding delay times between each page to avoid detection
            wait_time = random.uniform(15, 25)
            print(f"Waiting {int(wait_time)}s before next page...")
            time.sleep(wait_time)

finally:
    print("Scraping finished or interrupted")
    driver.quit()