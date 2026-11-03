# import sys
# import requests
# import configparser
# import mysql.connector
# import json
# import threading
# from urllib.parse import urlparse
# from selenium.webdriver.chrome.options import Options
# from seleniumwire import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
# from urllib.parse import parse_qs
# from time import sleep
# from os.path import dirname
# sys.path.append(dirname(dirname(f'{__file__}')))
# from v2.yaml_vuln import vuln_extract


# def create_webdriver():
#     try:
#         # Try creating a Chrome webdriver
#         chrome_options = Options()
#         chrome_options.add_argument("headless")
#         return webdriver.Chrome(options=chrome_options)
#     except:
#         try:
#             # Try creating a Firefox webdriver
#             firefox_options = webdriver.FirefoxOptions()
#             firefox_options.add_argument("headless") 
#             return webdriver.Firefox(options=firefox_options)
#         except:
#             try:
#                 from selenium.webdriver.edge.options import Options as EdgeOptions
#                 # Try creating an Edge webdriver
#                 options = EdgeOptions()
#                 options.use_chromium = True
#                 options.add_argument("headless")
#                 return webdriver.Edge(options=options)
#             except:
#                 raise Exception("No suitable browser found")

# def __xss_attribute_check(body,payload_value):

#     if payload_value in body :
#         return True
#     return False

# def __xss_triggered_check(url, browser):
#     browser.get(url)
#     try:
#         WebDriverWait(browser, 3).until(EC.alert_is_present(),'Timed out')
#         alert = browser.switch_to.alert
#         alert.accept()
#         return True
#     except:
#         return False

# def injection(endpoint, params) : # params - input field's id in dict

#     if endpoint == url + "/authenticate" :
#         response = requests.post(endpoint, data=params)
#         session_cookie = response.cookies
#         cookie_storage.append(session_cookie)

#     print(f"Injecting into : {endpoint}")
    
#     # Injecting into GET req
#     if params == None : # if there is no params, it is GET Request
#         parsed_endpoint = urlparse(endpoint)
#         base_url = parsed_endpoint[0] + "://" + parsed_endpoint[1] + parsed_endpoint[2]
#         query = parsed_endpoint.query # replace query value with payload value later on     

#         xss = False
#         browser = create_webdriver()
#         for payload in payload_list :
#             modified_query = query.split('=')[0] + '=' + payload
#             url_to_send = base_url + "?" + modified_query
#             print(f"Payload injected into {endpoint}\n{payload}")

#             rxss = __xss_triggered_check(url_to_send, browser) # check if alert pops up on browser 
#             if not rxss : # if no alert pops up, check if there is proper validation/sanitization
#                 xss = __xss_attribute_check(browser.page_source, payload)
            
#             if rxss or xss :
#                 vuln_endpoint = {"Endpoint" : endpoint, "Accepted input" : payload}
#                 affected_urls.append(vuln_endpoint)
#                 break
#         browser.quit()
#         print("Done injecting...\n")
#         return
    
#     # Injecting into POST req
#     for payload in payload_list :
#         for key in params.keys() :
#             params[key] = payload

#         if cookie_storage :
#             response = requests.post(endpoint, data=params, cookies=cookie_storage[0])
#         else :
#             response = requests.post(endpoint, data=params)
#         sleep(1)
#         print(f"Payload injected into {endpoint}\n{params}")
        
#         xss = __xss_attribute_check(response.text, payload) # check if there is input validation/sanitization
#         if xss :
#             vuln_endpoint = {"Endpoint" : endpoint, "Accepted input" : payload}
#             affected_urls.append(vuln_endpoint)
#             break
#     print("Done injecting...\n")

# # Define a request interceptor function
# def my_request_interceptor(request):
#     # Do something with the intercepted request
#     if request.method == 'GET' and '?' in request.url :
#         params = None
#         parsed_endpoint = urlparse(request.url)
#         base_url = parsed_endpoint[0] + "://" + parsed_endpoint[1] + parsed_endpoint[2]
#         query = (parsed_endpoint.query).split('=')[0]
#         request.url = base_url + "?" + query + '='
#         if not any(request.url == x._args[0] for x in threads) : # check if the endpoint is alr going to be requested
#             thread = threading.Thread(target=injection ,args=(request.url, params))
#             threads.append(thread)

