from django.shortcuts import render, HttpResponse, redirect, render_to_response
import json
import pymysql
from li.models import UserInfo
from django.shortcuts import get_object_or_404
# Create your views here.


def index(request):
    # 1.获取数据库中所有的信息
    data_list = UserInfo.objects.all()
    return render(request, 'index.html', {"data_list": data_list})


def chartjs(request):
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

    return render(request, 'chartjs.html', {"female": female, "male": male, "graph": result1, "rawData": result2})


def buttons(request):
    return render(request, 'buttons.html')


def dropdowns(request):
    smoke = []
    num = []
    # 使用pymysql打开数据库连接
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        db='django',
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
    return render(request, 'dropdowns.html', {"num": num, "smoke": smoke})


def typography(request):
    return render(request, 'typography.html')


def basic_elements(request):
    return render(request, 'basic_elements.html')


def basic_table(request):
    return render(request, 'basic-table.html')


def mdi(request):
    return render(request, 'mdi.html')


def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    else:
        # 从前端表单中获取输入的数据，即账号和密码
        user = request.POST.get("user", None)
        pwd = request.POST.get("pwd", None)
        # 获取数据库中的账号密码数据
        test = UserInfo.objects.values("user", "pwd").filter(user=user)
        # 判断根据账号筛选前端输入的数据是否存在于数据库中
        if test.count() == 0:
            return render(request, "login.html", {"msg": "登录失败,账号不存在"})
        else:
            if test[0]['pwd'] == pwd:
                return redirect("http://127.0.0.1:8080/index")
            else:
                return render(request, "login.html", {'msg': '登陆失败,密码错误'})
    # # 连接数据库
    # conn = pymysql.connect(
    #     host='localhost',
    #     port=3306,
    #     user='root',
    #     password='PASSWORD',
    #     charset='utf8',
    #     db='django'
    # )
    # cur = conn.cursor()
    # sql = 'select * from li_userinfo'
    # cur.execute(sql)
    # data = cur.fetchall()
    # # print(data)
    # user = []
    # pwd = []
    # for item in data:
    #     # print(item)
    #     user.append(item[1])
    #     pwd.append(item[4])
    # # print(username1, password1)
    # cur.close()
    # conn.close()
    # return render(request, 'login.html', {"user": user, "pwd": pwd})


def register(request):
    if request.method == "GET":
        return render(request, 'register.html')
    # 获取用户提交的数据
    user = request.POST.get("user")
    email = request.POST.get("email")
    age = request.POST.get("age")
    pwd = request.POST.get("pwd")
    return redirect("http://127.0.0.1:8080/index")


def documentation(request):
    return render(request, 'documentation.html')


def info_delete(request):
    nid = request.GET.get('nid')
    UserInfo.objects.filter(id=nid).delete()
    return redirect("http://127.0.0.1:8080/index")


def draft(request):
    data_list = UserInfo.objects.all()
    return render(request, 'draft.html', {"data_list": data_list})


def page_not_found(request, **kwargs):
    # 全局404处理函数
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response
