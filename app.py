from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
from pymongo import MongoClient
# import datetime

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


client = MongoClient('mongodb+srv://sparta:test@cluster0.9fktzhz.mongodb.net/?retryWrites=true&w=majority') #각자의 DB 주소를 넣어주세요
db = client.habitTracker #각자의 DB 및 collection

# client = MongoClient('mongodb+srv://devdeeplake:<password>@cluster0.p2pjkxs.mongodb.net/?retryWrites=true&w=majority') #각자의 DB 주소를 넣어주세요
# db = client.habitTracker


@app.route('/')
def home():
   return render_template('index.html')

@app.route('/signUp')
def sign_up():
   return render_template('sign-up.html')

@app.route('/login')
def login():
   return render_template('login.html')


@app.route("/showHabit", methods=["POST"])
def showHabit_post():
    userid_receive = request.form['User_ID_give']
    week_list = findWeekDate(datetime.today())

    or_query = { '$or': [{"startDate":week_list[0]},{"startDate":week_list[1]},{"startDate":week_list[2]},{"startDate":week_list[3]},{"startDate":week_list[4]},{"startDate":week_list[5]},{"startDate":week_list[6]}] }

    query = {'$and': [ { 'userid' : userid_receive }, or_query ] }

    habit_list = list(db.habits.find(query).sort('_id',-1))
    results = []
    for document in habit_list:
        document['_id'] = str(document['_id'])
        results.append(document)

    print(results)
    return jsonify({'result': results})


@app.route("/addHabit", methods=["POST"])
def addHabit_post():
    userid_receive = request.form['User_ID_give']
    todo_receive = request.form['TODO_give']
    complete_recive = [True,True,True,True,True,True,True]
    displayDate_recive = ['2023-03-28','2023-03-29','2023-03-30','2023-03-31','2023-04-01','2023-04-02','2023-04-03']

    dtBunch_recive = {}
    for day in range(7):
        dt = datetime.today() + timedelta(days=day)
        result = dt.strftime("%Y-%m-%d")
        dtBunch_recive[result] = False

    doc = {
        'userid' : userid_receive,
        'habit' : todo_receive,
        'complete' : complete_recive,
        'startDate' : datetime.today().strftime("%Y-%m-%d"),
        'displayDate' : displayDate_recive,
        'dtBunch' : dtBunch_recive
    }

    db.habits.insert_one(doc)
    return jsonify({'result': 'result 완료!'})


@app.route("/dateShow", methods=["GET"])
def getWeekDates() :
    # 오늘 날짜를 계산해서, 오늘 날짜가 포함된 월 ~ 일의 date를 프론트로 리턴
    now = datetime.today()
    thisWeekDates = findWeekDate(now)
    return jsonify({"result": thisWeekDates})


if __name__ == '__main__':
   app.run('0.0.0.0', port=5001, debug=True) #Mac 용 세팅
#    app.run('0.0.0.0', port=5000, debug=True) #Mac 분들은 주의해주세요
