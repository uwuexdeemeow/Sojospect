# import sys
# import requests
# import configparser
# import json
# from urllib.parse import urlparse
# from os.path import dirname
# sys.path.append(dirname(dirname(f'{__file__}')))
# from scripts.sql_errors import sql_error_check
# from datetime import timedelta
# from timeit import default_timer as timer
# import subprocess


# if __name__ == "__main__":
#     user_input = sys.argv[1] # this is the domain
#     scan_id = int(sys.argv[2])

# parsed_url = urlparse(user_input)
# scheme = parsed_url.scheme
# netloc = parsed_url.netloc
# url = scheme + "://" + netloc

# config = configparser.ConfigParser()
# config.read("config.ini")
# username = config.get('Advanced Scan Settings','scraping_username')
# password = config.get('Advanced Scan Settings','scraping_password')
# filename = config.get('Advanced Scan Settings', 'mapped_file')
# scan_for_sql = config.get('Advanced Scan Settings','scan_for_sql')
# scan_for_xss = config.get('Advanced Scan Settings','scan_for_xss')
# sql_inject_all_eps = config.get('Advanced Scan Settings', 'sql_inject_all_eps')
# xss_inject_all_eps = config.get('Advanced Scan Settings', 'xss_inject_all_eps')

# def xss_tryauto() :
#     print("injection xss payloads")
#     return

# def sql_tryauto(listofgeturlrequests,session_cookie,payload_list,error_xml_file):
#     global affected_urls
#     trylist_sql = set()
#     # for every url:
#     for url in listofgeturlrequests:
#         def makeinject(url,payload):
#             querysplit = url.split("?")
#             anpersplit = querysplit[1].split("&")
#             newlist = []
#             for i in anpersplit:
#                 valusplit = i.split("=")
#                 querystring = f"{valusplit[0]}={payload}"
#                 newlist.append(querystring)
#             addanper = "&".join(newlist)
#             addquery = f"{querysplit[0]}?{addanper}"
#             return addquery
#         # add a payload
#         for payload in payload_list:
#             addquery = makeinject(url,payload)
#             trylist_sql.add(addquery)
#     # start testing now:
#     for injection_url in trylist_sql:
#         print(f"trying: {injection_url}")
#         start = timer()
#         resp_in_text = requests.get(injection_url,cookies=session_cookie).text
#         end = timer()
#         delay_time_s = 120
#         error = sql_error_check(resp_in_text, error_xml_file)
#         if error != -1 :
#             vuln_endpoint = {"Endpoint" : injection_url, "Error" : error}
#             print("error found")
#             affected_urls.append(vuln_endpoint)
#         elif (timedelta(seconds=4.9) <= timedelta(seconds=end - start) <= timedelta(seconds=delay_time_s)):
#             vuln_endpoint = {"Endpoint" : injection_url, "Error" : "There was a delay in the load time. Possible error"}
#             print("Delay error found")
#             affected_urls.append(vuln_endpoint)

# # # main part of the code
            
# def login(username, password):
#     login_info = {"loginId": username, "password": password}
#     response = requests.post(
#         "https://chmsdemo.greenfossil.com/authenticate", data=login_info
#     )
#     session_cookie = response.cookies
#     return session_cookie

# # url_testlist = ["https://demo.testfire.net/search.jsp?query="]
# url_testlist = []
# affected_urls = []
# # get the URLs that are GET requests as well as the URLs and have a parameter to inject
# with open("crawl-.txt", "r") as crawl_file: # change this back to crawl.txt after the testing
#     for i in crawl_file.readlines():
#         data_dict = json.loads(i)
#         if data_dict["Method"] == "GET":
#             if "?" in data_dict["URL"]:
#                 url_testlist.append(data_dict["URL"])

# payloadfile='sqlpayload.txt'
# text_file = open(payloadfile, "r")
# payload_list = text_file.read().split('\n')
# error_xml_file = 'scripts/errors.xml'

# session_cookie = login(username,password)

# # session_cookie = cookies = {
# #     'PHPSESSID': '201d7e8410a03beb3409f600ce14bea6',
# #     'security_level': '0',
# #     # Add more cookies as needed
# # } # This cookie is to test for the bee-box

# if int(scan_for_xss) == 1 :
#     sql_tryauto(url_testlist,session_cookie,payload_list,error_xml_file)

# if int(scan_for_xss) == 1 :
#     xss_tryauto()

# with open("./injection-results/sql_vuln_endpoints.txt","a+") as file:
#     file.writelines(str(row) +'\n' for row in affected_urls)

# if int(sql_inject_all_eps) == 1 or int(xss_inject_all_eps) ==  1 : # only run the browserlaunch.py if user checks inject all eps
#     process = subprocess.Popen(['python', f"./scripts/BrowserLaunch.py", url, str(scan_id)])
#     process.wait() # wait for process to finish