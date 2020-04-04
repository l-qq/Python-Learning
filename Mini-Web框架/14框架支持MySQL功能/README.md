# 14

框架支持数据库连接和查询，并动态返回数据

## 使用说明

- 安装 MySQL：`scoop install mysql`
- 启动服务端：`mysqld --standalone` or `mysqld --console`
- 客户端连接：`mysql -u rooy -p` 密码默认为空
- 创建数据库：`create database stock_db charset=utf8;`
- 导入数据：
  - 使用 stock_db：`use stock_db;`
  - 导入数据：`source stock_db.sql` （.sql 文件有误，直接复制到 cmd 执行即可，不能 `source`）
- 运行：`./run.bat` 或者 `python3 web_server.py 8080 mini_frame:application`

## 文件说明

``` powershell
│  web_server.conf  # 服务器读取的配置文件
│  web_server.py  # Python 实现的简易 Web 服务器
│  stock_db.sql  # 数据库执行语句
|
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
