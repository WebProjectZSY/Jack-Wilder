#coding:utf8
from flask.ext.sqlalchemy import SQLAlchemy
from flask import session
from flask import request
from flask import Flask
from flask.ext.session import Session
from flask import render_template, request, redirect, abort, jsonify, json, url_for, session
import time, datetime
import hashlib
import re


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SESSION_TYPE'] = "filesystem"
app.config['SESSION_FILE_DIR'] = "/tmp/flask_session"
app.config['PERMANENT_SESSION_LIFETIME'] = 604800
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key="94e68353e3a9da218d4240eb11e201da"
Session(app)

def format_datetime(value):
    return value.strftime("%Y-%m-%d %H:%M")

app.jinja_env.filters['datetime'] = format_datetime

def sha512(string):
    return str(hashlib.sha512(str(string)).hexdigest())

db = SQLAlchemy()
db.init_app(app)

class Users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    email = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(512))
    money = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = sha512(str(password))
        self.money = 10000
        self.date = datetime.datetime.now()

class Goods(db.Model):
    __tablename__ = 'Goods'
    id = db.Column(db.Integer, primary_key=True)
    good_name = db.Column(db.String(128))
    good_price = db.Column(db.Integer)
    good_img_path = db.Column(db.String(4096), unique=True)
    good_desc = db.Column(db.String(4096), unique=True)
    date = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, good_name, good_price, good_img_path, good_desc):
        self.good_name = good_name
        self.good_price = good_price
        self.good_img_path = good_img_path
        self.good_desc = good_desc
        self.date = datetime.datetime.now()

