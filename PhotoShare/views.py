from PhotoShare.app import app, db  # 导入app
from flask import render_template, redirect
from PhotoShare.models import Image, User

'''
网站主页
'''


@app.route("/")
def index():
    images = Image.query.order_by(db.desc(Image.id)).limit(10).all()
    return render_template('index.html', images=images)


@app.route('/image/<int:image_id>/')
def image(image_id):
    img = Image.query.get(image_id)
    if img is None:
        return redirect('/error')
    return render_template('pageDetail.html', image=img)


@app.route('/profile/<int:user_id>/')
def profile(user_id):
    user = User.query.get(user_id)
    if user is None:
        return redirect('/error')
    return render_template('profile.html', user=user)


'''
Not Found 页面
'''


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
