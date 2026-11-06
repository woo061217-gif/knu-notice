from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import re
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
import requests
from sentence_transformers import SentenceTransformer, util
import streamlit as st

# 웹페이지 기본 설정
st.set_page_config(
    page_title="강원대학교 맞춤형 공지사항 검색",
    layout="wide",
)

# 세련되고 미니멀한 UI 디자인 스타일링 (CSS)
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', 'Inter', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', sans-serif;
    color: #0f172a;
    letter-spacing: -0.018em;
}

/* 캔버스 배경 (세련된 소프트 슬레이트 틴트) */
.stApp {
    background-color: #f8fafc;
}

/* 사이드바 스타일링 */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.02);
}

/* 전체 메인 패딩 및 컨테이너 너비 */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 5rem;
    max-width: 1140px;
}

/* 1. 상단 네비게이션 헤더 바 (Glassmorphism 디테일) */
.knu-navbar {
    background: rgba(255, 255, 255, 0.88);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 14px;
    padding: 13px 22px;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 15px -3px rgba(15, 23, 42, 0.04);
}
.navbar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}
.knu-emblem {
    background: linear-gradient(135deg, #003876 0%, #1e40af 100%);
    color: #ffffff;
    font-weight: 800;
    font-size: 0.84rem;
    padding: 4px 10px;
    border-radius: 6px;
    letter-spacing: 0.04em;
    box-shadow: 0 2px 6px rgba(30, 64, 175, 0.25);
}
.navbar-title {
    font-weight: 700;
    font-size: 1.08rem;
    color: #0f172a;
}
.navbar-subpill {
    background: #f1f5f9;
    color: #475569;
    font-size: 0.76rem;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 20px;
    border: 1px solid #e2e8f0;
}
.navbar-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.84rem;
    color: #334155;
    font-weight: 600;
}
.status-indicator {
    width: 8px;
    height: 8px;
    background-color: #059669;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 0 2.5px rgba(5, 150, 105, 0.2);
}

/* 2. 상단 메인 헤더 박스 */
.app-header-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 22px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.04);
    border-left: 4px solid #1e40af;
}

/* 3. 모던 공지사항 카드 (입체감 & Elevation & Hover) */
.modern-notice-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 14px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.03);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.modern-notice-card:hover {
    border-color: #93c5fd;
    box-shadow: 0 12px 24px -4px rgba(30, 64, 175, 0.10), 0 4px 8px -2px rgba(0, 0, 0, 0.03);
    transform: translateY(-3px);
}

/* 카드 상단 메타 바 */
.card-meta-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}
.card-meta-left {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

/* 공지 유형별 파스텔 뱃지 시스템 */
.badge {
    font-size: 0.78rem;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    letter-spacing: -0.01em;
}
.badge-dept {
    background-color: #eef2ff;
    color: #4338ca;
    border: 1px solid #c7d2fe;
}
.badge-academic {
    background-color: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
}
.badge-scholarship {
    background-color: #ecfdf5;
    color: #047857;
    border: 1px solid #a7f3d0;
}
.badge-career {
    background-color: #fffbeb;
    color: #b45309;
    border: 1px solid #fde68a;
}
.badge-event {
    background-color: #fff1f2;
    color: #be123c;
    border: 1px solid #fecdd3;
}
.badge-general {
    background-color: #f1f5f9;
    color: #475569;
    border: 1px solid #e2e8f0;
}

.date-chip {
    color: #64748b;
    font-size: 0.84rem;
    font-weight: 500;
}
.views-chip {
    background-color: #f8fafc;
    color: #475569;
    padding: 2px 8px;
    border-radius: 5px;
    font-size: 0.81rem;
    font-weight: 600;
    border: 1px solid #e2e8f0;
}

/* 원문 바로가기 버튼 (브랜드 포인트 컬러) */
.origin-btn {
    color: #1e40af !important;
    text-decoration: none !important;
    font-size: 0.83rem;
    font-weight: 600;
    padding: 4px 11px;
    border-radius: 6px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    transition: all 0.15s ease-in-out;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}
.origin-btn:hover {
    background: #1e40af;
    color: #ffffff !important;
    border-color: #1e40af;
    box-shadow: 0 3px 8px rgba(30, 64, 175, 0.25);
}

/* 공지 제목 */
.notice-card-title {
    font-size: 1.13rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.5;
    margin-bottom: 6px;
}
.notice-card-title a {
    color: #0f172a;
    text-decoration: none;
    transition: color 0.15s;
}
.notice-card-title a:hover {
    color: #1e40af;
}

/* 본문 핵심 요약 박스 */
.clean-summary-box {
    background-color: #f8fafc;
    border-left: 3.5px solid #2563eb;
    border-radius: 8px;
    padding: 12px 18px;
    margin-top: 12px;
    font-size: 0.92rem;
    line-height: 1.68;
    color: #334155;
    border-top: 1px solid #f1f5f9;
    border-right: 1px solid #f1f5f9;
    border-bottom: 1px solid #f1f5f9;
}
.clean-summary-header {
    font-weight: 700;
    color: #1d4ed8;
    margin-bottom: 6px;
    font-size: 0.86rem;
    letter-spacing: -0.01em;
}

/* 버튼 디자인 (브랜드 그라데이션) */
div.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.92rem;
    padding: 0.45rem 1rem;
    transition: all 0.15s ease-in-out;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}
div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
    border: none;
    color: #ffffff;
    box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
}
div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
}

