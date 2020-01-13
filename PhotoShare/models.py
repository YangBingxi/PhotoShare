# -*-encoding=utf8-*-

from PhotoShare.app import db, login_manager
from datetime import datetime
import random

'''
用户类
基于ORM管理数据库
'''


class User(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}  # 设置表的编码格式为utf8
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 用户id：整形、主键、自增
    username = db.Column(db.String(80), unique=True)  # 用户名：字符串类型、唯一
    password = db.Column(db.String(32))  # 用户密码
    salt = db.Column(db.String(32))  # 用户密码salt
    head_url = db.Column(db.String(256))  # 用户头像url地址
    images = db.relationship('Image', backref='user', lazy='dynamic')

    '''
    类的构造函数
    '''

    def __init__(self, username, password, salt=''):
        self.username = username
        self.password = password
        self.salt = salt
        self.head_url = 'https://raw.githubusercontent.com/youngsw/Head-Img/master/headUrl2/HeadImg' \
                        + str(random.randint(1, 171)) + \
                        'sw.png'  # 在头像库中随机选取一个作为用户的头像

    '''
        打印函数
        '''

    def __repr__(self):
        return '<User %d %s>' % (self.id, self.username)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


'''
用户的登录管理
'''


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


''' 
图片类
'''


class Image(db.Model):
    # __table_args__ = {'mysql_collate': 'utf8_general_ci'}  # 设置表的编码格式为utf8
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 图片id：整形、主键、自增
    url = db.Column(db.String(512))  # 图片URL
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 图片关联的用户id，关联外键
    create_date = db.Column(db.DateTime)  # 图片创建时间
    comments = db.relationship('Comment')

    '''
    类的构造函数
    '''

    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id
        self.create_date = datetime.now()

    '''
        打印函数
        '''

    def __repr__(self):
        return '<Image %d %s>' % (self.id, self.url)


'''
评论类
'''


class Comment(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}  # 设置表的编码格式为utf8
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 评论id：整形、主键、自增
    content = db.Column(db.String(1024))  # 评论内容
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))  # 评论所关联的图片
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 评论所关联的用户
    status = db.Column(db.Integer, default=0)  # 评论的状态 0正常 1异常，默认值为0
    # create_date = db.Column(db.DateTime)  # 评论创建时间
    user = db.relationship('User')

    '''
    类的构造函数
    '''

    def __init__(self, content, image_id, user_id):
        self.content = content
        self.image_id = image_id
        self.user_id = user_id

    '''
    打印函数
    '''

    def __repr__(self):
        return '<Comment %d %s>' % (self.id, self.content)
