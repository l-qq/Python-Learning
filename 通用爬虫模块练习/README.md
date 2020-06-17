# 简单爬虫练习

## 快速开始

``` powershell
pip install virtualenv
pip install virtualenvwrapper-win
mkvirtualenv pachong  # 创建名为pachong的虚拟环境，默认位置为用户\~\Envs
cmd /k workon pachong  # 开启pachong虚拟环境，由于powershell执行没反应，所以需要使用cmd激活虚拟环境
deactivate  # 离开虚拟环境
rmvirtualenv pachong  # 删除虚拟环境
```

> [workon command doesn't work in Windows PowerShell to activate virtualenv](https://stackoverflow.com/questions/38944525/workon-command-doesnt-work-in-windows-powershell-to-activate-virtualenv)

``` powershell
pip install requests  # 安装第三方库
```

## 学习笔记

### Requests 库

Requests 模块的使用，可以在 python 交互环境下 `import requests` 后执行验证：

``` python
url = "https://www.baidu.com"
response = requests.get(url)  # 使用GET请求访问网站
response.text  # str类型字符串
response.content  # bytes类型数据
response.content.decode("utf-8")  # 对返回的bytes数据解码
response.status_code
response.request.headers
response.headers
requests.get(url, headers=headers, params=kw)  # 发送带header/参数的请求，格式为字典，例如headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
requests.post(url, data=data)  # 发送POST请求，data格式为字典
requests.post(url, data=data, proxies=proxies)  # 使用代理，proxies格式为字典，例如proxies={"http":"http://127.0.0.1:1080", "https":"https://127.0.0.1:1080"}
# 使用session
session = requests.session()  # 实例化一个session
response = session.get(url, headers=headers)  # 使用session请求url并让session获得cookie，为后续请求做好铺垫
requests.utils.unquote("https://www.baidu.com/s?wd=%E4%BD%A0%E5%A5%BD")  # URL解码
requests.utils.quote("https://www.baidu.com/s?wd=你好")  # URL编码
response.cookies
requests.utils.dict_from_cookiejar  # 把cookie对象转化为字典
response = requests.get(url, verify=False)  # 不验证SSL证书
response = requests.get(url, timeout=10)  # 设置超时
```

### json 库

常用方法

``` python
import json  # 导入json标准库
json.loads(json_str)  # 将json字符串转为python字典
json.dumps(dict_ret)  # 将python字典转为json字符串
```

### 正则表达式

常用方法

``` python
imoport re  # 导入标准库
str = "abc123ba1"  # 待匹配字符串
re.match("b\w1", str)  # 从字符串头部开始查找匹配
re.search("b\w1", str)  # 找一个
re.findall("b\w1", str)  # 找所有
re.sub("\d", "-", str)  # 替换
pattern = re.compile("b\w1")
pattern = re.compile(".", re.S)  # 让.可以匹配到换行符
# 编译正则表达式后再进行匹配
pattern.match(str)
pattern.search(str)
pattern.findall(str)
pattern.sub("-", str)
```

Q：如何非贪婪的匹配？

A：正则表达式中在 `+` 或 `.` 后面加 `?`

Q：`re.findall(r"a.*bc", "a\nbc", re.DOTALL)` 和 `re.findall(r"a(.*)bc", "a\nbc", re.DOTALL)` 的区别

A：

``` powershell
>>> re.findall(r"a.*bc", "a\nbc", re.DOTALL)
['a\nbc']
>>> re.findall(r"a(.*)bc", "a\nbc", re.DOTALL)  # 能够返回分组内容，起到定位的作用
['\n']
>>>
```

### Xpath

语法：

``` xpath
/html/head/title/text()  # 获取根节点下html节点下head节点下title节点下的文本
/html/head/link/@href  # 获取根节点下html节点下head节点下所有link节点的href属性值
//ul[@id="detail-list"]  # 选择所有id为detail-list的ul节点，//表示不考虑路径位置，选择当前选中节点下的所有ul
a//text()  # 获取a标签下所有文本
//a[text()="下一页"]  # 选择文本为“下一页”三个字的a标签
```

``` powershell
pip install lxml  # 安装第三方库
```

使用入门：

``` python
from lxml import etree
str = "<html><body><a>haha</a>"
html = etree.HTML(str)  # 将字符串转换为element对象
print(etree.tostring(html).decode())  # lxml可以自动修复代码不规范的HTML
html.xpath("/html/body/a")  # 使用element对象的xpath方法
```

### Selenium 和 PhantomJS

``` powershell
pip install selenium  # 虚拟环境中安装该测试工具，可以用它控制浏览器
```

使用入门

``` python
from selenium import webdriver
driver = webdriver.Chrome()  # 实例化一个浏览器，使用chrome浏览器
driver.set_window_size(1920, 1080)  # 设置窗口大小
driver.maximize_window()  # 最大化窗口
driver.get("https://www.baidu.com")
driver.find_element_by_id("kw").send_keys("haha")  # 元素定位及输入框输入数据
driver.save_screenshot("./baidu.png")  # 当使用PhantomJS无界面浏览器时使用截屏查看浏览器结果
cookies = driver.get_cookies()
driver.switch_to.frame("login_frame")  # 切换到frame
driver.quit()  # 退出浏览器
```

> [使用python selenium時關於chromedriver的小問題](https://medium.com/@Epicure1709/%E4%BD%BF%E7%94%A8python%E7%9A%84selenium%E6%99%82%E9%81%87%E5%88%B0%E7%9A%84%E4%B8%80%E4%BA%9B%E5%B0%8F%E5%95%8F%E9%A1%8C-7fb5de198ff7)
