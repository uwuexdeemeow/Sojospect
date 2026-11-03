import scrapy

input_urls = []
test = 0

class TestSpider(scrapy.Spider):
    name = "robotstest"
    allowed_domains = ["chmsdemo.greenfossil.com"]
    #allowed_domains = ["amazon.com"]
    start_urls = ["https://chmsdemo.greenfossil.com/robots.txt"]
    #start_urls = ["https://www.amazon.com/robots.txt"]

    def parse(self, response):
       if(response.status != 200):
            print("Robots.txt page does not exist")
       else:
           print("Robots.txt does exist")