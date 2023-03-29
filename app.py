from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

def dateToStr (date, pattern) : # date를 string으로 바꿔주되, pattern대로 바꿔주는 함수
    stringified = date.strftime(pattern)
    return stringified

def findWeekDate (date) : # 날짜를 넣으면 해당일이 속한 주의 첫번째 날짜를 돌려주는 함수
    day = date.weekday()
    weekDate = []
    weekStartsAt = datetime.strptime(date.strftime("%Y-%m-%d"), "%Y-%m-%d")
    if (day != 0):
        weekStartsAt = weekStartsAt - timedelta(days = day)

    for i in range(0, 7):
        thisDate = weekStartsAt + timedelta(days = i)
        thisDateStr = dateToStr(thisDate, "%Y-%m-%d")
        weekDate.append(thisDateStr)
    
    return weekDate

app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://devdeeplake:<password>@cluster0.p2pjkxs.mongodb.net/?retryWrites=true&w=majority') #각자의 DB 주소를 넣어주세요
db = client.habitTracker


@app.route('/')
def home():
   return render_template('index.html')

@app.route('/signUp')
def sign_up():
   return render_template('sign-up.html')

@app.route('/login')
def login():
   return render_template('login.html')




@app.route("/guestbook", methods=["POST"])
def guestbook_post():

    return jsonify({'result': 'result 완료!'})




@app.route("/guestbook", methods=["GET"])
def guestbook_get():


    return jsonify({'result': 'result'})


@app.route("/dateShow", methods=["GET"])
def getWeekDates() :
    # 오늘 날짜를 계산해서, 오늘 날짜가 포함된 월 ~ 일의 date를 프론트로 리턴
    now = datetime.today()
    thisWeekDates = findWeekDate(now)
    return jsonify({"result": thisWeekDates})




if __name__ == '__main__':
    # app.run('0.0.0.0', port=5000, debug=True) #Mac 분들은 주의해주세요
   app.run('0.0.0.0', port=5001, debug=True) #Mac 용 세팅