/* 검색 인풋창 스타일 */
div[data-testid="stTextInput"] input {
    border-radius: 8px;
    font-size: 0.98rem;
    padding: 11px 16px;
    border: 1px solid #cbd5e1;
    background-color: #ffffff;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    transition: all 0.2s ease-in-out;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}
</style>
""", unsafe_allow_html=True)

# 🏷️ 공지 유형별 맞춤형 파스텔 뱃지 HTML 생성 함수
def get_board_badge_html(board_name, is_dept=False):
  if is_dept:
    return f'<span class="badge badge-dept">{board_name}</span>'
  if "학사" in board_name:
    return f'<span class="badge badge-academic">{board_name}</span>'
  elif "장학" in board_name:
    return f'<span class="badge badge-scholarship">{board_name}</span>'
  elif "채용" in board_name or "취업" in board_name:
    return f'<span class="badge badge-career">{board_name}</span>'
  elif "행사" in board_name:
    return f'<span class="badge badge-event">{board_name}</span>'
  else:
    return f'<span class="badge badge-general">{board_name}</span>'

# =============================================================================
# 🏛️ 강원대학교 캠퍼스 > 단과대학 > 학과 및 공지사항 URL 데이터베이스
# =============================================================================
CAMPUS_DATA = {
    "춘천캠퍼스": {
        "IT대학": {
            "컴퓨터공학과": (
                "https://cse.kangwon.ac.kr/cse/community/undergraduate-notice.do"
            ),
            "전자공학과": (
                "https://eice.kangwon.ac.kr/eice/community/notice001.do"
            ),
            "AI융합학과": "https://ai.kangwon.ac.kr/ai/community/notice.do",
            "전기전자공학과": (
                "https://ee.kangwon.ac.kr/ee/community/notice.do"
            ),
        },
        "문화예술·공과대학": {
            "기계공학전공": "https://me.kangwon.ac.kr/me/community/notice.do",
            "화학공학과": (
                "https://chemeng.kangwon.ac.kr/chemeng/community/notice.do"
            ),
            "신소재공학과": (
                "https://mse.kangwon.ac.kr/mse/community/notice.do"
            ),
            "건축학과": "https://arch.kangwon.ac.kr/arch/community/notice.do",
            "토목공학전공": "https://civil.kangwon.ac.kr/civil/community/notice.do",
            "에너지자원공학과": (
                "https://energy.kangwon.ac.kr/energy/community/notice.do"
            ),
        },
        "경영대학": {
            "경영학전공": "https://biz.kangwon.ac.kr/biz/community/notice.do",
            "경제학전공": "https://econ.kangwon.ac.kr/econ/community/notice.do",
            "관광경영학과": (
                "https://tourism.kangwon.ac.kr/tourism/community/notice.do"
            ),
            "회계학전공": "https://acc.kangwon.ac.kr/acc/community/notice.do",
        },
        "인문대학": {
            "국어국문학과": (
                "https://gukmun.kangwon.ac.kr/gukmun/community/notice.do"
            ),
            "영어영문학과": (
                "https://english.kangwon.ac.kr/english/community/notice.do"
            ),
            "사학과": (
                "https://history.kangwon.ac.kr/history/community/notice.do"
            ),
            "철학과": (
                "https://philosophy.kangwon.ac.kr/philosophy/community/notice.do"
            ),
            "독어독문학과": (
                "https://german.kangwon.ac.kr/german/community/notice.do"
            ),
            "불어불문학과": (
                "https://french.kangwon.ac.kr/french/community/notice.do"
            ),
        },
        "사회과학대학": {
            "행정학전공": "https://padm.kangwon.ac.kr/padm/community/notice.do",
            "미디어커뮤니케이션학과": (
                "https://masscom.kangwon.ac.kr/masscom/community/notice.do"
            ),
            "정치외교학과": (
                "https://politics.kangwon.ac.kr/politics/community/notice.do"
            ),
            "사회학과": (
                "https://sociology.kangwon.ac.kr/sociology/community/notice.do"
            ),
            "심리학과": (
                "https://psychology.kangwon.ac.kr/psychology/community/notice.do"
            ),
        },
        "자연과학대학": {
            "수학과": "https://math.kangwon.ac.kr/math/community/notice.do",
            "물리학과": (
                "https://physics.kangwon.ac.kr/physics/community/notice.do"
            ),
            "화학과": (
                "https://chemistry.kangwon.ac.kr/chemistry/community/notice.do"
            ),
            "생명과학과": "https://bio.kangwon.ac.kr/bio/community/notice.do",
            "지질지구물리학부": "https://geo.kangwon.ac.kr/geo/community/notice.do",
        },
        "간호대학": {
            "간호학과": (
                "https://nurse.kangwon.ac.kr/nurse/community/notice01.do"
            ),
        },
        "농업생명과학대학": {
            "식물자원응용공학과": (
                "https://plant.kangwon.ac.kr/plant/community/notice.do"
            ),
            "원예·농업자원경제학부": (
                "https://horti.kangwon.ac.kr/horti/community/notice.do"
            ),
            "바이오시스템공학과": (
                "https://bse.kangwon.ac.kr/bse/community/notice.do"
            ),
        },
        "사범대학": {
            "교육학과": "https://edu.kangwon.ac.kr/edu/community/notice.do",
            "국어교육과": (
                "https://koredu.kangwon.ac.kr/koredu/community/notice.do"
            ),
            "수학교육과": (
                "https://mathedu.kangwon.ac.kr/mathedu/community/notice.do"
            ),
            "영어교육과": (
                "https://engedu.kangwon.ac.kr/engedu/community/notice.do"
            ),
        },
    },
    "삼척·도계캠퍼스": {
        "공학대학(삼척)": {
            "첨단AI공학과": "https://cms.kangwon.ac.kr/EAIS/info.do",
            "기계시스템공학과": "https://cms.kangwon.ac.kr/mech/sub04_01.do",
            "전자정보통신공학과": (
                "https://cms.kangwon.ac.kr/elec/sub04_01.do"
            ),
            "소방방재학부": "https://cms.kangwon.ac.kr/fire/sub04_01.do",
            "건축공학전공": "https://cms.kangwon.ac.kr/arch-sc/sub04_01.do",
        },
        "인문사회·디자인대학(삼척)": {
            "행정학과(삼척)": "https://cms.kangwon.ac.kr/samad/sub04_01.do",
            "디자인학부": "https://cms.kangwon.ac.kr/design/sub04_01.do",
            "영어과": "https://cms.kangwon.ac.kr/english-sc/sub04_01.do",
            "일본어과": "https://cms.kangwon.ac.kr/japan-sc/sub04_01.do",
        },
        "보건과학대학(도계)": {
            "간호학과(도계)": "https://cms.kangwon.ac.kr/nurse-d/sub04_01.do",
            "물리치료학과": "https://cms.kangwon.ac.kr/pt/sub04_01.do",
            "방사선학과": "https://cms.kangwon.ac.kr/rad/sub04_01.do",
            "작업치료학과": "https://cms.kangwon.ac.kr/ot/sub04_01.do",
            "응급구조학과": "https://cms.kangwon.ac.kr/emt/sub04_01.do",
        },
        "보건복지대학(도계)": {
            "사회복지학과": "https://cms.kangwon.ac.kr/welfare/sub04_01.do",
            "유아교육과": "https://cms.kangwon.ac.kr/ece/sub04_01.do",
            "식품영양학과": "https://cms.kangwon.ac.kr/food/sub04_01.do",
        },
    },
}

# 🌐 전체 캠퍼스(춘천, 삼척·도계) 학과 매핑 데이터
ALL_CAMPUS_DEPTS = {}
for camp_k, col_dict in CAMPUS_DATA.items():
  for col_k, d_dict in col_dict.items():
    for d_k, d_url in d_dict.items():
      lbl = f"[{camp_k} | {col_k}] {d_k}"
      c_prefix = "춘천" if "춘천" in camp_k else "삼척·도계"
      ALL_CAMPUS_DEPTS[lbl] = {
          "campus": camp_k,
          "college": col_k,
          "dept": d_k,
          "url": d_url,
          "short_label": f"[{c_prefix}] {d_k}",
      }

# 📌 강원대학교 통합 공지사항 게시판 목록
KNU_INTEGRATED_BOARDS = [
    {"name": "일반공지", "url": "https://www.kangwon.ac.kr/ko/bbs/504/list.do"},
    {"name": "학사공지", "url": "https://www.kangwon.ac.kr/ko/bbs/720/list.do"},
    {"name": "장학공지", "url": "https://www.kangwon.ac.kr/ko/bbs/721/list.do"},
    {"name": "채용안내", "url": "https://www.kangwon.ac.kr/ko/bbs/716/list.do"},
    {"name": "행사안내", "url": "https://www.kangwon.ac.kr/ko/bbs/715/list.do"},
]

# 🚫 검색 주제어 왜곡 방지를 위한 메타 단어 (자료, 공지 등은 지시어/보조어이므로 핵심어에서 배제 또는 후순위 처리)
META_STOPWORDS = {
    "자료",
    "공지",
    "공지사항",
    "게시물",
    "게시글",
    "게시판",
    "글",
    "내용",
    "사항",
    "정보",
    "문서",
    "파일",
    "소식",
    "안내문",
    "안내사항",
    "알림",
    "관련",
    "안내",
    "문의",
}

# 🚫 추상적인 단어 및 상투어 블랙리스트 (문서 추천 기준으로 배제)
ABSTRACT_WORDS = {
    "관심",
    "사랑",
    "애정",
    "행복",
    "응원",
    "노력",
    "바람",
    "생각",
    "마음",
    "의미",
    "열정",
    "꿈",
    "희망",
    "참여",
    "부탁",
    "협조",
    "감사",
    "인사",
    "모습",
    "자세",
    "기대",
    "소중",
    "다양",
    "많은",
    "최선",
    "지속",
    "적극",
    "안녕",
    "반가",
    "이야기",
    "행사",
    "방법",
    "전달",
    "추진",
    "계획",
    "예정",
    "진행",
    "현황",
    "개요",
    "목적",
    "방침",
    "공유",
    "소통",
}

# 🚫 비명사 단어 목록 (동사, 형용사, 부사, 접속사 등 실질 명사가 아닌 단어 배제)
NON_NOUN_WORDS = {
    "하는", "하면", "하고", "해서", "하니", "하려", "하여", "해야", "해도",
    "되는", "되면", "되고", "돼서", "되니", "되려", "되어", "돼야", "돼도",
    "있는", "있으면", "있고", "있어", "있으니", "있으려",
    "없는", "없으면", "없고", "없어", "없으니",
    "받는", "받으면", "받고", "받아", "받으려",
    "내는", "내면", "내고", "내서", "내려",
    "보는", "보면", "보고", "봐서", "보려",
    "가는", "가면", "가고", "가서", "가려",
    "오는", "오면", "오고", "와서", "오려",
    "주는", "주면", "주고", "줘서", "주려",
    "아는", "알면", "알고", "알아",
    "모르는", "모르면", "모르고", "몰라",
    "싶은", "어떤", "이런", "저런", "그런",
    "어떻게", "언제", "어디", "누가", "무엇", "몇시", "얼마",
    "많은", "적은", "좋은", "나쁜", "빠른", "늦은",
}

# 📚 대학 학사/장학/취업/생활 실질 명사 특화 유사 단어 사전
SYNONYM_DICT = {
    "장학금": [
        "장학",
        "장학생",
        "국가장학",
        "근로장학",
        "성적장학",
        "지급",
        "장학재단",
        "소득분위",
        "한국장학재단",
    ],
    "장학": [
        "장학금",
        "장학생",
        "국가장학",
        "근로장학",
        "성적장학",
        "지급",
        "장학재단",
    ],
    "등록금": [
        "수업료",
        "고지서",
        "분할납부",
        "분납",
        "가상계좌",
        "수납",
        "등록",
        "납부",
        "은행",
    ],
    "수강신청": [
        "수강",
        "개설강좌",
        "시간표",
        "학점",
        "정정",
        "폐강",
        "신청",
        "수강바구니",
        "강의계획서",
    ],
    "수강": ["수강신청", "개설강좌", "시간표", "학점", "정정", "강의평가", "이수"],
    "휴학": [
        "복학",
        "휴·복학",
        "학적",
        "자퇴",
        "제적",
        "군휴학",
        "일반휴학",
        "질병휴학",
        "휴학원",
    ],
    "복학": ["휴학", "휴·복학", "학적", "수강신청", "등록금"],
    "성적": [
        "학점",
        "평점",
        "이의신청",
        "정정",
        "성적조회",
        "F학점",
        "평점평균",
        "열람",
    ],
    "기숙사": [
        "생활관",
        "난지원",
        "입사",
        "퇴사",
        "관비",
        "룸메이트",
        "합격자",
        "생활관비",
    ],
    "생활관": ["기숙사", "난지원", "입사", "퇴사", "관비", "식비"],
    "취업": [
        "채용",
        "인턴",
        "일자리",
        "공채",
        "이력서",
        "면접",
        "자격증",
        "직무",
        "서류",
        "기업",
    ],
    "채용": ["취업", "인턴", "일자리", "공채", "모집", "선발", "서류", "면접"],
    "교환학생": ["어학연수", "토익", "토플", "해외파견", "국제교류", "유학"],
    "졸업": [
        "학위수여",
        "졸업사정",
        "졸업유예",
        "학사학위",
        "학위",
        "논문",
        "졸업작품",
    ],
    "계절학기": ["계절수업", "하계", "동계"],
    "자격증": ["자격", "취득", "교육", "시험", "응시료", "역량", "과정"],
    "동아리": ["중앙동아리", "모집", "가입", "동아리연합회"],
    "봉사": ["사회봉사", "봉사활동", "봉사시간", "VMS", "1365"],
    "셔틀버스": ["통학버스", "버스", "노선", "운행", "시간표", "승차"],
    "과제": ["레포트", "보고서", "제출", "기한"],
    "졸업시험": ["졸시", "졸업논문", "통과기준", "합격"],
    "ai": [
        "인공지능",
        "머신러닝",
        "딥러닝",
        "생성형ai",
        "llm",
        "ai융합",
        "인공지능융합",
        "빅데이터",
        "챗gpt",
    ],
    "인공지능": [
        "ai",
        "머신러닝",
        "딥러닝",
        "생성형ai",
        "llm",
        "ai융합",
        "인공지능융합",
        "빅데이터",
        "챗gpt",
        "인공지능학부",
    ],
    "ai융합": ["ai", "인공지능", "인공지능융합", "머신러닝", "소프트웨어"],
    "sw": ["소프트웨어", "코딩", "프로그래밍", "sw중심대학", "개발자", "컴퓨터"],
    "소프트웨어": ["sw", "코딩", "프로그래밍", "sw중심대학", "개발", "컴퓨터공학"],
    "it": ["정보기술", "정보통신", "it대학", "컴퓨터", "소프트웨어"],
    "gpt": ["챗gpt", "생성형ai", "인공지능", "llm"],
    "챗gpt": ["gpt", "생성형ai", "인공지능", "ai"],
    "코딩": ["프로그래밍", "sw", "소프트웨어", "개발"],
    "빅데이터": ["데이터", "데이터사이언스", "인공지능", "ai"],
}

# 🔍 단어 경계(Word Boundary) 엄격 정규식 매칭 함수
def is_term_matched(term, text):
  """
  영문 약어(ai, sw, it, gpt 등) 검색 시 다른 영단어의 일부(email, chair, daily, detail 등)로
  포함된 가짜 일치를 원천 방지하고, 독립된 단어 또는 한글 접미사가 붙은 형태만 정확히 매칭
  """
  if not term or not text:
    return False
  term_lower = term.lower()
  text_lower = text.lower()

  # 영문자나 숫자로만 이루어진 단어 (예: 'ai', 'sw', 'it', 'gpt')
  if re.fullmatch(r"[a-z0-9]+", term_lower):
    # 앞뒤에 영문자가 없는 독립된 단어 형태 매칭 (예: ' AI ', '[AI]', 'AI융합', '생성형 AI' 등은 일치, 'email', 'chair'는 제외)
    pattern = rf"(?<![a-z]){re.escape(term_lower)}(?![a-z])"
    return bool(re.search(pattern, text_lower))
  else:
    # 한글 및 일반 어휘 (예: '인공지능', '등록금', '장학금')
    return term_lower in text_lower

# 🔤 한글 자모 분해 함수 (초성/중성/종성 분해로 오타 및 자모 유사도 정밀 비교)
def decompose_hangul(text):
  chosung = [
      'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ',
      'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ',
  ]
  jungsung = [
      'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ',
      'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ',
  ]
  jongsung = [
      '', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ',
      'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ',
      'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ',
  ]
  result = []
  for ch in text:
    code = ord(ch)
    if 0xAC00 <= code <= 0xD7A3:
      s_idx = code - 0xAC00
      cho = s_idx // (21 * 28)
      jung = (s_idx % (21 * 28)) // 28
      jong = s_idx % 28
      result.append(chosung[cho])
      result.append(jungsung[jung])
      if jong > 0:
        result.append(jongsung[jong])
    else:
      result.append(ch)
  return ''.join(result)


def hangul_similarity(w1, w2):
  d1 = decompose_hangul(w1)
  d2 = decompose_hangul(w2)
  return SequenceMatcher(None, d1, d2).ratio()


# 🏛️ 강원대 학사 대표 표준 어휘 사전 (오타 자동 교정 기준)
ACADEMIC_STANDARD_KEYWORDS = sorted(
    list(
        set(
            list(SYNONYM_DICT.keys())
            + [v for vals in SYNONYM_DICT.values() for v in vals]
            + [
                "등록금", "분할납부", "수업료", "환불", "고지서", "가상계좌",
                "장학금", "국가장학금", "근로장학", "성적우수", "소득분위",
                "수강신청", "예비수강", "수강정정", "수강취소", "계절학기", "계절수업",
                "성적조회", "성적이의", "성적평가", "학점포기", "학점인정",
                "졸업", "졸업요건", "졸업논문", "졸업사정", "학위수여", "졸업유예", "조기졸업",
                "휴학", "일반휴학", "군휴학", "질병휴학", "복학", "복학신청",
                "전과", "다전공", "복수전공", "부전공", "연계전공",
                "생활관", "기숙사", "입사", "퇴사", "룸메이트", "식권", "생활관비",
                "학사일정", "개강", "종강", "중간고사", "기말고사", "보강",
                "교환학생", "어학연수", "토익", "캡스톤", "현장실습", "인턴십",
                "취업", "채용", "이력서", "면접", "학생증", "모바일학생증", "증명서",
                "동아리", "봉사활동", "셔틀버스", "통학버스", "이루리", "스마트캠퍼스"
            ]
        )
    )
)


def find_fuzzy_academic_keyword(token, threshold=0.72):
  """사용자가 오타를 입력했을 때, 자모 유사도를 기반으로 올바른 학사 키워드로 자동 보정"""
  if len(token) < 2 or token in ACADEMIC_STANDARD_KEYWORDS:
    return None, 1.0

  best_match = None
  best_sim = 0.0

  for kw in ACADEMIC_STANDARD_KEYWORDS:
    sim = hangul_similarity(token, kw)
    if sim > best_sim:
      best_sim = sim
      best_match = kw

  if best_sim >= threshold and best_match:
    return best_match, best_sim
  return None, 0.0

# 🇰🇷 한국어 조사 목록 (긴 복합 조사부터 분리)
JOSA_PATTERNS = [
    # 3음절 이상 복합 조사
    "에서는",
    "에서도",
    "에게서는",
    "에게서",
    "한테서는",
    "한테서",
    "까지는",
    "부터는",
    "으로는",
    "으로써",
    "로부터",
    "이라도",
    "이라서",
    "이라고",
    "이라며",
    # 2음절 조사
    "에서",
    "에게",
    "한테",
    "으로",
    "로써",
    "로의",
    "에의",
    "와의",
    "과의",
    "보다",
    "처럼",
    "만큼",
    "까지",
    "부터",
    "마저",
    "조차",
    "마다",
    "이나",
    "라도",
    "에는",
    "에도",
    "로는",
    "로도",
    "과는",
    "와는",
    "하고",
    "이라",
    # 1음절 조사
    "은",
    "는",
    "이",
    "가",
    "을",
    "를",
    "의",
    "에",
    "로",
    "와",
    "과",
    "도",
    "만",
    "나",
    "요",
]

# 한국어 질문 빈출 용언/어미 패턴
VERB_ENDINGS = [
    "싶어요",
    "싶은데",
    "싶어",
    "싶다",
    "알려줘",
    "알려주세요",
    "알려줘요",
    "해주세요",
    "해줘",
    "알고싶어",
    "알고싶어요",
    "언제까지야",
    "언제야",
    "언제인지",
    "어디야",
    "어디서",
    "어떻게해",
    "어떻게",
    "있나요",
    "있어",
    "있을까",
    "있을까요",
    "되나요",
    "될까요",
    "되는지",
    "취소하면",
    "퇴사할때",
    "신청할때",
    "납부할때",
    "받으려면",
    "신청하려면",
    "궁금해요",
    "궁금해",
    "모르겠어",
]

STOPWORDS = {
    "은",
    "는",
    "이",
    "가",
    "을",
    "를",
    "에",
    "에서",
    "의",
    "로",
    "으로",
    "과",
    "와",
    "도",
    "만",
    "까지",
    "부터",
    "에게",
    "한테",
    "언제",
    "어디",
    "어떻게",
    "왜",
    "무엇",
    "알려줘",
    "알려주세요",
    "알고싶어",
    "있나요",
    "있어",
    "있을까",
    "찾아줘",
    "관련",
    "관련된",
    "대해",
    "대해서",
    "대한",
    "하는",
    "할",
    "해",
    "좀",
    "혹시",
    "및",
    "안내",
    "알림",
    "신청",
    "공지",
    "문의",
    "어떤",
    "방법",
    "궁금해",
    "알려",
    "주세요",
    "싶은데",
    "어떤게",
    "할때",
    "대해서",
    "알고",
    "싶어",
    "있나",
    "되나",
    "알려주세",
}


# 🔗 URL 정규화 함수 (중복 공지 방지 및 상세 본문 링크 보존)
def canonicalize_url(url):
  if not url:
    return ""
  parsed = urlparse(url)
  qs = parse_qs(parsed.query)

  # 강원대 포털: pstSn이 고유 글 번호
  if "pstSn" in qs:
    clean_query = f"pstSn={qs['pstSn'][0]}"
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{clean_query}"

  # 학과 게시판: mode=view 파라미터가 반드시 있어야 공지 본문 상세 화면으로 이동함!
  if "articleNo" in qs:
    clean_query = f"mode=view&articleNo={qs['articleNo'][0]}"
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{clean_query}"
  if "nttNo" in qs:
    clean_query = f"mode=view&nttNo={qs['nttNo'][0]}"
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{clean_query}"

  # 기타 페이징 쿼리 제거
  filtered_qs = {
      k: v
      for k, v in qs.items()
      if k
      not in [
          "pageIndex",
          "pageItm",
          "searchOrderSort",
          "searchGbn",
          "article.offset",
          "articleLimit",
          "searchCnd",
          "searchWrd",
      ]
  }
  new_query = urlencode(filtered_qs, doseq=True)
  return urlunparse((
      parsed.scheme,
      parsed.netloc,
      parsed.path,
      parsed.params,
      new_query,
      parsed.fragment,
  ))


# 🏷️ 제목 정규화 함수 (공백 및 특수문자 제거 후 비교)
def normalize_title(title):
  return re.sub(r"[\s\W_]+", "", title).lower()


# ✂️ 단어에서 조사 및 어미를 정밀 분리하는 함수
def strip_josa_and_ending(word):
  word = word.strip()
  for ve in VERB_ENDINGS:
    if word == ve:
      return ""
    if word.endswith(ve) and len(word) > len(ve):
      word = word[: -len(ve)]

  for _ in range(2):
    for josa in JOSA_PATTERNS:
      if word.endswith(josa) and len(word) > len(josa):
        stem = word[: -len(josa)]
        if len(stem) >= 2:
          word = stem
          break
  return word


# 🔍 1단계: 실질 명사만 추출 (추상어, 메타 보조어, 동사/형용사 등 비명사 배제 및 오타 유사도 자동 보정)
def extract_keywords_and_synonyms(query):
  clean = re.sub(r"[^\w\s]", " ", query)
  tokens = clean.split()

  core_keywords = []
  abstract_detected = []
  meta_detected = []
  typo_corrections = []

  for token in tokens:
    stem = strip_josa_and_ending(token)
    if not stem:
      continue

    # 1) 메타 단어 감지 ("자료", "공지", "공지사항", "게시물" 등 주제어 왜곡 방지를 위해 배제)
    if stem in META_STOPWORDS:
      if stem not in meta_detected:
        meta_detected.append(stem)
      continue

    # 2) 추상적인 단어 감지 및 배제 ("관심", "노력", "의미", "방법", "계획" 등)
    if stem in ABSTRACT_WORDS:
      if stem not in abstract_detected:
        abstract_detected.append(stem)
      continue

    # 3) 비명사(동사/형용사성 어간, 부사 등) 및 불용어, 1글자 단어 제외
    if stem in NON_NOUN_WORDS or stem in STOPWORDS or len(stem) < 2:
      continue

    # 4) 오타 자모 유사도 분석 (Fuzzy Keyword Matching)
    corrected_kw, sim = find_fuzzy_academic_keyword(stem)
    if corrected_kw and corrected_kw != stem:
      typo_corrections.append((stem, corrected_kw, int(sim * 100)))
      if corrected_kw not in core_keywords:
        core_keywords.append(corrected_kw)
    else:
      if stem not in core_keywords:
        core_keywords.append(stem)

  # 유사 단어 / 연관어 확장 (실질 명사 특화 및 대소문자 무시 매칭)
  expanded_synonyms = set()
  for kw in core_keywords:
    kw_lower = kw.lower()
    for dict_key, syns in SYNONYM_DICT.items():
      dict_key_lower = dict_key.lower()
      is_match = False
      if len(kw_lower) <= 3 and re.fullmatch(r"[a-z0-9]+", kw_lower):
        is_match = (kw_lower == dict_key_lower)
      else:
        is_match = (
            kw_lower == dict_key_lower
            or kw_lower in dict_key_lower
            or dict_key_lower in kw_lower
        )

      if is_match:
        for s in syns:
          if (
              s not in ABSTRACT_WORDS
              and s not in META_STOPWORDS
              and s not in NON_NOUN_WORDS
          ):
            expanded_synonyms.update([s])

  synonyms = [s for s in expanded_synonyms if s not in core_keywords]
  return core_keywords, synonyms, abstract_detected, meta_detected, typo_corrections


# 🧠 AI 임베딩 모델 로드
@st.cache_resource
def load_embedding_model():
  return SentenceTransformer(
      "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  )


# 👁️ 공지사항 조회수 추출 헬퍼 함수
def extract_views(row):
  text = row.get_text()
  # 1. 텍스트 내 "조회 1,234" 또는 "조회수 1,234" 패턴 검사
  m = re.search(r"조회(?:수)?\s*[:\s]?\s*([\d,]+)", text)
  if m:
    try:
      return int(m.group(1).replace(",", ""))
    except Exception:
      pass

  # 2. 클래스명 기반 td 탐색 (.hit, .views, .count, .view, .hits 등)
  hit_td = row.select_one("td.hit, td.views, td.count, td.view, td.hits")
  if hit_td:
    v_txt = re.sub(r"[^\d]", "", hit_td.get_text(strip=True))
    if v_txt:
      try:
        return int(v_txt)
      except Exception:
        pass

  # 3. 각 td 중 숫자만 있고 날짜가 아닌 열 (주로 뒤쪽 열들)
  tds = row.select("td")
  if len(tds) >= 4:
    for td in reversed(tds[2:]):
      txt = td.get_text(strip=True)
      if re.search(r"\d{2,4}[.-]\d{1,2}[.-]\d{1,2}", txt):
        continue
      cleaned = txt.replace(",", "").strip()
      if cleaned.isdigit() and len(cleaned) <= 7:
        try:
          return int(cleaned)
        except Exception:
          pass
  return 0


# 🚀 강원대 포털 통합 공지사항 수집 (중복 완벽 방지 & 조회수 추출)
@st.cache_data(ttl=600)
def fetch_knu_integrated_notices():
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }
  all_notices = []
  seen_canonical_urls = set()
  seen_norm_titles = set()
  today = datetime.now().date()
  four_years_ago = today - timedelta(days=365 * 4)

  for board in KNU_INTEGRATED_BOARDS:
    board_name = board["name"]
    base_url = board["url"]

    for page in range(1, 8):
      page_url = (
          f"{base_url}&pageIndex={page}"
          if "?" in base_url
          else f"{base_url}?pageIndex={page}"
      )
      try:
        res = requests.get(page_url, headers=headers, timeout=6)
        if res.status_code != 200:
          break
        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select("div.table-inner table tbody tr, table tbody tr")
        if not rows:
          break

        has_older_than_4y = False
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

          full_link = urljoin(page_url, href)
          canon_link = canonicalize_url(full_link)
          norm_title = normalize_title(title)

          # URL 및 제목 기준 중복 차단
          if (
              canon_link in seen_canonical_urls
              or norm_title in seen_norm_titles
          ):
            continue

          date_tag = row.select_one(
              "td:nth-child(4), td.date, td:nth-child(5), td:nth-child(3)"
          )
          date_str = date_tag.get_text(strip=True) if date_tag else ""
          match = re.search(r"(\d{4})[.-](\d{1,2})[.-](\d{1,2})", date_str)
          if not match:
            match = re.search(
                r"(\d{4})[.-](\d{1,2})[.-](\d{1,2})", row.get_text()
            )

          notice_date = today
          clean_date = str(today)
          if match:
            y, m, d = match.groups()
            clean_date = f"{y}-{int(m):02d}-{int(d):02d}"
            try:
              notice_date = datetime.strptime(clean_date, "%Y-%m-%d").date()
            except:
              pass

          if notice_date < four_years_ago:
            has_older_than_4y = True
            continue

          views = extract_views(row)

          seen_canonical_urls.add(canon_link)
          seen_norm_titles.add(norm_title)

          all_notices.append({
              "board": board_name,
              "is_dept": False,
              "title": title,
              "link": canon_link,
              "date": clean_date,
              "datetime": notice_date,
              "views": views,
          })

        if has_older_than_4y:
          break
      except Exception:
        continue
  return all_notices


# 📖 선택된 학과 공지사항 수집 (중복 완벽 방지 & 조회수 추출, 최대 4년 전까지)
@st.cache_data(ttl=600)
def fetch_department_notices(dept_name, dept_url):
  if not dept_url or not dept_url.startswith("http"):
    return []

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }
  notices = []
  seen_canonical_urls = set()
  seen_norm_titles = set()
  today = datetime.now().date()
  four_years_ago = today - timedelta(days=365 * 4)

  try:
    res = requests.get(dept_url, headers=headers, timeout=6)
    if res.status_code == 200:
      soup = BeautifulSoup(res.text, "html.parser")
      rows = soup.select(
          "table tbody tr, .tbl_board tbody tr, ul.board-list li, .bbs__list"
          " tbody tr"
      )
      for row in rows:
        title_tag = row.select_one("td.title a, td.subject a, td a, a")
        if not title_tag:
          continue
        title = title_tag.get_text(strip=True)
        if not title or len(title) < 2 or title.isdigit():
          continue
        href = title_tag.get("href", "")
        if not href or href == "#" or "javascript" in href:
          continue

        full_link = urljoin(dept_url, href)
        canon_link = canonicalize_url(full_link)
        norm_title = normalize_title(title)

        if (
            canon_link in seen_canonical_urls
            or norm_title in seen_norm_titles
        ):
          continue

        date_tag = row.select_one(
            "td:nth-child(4), td:nth-child(5), .date, td.date"
        )
        date_str = date_tag.get_text(strip=True) if date_tag else ""
        match = re.search(r"(\d{2,4})[.-](\d{1,2})[.-](\d{1,2})", date_str)
        if not match:
          match = re.search(
              r"(\d{2,4})[.-](\d{1,2})[.-](\d{1,2})", row.get_text()
          )

        notice_date = today
        clean_date = str(today)
        if match:
          y, m, d = match.groups()
          if len(y) == 2:
            y = "20" + y
          clean_date = f"{y}-{int(m):02d}-{int(d):02d}"
          try:
            notice_date = datetime.strptime(clean_date, "%Y-%m-%d").date()
          except:
            pass

        if notice_date < four_years_ago:
          continue

        views = extract_views(row)

        seen_canonical_urls.add(canon_link)
        seen_norm_titles.add(norm_title)

        notices.append({
            "board": dept_name,
            "is_dept": True,
            "title": title,
            "link": canon_link,
            "date": clean_date,
            "datetime": notice_date,
            "views": views,
        })
  except Exception as e:
    print(f"학과 공지 수집 실패 ({dept_name}): {e}")

  return notices


# 🧹 본문 상투적 인사말/경로/메타정보 정제 함수 (Denoising)
def clean_body_text(text):
  if not text:
    return ""
  patterns = [
      r"홈\s*>\s*[^>\n]+>[^>\n]+",  # 홈 > 대학생활 > 학과공지 등 네비게이션 경로
      r"위치\s*:\s*홈\s*>.*",
      r"홈으로\s*돌아가기.*?(?=\s|$)",
      r"목록으로\s*돌아가기.*?(?=\s|$)",
      r"arrow_\w+",
      r"^내용\s+",
      r"(작성자|등록자)\s*[:\s]?[^\s]+\s*(작성일|등록일)\s*[:\s]?[\d.-]+(\s*(조회수)?\s*[:\s]?[\d,]+)?",
      r"(학생 여러분의?|학우 여러분의?|여러분의?|교직원 여러분의?)?\s*(많은)?\s*(관심과?\s*(사랑|참여|성원)?|사랑과?\s*관심?)\s*(부탁드립니다|바랍니다|부탁드려요)[.!]?",
      r"많은\s*(관심|참여|성원)\s*(부탁드립니다|바랍니다)[.!]?",
      r"감사합니다[.!]?",
      r"기타\s*문의사항은.*",
      r"문의(처)?\s*:\s*[0-9\-\s]+",
  ]
  for p in patterns:
    text = re.sub(p, " ", text, flags=re.IGNORECASE)
  text = re.sub(r"\s+", " ", text).strip()
  return text


# 📖 개별 공지 본문 크롤링 및 캐싱 (순수 본문 컨테이너 우선 탐색)
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_notice_content(link):
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }
  try:
    res = requests.get(link, headers=headers, timeout=5)
    if res.status_code == 200:
      soup = BeautifulSoup(res.text, "html.parser")

      # 1. 네비게이션 경로(breadcrumb, location), 메타정보, 버튼, 이전글/다음글 태그 제거
      for noise in soup.select(
          "script, style, button, .location, .breadcrumb, .navi, .snav,"
          " .sub-nav, .view-info, .writer-info, .bbs_prev_next, .page-move,"
          " .prev-next, .board-bottom, .file-list, .attach-list"
      ):
        noise.decompose()

      # 2. 순수 본문 영역 우선 선택 (.b-content-box, .fr-view: 학과 CMS 순수 본문 컨테이너)
      content_area = soup.select_one(
          ".b-content-box, .fr-view, .editor-wrap, .info-editor-area,"
          " .view-con, .view-content, .bbs_view, .board-view, #contents,"
          " .content"
      )
      if content_area:
        raw_text = content_area.get_text(separator=" ", strip=True)
        # 상투적인 인사말 및 경로 텍스트 정제
        clean_text = clean_body_text(raw_text)
        return clean_text[:3000]
  except Exception as e:
    print(f"본문 크롤링 실패 ({link}): {e}")
  return ""


def chunk_text(text, chunk_size=250, overlap=50, max_chunks=8):
  if not text or len(text) < 30:
    return []
  chunks = []
  start = 0
  step = max(1, chunk_size - overlap)
  while start < len(text) and len(chunks) < max_chunks:
    end = min(start + chunk_size, len(text))
    chunk = text[start:end].strip()
    if len(chunk) >= 30:
      chunks.append(chunk)
    start += step
  return chunks


# 📑 본문 핵심 내용 자동 요약 헬퍼 함수 (경로성 텍스트 완전 배제)
def generate_notice_summary(content, matched_terms=None, title=""):
  if not content or len(content.strip()) < 20:
    return "본문 상세 내용은 원문 링크를 통해 확인해 주세요."

  cleaned = re.sub(r"[\r\n\t]+", " ", content)
  raw_sentences = [
      s.strip()
      for s in re.split(r"(?<=[.!?])\s+", cleaned)
      if len(s.strip()) >= 15
  ]

  # 경로, 메뉴, 이전글/다음글 등 노이즈 문장 엄격 배제
  filtered_sentences = []
  noise_words = [
      "홈 >",
      "위치 :",
      "이전글",
      "다음글",
      "첨부파일",
      "조회수",
      "작성자",
      "다운로드",
      "KNU광장",
      "홈으로 돌아가기",
      "목록으로 돌아가기",
      "대학생활만족도",
  ]
  for s in raw_sentences:
    if any(nw in s for nw in noise_words):
      continue
    filtered_sentences.append(s)

  sentences = filtered_sentences if filtered_sentences else raw_sentences
  if not sentences:
    return content[:180] + "..."

  key_patterns = [
      r"기간",
      r"일시",
      r"대상",
      r"신청",
      r"접수",
      r"방법",
      r"선발",
      r"지급",
      r"금액",
      r"안내",
      r"제출",
      r"마감",
      r"문의",
      r"일정",
  ]
  scored_sentences = []
  matched = [t.lower() for t in matched_terms] if matched_terms else []

  for idx, s in enumerate(sentences):
    s_lower = s.lower()
    score = 0
    # 질문 핵심 단어 포함 시 가중치
    for term in matched:
      if term in s_lower:
        score += 4
    # 공지 핵심 용어(기간, 대상, 신청, 선발 등) 포함 시 가중치
    for pat in key_patterns:
      if re.search(pat, s):
        score += 1.5
    # 도입부 가중치
    if idx < 3:
      score += 0.5
    scored_sentences.append((score, idx, s))

  scored_sentences.sort(key=lambda x: x[0], reverse=True)
  top_sentences = scored_sentences[:2]
  if top_sentences[0][0] == 0:
    top_sentences = [(0, i, s) for i, s in enumerate(sentences[:2])]

  top_sentences.sort(key=lambda x: x[1])  # 원래 본문 순서 유지
  summary_text = " ".join([s[2] for s in top_sentences])

  if len(summary_text) > 230:
    summary_text = summary_text[:227] + "..."

  return summary_text


# =============================================================================
# 🎛️ 세션 상태 초기화
# =============================================================================
if "user_role" not in st.session_state:
  st.session_state.user_role = "student"

if "onboarded" not in st.session_state:
  st.session_state.onboarded = False

if "selected_campus" not in st.session_state:
  st.session_state.selected_campus = "춘천캠퍼스"

if "selected_college" not in st.session_state:
  st.session_state.selected_college = "IT대학"

if "selected_dept" not in st.session_state:
  st.session_state.selected_dept = "컴퓨터공학과"

if "selected_dept_url" not in st.session_state:
  st.session_state.selected_dept_url = CAMPUS_DATA["춘천캠퍼스"]["IT대학"][
      "컴퓨터공학과"
  ]

if "selected_depts" not in st.session_state:
  st.session_state.selected_depts = ["컴퓨터공학과"]

if "selected_dept_urls" not in st.session_state:
  st.session_state.selected_dept_urls = {
      "컴퓨터공학과": CAMPUS_DATA["춘천캠퍼스"]["IT대학"]["컴퓨터공학과"]
  }

if "selected_dept_labels" not in st.session_state:
  st.session_state.selected_dept_labels = {
      "컴퓨터공학과": "[춘천] 컴퓨터공학과"
  }

if "prof_added_depts" not in st.session_state:
  st.session_state.prof_added_depts = {}

today = datetime.now().date()
default_2months_ago = today - timedelta(days=60)

if "applied_period" not in st.session_state:
  st.session_state.applied_period = default_2months_ago

if "user_query" not in st.session_state:
  st.session_state.user_query = ""


# =============================================================================
# [첫 번째 화면] 캠퍼스 / 단과대학 / 학과 소속 선택 화면 (학생용 vs 교수용)
# =============================================================================
if not st.session_state.onboarded:
  st.markdown(
      """<div style="text-align: center; padding: 25px 0 25px 0;">
      <div style="display: inline-flex; align-items: center; gap: 8px; margin-bottom: 12px;">
          <span class="knu-emblem">KNU</span>
          <span class="navbar-subpill">Smart Notice Portal</span>
      </div>
      <h1 style="font-size: 2.15em; font-weight: 800; color: #0f172a; margin-bottom: 8px; letter-spacing: -0.02em;">
          강원대학교 공지사항 스마트 검색
      </h1>
      <p style="font-size: 1.05em; color: #64748b; max-width: 650px; margin: 0 auto;">
          소속 학과를 선택하시면 학과 홈페이지 공지사항과 강원대학교 포털 통합 공지사항을 한곳에 모아 정확하게 검색해 드립니다.
      </p>
  </div>""",
      unsafe_allow_html=True,
  )

  col_box_l, col_box_m, col_box_r = st.columns([0.10, 0.80, 0.10])
  with col_box_m:
    st.markdown(
        """<div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 30px 36px; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.04);">
        <h3 style="margin-top: 0; color: #0f172a; font-weight: 700; font-size: 1.25rem;">사용자 구분 및 소속 학과 선택</h3>
    """,
        unsafe_allow_html=True,
    )

    role_choice = st.radio(
        "사용자 구분을 선택하세요",
        [
            "학생용 (소속 학과 1개 선택)",
            "교수용 (캠퍼스 무관 여러 학과 복수 선택 및 동시 조회)",
        ],
        index=0 if st.session_state.user_role == "student" else 1,
        horizontal=True,
    )
    is_professor = "교수용" in role_choice

    st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)

    if not is_professor:
      # =======================================================================
      # [학생용] 단일 학과 선택 모드
      # =======================================================================
      campus_list = list(CAMPUS_DATA.keys())
      campus_idx = (
          campus_list.index(st.session_state.selected_campus)
          if st.session_state.selected_campus in campus_list
          else 0
      )
      selected_campus = st.selectbox(
          "캠퍼스 선택", campus_list, index=campus_idx
      )
      college_dict = CAMPUS_DATA[selected_campus]

      college_list = list(college_dict.keys())
      college_idx = (
          college_list.index(st.session_state.selected_college)
          if st.session_state.selected_college in college_list
          else 0
      )
      selected_college = st.selectbox(
          "단과대학 선택", college_list, index=college_idx
      )

      dept_dict = college_dict[selected_college]
      dept_list = list(dept_dict.keys()) + ["직접 학과명 및 공지 URL 입력"]
      dept_idx = (
          dept_list.index(st.session_state.selected_dept)
          if st.session_state.selected_dept in dept_list
          else 0
      )
      selected_dept = st.selectbox(
          "학과 / 전공 선택", dept_list, index=dept_idx
      )

      if selected_dept == "직접 학과명 및 공지 URL 입력":
        custom_dept_name = st.text_input(
            "학과 이름을 입력하세요", placeholder="예: 생물공학전공"
        )
        custom_url = st.text_input(
            "해당 학과의 공지사항 게시판 URL을 입력하세요",
            placeholder="https://...kangwon.ac.kr/.../notice.do",
        )
        final_dept_name = (
            custom_dept_name.strip() if custom_dept_name.strip() else "기타학과"
        )
        final_dept_url = custom_url.strip()
      else:
        final_dept_name = selected_dept
        final_dept_url = dept_dict.get(selected_dept, "")

      st.markdown("</div>", unsafe_allow_html=True)

      col_btn_l, col_btn_r = st.columns([0.3, 0.7])
      with col_btn_r:
        if st.button(
            "공지사항 조회 시작하기",
            type="primary",
            use_container_width=True,
        ):
          st.session_state.user_role = "student"
          st.session_state.selected_campus = selected_campus
          st.session_state.selected_college = selected_college
          st.session_state.selected_dept = final_dept_name
          st.session_state.selected_dept_url = final_dept_url
          st.session_state.selected_depts = [final_dept_name]
          st.session_state.selected_dept_urls = {
              final_dept_name: final_dept_url
          }
          st.session_state.selected_dept_labels = {
              final_dept_name: f"[{'춘천' if '춘천' in selected_campus else '삼척'}] {final_dept_name}"
          }
          st.session_state.onboarded = True
          st.rerun()

    else:
      # =======================================================================
      # [교수용] 복수 학과 선택 모드
      # =======================================================================
      camp_list_prof = list(CAMPUS_DATA.keys())
      sel_camp_prof = st.selectbox(
          "캠퍼스 선택", camp_list_prof, key="prof_camp"
      )

      col_dict_prof = CAMPUS_DATA[sel_camp_prof]
      col_list_prof = list(col_dict_prof.keys())
      sel_col_prof = st.selectbox(
          "단과대학 선택", col_list_prof, key="prof_col"
      )

      dept_dict_prof = col_dict_prof[sel_col_prof]
      dept_list_prof = list(dept_dict_prof.keys())
      sel_dept_prof = st.selectbox(
          "학과 / 전공 선택", dept_list_prof, key="prof_dept"
      )

      col_add1, col_add2 = st.columns([0.55, 0.45])
      with col_add1:
        if st.button("선택 학과 추가", use_container_width=True, type="secondary"):
          st.session_state.prof_added_depts[sel_dept_prof] = {
              "campus": sel_camp_prof,
              "college": sel_col_prof,
              "url": dept_dict_prof[sel_dept_prof],
          }
          st.rerun()

      with col_add2:
        if st.button(f"{sel_col_prof} 전체 학과 추가", use_container_width=True):
          for d_name, d_url in dept_dict_prof.items():
            st.session_state.prof_added_depts[d_name] = {
                "campus": sel_camp_prof,
                "college": sel_col_prof,
                "url": d_url,
            }
          st.rerun()

      # 추가된 학과 목록 표시
      st.markdown("<hr style='margin: 16px 0 12px 0; border: none; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)
      st.markdown(
          f"##### 추가된 학과 목록 ({len(st.session_state.prof_added_depts)}개)"
      )

      if st.session_state.prof_added_depts:
        st.markdown(
            """<div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px;">""",
            unsafe_allow_html=True,
        )
        for d_name, d_info in list(st.session_state.prof_added_depts.items()):
          col_item_l, col_item_m, col_item_r = st.columns([0.65, 0.22, 0.13])
          with col_item_l:
            camp_badge = "춘천" if "춘천" in d_info["campus"] else "삼척·도계"
            st.markdown(
                f'<span style="background-color: #f1f5f9; color: #475569; font-weight: 600; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; margin-right: 6px; border: 1px solid #e2e8f0;">{camp_badge}</span>'
                f'<span style="color: #64748b; font-size: 0.88em;">{d_info["college"]} &gt; </span>'
                f'<strong style="color: #0f172a;">{d_name}</strong>',
                unsafe_allow_html=True,
            )
          with col_item_m:
            st.markdown(
                f"<small><a href='{d_info['url']}' target='_blank' style='color:#2563eb; text-decoration:none;'>공지 바로가기</a></small>",
                unsafe_allow_html=True,
            )
          with col_item_r:
            if st.button("삭제", key=f"del_{d_name}", help=f"{d_name} 제거"):
              del st.session_state.prof_added_depts[d_name]
              st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        if len(st.session_state.prof_added_depts) > 1:
          if st.button("추가된 학과 전체 비우기", type="secondary"):
            st.session_state.prof_added_depts = {}
            st.rerun()
      else:
        st.info("학과를 선택한 후 [선택 학과 추가] 버튼을 눌러주세요. 캠퍼스를 변경하여 여러 캠퍼스의 학과도 자유롭게 추가할 수 있습니다.")

      st.markdown("</div>", unsafe_allow_html=True)

      col_btn_l, col_btn_r = st.columns([0.3, 0.7])
      with col_btn_r:
        if st.button(
            "공지사항 통합 조회 시작하기",
            type="primary",
            use_container_width=True,
        ):
          if not st.session_state.prof_added_depts:
            st.error("최소 1개 이상의 학과를 추가해 주세요.")
          else:
            final_depts_list = list(st.session_state.prof_added_depts.keys())
            final_urls_map = {
                k: v["url"] for k, v in st.session_state.prof_added_depts.items()
            }
            final_labels_map = {
                k: f"[{'춘천' if '춘천' in v['campus'] else '삼척'}] {k}"
                for k, v in st.session_state.prof_added_depts.items()
            }

            st.session_state.user_role = "professor"
            st.session_state.selected_campus = "전체 캠퍼스"
            st.session_state.selected_college = "전체 단과대학"
            st.session_state.selected_depts = final_depts_list
            st.session_state.selected_dept_urls = final_urls_map
            st.session_state.selected_dept_labels = final_labels_map
            st.session_state.selected_dept = ", ".join(final_depts_list)
            st.session_state.selected_dept_url = list(final_urls_map.values())[0]
            st.session_state.onboarded = True
            st.rerun()

  st.stop()


