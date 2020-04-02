# 11

Mini-Web 框架使用字典实现路由，根据不同的页面请求调用不同的函数

## 使用说明

- 运行：`./run.bat` 或者 `python3 web_server.py 8080 mini_frame:application`

## 文件说明

``` powershell
│  web_server.conf  # 服务器读取的配置文件
│  web_server.py  # Python 实现的简易 Web 服务器
│
├─dynamic  # 存放所有的框架文件
│  └─  mini_frame.py  # Python 实现的简易 Mini-Web 框架
│
├─static  # 存放所有的静态 Web 资源
│  ├─css
│  │      1.css
│  │
│  └─js
└─templates  # 存放框架要使用的模板页面
        index.html
```
