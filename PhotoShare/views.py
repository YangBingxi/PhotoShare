# -*-encoding=utf8-*-
import hashlib
import json
import os
import random
import sys
import uuid

from flask import render_template, redirect, request, flash, get_flashed_messages, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required

from PhotoShare import app, db  # 导入app
from PhotoShare.models import Image, User, Comment
from PhotoShare.qiniusdk import qiniu_upload_file

# 解决用户名中文输入的问题
reload(sys)
sys.setdefaultencoding('utf-8')


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
    # return render_template('index.html', images=images)
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=1, per_page=3, error_out=False)  # 分页，每页三张图片
    return render_template('index.html', images=paginate.items, has_next=paginate.has_next)


'''
网站主页分页
'''


@app.route('/index/images/<int:page>/<int:per_page>/')
def index_images(page, per_page):
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=page, per_page=per_page, error_out=False)
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        comments = []
        for i in range(0, min(2, len(image.comments))):
            comment = image.comments[i]
            comments.append({'username': comment.user.username,
                             'user_id': comment.user_id,
                             'content': comment.content})
        imgvo = {'id': image.id,
                 'url': image.url,
                 'comment_count': len(image.comments),
                 'user_id': image.user_id,
                 'username': image.user.username,
                 'head_url': image.user.head_url,
                 'created_date': str(image.create_date),
                 'comments': comments}
        images.append(imgvo)

    map['images'] = images
    return json.dumps(map)


'''
Not Found 页面
'''


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


'''
注册页面
'''


@app.route("/register")
def register(msg=''):
    for m in get_flashed_messages(with_categories=False, category_filter=['login']):
        msg += msg
    return render_template('login.html', msg=msg, next=request.values.get('next'))  # 已登录的话，就跳到首页


'''
登录页面
'''


@app.route("/login", methods={'post', 'get'})
def login():
    username = str(request.values.get('username')).strip()  # 从前端获取用户名
    password = str(request.values.get('password')).strip()  # 从前端获取密码
    if username == '' or password == '':  # 检测用户名或密码是否为空
        return redirect_with_msg('register', u"用户名或密码不能为空", "login")

    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect_with_msg("/register", u"用户或密码不正确", "login")

    m = hashlib.md5()  # 将用户登录时提交的密码进行md5
    m.update(password.encode('utf-8') + user.salt.encode('utf-8'))
    if m.hexdigest() != user.password:
        return redirect_with_msg("/register", u"用户或密码不正确", "login")

    login_user(user)

    '''
    next功能的跳转
    '''
    next = request.values.get('next')
    if next != None and next.startswith('/') > 0:
        return redirect(next)
    return redirect("/")


@app.route("/reg", methods={'post', 'get'})
def reg():
    username = str(request.values.get('username'.encode('utf-8'))).strip()  # 从前端获取用户名
    password = str(request.values.get('password')).strip()  # 从前端获取密码
    '''
    检查注册用户字段是否合法
    '''
    if username == '' or password == '':
        return redirect_with_msg('/register', "用户名或密码不能为空", "login")
    '''
    检查注册用户是否已存在
    '''
    user = User.query.filter_by(username=username).first()
    if user != None:
        return redirect_with_msg('/register', "用户已存在", "login")

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

    '''
    next功能的跳转
    '''
    next = request.values.get('next')
    if next != None and next.startswith('/') > 0:
        return redirect(next)

    return redirect('/')


'''
用户登出函数
'''


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/image/<int:image_id>/')
@login_required  # 添加访问权限，登录用户才可以访问
def image(image_id):
    image = Image.query.get(image_id)
    if image == None:
        return redirect('/')
    comments = Comment.query.filter_by(image_id=image_id).order_by(db.desc(Comment.id)).limit(20).all()
    return render_template('pageDetail.html', image=image, comments=comments)


@app.route('/profile/<int:user_id>/')
@login_required  # 添加访问权限，登录用户才可以访问
def profile(user_id):
    user = User.query.get(user_id)
    if user is None:
        return redirect('/error')
    paginate = Image.query.filter_by(user_id=user_id).order_by(db.desc(Image.id)).paginate(page=1, per_page=3,
                                                                                           error_out=False)
    print(user.id)
    return render_template('profile.html', user=user, images=paginate.items, has_next=paginate.has_next)


@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page,
                                                               error_out=False)  # 分页，每页三张图片
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id': image.id, 'url': image.url, 'comment_count': len(image.comments)}
        images.append(imgvo)
    map['images'] = images
    return json.dumps(map)


'''
添加评论
'''


@app.route('/addcomment/', methods={'post'})
@login_required
def add_comment():
    image_id = int(request.values['image_id'])
    content = request.values['content']
    comment = Comment(content, image_id, current_user.id)
    db.session.add(comment)
    db.session.commit()
    return json.dumps({"code": 0, "id": comment.id,
                       "content": comment.content,
                       "username": comment.user.username,
                       "user_id": comment.user_id})


@app.route('/image/<image_name>')
def view_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)


def save_to_qiniu(file, file_name):
    return qiniu_upload_file(file, file_name)


def save_to_local(file, file_name):
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir, file_name))
    return '/image/' + file_name


@app.route('/upload/', methods={'post'})
@login_required
def upload():
    file = request.files['file']
    file_ext = ''
    if file.filename.find('.') > 0:
        file_ext = file.filename.rsplit('.', 1)[1].strip().lower()
    if file_ext in app.config['ALLOWED_EXT']:
        file_name = str(uuid.uuid1()).replace('-', '') + '.' + file_ext
        url = qiniu_upload_file(file, file_name)

        # url = save_to_local(file, file_name)
        if url != None:
            db.session.add(Image(url, current_user.id))
            db.session.commit()

    return redirect('/profile/%d' % current_user.id)
