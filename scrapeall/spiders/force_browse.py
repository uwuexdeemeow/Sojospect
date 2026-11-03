import scrapy
from pathlib import Path
from scrapy.http import FormRequest
from scrapy.exceptions import IgnoreRequest

input_urls = []

class TestSpider(scrapy.Spider):
    name = "forcebrowse"
    allowed_domains = ["chmsdemo.greenfossil.com"]
    start_urls = ["https://chmsdemo.greenfossil.com/login"]


    def parse(self, response):
        return FormRequest.from_response(response, formdata={
            'loginId': 'admin',
            'password': 'password'
        }, callback=self.continue_scraping)

    def continue_scraping(self, response):
        next_page = response.css('div.menu-items a.item::attr(href)').getall()
        next_page.pop(-1)
        print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'+str(next_page))
        print(len(next_page))
        
        for i in range(len(next_page)):
            yield response.follow(str(next_page[i]),callback = self.scrap_new_page)
        #print('asdfasdfasdfasdfasdf22423432421242134'+str(input_urls))
        

    def scrap_new_page(self,response):
        URL_in_page = response.css('div.container a::attr(href)').getall()
        #print('thisthisthisthisthisthishthis'+str(URL_in_page))
        if URL_in_page is not None:
            for i in range(len(URL_in_page)):
                input_urls.append(URL_in_page[i])
                yield response.follow(str(URL_in_page[i]),callback = self.scrap_new_page)
        print('asdfasdfasdfasdfasdf22423432421242134'+str(input_urls))
        print(len(input_urls))
        
        return
