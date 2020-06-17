from selenium import webdriver
import time
import requests

"""
使用selenium模拟登录豆瓣网
"""
# 实例化一个浏览器，使用chrome浏览器
driver = webdriver.Chrome()

# 发送请求
driver.get("https://www.douban.com")
driver.switch_to.frame(0)  # 1.用frame的index来定位，第一个是0

driver.find_element_by_class_name("account-tab-account").click()

# 用户名和密码
driver.find_element_by_id("username").send_keys("haha")
driver.find_element_by_id("password").send_keys("haha")

""" # 识别验证码
image_url = driver.find_element_by_id("captcha_image").get_attributes("src")
image_content = requests.get(image_url).content
image_code = identify(image_content)  # 使用云打码识别验证码

# 输入验证码
driver.find_element_by_id("captcha_field").send_keys(image_code) """

# 登录
driver.find_element_by_class_name("account-form-field-submit ").click()

# 获取cookie
cookies = driver.get_cookies()
print(cookies)
print("*"*100)
cookies = {i["name"]:i["value"] for i in cookies}  # 将cookies列表转换为requests库可以使用的字典形式
print(cookies)

# 退出浏览器
time.sleep(3)
driver.close()
driver.quit()