import requests
from bs4 import BeautifulSoup as soup
from urllib.parse import urljoin, urlsplit, urlparse
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
import json
import configparser
import sys
import multiprocessing
'''
#----------------------USAGE---------------------------

import json

with open('crawl.txt','r') as crawl_file:
    for i in (crawl_file.readlines()):
        data_dict = json.loads(i) #Data is now a dictionary from json loads
        #Examples to read data
        #To print all fields
        for key in data_dict.keys():
            if(key.startswith("Param_")):
                print(data_dict[key])
                #Accessing input field name
                print(data_dict[key]['name'])
                #Accessing input field id
                print(data_dict[key]['id'])
                #Accessing default value
                print(data_dict[key]['value'])
                #Accessing input type
                print(data_dict[key]['type'])
        #To get method
        print(data_dict['Method']) #Could be None

        #To get endpoint
        print(data_dict['Endpoint']) #Could be None

        #To get parent url
        print(data_dict['URL'])

'''

#Modify the sleep timing at your own risk

def login(edgeBrowser, UsernameField, PasswordField, username, password):

    inputUsername = WebDriverWait(edgeBrowser, 10).until(
    EC.presence_of_element_located((By.ID, UsernameField)))
    inputUsername.send_keys(username) 
    inputPassword = WebDriverWait(edgeBrowser, 10).until(
        EC.presence_of_element_located((By.ID, PasswordField)))
    inputPassword.send_keys(password)
    inputPassword.send_keys(Keys.ENTER)

def create_webdriver():
    try:
        # Try creating a Chrome webdriver
        chrome_options = Options()
        chrome_options.add_argument("headless")
        return webdriver.Chrome(options=chrome_options)
    except:
        try:
            # Try creating a Firefox webdriver
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.add_argument("headless") 
            return webdriver.Firefox(options=firefox_options)
        except:
            try:
                from selenium.webdriver.edge.options import Options as EdgeOptions
                # Try creating an Edge webdriver
                options = EdgeOptions()
                options.use_chromium = True
                options.add_argument("headless")
                return webdriver.Edge(options=options)
            except:
                raise Exception("No suitable browser found")

def crawl(script_dict,uncrawled_url,crawled_url,base_url,domain,cookies,filename):
    print(uncrawled_url[0])
    x = requests.get(uncrawled_url[0],cookies=cookies)
    page_soup = soup(x.content,"html.parser",from_encoding="iso-8859-1")
    for res in page_soup.find_all(href=True):
        link = res.get('href')
        link.replace("https://","")
        parsed_link = ""
        if(link.startswith("/")):
            parsed_link = urljoin(base_url,link)
        else:
            if(urlsplit(link).scheme not in ["https","http"]):
                parsed_link = "https://"+link
            else:
                parsed_link = link
        if(urlsplit(parsed_link).netloc == domain):
            #Throw the links into uncrawled if they don't exist in crawled
            if parsed_link not in crawled_url and parsed_link not in uncrawled_url:
                uncrawled_url.append(parsed_link)
    to_write_json = []
    get_dict = {
        "URL":uncrawled_url[0],
        "Endpoint":urlsplit(uncrawled_url[0]).path,
        "Method":"GET"
    }
    to_write_json.append(json.dumps(get_dict))
    #Obtain the forms
    for form in page_soup.find_all('form'):
        endpoint = None
        url = uncrawled_url[0]
        method = None
        if(not form.has_attr('action') or len(form['action'].strip())==0):
            #Empty
            endpoint = None
        else:
            endpoint = form['action']
        method = form['method'].upper() if form.has_attr('method') else None
        inputs = form.find_all('input')
        consolidate_dict = {
            "URL":url,
            "Endpoint":endpoint,
            "Method":method,
        }
        param_count = 0
        for row in inputs:
            param_count+=1
            consolidate_dict[f"Param_{param_count}"] = {} #Initialize dict
            consolidate_dict[f"Param_{param_count}"]["class"] = row["class"] if row.has_attr("class") else None
            consolidate_dict[f"Param_{param_count}"]["id"] = row["id"] if row.has_attr("id") else None
            consolidate_dict[f"Param_{param_count}"]["name"] = row["name"] if row.has_attr("name") else None
            consolidate_dict[f"Param_{param_count}"]["type"] = row["type"] if row.has_attr("type") else None
            consolidate_dict[f"Param_{param_count}"]["value"] = row["value"] if row.has_attr("value") else None
        json_data = json.dumps(consolidate_dict)
        to_write_json.append(json_data)
    with open(filename,"a+") as file:
        file.writelines(row +'\n' for row in to_write_json)
    #Obtain the scripts
    for script in page_soup.find_all('script'):
        if(not script.has_attr('src') or len(script['src'].strip())==0):
            continue
        else:
            url = script['src']
            script_dict["URL"] = url
        json_data = json.dumps(script_dict)
        to_write_json.append(json_data)
    crawled_url.append(uncrawled_url.pop(0))
    with open(filename,"a+") as file:
        file.writelines(row +'\n' for row in to_write_json)
    return uncrawled_url

