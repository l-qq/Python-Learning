import requests
from lxml import etree
import threading
from queue import Queue

"""
爬取糗事百科首页数据，使用多线程技术
"""
class QiubaiSpider:
    def __init__(self):
        super().__init__()
        self.url_temp = "https://www.qiushibaike.com/8hr/page/{}/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
        }
        self.url_queue = Queue()
        self.html_queue = Queue()
        self.content_queue = Queue()

    def get_url_list(self):
        # return [self.url_temp.format(i) for i in range(1,14)]
        for i in range(1,14):
            self.url_queue.put(self.url_temp.format(i))

    def parse_url(self):
        while True:
            url = self.url_queue.get()
            print(url)
            response = requests.get(url, headers=self.headers)
            self.html_queue.put(response.content.decode())
            self.url_queue.task_done()

    def get_content_list(self):  # 提取数据
        while True:
            html_str = self.html_queue.get()
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
            # return content_list
            self.content_queue.put(content_list)
            self.html_queue.task_done()

    def save_content_list(self):
        while True:
            content_list = self.content_queue.get()
            for i in content_list:
                print(i)
            print("假装保存完毕")
            self.content_queue.task_done()

    def run(self):
        thread_list = []
        # 1.url_list
        t_url = threading.Thread(target=self.get_url_list)
        thread_list.append(t_url)
        # 2.遍历，发送请求，获取响应
        for i in range(20):  # 开启多个线程
            t_parse = threading.Thread(target=self.parse_url)
            thread_list.append(t_parse)
            # 3.提取数据
        for i in range(2):  # 开启多个线程
            t_html = threading.Thread(target=self.get_content_list)
            thread_list.append(t_html)
            # 4.保存
        t_save = threading.Thread(target=self.save_content_list)
        thread_list.append(t_save)
        for t in thread_list:
            t.setDaemon(True)  # 设置为守护线程，该线程不重要，主线程结束该线程就结束
            t.start()

        for q in [self.url_queue, self.html_queue, self.content_queue]:
            q.join()  # 让主线程的等待阻塞，等待队列的任务完成后再完成

        print("主线程完毕")

if __name__ == "__main__":
    qiubai = QiubaiSpider()
    qiubai.run()