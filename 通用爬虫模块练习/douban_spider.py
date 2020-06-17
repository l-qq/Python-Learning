import requests
import json
import pprint

"""
访问豆瓣手机版页面https://m.douban.com/tv/american获取所有美剧json数据
"""
class DoubanSpider:
    def __init__(self):
        self.url_temp = "https://m.douban.com/rexxar/api/v2/subject_collection/tv_american/items?start={}&count=18&loc_id=108288"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
            "Referer": "https://m.douban.com/tv/american",
            }

    def parse_url(self, url):  # 发送请求获取响应
        print(url)
        response = requests.get(url, headers=self.headers)
        return response.content.decode()

    def get_content_list(self, json_str):  # 提取数据，对json数据清洗
        dict_ret = json.loads(json_str)
        content_list = dict_ret["subject_collection_items"]
        return content_list, dict_ret["total"]

    def save_content_list(self, content_list):  # 保存数据
        with open("douban.txt", "a", encoding="utf-8") as f:
            for content in content_list:
                f.write(json.dumps(content, ensure_ascii=False))
                f.write("\n")  # 换行，每行对应一个美剧信息
        print("保存完毕")

    # 实现主要逻辑
    def run(self):
        num = 0
        total = 0
        while num < total+18:
            # 1.构造url
            url = self.url_temp.format(num)
            # 2.发送请求，获取响应
            json_str = self.parse_url(url)
            # 3.提取数据
            content_list, total = self.get_content_list(json_str)
            # 4.保存
            self.save_content_list(content_list)
            if len(content_list) < 18:
                break
            num += 18

if __name__ == "__main__":
    douban_spider = DoubanSpider()
    douban_spider.run()

    response = requests.get(
        "https://movie.douban.com/j/search_subjects?type=tv&tag=美剧&sort=recommend&page_limit=500&page_start=0",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
        })
    data = json.loads(response.content.decode())
    pprint.pprint(data["subjects"])