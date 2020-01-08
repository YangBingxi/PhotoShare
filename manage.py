from PhotoShare.app import app, db
from flask_script import Manager
from PhotoShare.models import User, Image, Comment
import random

manager = Manager(app)


def get_image_url():
    return 'https://raw.githubusercontent.com/youngsw/Head-Img/master/img/img' \
           + str(random.randint(0, 1000)) + \
           'sw.png'  # 在头像库中随机选取一个作为用户的头像


'''
数据库初始化函数
'''


@manager.command  # 只允许命令行执行该函数
def init_database():
    db.drop_all()
    db.create_all()
    for i in range(0, 100):
        db.session.add(User('User' + str(i+1), 'a'+str(i+1)))
        for j in range(0, 10):
            db.session.add(Image(get_image_url(), i+1))
            for k in range(0, 3):
                db.session.add(Comment('This is a comment' + str(k), 1+10*i+j, i+1))

    db.session.commit()  # 提交数据库的修改


'''    for i in range(50, 100, 2):
        user = User.query.get(i)
        user.username = '[New]' + user.username
    print(1, User.query.all())  # 获取全部信息
    print(1, Image.query.all())  # 获取全部信息
    print(2, User.query.get(3))  # 获取主键为3的用户信息'''

if __name__ == '__main__':
    manager.run()
