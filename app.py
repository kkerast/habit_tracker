from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('각자의 db 주소') #각자의 DB 주소를 넣어주세요
db = client.dbsparta


@app.route('/')
def home():
   return render_template('index.html')




@app.route("/guestbook", methods=["POST"])
def guestbook_post():

    return jsonify({'result': 'result 완료!'})




@app.route("/guestbook", methods=["GET"])
def guestbook_get():


    return jsonify({'result': 'result'})



if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True) #Mac 분들은 주의해주세요