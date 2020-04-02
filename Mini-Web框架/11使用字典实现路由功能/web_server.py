import socket
import multiprocessing
import re
import time
# import dynamic.mini_frame
import sys

class WSGIServer(object):
    def __init__(self, port, app, static_path):
        # 1. 创建套接字
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 端口和IP重用，即使服务器挂掉后，也不会因为四次挥手导致服务器资源不释放，从而不能立马再次运行
        # 2. 绑定
        self.tcp_server_socket.bind(("", port))
        # 3. 监听
        self.tcp_server_socket.listen(128)

        self.application = app
        self.static_path = static_path

    def service_client(self, new_socket):
        """为这个客户端返回数据"""
        # 1. 接收浏览器发送过来的HTTP请求
        # GET / HTTP/1.1
        request = new_socket.recv(1024).decode("utf-8")
        request_lines = request.splitlines()
        print("")
        print(">"*20)
        print(request_lines)
        # GET /index.html HTTP/1.1
        file_name = ""
        ret = re.match(r"[^/]+(/[^ ]*)", request_lines[0])
        if ret:
            file_name = ret.group(1)
            if file_name == "/":
                file_name = "/index.html"
        # 2. 返回HTTP格式的数据给浏览器
        # 如果请求的资源不是以.py结尾，那么就认为是静态资源
        if not file_name.endswith(".py"):
            try:
                f = open(self.static_path + file_name, "rb")
            except:
                response = "HTTP/1.1 404 NOT FOUND\r\n"
                response += "\r\n"
                response += "------file not found------"
                new_socket.send(response.encode("utf-8"))
            else:
                html_content = f.read()
                print(html_content)
                f.close()
                # 2.1 准备发送给浏览器的数据---header
                response = "HTTP/1.1 200 OK\r\n"
                response += "\r\n"
                # 2.1 准备发送给浏览器的数据---body
                # response += "hahahah"

                # 将response header发送给浏览器
                new_socket.send(response.encode("utf-8"))
                # 将response body发送给浏览器
                new_socket.send(html_content)
        else:
            # 如果请求的资源以.py结尾，那么就认为是动态资源
            
            # body = "haha %s" % time.ctime()
            # if file_name == "/login.py":
            #     body = mini_frame.login()
            # elif file_name == "/register.py":
            #     body = mini_frame.register()
            env = dict()
            env['PATH_INFO'] = file_name
            # body = dynamic.mini_frame.application(env, self.set_response_header)
            body = self.application(env, self.set_response_header)
            
            header = "HTTP/1.1 %s\r\n" % self.status
            for temp in self.headers:
                header += "%s:%s\r\n" % (temp[0], temp[1])
            header += "\r\n"

            response = header + body
            new_socket.send(response.encode("utf-8"))

        # 3. 关闭套接字
        new_socket.close()

    def set_response_header(self, status, headers):
        self.status = status
        self.headers = [("server", "mini_web v8.8")]
        self.headers += headers

    def run_forever(self):
        """用来完成整体的流程控制"""
        while True:
            # 4. 等待客户端的链接
            new_socket, client_addr = self.tcp_server_socket.accept()
            # 5. 为这个客户端服务
            p = multiprocessing.Process(target=self.service_client, args=(new_socket,))
            p.start()

            new_socket.close()  # 关闭主进程对文件描述符的引用，因为是多进程实现，子进程复制一份主进程的资源，所以主进程和子进程的new_socket都会引用同一个资源
        # 关闭监听套接字
        self.tcp_server_socket.close()

def main():
    """控制整体，创建一个web服务器对象，然后调用这个对象的run_forever方法运行"""
    if len(sys.argv) == 3:
        try:
            port = int(sys.argv[1])
            frame_app_name = sys.argv[2]
        except Exception as ret:
            print("端口输入错误。。。")
            return
    else:
        print("请按照以下方式运行：")
        print("python3 xxx.py 8080 mini_frame:application")
        return

    # mini_frame:application
    ret = re.match(r"([^:]+):(.*)", frame_app_name)
    if ret:
        frame_name = ret.group(1)
        app_name = ret.group(2)
    else:
        print("请按照以下方式运行：")
        print("python3 xxx.py 8080 mini_frame:application")
        return

    # import frame_name --->此时找frame_name.py，不正确，不能这么用
    with open("./web_server.conf") as f:
        conf_info = eval(f.read())  # 字符串转为字典

    sys.path.append(conf_info["dynamic_path"])
    frame = __import__(frame_name)  # 返回值标记着导入的模块
    app = getattr(frame, app_name)  # 返回值指向模块中的函数app_name即application

    wsgi_server = WSGIServer(port, app, conf_info["static_path"])
    wsgi_server.run_forever()

if __name__ == "__main__":
    main()