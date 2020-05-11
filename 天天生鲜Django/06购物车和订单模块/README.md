# 06

---------------++++++++++++---

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
pip install python-alipay-sdk  # 支付宝API第三方SDK

scoop install redis  # 使用redis作为中间人/任务队列（broker）
redis-server.exe .\redis.conf  # 其中的配置文件内容为 bind 0.0.0.0
scoop install mysql
mysqld.exe --console --bind-address=0.0.0.0  # 由于需要Ubuntu局域网访问，所以不默认绑定127.0.0.1
mysql -u root -p
create database dailyfresh charset=utf8;
scoop install openssl

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

#### 购物车功能

修改商品详情页面的模板文件 `.\templates\detail.html`，页面底部增加 JS 代码，动态显示用户选择的商品数量和价钱总金额

##### 添加商品到购物车按钮

由于在商品详情页添加购物车时，页面没有跳转，所以使用 Ajax POST 方式（涉及数据表的修改，所以用 POST 方式）实现

首先编写购物车应用的后台逻辑，修改视图文件 `.\apps\cart\views.py`，增加 `CartAddView`，购物车的数据由 redis 存储，由于 Ajax 提交都是在后台执行，所以视图文件验证用户是否登录不能用装饰器，即便装饰了引导用户跳转登陆页面也只会在后台返回登陆页面，用户界面依然不变。然后添加路由规则 `.\apps\cart\urls.py`

接着修改前端页面 `.\templates\detail.html`，底部增加 Ajax 提交请求。由于 Django 默认开启 CSRF 防护，提交表单时可以通过 `csrf token` 发送给后台，而 Ajax 提交时，可以通过获取 `csrf token` 隐藏域的数据，然后再提交 POST 请求

##### 我的购物车显示页面

复制静态页面 `.\static\cart.html` 到模板文件 `.\templates\cart.html` 下，并修改该模板文件，同时修改父模板 `.\templates\base.html` 中「我的购物车」的链接地址。然后修改视图文件增加 `CartInfoView`，并在路由规则中增加 `url(r'^$', CartInfoView.as_view(), name='show')`

###### 功能完善

编写模板文件 `.\templates\cart.html` 「全选/全不选」功能 JS

编写视图 `.\apps\cart\views.py` 增加 `CartUpdateView`（和`CartAddView` 类似），增加前端页面「+/-」功能，添加路由

购物车的删除视图，从 redis 删除该商品 id 和数量

### 订单模块

#### 购物车页面的「去结算」

首先修改 `.\templates\cart.html` 模板文件，给「去结算」增加表单表单，并设置 `<form>` 的提交地址

路由规则 `.\apps\order\urls.py` 中增加 `url(r'^place$', OrderPlaceView.as_view(), name='place')`

编写视图文件 `.\apps\order\views.py` 增加 `OrderPlaceView`，使用 `request.POST.getlist` 方法获取前端页面选中的所有商品的 id

复制静态页面 `.\static\place_order.html` 到模板文件 `.\templates\place_order.html` 下，并修改该模板文件，`radio` 标签设置 `name` 属性后就可以实现单选，选择一个邮寄地址

#### 结算页面的「提交订单」

完善模板文件 `.\templates\place_order.html`「提交订单」功能，编写 JS，使用 Ajax 提交到后台地址

路由规则 `.\apps\order\urls.py` 中增加 `url(r'^commit$', OrderCommitView.as_view(), name='commit')`

根据 JS 的提交地址，再视图 `.\apps\order\views.py` 文件增加 `OrderCommitView1`，在该视图中需要对请求的数据校验，为了校验数据是否合法，在模型类 `.\apps\order\models.py` 里添加字典。并且使用事务，保证该业务逻辑中生成的两个表的记录不出错

#### 订单并发

`OrderCommitView1` 的业务处理逻辑中，如果存在两个用户/进程同时下单，高并发下容易存在一件物品卖出去了多次的问题

- 解决办法：

  **悲观锁：** 在查询数据前先加锁 `select * from df_goods_sku where id=17 for update;`，使用 `for update` 加锁，等事务完成后释放锁。例子：修改 `OrderCommitView1` 视图类中代码，在使用事务 `@transaction.atomic` 的基础上，查询前增加 `sku = GoodsSKU.objects.select_for_update().get(id=sku_id)` 进而加锁

  **乐观锁：** 在查询数据前不加锁，在更新的时候判断和之前读到的数据是否一致。更新时 `update df_goods_sku set stock=0,sales=1 where id=17 and stock=1;`，使用 `and stock=1` 确保和之前查到的库存量一致。例子：复制 `OrderCommitView1` 为 `OrderCommitView`，在 `OrderCommitView` 中更新数据时使用如下代码

  ``` python
  # todo: 更新商品的库存和销量
  orgin_stock = sku.stock
  new_stock = orgin_stock - int(count)
  new_sales = sku.sales + int(count)
  # update df_goods_sku set stock=new_stock, sales=new_sales where id=sku_id and stock = orgin_stock
  # 返回受影响的行数
  res = GoodsSKU.objects.filter(id=sku_id, stock=orgin_stock).update(stock=new_stock, sales=new_sales)
  ```

  *乐观锁的问题：* 乐观锁在更新失败时，虽然表明与先前的查询数据不一致，有人抢先修改了数据，但并不表明没有了库存，用户不能下单。所以还要修改 `OrderCommitView` 代码，增加循环多次去抢订单 `for i in range(3):`。虽然增加了多次尝试，还是失败，是因为 MySQL 默认的事务之间的隔离级别为「可重复读」，需要降低一下隔离级别，改为「读已提交」

  在冲突比较少的的时候建议使用乐观锁，可以省去加锁的开销，而且往往一次就成功，不用多次尝试。如果乐观锁产生冲突需要尝试的代价比较大，那么就用悲观锁。

