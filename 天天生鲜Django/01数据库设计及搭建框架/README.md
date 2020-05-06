# 01

根据需求分析及页面最终展示，设计数据表，完成模型类的编码并搭建整体框架

## 快速使用

``` powershell
python -m venv virtual_env
.\virtual_env\Scripts\activate
pip install django
pip install django-tinymce
pip install mysqlclient
pip install Pillow
scoop install mysql
mysqld.exe --console
mysql -u root -p
create database dailyfresh charset=utf8;
cd .\dailyfresh
python .\manage.py migrate
python .\manage.py runserver
```

## 学习笔记

### 开发步骤

#### 需求分析 ➕ 数据库设计

分析需求，确定项目架构，设计数据表

#### 搭建项目框架

``` powershell
python -m venv virtual_env  # 创建名为virtual_env的虚拟环境
.\virtual_env\Scripts\activate  # 激活并使用该虚拟环境
pip install django  # 虚拟环境中安装Django
django-admin.exe startproject dailyfresh  # 创建项目
cd .\dailyfresh\  # 进入项目目录（该目录包含manage.py）
python .\manage.py startapp user  # 创建用户模块
python .\manage.py startapp goods  # 商品
python .\manage.py startapp cart  # 购物车
python .\manage.py startapp order  # 订单
deactivate  # 停止使用虚拟环境
```

由于应用较多，在项目目录中创建 `apps` 文件夹，并将当前目录中的 `user`、`goods`、`cart` 和 `order` 文件夹放入 `apps` 文件夹中，并对 `.\dailyfresh\settings.py` 修改如下

``` python
import sys
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))  # 将apps目录加入搜索路径，可以避免在注册App时输入apps.application_name
```

在项目目录中创建 `templates` 文件夹，并修改 `.\dailyfresh\settings.py`

``` python
'DIRS': [os.path.join(BASE_DIR, 'templates')],  # 配置模板目录
```

安装 MySql `scoop install mysql`，启动数据库服务端 `mysqld.exe --console`，连接数据库 `mysql -u root -p`，创建数据库 `create database dailyfresh charset=utf8;`，并修改 `.\dailyfresh\settings.py`

``` python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dailyfresh',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': 3306,
    }
}
```

本地化，设置时区及语言，修改 `.\dailyfresh\settings.py`

``` python
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
```

在项目目录中创建 `static` 文件夹，并修改 `.\dailyfresh\settings.py`

``` python
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
```

给每个 App 新建 `urls.py`，并修改 `.\dailyfresh\urls.py`

``` python
url(r'^user/', include('user.urls', namespace='user')), # 用户模块，加上namespace可以使用url反向解析
url(r'^cart/', include('cart.urls', namespace='cart')), # 购物车模块
url(r'^order/', include('order.urls', namespace='order')), # 订单模块
url(r'^', include('goods.urls', namespace='goods')), # 商品模块
```

创建模型抽象基类，在项目目录中创建 `db` 文件夹，并在该文件夹下新建 `base_model.py`

根据设计的数据表，编写各个 App 中的模型类，修改 `models.py`

- 修改 `.\apps\user\models.py`，需修改 `.\dailyfresh\settings.py`，来指定生成迁移文件时使用自定义的用户模型类，而不使用 Django 自动生成的 `auth_user` 表

  ``` python
  AUTH_USER_MODEL='user.User'
  ```

- 修改 `.\apps\goods\models.py`，由于使用了富文本编辑器 **tinymce**（`pip install django-tinymce`），需修改 `.\dailyfresh\settings.py`

  ``` python
  INSTALLED_APPS = [
    ...
    'tinymce',  # 富文本编辑器注册App
  ]
  # 富文本编辑器配置
  TINYMCE_DEFAULT_CONFIG = {
      'theme': 'advanced',
      'width': 600,
      'height': 400,
  }
  ```

  接着`.\dailyfresh\urls.py` 增加一行 `url(r'^tinymce/', include('tinymce.urls')),`

- 修改 `.\apps\order\models.py`

~~安装 `pip install pymysql` 并修改 `.\dailyfresh\__init__.py`~~

``` python
import pymysql
pymysql.install_as_MySQLdb()
```

新版 Django 已经不用 `pymysql` 了，改用 `mysqlclient` 了，`pip install mysqlclient`，然后清空 `.\dailyfresh\__init__.py` 中的内容

#### 运行测试

``` powershell
pip install Pillow  # 接着安装额外依赖的包
python .\manage.py makemigrations  # 生成迁移文件（执行后app下的migrations中会生成新文件，用来表示数据表，show tables;返回依然为空）
python .\manage.py migrate  # 迁移数据库(执行后，show tables;返回值不为空，新的数据表已创建)
python .\manage.py runserver  # 运行服务
```
