import socket
import multiprocessing
import re

def service_client(new_socket):
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
    try:
        f = open("./html" + file_name, "rb")
    except:
        response = "HTTP/1.1 404 NOT FOUND\r\n"
        response += "\r\n"
        response += "------file not found------"
        new_socket.send(response.encode("utf-8"))
    else:
        html_content = f.read()
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
    # 3. 关闭套接字
    new_socket.close()

def main():
    """用来完成整体的流程控制"""
    # 1. 创建套接字
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 端口和IP重用，即使服务器挂掉后，也不会因为四次挥手导致服务器资源不释放，从而不能立马再次运行
    # 2. 绑定
    tcp_server_socket.bind(("", 8080))
    # 3. 监听
    tcp_server_socket.listen(128)
    while True:
        # 4. 等待客户端的链接
        new_socket, client_addr = tcp_server_socket.accept()
        # 5. 为这个客户端服务
        p = multiprocessing.Process(target=service_client, args=(new_socket,))
        p.start()

        new_socket.close()  # 关闭主进程对文件描述符的引用，因为是多进程实现，子进程复制一份主进程的资源，所以主进程和子进程的new_socket都会引用同一个资源
    # 关闭监听套接字
    tcp_server_socket.close()

if __name__ == "__main__":
    main()