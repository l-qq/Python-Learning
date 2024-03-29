from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from celery_tasks.tasks import send_register_active_email
from django_redis import get_redis_connection
import re
from user.models import User, Address
from utils.mixin import LoginRequiredMixin
from goods.models import GoodsSKU


# Create your views here.

# /user/register
def register(request):
    """ 显示注册页面 """
    if request.method == "GET":
        return render(request, "register.html")  # 显示注册页面
    else:
        """ 进行注册处理 """
        # 接收数据
        username = request.POST.get("user_name")
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get("allow")

        # 进行数据校验
        if not all([username, password, email]):
            return render(request, "register.html", {"errmsg": "数据不完整"})
        if not re.match(r"^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
            return render(request, "register.html", {"errmsg": "邮箱不正确"})
        if allow != "on":
            return render(request, "register.html", {"errmsg": "请同意协议"})

        # 检查用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, "register.html", {"errmsg": "用户名已存在"})

        # 进行业务处理：进行用户注册
        """ user = User()
        user.username = username
        user.password = password
        ... 传统的业务处理方法
        user.save()
        """
        user = User.objects.create_user(username, email, password)  # 使用Django的认证系统
        user.is_active = 0  # 不让Django自动帮我们激活该账号，避免Django自动让is_active=1
        user.save()

        # 返回应答
        return redirect(reverse("goods:index"))  # url反向解析，格式为<应用名字:url名字>

# def register_handle(request):
#     """ 进行注册处理 """
#     # 接收数据
#     username = request.POST.get("user_name")
#     password = request.POST.get('pwd')
#     email = request.POST.get('email')
#     allow = request.POST.get("allow")

#     # 进行数据校验
#     if not all([username, password, email]):
#         return render(request, "register.html", {"errmsg": "数据不完整"})
#     if not re.match(r"^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
#         return render(request, "register.html", {"errmsg": "邮箱不正确"})
#     if allow != "on":
#         return render(request, "register.html", {"errmsg": "请同意协议"})

#     # 检查用户名是否重复
#     try:
#         user = User.objects.get(username=username)
#     except User.DoesNotExist:
#         user = None
#     if user:
#         return render(request, "register.html", {"errmsg": "用户名已存在"})

#     # 进行业务处理：进行用户注册
#     """ user = User()
#     user.username = username
#     user.password = password
#     ... 传统的业务处理方法
#     user.save()
#     """
#     user = User.objects.create_user(username, email, password)  # 使用Django的认证系统
#     user.is_active = 0  # 不让Django自动帮我们激活该账号，避免Django自动让is_active=1
#     user.save()

#     # 返回应答
#     return redirect(reverse("goods:index"))  # url反向解析，格式为<应用名字:url名字>

# /user/register
class RegisterView(View):
    """ 注册类视图，实现展示注册页和进行注册处理 """
    def get(self, request):
        """ 显示注册页面，处理GET请求 """
        return render(request, "register.html")

    def post(self, request):
        """ 进行注册处理，处理POST请求 """
        # 接收数据
        username = request.POST.get("user_name")
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get("allow")

        # 进行数据校验
        if not all([username, password, email]):
            return render(request, "register.html", {"errmsg": "数据不完整"})
        if not re.match(r"^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
            return render(request, "register.html", {"errmsg": "邮箱不正确"})
        if allow != "on":
            return render(request, "register.html", {"errmsg": "请同意协议"})

        # 检查用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, "register.html", {"errmsg": "用户名已存在"})

        # 进行业务处理：进行用户注册
        """ user = User()
        user.username = username
        user.password = password
        ... 传统的业务处理方法
        user.save()
        """
        user = User.objects.create_user(username, email, password)  # 使用Django的认证系统
        user.is_active = 0  # 不让Django自动帮我们激活该账号，避免Django自动让is_active=1
        user.save()

        # 发送激活邮件，包含激活链接http://127.0.0.1:8000/user/active/
        # 激活链接要包含用户的身份信息，并且身份信息需要加密签名（使用itsdangerous第三方库），避免被敌手猜测出来
        serializer = Serializer(settings.SECRET_KEY, 3600)  # 使用settings.py中的密钥创建一个加密对象
        info = {"confirm": user.id}
        token = serializer.dumps(info)  # 加密用户的信息
        # token = token.decode("utf8")

        # 发送邮件
        # subject = "天天生鲜欢迎信息"
        # message = '<h1>%s，欢迎注册会员</h1>点击链接激活账户</ br><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (username, token, token)
        # html_message = '</ br><h1>%s，欢迎注册会员</h1>点击链接激活账户</ br><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (username, token.decode("utf8"), token.decode("utf8"))
        # sender = settings.EMAIL_FROM
        # reciever = [email]
        # send_mail(subject, message, sender, reciever, html_message=html_message)
        send_register_active_email.delay(email, username, token.decode())

        # 返回应答
        return redirect(reverse("goods:index"))  # url反向解析，格式为<应用名字:url名字>

# user/active/<token>
class ActiveView(View):
    '''用户激活'''
    def get(self, request, token):
        '''进行用户激活'''
        # 进行解密，获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取待激活用户的id
            user_id = info['confirm']

            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')

# user/login
class LoginView(View):
    """ 用户登陆 """
    def get(self, request):
        """ 显示登录页面 """
        if "username" in request.COOKIES:  # 判断是否记住了用户名
            username = request.COOKIES.get("username")
            checked = "checked"
        else:
            username = ""
            checked = ""
        # 使用模板，渲染对应的登陆页面
        return render(request, "login.html", {"username": username, "checked": checked})

    def post(self, request):
        """ 登录校验 """
        # 接收数据
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        # 数据校验
        if not all([username, password]):
            return render(request, "login.html", {"errmsg": "数据不完整"})
        # 业务处理：登录校验
        """
        User.objects.get(username=username, password=password)
        传统的业务（认证）处理方法
        """
        user = authenticate(username=username, password=password)  # 使用Django自带的认证功能
        if user is not None:
            if user.is_active:  # 判断用户是否激活
                login(request, user)  # 使用Django自带的session框架记录功能，记录用户的登录状态
                # 获取登陆后需要跳转的地址，默认跳转首页
                next_url = request.GET.get("next", reverse('goods:index'))
                response = redirect(next_url)
                # 判断是否需要记住用户名
                remember = request.POST.get("remember")
                if remember == "on":
                    response.set_cookie("username", username, max_age=7*24*3600)
                else:
                    response.delete_cookie("username")
                return response
            else:
                return render(request, "login.html", {"errmsg": "账户未激活"})  # 这句有bug，不会执行该句
        else:
            return render(request, "login.html", {"errmsg": "用户名或密码错误"})
        # 返回应答

# /user/logout
class LogoutView(View):
    '''退出登录'''
    def get(self, request):
        '''退出登录'''
        # 清除用户的session信息
        logout(request)
        # 跳转到首页
        return redirect(reverse('goods:index'))

# /user
class UserInfoView(LoginRequiredMixin, View):
    """ 用户中心--信息页 """
    def get(self, request):
        '''显示'''
        # Django会给request对象添加一个属性request.user
        # 如果用户未登录->user是AnonymousUser类的一个实例对象
        # 如果用户登录->user是User类的一个实例对象
        # request.user.is_authenticated()

        # 获取用户的个人信息
        user = request.user
        address = Address.objects.get_default_address(user)

        # 获取用户的历史浏览记录
        # from redis import StrictRedis
        # sr = StrictRedis(host='172.16.179.130', port='6379', db=9)
        con = get_redis_connection('default')

        history_key = 'history_%d'%user.id  # 拼接出redis中的key

        # 获取用户最新浏览的5个商品的id
        sku_ids = con.lrange(history_key, 0, 4) # [2,3,1]

        # 从数据库中查询用户浏览的商品的具体信息
        # goods_li = GoodsSKU.objects.filter(id__in=sku_ids)
        #
        # goods_res = []
        # for a_id in sku_ids:
        #     for goods in goods_li:
        #         if a_id == goods.id:
        #             goods_res.append(goods)

        # 遍历获取用户浏览的商品信息
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        # 组织上下文
        context = {'page':'user',
                   'address':address,
                   'goods_li':goods_li}

        # 除了你给模板文件传递的模板变量之外，django框架会把request.user也传给模板文件
        return render(request, 'user_center_info.html', context)
        # return render(request, "user_center_info.html", {"page": "user"})  # 使用page变量传递到前端控制class样式

# /user/order
class UserOrderView(LoginRequiredMixin, View):
    """ 用户中心--订单页 """
    def get(self, request):
        return render(request, "user_center_order.html", {"page": "order"})

# /user/address
class AddressView(LoginRequiredMixin, View):
    """ 用户中心--地址页 """
    def get(self, request):
        '''显示'''
        # 获取登录用户对应User对象
        user = request.user

        # 获取用户的默认收货地址
        # try:
        #     address = Address.objects.get(user=user, is_default=True) # models.Manager
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        address = Address.objects.get_default_address(user)

        # 使用模板
        return render(request, 'user_center_site.html', {'page':'address', 'address':address})

    def post(self, request):
        '''地址的添加'''
        # 接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 校验数据
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg':'数据不完整'})

        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg':'手机格式不正确'})

        # 业务处理：地址添加
        # 如果用户已存在默认收货地址，添加的地址不作为默认收货地址，否则作为默认收货地址
        # 获取登录用户对应User对象
        user = request.user

        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None

        address = Address.objects.get_default_address(user)

        if address:
            is_default = False
        else:
            is_default = True

        # 添加地址
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)

        # 返回应答,刷新地址页面
        return redirect(reverse('user:address')) # get请求方式