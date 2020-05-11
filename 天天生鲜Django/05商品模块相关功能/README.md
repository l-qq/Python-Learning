# 05

首页，详情页，商品列表，搜索

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
pip install django-haystack  # 全文检索框架
pip install whoosh  # 搜索引擎
pip install six jieba  # 参下

scoop install redis  # 使用redis作为中间人/任务队列（broker）
redis-server.exe .\redis.conf  # 其中的配置文件内容为 bind 0.0.0.0
scoop install mysql
mysqld.exe --console --bind-address=0.0.0.0  # 由于需要Ubuntu局域网访问，所以不默认绑定127.0.0.1
mysql -u root -p
create database dailyfresh charset=utf8;

sudo service fdfs_trackerd start
sudo service fdfs_storaged start
sudo /usr/local/nginx/sbin/nginx
celery -A celery_tasks.tasks worker --loglevel=info  # Linux下任务处理者开始监听

cd .\dailyfresh
python .\manage.py migrate
python .\manage.py rebuild_index
python .\manage.py runserver
```

## 学习笔记

### 开发步骤

#### 首页 index.html 功能

根据父模板修改 `.\templates\index.html`，修改视图文件 `.\apps\goods\views.py` 添加类试图 `IndexView`，修改路由规则 `.\apps\goods\urls.py`。

再次修改视图文件 `.\apps\goods\views.py`，根据静态页面的首页组织，在视图逻辑里返回上下文字典 `context`

``` python
# 组织模板上下文
context = {'types':types,
           'goods_banners':goods_banners,
           'promotion_banners':promotion_banners,
         #   "type_goods_banners":type_goods_banners,
           'cart_count':cart_count}
