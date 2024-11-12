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

def crawl_brand():
    # 입력받은 URL 열기
    driver.get(brand_url)
    # 페이지가 완전히 로드되도록 초기 대기 시간 설정
    sleep(5)

    brand_code = []  # 브랜드, 의류코드를 저장할 리스트
    scroll_position = 0  # 현재 스크롤 위치를 저장하는 변수

    # 스크롤을 내려 추가 로드
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(random.uniform(4, 15))

    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR,
                     "#commonLayoutContents > div.sc-zjwr47-0.vSiPV > div:nth-child(2) > div.sc-f39157-1.dqBVvr > div > div > div > div:nth-child(1) > div > div:nth-child(1) > div.sc-bZHSRq.hOJOdn > div > div.sc-ilxebA.hQIHhD"))
            )
        except TimeoutException:
            print("페이지가 시간 내에 로드되지 않았습니다.")
            break

        # 브랜드 이름, 의류 코드, 가격을 포함하는 요소들을 찾기
        brand_elements = driver.find_elements(By.CSS_SELECTOR,
                                               "#commonLayoutContents > div.sc-jv3z1e-0.eiMjNN > div.sc-hm89qk-0.iYyNpu > div.sc-hm89qk-4.bVhYTd > span.text-etc_22px_med.font-semibold.sc-hm89qk-5.kXAuqX.text-black.font-pretendard")
        Pname_containers = driver.find_elements(By.CSS_SELECTOR, "#commonLayoutContents > div.sc-zjwr47-0.vSiPV > div:nth-child(2) > div.sc-f39157-1.dqBVvr > div > div > div > div:nth-child(1) > div > div:nth-child(1) > div.sc-bZHSRq.hOJOdn > div > div.sc-ilxebA.hQIHhD > a")
        price_containers = driver.find_elements(By.CSS_SELECTOR, "#commonLayoutContents > div.sc-zjwr47-0.vSiPV > div:nth-child(2) > div.sc-f39157-1.dqBVvr > div > div > div > div:nth-child(1) > div > div:nth-child(1) > div.sc-bZHSRq.hOJOdn > div > div.sc-ilxebA.hQIHhD > div > span:nth-child(2)")
        info_containers = driver.find_elements(By.CSS_SELECTOR, "a.gtm-select-item")


        # # 각각의 요소에서 텍스트를 추출하여 출력
        # print("브랜드:", [element.text for element in brand_elements])
        # print("제품명:", [element.text for element in Pname_containers])
        # print("가격:", [element.text for element in price_containers])


        # 정보를 추출하여 리스트에 저장
        for i in range(len(Pname_containers)):
            try:
                # 브랜드 추출
                Brand = brand_elements[i].text if i < len(brand_elements) else "브랜드 정보 없음"

                # 제품명 추출
                Pname = Pname_containers[i].text

                # 가격 추출
                Price = price_containers[i].text if i < len(price_containers) else "가격 정보 없음"

                # 코드 추출
                ClothesCode = info_containers[i].get_attribute("data-item-id")

                # 데이터 리스트에 추가
                brand_code.append({
                    "Brand": Brand,
                    "Pname": Pname,
                    "Price": Price,
                    "Clothesode": ClothesCode
                })

                # 진행 상황 출력
                print(f"브랜드: {Brand} | 제품명: {Pname} | 가격: {Price} | 의류코드: {ClothesCode}")

            except NoSuchElementException:
                print("요소를 찾을 수 없습니다.")
                continue

        # 스크롤을 현재 위치에서 일정 픽셀만큼만 아래로 이동
        scroll_position += 300
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        sleep(random.uniform(2, 5))

        # 새로운 콘텐츠가 로드되었는지 확인
        new_height = driver.execute_script("return document.body.scrollHeight")
        if scroll_position >= new_height:
            print("더 이상 로드할 내용이 없습니다.")
            break

    return brand_code

# 실행
crawl_brand()