#### 订单支付

用户提交订单后，页面 `place_order.html` 将跳转到用户中心的全部订单页面 `user_center_order.html`

开始编写用户模块的用户中心-订单页，由于订单页有分页效果，所以跳转该页时需要传递页码信息，修改路由规则 `.\apps\user\urls.py`

``` python
url(r'^order/(?P<page>\d+)$', UserOrderView.as_view(), name='order'), # 用户中心-订单页
```

视图文件 `.\apps\user\views.py` 导入订单模型类 `OrderInfo` 和 `OrderGoods`，然后编写视图类 `UserOrderView`

修改模板页面，根据后台返回的模板上下文修改 `user_center_order.html`

##### 使用支付宝开放平台

登录支付宝开放平台，使用「沙箱」应用，参考文档 [电脑网站支付](https://opendocs.alipay.com/open/270)

如果网站没有公网 IP，则付款结果由支付宝返回给商户网站时，支付宝无法访问商户网站，为了能查到用户的付款结果，这时商户网站可以主动调用支付宝 API `alipay.trade.query` 查询付款结果

使用支付宝 API 的第三方 SDK（对支付宝原生 API 进行了封装）<https://github.com/fzlee/alipay/blob/master/README.zh-hans.md>

``` powershell
pip install python-alipay-sdk --upgrade  # 安装python版SDK
scoop install openssl  # 安装openssl，使用它生成公私钥并上传到支付宝开放平台「沙箱」应用中的信息配置
# 生成密钥文件
openssl
OpenSSL> genrsa -out app_private_key.pem 2048  # 生成私钥
OpenSSL> rsa -in app_private_key.pem -pubout -out app_public_key.pem  # 导出该私钥对应的公钥
OpenSSL> exit
```

然后将生成的公钥上传到「沙箱」应用中，并在「沙箱」应用中得到支付宝公钥。在项目订单应用下创建支付宝公钥文件 `.\apps\order\alipay_public_key.pem`，同理把刚刚生成的私钥文件放到该目录下 `.\apps\order\app_private_key.pem`

开始编写视图文件 `.\apps\order\views.py` 中的 `OrderPayView`，利用第三方 SDK 发送请求调用支付宝的 API

前端模板文件 `.\templates\user_center_order.html` 使用 `$('.oper_btn').click()` 接收 `OrderPayView` 的返回地址，跳转到支付宝的支付页面（即使用了支付宝的 API）

#### 订单结果查询

没有使用支付宝自己的 API `return_url` 或 `notify_url` 来访问网站告诉刚才那笔交易的交易结果，而是网站自己去查询 `alipay.trade.query`

前端模板文件 `.\templates\user_center_order.html` 使用 `window.open(data.pay_url)` 让用户跳转到支付宝的支付页面后，立马发送 Ajax 请求，去查询该订单的支付状态，查询地址为 `/order/check`

开始编写视图文件 `.\apps\order\views.py` 中的 `CheckPayView`，然后增加路由规则

#### 评论功能

修改前端模板文件 `.\templates\user_center_order.html`，使用 JS 控制分别显示「去支付/去评价/已完成」

编写评论功能的视图➕路由➕模板

然后修改模板文件 `.\templates\detail.html` 用 JS 实现商品简介和评论的点击切换显示事件，如下

``` javascript
$('#tag_detail').click(function () {
   $('#tag_comment').removeClass('active')
   $(this).addClass('active')
   $('#tab_detail').show()
   $('#tab_comment').hide()
})

$('#tag_comment').click(function () {
   $('#tag_detail').removeClass('active')
   $(this).addClass('active')
   $('#tab_detail').hide()
   $('#tab_comment').show()
})
```

#### 修改 TinyMCE 后台管理时的显示 bug 问题

修改项目配置文件 `settings.py`

``` python
TINYMCE_DEFAULT_CONFIG = {
    # 'theme': 'advanced',
    'theme': 'silver',  # 使用这里面有的主题 \virtual_env\Lib\site-packages\tinymce\static\tinymce\themes
    ...
}
```
