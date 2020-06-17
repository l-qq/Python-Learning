from selenium import webdriver
import time

# 实例化一个浏览器，使用chrome浏览器
driver = webdriver.Chrome()
driver.maximize_window()

# 发送请求
driver.get("https://www.baidu.com")

# 元素定位
driver.find_element_by_id("kw").send_keys("haha")  # 输入框输入数据
driver.find_element_by_id("su").click()  # 点击按钮

# 获取cookie
cookies = driver.get_cookies()
print(cookies)
print("*"*100)
cookies = {i["name"]:i["value"] for i in cookies}  # 将cookies列表转换为requests库可以使用的字典形式
print(cookies)

# 获取网页字符串
print(driver.page_source)  # 返回的值是浏览器elements中的内容，包含了js执行后的结果等，不是response内容


# 退出浏览器
time.sleep(3)
driver.close()
driver.quit()