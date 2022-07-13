from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'


#-----------------------------------------
# DB
#-----------------------------------------
# 회원 관리 정보 > users
# 상품 관리 정보 >game_info
# 리뷰 정보 > review

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.msszki5.mongodb.net/Cluster0?retryWrites=true&w=majority', 27017)
db=client.game
#client = MongoClient('localhost', 27017)
#db=client.dbsparta_plus_week4



#----------------------------------------------------------------------------------
# 로그인, 회원가입 (중복확인)
#----------------------------------------------------------------------------------


# 토큰 받아오기 -----------------------------------------
@app.route('/')
def home():
    
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info, user_category=user_info["usercategory"])


    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))





# 로그인 페이지 이동 + msg 출력-----------------------------------------

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)




# 로그인-----------------------------------------

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})




# 회원 가입 -----------------------------------------

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    #회원가입 api 정보를 받아서 db 저장
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']
    usercategory_receive = request.form['usercategory_give']
    #비밀 번호는 해쉬 처리
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "nickname": nickname_receive,                               # 닉네임
        "usercategory": usercategory_receive                        # 유저 유형
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# 아이디 중복 확인-----------------------------------------

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})








# 상품 등록 페이지로 이동 + 닉네임 불러옴-----------------------------------------
@app.route('/product')
def nick_get():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('product.html', user_info=user_info)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))



# 상품 상세 페이지로 이동 + 닉네임 불러옴-----------------------------------------
@app.route('/detail/<num>')
def detail(num):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('detail.html', user_info=user_info,user_category=user_info["usercategory"])

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))




# 상품 상세 페이지로 이동-----------------------------------------
@app.route('/detail/<num>', methods=["POST"])
def review():
    review_comment_receive = request.form["review_comment_give"],
    grade_receive = request.form["grade_give"],
    nick_receive = request.form["nickname_give"]
    doc = {
        "review_comment":review_comment_receive,
        "grade":grade_receive,
        "nickname":nick_receive
    }
    db.review.insert_one(doc)

    return jsonify({'msg': '주문 완료!'})


@app.route('/detail/<num>', methods=["GET"])
def review_get(num):
    review_list = list(db.review.find({}, {'_id': False}))
    return jsonify({'review':review_list})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)