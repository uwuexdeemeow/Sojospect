# import sys
# import requests
# import configparser
# import mysql.connector
# import json
# import threading
# from timeit import default_timer as timer
# from datetime import timedelta
# from urllib.parse import urlparse
# from seleniumwire import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
# from urllib.parse import parse_qs
# from urllib.parse import urlencode
# from seleniumwire.utils import decode
# from time import sleep
# from os.path import dirname
# sys.path.append(dirname(dirname(f'{__file__}')))
# from v2.yaml_vuln import vuln_extract
# from scripts.sql_errors import sql_error_check

# def injection(endpoint, params) : # params - input field's id in dict

#     if endpoint == url + "/authenticate" :
#         response = requests.post(endpoint, data=params)
#         session_cookie = response.cookies
#         cookie_storage.append(session_cookie)

#     print(f"Injecting into : {endpoint}")
#     for payload in payload_list :
#         for key in params.keys() :
#             params[key] = payload
#         print(f"Payload injected into {endpoint}\n{params}")
        
#         delay_time_s = 5
#         time_based_keyword = ["SLEEP", "DELAY", "WAIT", str(delay_time_s)]
#         if any(keyword in payload for keyword in time_based_keyword) : # inject time base payload
#             start = timer()
#             if cookie_storage :
#                 response = requests.post(endpoint, data=params, cookies=cookie_storage[0])
#             else :
#                 response = requests.post(endpoint, data=params)
#             end = timer()

#             if timedelta(seconds=end - start) >= timedelta(seconds=delay_time_s) :
#                 print("Time Based SQLi worked")
#                 vuln_endpoint = {'Endpoint' : endpoint, 'Error' : None, "Blind SQLi" : True}
#                 affected_urls.append(vuln_endpoint)
#                 break # end loop if detected blind sqli

#         else : # inject not paylods that is not time based
#             if cookie_storage :
#                 response = requests.post(endpoint, data=params, cookies=cookie_storage[0])
#             else :
#                 response = requests.post(endpoint, data=params)
#         sleep(1)

#         # check whether app is vuln to sqli
#         error = sql_error_check(response.text, error_xml_file)
#         if error != -1 :
#             vuln_endpoint = {"Endpoint" : endpoint, "Error" : error}
#             affected_urls.append(vuln_endpoint)
#             break
#         else :
#             if response.status_code == 500 :
#                 error = f"{response.reason} - {response.status_code}"
#                 # input(response.text)
#                 vuln_endpoint = {"Endpoint" : endpoint, "Error" : error}
#                 affected_urls.append(vuln_endpoint)
#                 break
    
#     print("Done injecting...")
#     print(f"Errors : {error}\n")

# # Define a request interceptor function
# def my_request_interceptor(request):
#     # Do something with the intercepted request
#     # if request.method == 'POST' and request.headers['Content-Type'] == 'application/x-www-form-urlencoded' :
#     if request.method == 'POST' :
#         # print(f"body : {request.body}, type : {type(request.body)}")
#         body_in_string = (request.body).decode('utf-8')
        
#         if request.headers['Content-Type'] == 'application/json' :
#             params = json.loads(body_in_string)
#         elif request.headers['Content-Type'] == 'application/x-www-form-urlencoded' :
#             params = {key: value[0] if len(value) == 1 else value for key, value in parse_qs(body_in_string).items()}
        
#         if not any(request.url == x._args[0] for x in threads) : # check if the endpoint is alr going to be requested
#             thread = threading.Thread(target=injection, args=(request.url, params))
#             threads.append(thread)
        
#         # result = injection(request.url, params)
#         # print("Done injecting...")
#         # print(f"Errors : {result}\n")
#         # if result != -1 :
#         #     vuln_endpoint = {"Endpoint" : request.url, "Error" : result}
#         #     affected_urls.append(vuln_endpoint)

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

# ######
# # aiken u can add in ur code here
# ######


# ######################## start of using selenium wire - pops up browser #######################
# error_xml_file = 'scripts/errors.xml'
# # put sql payloads into list
# payloadfile='sqlpayload.txt'
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
#     cwe_id = "CWE-89"
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
