# 02

完成用户注册的相关逻辑代码

## 快速使用

``` powershell
python -m venv virtual_env  # 创建虚拟环境
.\virtual_env\Scripts\activate  # 激活虚拟环境
pip install django
pip install django-tinymce  # 富文本
pip install mysqlclient  # django使用mysqlclient，弃用pymysql
pip install Pillow
pip install itsdangerous  # 签名加密
scoop install redis  # 使用redis作为中间人/任务队列（broker）
redis-server.exe  # 启动redis服务端
pip install celery  # 异步处理，任务队列，加入/执行任务到redis
pip install redis  # 安装redis客户端
scoop install mysql
mysqld.exe --console
mysql -u root -p
create database dailyfresh charset=utf8;
cd .\dailyfresh
python .\manage.py migrate
python .\manage.py runserver
celery.exe -A celery_tasks.tasks worker --loglevel=info --pool solo  # windows下任务处理者开始监听队列
```

## 学习笔记

### 开发步骤

#### 导入静态文件

在项目的 `static` 目录中导入前端页面，页面说明如下

``` txt
1、index.html   网站首页，顶部“注册|登录”和用户信息是切换显示的，商品分类菜单点击直接链接滚动到本页面商品模块。首页已加入幻灯片效果。此效果在课程中已讲述如何制作。
2、list.html  商品列表页，商品分类菜单鼠标悬停时切换显示和隐藏，点击菜单后链接到对应商品的列表页。
3、detail.html  商品详情页，某一件商品的详细信息。
4、cart.html 我的购物车页，列出已放入购物车上的商品
5、place_order.html 提交订单页
6、login.html 登录页面
7、register.html 注册页面，已加入了初步的表单验证效果，此效果在课程中已讲述如何制作。
8、user_center_info.html 用户中心-用户信息页 用户中心功能一，查看用户的基本信息
9、user_center_order.html 用户中心-用户订单页 用户中心功能二，查看用户的全部订单
10、user_center_site.html 用户中心-用户收货地址页 用户中心功能三，查看和设置用户的收货地址
```

#### 运行测试

``` powershell
python .\manage.py runserver  # 运行服务
```

访问 <http://127.0.0.1:8000/static/register.html> 验证静态页面是否可以正常打开

``` powershell
mysql> select * from df_user \G;
```

#### 编写视图 ➕ 路由

##### 显示注册页面

1. 修改视图文件 `.\apps\user\views.py`，添加 `register()` 函数
2. 修改路由文件 `.\apps\user\urls.py`，添加匹配规则
3. 复制 `.\static\register.html` 到 `.\templates\register.html` 作为模板文件
4. 修改该模板文件，使用模板变量。用 `{% load static %}` 和 `href="{% static 'css/reset.css' %}"` 等

##### 注册提交功能

1. 修改该 `.\templates\register.html` 模板文件。用 `<form method="post" action="/user/register_handle">` 和 `{% csrf_token %}`
2. 修改视图文件 `.\apps\user\views.py`，添加 `register_handle()` 函数
3. 修改路由文件 `.\apps\user\urls.py`，添加匹配规则

##### 注册完毕，跳转首页

1. 复制 `.\static\index.html` 到 `.\templates\index.html` 作为模板文件
2. 修改视图文件 `.\apps\goods\views.py`，添加 `index()` 函数
3. 修改路由文件 `.\apps\goods\urls.py`，添加匹配规则

##### 优化精简

1. `register()` 函数和 `register_handle()` 函数合并，通过判断请求的类型（GET/POST）来执行不同的功能，从而共用一个路由规则
2. 使用 `类视图` 替换上述 `函数视图`
   1. 修改视图文件 `.\apps\user\views.py`，添加 `RegisterView` 类
   2. 修改路由文件 `.\apps\user\urls.py`，添加匹配规则，删除之前基于函数的路由规则，改为类视图

##### 实现邮箱激活功能

1. 虚拟环境安装 `pip install itsdangerous` （注意确保安装到了正确的虚拟环境中）
2. 修改视图文件 `.\apps\user\views.py`，修改 `RegisterView` 类中的 `post()` 方法，发送邮件
3. 修改视图文件 `.\apps\user\views.py`，添加 `ActiveView` 类，响应用户的激活 GET 请求
   1. 复制 `.\static\login.html` 到 `.\templates\login.html` 作为模板文件
   2. 修改视图文件 `.\apps\user\views.py`，添加 `LoginView` 类
   3. 修改路由文件 `.\apps\user\urls.py`，添加登录页面匹配规则
