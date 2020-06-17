import requests
from lxml import etree

"""
爬取糗事百科首页数据，使用xpath语法解析数据
"""
class QiubaiSpider:
    def __init__(self):
        super().__init__()
        self.url_temp = "https://www.qiushibaike.com/8hr/page/{}/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
        }

    def get_url_list(self):
        return [self.url_temp.format(i) for i in range(1,14)]

    def parse_url(self, url):
        print(url)
        response = requests.get(url, headers=self.headers)
        return response.content.decode()

    def get_content_list(self, html_str):  # 提取数据
        html = etree.HTML(html_str)
        div_list = html.xpath("//div[@class=\"recommend-article\"]/ul/li")  # 分组
        content_list = []
        for li in div_list:
            # 每个分组进行内容提取
            item = {}
            item["content"] = li.xpath("./div/a/text()")
            item["recmd"] = li.xpath(".//div[contains(@class, 'recmd-num')]/span/text()")
            item["author"] = li.xpath("./div/div/a/span/text()")
            item["img"] = li.xpath("./a/img/@src")
            content_list.append(item)
        return content_list

    def save_content_list(self, content_list):
        for i in content_list:
            print(i)
        print("假装保存完毕")

    def run(self):
        # 1.url_list
        url_list = self.get_url_list()
        # 2.遍历，发送请求，获取响应
        for url in url_list:
            html_str = self.parse_url(url)
            # 3.提取数据
            content_list = self.get_content_list(html_str)
            # 4.保存
            self.save_content_list(content_list)

if __name__ == "__main__":
    qiubai = QiubaiSpider()
    qiubai.run()