```

再次修改模板文件 `.\templates\index.html`，使用 `for` 循环取出 `context` 传递的模板变量，利用 python 语言的动态性，再次修改 `.\apps\goods\views.py` 给查到的商品种类添加新属性，这样可以方便模板文件遍历

``` python
type.image_banners = image_banners  # 给查询到的商品种类type添加新属性
type.title_banners = title_banners
```

修改视图文件 `.\apps\goods\views.py`，编写页面显示购物车的功能，购物车使用 redis 存储，存储格式为 `<key>:cart_user.id, <value>:{"goodsSKU.id1":amount1,"goodsSKU.id2":amount2}`，并修改父模板 `.\templates\base.html` 中显示购物车的部分 `{{ cart_count }}`

##### 静态化

由于首页经常被很多用户访问，避免每次访问时都从数据库取出模板上下文 `context`，考虑首页的静态化，使用 celery 来实现首页静态化功能。在文件 `.\celery_tasks\tasks.py` 中新建任务 `generate_static_index_html()`。并由 `base.html` 创建新的模板文件 `static_base.html`，让 `static_index.html` 继承该模板

- 测试 `generate_static_index_html()`

  1. 启动 celery 任务执行者开始监听队列 `celery.exe -A celery_tasks.tasks worker --loglevel=info --pool solo`
  2. 启动 python 交互解释器，并执行

     ``` powershell
     >>> from celery_tasks.tasks import generate_static_index_html
     >>> generate_static_index_html.delay()
     <AsyncResult: a7f35e4a-60bc-4847-bf5b-f3ce7beb7537>
     ```

  3. 此时发现 celery 任务执行者电脑中的 `.\static\` 目录下生成了新的静态首页 `index.html`

- 使用 Nginx 托管生成的静态首页

  分布式架构说明，Windows 10 电脑上部署 Django 项目，同时部署 MySql 和 Redis 服务端。Ubuntu 20.04 电脑上部署 Celery 监听 Redis 的任务队列，同时部署 FastDFS 和 Nginx Web 服务器，其中 Nginx 提供 FastDFS 的文件访问，以及提供访问生成的首页静态文件 `index.html`

  1. 复制当前项目文件夹 `dailyfresh` 到 Linux 系统上，修改`settings.py` 和 `tasks.py` 中的数据库等 IP 地址，并安装所需依赖 `pip3 install django django-tinymce django-redis mysqlclient celery redis itsdangerous`。安装 `mysqlclient` 失败时可以试试安装依赖 `sudo apt install libmysqlclient-dev`
  2. Windows 上启动相关软件

     ``` powershell
     mysqld.exe --console --bind-address=0.0.0.0  # 由于需要Ubuntu局域网访问，所以不默认绑定127.0.0.1
     redis-server.exe .\redis.conf  # 其中的配置文件内容为 bind 0.0.0.0，用来替换默认的 redis 配置，这样既可以让 Linux 局域网访问 Windows 上的 redis，还可以让 Windows 上 Django 网站本地访问 redis
     ```

     Windows 下连接 MySQL，创建一个新用户给 Ubuntu 使用

     ``` powershell
     mysql -u root
     mysql> CREATE USER 'vm'@'%' IDENTIFIED BY 'hahaha';  # 创建用户：vm密码：hahaha，记得修改Ubuntu中settings.py文件中的DATABASES数据
     mysql> GRANT ALL PRIVILEGES ON dailyfresh.* TO 'vm'@'%' WITH GRANT OPTION;  # 授权该用户可以从任何机器访问，并对数据库dailyfresh拥有所有权限
     ```

     > 参考：[How to grant all privileges to root user in MySQL 8.0](https://stackoverflow.com/questions/50177216/how-to-grant-all-privileges-to-root-user-in-mysql-8-0/50197630)
     >
     > [MySQL允许局域网连接](https://www.jianshu.com/p/8e8d3b657709)

  3. Linux 上启动相关软件

     ``` bash
     sudo service fdfs_trackerd start
     sudo service fdfs_storaged start
     sudo /usr/local/nginx/sbin/nginx
     ```

  4. 修改 Nginx 的配置，增加一个对静态首页 `index.html` 资源访问的 `server` 项

     ``` bash
     sudo vim /usr/local/nginx/conf/nginx.conf  # 配置nginx
     server {
        listen       80;
        server_name  localhost;
        location /static {
            alias /home/vm/桌面/05商品模块相关功能/dailyfresh/static;
        }
        location / {
            #root   html;
            root /home/vm/桌面/05商品模块相关功能/dailyfresh/static;
            index  index.html index.htm;
        }
        ...
     }
     sudo /usr/local/nginx/sbin/nginx -s reload  # 重启nginx
     ```

  5. Celery 开始监听 `celery -A celery_tasks.tasks worker --loglevel=info`
  6. Windows 启动 python 交互解释器，并执行 `generate_static_index_html.delay()`
  7. 测试验证，访问网站，Ubuntu 访问 <http://127.0.0.1:80>，Windows 访问 <http://192.168.58.128:80>

修改 `.\apps\goods\urls.py` 的路由规则，静态首页访问 <http://127.0.0.1:80>，动态首页访问 <http://127.0.0.1:8000/index>，以后通过再搭建一个 Nginx 来调度对这两个首页的访问请求

修改 `.\apps\goods\admin.py` 文件，增加模型管理类 `IndexPromotionBannerAdmin` 继承自 Django 自带的 `admin.ModelAdmin` 并重写 `save_model()` 和 `delete_model()` 方法，这样可以实现后台管理时当对数据表进行了修改，即调用 celery 中的任务，重新生成新的静态首页。使用 celery 异步执行任务，可以避免管理员修改数据表后页面卡死等待

##### Redis 缓存首页内容

首页数据的缓存（首页静态化针对的是众多非登录用户访问首页时的优化，首页数据缓存针对的是登录用户访问时，生成动态首页是的优化，避免登录用户多次访问首页而导致反复进行数据库查询操作）。Django 有站点缓存、视图缓存、模板片段缓存。站点缓存占用空间太多，不同用户视图返回结果不一样，使用视图缓存不好，由于视图最后才渲染模板，使用模板片段缓存也不好。

修改视图文件 `.\apps\goods\views.py` 的 `IndexView`，使用自定义的缓存（调用 Django 底层的缓存 API），编写 `cache.set()` 和 `cache.get()` 方法

修改 `.\apps\goods\admin.py` 文件中的模型管理类，实现后台管理时当对数据表进行修改，就调用 `cache.delete()` 方法，清空缓存，这样用户在访问首页时就会重新生成缓存

#### 商品详情页 detail.html 功能

复制 `.\static\detail.html` 到模板文件 `.\templates\detail.html`，并根据父模板改造该详情页面的模板文件并修改视图文件 `.\apps\goods\views.py` 添加类试图 `DetailView`，修改路由规则 `.\apps\goods\urls.py`

根据商品详情页的组织结构，在视图逻辑里返回上下文字典 `context`，然后再次修改模板文件 `.\templates\detail.html` 和 `.\templates\base_detail_list.html`

##### 用户浏览历史记录的功能

首先给模板文件 `.\templates\index.html` 中的每个商品链接 `<a>` 标签加上 URL 反向解析，解析到商品详情页

接着给视图 `DetailView` 类中，判断完用户登录后，使用 redis 添加该用户的浏览记录，然后去完善 `.\templates\user_center_info.html` 模板中历史记录部分的 `<a>` 标签链接属性 `href=` 使用反向解析 `url 'goods:detail' goods.id`

#### 商品列表页 list.html 功能

复制 `.\static\list.html` 到模板文件 `.\templates\list.html`，并根据父模板改造该详情页面的模板文件。编写视图 `ListView`，访问列表页面时需要在 URL 传递 `商品种类，显示第几页，排序方式` 信息。使用 restful api 设计风格，增加该页面的路由规则 `.\apps\goods\urls.py`

视图中使用 Django 自带的 `Paginator` 实现分页。然后实现页码控制，只显示 5 页

#### 搜索功能

使用全文检索框架 `haystack`，框架调用的搜索引擎为 `whoosh`

1. 安装

   ``` powershell
   pip install django-haystack  # 全文检索框架
   pip install whoosh  # 搜索引擎
   ```

2. 配置

   在项目的 `.\dailyfresh\settings.py` 注册应用 `haystack`，并添加对应的配置

   ``` python
   # 全文检索框架的配置
   HAYSTACK_CONNECTIONS = {
      'default': {
         # 使用whoosh引擎
         'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',  # \virtual_env\Lib\site-packages\haystack\backends\whoosh_backend.py
         # 索引文件路径
         'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
      }
   }
   ```

3. 使用 whoosh 引擎建立索引

   需要根据商品模型 `GoodsSKU` 生成索引信息，方便搜索。在应用 goods 目录下新建索引类 `.\apps\goods\search_indexes.py`，该文件名字为固定写法。文件 `search_indexes.py` 中使用了 `use_template=True`，所以在模板目录下 `.\templates` 创建 `.\templates\search\indexes\goods\goodssku_text.txt`（为固定写法，「应用名\模型类小写_text.txt」），编辑该文件指定表中需要生成索引的字段

   完成后，开始建立索引

   ``` powershell
   python.exe .\manage.py rebuild_index
   ```

   建立索引时会报错: ImportError: cannot import name 'six' from 'django.utils'。解决如下：

   1. `pip install six`
   2. 复制 `\virtual_env\Lib\site-packages\six.py` 到 `\virtual_env\Lib\site-packages\django\utils` 目录下

   然后又报错: ImportError: cannot import name 'python_2_unicode_compatible' from 'django.utils.encoding'。解决如下：

   ``` python
   # 将site-packages\haystack\inputs.py 中
   from django.utils.encoding import force_text, python_2_unicode_compatible
   # 改为
   from django.utils.encoding import force_text
   from django.utils.six import python_2_unicode_compatible
   ```

   > 参考：<https://blog.csdn.net/weixin_44485643/article/details/104243048>

   建立索引后，会发现项目目录下自动生成了 `.\whoosh_index` 文件夹（是根据 `settings.py` 中指定的目录生成的）

4. 编码

   首先修改模板文件 `base.html` 中有关搜索的 `<div>`，使之变成一个 `<from>`，根据表单的提交地址，修改路由规则 `.\dailyfresh\urls.py`，将匹配到的处理逻辑交给全文检索框架 `haystack` 处理

   ``` python
   url(r'^search', include('haystack.urls'))
   ```

   由于 `haystack` 处理请求需要渲染的模板文件，所以在 `.\templates\search\` 目录下新建模板文件 `search.html`，该模板内容参考 `.\templates\list.html`

5. 进一步优化

   默认的搜索引擎对中文的分词效果不是很好，有些搜索结果为空，所以需要改造 `haystack` 后端的搜索引擎 `whoosh`

   ``` powershell
   pip install jieba  # 安装分词包
   # 交互环境，体验一下
   python
   >>> import jieba
   >>> str = "今天天气真好，风也温柔"
   >>> res = jieba.cut(str, cut_all=True)
   >>> res
   <generator object Tokenizer.cut at 0x000002917E1274A0>
   >>> for val in res:
   ...     print(val)
   ...
   ```

   1. 找到虚拟环境 `haystack` 安装包的后端文件夹 `\virtual_env\Lib\site-packages\haystack\backends` 进入该目录，创建新文件 `ChineseAnalyzer.py`，文件内容如下

      ``` python
      import jieba
      from whoosh.analysis import Tokenizer, Token

      class ChineseTokenizer(Tokenizer):
         def __call__(self, value, positions=False, chars=False, keeporiginal=False, removestops=True, start_pos=0, start_char=0, mode="", **kwargs):
            t = Token(positions, chars, removestops=removestops, mode=mode, **kwargs)
            seglist = jieba.cut(value, cut_all=True)
            for w in seglist:
               t.original = t.text = w
               t.boost = 1.0
               if positions:
                  t.pos = start_pos + value.find(w)
               if chars:
                  t.startchar = start_char + value.find(w)
                  t.endchar = start_char + value.find(w) + len(w)
               yield t

      def ChineseAnalyzer():
         return ChineseTokenizer()
      ```

   2. 复制一份 `whoosh_backen.py`，改为 `whoosh_cn_backen.py`，对该文件修改如下

      ``` powershell
      导入我们自己的词语分析类：
      from .ChineseAnalyzer import ChineseAnalyzer
      查找：
      analyzer=ChineseAnalyzer()
      替换为：
      analyzer=ChineseAnalyzer()
      ```

   3. 修改项目配置 `settings.py` 使用改造后的后端引擎

      ``` python
      'ENGINE': 'haystack.backends.whoosh_cn_backend.WhooshEngine',
      ```

      然后重新生成索引 `python.exe .\manage.py rebuild_index` 并启动项目检查 `python.exe .\manage.py runserver`
