`PythonWeb/Flask` 和`PythonWeb/Django`是同一套页面。

主要差异：
| 配置 | Django 版 | Flask 版 |
| --- | --- | --- |
| 路由 | `Liwhale/urls.py` 配置 |  `@app.route` 装饰器配置 |
| 数据层 | `models.py` + Django ORM | 通过`pymysql` 写 SQL |
| 静态路径 | 模板用 `{% static %}` | 模板用 `../static/` |
| 后台 | 有 `admin.py`，自带 Admin | 无 |
| 启动端口 | 8080 | 5000 |
