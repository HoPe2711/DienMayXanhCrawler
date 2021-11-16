## Giới thiệu
- Đây là chương trình sử dụng Scrapy và Selenium để thu thập 6000 thông tin và nhận xét của sản phẩm từ trang https://www.dienmayxanh.com/

### Cài đặt:

    conda install -c conda-forge scrapy
    conda install -c conda-forge protego
    conda install -c conda-forge selenium  

Tải chromedriver + chrome cùng phiên bản để sử dụng Selenium


    DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0',
    }
    FEED_EXPORT_ENCODING = 'utf-8'
 
Thay đổi user-agent bằng cách thêm đoạn code trên trong setting.py. Chạy code:

    
    scrapy crawl dmx -o data.json

### Dạng dữ liệu đầu ra của một sản phẩm:

    class Comment(scrapy.Item):
        User = scrapy.Field()
        Comment = scrapy.Field()
        Time = scrapy.Field()


    class CrawlerItem(scrapy.Item):
        STT = scrapy.Field()
        URL = scrapy.Field()
        TenSanPham = scrapy.Field()
        GiaTien = scrapy.Field()
        ChuyenMuc = scrapy.Field()
        ChitietSanPham = scrapy.Field()
        Nhanxet = scrapy.Field()

### Lấy link các danh mục sản phẩm

    def parse(self, response):
        a = 0
        for category in response.css("div.submenu aside a"):
            a += 1
            if a == 337:
                break
            url = self.start_urls[0] + category.css("a::attr(href)").get() + "?prv=-1"
            yield scrapy.Request(url=url, callback=self.parse_product_lists)

### Lấy link sản phẩm

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

Sử dụng selenium mô phỏng click "xem thêm" để load full page.


    elems = self.driver.find_elements_by_css_selector("ul.listproduct .main-contain")
    links = [elem.get_attribute('href') for elem in elems]
    self.driver.close()
    for url in links:
        yield scrapy.Request(url=url, callback=self.parse_product)

Lấy link của từng sản phẩm trong trang.

### Lấy dữ liệu sản phẩm

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

### Kết quả:
- Chương trình chạy xong thu được file dữ liệu data.json, sau đó format lại thành output.txt.
- Dữ liệu thu được hơn 6300 sản phẩm.
- Do máy tính hơi cùi nên thời gian thu thập mất gần 2h.
