import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

def setup_driver():
    """Chrome WebDriver 설정"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 헤드리스 모드
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-javascript")  # JavaScript 비활성화로 더 빠른 로딩
    
    try:
        # Windows 환경에서 더 안정적인 방법
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Chrome WebDriver 설정 실패: {e}")
        # 대안: requests와 BeautifulSoup 사용
        return None

def crawl_with_requests():
    """requests와 BeautifulSoup을 사용한 크롤링 (대안)"""
    try:
        # 1단계: 프로그램 목록 페이지 접속
        print("1단계: 프로그램 목록 페이지에 접속 중...")
        url = "https://www.cgntv.net/tv/31000/1/2/vlist.cgn"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # 2단계: HTML 파싱
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 3단계: onclick 속성이 movePlayerPage를 포함하는 첫 번째 요소 찾기
        print("2단계: programList에서 첫 번째 항목 검색 중...")
        onclick_elements = soup.find_all(attrs={"onclick": re.compile(r"movePlayerPage")})
        
        if not onclick_elements:
            print("프로그램 목록을 찾을 수 없습니다.")
            return None
        
        first_element = onclick_elements[0]
        onclick_value = first_element.get('onclick')
        print(f"첫 번째 프로그램 onclick: {onclick_value}")
        
        # 4단계: video ID 추출
        video_id = extract_video_id_from_onclick(onclick_value)
        if not video_id:
            print("video ID를 추출할 수 없습니다.")
            return None
        
        print(f"추출된 video ID: {video_id}")
        
        # 5단계: 플레이어 페이지로 이동
        print("4단계: 플레이어 페이지로 이동 중...")
        player_url = f"https://www.cgntv.net/player/home.cgn?vid={video_id}&pid=1"
        
        player_response = requests.get(player_url, headers=headers)
        player_response.raise_for_status()
        
        # 6단계: pTitle 요소 찾기
        print("5단계: pTitle 요소 검색 중...")
        player_soup = BeautifulSoup(player_response.content, 'html.parser')
        
        # HTML 내용을 파일로 저장 (디버깅용)
        with open("player_soup.txt", "w", encoding="utf-8") as f:
            f.write(str(player_soup))
        
        # pTitle 요소 찾기
        ptitle_element = player_soup.find(id="pTitle")
        ptitle_text = ""
        if ptitle_element:
            ptitle_text = ptitle_element.get_text(strip=True)
            print(f"pTitle 내용: {ptitle_text}")
        
        # 'contArea' id와 'cont' 클래스를 가진 요소를 찾기
        cont_area_element = player_soup.find(id="contArea")
        cont_content_element = None
        if cont_area_element:
            cont_content_element = cont_area_element.find(class_="cont")
            print("contArea.cont 요소:", cont_content_element)
        
        # JavaScript에서 VOD 객체 추출
        vod_data = extract_vod_data_from_html(player_response.text)
        
        # 컨텐츠 날짜/요일 정보 추출
        content_date = extract_content_date_from_html(player_response.text)
        
        # 결과 데이터 구성
        result = {
            "program_list_url": url,
            "first_program_onclick": onclick_value,
            "extracted_video_id": video_id,
            "player_url": player_url,
            "pTitle": ptitle_text,
            "contArea_content": str(cont_content_element) if cont_content_element else "",
            "vod_data": vod_data if vod_data else "",
            "content_date": content_date if content_date else {},
            "crawled_at": datetime.now().isoformat()
        }
        
        return result
            
    except Exception as e:
        print(f"requests 크롤링 중 오류 발생: {e}")
        return None

def extract_video_id_from_onclick(onclick_text):
    """onclick 속성에서 video ID 추출"""
    # onclick="movePlayerPage('332189' , '1' , '2025-07-18 00:00:00.0');" 형태에서 332189 추출
    pattern = r"movePlayerPage\('(\d+)'"
    match = re.search(pattern, onclick_text)
    if match:
        return match.group(1)
    return None

def extract_vod_data_from_html(html_content):
    """HTML에서 VOD 관련 JavaScript 객체 추출"""
    try:
        # MAQT 패턴의 URL들을 직접 찾기
        maqt_pattern = r'mod7\.cgntv\.net/_NewMP4/\d+/MAQT\d+\.h\d+x\d+\.mp4'
        maqt_matches = re.findall(maqt_pattern, html_content)
        
        if maqt_matches:
            print(f"MAQT 패턴 URL들 발견: {maqt_matches}")
            
            if len(maqt_matches) > 1:
                second_src = maqt_matches[1]  # 2번째 src (인덱스 1)
                print(f"2번째 MAQT 소스의 src: {second_src}")
                
                return f"//{second_src}"
        
        # jsonSrc 객체 내부의 주석 처리된 sources를 정확히 찾기
        json_src_pattern = r'var\s+jsonSrc\s*=\s*{([^}]+sources[^}]+)}'
        json_src_match = re.search(json_src_pattern, html_content, re.DOTALL)
        
        if json_src_match:
            print("jsonSrc 객체 발견")
            json_src_text = json_src_match.group(1)
            print(f"jsonSrc 내용: {json_src_text}")
            
            # jsonSrc 내부의 주석 처리된 sources 찾기
            commented_sources_pattern = r'/\*\s*([^*]+?)\*/'
            commented_matches = re.findall(commented_sources_pattern, json_src_text, re.DOTALL)
            
            for commented_text in commented_matches:
                print("jsonSrc 내부 주석 처리된 sources 발견")
                print(f"주석 내용: {commented_text}")
                
                # 주석 내부의 src 값들 추출
                src_pattern = r'src\s*:\s*["\']([^"\']+)["\']'
                src_matches = re.findall(src_pattern, commented_text)
                
                if len(src_matches) > 1:
                    second_src = src_matches[1]  # 2번째 src (인덱스 1)
                    print(f"주석에서 2번째 소스의 src: {second_src}")
                    
                    return second_src
        
        # 주석 처리된 sources 배열을 우선적으로 찾기 (더 정확한 패턴)
        commented_sources_pattern = r'/\*\s*([^*]+?)\*/'
        commented_matches = re.findall(commented_sources_pattern, html_content, re.DOTALL)
        
        for commented_text in commented_matches:
            print("주석 처리된 sources 발견")
            print(f"주석 내용: {commented_text}")
            
            # 주석 내부의 src 값들 추출
            src_pattern = r'src\s*:\s*["\']([^"\']+)["\']'
            src_matches = re.findall(src_pattern, commented_text)
            
            if len(src_matches) > 1:
                second_src = src_matches[1]  # 2번째 src (인덱스 1)
                print(f"주석에서 2번째 소스의 src: {second_src}")
                
                return second_src
        
        # loadVOD(obj) 함수 호출 부분 찾기
        load_vod_pattern = r'loadVOD\s*\(\s*({[^}]+})\s*\)'
        load_vod_match = re.search(load_vod_pattern, html_content, re.DOTALL)
        
        if load_vod_match:
            print("loadVOD 함수 호출 발견")
            # 더 정확한 객체 추출을 위해 다른 패턴 시도
            pass
        
        # sources 배열이 포함된 JavaScript 객체 찾기
        sources_pattern = r'sources\s*:\s*\[([^\]]+)\]'
        sources_match = re.search(sources_pattern, html_content, re.DOTALL)
        
        if sources_match:
            print("sources 배열 발견")
            sources_text = sources_match.group(1)
            print(f"sources 내용: {sources_text}")
            
            # src 값들 추출
            src_pattern = r'src\s*:\s*["\']([^"\']+)["\']'
            src_matches = re.findall(src_pattern, sources_text)
            
            if len(src_matches) > 1:
                second_src = src_matches[1]  # 2번째 src (인덱스 1)
                print(f"2번째 소스의 src: {second_src}")
                
                return second_src
        
        # 다른 패턴으로 시도: var obj = {...} 형태
        var_obj_pattern = r'var\s+\w+\s*=\s*({[^}]+sources[^}]+})'
        var_obj_match = re.search(var_obj_pattern, html_content, re.DOTALL)
        
        if var_obj_match:
            print("var obj 형태 발견")
            obj_text = var_obj_match.group(1)
            print(f"객체 내용: {obj_text}")
            
            # src 값 추출
            src_pattern = r'src\s*:\s*["\']([^"\']+)["\']'
            src_matches = re.findall(src_pattern, obj_text)
            
            if len(src_matches) > 1:
                second_src = src_matches[1]
                print(f"2번째 소스의 src: {second_src}")
                
                return second_src
        
        # JSON 형태로 직접 정의된 경우
        json_pattern = r'({[^}]*"sources"[^}]*})'
        json_matches = re.findall(json_pattern, html_content, re.DOTALL)
        
        for json_text in json_matches:
            try:
                # JSON 파싱 시도
                import json
                data = json.loads(json_text)
                if 'sources' in data and len(data['sources']) > 1:
                    second_src = data['sources'][1].get('src')
                    print(f"JSON에서 2번째 소스의 src: {second_src}")
                    
                    return second_src
            except:
                continue
        
        print("VOD 데이터를 찾을 수 없습니다.")
        return None
        
    except Exception as e:
        print(f"VOD 데이터 추출 중 오류: {e}")
        return None

def extract_content_date_from_html(html_content):
    """HTML에서 컨텐츠 날짜/요일 정보 추출"""
    try:
        # URL에서 날짜 정보 추출 (예: MAQT250718 -> 2025-07-18)
        date_pattern = r'MAQT(\d{2})(\d{2})(\d{2})'
        date_match = re.search(date_pattern, html_content)
        
        if date_match:
            year = "20" + date_match.group(1)  # 25 -> 2025
            month = date_match.group(2)        # 07
            day = date_match.group(3)          # 18
            
            from datetime import datetime
            date_obj = datetime(int(year), int(month), int(day))
            weekday = date_obj.strftime("%A")  # 요일 (영어)
            weekday_kr = {
                "Monday": "월요일",
                "Tuesday": "화요일", 
                "Wednesday": "수요일",
                "Thursday": "목요일",
                "Friday": "금요일",
                "Saturday": "토요일",
                "Sunday": "일요일"
            }
            
            return {
                "date": f"{year}-{month}-{day}",
                "weekday": weekday,
                "weekday_kr": weekday_kr.get(weekday, weekday)
            }
        
        return None
        
    except Exception as e:
        print(f"날짜 추출 중 오류: {e}")
        return None

def crawl_cgntv():
    """CGNTV 크롤링 메인 함수"""
    # 먼저 Selenium으로 시도
    driver = setup_driver()
    
    if driver:
        try:
            # 1단계: 프로그램 목록 페이지 접속
            print("1단계: 프로그램 목록 페이지에 접속 중...")
            url = "https://www.cgntv.net/tv/31000/1/2/vlist.cgn"
            driver.get(url)
            time.sleep(3)  # 페이지 로딩 대기
            
            # 2단계: programList에서 첫 번째 항목의 onclick 속성 찾기
            print("2단계: programList에서 첫 번째 항목 검색 중...")
            wait = WebDriverWait(driver, 10)
            
            # programList 요소들 찾기
            program_elements = driver.find_elements(By.CSS_SELECTOR, "[onclick*='movePlayerPage']")
            
            if not program_elements:
                print("프로그램 목록을 찾을 수 없습니다.")
                return None
            
            # 첫 번째 요소 선택
            first_program = program_elements[0]
            onclick_value = first_program.get_attribute("onclick")
            print(f"첫 번째 프로그램 onclick: {onclick_value}")
            
            # 3단계: video ID 추출
            video_id = extract_video_id_from_onclick(onclick_value)
            if not video_id:
                print("video ID를 추출할 수 없습니다.")
                return None
            
            print(f"추출된 video ID: {video_id}")
            
            # 4단계: 플레이어 페이지로 이동
            print("4단계: 플레이어 페이지로 이동 중...")
            player_url = f"https://www.cgntv.net/player/home.cgn?vid={video_id}&pid=1"
            driver.get(player_url)
            time.sleep(3)  # 페이지 로딩 대기
            
            # 5단계: pTitle 요소 찾기
            print("5단계: pTitle 요소 검색 중...")
            try:
                ptitle_element = wait.until(EC.presence_of_element_located((By.ID, "pTitle")))
                ptitle_text = ptitle_element.text
                print(f"pTitle 내용: {ptitle_text}")
                
                # 결과 데이터 구성
                result = {
                    "program_list_url": url,
                    "first_program_onclick": onclick_value,
                    "extracted_video_id": video_id,
                    "player_url": player_url,
                    "pTitle": ptitle_text,
                    "contArea_content": "", # 기본값 추가
                    "vod_data": "", # 기본값 추가
                    "content_date": {}, # 기본값 추가
                    "crawled_at": datetime.now().isoformat()
                }
                
                return result
                
            except Exception as e:
                print(f"pTitle 요소를 찾을 수 없습니다: {e}")
                return None
                
        except Exception as e:
            print(f"Selenium 크롤링 중 오류 발생: {e}")
            return None
            
        finally:
            driver.quit()
    else:
        # Selenium 실패 시 requests 사용
        print("Selenium 설정 실패, requests로 대체 시도...")
        return crawl_with_requests()

def save_result(result, filename=None):
    """결과를 JSON 파일로 저장"""
    if result:
        import os
        from datetime import datetime
        
        # data 폴더 생성
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # 파일명을 cgntv_crawl_result.json으로 고정
        filename = "cgntv_crawl_result.json"
        
        filepath = os.path.join(data_dir, filename)
        
        # 기존 파일이 있는지 확인
        existing_data = []
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
            except:
                existing_data = []
        
        # 새로운 데이터를 맨 앞에 추가
        existing_data.insert(0, result)
        
        # 최대 10개만 유지
        if len(existing_data) > 10:
            existing_data = existing_data[:10]
        
        # 파일에 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        print(f"결과가 {filepath}에 저장되었습니다. (총 {len(existing_data)}개 항목, 최대 10개 유지)")
    else:
        print("저장할 결과가 없습니다.")

if __name__ == "__main__":
    print("CGNTV 크롤러 시작...")
    result = crawl_cgntv()
    save_result(result)
    print("크롤링 완료!")