class Shopcar(db.Model):
    __tablename__ = 'Shopcar'
    id = db.Column(db.Integer, primary_key=True)
    good_id = db.Column(db.Integer, db.ForeignKey('Goods.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, good_id, user_id):
        self.good_id = good_id
        self.user_id = user_id
        self.date = datetime.datetime.now()

class PurchasedGoods(db.Model):
    __tablename__ = 'PurchasedGoods'
    id = db.Column(db.Integer, primary_key=True)
    good_id = db.Column(db.Integer, db.ForeignKey('Goods.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, good_id, user_id):
        self.good_id = good_id
        self.user_id = user_id
        self.date = datetime.datetime.now()

class Configs(db.Model):
    __tablename__ = "Configs"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(4096))
    value = db.Column(db.String(4096))

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.date = datetime.datetime.now()



def is_logined():
    return bool(session.get('id', False))

def check_email_format(email):
    return bool(re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        info=''
        return render_template('login.html', info=info)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password = sha512(password)
        print password

        user = Users.query.filter_by(username=username, password=password).first()

        if not user:
            info = "Username or Password Wrong!"
            return render_template('login.html', info=info)

        session['id'] = user.id
        session['username'] = user.username
        return redirect('/index')

@app.route("/index", methods=['GET'])
@app.route("/", methods=['GET'])
def index():
    goods = Goods.query.all()
    goods = goods

    user_logined = False
    if is_logined():
        user_logined = True
        user_id = session['id']
        user = Users.query.filter_by(id=user_id).first()
        username = user.username
        shopcarnum = Shopcar.query.filter_by(user_id=user_id).count()
        return render_template('index.html', goods=goods, user_logined=user_logined, username=username, shopcar_num=shopcarnum)

    return render_template('index.html', goods=goods, user_logined=user_logined)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        errors = []
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        username_long = len(username) > 9
        username_short = len(password) < 2
        username_duplicate = Users.query.filter_by(username=username).first()
        email_duplicate = Users.query.filter_by(email=email).first()
        pass_short = len(password) < 6
        pass_long = len(password) > 15
        valid_email = check_email_format(email)

        if not valid_email:
            errors.append("邮箱格式不对的".decode('utf-8'))
        if username_duplicate:
            errors.append('这个名字已经有人用了'.decode('utf-8'))
        if email_duplicate:
            errors.append('这个邮箱有人注册过了'.decode('utf-8'))
        if pass_short:
            errors.append('密码太短了至少六位'.decode('utf-8'))
        if pass_long:
            errors.append('密码太长了最多十八位'.decode('utf-8'))
        if username_long:
            errors.append('名字太长啦'.decode('utf-8'))
        if username_short:
            errors.append('名字太短了'.decode('utf-8'))

        if len(errors) > 0:
            return render_template('register.html', errors=errors, username=request.form['username'], email=request.form['email'], password=request.form['password'])
        else:
            user = Users(username, email.lower(), password)
            db.session.add(user)
            db.session.commit()
            db.session.flush()

            session['username'] = user.username
            session['id'] = user.id

            db.session.close()
        return redirect('/index')

    else:
        return render_template('register.html')


@app.route("/shopcar", methods=['GET'])
def shopcar():
    if not is_logined():
        return redirect('/index')

    user_id = session['id']
    user = Users.query.filter_by(id=user_id).first()
    username = user.username
    user_money = user.money

    if request.method == "GET":
        goods_in_shopcar = db.session.query(Goods.id, Goods.good_name, Goods.good_price, Shopcar.date).join(Shopcar).filter(Shopcar.user_id == user_id).all()
        return render_template('shopcar.html', username=username, goods_in_shopcar=goods_in_shopcar)


@app.route("/pay", methods=['POST'])
def pay():
        if not is_logined():
            return redirect('/index')

        user_id = session['id']
        user = Users.query.filter_by(id=user_id).first()
        username = user.username
        user_money = user.money
        password = request.form['password']

        if sha512(password) != user.password:
            info = "密码错误".decode('utf-8')
            return render_template('payinfo.html', info)

        goods_in_shopcar = Goods.query.join(Shopcar).filter(Shopcar.user_id == user_id).all()

        total_price = 0
        for good in goods_in_shopcar:
            total_price += int(good.good_price)

        if total_price > user_money:
            info = "余额不足".decode('utf-8')
            return render_template('payinfo.html', info)

        for good in goods_in_shopcar:
            Shopcar.query.filter_by(good_id=good.id).delete()
            purchased_good = PurchasedGoods(good.id, user_id)
            db.session.add(purchased_good)
            db.session.commit()

        user.money = user_money - total_price
        db.session.commit()
        db.session.close()

        info = "支付成功".decode('utf-8')
        return render_template('payinfo.html', info=info)


@app.route("/addshopcar", methods=['POST'])
def addshopcar():
    if not is_logined():
        return redirect('/index')

    user_id = session['id']
    good_id = request.form['good_id']
    good_id = int(good_id)
    add_good = Shopcar(good_id, user_id)
    db.session.add(add_good)
    db.session.commit()
    db.session.close()
    return render_template('add_success.html', good_id=good_id)

@app.route("/good/<int:id>", methods=['GET'])
def good(id):
    user_logined = False
    username = ''
    shopcarnum = 0
    if is_logined():
        user_logined = True
        user_id = session['id']
        user = Users.query.filter_by(id=user_id).first()
        username = user.username
        shopcarnum = Shopcar.query.filter_by(user_id=user_id).count()

    good = Goods.query.filter_by(id = id).first()
    return render_template("good.html", good=good, user_logined=user_logined, username=username, shopcar_num=shopcarnum)
@app.route("/logout")
def logout():
    if is_logined():
        session.clear()
    return redirect('/index')
@app.route("/profile")
def profile():
    user_logined = False
    if is_logined():
        user_logined = True
        user_id = session['id']
        user = Users.query.filter_by(id=user_id).first()
        balance = user.money
        username = user.username
        purchased_goods = db.session.query(Goods.id, Goods.good_name, Goods.good_price, PurchasedGoods.date).join(PurchasedGoods).filter(PurchasedGoods.user_id == user_id).all()
        num = len(purchased_goods)
        return render_template('profile.html', purchased_goods=purchased_goods, num=num, balance=balance)
    else:
        return redirect('/index')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
