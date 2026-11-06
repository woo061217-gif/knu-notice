from datetime import datetime, timedelta
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import streamlit as st

# 웹페이지 기본 설정
st.set_page_config(
    page_title="강원대 통합 공지사항 스마트 검색", page_icon="⚡", layout="wide"
)

st.title("⚡ 강원대학교 통합 공지사항 스마트 검색")
st.write(
    "1년 치 공지 데이터를 깊이 있게 수집하여, 선택하신 기간 내의 공지를"
    " 정확하게 찾아드립니다."
)

# 📌 수집 대상 게시판 목록 (강원대학교 공식 최신 주소)
TARGET_URLS = [
    {"name": "일반공지", "url": "https://www.kangwon.ac.kr/ko/bbs/504/list.do"},
    {"name": "학사공지", "url": "https://www.kangwon.ac.kr/ko/bbs/720/list.do"},
    {"name": "장학공지", "url": "https://www.kangwon.ac.kr/ko/bbs/721/list.do"},
    {"name": "채용안내", "url": "https://www.kangwon.ac.kr/ko/bbs/716/list.do"},
]


# 🚀 1단계: 금일 기준 최대 1년 치까지 페이지를 돌며 수집하는 함수
@st.cache_data(ttl=600)
def fetch_knu_notices_one_year():
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  all_notices = []
  today = datetime.now().date()
  one_year_ago = today - timedelta(days=365)

  for board in TARGET_URLS:
    board_name = board["name"]
    base_url = board["url"]

    for page in range(1, 6):
      page_url = (
          f"{base_url}&pageIndex={page}"
          if "?" in base_url
          else f"{base_url}?pageIndex={page}"
      )

      try:
        response = requests.get(page_url, headers=headers, timeout=8)
        if response.status_code != 200:
          print(f"[{board_name}] {page_url} HTTP {response.status_code}")
          break

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select("div.table-inner table tbody tr, table tbody tr")
        if not rows:
          break

        old_data_found = False

        for row in rows:
          title_tag = row.select_one(
              "td.title a, td.link-ellipsis a, a.detail-button, td.subject a"
          )
          if not title_tag:
            continue

          title = title_tag.get_text(strip=True)
          if not title or len(title) < 2 or title.isdigit():
            continue

          href = title_tag.get("href", "")
          if not href or href == "#" or "javascript" in href:
            continue

          link = urljoin(page_url, href)

          date_tag = row.select_one(
              "td:nth-child(4), td.date, td:nth-child(5), td:nth-child(3)"
          )
          date_str = date_tag.get_text(strip=True) if date_tag else ""
          match = re.search(r"\d{4}[.-]\d{2}[.-]\d{2}", date_str)
          if not match:
            match = re.search(r"\d{4}[.-]\d{2}[.-]\d{2}", row.get_text())

          notice_date = None
          if match:
            clean_date = match.group(0).replace(".", "-")
            try:
              notice_date = datetime.strptime(clean_date, "%Y-%m-%d").date()
              date_str = clean_date
            except ValueError:
              pass

          if not notice_date:
            notice_date = today

          # 1년 전보다 과거 데이터면 탐색 중지
          if notice_date < one_year_ago:
            old_data_found = True
            continue

          if not any(n["link"] == link for n in all_notices):
            all_notices.append({
                "board": board_name,
                "title": title,
                "link": link,
                "date": date_str if date_str else str(today),
                "datetime": notice_date,
            })

        if old_data_found:
          break

      except Exception as e:
        print(f"[{board_name}] {page}페이지 수집 중 에러: {e}")
        continue

  all_notices.sort(key=lambda x: x["datetime"], reverse=True)
  return all_notices


# 🔍 2단계: 실시간 본문 지연 로딩 및 정밀 분석 함수
def fetch_notice_content_deep(link):
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }
  try:
    res = requests.get(link, headers=headers, timeout=4)
    if res.status_code == 200:
      soup = BeautifulSoup(res.text, "html.parser")
      content_selectors = [
          ".info-editor-area",
          ".card.detail",
          ".view-content",
          ".board-view-content",
          ".content",
          "div.view",
          ".b_view_content",
          ".board_view",
          ".view_text",
          "#contents",
          ".sub_content",
      ]
      for selector in content_selectors:
        content_box = soup.select_one(selector)
        if content_box:
          text = content_box.get_text(strip=True)
          if len(text) > 10:
            return text
      return soup.get_text(strip=True)
  except Exception as e:
    print(f"본문 로딩 실패 ({link}): {e}")
    return ""


