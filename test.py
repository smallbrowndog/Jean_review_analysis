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

# Chrome 옵션 설정
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Chrome Driver 설정
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# 스크래핑할 URL
brand_url = "https://www.musinsa.com/brand/musinsastandard?categoryCode=003002&gf=A"


def crawl_brand():
    driver.get(brand_url)
    sleep(5)  # 페이지가 완전히 로드되도록 초기 대기 시간 설정

    brand_code = []  # 결과 저장 리스트

    # 상위 컨테이너 요소 찾기
    main_container_selector = "#commonLayoutContents > div.sc-zjwr47-0.vSiPV > div:nth-child(2) > div.sc-f39157-1.dqBVvr"
    main_container = driver.find_element(By.CSS_SELECTOR, main_container_selector)

    # 반복적으로 `data-index` 값이 있는 div들 탐색
    i = 0
    while True:
        try:
            item_selector = f"{main_container_selector} > div[data-index='{i}']"
            item_container = driver.find_element(By.CSS_SELECTOR, item_selector)

            # 제품명, 가격, 코드 추출
            pname_selector = "div.sc-ilxebA.hQIHhD > a"  # 제품명을 나타내는 CSS Selector
            price_selector = "div.sc-ilxebA.hQIHhD > div > span:nth-child(2)"  # 가격을 나타내는 CSS Selector
            code_selector = "a.gtm-select-item"  # ClothesCode의 CSS Selector

            Pname = item_container.find_element(By.CSS_SELECTOR, pname_selector).text
            Price = item_container.find_element(By.CSS_SELECTOR, price_selector).text
            ClothesCode = item_container.find_element(By.CSS_SELECTOR, code_selector).get_attribute("data-item-id")

            # 추출한 정보를 저장
            brand_code.append({
                "Pname": Pname,
                "Price": Price,
                "ClothesCode": ClothesCode
            })

            print(f"제품명: {Pname} | 가격: {Price} | 의류코드: {ClothesCode}")

            i += 1  # 다음 data-index로 이동

        except NoSuchElementException:
            print("모든 제품을 탐색했습니다.")
            break

    return brand_code


# 실행
crawl_brand()
