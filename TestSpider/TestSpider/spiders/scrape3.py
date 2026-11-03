import scrapy
from pathlib import Path
from scrapy.http import FormRequest

input_urls = []
test = 0
class TestSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["chmsdemo.greenfossil.com"]
    start_urls = ["https://chmsdemo.greenfossil.com/login"]

    def parse(self, response):
        return FormRequest.from_response(response, formdata={
            'loginId': 'U0000028',
            'password': 'password'
        }, callback=self.continue_scraping)

    def continue_scraping(self, response):
        # page = response.url.split("/")[-2]
        # filename = f'{page}.html'
        # Path(filename).write_bytes(response.body)
        # self.log(f'Saved file {filename}')

        next_page = response.css('div.menu-items a.item::attr(href)').getall()
        print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'+str(next_page))
        print(len(next_page))
        for i in range(len(next_page)):
            yield response.follow(str(next_page[i]),callback = self.scrap_new_page)
        print('asdfasdfasdfasdfasdf22423432421242134'+str(input_urls))


    def scrap_new_page(self,response):
        input_fields = response.css('div.field input').get()
        if input_fields is not None:
            # page = response.url.split("/")[-2]
            # filename = f'{page}.html'
            # Path(filename).write_bytes(response.body)
            # self.log(f'Saved file {filename}')
            input_urls.append(response)

        URL_in_page = response.css('div.container a::attr(href)').getall()
        #print('thisthisthisthisthisthishthis'+str(URL_in_page))
        if URL_in_page is not None:
            for i in range(len(URL_in_page)):
                yield response.follow(str(URL_in_page[i]),callback = self.scrap_new_page)
        # print(input_urls)

        return