import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import re
import configparser
import select
from selenium.webdriver.edge.options import Options

delete_button=[]
remove_button=[]

config = configparser.ConfigParser()
config.read("config.ini")
username = config.get('Advanced Scan Settings','scraping_username')
password = config.get('Advanced Scan Settings','scraping_password')

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
                # Try creating an Edge webdriver
                options = Options()
                options.use_chromium = True
                options.add_argument("headless")
                return webdriver.Edge(options=options)
            except:
                raise Exception("No suitable browser found")

edgeBrowser = create_webdriver()

driver = edgeBrowser
url = "https://chmsdemo.greenfossil.com/"
driver.get(url)
def login():
    input_text_loginid = driver.find_element(By.ID,'loginId')
    input_text_password = driver.find_element(By.ID,'password')
    input_text_loginid.send_keys(username)
    input_text_password.send_keys(password,Keys.RETURN)

def delete():
    page_source = driver.page_source
    soup = BeautifulSoup(page_source,features="html.parser")
    button = soup.find_all('form')
    print("button123"+str(button))

    with open('before_delete.txt','r') as deleteFile:
        line = deleteFile.read()
        name = line.strip().split('///')
        name.pop(-1)

    if button:
        for form in button:
            if str(form) in str(name):
                print('i already existed in the first place')
            else:
                print(form)
                action_value = form['action']
                
                if action_value != "":
                    if "relationship" in action_value:
                        xpath ='//form[@action="'+str(action_value)+'"]//button[@class="ui right floated mini negative button deleteBtn"]'
                    else:
                        xpath = '//form[@action="'+str(action_value)+'"]/button[@class="ui right floated icon tertiary button red deleteBtn"]'
                    
                    print(form)
                    try:
                        deletebutton=driver.find_element(By.XPATH,xpath)
                        deletebutton.click()
                    except:
                        print("Skipping")

                    # class="ui delete modal front transition visible active"
                    page_source = driver.page_source
                    soup1 = BeautifulSoup(page_source,features="html.parser")
                    yes = driver.find_element(By.CSS_SELECTOR,".ui.basic.button.ok")
                    try:
                        yes.click()
                    except:
                        print("Skipping")

def image():
    page_source = driver.page_source
    soup = BeautifulSoup(page_source,features="html.parser")
    for item in soup.select("[type^='hidden']"):
        item.decompose()
    edit_image = soup.find('a',class_="button")
    edit_image="https://chmsdemo.greenfossil.com"+edit_image.get('href')
    driver.get(edit_image)
    del_photo = driver.find_element(By.ID,"deletePhoto")
    del_photo.click()
    yes_del = driver.find_element(By.CSS_SELECTOR,".ui.basic.button")
    yes_del.click()
    
def personal_details():
    with open('personal_details_text.txt','r') as deleteFile:
        line = deleteFile.read()
        name = line.strip().split('///')
        name.pop(-1)
    with open('dropdown.txt','r') as deleteFile:
        line = deleteFile.read()
        olddropdown = line.strip().split('///')
        olddropdown.pop(-1)
    for i in range(len(olddropdown)):
        if "Degree" in olddropdown[i]:
            new_name = olddropdown[i].replace("'",u"\u2019")
            olddropdown.pop(i)
            olddropdown.insert(i,new_name)
    print(olddropdown)
    personal_details = driver.find_element(By.CSS_SELECTOR,".large.edit.icon")
    personal_details.click()
    page_source = driver.page_source
    #using soup to change everything from hidden to not hidden
    soup = BeautifulSoup(page_source, features="html.parser")
    for item in soup.select("[type^='hidden']"):
        item.decompose()
    inputs = soup.find_all('input')
    inputfield=[]
    for tag in inputs:
        input = tag.get('name',None)
        if input is not None:
            inputfield.append(input)
        
    #using soup again to look for dropdown boxes
    soup2 = BeautifulSoup(page_source, features="html.parser")
    inputs2 = soup2.find_all(class_="selection")
    dropdowns = []
    for tag in inputs2:
        input2 = tag.get('class',None)
        if input2 is not None:
            dropdowns.append(input2)

    Selection=driver.find_elements(By.CLASS_NAME, "selection")

    #To click to make the choices visable 
    for num in range(len(Selection)):
        if Selection[num].is_displayed():
            #click to open selection field
            Selection[num].click()
            sleep(0.2)
            #find the first option
            print(str(olddropdown[num]))
            clcik=Selection[num].find_element(By.CSS_SELECTOR,'div[data-text="'+str(olddropdown[num])+'"]')
            print(clcik)
            #Select the first option
            clcik.click()
            sleep(1)
    print(name)
    for i in range(len(inputfield)):
        if inputfield[i] !='partialNricOpt':
            payload = name[i]
            sampleElement = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, inputfield[i])))
            sampleElement.clear()
            sampleElement.send_keys(f"{payload}")
            sleep(1)
        else:
            payload = name[i]
            sampleElement = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, inputfield[i])))
            sampleElement.send_keys(f"123A")
            sleep(1)

    #Submit the form to test payload
    submit=driver.find_element(By.CSS_SELECTOR,".ui.right.floated.primary.button")
    #Select the first option
    submit.click()
    sleep(5)
    
login()
delete()
# image()
personal_details()