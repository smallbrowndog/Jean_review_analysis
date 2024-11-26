import csv
import os
import random
import pandas as pd
from itertools import count
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# ChromeDriver 경로
chrome_driver_path = "./chromedriver-win64/chromedriver.exe"

# Chrome 옵션 설정 (Anti-Detection)
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def scrape_reviews(driver, url, brand, clothing_code):
    driver.get(url)
    sleep(10)  # 페이지 로딩을 위한 초기 대기
    refresh_attempts = 0  # 새로고침 시도 횟수 제한

    reviews_data = []
    seen_reviews = set()  # 중복 체크를 위한 집합
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    max_scroll_attempts = 5  # 최대 스크롤 시도 횟수
    scroll_increment = 300  # 스크롤 시 이동할 픽셀 수

    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR,
                     "#commonLayoutContents > section > div > div.GoodsReviewListSection__Container-sc-1x35scp-0.dMdlme > div:nth-child(8) > div > div > div")
                )
            )
        except TimeoutException:
            print(f"리뷰가 시간 내에 로드되지 않았습니다. 새로고침 시도 중... ({refresh_attempts + 1}/5)")
            refresh_attempts += 1
            if refresh_attempts >= 5:
                print("최대 새로고침 횟수에 도달했습니다. 다음 URL로 이동합니다.")
                break
            driver.refresh()
            sleep(5)
            continue

        # '낮은 평점순' 버튼 클릭
        try:
            sort_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='유용한순']"))
            )
            sort_button.click()
            sleep(2)  # 버튼 클릭 후 잠시 대기

            low_rating_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='낮은 평점순']"))
            )
            low_rating_option.click()
            sleep(5)  # 정렬이 변경된 후 페이지가 업데이트될 시간을 기다림
        except TimeoutException:
            print("정렬 버튼을 찾거나 클릭할 수 없습니다.")

        info_containers = driver.find_elements(By.CSS_SELECTOR, "#commonLayoutContents > section > div > div.GoodsReviewListSection__Container-sc-1x35scp-0.dMdlme > div:nth-child(8) > div > div > div")

        if not info_containers:
            print("리뷰 요소를 찾지 못했습니다.")
            break

        for container in info_containers:
            try:
                # "더보기" 버튼 클릭 로직 추가
                try:
                    more_button = container.find_element(By.XPATH, ".//span[text()='더보기']")
                    driver.execute_script("arguments[0].scrollIntoView(true);", more_button)  # 버튼이 보이도록 스크롤
                    sleep(1)  # 스크롤 후 대기

                    # JavaScript 클릭 사용
                    driver.execute_script("arguments[0].click();", more_button)
                    sleep(2)  # 버튼 클릭 후 잠시 대기
                except NoSuchElementException:
                    print("더보기 버튼이 없습니다. 다음 리뷰로 진행합니다.")
                    continue  # 더보기 버튼이 없으면 다음 리뷰로 넘어감

                # 리뷰 텍스트 수집
                review_elements = container.find_elements(By.CSS_SELECTOR, "span > span:nth-child(1) > span")
                review_text = "<br>".join([element.text for element in review_elements])  # 모든 리뷰를 줄바꿈으로 연결
                rating = container.find_element(By.CSS_SELECTOR, "span.text-body_13px_semi.font-pretendard").text
                review_date = container.find_element(By.CSS_SELECTOR, "span.text-body_13px_reg.text-gray-500.font-pretendard").text
                print(review_text)

                # 중복 체크
                if review_text in seen_reviews:
                    print("중복된 리뷰 발견:", review_text)
                    continue  # 중복된 리뷰는 건너뜀

                # 중복되지 않은 경우, 집합에 추가하고 데이터에 추가
                seen_reviews.add(review_text)
                reviews_data.append({
                    "브랜드": brand,
                    "의류코드": clothing_code,
                    "리뷰": review_text,
                    "별점": rating,
                    "작성일": review_date
                })

            except NoSuchElementException:
                print(f"리뷰 정보에서 필요한 요소를 찾을 수 없습니다.")
                continue
            except StaleElementReferenceException:
                print("Stale element reference error 발생. 요소를 다시 찾습니다.")
                break  # 현재 반복을 종료하고 다음 스크롤로 이동

        # 스크롤을 조금씩 내리기
        driver.execute_script(f"window.scrollTo(0, {last_height + scroll_increment});")
        sleep(5)  # 스크롤 후 대기
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("더 이상 로드할 리뷰가 없습니다.")
            break
        last_height = new_height
        scroll_attempts += 1

    print(f'{len(reviews_data)}개의 데이터가 수집되었습니다')
    return reviews_data


# 여러 URL을 처리하는 메인 함수
def process_urls(folder_path):
    txt_files = [file for file in os.listdir(folder_path) if file.endswith(".txt")]
    all_reviews = []  # 모든 리뷰 데이터를 저장할 리스트

    for txt_file in txt_files:
        file_path = os.path.join(folder_path, txt_file)
        brand_name = os.path.splitext(txt_file)[0]

        # 각 txt 파일에 대한 리뷰 데이터를 저장할 리스트
        reviews_for_current_file = []

        with open(file_path, "r") as file:
            urls = [line.strip() for line in file.readlines()]

        for idx, url in enumerate(urls, start=1):
            print(f"'{brand_name}' - URL {idx}/{len(urls)} 처리 중: {url}")

            driver = get_driver()
            try:
                clothing_code = url.split("/")[-1]
                reviews = scrape_reviews(driver, url, brand_name, clothing_code)
                reviews_for_current_file.extend(reviews)
                all_reviews.extend(reviews)  # 모든 리뷰 데이터에 추가
            except Exception as e:
                print(f"'{brand_name}' 처리 중 오류 발생: {e}")
            finally:
                driver.quit()
                print(f"'{brand_name}'의 드라이버가 종료되었습니다.")

        # 각 txt 파일에 대한 리뷰 데이터를 별도의 CSV 파일로 저장
        if reviews_for_current_file:
            output_file = f"{brand_name}_reviews.csv"
            with open(output_file, "w", newline="", encoding="utf-8-sig") as csvfile:
                fieldnames = ["브랜드", "의류코드", "리뷰", "별점", "작성일"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(reviews_for_current_file)

            print(f"'{brand_name}' 리뷰 데이터가 {output_file}에 저장되었습니다.")
        else:
            print(f"'{brand_name}'에 대한 리뷰 데이터가 없습니다. CSV 파일을 생성하지 않습니다.")

    # 모든 리뷰 데이터를 한 번에 CSV로 저장
    output_file_all = "Data/Original_Data/all_reviews.csv"
    with open(output_file_all, "w", newline="", encoding="utf-8-sig") as csvfile:
        fieldnames = ["브랜드", "의류코드", "리뷰", "별점", "작성일"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_reviews)

    print(f"모든 리뷰 데이터가 {output_file_all}에 저장되었습니다.")

# 스크립트 실행
if __name__ == "__main__":
    process_urls("URL")
