#importing all required libraries
import scrapy
from pathlib import Path
from scrapy.http import FormRequest
import configparser
from scrapy.crawler import CrawlerProcess
import os
import sys

if __name__ == "__main__":
    user_input = sys.argv[1]

#variables
input_urls = []
post_urls =[]
test = 0
base_url = user_input
if "https" in base_url:
    domain = str(base_url).replace("https://","")
else:
    domain = str(base_url).replace("http://","")
domain2 = domain.replace("/","")

#Setting the allowed domains
class TestSpider(scrapy.Spider):
    name = "input_urls"
    allowed_domains = [domain2]
    start_urls = [base_url+"login"]
    #Logining in to the system
    def parse(self, response):
        config = configparser.ConfigParser()
        config.read(self.config_file_path)
        username = config.get('Advanced Scan Settings','scraping_username')
        password = config.get('Advanced Scan Settings','scraping_password')
        injection = config.get('Advanced Scan Settings','scan_for_injection')
        if int(injection) ==1:
            return FormRequest.from_response(response, formdata={
                'loginId': username,
                'password': password
            }, callback=self.continue_scraping)
        else:
            return
    #Scraping the navigation bar and profile page for URLs to follow
    def continue_scraping(self, response):
        #clearing all the contents of the page
        file_to_open = open("input_fields.txt",'w')
        file_to_open.close()
        #scraping all the URLs in the navigation bar
        next_page = response.css('div.menu-items a.item::attr(href)').getall()
        #taking logout out so that the program does not crash
        next_page.pop(-1)
        #scraping all the URLs in the profile page
        profile_page = response.css('div.container a::attr(href)').getall()
        
        for i in range(len(profile_page)):
            next_page.append(profile_page[i])
            #yield response.follow(str(profile_page[i]),callback = self.scrap_new_page)
        print("Hello"+str(next_page))
        
        for i in range(len(next_page)):
            yield response.follow(str(next_page[i]),callback = self.scrap_new_page)
        
    #Scraping the page for further URLs and checking if the page has an input fields
    def scrap_new_page(self,response):
        #Checking for input fields
        input_fields = response.css('input').get()
        print(str(response)+'///'+str(input_fields))
        if input_fields is not None:
            #Appending the URLs with input fields into a file 
            with open('input_fields.txt','a') as testing:
                string1 = str(response).replace("<200 ","")
                string2 = string1.replace(">","")
                testing.write(string2+', ')
        #Scraping for more URLs within the page
        URL_in_page = response.css('div.container a::attr(href)').getall()
        if URL_in_page is not None:
            for i in range(len(URL_in_page)):
                yield response.follow(str(URL_in_page[i]),callback = self.scrap_new_page)
        return

if __name__ == "__main__":
    # Get the absolute path to the directory containing this script
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Get the absolute path to the parent directory of the script's directory
    parent_directory = os.path.dirname(script_directory)
    
    # Construct the absolute path to the config.ini file
    config_file_path = os.path.join(parent_directory, "config.ini")
    
    # Create a CrawlerProcess instance
    process = CrawlerProcess()

    # Add your spider to the process
    process.crawl(TestSpider, config_file_path=config_file_path)

    # Start the crawling process
    process.start()