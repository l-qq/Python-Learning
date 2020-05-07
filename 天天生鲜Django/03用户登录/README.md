# 03

用户注册后，跳转到登陆页面，完成用户登录的相关逻辑代码

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
pip install django-redis  # 使用Redis作为Django缓存和session存储后端
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

#### 完善登录页面功能

1. 修改 `.\templates\login.html` 模板文件。用 `load static` 和 `static 'css/reset.css'` 等，`<form method="post">`，action 不写，则提交地址仍为当前页
2. 修改视图文件 `.\apps\user\views.py`，给 `LoginView` 类添加 `post()` 方法，响应用户登录

#### 使用 Redis 存储 Session

由于使用 Django 自带的 `login()` 函数存储的 session 信息在 MySQL 中的 `django_session` 表中，影响读写。故使用 Redis 作为 Django 缓存和 session 存储后端

1. `pip install django-redis`，然后修改项目的 `.\dailyfresh\settings.py`，增加如下

   ``` python
   CACHES = {
      "default": {
         "BACKEND": "django_redis.cache.RedisCache",
         "LOCATION": "redis://127.0.0.1:6379/9",
         "OPTIONS": {
               "CLIENT_CLASS": "django_redis.client.DefaultClient",
         }
      }
   }
   SESSION_ENGINE = "django.contrib.sessions.backends.cache"
   SESSION_CACHE_ALIAS = "default"
   ```

#### 完善记住用户名功能

1. 修改视图文件 `.\apps\user\views.py`，`LoginView` 类中的 `post()` 方法，使用 `response.set_cookie()` 方法记住用户名
2. 修改视图文件 `.\apps\user\views.py`，`LoginView` 类中的 `get()` 方法，根据是否有 cookie 而渲染不同的登录页面
3. 修改 `.\templates\login.html` 模板文件。用 `value="{{ username }}"` 和 `{{ checked }}`
