import time

import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from crawler_data.items import CrawlerItem, Comment


class DienMayXanhSpider(scrapy.Spider):
    name = "dmx"
    PATH = 'G:\\crawler_data\\crawler_data\\chromedriver.exe'
    allowed_domains = ["dienmayxanh.com"]
    start_urls = [
        "https://www.dienmayxanh.com",
    ]
    order_number = 1

    def parse(self, response):
        a = 0
        for category in response.css("div.submenu aside a"):
            a += 1
            if a == 337:
                break
            url = self.start_urls[0] + category.css("a::attr(href)").get() + "?prv=-1"
            yield scrapy.Request(url=url, callback=self.parse_product_lists)

    def parse_product_lists(self, response):
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=self.PATH)
        self.driver.get(response.url)
        while True:
            next = self.driver.find_element_by_xpath('//*[@id="categoryPage"]/div[@class="container-productbox"]/div[2]/a')
            time.sleep(3)
            try:
                next.click()
            except:
                break
        elems = self.driver.find_elements_by_css_selector("ul.listproduct .main-contain")
        links = [elem.get_attribute('href') for elem in elems]
        self.driver.close()
        for url in links:
            yield scrapy.Request(url=url, callback=self.parse_product)

    def parse_product(self, response):
        if response.status == 200:
            item = CrawlerItem()
            item['STT'] = self.order_number
            item['URL'] = response.url
            item['TenSanPham'] = response.css("h1 ::text").get()
            item['GiaTien'] = ' '.join(response.css("div.box-price p ::text").getall())
            item['ChuyenMuc'] = response.css("ul.breadcrumb a ::text").getall()
            dictionary = {}
            for key in response.css("div.parameter ul li"):
                dictionary[key.css("p ::text").get()] = key.css("span ::text").get()
            print(dictionary)
            item['ChitietSanPham'] = dictionary
            tmp = []
            comment_root = '//div[@id="comment"]/div[3]'
            for a in range(1, 21, 2):
                query = ''.join([comment_root, '/div[', str(a), ']'])
                comment = Comment()
                comment['User'] = response.xpath(''.join([query, '/strong/text()'])).get()
                if comment['User'] is not None:
                    comment['Comment'] = response.xpath(''.join([query, '/div[@class="infocom_ask"]/text()'])).get()
                    tmp1 = response.xpath(''.join([query, '/div[@class="relate_infocom"]/span/text()'])).extract()
                    comment['Time'] = tmp1[len(tmp1)-1]
                    tmp.append(comment)
            item['Nhanxet'] = tmp
            self.order_number += 1
            yield item
