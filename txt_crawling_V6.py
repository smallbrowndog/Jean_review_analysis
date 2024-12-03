import csv
import os
import random
import pandas as pd
from itertools import count
from time import sleep, time

from numpy.lib.user_array import container
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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

def format_time(seconds):
    """초를 분과 초로 변환하여 'n분 n초' 형식으로 반환"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}분 {seconds}초"

def scrape_reviews(driver, url, brand, clothing_code, sort_order):
    start_time = time()  # 시작 시간 기록
    driver.get(url)
    sleep(5)  # 페이지 로딩을 위한 초기 대기

    reviews_data = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    refresh_attempts = 0  # 새로고침 시도 횟수 제한

    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "#commonLayoutContents > section > div > div.GoodsReviewListSection__Container-sc-1x35scp-0.dMdlme > div:nth-child(8) > div > div > div")
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

        # 정렬 기준 변경
        try:
            sort_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='유용한순']"))
            )
            sort_button.click()
            sleep(2)  # 버튼 클릭 후 잠시 대기

            order_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//span[text()='{sort_order}']"))
            )
            order_option.click()
            sleep(5)  # 정렬이 변경된 후 페이지가 업데이트될 시간을 기다림
        except TimeoutException:
            print(f"'{sort_order}' 정렬 버튼을 찾거나 클릭할 수 없습니다.")

        info_containers = driver.find_elements(By.CSS_SELECTOR, "#commonLayoutContents > section > div > div.GoodsReviewListSection__Container-sc-1x35scp-0.dMdlme > div:nth-child(8) > div > div > div")

        if not info_containers:
            print("리뷰 요소를 찾지 못했습니다.")

        min_length = len(info_containers)
        for i in range(min_length):
            try:
                container = info_containers[i]
                # try:
                #     more_button = WebDriverWait(container, 2).until(
                #     EC.presence_of_element_located((By.XPATH, ".//span[text()='더보기']"))
                #     )
                #     driver.execute_script("arguments[0].click();", more_button)
                # except TimeoutException:
                #     print("더보기 버튼이 로드되지 않았습니다. 다음 리뷰로 진행합니다.")
                #     continue  # 더보기 버튼이 없으면 다음 리뷰로 넘어감

                review_elements = container.find_elements(By.CSS_SELECTOR, "span > span:nth-child(1) > span")
                review_text = "<br>".join([element.text for element in review_elements])  # 모든 리뷰를 줄바꿈으로 연결
                rating = info_containers[i].find_element(By.CSS_SELECTOR, "span.text-body_13px_semi.font-pretendard").text
                review_date = info_containers[i].find_element(By.CSS_SELECTOR, "span.text-body_13px_reg.text-gray-500.font-pretendard").text
                print(review_text)
                print(rating)
                print(review_date)

                # 낮은 평점순일 때만 평점이 5인 경우 수집 중단
                if sort_order == '낮은 평점순' and rating == "4":
                    print("평점이 4인 리뷰를 발견했습니다. 수집을 중단합니다.")
                    end_time = time()  # 종료 시간 기록
                    elapsed_time = end_time - start_time  # 소요 시간 계산
                    print(f'한 리뷰 수집에 걸린 시간: {format_time(elapsed_time)}')
                    print(f'{len(reviews_data)}개의 데이터가 수집되었습니다')
                    return reviews_data

                reviews_data.append({
                    "브랜드": brand,
                    "의류코드": clothing_code,
                    "리뷰": review_text,
                    "별점": rating,
                    "작성일": review_date
                })

            except NoSuchElementException:
                print(f"리뷰 {i}에서 필요한 정보를 찾을 수 없습니다.")
                continue

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(random.uniform(2, 4))
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("더 이상 로드할 리뷰가 없습니다.")
            break
        last_height = new_height
        scroll_attempts += 1

    end_time = time()  # 종료 시간 기록
    elapsed_time = end_time - start_time  # 소요 시간 계산
    print(f'한 리뷰 수집에 걸린 시간: {format_time(elapsed_time)}')

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
            start_url_time = time()  # URL 처리 시작 시간 기록
            try:
                clothing_code = url.split("/")[-1]
                # for sort_order in ['낮은 평점순', '높은 평점순']:
                for sort_order in ['낮은 평점순']:
                    reviews = scrape_reviews(driver, url, brand_name, clothing_code, sort_order)
                    reviews_for_current_file.extend(reviews)
                    all_reviews.extend(reviews)  # 모든 리뷰 데이터에 추가
            except Exception as e:
                print(f"'{brand_name}' 처리 중 오류 발생: {e}")
            finally:
                driver.quit()
                end_url_time = time()  # URL 처리 종료 시간 기록
                url_elapsed_time = end_url_time - start_url_time  # 소요 시간 계산
                print(f"'{brand_name}'의 URL 수집에 걸린 시간: {format_time(url_elapsed_time)}")
                print(f"'{brand_name}'의 드라이버가 종료되었습니다.")

        # 각 txt 파일에 대한 리뷰 데이터를 별도의 CSV 파일로 저장
        if reviews_for_current_file:
            # output_file = f"{brand_name}_reviews.csv"
            output_file = f"{brand_name}_row_reviews.csv"
            with open(output_file, "w", newline="", encoding="utf-8-sig") as csvfile:
                fieldnames = ["브랜드", "의류코드", "리뷰", "별점", "작성일"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(reviews_for_current_file)

            print(f"'{brand_name}' 리뷰 데이터가 {output_file}에 저장되었습니다.")
        else:
            print(f"'{brand_name}'에 대한 리뷰 데이터가 없습니다. CSV 파일을 생성하지 않습니다.")

    # 모든 리뷰 데이터를 한 번에 CSV로 저장
    # output_file_all = "all_reviews.csv"
    with open(output_file_all, "w", newline="", encoding="utf-8-sig") as csvfile:
        fieldnames = ["브랜드", "의류코드", "리뷰", "별점", "작성일"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_reviews)

    print(f"모든 리뷰 데이터가 {output_file_all}에 저장되었습니다.")

# 스크립트 실행
if __name__ == "__main__":
    process_urls("URL")
