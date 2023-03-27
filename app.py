from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
import datetime
from pymongo import MongoClient
client = MongoClient('mongodb+srv://sparta:test@cluster0.9fktzhz.mongodb.net/?retryWrites=true&w=majority') #각자의 DB 주소를 넣어주세요
db = client.toy_project.habit #각자의 DB 및 collection


@app.route('/')
def home():
   return render_template('index.html')




@app.route("/addHabit", methods=["POST"])
def guestbook_post():
    userid_receive = request.form['User_ID_give']
    todo_receive = request.form['TODO_give']
    print(todo_receive,userid_receive)
    doc = {
        'userid' : userid_receive,
        'todo' : todo_receive,
        'DATE' : datetime.datetime.now()
    }
    
    db.insert_one(doc)
    return jsonify({'result': 'result 완료!'})




if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True) #Mac 분들은 주의해주세요