# =============================================================================
# [메인 검색 화면] 소속 학과 공지 (복수 학과 지원) + 강원대 통합 공지 결합 검색
# =============================================================================

# 1. 상단 고정 Glassmorphism 네비게이션 바
curr_role_text = "교수 모드 (복수 모니터링)" if st.session_state.user_role == "professor" else "학생 모드 (소속 학과 맞춤)"
st.markdown(
    f"""<div class="knu-navbar">
        <div class="navbar-brand">
            <span class="knu-emblem">KNU</span>
            <span class="navbar-title">강원대학교 공지사항 스마트 검색</span>
            <span class="navbar-subpill">Smart Notice Portal</span>
        </div>
        <div class="navbar-status">
            <span class="status-indicator"></span>
            <span>{curr_role_text}</span>
        </div>
    </div>""",
    unsafe_allow_html=True,
)

col_title, col_change_dept = st.columns([0.80, 0.20])

with col_title:
  if st.session_state.user_role == "professor":
    dept_badges = " ".join([
        f'<span class="badge badge-dept">{st.session_state.selected_dept_labels.get(d, d)}</span>'
        for d in st.session_state.selected_depts
    ])
    st.markdown(
        f"""<div class="app-header-box">
            <div style="font-size: 0.84rem; font-weight: 700; color: #1e40af; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 4px;">
                Professor Monitoring Dashboard
            </div>
            <h2 style="margin: 0 0 10px 0; color: #0f172a; font-weight: 800; font-size: 1.45rem;">
                선택 학과 및 대학 포털 통합 공지 모니터링
            </h2>
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 8px;">
                <span style="background-color: #f1f5f9; color: #334155; padding: 3px 9px; border-radius: 6px; font-weight: 700; font-size: 0.8rem; border: 1px solid #e2e8f0;">선택 {len(st.session_state.selected_depts)}개 학과</span>
                {dept_badges}
            </div>
            <div style="color: #64748b; font-size: 0.86rem; margin-top: 8px;">
                선택하신 학과 홈페이지 공지사항과 강원대학교 포털 통합 공지를 실시간으로 분석합니다.
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
  else:
    st.markdown(
        f"""<div class="app-header-box">
            <div style="font-size: 0.84rem; font-weight: 700; color: #1e40af; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 4px;">
                Student Academic Notice Feed
            </div>
            <h2 style="margin: 0 0 10px 0; color: #0f172a; font-weight: 800; font-size: 1.45rem;">
                {st.session_state.selected_dept} 맞춤형 공지 검색
            </h2>
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 8px;">
                <span class="badge badge-dept">{st.session_state.selected_campus}</span>
                <span class="badge badge-general">{st.session_state.selected_college}</span>
                <span class="badge badge-academic" style="font-size: 0.84rem;">{st.session_state.selected_dept}</span>
            </div>
            <div style="color: #64748b; font-size: 0.86rem; margin-top: 8px;">
                선택하신 학과 공지와 강원대학교 포털 통합 공지를 결합하여 최적의 학사 정보를 제공합니다.
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

with col_change_dept:
  st.write("")
  if st.button("학과/모드 재설정", use_container_width=True, type="secondary"):
    st.session_state.onboarded = False
    st.rerun()

# 사이드바: 검색 옵션 설정
st.sidebar.markdown("### 검색 옵션")
today = datetime.now().date()
four_years_ago = today - timedelta(days=365 * 4)
default_2months_ago = today - timedelta(days=60)

selected_date = st.sidebar.date_input(
    "조회 기간 시작일 (기본: 최근 2개월)",
    value=st.session_state.applied_period,
    min_value=four_years_ago,
    max_value=today,
    help="기본으로 최근 2개월 전 공지부터 표시되며, 최대 4년 전까지 선택할 수 있습니다.",
)

col_apply, col_reload = st.sidebar.columns(2)
with col_apply:
  if st.button("기간 적용", use_container_width=True, type="primary"):
    st.session_state.applied_period = selected_date
    st.rerun()

with col_reload:
  if st.button("캐시 새로고침", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.divider()

if st.session_state.user_role == "professor":
  st.sidebar.markdown(
      f"**모니터링 학과 ({len(st.session_state.selected_depts)}개):**"
  )
  for d_name in st.session_state.selected_depts:
    d_url = st.session_state.selected_dept_urls.get(d_name, "")
    d_label = st.session_state.selected_dept_labels.get(d_name, d_name)
    if d_url:
      st.sidebar.markdown(
          f"• **{d_label}** [바로가기]({d_url})", unsafe_allow_html=True
      )
    else:
      st.sidebar.markdown(f"• **{d_label}**")
else:
  st.sidebar.markdown(
      f"""**현재 선택 학과:**<br>
`{st.session_state.selected_dept}`<br>
<small><a href="{st.session_state.selected_dept_url}" target="_blank" style="color:#2563eb; text-decoration:none;">학과 공지 바로가기</a></small>
""",
      unsafe_allow_html=True,
  )


def reset_all():
  st.session_state.user_query = ""
  st.session_state.applied_period = default_2months_ago


# 메인 화면: 입력창과 초기화 버튼
col_input, col_btn = st.columns([0.87, 0.13])

with col_input:
  user_query = st.text_input(
      "궁금한 학사 주제를 입력하세요 (실질 명사 중심 검색)",
      key="user_query",
      placeholder=(
          "예: 등록금 분할납부 기간, 국가장학금 신청, 졸업요건, 수강신청 일정 등"
      ),
  )

with col_btn:
  st.write("")
  st.write("")
  if st.button("초기화", on_click=reset_all, use_container_width=True):
    st.rerun()

# 통합 공지 및 학과 공지 로딩
loading_target = (
    f"{len(st.session_state.selected_depts)}개 학과"
    if st.session_state.user_role == "professor"
    else st.session_state.selected_dept
)
with st.spinner(
    f"통합 공지 및 {loading_target} 공지사항을 수집 중입니다..."
):
  knu_notices = fetch_knu_integrated_notices()

  # 학과 공지사항 수집 (복수 학과일 경우 ThreadPoolExecutor로 병렬 수집)
  dept_notices = []
  if st.session_state.user_role == "professor":
    max_th = min(len(st.session_state.selected_dept_urls), 8)
    with ThreadPoolExecutor(max_workers=max_th) as executor:
      futures = [
          executor.submit(fetch_department_notices, d_name, d_url)
          for d_name, d_url in st.session_state.selected_dept_urls.items()
      ]
      for f in futures:
        try:
          dept_notices.extend(f.result())
        except Exception:
          pass
  else:
    dept_notices = fetch_department_notices(
        st.session_state.selected_dept, st.session_state.selected_dept_url
    )

  # 중복 완전 방지 결합 (Canonical Link 및 Normalized Title 기준)
  all_combined_notices = []
  global_seen_links = set()
  global_seen_titles = set()

  # 학과 공지 우선 등록
  for n in dept_notices:
    c_link = n["link"]
    n_title = normalize_title(n["title"])
    if c_link not in global_seen_links and n_title not in global_seen_titles:
      global_seen_links.add(c_link)
      global_seen_titles.add(n_title)
      all_combined_notices.append(n)

  # 강원대 통합 공지 등록
  for n in knu_notices:
    c_link = n["link"]
    n_title = normalize_title(n["title"])
    if c_link not in global_seen_links and n_title not in global_seen_titles:
      global_seen_links.add(c_link)
      global_seen_titles.add(n_title)
      all_combined_notices.append(n)

  # ⭐️ 기본 정렬: 조회수(views) 높은 순으로 나열 (동일 조회수일 경우 최신순)
  all_combined_notices.sort(
      key=lambda x: (x.get("views", 0), x["datetime"]), reverse=True
  )
  model = load_embedding_model()

if all_combined_notices:
  filtered_notices = []
  current_filter_date = st.session_state.applied_period

  period_filtered = [
      item
      for item in all_combined_notices
      if item["datetime"] >= current_filter_date
  ]

  if user_query.strip():
    query_text = user_query.strip()

    # =========================================================================
    # 🔍 [1단계] 메타 보조어(자료, 공지) 및 추상어 배제, 오타 유사도 자동 보정 분석
    # =========================================================================
    core_kws, syn_kws, abs_kws, meta_kws, typo_corrs = extract_keywords_and_synonyms(query_text)
    all_search_terms = list(set(core_kws + syn_kws))

    # 추상적인 단어 또는 메타 단어만 단독으로 들어왔을 경우 안내
    if not all_search_terms and (abs_kws or meta_kws):
      warn_msg = []
      if meta_kws:
        warn_msg.append(f"'{', '.join(meta_kws)}'(은)는 문맥상 지시/보조어이므로 단독 검색 기준으로 사용되지 않습니다.")
      if abs_kws:
        warn_msg.append(f"'{', '.join(abs_kws)}'과 같은 추상적인 단어는 학사 공지 검색 기준으로 사용되지 않습니다.")
      st.warning(f"💡 {' '.join(warn_msg)} 구체적인 학사 주제어(예: 등록금, 장학금, 수강신청, 졸업, 자격증 등)를 입력해 주세요.")

    with st.spinner(
        "AI 임베딩 의미 유사도 분석 및 핵심 키워드로 공지사항을 검색 중입니다..."
    ):
      # 1-1. 제목 기반 키워드 매칭 (단어 경계 정밀 검사로 영단어 일부 일치 방지)
      title_matches = []
      for item in period_filtered:
        t_text = item["title"]
        matched_in_title = [
            term for term in all_search_terms if is_term_matched(term, t_text)
        ]
        if matched_in_title:
          title_matches.append({
              "item": item,
              "matched_terms": matched_in_title,
              "match_type": "제목 키워드 일치",
          })

      # 🧠 1-2. AI 임베딩 코사인 유사도 분석 (약어의 시맨틱 확장 반영)
      # 'ai' 등 약어가 입력된 경우, 확장된 유의어('인공지능')를 시맨틱 쿼리에 반영하여 임베딩 코사인 유사도 정밀도 극대화
      semantic_query = query_text
      if all_search_terms:
        extra_syns = [
            s for s in all_search_terms if s.lower() != query_text.lower()
        ][:3]
        if extra_syns:
          semantic_query = f"{query_text} {' '.join(extra_syns)}"

      query_embedding = model.encode(semantic_query, convert_to_tensor=True)
      period_titles = [it["title"] for it in period_filtered]
      
      emb_top_items = []
      if period_titles:
        title_embs = model.encode(period_titles, convert_to_tensor=True, show_progress_bar=False)
        title_sim_scores = util.cos_sim(query_embedding, title_embs)[0].tolist()
        
        # 제목 임베딩 유사도 점수를 각 item에 매핑
        indexed_scores = list(enumerate(title_sim_scores))
        # 유사도 내림차순 정렬
        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 임베딩 유사도 기준: 상위 25개 또는 유사도 0.30 이상인 공지를 임베딩 후보로 선정
        for idx_sc, sim_val in indexed_scores[:25]:
          if sim_val >= 0.28:
            matched_item = period_filtered[idx_sc]
            emb_top_items.append((matched_item, sim_val))

      # 1-3. 본문 크롤링 대상 취합 (키워드 매칭 + 임베딩 상위 후보 + 학과 공지)
      sample_for_body = [it for it in period_filtered if it.get("is_dept")]
      for tm in title_matches:
        if tm["item"] not in sample_for_body:
          sample_for_body.append(tm["item"])
      for emb_item, _ in emb_top_items:
        if emb_item not in sample_for_body:
          sample_for_body.append(emb_item)

      # 최대 50개까지만 심층 본문 분석 진행 (네트워크 및 성능 최적화)
      sample_for_body = sample_for_body[:50]

      links_to_fetch = [it["link"] for it in sample_for_body]
      with ThreadPoolExecutor(max_workers=10) as executor:
        fetched_contents = list(
            executor.map(fetch_notice_content, links_to_fetch)
        )

      content_dict = {
          it["link"]: c for it, c in zip(sample_for_body, fetched_contents)
      }

      stage1_candidates = []
      seen_candidate_links = set()

      # 제목 키워드 매칭된 공지 후보 등록
      for tm in title_matches:
        link = tm["item"]["link"]
        if link in content_dict:
          seen_candidate_links.add(link)
          body_txt = content_dict.get(link, "")
          body_matched = [
              term
              for term in all_search_terms
              if is_term_matched(term, body_txt)
              and term not in tm["matched_terms"]
          ]
          all_matched = list(set(tm["matched_terms"] + body_matched))
          stage1_candidates.append({
              "item": tm["item"],
              "matched_terms": all_matched,
              "content": body_txt,
              "match_src": "제목 & 본문 키워드",
          })

      # 본문 키워드 매칭된 공지 후보 등록
      for it in sample_for_body:
        link = it["link"]
        if link in seen_candidate_links:
          continue
        body_txt = content_dict.get(link, "")
        if body_txt and all_search_terms:
          body_matched = [
              term for term in all_search_terms if is_term_matched(term, body_txt)
          ]
          if body_matched:
            seen_candidate_links.add(link)
            stage1_candidates.append({
                "item": it,
                "matched_terms": body_matched,
                "content": body_txt,
                "match_src": "본문 키워드 포함",
            })

      # 🧠 AI 임베딩 유사도로 발굴된 공지 (키워드에 직접 안 걸려도 오타/문맥 유사도로 포섭)
      for emb_item, sim_val in emb_top_items:
        link = emb_item["link"]
        if link not in seen_candidate_links:
          seen_candidate_links.add(link)
          body_txt = content_dict.get(link, "")
          stage1_candidates.append({
              "item": emb_item,
              "matched_terms": core_kws if core_kws else [query_text],
              "content": body_txt,
              "match_src": "AI 임베딩 의미/오타 매칭",
          })

    # =========================================================================
    # 🧠 [2단계] 선별된 공지들의 본문 심층 문맥 분석 (Semantic Reranking)
    # =========================================================================
    if stage1_candidates:
      with st.spinner(
          f"2단계: 선별된 {len(stage1_candidates)}개 공지의 본문 내용을 심층"
          " 분석 중입니다..."
      ):
        stage2_results = []

        for cand in stage1_candidates:
          item = cand["item"]
          content = cand["content"]
          matched_terms = cand["matched_terms"]

          t_emb = model.encode(item["title"], convert_to_tensor=True)
          t_score = util.cos_sim(query_embedding, t_emb).item()

          chunks = chunk_text(content)
          best_chunk_score = 0.0
          best_chunk_text = ""

          if chunks:
            c_embs = model.encode(chunks, convert_to_tensor=True)
            c_scores = util.cos_sim(query_embedding, c_embs)[0]
            best_idx = c_scores.argmax().item()
            best_chunk_score = c_scores[best_idx].item()
            best_chunk_text = chunks[best_idx]

          # 키워드 매칭 보너스 및 학과 공지 가산점
          keyword_bonus = min(len(matched_terms) * 0.04, 0.15) if "키워드" in cand["match_src"] else 0.0
          dept_bonus = 0.05 if item.get("is_dept") else 0.0

          if best_chunk_score > 0:
            final_score = (
                max(t_score, best_chunk_score * 1.05)
                + keyword_bonus
                + dept_bonus
            )
          else:
            final_score = t_score + keyword_bonus + dept_bonus

          res = dict(item)
          res["final_score"] = final_score
          res["content_score"] = best_chunk_score
          res["title_score"] = t_score
          res["matched_terms"] = matched_terms
          res["match_src"] = cand["match_src"]
          res["best_chunk"] = best_chunk_text
          res["summary"] = generate_notice_summary(
              content, matched_terms, item.get("title", "")
          )
          stage2_results.append(res)

        # 유사도 0.28 이상인 유의미한 검색 결과 선별
        valid_results = [
            r for r in stage2_results if r["final_score"] >= 0.28
        ]
        # ⭐️ 검색 후에는 최신 날짜 순(datetime 내림차순, 동일 날짜 시 관련도 및 조회수 순)으로 정렬!
        valid_results.sort(
            key=lambda x: (x["datetime"], x["final_score"], x.get("views", 0)),
            reverse=True,
        )
        filtered_notices = valid_results
    else:
      filtered_notices = []

  else:
    # ⭐️ 검색어 입력 전: 2개월 기간 내 공지들이 조회수 높은 순으로 나열
    filtered_notices = period_filtered

  dept_notice_count = sum(1 for it in filtered_notices if it.get("is_dept"))
  knu_notice_count = len(filtered_notices) - dept_notice_count
  period_msg = f"[{current_filter_date} ~ {today}] 공지사항 |"

  if user_query.strip():
    if filtered_notices:
      st.success(
          f"{period_msg} 검색 완료: 총"
          f" **{len(filtered_notices)}건**의 연관 공지사항이 **최신 날짜 순**으로 나열되어 있습니다. (학과 공지:"
          f" {dept_notice_count}건, 통합 공지: {knu_notice_count}건)"
      )
    else:
      st.warning(
          "입력하신 검색어와 일치하는 문서(제목 또는 본문)를 찾지 못했습니다."
          " 다른 실질 키워드로 검색해 보세요."
      )
  else:
    dept_label_info = (
        f"{len(st.session_state.selected_depts)}개 학과"
        if st.session_state.user_role == "professor"
        else st.session_state.selected_dept
    )
    st.info(
        f"{period_msg} 총 **{len(filtered_notices)}건**의 공지사항이 **조회수"
        f" 높은 순**으로 나열되어 있습니다. (학과 공지:"
        f" {dept_notice_count}건 / 통합 공지: {knu_notice_count}건)"
    )

  st.divider()

  # 모던 카드형 공지사항 결과 리스트 렌더링 (공지 유형별 파스텔 뱃지 & 입체감 적용)
  for idx, item in enumerate(filtered_notices, 1):
    is_dept = item.get("is_dept", False)
    board_chip_html = get_board_badge_html(item["board"], is_dept=is_dept)
    views_val = item.get("views", 0)
    views_chip_html = f'<span class="views-chip">조회 {views_val:,}회</span>'
    date_chip_html = f'<span class="date-chip">{item["date"]}</span>'

    summary_html = ""
    if user_query.strip() and item.get("summary"):
      summary_html = f"""
      <div class="clean-summary-box">
          <div class="clean-summary-header">본문 요약</div>
          <div>{item['summary']}</div>
      </div>
      """

    card_html = f"""
    <div class="modern-notice-card">
        <div class="card-meta-bar">
            <div class="card-meta-left">
                {board_chip_html}
                {date_chip_html}
                {views_chip_html}
            </div>
            <div>
                <a href="{item['link']}" target="_blank" class="origin-btn">원문 바로가기</a>
            </div>
        </div>
        <div class="notice-card-title">
            <a href="{item['link']}" target="_blank">{idx}. {item['title']}</a>
        </div>
        {summary_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
else:
  st.error(
      "공지사항을 가져오지 못했습니다. 네트워크 연결 상태를 확인해 주세요."
  )
