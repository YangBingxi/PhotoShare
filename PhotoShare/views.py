# -*-encoding=utf8-*-
import hashlib
import random

from flask import render_template, redirect, request, flash, get_flashed_messages

from PhotoShare.app import app, db  # 导入app
from PhotoShare.models import Image, User
from flask_login import login_user, logout_user, current_user, login_required


def redirect_with_msg(target, msg, category):
    if msg is not None:
        flash(msg, category=category)
    return redirect(target)


'''
网站主页
'''


@app.route("/")
def index():
    images = Image.query.order_by(db.desc(Image.id)).limit(10).all()
    return render_template('index.html', images=images)


'''
Not Found 页面
'''


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


'''
登录注册页面
'''


@app.route("/login")
def login():
    msg = ''
    for m in get_flashed_messages(with_categories=False, category_filter=['login']):
        msg += msg
    return render_template('login.html', msg=msg)


@app.route("/reg", methods={'post', 'get'})
def reg():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    '''
    检查注册用户字段是否合法
    '''
    if username == '' or password == '':
        return redirect_with_msg('/login', "用户名或密码不能为空", "login")
    '''
    检查注册用户是否已存在
    '''
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return redirect_with_msg('/login', "用户已存在", "login")

    '''
    注册用户
    '''
    # 生成盐字段
    salt = '.'.join(random.sample("0123456789"
                                  "abcdefghijklmnopqrstuvwxyz"
                                  "ABCDEFGHIJKLMNOPQRSTUVWXYZ", 10))

    m = hashlib.md5()
    m.update(password.encode('utf-8') + salt.encode('utf-8'))
    password = m.hexdigest()
    user = User(username, password, salt)  # 创建用户
    db.session.add(user)  # 添加用户
    db.session.commit()  # 提交到数据库

    login_user(user)  # 注册完后自动登录

    return redirect('/')


'''
用户登出函数
'''


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/image/<int:image_id>/')
def image(image_id):
    img = Image.query.get(image_id)
    if img is None:
        return redirect('/error')
    return render_template('pageDetail.html', image=img)


@app.route('/profile/<int:user_id>/')
@login_required  # 添加访问权限，登录用户才可以访问
def profile(user_id):
    user = User.query.get(user_id)
    if user is None:
        return redirect('/error')
    return render_template('profile.html', user=user)
