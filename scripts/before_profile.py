import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import re
import configparser

input_urls = []
delete_button = []
test_input = 'This is a test'

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

edgeBrowser = create_webdriver()

driver = edgeBrowser
base_url = "https://chmsdemo.greenfossil.com/"
driver.get(base_url)

def login():
    config = configparser.ConfigParser()
    config.read("config.ini")
    username = config.get('Advanced Scan Settings','scraping_username')
    password = config.get('Advanced Scan Settings','scraping_password')
    input_text_loginid = driver.find_element(By.ID,'loginId')
    input_text_password = driver.find_element(By.ID,'password')
    input_text_loginid.send_keys(username)
    input_text_password.send_keys(password,Keys.RETURN)

def del_icon():
    wait = WebDriverWait(driver, 10)
    page_source = driver.page_source
    #using soup to change everything from hidden to not hidden
    soup = BeautifulSoup(page_source, features="html.parser")
    file_to_open = open("before_delete.txt",'w')
    file_to_open.close()
    ui_cards = soup.find_all(class_ = 'ui two doubling cards')
    # print(ui_cards)
    for card in ui_cards:
        links = card.find_all("form")
        if links is not None:
            for i in links:
                with open('before_delete.txt','a') as testing:
                    testing.write(str(i)+"///")
                    
    ui_cards = soup.find_all(class_ = 'ui cards')
    # print(ui_cards)
    for card in ui_cards:
        header = card.find(class_="ui brand dividing header")
        # if header.text == 'Contacts':
        #print(header.text)
        links = card.find_all("form")
        for i in links:

            with open('before_delete.txt','a') as testing:
                testing.write(str(i)+"///")
        print(links)
        print(len(links))

def input_field():
    file_to_open = open("personal_details_text.txt",'w')
    file_to_open.close()
    personal_details = driver.find_element(By.CSS_SELECTOR,".large.edit.icon")
    personal_details.click()
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, features="html.parser")
    for item in soup.select("[type^='hidden']"):
        item.decompose()
    inputs = soup.find_all('input')
    inputfield=[]
    for tag in inputs:
        input = tag.get('name',None)
        if input is not None:
            inputfield.append(input)
    for i in inputfield:
        sampleElement = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, i)))
        value = sampleElement.get_attribute('value')
        print(value)
        with open('personal_details_text.txt','a') as testing:
            testing.write(str(value)+"///")

    file_to_open = open("dropdown.txt",'w')
    file_to_open.close()
    #using soup again to look for dropdown boxes
    soup2 = BeautifulSoup(page_source, features="html.parser")
    inputs2 = soup2.find_all(class_="selection")

    for tag in inputs2:
        text = tag.find(class_="text")
        with open('dropdown.txt','a') as testing:
            text1 = text.getText()
            print(text1)
            if u"\u2019" in text1:
                text1 = text1.replace(u"\u2019","'")
            testing.write(str(text1)+"///")

login()
del_icon()
input_field()

