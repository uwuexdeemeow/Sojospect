# import scrapy
# from pathlib import Path
# from scrapy.http import FormRequest
# from scrapy.exceptions import IgnoreRequest

# input_urls = []
# test = 0

# class TestSpider(scrapy.Spider):
#     name = "test"
#     allowed_domains = ["chmsdemo.greenfossil.com"]
#     start_urls = ["https://chmsdemo.greenfossil.com/login"]

#     def parse(self, response):
#         return FormRequest.from_response(response, formdata={
#             'loginId': 'u0000028',
#             'password': 'password'
#         }, callback=self.continue_scraping)

#     def continue_scraping(self, response):      
#         next_page = response.css('div.menu-items a.item::attr(href)').getall()
#         next_page.pop(10)
#         print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'+str(next_page))
#         print(len(next_page))
        
#         for i in range(len(next_page)):
#             yield response.follow(str(next_page[i]),callback = self.scrap_new_page)
#         #print('asdfasdfasdfasdfasdf22423432421242134'+str(input_urls))
        
        

#     def scrap_new_page(self,response):
#         input_fields = response.css('input').get()
#         if input_fields is not None:
#             # print('hello'+input_fields)
#             with open('test.txt','a') as testing:
#                 string1 = response.replace("<200 https://chmsdemo.greenfossil.com","")
#                 string2 = string1.replace(">","")
#                 testing.write(string2+',')


            
#         URL_in_page = response.css('div.container a::attr(href)').getall()
#         #print('thisthisthisthisthisthishthis'+str(URL_in_page))
    
#         if URL_in_page is not None:
#             for i in range(len(URL_in_page)):
#                 yield response.follow(str(URL_in_page[i]),callback = self.scrap_new_page)
#         print('asdfasdfasdfasdfasdf22423432421242134'+str(input_urls))
#         print(len(input_urls))
        
        
        










# import scrapy
# from pathlib import Path
# from scrapy.http import FormRequest

# input_urls = []
# post_urls =[]
# test = 0




# class TestSpider(scrapy.Spider):
#     name = "test"
#     allowed_domains = ["chmsdemo.greenfossil.com"]
#     start_urls = ["https://chmsdemo.greenfossil.com/login"]
#     # custom_settings = {
#     # #     'DEPTH_LIMIT': 4
#     #     'DUPEFILTER_CLASS': 'CustomDupeFilter'
#     # }

#     def parse(self, response):
#         return FormRequest.from_response(response, formdata={
#             'loginId': 'u0000028',
#             'password': 'password'
#         }, callback=self.continue_scraping)

    
#     def continue_scraping(self, response):
#         next_page = response.css('div.menu-items a.item::attr(href)').getall()
#         next_page.pop(-1)
#         #booking_page = next_page.pop(2)
#         print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'+str(next_page))
#         print(len(next_page))
#         #yield response.follow(str(booking_page),callback = self.scrap_booking_page)
#         #for i in range(len(next_page)):
#         yield response.follow(str(next_page[1]),callback = self.scrap_new_page)
#         #print('asdfasdfasdfasdfasdf22423432421242134'+str(input_urls))
        

#     def scrap_new_page(self,response):
#         input_fields = response.css('input').get()
#         if input_fields is not None:
#             if (response.request.method == 'GET'):
#                 input_urls.append(response)
#                 print('this is the GET list'+str(input_urls))
#             else:
#                 post_urls.append(response)
#                 print('this is the post list'+ str(post_urls))
            
    
#         URL_in_page = response.css('div.container a::attr(href)').getall()
        

#         print('thisthisthisthisthisthishthis'+str(URL_in_page))
#         if URL_in_page is not None:
#             for i in range(len(URL_in_page)):
#                 yield response.follow(str(URL_in_page[i]),callback = self.scrap_new_page)
#         print('asdfasdfasdfasdfasdf22423432421242134'+str(input_urls))
#         print(len(input_urls))
#         return










# #for presentation code snippets
# import scrapy
# from pathlib import Path
# from scrapy.http import FormRequest
# from scrapy.exceptions import IgnoreRequest

# input_urls = []
# test = 0

# class TestSpider(scrapy.Spider):
#     name = "test"
#     allowed_domains = ["chmsdemo.greenfossil.com"]
#     start_urls = ["https://chmsdemo.greenfossil.com/login"]

#     def parse(self, response):
#         return FormRequest.from_response(response, formdata={
#             'loginId': 'u0000028',
#             'password': 'password'
#         }, callback=self.continue_scraping)
    
#     #Scraping the first page after login 
#     def continue_scraping(self, response):  
#         #Getting all the URLs in the navigation bar   
#         next_page = response.css('div.menu-items a.item::attr(href)').getall()
#         next_page.pop(10)
#         for i in range(len(next_page)):
#             #Following the URLs
#             yield response.follow(str(next_page[i]),callback = self.scrap_new_page)

#     #Scraping the new found URLS
#     def scrap_new_page(self,response):
#         #Looking for input fields in the webpage
#         input_fields = response.css('input').get()
#         #Appending those URLs with input fields to a list
#         if input_fields is not None:
#             input_urls.append(response)  
#         #Looking for further URLs in the page
#         URL_in_page = response.css('div.container a::attr(href)').getall()
#         #Checking if there are further URLs in the page
#         if URL_in_page is not None:
#             for i in range(len(URL_in_page)):
#                 #Following the new found URLS
#                 yield response.follow(str(URL_in_page[i]),callback = self.scrap_new_page)
#         return










#Directory bruteforcing
import scrapy
from pathlib import Path
from scrapy.http import FormRequest

directory_urls = []
test = 0

class TestSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["chmsdemo.greenfossil.com"]
    start_urls = ["https://chmsdemo.greenfossil.com/login"]
    handle_httpstatus_list = [403,404]

    def parse(self, response):
        return FormRequest.from_response(response, formdata={
            'loginId': 'u0000028',
            'password': 'password'
        }, callback=self.continue_scraping)

    def continue_scraping(self, response):
        myfile = open('Filenames_or_Directories_Common.txt','r')
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