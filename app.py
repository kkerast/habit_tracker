from flask import Flask, render_template, request, jsonify, session, redirect, url_for
# from datetime import datetime, timedelta
from datetime import timedelta
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import certifi

def dateToStr (date, pattern) : # date를 string으로 바꿔주되, pattern대로 바꿔주는 함수
    stringified = date.strftime(pattern)
    return stringified

def findWeekDate (dateStr) : # 날짜 str를 넣으면 해당일이 속한 주의 날짜 Str 배열을 돌려주는 함수
    strToDate = datetime.datetime.strptime(dateStr, "%Y-%m-%d")
    day = strToDate.weekday()
    weekDate = []
    weekStartsAt = datetime.datetime.strptime(strToDate.strftime("%Y-%m-%d"), "%Y-%m-%d")
    if (day != 0):
        weekStartsAt = weekStartsAt - timedelta(days = day)

    for i in range(0, 7):
        thisDate = weekStartsAt + timedelta(days = i)
        thisDateStr = dateToStr(thisDate, "%Y-%m-%d")
        weekDate.append(thisDateStr)
    
    return weekDate

def repeat_check (database, id , habit = 'none') : #인자로 전달되는 Habit이 중복인지 아닌지 확인해서 중복이면 True 중복이 아니면 False를 돌려주는함수
    print(habit)
    if habit == 'none':
        repeat_habit = list(database.find(id).sort('_id',-1))#이때 id값은 query ={ 'id' : id_receive } 거나 query ={ 'nick' : nickname_receive } 이다.
    else:
        repeat_habit = list(database.find({'$and': [ { 'userid' : id }, {'habit':habit} ] }).sort('_id',-1))
    print(repeat_habit)
    if repeat_habit != []:
        return True
    elif repeat_habit == []:
        return False

    
app = Flask(__name__)


ca=certifi.where()

client = MongoClient('mongodb+srv://sparta:test@cluster0.9fktzhz.mongodb.net/?retryWrites=true&w=majority') #각자의 DB 주소를 넣어주세요
db = client.habitTracker #각자의 DB 및 collection

# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'SPARTA'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib


