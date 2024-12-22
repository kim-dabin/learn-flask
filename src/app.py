#######################
# app.py
#######################
import os
from flask import Flask, render_template, request
import requests
from pandas import DataFrame
import gspread
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()  # 기본적으로 현재 경로에 있는 .env를 찾습니다.

app = Flask(__name__)

#-----------------------------------
# 1) YouTube API로 데이터 가져오기 (샘플)
#-----------------------------------
def fetch_youtube_data(query="스포츠 부상", max_results=10):
    """
    YouTube Data API를 통해 'query' 검색 결과를 가져옵니다.
    반환: 동영상 정보 리스트 (title, videoId, channelTitle 등)
    """
    API_KEY =  os.environ.get('YOUTUBE_API_KEY')  # 실제로는 os.environ.get('YOUTUBE_API_KEY') 등
    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': max_results,
        'key': API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    video_list = []
    items = data.get("items", [])
    for item in items:
        snippet = item["snippet"]
        video_id = item["id"]["videoId"]
        video_info = {
            "title": snippet["title"],
            "video_id": video_id,
            "channel_title": snippet["channelTitle"],
            "published_at": snippet["publishedAt"]
        }
        video_list.append(video_info)

    return video_list


#-----------------------------------
# 2) Google Spreadsheet에서 데이터 가져오기 (샘플)
#-----------------------------------
def fetch_injury_types_from_sheet():
    """
    gspread를 통해 'Search_Result' 스프레드시트 중 '부상종류' 워크시트에 있는 데이터를 가져옵니다.
    반환: [{'부상명': ..., '스포츠': ...}, ...] 형태의 리스트
    """
    # 서비스 계정 JSON 파일명. 실제 경로/파일명 맞춰주세요.
    SERVICE_ACCOUNT_FILE = 'src/vital-reef-443808-f5-f838e0b0c962.json'

    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    wks = gc.open("Search_Result").worksheet('부상종류')

    # 워크시트의 모든 기록(첫 행 헤더로 자동 인식)
    records = wks.get_all_records()
    return records


#-----------------------------------
# 3) Flask 라우트
#-----------------------------------
@app.route('/')
def main_dashboard():
    """
    메인 대시보드:
    - 카테고리(스포츠) 목록
    - 검색창
    - 요약 카드(새로운 데이터, 오늘의 팁, 인기 부상 사례)
    - YouTube API 결과(필요 시)
    - Google Sheets 결과(필요 시)
    """
    # (1) 스포츠 카테고리 (하드코딩 or DB/스프레드시트/기타)
    sports_categories = ["축구", "농구", "야구", "배구", "테니스"]
    
    # (2) 인기 부상 사례 (하드코딩 or DB)
    popular_injuries = [
        {"title": "전방 십자인대 파열(ACL)", "desc": "무릎에 흔히 발생하는 심각한 부상"},
        {"title": "발목 염좌", "desc": "점프 착지 시 자주 발생"},
        {"title": "어깨 회전근개 파열", "desc": "과도한 스윙 동작에서 자주 발생"}
    ]

    # (3) 오늘의 팁 (1개만 노출 예시)
    tip_of_the_day = "운동 전후에 충분한 워밍업과 쿨다운을 하세요."

    # (4) 새로운 데이터 알림 (예시로 YouTube 최신 영상 5개)
    # 실제론 부상 사례 DB로부터 '최신 등록 순' 불러올 수도 있음
    new_injuries = fetch_youtube_data(query="스포츠 부상", max_results=5)
    # -> new_injuries에 [ {title, video_id, channel_title, published_at}, ... ] 형태로 담김
    print(new_injuries)
    # (5) 구글 시트에서 불상종류/데이터를 가져와서 필요 시 가공
    # 예: [{'부상명': '발목 염좌', '스포츠': '농구', ...}, ...]
    sheet_injury_data = fetch_injury_types_from_sheet()

    return render_template(
        'index.html',
        sports_categories=sports_categories,
        popular_injuries=popular_injuries,
        tip_of_the_day=tip_of_the_day,
        new_injuries=new_injuries,
        sheet_injury_data=sheet_injury_data
    )


@app.route('/search', methods=['GET'])
def search_injuries():
    """
    검색 처리:
    - ?q=발목 형태로 검색어 받음
    - 부상 이름, 스포츠 종류, 신체 부위 등에 대해 필터링
    - 결과 페이지 렌더링
    """
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('search_result.html', query="", results=[])

    # 예: 부상종류 시트에서 가져와서 간단 검색
    # 실제로는 DB에서 LIKE/REGEX 로 검색 가능
    records = fetch_injury_types_from_sheet()
    filtered = [
        r for r in records 
        if (query.lower() in r.get('부상명', '').lower()
            or query.lower() in r.get('스포츠', '').lower())
    ]

    return render_template('search_result.html', query=query, results=filtered)


@app.route('/category/<sport_name>')
def show_sport_category(sport_name):
    """
    카테고리(스포츠)별 페이지
    - sport_name에 해당하는 부상 정보 표시 (구글 시트 or DB)
    """
    records = fetch_injury_types_from_sheet()
    injuries = [r for r in records if r.get('스포츠') == sport_name]

    return render_template(
        'category.html',
        sport_name=sport_name,
        injuries=injuries
    )


# Flask 실행
if __name__ == '__main__':
    app.run(debug=True, port=5000)