from PhotoShare import app  # 导入app


@app.app.route("/")  # 网站主页
def index():
    return "hello"
