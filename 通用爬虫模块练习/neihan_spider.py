import requests
import re
import json

"""
内涵段子官网数据爬取，并用正则表达式匹配
"""
class Neihan:
    def __init__(self):
        super().__init__()
        self.start_url = "http://neihanshequ.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
        }

    def parse_url(self, url):  # 发送请求
        response = requests.get(url, headers=self.headers)
        return response.content.decode()

    def get_first_page_content_list(self, html_str):  # 提取第一页的数据
        content_list = re.findall(r"<h1 class=\"title\">.*?<p>(.*?)</p>", html_str, re.S)
        max_time = re.findall("max_time: '(.*?)',", html_str)[0]  # 获取下一页的请求
        return content_list, max_time

    def save_content_list(self, content_list):  # 保存
        with open("neihan.txt", "a") as f:
            for content in content_list:
                f.write(json.dumps(content, ensure_ascii=False))

    def run(self):  # 实现主要逻辑
        # 1.start_url
        # 2.发送请求，获取响应
        html_str = self.parse_url(self.start_url)
        # 3.提取数据
        content_list, max_time = self.get_first_page_content_list(html_str)
        # 4.保存
        self.save_content_list(content_list)
        # 5.构造下一页url地址
        # 6.发送请求
        # 7.提取数据，提取max_time
        # 8.保存
        # 9.循环

if __name__ == "__main__":
    neihan = Neihan()
    neihan.run()