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
# @route("/index.html")
@route("/index\.html")
def index(ret):
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
            <td><input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="%s"></td>
        </tr>
    """
    html = ""
    for line_info in stock_infos:
        html += tr_template % (line_info[0], line_info[1], line_info[2], line_info[3], line_info[4], line_info[5], line_info[6], line_info[7], line_info[1])
    # content = re.sub(r"\{%content%\}", str(stock_infos), content)
    content = re.sub(r"\{%content%\}", html, content)
    return content

# @route("/center.py")
# @route("/center.html")
@route("/center\.html")
def center(ret):
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
            <td>
                <a type="button" class="btn btn-default btn-xs" href="/update/%s.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
            </td>
            <td>
                <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="%s">
            </td>
        </tr>
    """
    html = ""
    for line_info in stock_infos:
        html += tr_template % (line_info[0], line_info[1], line_info[2], line_info[3], line_info[4], line_info[5], line_info[6], line_info[0], line_info[0])
    content = re.sub(r"\{%content%\}", html, content)
    return content

# 采用正则，可以编写一次route匹配多个url，对应同一个调用函数
@route(r"/add/(\d+)\.html")
def add_focus(ret):
    # 1. 获取股票代码
    stock_code = ret.group(1)
    # 2. 判断是否存在该代码
    conn = connect(host="localhost", port=3306, user="root", password="", database="stock_db", charset="utf8")
    cs = conn.cursor()
    sql = "select * from info where code=%s;"
    cs.execute(sql, (stock_code,))  # 防止SQL注入
    if not cs.fetchone():
        cs.close()
        conn.close()
        return "没有这支股票"
    # 3. 判断是否已经关注过
    sql = "select * from info as i inner join focus as f on i.id=f.info_id where i.code=%s;"
    cs.execute(sql, (stock_code,))
    if cs.fetchone():
        cs.close()
        conn.close()
        return "已经关注过了，请勿重复"
    # 4. 添加关注
    sql = "insert into focus(info_id) select id from info where code=%s;"
    cs.execute(sql, (stock_code,))
    conn.commit()
    cs.close()
    conn.close()
    # return "add (%s) ok ......" % stock_code
    return "关注成功"

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
        for url, func in URL_FUNC_DICT.items():
            # {
            #     r"/index\.html": index,
            #     r"/center\.html": center,
            #     r"/add/\d+\.html": add_focus
            # }
            ret = re.match(url, file_name)
            if ret:
                return func(ret)
        else:
            return "请求的url(%s)没有对应的函数。。。" % file_name
    except Exception as ret:
        return "产生了异常：%s" % str(ret)