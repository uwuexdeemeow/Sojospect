#Directory bruteforcing
import scrapy
from pathlib import Path
from scrapy.http import FormRequest

directory_urls = []
test = 0

class TestSpider(scrapy.Spider):
    name = "test1"
    allowed_domains = ["chmsdemo.greenfossil.com"]
    start_urls = ["https://chmsdemo.greenfossil.com/login"]
    handle_httpstatus_list = [403,404]

    def parse(self, response):
        return FormRequest.from_response(response, formdata={
            'loginId': 'u0000028',
            'password': 'password'
        }, callback=self.continue_scraping)

    def continue_scraping(self, response):
        myfile = open('Filenames_or_Directories_Common2.txt','r')
        newlist = []
        for line in myfile:
            line = '/'+ line
            newlist.append(line.replace("\n",""))       
        myfile.close()
        
        for i in range(len(newlist)):
            print('bbbbbbbbb'+str(i))
            yield response.follow(str(newlist[i]),callback = self.scrap_new_page)
            print('cccccccc'+str(newlist[i]))
        
        print(directory_urls)

    def scrap_new_page(self,response):
        if(response.status == 200):
            directory_urls.append(response)
            page = response.url.split("/")[-1]
            filename = f'{page}.html'
            print('aaaaaaaaaa'+filename)
            Path(filename).write_bytes(response.body)
            self.log(f'Saved file {filename}')
        print('from scrapnewpage'+str(directory_urls))
        
        return