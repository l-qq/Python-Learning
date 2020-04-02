import re


def index():
    # return "这是主页"
    with open("./templates/index.html", encoding="utf-8") as f:  # python程序以运行web_server.py的路径为当前路径，而不是这个文件的路径，所以不用"../templates/index.html"
        content = f.read()
        # print(content)
    return content

def center():
    return "这是中心页面"

URL_FUNC_DICT = {
    "/index.py": index,
    "/center.py": center
}

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
    func = URL_FUNC_DICT[file_name]
    return func()