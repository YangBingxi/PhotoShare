# -*-encoding=utf8-*-

'''from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config.from_pyfile("app.conf")  # 加载app的初始化文件
app.secret_key = 'sw'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # 配置登录界面，如：未登录用户访问限制页面，会调到设置页面
from PhotoShare import views, models


@app.route('/default')  # default页面
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
'''