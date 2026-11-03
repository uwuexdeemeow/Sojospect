import sys
import requests
import configparser
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib.parse import parse_qs
from urllib.parse import urlencode
from seleniumwire.utils import decode
from time import sleep
from os.path import dirname
sys.path.append(dirname(dirname(f'{__file__}')))
# from v2.yaml_vuln import vuln_extract
from scripts.sql_errors import sql_error_check


chrome_options = Options()

# Create a new instance of the Selenium Wire WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def login(username, password) :
    login_info = {"loginId":username, "password":password}
    response = requests.post("https://chmsdemo.greenfossil.com/authenticate", data=login_info)
    session_cookie = response.cookies
    return session_cookie


def injection(endpoint, params) : # params - input field's id in dict

    print(f"Injecting into : {endpoint}")
    for payload in payload_list :
        for key in params.keys() :
            params[key] = payload

        response = requests.post(endpoint, data=params)
        
        # response = requests.post(endpoint, cookies=session_cookie, data=params)
        print(f"Payload injected : {params}")
        resp_in_text = response.text
        input(resp_in_text)
        print('\n')

        result = sql_error_check(resp_in_text, error_xml_file)
    return result

# Define a request interceptor function
def my_request_interceptor(request):
    # Do something with the intercepted request
    if request.body : # check if there is params

        # print(f"Endpoint : {request.url}") # endpoint
        # print(f"{request.headers['Content-Type']}")
        print(f"body : {request.body}, type : {type(request.body)}")
        body_in_string = (request.body).decode('utf-8')
        params = {key: value[0] if len(value) == 1 else value for key, value in parse_qs(body_in_string).items()}
        

        result = injection(request.url, params)

        if result != -1 :
            vuln_endpoint = {"Endpoint" : request.url, "Vulnerability" : result}
            affected_url.append(vuln_endpoint)


config = configparser.ConfigParser()
config.read("config.ini")
username = config.get('Advanced Scan Settings','scraping_username')
password = config.get('Advanced Scan Settings','scraping_password')
filename = config.get('Advanced Scan Settings', 'mapped_file')
scan_for_sql = config.get('Advanced Scan Settings','scan_for_sql') # check name in config.ini later

# session_cookie = login(username, password)
# if len(session_cookie) == 0 :
#     print("Username/Password incorrect.")
#     sys.exit()

error_xml_file = 'scripts/errors.xml'
# put sql payloads into list
payloadfile='sqlpayload.txt'
text_file = open(payloadfile, "r")
payload_list = text_file.read().split('\n')
text_file.close()
print(payload_list)


affected_url = []

# Set the request interceptor
driver.request_interceptor = my_request_interceptor


# # Set the response interceptor
# driver.response_interceptor = my_response_interceptor


# Make requests
# driver.scopes=['chmsdemo.greenfossil.com']
# driver.get('https://chmsdemo.greenfossil.com/')
driver.scopes=['demo.testfire.net']
driver.get("https://demo.testfire.net/")

sleep(100000) # Long sleep, if not browser will close try to fix this