#################################
##  HTML을 주는 부분             ##
#################################
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('index.html', nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')


#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    query ={ 'id' : id_receive }
    if ( repeat_check (db.user, query)):
        return jsonify({'result': 'fail' , 'msg': 'id_repeat'})
    
    pw_receive = request.form['pw_give']
    
    nickname_receive = request.form['nickname_give']
    query ={ 'nick' : nickname_receive }
    if ( repeat_check (db.user, query)):
        return jsonify({'result': 'fail', 'msg': 'nickname_receive_repeat'})    

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

@app.route("/showHabit", methods=["POST"])
def showHabit_post():
    userid_receive = request.form['User_ID_give']
    dateStr_receive = request.form["dateStr_give"]
    # dateList = dateStr_receive.split("-")
    # year = int(dateList[0])
    # month = int(dateList[1])
    # date = int(dateList[2])
    # print(datetime.date(year, month, date))
    # print(year)
    # print(month)
    # print(date)
    # print(dateList)
    week_list = findWeekDate(dateStr_receive)
    print(week_list)

    or_query = { '$or': [{"startDate":week_list[0]},{"startDate":week_list[1]},{"startDate":week_list[2]},{"startDate":week_list[3]},{"startDate":week_list[4]},{"startDate":week_list[5]},{"startDate":week_list[6]}] }

    query = {'$and': [ { 'userid' : userid_receive }, or_query ] }

    habit_list = list(db.habits.find(query).sort('_id',-1))
    results = []
    for document in habit_list:
        document['_id'] = str(document['_id'])
        results.append(document)

    #print(results)
    return jsonify({'result': results})

@app.route("/Habit", methods=["POST"])
def Habit_post(): # 맨처음 habit이 생성될 때 Habit이 생성된 주차의 더미 데이터를 넣어줌 (dtBunch => 날짜: false)
    # 수정사항 : 시작일을 받아오면, 시작일부터 dtBunch에 데이터 넣어주기 (이전 데이터는 넣지 않기)
    userid_receive = request.form['User_ID_give']
    todo_receive = request.form['TODO_give']
    complete_receive = []

    # complete_receive = [True,True,True,True,True,True,True]
    # displayDate_recieve = ['2023-03-28','2023-03-29','2023-03-30','2023-03-31','2023-04-01','2023-04-02','2023-04-03']

    today = datetime.datetime.today()
    thisDateStr = dateToStr(today, "%Y-%m-%d") # 오늘의 date객체를 string 형식으로 바꿔줌
    thisDay = today.weekday() # 요일을 0 ~ 6의 숫자로 리턴 (월 ~ 일)

    week_list = findWeekDate(thisDateStr) # 오늘이 속한 주의 날짜 배열(7개 원소)을 돌려줌
    for pastDay in range(0, thisDay):
        complete_receive.append("none")

    dtBunch_recieve = {}
    repeat = repeat_check (db.habits, userid_receive , todo_receive)
    if( repeat ) :
        return jsonify({'result': '중복으로 인한 추가 불가!!'})
    for day in range(thisDay, 7): # 시작일부터 일요일까지, dtBunch에 쓸 데이터 생성
        print(day)
        complete_receive.append(False)
        dtBunch_recieve[week_list[day]] = False

    doc = {
        'userid' : userid_receive,
        'habit' : todo_receive,
        'complete' : complete_receive,
        'startDate' : datetime.datetime.today().strftime("%Y-%m-%d"),
        'displayDate' : week_list,
        'dtBunch' : dtBunch_recieve
    }

    db.habits.insert_one(doc)
    return jsonify({'result': 'add'})
    
@app.route("/Habit/<id>", methods=["DELETE","PUT"])
def Habit_del_put(id):
    if request.method == 'DELETE':
        print('del',id)
        query = {"_id": ObjectId(id)}
        db.habits.delete_one(query)
        return jsonify({'result': 'result 완료!'})
    
    elif request.method == 'PUT':
        
        example = request.json
        print('PUT',id,example)
        userid_receive = example['User_ID_give']
        todo_receive = example['TODO_give']
        query = {"_id": ObjectId(id)}
        set_query = {'habit' : todo_receive}
        new_values = {"$set": set_query}
        
        repeat = repeat_check (db.habits, userid_receive , todo_receive)
        print(repeat)
        if( repeat ) :
            return jsonify({'result': '중복으로 인한 수정 불가!!'})        
        
        db.habits.update_one(query, new_values)

        return jsonify({'result': 'update'})

@app.route("/HabitComp/<id>", methods=["POST"])
def Habit_comp(id):
    changeComple = request.form['habit_update_give']

    strings = changeComple.split(',')
    for a in range(7):
        print(strings[a])
        if strings[a] == 'true':
            strings[a] = True
        elif strings[a] == 'false':
            strings[a] = False #문자열을 불리언으로 바꿔서 저장

    
    #이전값에서 뒤에 7개 지우고 추가해야함



    #데이터바꿈
    print('habit_update_give', id, strings)
    query = {"_id": ObjectId(id)}
    new_values = {"$set": {'complete':strings}}

    
    db.habits.update_one(query, new_values)
    return jsonify({'result': 'result 완료!'})


@app.route("/dateShow", methods=["GET"])
def getWeekDates() :
    # 오늘 날짜를 계산해서, 오늘 날짜가 포함된 월 ~ 일의 date를 프론트로 리턴
    now = datetime.datetime.today()
    nowStr = dateToStr(now, "%Y-%m-%d")
    thisWeekDates = findWeekDate(nowStr)
    #print(thisWeekDates)
    return jsonify({"result": thisWeekDates})


@app.route("/habitDateChange", methods=["GET"])
def showChangedWeek() :
    userid_recieve = request.args.get("userid").strip('"')
    weekStartDate_recieve = request.args.get("weekStartDate").strip('"')
    weekdates = findWeekDate(weekStartDate_recieve)
    userDataWhole = list(db.habits.find({"userid": userid_recieve}))

    # or_query = { '$or': [{"startDate":week_list[0]},{"startDate":week_list[1]},{"startDate":week_list[2]},{"startDate":week_list[3]},{"startDate":week_list[4]},{"startDate":week_list[5]},{"startDate":week_list[6]}] }
    returnData = []
    for idx, data in enumerate(userDataWhole):
        habitId = str(data["_id"])
        userId = data["userid"]
        habit = data["habit"]
        complete = []
        # startDate = data["startDate"]
        displayDate = weekdates

        dtBunchDates = data["dtBunch"].keys()
        print(dtBunchDates)
        for date in weekdates:
            if date in dtBunchDates:
                dayComplete = data["dtBunch"][date]
                complete.append(dayComplete)
            else:
                complete.append("none")

        repackDict = {
            "userid": userId,
            "_id": habitId,
            "habit": habit,
            "displayDate": displayDate,
            "complete": complete
        }

        returnData.append(repackDict)

    return jsonify({"result" : returnData})



if __name__ == '__main__':
   app.run('0.0.0.0', port=5001, debug=True) #Mac 용 세팅
#    app.run('0.0.0.0', port=5000, debug=True) #Mac 분들은 주의해주세요
