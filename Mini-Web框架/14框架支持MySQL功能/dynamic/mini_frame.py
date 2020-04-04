import re
from pymysql import connect

URL_FUNC_DICT = dict()
# func_list = list()

# 使用带参数的装饰器
def route(url):
    def set_func(func):
        # func_list.append(func)
        URL_FUNC_DICT[url] = func  # URL_FUNC_DICT["/index.py"] = index
        def call_func(*args, **kwargs):
            return func(*args, **kwargs)
        return call_func
    return set_func

# @route("/index.py")
@route("/index.html")
def index():
    # return "这是主页"
    with open("./templates/index.html", encoding="utf-8") as f:  # python程序以运行web_server.py的路径为当前路径，而不是这个文件的路径，所以不用"../templates/index.html"
        content = f.read()
        # print(content)
    """
    my_stock_info = "哈哈，这是数据库的数据"
    content = re.sub(r"\{%content%\}", my_stock_info, content)
    """
    conn = connect(host="localhost", port=3306, user="root", password="", database="stock_db", charset="utf8")
    cs = conn.cursor()
    cs.execute("select * from info;")
    stock_infos = cs.fetchall()  # 返回为元组
    cs.close()
    conn.close()

    tr_template = """
        <tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>添加自选</td>
        </tr>
    """
    html = ""
    for line_info in stock_infos:
        html += tr_template % (line_info[0], line_info[1], line_info[2], line_info[3], line_info[4], line_info[5], line_info[6], line_info[7])
    # content = re.sub(r"\{%content%\}", str(stock_infos), content)
    content = re.sub(r"\{%content%\}", html, content)
    return content

# @route("/center.py")
@route("/center.html")
def center():
    # return "这是中心页面"
    with open("./templates/center.html", encoding="utf-8") as f:  # python程序以运行web_server.py的路径为当前路径，而不是这个文件的路径，所以不用"../templates/index.html"
        content = f.read()
        # print(content)

    conn = connect(host="localhost", port=3306, user="root", password="", database="stock_db", charset="utf8")
    cs = conn.cursor()
    cs.execute("select i.code,i.short,i.chg,i.turnover,i.price,i.highs,f.note_info from info as i inner join focus as f on i.id=f.info_id;")
    stock_infos = cs.fetchall()  # 返回为元组
    cs.close()
    conn.close()

    tr_template = """
        <tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>修改</td>
            <td>删除</td>
        </tr>
    """
    html = ""
    for line_info in stock_infos:
        html += tr_template % (line_info[0], line_info[1], line_info[2], line_info[3], line_info[4], line_info[5], line_info[6])
    content = re.sub(r"\{%content%\}", html, content)
    return content

def application(env, start_response):
    # start_response('200 OK', [('Content-Type', 'text/html;charset=gbk')])
    start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
    file_name = env['PATH_INFO']
    # file_name = "/index.py"
    """
    if file_name == "/index.py":
        return index()
    elif file_name == "/login.py":
        return login()
    else:
        return "hello world!哈哈哈"
    """

    try:
        func = URL_FUNC_DICT[file_name]  # 模块只要一导入。装饰器就装饰，字典就填充
        return func()
    except Exception as ret:
        return "产生了异常：%s" % str(ret)