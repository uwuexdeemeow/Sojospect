# Imports
from bs4 import BeautifulSoup
import requests.exceptions
from urllib.parse import urlsplit
from urllib.parse import urlparse
from collections import deque
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.edge.options import Options
import pickle
import re
import configparser
import mysql.connector
import sys
import os
import time
import csv

# Functions
# Login Function
def login(edgeBrowser, UsernameField, PasswordField):
    # Wait until the selenium browser finds the element with the username input field id
    inputUsername = WebDriverWait(edgeBrowser, 10).until(
    EC.presence_of_element_located((By.ID, UsernameField)))
    # Input the username in the input field
    inputUsername.send_keys('systemadmin')
    # Wait until the selenium browser finds the element with the password input field id
    inputPassword = WebDriverWait(edgeBrowser, 10).until(
        EC.presence_of_element_located((By.ID, PasswordField)))
    # Input the password into the input field
    inputPassword.send_keys('theworkshop@5008AMK')
    # Send the enter key input to submit the form
    inputPassword.send_keys(Keys.ENTER)

# Function to create the selenium browser
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

################################################################ Code Starts Here ################################################################
# Declare variables
url = "https://chmsdemo.greenfossil.com" 
# Create a queue for all the new urls found
new_urls = deque([url])
processed_urls = set(new_urls)
local_urls = set()
foreign_urls = set()
broken_urls = set()
urls_with_input = set()
endpoint_urls = list()

# Remove any old cookies
if os.path.isfile("./cookie.pkl"):
    os.remove("./cookie.pkl")

try:
    while len(new_urls):
        # Move url from the queue to processed url set
        url = new_urls.popleft()
        processed_urls.add(url)
        print("Processing %s" % url)

        edgeBrowser = create_webdriver()
        # Check if there is cookies
        if os.path.isfile("./cookie.pkl"):
            cookies = pickle.load(open("./cookie.pkl", "rb"))
            if cookies is not None:
                edgeBrowser.get(login_url)
                for cookie in cookies:
                    edgeBrowser.add_cookie(cookie)
        try:
            # Browser will get navigated to the given URL
            edgeBrowser.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema):
            broken_urls.add(url)
            continue

        # Extract base url to resolve relative links
        parts = urlsplit(url)
        base = "{0.netloc}".format(parts)
        strip_base = base.replace("www.", "")
        base_url = "{0.scheme}://{0.netloc}".format(parts)
        path = url[:url.rfind('/')+1] if '/' in parts.path else url

        page_source = edgeBrowser.page_source
        soup = BeautifulSoup(page_source, features="html.parser")
        # Find all the links in the webpage
        for link in soup.find_all("a"):
            url_in_link = link.get("href")
            if(url_in_link == None):
                continue
            elif (url != edgeBrowser.current_url):
                local_urls.add(edgeBrowser.current_url)
            elif url_in_link.startswith('/'):
                local_link = base_url + url_in_link
                local_urls.add(local_link)
            elif strip_base in url_in_link:
                local_urls.add(url_in_link)
            else:
                foreign_urls.add(url_in_link)
        # Find all the forms in the webpage
        for form in soup.find_all("form"):
            input_fields = ""
            if (form.text.find("Login") != -1):
                login_url = edgeBrowser.current_url
                inputs = form.find_all("input")
                UsernameField,PasswordField = None, None
                for field in inputs:
                    identification = ""
                    if field.get("name") != None:
                        identification = "name"
                    elif field.get("id") != None:
                        identification = "id"
                    # Find the username and password input fields
                    if (field.get(identification) == "loginId" or field.get(identification) == "email"):
                        UsernameField = field.get(identification)
                    elif (field.get(identification) == "password"):
                        PasswordField = field.get(identification)
                    # Map the input fields
                    if field.get(identification) != None:
                        input_fields += field.get(identification) + ": " + field.get("type") + ", "
                    else:
                       input_fields += "No id or name, "
                if UsernameField and PasswordField != None:
                    # Map the form and webpage
                    urls_with_input.add(edgeBrowser.current_url)
                    thisDict = {"Url": edgeBrowser.current_url, "Method": form.get("method"), "Endpoint": form.get("action"), "Input Fields":  input_fields}
                    endpoint_urls.append(thisDict)
                    # Call the login function
                    login(edgeBrowser, UsernameField, PasswordField)
                    #Write the cookies out to a pkl file
                    with open('./cookie.pkl', 'wb') as f:
                        pickle.dump(edgeBrowser.get_cookies(), f)
                    if (url != edgeBrowser.current_url):
                        local_urls.add(edgeBrowser.current_url)
                break
            else:
                # Find all the input fields
                inputs = form.find_all("input")
                if inputs != None:
                # Map the input fields
                    for field in inputs:
                        if field.get("name") != None:
                            input_fields += field.get("name") + ": " + field.get("type") + ", "
                        elif field.get("id") !=None: 
                            input_fields += field.get("id") + ": " + field.get("type") + ", "
                        else:
                            input_fields += "No id or name, "
                else:
                    input_fields = "None"
                urls_with_input.add(edgeBrowser.current_url)
                # Map the form and webpage
                thisDict = {"Url": edgeBrowser.current_url, "Method": form.get("method"), "Endpoint": form.get("action"), "Input Fields":  input_fields}
                endpoint_urls.append(thisDict)
        # Add the urls found into the queue
        for url2 in local_urls:
            if (not url2 in new_urls and not url2 in processed_urls):
                new_urls.append(url2)
        edgeBrowser.close()
    for urls in urls_with_input:
        if urls in processed_urls:
            processed_urls.remove(urls)
    # Map the Urls without forms
    for urls in processed_urls:
        thisDict = {"Url": url, "Method": "No forms found", "Endpoint": "No forms found", "Input Fields":  "No forms found"}
        endpoint_urls.append(thisDict)
    # Declare headers for the csv file
    fieldnames = ["Url", "Method", "Endpoint", "Input Fields"]
    # Write out the mappings into a csv file
    with open("mapped.csv", "w", encoding="UTF-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(endpoint_urls)
except:
    for urls in urls_with_input:
        if urls in processed_urls:
            processed_urls.remove(urls)
    # Map the Urls without forms
    for urls in processed_urls:
        thisDict = {"Url": url, "Method": "No forms found", "Endpoint": "No forms found", "Input Fields":  "No forms found"}
        endpoint_urls.append(thisDict)
    # Declare headers for the csv file
    fieldnames = ["Url", "Method", "Endpoint", "Input Fields"]
    # Write out the mappings into a csv file
    with open("mapped.csv", "w", encoding="UTF-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(endpoint_urls)