# 🛠️ 사이드바: 검색 옵션 설정
st.sidebar.header("🔍 검색 옵션")
today = datetime.now().date()
one_year_ago = today - timedelta(days=365)  # 정확히 1년 전
default_4months_ago = today - timedelta(
    days=120
)  # 초반 기본 표시: 4개월(120일) 전

# 세션 상태 초기화 (최초 실행 시 4개월 전으로 설정)
if "applied_period" not in st.session_state:
  st.session_state.applied_period = default_4months_ago

# 1. 날짜 선택 위젯 (최소 1년 전 ~ 오늘 까지만 선택 가능하도록 엄격히 제한)
selected_date = st.sidebar.date_input(
    "표시 기간 시작일 선택",
    value=st.session_state.applied_period,
    min_value=one_year_ago,
    max_value=today,
    help="금일 기준 최대 1년 전까지만 선택할 수 있습니다.",
)

# 2. '기간 적용하기' 및 캐시 새로고침 버튼
col_apply, col_reload = st.sidebar.columns(2)
with col_apply:
  if st.button("기간 적용하기", use_container_width=True):
    st.session_state.applied_period = selected_date
    st.rerun()

with col_reload:
  if st.button("🔄 캐시 새로고침", use_container_width=True):
    st.cache_data.clear()
    st.rerun()


# 🔄 초기화 버튼 동작을 위한 세션 상태 관리
if "user_query" not in st.session_state:
  st.session_state.user_query = ""


def reset_query():
  st.session_state.user_query = ""
  st.session_state.applied_period = default_4months_ago


# 💬 메인 화면: 입력창과 초기화 버튼 나란히 배치
col_input, col_btn = st.columns([0.85, 0.15])

with col_input:
  user_query = st.text_input(
      "💬 어떤 공지사항을 찾고 싶으신가요?",
      key="user_query",
      placeholder=(
          "예: 장학금 신청 관련 공지 찾아줘, 수강신청 언제 해?, 과제 안내"
      ),
  )

with col_btn:
  st.write("")
  st.write("")
  if st.button("🗑️ 초기화", on_click=reset_query, use_container_width=True):
    st.rerun()

# ⚡ 대량 목록 로딩
with st.spinner("공지사항 데이터를 불러오는 중입니다..."):
  notice_list = fetch_knu_notices_one_year()

if notice_list:
  filtered_notices = []
  current_filter_date = st.session_state.applied_period

  for item in notice_list:
    if item["datetime"] >= current_filter_date:
      if user_query.strip():
        keywords = user_query.strip().split()

        # 1차: 제목 매칭
        match_in_title = any(kw.lower() in item["title"].lower() for kw in keywords)

        if match_in_title:
          filtered_notices.append(item)
        else:
          # 2차: 본문 심층 분석
          content = fetch_notice_content_deep(item["link"])
          match_in_content = any(kw.lower() in content.lower() for kw in keywords)
          if match_in_content:
            filtered_notices.append(item)
      else:
        filtered_notices.append(item)

  period_msg = f"📅 [{current_filter_date} ~ {today}] 기간 내 공지사항 |"

  # 결과 안내 출력
  if user_query.strip():
    st.success(
        f"{period_msg} '{user_query}' 분석 결과, 총"
        f" **{len(filtered_notices)}개**의 공지사항을 찾았습니다."
    )
  else:
    st.info(
        f"{period_msg} 총 **{len(filtered_notices)}개**의 공지사항이"
        " 있습니다. 위 메시지 창에 궁금한 내용을 입력해 보세요!"
    )

  st.divider()

  # 결과 리스트 렌더링
  for idx, item in enumerate(filtered_notices, 1):
    col1, col2, col3, col4 = st.columns([0.15, 0.15, 0.6, 0.1])
    with col1:
      st.text(item["date"])
    with col2:
      st.markdown(f"**[{item['board']}]**")
    with col3:
      st.markdown(f"**{idx}. [{item['title']}]({item['link']})**")
    with col4:
      st.markdown(f"[원문 보기]({item['link']})")
    st.divider()
else:
  st.error(
      "공지사항을 가져오지 못했습니다. 네트워크 연결 상태를 확인해 주세요."
  )
