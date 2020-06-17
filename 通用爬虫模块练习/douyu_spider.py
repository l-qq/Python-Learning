from selenium import webdriver
import time

"""
使用selenium爬取斗鱼所有直播
"""
class DouyuSpider:
    def __init__(self):
        super().__init__()
        self.start_url = "https://www.douyu.com/directory/all"
        self.driver = webdriver.Chrome()

    def get_content_list(self):
        li_list = self.driver.find_elements_by_xpath("//ul[@class='layout-Cover-list']/li")
        content_list = []
        for li in li_list:
            item = {}
            item["room_image"] = li.find_element_by_xpath(".//img").get_attribute("src")
            item["room_title"] = li.find_element_by_xpath(".//h3[@class='DyListCover-intro']").get_attribute("title")
            item["room_cate"] = li.find_element_by_xpath(".//span[@class='DyListCover-zone']").text
            item["room_author"] = li.find_element_by_xpath(".//h2[@class='DyListCover-user']").text
            item["room_watch"] = li.find_element_by_xpath(".//span[@class='DyListCover-hot']").text
            print(item)
            content_list.append(item)
        # 获取下一页元素
        next_url = self.driver.find_elements_by_xpath("//span[@class='dy-Pagination-item-custom' and text()='下一页']")
        next_url = next_url[0] if len(next_url)>0 else None
        return content_list, next_url

    def save_content_list(self, content_list):
        pass

    def run(self):
        # 1.start_url
        # 2.发送请求获取响应
        self.driver.get(self.start_url)
        time.sleep(10)
        # 3.提取数据，提取下一页按钮
        content_list, next_url = self.get_content_list()
        # 4.保存数据
        self.save_content_list(content_list)
        # 5.点击下一页，循环
        while next_url is not None:
            next_url.click()
            time.sleep(10)  # 延时确保新打开的页面充分加载完毕，然后再开始进行页面分析
            content_list, next_url = self.get_content_list()
            self.save_content_list(content_list)

if __name__ == "__main__":
    douyu = DouyuSpider()
    douyu.run()