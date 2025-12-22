from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

bible_dictionary = {
    "GEN": "창세기",
    "EXO": "출애굽기",
    "LEV": "레위기",
    "NUM": "민수기",
    "DEU": "신명기",
    "JOS": "여호수아",
    "JDG": "사사기",
    "RUT": "룻기",
    "1SA": "사무엘상",
    "2SA": "사무엘하",
    "1KI": "열왕기상",
    "2KI": "열왕기하",
    "1CH": "역대상",
    "2CH": "역대하",
    "EZR": "에스라",
    "NEH": "느헤미야",
    "EST": "에스더",
    "JOB": "욥기",
    "PSA": "시편",
    "PRO": "잠언",
    "ECC": "전도서",
    "SNG": "아가",
    "ISA": "이사야",
    "JER": "예레미야",
    "LAM": "예레미야애가",
    "EZK": "에스겔",
    "DAN": "다니엘",
    "HOS": "호세아",
    "JOL": "요엘",
    "AMO": "아모스",
    "OBA": "오바댜",
    "JON": "요나",
    "MIC": "미가",
    "NAM": "나훔",
    "HAB": "하박국",
    "ZEP": "스바냐",
    "HAG": "학개",
    "ZEC": "스가랴",
    "MAL": "말라기",
    "MAT": "마태복음",
    "MRK": "마가복음",
    "LUK": "누가복음",
    "JHN": "요한복음",
    "ACT": "사도행전",
    "ROM": "로마서",
    "1CO": "고린도전서",
    "2CO": "고린도후서",
    "GAL": "갈라디아서",
    "EPH": "에베소서",
    "PHP": "빌립보서",
    "COL": "골로새서",
    "1TH": "데살로니가전서",
    "2TH": "데살로니가후서",
    "1TI": "디모데전서",
    "2TI": "디모데후서",
    "TIT": "디도서",
    "PHM": "빌레몬서",
    "HEB": "히브리서",
    "JAS": "야고보서",
    "1PE": "베드로전서",
    "2PE": "베드로후서",
    "1JN": "요한일서",
    "2JN": "요한이서",
    "3JN": "요한삼서",
    "JUD": "유다서",
    "REV": "요한계시록"
}

def is_verse_num(element) :
	return "verse-span" in (element.get_attribute("class") or "") and element.find_elements(By.CSS_SELECTOR, ".v")

def is_footnote(object) :
	return len(object.find_elements(By.XPATH, "./*[contains(@class, 'ftext hidden')]")) > 0

# 절 본문 가져오기
def get_verce_texts(driver) :
	verses = driver.find_elements(By.CLASS_NAME, "verse-span")
	verse_nums = driver.find_elements(By.CSS_SELECTOR, ".verse-span:has(> .v)")
	return [i for i in verses if i not in verse_nums]

def get_titles(driver) :
	return driver.find_elements(By.CLASS_NAME, "ms")

def get_subtitles(driver) :
	return driver.find_elements(By.CLASS_NAME, "s")

def get_paragraphs(driver) :
	return driver.find_elements(By.CSS_SELECTOR, ".p, .m")

def get_quotes(driver) :
	return driver.find_elements(By.CLASS_NAME, "q1")

def get_footnotes(driver) :
	return driver.find_elements(By.CSS_SELECTOR, "[class*='ftext hidden']")

def setup_driver():
	"""Selenium WebDriver 설정"""
	chrome_options = Options()
	# chrome_options.add_argument("--headless")  # 브라우저 창 숨기기
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument("--disable-dev-shm-usage")
	chrome_options.add_argument("--disable-gpu")
	chrome_options.add_argument("--window-size=1920,1080")
	service = Service(ChromeDriverManager().install())
	driver = webdriver.Chrome(service=service, options=chrome_options)
	return driver

