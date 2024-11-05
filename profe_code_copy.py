import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
import random

# ChromeDriver 경로 설정
chrome_driver_path = "./chromedriver-win64/chromedriver.exe"  # 사용자의 경로로 업데이트

# Chrome 옵션 설정 (Anti-Detection)
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")

# Chrome Driver 설정
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Anti-Detection 스크립트 - Webdriver 속성을 숨김
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
})

# 스크래핑할 URL
brand_url = "https://www.musinsa.com/brand/musinsastandard?categoryCode=003002&gf=A"
review_url = "https://www.musinsa.com/review/goods/1555407"

#브랜드 url, 의류코드 크롤링
def crawl_brand():
    # 입력받은 URL 열기
    driver.get(brand_url)
    # 페이지가 완전히 로드되도록 초기 대기 시간 설정
    sleep(20)

    brand_code = []  # 브랜드, 의류코드를 저장할 리스트
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # 페이지가 로드될 때까지 대기
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "p.text-body_13px_reg.ReviewContentExpandable__TextContainer-sc-14vwok6-1"))
            )
        except TimeoutException:
            print("페이지가 시간 내에 로드되지 않았습니다.")
            break

        # 페이지에서 브랜드, 의류코드, 제품명, 가격 컨테이너 찾기
        brand_elements = driver.find_elements(By.CSS_SELECTOR,
                                               "text-etc_22px_med font-semibold sc-hm89qk-5 kXAuqX text-black font-pretendard")
        info_containers = driver.find_elements(By.CSS_SELECTOR, "div.sc-f39157-1 dqBVvr")

        # 정보를 추출하여 리스트에 저장
        for i in range(0, 10):
            try:
                # 브랜드 추출
                Brand = brand_elements[i].text

                # 의류코드, 제품명, 가격 추출
                ClothesCode = info_containers[i].find_element(By.CSS_SELECTOR,
                                                         "span.text-body_14px_semi.font-pretendard").text

                # 데이터 리스트에 추가
                brand_code.append({
                    "Brand": Brand,
                    "ClothesCode": ClothesCode,
                    "PName": PName,
                    "Price": Price
                })

                # 진행 상황 출력
                print(f"브랜드: {review_text[:]}... | 의류: {ClothesCode}")

            except NoSuchElementException:
                print(f"브랜드 및 의류코드를 검색할 수 없습니다")
                continue

        # 스크롤을 내려 추가 로드
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(random.uniform(4, 15))

        # 새로운 콘텐츠가 로드되었는지 확인
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("더 이상 로드할 리뷰가 없습니다.")
            break
        last_height = new_height

    return brand_code


# 스크롤 및 리뷰, 평점, 작성일자 스크래핑 함수
def scrape_reviews():
    driver.get(review_url)
    sleep(20)
    reviews_data = []  # 각 리뷰 데이터를 저장할 리스트
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # 리뷰가 로드될 때까지 대기
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "p.text-body_13px_reg.ReviewContentExpandable__TextContainer-sc-14vwok6-1"))
            )
        except TimeoutException:
            print("리뷰가 시간 내에 로드되지 않았습니다.")
            break

        # 페이지에서 리뷰 내용, 평점, 날짜 컨테이너 찾기
        review_elements = driver.find_elements(By.CSS_SELECTOR,
                                               "p.text-body_13px_reg.ReviewContentExpandable__TextContainer-sc-14vwok6-1")
        info_containers = driver.find_elements(By.CSS_SELECTOR, "div.ReviewSubInfo__Container-sc-1j4ti7g-0")

        # 정보를 추출하여 리스트에 저장
        for i in range(len(review_elements)):
            try:
                # 리뷰 텍스트 추출
                review_text = review_elements[i].text

                # 평점과 날짜 추출
                rating = info_containers[i].find_element(By.CSS_SELECTOR,
                                                         "span.text-body_14px_semi.font-pretendard").text
                review_date = info_containers[i].find_element(By.CSS_SELECTOR,
                                                              "span.text-body_13px_reg.text-gray-600.font-pretendard").text

                # 데이터 리스트에 추가
                reviews_data.append({
                    "Review": review_text,
                    "Rating": rating,
                    "Date": review_date
                })

                # 진행 상황 출력
                print(f"리뷰: {review_text[:]}... | 평점: {rating} | 작성일자: {review_date}")

            except NoSuchElementException:
                print(f"{i}번째 리뷰에서 평점 또는 날짜를 찾을 수 없습니다.")
                continue

        # 스크롤을 내려 추가 리뷰 로드
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(random.uniform(4, 15))

        # 새로운 콘텐츠가 로드되었는지 확인
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("더 이상 로드할 리뷰가 없습니다.")
            break
        last_height = new_height

    return reviews_data


# 리뷰 스크래핑 시작
try:
    reviews_data = crawl_brand()
    reviews_data.append(scrape_reviews())
    print(f"총 스크래핑된 리뷰 수: {len(reviews_data)}")

    # CSV 파일로 저장
    with open("musinsa_reviews2.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Brand", "ClothesCode", "PName", "Price","Review", "Rating", "Date"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()  # 헤더 작성
        for review in reviews_data:
            writer.writerow(review)  # 각 리뷰 데이터 작성

    print("데이터가 musinsa_reviews.csv 파일에 저장되었습니다.")

except Exception as e:
    print(f"오류가 발생했습니다: {e}")

finally:
    driver.quit()

print("스크래핑 완료.")