#     if request.method == 'POST' and request.headers['Content-Type'] == 'application/x-www-form-urlencoded' :
#     # if request.body : # check if there is params
#         # print(f"body : {request.body}, type : {type(request.body)}")
#         body_in_string = (request.body).decode('utf-8')
#         params = {key: value[0] if len(value) == 1 else value for key, value in parse_qs(body_in_string).items()}
        
#         if not any(request.url == x._args[0] for x in threads) : # check if the endpoint is alr going to be requested
#             thread = threading.Thread(target=injection, args=(request.url, params))
#             threads.append(thread)
        
# if __name__ == "__main__":
#     user_input = sys.argv[1] # this is the domain
#     scan_id = int(sys.argv[2])

# parsed_url = urlparse(user_input)
# scheme = parsed_url.scheme
# netloc = parsed_url.netloc
# url = scheme + "://" + netloc

# options = webdriver.ChromeOptions()
# options.add_experimental_option("detach", True)
# # Create a new instance of the Selenium Wire WebDriver
# driver = webdriver.Chrome(chrome_options=options, service=Service(ChromeDriverManager().install()))

# config = configparser.ConfigParser()
# config.read("config.ini")
# username = config.get('Advanced Scan Settings','scraping_username')
# password = config.get('Advanced Scan Settings','scraping_password')
# filename = config.get('Advanced Scan Settings', 'mapped_file')
# scan_for_sql = config.get('Advanced Scan Settings','scan_for_sql') # check name in config.ini later

# ######################## start of using selenium wire - pops up browser #######################
# # put xss payloads into list
# payloadfile='xsspayload.txt'
# text_file = open(payloadfile, "r")
# payload_list = text_file.read().split('\n')
# text_file.close()
# print(payload_list)

# threads = []
# affected_urls = []

# # Set the request interceptor
# driver.request_interceptor = my_request_interceptor

# # Make requests
# # driver.scopes=['chmsdemo.greenfossil.com']
# # driver.get('https://chmsdemo.greenfossil.com/')
# driver.scopes=[netloc]
# driver.get(url)

# DISCONNECTED_MSG = 'Unable to evaluate script: no such window: target window already closed\nfrom unknown error: web view not found\n'
# while True :
#     # print(driver.get_log('driver'))
#     if len(driver.get_log('driver')) == 0 :
#         sleep(1)
#         continue
#     if driver.get_log('driver')[-1]['message'] == DISCONNECTED_MSG:
#         break
#     sleep(1)

# print("Browser closed by user")

# cookie_storage = []
# for thread in threads :
#     thread.start()
#     thread.join()

# print("Affected endpoints:")
# print(affected_urls)

# if len(affected_urls) > 0 :
    
#     db_host = config.get('SQL Database', 'db_host')
#     db_user = config.get('SQL Database', 'db_user')
#     db_password = config.get('SQL Database', 'db_password')

#     db_connection = mysql.connector.connect(
#         host=db_host,
#         user=db_user,
#         password=db_password,
#         database="vulnerabilities"
#     )

#     db_cursor = db_connection.cursor()
#     cwe_id = "CWE-79"
#     # Insert a row into the MySQL table
#     vuln_yml = vuln_extract(cwe_id)
#     name = vuln_yml["name"]

#     insert_query = "INSERT INTO vulnerabilities (scan_id, vulnerability_name, vulnerability_id, url, additional_information) VALUES (%s, %s, %s, %s, %s)"
#     values = []
#     error_dict = json.dumps(affected_urls)
#     values.append([scan_id,name,cwe_id,user_input,error_dict])
#     db_cursor.executemany(insert_query, values)# Insert multiple rows together
#     db_connection.commit()

#     db_cursor.close()
#     db_connection.close()