def main():
	#TODO 동적 크롤링 구현하기
	#TODO 인용(q1) 처리하기
	#TODO ms, s, mr, r
	#TODO 크롤링 map json으로 변환

	# p, m 단락
	# q1 인용
	# ms 대제목
	# s 소제목
	# mr 대제목의 레퍼런스절
	# r 소제목의 레퍼런스절

	# p, m, q1 > verse-span > v : 절
	# p, m, q1 > verse-span : 본문
	# p, m, q1 > ft 서.장.절 > ftext hidden : 각주


	testament = "GEN"
	chapter = 1
	url = f"https://www.bskorea.or.kr/KNT/index.php?chapter={testament}.{chapter}"
	
	driver = setup_driver()
	wait = WebDriverWait(driver, 10)
	
	try:
		# 최종 결과를 담을 리스트들 (순수 파이썬 데이터만 저장)
		all_verse_maps = []
		all_subtitle_maps = []
		all_paragraph_maps = []
		all_quote_maps = []
		all_footnote_maps = []

		for i in range(2):
			testament = "GEN"
			chapter = i + 1
			url = f"https://www.bskorea.or.kr/KNT/index.php?chapter={testament}.{chapter}"

			driver.get(url)
			print(f"페이지 로드 완료: {driver.title}")
			# 페이지 로드 대기
			wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
			time.sleep(0.5)

			# 이 장에서 사용할 WebElement 들만 가져오기
			ch_verse_texts = get_verce_texts(driver)
			ch_subtitles = get_subtitles(driver)
			ch_paragraphs = get_paragraphs(driver)
			ch_quotes = get_quotes(driver)
			ch_footnotes = get_footnotes(driver)

			# 절 본문 전처리
			ch_verse_maps = []
			temp_source = None
			temp_text = None
			for verse_text in ch_verse_texts:
				now_source = verse_text.get_attribute("data-verse-id")
				if temp_source == now_source:
					#만약 이 절이 인용구라면 앞에 띄어쓰기를 추가한다.
					if "q1" in verse_text.find_element(By.XPATH, "..").get_attribute("class").split():
							temp_text += '\n'
					temp_text += verse_text.get_attribute("innerHTML")
				else:
					ch_verse_maps.append({temp_source: temp_text})
					temp_source = now_source
					temp_text = verse_text.get_attribute("innerHTML")

			# 첫 번째 dummy(None) 제거 및 마지막 절 추가
			ch_verse_maps.pop(0)
			ch_verse_maps.append({temp_source: temp_text})

			# verse_maps는 서명.장.절을 키로 하고 그 절의 내용을 값으로 하는 딕셔너리의 리스트입니다.
			# [{'GEN.1.1': '처음에 하나님이 하늘과 땅을 창조하셨다.}, {'GEN.1.2': '땅은 거칠고 비어 있었다. 어둠이 깊은 물 위에 깔려... ...]
			all_verse_maps.extend(ch_verse_maps)

			# 소제목 전처리
			ch_subtitle_maps = []
			for subtitle in ch_subtitles:
				# 바로 뒤에 오는 형제 요소 중 클래스명이 'p'인 요소를 찾습니다.
				next_sibling = subtitle.find_element(By.XPATH, "following-sibling::*[contains(@class, 'p')][1]",)
				child = next_sibling.find_element(By.CLASS_NAME, "verse-span")

				source = child.get_attribute("data-verse-id")
				text = subtitle.get_attribute("innerHTML")
				ch_subtitle_maps.append({source: text})

			# subtitle_maps는 소제목을 저장하며, 자신 바로 뒤에 나오는 구절의 서명.장.절을 키로 하고 자신의 내용을 값으로 하는 딕셔너리의 리스트입니다.
			# [{'GEN.1.1': '하나님이 온 누리를 지으시다'}, ...]
			all_subtitle_maps.extend(ch_subtitle_maps)

			# 단락 전처리
			ch_paragraph_maps = []
			for idx, paragraph in enumerate(ch_paragraphs):
				child = paragraph.find_element(By.CLASS_NAME, "verse-span")

				source = child.get_attribute("data-verse-id")
				text = paragraph.get_attribute("class")
				ch_paragraph_maps.append({source: text})
			
			# paragraph_maps는 구절들의 집합인 단락을 저장하며, 단락 안에서 처음 나오는 구절의 서명.장.절을 키로 하고 단락의 종류를 값으로 하는 딕셔너리의 리스트입니다.
			# 단락의 종류는 p, m이 있습니다. p는 평범한 본문들의 집합입니다. m은 q1 이후 나타나는 단락으로, p와 차이점은 없어 보입니다.
			# [{'GEN.1.1': 'p'}, {'GEN.1.6': 'p'}, {'GEN.1.9': 'p'}, ...]
			all_paragraph_maps.extend(ch_paragraph_maps)

			# 인용 전처리

			# 각주 전처리
			ch_footnote_maps = []
			for footnote in ch_footnotes:
				verse_source = footnote.get_attribute("id").split(".", 1)[1]

				# 바로 위에 선행 형제가 없는 경우가 있어 NoSuchElement 문제가 발생할 수 있으므로
				# find_elements 를 사용해 방어적으로 처리한다.
				ups = footnote.find_elements(By.XPATH, "../preceding-sibling::*[1]")
				if not ups:
					# 선행 형제가 전혀 없다면 각주 앞에 글자가 없다고 보고 0으로 처리
					char_source = 0
				else:
					up = ups[0]

					#! q1(quote) 구문에 대한 코드 수정 필요(창2)
					# 각주 앞에 글자가 몇 개 있는지 검사하는 코드
					if is_verse_num(up):
						# 각주 앞 절 표시가 있다는 것은 글자가 없다는 뜻이므로 0
						char_source = 0
					else:
						more_up = up
						prev_str = more_up.get_attribute("innerHTML")
						while True:
							# 더 위의 객체를 찾는다 (없을 수도 있으므로 방어적으로)
							prev_siblings = more_up.find_elements(By.XPATH, "preceding-sibling::*[1]")
							if not prev_siblings: break
							more_up = prev_siblings[0]
							# 더 위의 객체가 절 표시라면 더 이상의 글자는 없으므로 종료
							if is_verse_num(more_up): break
							# 더 위의 객체가 각주라면 그 위에 또 글자가 있다는 뜻이므로 continue
							if is_footnote(more_up): continue
							# 위의 모든 상황에 해당하지 않는다면 같은 절의 또 다른 글자이므로 이를 prev_str에 추가
							prev_str = more_up.get_attribute("innerHTML") + prev_str
						char_source = len(prev_str)

				source = verse_source + "." + str(char_source)
				text = footnote.get_attribute("innerHTML")
				ch_footnote_maps.append({source: text})
			
			# footname_maps는 각주를 저장하며, 구절의 서명.장.절.{자신이 나오기 전 해당 절의 글자 수}를 키로 하고 자신의 내용을 값으로 하는 딕셔너리의 리스트입니다.
			# GEN.1.2.39 각주는 창세기 1장 2절의 39글자(띄어쓰기 포함) 이후 바로 각주가 나타난다는 뜻입니다.
			# [{'GEN.1.1.0': '또는 ‘태초에’'}, {'GEN.1.2.39': '또는 ‘하나님의 바람’'}, {'GEN.1.21.7': '또는 ‘바다짐승들’'}, ...]
			all_footnote_maps.extend(ch_footnote_maps)

		
		print(all_verse_maps)
		print(all_subtitle_maps)
		print(all_paragraph_maps)
		print(all_footnote_maps)

	except Exception as e:
		print(f"에러 발생: {e}")
	finally:
		driver.quit()

if __name__ == "__main__":
	main()

