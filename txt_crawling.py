import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
import random

# ChromeDriver Path
chrome_driver_path = "chromedriver-win64/chromedriver.exe"  # Update with your path

# Configure Chrome Options for Anti-Detection
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Set up Chrome Driver
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # Anti-Detection Script to Hide Webdriver Properties
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

# Read URLs from url.txt
def read_urls(file_path):
    with open(file_path, "r") as file:
        urls = [line.strip() for line in file.readlines()]
    return urls

# Function to scrape reviews from a single URL
def scrape_reviews(driver, url):
    driver.get(url)
    sleep(20)  # Allow the page to load

    # Select "최신순" option
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.SelectMenu__MenuContent-sc-1i5zu14-4"))
        )
        latest_option = driver.find_element(By.XPATH, "//span[text()='최신순']")
        latest_option.click()
        print(f"Selected '최신순' for URL: {url}")
        sleep(2)
    except TimeoutException:
        print(f"Could not find the select menu or '최신순' option for URL: {url}")

    reviews_data = []  # List to store review data
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Wait for reviews to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "p.text-body_13px_reg.ReviewContentExpandable__TextContainer-sc-14vwok6-1"))
            )
        except TimeoutException:
            print("Reviews did not load in time.")
            break

        # Find review content, rating, and date containers
        review_elements = driver.find_elements(By.CSS_SELECTOR, "p.text-body_13px_reg.ReviewContentExpandable__TextContainer-sc-14vwok6-1")
        info_containers = driver.find_elements(By.CSS_SELECTOR, "div.ReviewSubInfo__Container-sc-1j4ti7g-0")

        for i in range(len(review_elements)):
            try:
                # Extract review text
                review_text = review_elements[i].text
                # Extract rating and date
                rating = info_containers[i].find_element(By.CSS_SELECTOR, "span.text-body_14px_semi.font-pretendard").text
                review_date = info_containers[i].find_element(By.CSS_SELECTOR, "span.text-body_13px_reg.text-gray-600.font-pretendard").text

                # Add data to list
                reviews_data.append({
                    "Review": review_text,
                    "Rating": rating,
                    "Date": review_date
                })

                print(f"Review found: {review_text[:60]}... | Rating: {rating} | Date: {review_date}")

            except NoSuchElementException:
                print(f"Missing rating or date for review at index {i}.")
                continue

        # Scroll down to load more reviews
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(random.uniform(2, 4))

        # Check if more content has loaded
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("No more reviews to load.")
            break
        last_height = new_height

    return reviews_data

# Main function to process multiple URLs
def process_urls(url_file):
    urls = read_urls(url_file)

    for idx, url in enumerate(urls, start=1):
        print(f"Processing URL {idx}/{len(urls)}: {url}")

        # Start a new ChromeDriver instance for each URL
        driver = get_driver()
        try:
            reviews = scrape_reviews(driver, url)

            # Save reviews to a CSV file
            output_file = f"reviews_{idx}.csv"
            with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Review", "Rating", "Date"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for review in reviews:
                    writer.writerow(review)

            print(f"Data for URL {idx} saved to {output_file}")
        except Exception as e:
            print(f"An error occurred while processing URL {idx}: {e}")
        finally:
            driver.quit()
            print(f"Driver closed for URL {idx}")

# Run the script
if __name__ == "__main__":
    process_urls("./URL/url.txt")