if(__name__ == "__main__"):
    user_input = 'https://www.remove.bg/'

    config = configparser.ConfigParser()
    config.read('config.ini')
    username = config.get('Advanced Scan Settings','scraping_username')
    password = config.get('Advanced Scan Settings','scraping_password')
    filename = config.get('Advanced Scan Settings', 'mapped_file')

    csv_data = []
    base_url = user_input
    domain = urlsplit(base_url).netloc
    crawled_url = []
    manager = multiprocessing.Manager()
    uncrawled_url = manager.list()
    uncrawled_url.append(base_url)
    open('./crawl.txt', 'w').close() # CHANGE

    #Perform logging in to get cookie
    browser = create_webdriver()
    browser.get(base_url)
    initial_url = browser.current_url
    page_source = browser.page_source
    page_soup = soup(page_source, features="html.parser")
    temp_cookie_store = None

    for form in page_soup.find_all("form"):
        login_url = browser.current_url
        inputs = page_soup.find_all("input")
        UsernameField,PasswordField = None, None
        for field in inputs:
            identification = ""
            if field.get("name") != None:
                identification = "name"
            elif field.get("id") != None:
                identification = "id"
            if (field.get(identification) == "loginId" or field.get(identification) == "email"):
                UsernameField = field.get(identification)
            elif (field.get(identification) == "password"):
                PasswordField = field.get(identification)
        if UsernameField and PasswordField != None:
            login(browser, UsernameField, PasswordField, username, password)
            if (initial_url != browser.current_url):
                #login successful
                print("Login successful")
                uncrawled_url.append(browser.current_url)
                uncrawled_url.append(initial_url)
                temp_cookie_store = browser.get_cookies()
                print(browser.get_cookies())
            
        break
    browser.close()

    #set cookies
    cookies = {}
    if temp_cookie_store is not None:
        for row in temp_cookie_store:
            name = row['name']
            value = row['value']
            cookies[name] = value
    script_dict = {}
    uncrawled_url = crawl(script_dict,uncrawled_url,crawled_url,base_url,domain,cookies,filename)
    while True:
        #URL locating
        jobs = []
        if urlsplit(uncrawled_url[0]).path != '/logout':#Preventing logout
            p1 = multiprocessing.Process(target=crawl, args=(script_dict,uncrawled_url,crawled_url,base_url,domain,cookies,filename))
            p1.start()
            p1.join()
            jobs.append(multiprocessing.Process(target=crawl, args=(script_dict,uncrawled_url,crawled_url,base_url,domain,cookies,filename)))
            crawled_url.append(uncrawled_url.pop(0))
            jobs.append( multiprocessing.Process(target=crawl, args=(script_dict,uncrawled_url,crawled_url,base_url,domain,cookies,filename)))
            crawled_url.append(uncrawled_url.pop(0))
            jobs.append( multiprocessing.Process(target=crawl, args=(script_dict,uncrawled_url,crawled_url,base_url,domain,cookies,filename)))
            crawled_url.append(uncrawled_url.pop(0))
            jobs.append( multiprocessing.Process(target=crawl, args=(script_dict,uncrawled_url,crawled_url,base_url,domain,cookies,filename)))
            for pr in jobs:
                pr.start()
            for pr in jobs:
                pr.join()

        else:
            get_dict = {
                "URL":uncrawled_url[0],
                "Endpoint":urlsplit(uncrawled_url[0]).path,
                "Method":"GET"
            }
            to_write_json = [json.dumps(get_dict)]
            with open(filename,"a+") as file:
                file.writelines(row +'\n' for row in to_write_json)
            crawled_url.append(uncrawled_url.pop(0))
            if(len(uncrawled_url) == 0):
                break
            continue
        for job in jobs:
            job.join()
        if(len(uncrawled_url) == 0):
            break