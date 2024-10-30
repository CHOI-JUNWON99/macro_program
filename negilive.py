from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pickle



#-----------------------------------------------------------------

#driver = webdriver.Chrome('C:\\Users\\A\\Downloads\\chrome-win64\\chrome-win64\\chrome.exe')

chrome_options = Options()
chrome_options.binary_location = r"C:\Users\A\Downloads\chrome-win64\chrome-win64\chrome.exe"  # 크롬 브라우저 경로

# 새로 설치한 chromedriver.exe 경로 지정
chrome_service = Service(executable_path=r'C:\Users\A\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe')

# WebDriver에 Service와 Options 전달
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# 캐치테이블 로그인 페이지 열기
driver.get('https://app.catchtable.co.kr/ct/login')

# 로그인 및 핸드폰 인증을 수동으로 완료한 후, Enter를 눌러 쿠키를 저장
input("로그인이 완료되면 Enter 키를 눌러주세요...")

# 로그인 후 쿠키 저장
pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))

driver.quit()  # 드라이버 종료



#-----------------------------------------------------------------

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time
from datetime import datetime

chrome_options = Options()
chrome_options.binary_location = r"C:\Users\A\Downloads\chrome-win64\chrome-win64\chrome.exe"

chrome_service = Service(executable_path=r'C:\Users\A\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe')
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

driver.get('https://app.catchtable.co.kr/ct/shop/negilive')
cookies = pickle.load(open("cookies.pkl", "rb"))
for cookie in cookies:
    driver.add_cookie(cookie)

driver.refresh()

# 새로고침을 할 정확한 시간 설정
target_refresh_time = "17:22:50"
current_time = datetime.now().strftime("%H:%M:%S")
print(f"현재 시간: {current_time}, 새로고침 대기 중...")

while current_time != target_refresh_time:
    current_time = datetime.now().strftime("%H:%M:%S")
    time.sleep(0.1)

driver.refresh()
print("페이지 새로고침을 수행했습니다. 예약 버튼 대기 중...")

# 예약하기 버튼을 JavaScript로 직접 클릭
try:
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button.pgjaj01"))
    )
    reserve_button_js = """
    var button = document.querySelector('button.pgjaj01');
    if (button) {
        button.click();
        return true;
    } else {
        return false;
    }
    """
    result = driver.execute_script(reserve_button_js)
    
    if result:
        print("예약하기 버튼을 클릭했습니다.")
    else:
        raise Exception("예약하기 버튼을 찾지 못했습니다.")
        
except Exception as e:
    print(f"예약하기 버튼 클릭 실패: {e}")

# 예약 가능한 날짜 목록 설정
dates_to_check = ['토요일, 12월 7, 2024', '토요일, 12월 14, 2024', '토요일, 12월 21, 2024', '토요일, 12월 28, 2024']

def try_reserve_date_and_time(date_label, time_label):
    try:
        # 날짜 클릭 전 UI 로드를 위해 짧은 대기 추가
        time.sleep(0.1)
        driver.execute_script(f"document.querySelector(\"div[aria-label='{date_label}']\").click();")
        print(f"{date_label} 날짜를 클릭했습니다.")
        
        # 시간대 클릭 전 대기
        time.sleep(0.1)
        driver.execute_script(f"""
        Array.from(document.querySelectorAll('a span.time')).find(el => el.textContent === '{time_label}').click();
        """)
        print(f"{time_label} 시간을 클릭했습니다.")
        
        # 확인 버튼 클릭
        confirm_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-lg btn-red' and text()='확인']"))
        )
        confirm_button.click()
        print("확인 버튼을 클릭했습니다.")
        
        return True  # 성공 시 True 반환
    except Exception as e:
        print(f"예약 시도 실패: {e}")
        return False  # 실패 시 False 반환

# 무한 루프: 예약 성공할 때까지 계속 시도
current_person_count = 2
while True:
    print(f"{current_person_count}명으로 설정하여 예약 시도 중...")
    
    # 인원 수 선택 (첫 시도는 기본값 2명이므로 건너뜀)
    if current_person_count == 3:
        driver.execute_script("document.querySelector(\"input[name='count'][value='3']\").click();")
    else:
        driver.execute_script("document.querySelector(\"input[name='count'][value='2']\").click();")
    
    # 날짜 순회하여 예약 시도
    success = False
    for date_label in dates_to_check:
        print(f"{date_label} 예약 시도 중...")
        
        success = try_reserve_date_and_time(date_label, '오후 12:00')
        
        if success:
            print(f"{date_label} 예약에 성공했습니다!")
            break  # 예약 성공 시 루프 종료
        else:
            print(f"{date_label} 예약이 불가능합니다. 다음 날짜로 이동합니다.")

    # 성공하면 무한 루프 종료
    if success:
        break
    
    # 실패 시 인원 수 변경 (2명 ↔ 3명)
    current_person_count = 3 if current_person_count == 2 else 2

print("예약이 완료되었습니다.")

# 자동결제로 예약하기 버튼 클릭
try:
    auto_payment_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@class='_1ty9tmod _1ty9tmoe _1ltqxco1z' and text()='자동결제로 예약하기']"))
    )
    auto_payment_button.click()
    print("자동결제로 예약하기 버튼을 클릭했습니다.")
except Exception as e:
    print(f"자동결제로 예약하기 버튼 클릭 실패: {e}")