4. 修改路由文件 `.\apps\user\urls.py`，添加匹配用户激活的 URL 规则

##### 让 Django 使用免费的 SMTP 服务器代发邮件

1. 去 QQ 邮箱开通 POP3/SMTP 服务并获取授权码
2. 修改 `.\dailyfresh\settings.py`

   ``` python
   # 发送邮件配置
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   # smpt服务地址
   EMAIL_HOST = 'smtp.qq.com'
   EMAIL_PORT = 465
   # 发送邮件的邮箱
   EMAIL_HOST_USER = '3184XXX3@qq.com'
   # 在邮箱中设置的客户端授权密码
   EMAIL_HOST_PASSWORD = 'owXXXdebg'
   # 收件人看到的发件人
   EMAIL_FROM = '天天生鲜<3184XXX3@qq.com>'
   ```

3. 修改视图文件 `.\apps\user\views.py`，修改 `RegisterView` 类中的 `post()` 方法，发送邮件，使用 Django 自带的 `send_mail()` 函数

##### 使用 celery 优化 `send_mail()` 函数

由于 `send_mail()` 函数往往比较耗时，故使用 `celery` 的任务队列机制，使该函数异步执行，提高效率，避免用户的页面等待

``` powershell
pip install celery  # 安装celery
scoop install redis  # 使用redis作为中间人/任务队列（broker）
pip install redis  # 安装redis客户端
redis-server.exe  # 启动redis服务端
redis-cli.exe  # redis客户端连接
```

在项目目录中创建 `celery_tasks` 文件夹，并添加发邮件的任务 `.\celery_tasks\tasks.py`

任务处理者（worker）开始监听队列（broker）

``` powershell
celery.exe -A celery_tasks.tasks worker -l info --pool=solo
```

###### Celery 排坑

在 Windows 10 下运行 `celery -A tasks worker --loglevel=info` 命令，会有 bug，处理者可以收到任务，但不执行，显示如下

``` powershell
INFO/MainProcess] Received task: tasks.my_task[aca8ec36-1aef-40b0-97cc-bbd4d48a837f]  # 收到测试文件tasks.py中的函数任务my_task
INFO/SpawnPoolWorker-10] child process 12640 calling self.run()  # 但没有显示执行结果
```

- 解决方法一

  将任务处理者部署在 Ubuntu 20.4 上

  1. 在 Windows 上启动 `redis-server.exe .\redis.conf`，其中的配置文件内容为 `bind <windows ip>`，用来替换默认的 redis 配置，可以让 Linux 局域网访问 Windows 上的 redis
  2. 在 Linux 上启动处理者 `celery -A tasks worker --loglevel=info`
  3. 在 Windows/Linux 上调用任务 `my_task.delay()`
  4. 此时输出正常

     ``` bash
     INFO/MainProcess] Received task: tasks.my_task[6d9e321b-ddb3-4b55-bd6e-a3d85d8b354d]  # 收到测试文件tasks.py中的函数任务my_task
     WARNING/ForkPoolWorker-4] 任务函数正在执行....
     INFO/ForkPoolWorker-4] Task tasks.my_task[6d9e321b-ddb3-4b55-bd6e-a3d85d8b354d] succeeded in 0.0010925110000243876s: None  # 异步执行完毕
     ```

- 解决方法二

  任务处理者依旧部署在 Windows 上

  1. 在 Windows 上启动 `redis-server.exe`，默认监听本地
  2. 在 Windows 上启动处理者 `celery -A tasks worker --loglevel=info --pool solo`
  3. 在 Windows 上调用任务 `my_task.delay()`
  4. 此时输出正常

     ``` powershell
     INFO/MainProcess] Received task: tasks.my_task[26f2c249-8ec4-4bfa-bd78-40441604e0e3]
     WARNING/MainProcess] 任务函数正在执行....
     INFO/MainProcess] Task tasks.my_task[26f2c249-8ec4-4bfa-bd78-40441604e0e3] succeeded in 0.0s: None
     ```

  > 参考：[How to run celery on windows?](https://stackoverflow.com/questions/37255548/how-to-run-celery-on-windows)

运行测试

``` powershell
python .\manage.py runserver  # 运行服务
```
