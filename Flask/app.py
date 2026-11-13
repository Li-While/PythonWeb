from IPython.display import Image
import stylecloud
from flask import Flask, render_template, request, redirect
import pymysql
# from gevent import pywsgi
import json
# from livereload import Server

app = Flask(__name__)


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/chartjs')
def chartjs():
    import pymysql
    # 连接数据库
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='PASSWORD',
        charset='utf8',
        db='cardio'
    )
    cur1 = conn.cursor()
    sql1 = '''select * from cardio_train where gender=1'''
    cur1.execute(sql1)
    data1 = cur1.fetchall()
    female = []
    for item in data1:
        female.append([item[3], item[4]])

    cur2 = conn.cursor()
    sql2 = '''select * from cardio_train where gender=2'''
    cur2.execute(sql2)
    data2 = cur2.fetchall()
    male = []
    for item in data2:
        male.append([item[3], item[4]])

    cur1.close()
    cur2.close()
    conn.close()
    with open('les-miserables.json') as a:
        result1 = json.load(a)

    with open('stock-DJI.json') as c:
        result2 = json.load(c)

    return render_template('chartjs.html', female=female, male=male, graph=result1, rawData=result2)


@app.route('/buttons')
def buttons():
    return render_template('buttons.html')


@app.route('/dropdowns')
def dropdowns():
    smoke = []
    num = []
    # 使用pymysql打开数据库连接
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        db='cardio',
        user='root',
        password='PASSWORD',
        charset='utf8')
    # 查询数据的sql
    sql = '''select smoke,count(smoke) from cardio_train group by smoke'''
    # 打开数据库游标
    cur = conn.cursor()
    # 执行查询
    cur.execute(sql)
    # 拉取数据
    data = cur.fetchall()
    for item in data:
        num.append(item[0])
        smoke.append(item[1])
    # 关闭游标
    cur.close()
    # 关闭数据库连接
    conn.close()
    return render_template('dropdowns.html', num=num, smoke=smoke)


@app.route('/typography')
def typography():
    return render_template('typography.html')


@app.route('/basic_elements')
def basic_elements():

    return render_template('basic_elements.html')


@app.route('/basic-table')
def basic_table():
    return render_template('basic-table.html')


@app.route('/mdi')
def mdi():
    return render_template('mdi.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    import pymysql
    # 连接数据库
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='PASSWORD',
        charset='utf8',
        db='myproduct'
    )
    cur = conn.cursor()
    sql = 'select * from login'
    cur.execute(sql)
    data = cur.fetchall()
    # print(data)
    username1 = []
    password1 = []
    for item in data:
        # print(item)
        username1.append(item[0])
        password1.append(item[1])
    print(username1, password1)
    cur.close()
    conn.close()
    return render_template('login.html', username1=username1, password1=password1)
    # request 对象可以拿到浏览器传给服务器的所有数据
    # username = request.form.get('username')
    # password = request.form.get('password')

    # 点击登录按钮之后，链接数据库，校验账号密码
    # print("从浏览器接收到的数据", username, password)
    # return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/documentation')
def documentation():
    return render_template('documentation.html')


@app.errorhandler(404)  # 传入错误码作为参数状态
def error_404(error):  # 接受错误作为参数
    # 返回对应的http状态码，和返回404错误的html文件
    return render_template("error-404.html"), 404


@app.errorhandler(500)  # 传入错误码作为参数状态
def error_500(error):  # 接受错误作为参数
    # 返回对应的http状态码，和返回500错误的html文件
    return render_template("error-500.html"), 500


# print('username:', username)
# print('password:', password)


# # 解决浏览器浏览器访问输出乱码问题
# app.config['JSON_AS_ASCII'] = False


# @app.after_request
# def after(resp):
#     resp = make_response(resp)
#     resp.headers['Access-Control-Allow-Origin'] = '*'  # 允许跨域地址
#     resp.headers['Access-Control-Allow-Methods'] = '*'  # 请求 ‘*’ 就是全部
#     # 头部
#     resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
#     resp.headers['Access-Control-Allow-Credentials'] = 'True'
#     return resp


# CORS(app, resources=r'/*', supports_credentials=True)


if __name__ == "__main__":
    # app.debug = True
    # live_server = Server(app.wsgi_app)
    # live_server.serve(port=5000)
    app.run(debug=True)
    # app.run(debug=True, host='127.0.0.1', port=5000)
    # server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    # server.serve_forever()
