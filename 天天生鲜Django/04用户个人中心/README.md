# 04

编写用户中心的三个页面的逻辑实现，并在 Ubuntu 上用 FastDFS 存储静态图片

## 快速使用

``` powershell
python -m venv virtual_env  # 创建虚拟环境
.\virtual_env\Scripts\activate  # 激活虚拟环境
pip install django
pip install django-tinymce  # 富文本
pip install mysqlclient  # django使用mysqlclient，弃用pymysql
pip install Pillow
pip install itsdangerous  # 签名加密
pip install celery  # 异步处理，任务队列，加入/执行任务到redis
pip install redis  # 安装redis客户端
pip install django-redis  # 使用Redis作为Django缓存和session存储后端
pip install fdfs_client_py34  # .\utils\fdfs\storage.py使用第三方包来上传文件到fastdfs

scoop install redis  # 使用redis作为中间人/任务队列（broker）
redis-server.exe  # 启动redis服务端
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

#### 提取模板页面基类

根据 `static` 文件夹下的页面，提取 4 个父模板页面 `base_*.html` 到 `.\templates` 文件夹下。将 `static` 文件夹中的用户中心的 3 个页面复制到 `.\templates`，并基于父模板页面进行改造

#### 编写视图 ➕ 路由

编写用户中心的 3 个页面的视图，`UserInfoView`，`UserOrderView` 和 `AddressView`，并配置 URL 路由规则

#### 登录装饰器及登陆后页面跳转

当使用 Django 自带的用户认证系统时，可以使用 Django 中的 `login_required` 装饰器，对视图函数装饰，从而限制未登录用户访问页面。由于 `login_required` 只能对视图函数装饰，所以对于视图类，修改 URL 路由规则 `.\apps\user\urls.py` 如下

``` python
url(r'^$', login_required(UserInfoView.as_view()), name='user'), # 用户中心-信息页
url(r'^order$', login_required(UserOrderView.as_view()), name='order'), # 用户中心-订单页
url(r'^address$', login_required(AddressView.as_view()), name='address'), # 用户中心-地址页
```

然后在项目配置文件中指定用户需要登陆的登录页面，修改 `.\dailyfresh\settings.py`

``` python
# 配置登录url地址
LOGIN_URL='/user/login' # 替换默认的/accounts/login这个地址
```

##### 登陆后页面跳转

修改 `LoginView` 中的 `post()` 方法，获取用户需要跳转的地址信息 `next/...`，代码为 `request.GET.get("next", reverse("goods:index"))` 指定如果没有 `next/...` 参数则跳转到首页

##### 精简优化

项目目录下创建 `.\utils` 工具包，新建 `mixin.py` 文件，创建 `LoginRequiredMixin` 类，类中的方法使用 `login_required` 装饰器修饰，然后让需要登录的视图（`UserInfoView`，`UserOrderView` 和 `AddressView`）继承该类

#### 编写 LogoutView 视图 ➕ 路由配置

一个请求过来后，Django 框架自动给 `request` 对象增加 `user` 属性，除了使用 `render` 函数给模板文件传递模板变量外，Django 框架会把 `request.user` 也传递给模板文件，所以可以直接在前端模板文件中使用 `if user.is_authenticated` 来验证用户是否登入，并使用 `user.username` 等值

使用 Django 自带的 `logout()` 函数退出登录，并且会自动清理 session，可以在 redis 中 `keys *` 来验证 session 是否删除

#### 再次完善用户中心的 3 个页面的视图并修改对应的模板文件

##### 完善 AddressView

修改 `.\apps\user\models.py` 文件，自定义地址模型管理器类 `AddressManager`。修改 `.\apps\user\views.py` 文件使用自定义模型管理器的方法 `Address.objects.get_default_address(user)`

##### 完善 UserInfoView

用户的浏览历史使用 redis 存储，存储格式为 `<key>:history_user.id, <value>:[goods.id1,good.id2]`，使用 `django-redis` 包的 `get_redis_connection()` 函数连接 redis，遍历获取用户浏览的商品信息，并将结果列表 `goods_li` 返回到模板页面，模板页面 `user_center_info.html` 使用 `for goods in goods_li` 模板标签展示用户的历史记录

#### 使用 FastDFS

FastDFS 分布式文件存储，海量存储，存储容量扩展方便，而且存储文件时使用哈希（文件指纹），可以减少冗余

##### 安装

在 Ubuntu 20.04 上安装 FastDFS

1. 首先安装依赖 `libfastcommon` <https://github.com/happyfish100/libfastcommon/releases>

   ``` bash
   cd libfastcommon-1.0.43/
   ./make.sh
   sudo ./make.sh install
   ```

2. 接着安装 `fastdfs` <https://github.com/happyfish100/fastdfs/releases>

   ``` bash
   cd fastdfs-6.06/
   ./make.sh
   sudo ./make.sh install
   ```

##### 配置

1. 配置 tracker 服务器

   ``` bash
   sudo cp /etc/fdfs/tracker.conf.sample /etc/fdfs/tracker.conf
   mkdir -p /home/vm/fastdfs/tracker  # 在用户vm的家目录下创建tracker文件夹
   sudo vim /etc/fdfs/tracker.conf
   base_path = /home/vm/fastdfs/tracker  # 配置tracker服务器存储数据的位置为刚刚创建的目录
   ```

2. 配置 storage 服务器

   ``` bash
   sudo cp /etc/fdfs/storage.conf.sample /etc/fdfs/storage.conf
   mkdir -p /home/vm/fastdfs/storage  # 在用户vm的家目录下创建storage文件夹
   sudo vim /etc/fdfs/storage.conf
   base_path = /home/vm/fastdfs/storage  # 配置storage服务器存储数据的位置为刚刚创建的目录
   store_path0 = /home/vm/fastdfs/storage  # 配置storage服务器存储文件的位置
   tracker_server = 192.168.58.128:22122  # ubuntu的IP地址加端口号，表明该storage服务器由哪个tracker服务器管理
   ```

3. 配置 client 客户端

   ``` bash
   sudo cp /etc/fdfs/client.conf.sample  /etc/fdfs/client.conf
   sudo vim /etc/fdfs/client.conf  # 修改客户端连接配置
   base_path = /home/vm/fastdfs/tracker  # 日志存储位置
   tracker_server = 192.168.58.128:22122  # ubuntu的IP地址加端口号，表明客户端使用哪个tracker服务器连接storage服务器
   ```

4. 启动

   ``` bash
   sudo service fdfs_trackerd start
   sudo service fdfs_storaged start
   ```

   上传文件测试 `fdfs_upload_file /etc/fdfs/client.conf <要上传的图片/文件>`，如果返回类似 `group1/M00/00/00/wKg6gF6zfiqAbf3XAEOAAM1oumU994.JPG` 的文件则表明上传成功，前往 `~/fastdfs/storage/data/00/00/` 目录即可找到该文件

##### 安装 nginx 及 fastdfs-nginx-module

当用户量请求比较大下载的时候就会有点慢，需借助 nginx 服务器，Nginx 内部使用 epoll 技术，可以应对大量的静态资源请求，效率高

1. 安装

   下载 nginx 安装包 <http://nginx.org/en/download.html>

   下载 fastdfs-nginx-module 模块 <https://github.com/happyfish100/fastdfs-nginx-module/releases>

   ``` bash
   cd ~
   tar -xvzf nginx-1.18.0.tar.gz  # 解压nginx
   tar -xvzf fastdfs-nginx-module-1.22.tar.gz  # 解压模块
   cd nginx-1.18.0/  # 进入nginx目录
   sudo apt install libpcre3 libpcre3-dev  # 配置nginx前，首先安装依赖PCRE
   sudo ./configure --prefix=/usr/local/nginx/ --add-module=/home/vm/桌面/fastdfs-nginx-module-1.22/   src/  # 为了让nginx配合fastdfs一起使用，安装nginx的时候添加fastdfs模块，指定nginx的安装位置，指定模块的绝对路径
   sudo make
   sudo make install
   ```

2. 配置

   ``` bash
   sudo cp ~/桌面/fastdfs-nginx-module-1.22/src/mod_fastdfs.conf /etc/fdfs/mod_fastdfs.conf
   sudo vim /etc/fdfs/mod_fastdfs.conf
   connect_timeout = 10
   tracker_server = 192.168.58.128:22122
   url_have_group_name = true  # 路径带不带组的信息group1
   store_path0 = /home/vm/fastdfs/storage  # 数据存放目录
   sudo cp ~/桌面/fastdfs-6.06/conf/http.conf /etc/fdfs/http.conf  # 复制fastdfs源码包里的文件到/etc/fdfs/目录下
   sudo cp ~/桌面/fastdfs-6.06/conf/mime.types /etc/fdfs/mime.types
   sudo vim /usr/local/nginx/conf/nginx.conf  # 配置nginx
   # 在http中添加一个server
   server{
      listen  8888;
      server_name  localhost;
      location  ~/group[0-9]/ {  # 访问的时候地址匹配上了就调用ngx_fastdfs_module
         ngx_fastdfs_module;
         }
      error_page  500 502 503 504 /50x.html;
      location = /50x.html {
         root html;
         }
      }
   ```

3. 启动并测试

   启动 nginx 服务器：`sudo /usr/local/nginx/sbin/nginx`

   Ubuntu 访问浏览器 <http://localhost:8888/group1/M00/00/00/wKg6gF6zfiqAbf3XAEOAAM1oumU994.JPG>

   Windows 访问浏览器 <http://192.168.58.128:8888/group1/M00/00/00/wKg6gF6zfiqAbf3XAEOAAM1oumU994.JPG>

   关闭 nginx 服务器：`sudo /usr/local/nginx/sbin/nginx -s stop`

##### 使用 Python 对接 FastDFS/Nginx

Ubuntu 下安装包 `pip3 install fdfs_client_py34`（使用带 _py34 结尾的包以兼容 python3），然后在 python3 交互环境下测试上传文件到 fastdfs

> 或者参考 <https://github.com/JaceHo/fdfs_client-py> 安装第三方包

``` bash
>>> from fdfs_client.client import *
>>> client = Fdfs_client('/etc/fdfs/client.conf')
>>> ret = client.upload_by_filename('./test.JPG')
>>> ret
{'Group name': b'group1', 'Remote file_id': b'group1/M00/00/00/wKg6gF6zw8qAH6biAEEAAJpGM-w253.JPG', 'Status': 'Upload successed.', 'Local file name': './test.JPG', 'Uploaded size': '4.06MB', 'Storage IP': b'192.168.58.128'}
```

#### 修改 Django 默认的文件上传行为

Django 默认上传文件使用的是 `FileSystemStorage` 类，里面有个 `save` 方法帮我们把文件保存在 MEDIA_ROOT 指定的目录中。如果我们要保存在 fastdfs 系统中，我们就要修改此类，当然不是修改 `FileSystemStorage` 代码，手写一个类继承 `Storeage` 且必须实现 `_open()` 和 `_save()` 方法

新建 `.\utils\fdfs\storage.py` 文件，编写自定义的文件存储类 `FDFSStorage`，新建 `.\utils\fdfs\client.conf` 文件（将 Ubuntu 中的 `client.conf` 复制过来），Windows 虚拟环境中 `pip install fdfs_client_py34`

修改项目配置文件 `.\dailyfresh\settings.py`

``` python
# 设置Django的文件存储类
DEFAULT_FILE_STORAGE='utils.fdfs.storage.FDFSStorage'
```

开始测试 admin 后台管理页面能否上传商品图片

1. 创建超级用户 `python manage.py createsuperuser` （自用用户名：admin，密码：~~root123123~~）
2. 启动项目 `python manage.py runserver` 访问 <http://127.0.0.1:8000/admin/>
3. 在 `.\apps\goods\admin.py` 中注册 `GoodsType` 模型类，这样就可以在后台添加商品类型
4. 再次刷新后台页面并添加商品图片，打开商品图片，发现需要完善 `FDFSStorage` 类中的 `url()` 方法，有了这个方法才可以配合前端模板文件 `user_center_info.html` 中 `{{ goods.image.url }}` 的 `.url`
5. 精简优化，在 `.\dailyfresh\settings.py` 中添加

   ``` python
   # 设置fdfs使用的client.conf文件路径
   FDFS_CLIENT_CONF='./utils/fdfs/client.conf'
   # 设置fdfs存储服务器上nginx的IP和端口号，为之前Ubuntu上的IP地址
   FDFS_URL='http://192.168.58.128:8888/'
   ```
