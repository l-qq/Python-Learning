from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import send_mail
from celery_tasks.tasks import send_register_active_email
import re
from user.models import User


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
        return render(request, "login.html")