#######################
# app.py
#######################
from flask import Flask, render_template, request

app = Flask(__name__)

# 예) DB를 사용한다면, DB 연결 설정
# from flask_pymongo import PyMongo
# app.config["MONGO_URI"] = "mongodb://localhost:27017/test"
# mongo = PyMongo(app)

# 또는 SQLAlchemy 사용 시
# from flask_sqlalchemy import SQLAlchemy
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# db = SQLAlchemy(app)

# Spreadsheet를 이용한다면 어떻게 할 수 있을 지 고민하기

############################
# (1) 메인 대시보드 라우트
############################
@app.route('/')
def main_dashboard():
    # 1) 스포츠 카테고리 가져오기 (예: ["축구", "농구", "야구"...])
    # 이 부분은 저장소(db, spreadsheet)에서 읽어오거나, 하드코딩 리스트로도 가능
    sports_categories = ["축구", "농구", "야구", "배구", "테니스"]
    
    # 2) 인기 부상 사례
    # 예시로 하드코딩; 실제로는 DB에서 "조회수"나 "발생 빈도" 높은 순으로 불러오기
    popular_injuries = [
        {"title": "전방십자인대 파열(ACL)", "desc": "무릎에 흔히 발생하는 심각 부상"},
        {"title": "발목 염좌", "desc": "점프 착지 시 자주 발생"},
        {"title": "허리디스크", "desc": "무거운 중량 운동 시 주의"}
    ]

    # 3) 오늘의 팁
    # 예시로 1개만 전달
    tip_of_the_day = "운동 전후 10분 이상 충분히 스트레칭을 해주세요."

    # 4) 새로운 데이터 알림
    # 예: 최근 5개 부상 사례
    # 예시
    new_injuries = [
        {"sport": "농구", "injury": "아킬레스건 파열", "created_at": "2024-12-22"},
        {"sport": "축구", "injury": "무릎 연골 손상", "created_at": "2024-12-20"},
    ]

    return render_template(
        'index.html',
        sports_categories=sports_categories,
        popular_injuries=popular_injuries,
        tip_of_the_day=tip_of_the_day,
        new_injuries=new_injuries
    )


############################
# (2) 검색 기능 라우트
############################
@app.route('/search', methods=['GET'])
def search_injuries():
    # 사용자가 /search?q=발목 이런 식으로 검색어를 보내는 예시
    query = request.args.get('q', '')  # 기본값은 빈 문자열

    # 여기서 DB를 검색
    # injuries = mongo.db.injuries.find({"injury_name": {"$regex": query, "$options": "i"}})

    # 예시로 결과를 가정
    results = [
        {"injury_name": "발목 염좌", "sport": "농구", "desc": "점프 후 착지 시 부상"},
        {"injury_name": "발목 골절", "sport": "축구", "desc": "충돌로 인한 부상"}
    ]
    # 실제로는 위 로직 대신 DB나 검색엔진을 사용하시면 됩니다.

    return render_template(
        'search_result.html',
        query=query,
        results=results
    )


############################
# (3) 스포츠별 페이지 라우트 (선택사항)
############################
@app.route('/category/<sport_name>')
def show_sport_category(sport_name):
    # 예: /category/축구 → "축구" 관련 부상 사례만
    # DB 쿼리 예시 (MongoDB의 경우)
    # injuries = list(mongo.db.injuries.find({"sport": sport_name}))
    
    # 예시 데이터
    injuries = [
        {"injury_name": "발목 염좌", "sport": sport_name},
        {"injury_name": "무릎 부상", "sport": sport_name},
    ]

    return render_template(
        'category.html',
        sport_name=sport_name,
        injuries=injuries
    )


if __name__ == '__main__':
    app.run(debug=True)