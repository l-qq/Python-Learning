import requests

"""
访问百度贴吧网站并下载网页
"""
class TiebaSpider:
    def __init__(self, tieba_name):
        super().__init__()
        self.tieba_name = tieba_name
        self.url_temp = "https://tieba.baidu.com/f?kw="+tieba_name+"&ie=utf-8&pn={}"
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}

    def get_url_list(self):  # 构造url列表
        url_list = []
        for i in range(10):
            url_list.append(self.url_temp.format(i*50))
        return url_list

    def parse_url(self, url):  # 发送请求获取响应
        response = requests.get(url, headers=self.headers)
        return response.content.decode()

    def save_html(self, html_str, page_num):  # 保存html字符串
        file_path = "{}-第{}页.html".format(self.tieba_name, page_num)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_str)

    # 实现主要逻辑，爬取贴吧的页面并下载
    def run(self):
        # 1.构造url列表
        url_list = self.get_url_list()
        # 2.遍历发送请求，获取响应
        for url in url_list:
            html_str = self.parse_url(url)
            # 3.保存
            page_num = url_list.index(url)+1
            self.save_html(html_str, page_num)

if __name__ == "__main__":
    tieba_spider = TiebaSpider("迪丽热巴")
    tieba_spider.run()