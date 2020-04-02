import re

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

@route("/index.py")
def index():
    # return "这是主页"
    with open("./templates/index.html", encoding="utf-8") as f:  # python程序以运行web_server.py的路径为当前路径，而不是这个文件的路径，所以不用"../templates/index.html"
        content = f.read()
        # print(content)
    return content

@route("/center.py")
def center():
    return "这是中心页面"

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