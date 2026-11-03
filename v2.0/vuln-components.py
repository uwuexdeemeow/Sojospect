import requests
import json
from urllib.parse import urlsplit
import os.path
import retirejs
import mysql.connector
import configparser
import sys
import time
# from v2.yaml_vuln import vuln_extract

# if __name__ == "__main__":
#     user_input = sys.argv[1] # this is the domain
#     scan_id = int(sys.argv[2])

# retrieve info from config.ini
# config = configparser.ConfigParser()
# config.read("config.ini")
# username = config.get('Advanced Scan Settings','scraping_username')
# password = config.get('Advanced Scan Settings','scraping_password')
# session_invalidation = config.get('Advanced Scan Settings','scan_for_session_invalidation')

urls = []
#Function here to get the list of javascripts
with open('crawl.txt','r') as crawl_file:
    for i in (crawl_file.readlines()):
        data_dict = json.loads(i) #Data is now a dictionary from json loads
        urls.append(data_dict['URL'])

possible_packagenames = {}
#Extract package name from filename, first field
for url in urls:
    filename = os.path.split(urlsplit(url).path)[1]
    # possible_packagename = filename.split('.')[0]
    if filename in possible_packagenames:
        possible_packagenames[filename].append(url)
    else:
        possible_packagenames[filename] = [url]

#Extract all version numbers for the package
for filename, urls in possible_packagenames.items():
    package = filename.split('.')[0]
    if (package != ""):
        for url in urls:
            url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?virtualMatchString=cpe:2.3:*:{package}:*:*:*:*:*"
            headers = {'apiKey':'4ec139bd-393a-4514-9288-80a331d7caec'}
            resp = requests.get(url, headers=headers)
            # try:
            #     resp = requests.get(url)
            # except requests.exceptions.MissingSchema:
            #     resp = requests.get('https://chmsdemo.greenfossil.com'+url)
            if( resp.status_code == 200):
                json_obj = json.loads(resp.text)
            #print(json_obj)
            # print('Completed')
            # exit(0)
            # print(json_obj['vulnerabilities'][1]['cve'].keys())
            # print(json_obj['vulnerabilities'][0]['cve']['configurations'])
                for index in range(len(json_obj['vulnerabilities'])):
                    cve_id = json_obj['vulnerabilities'][index]['cve']['id']
                    description = ""
                    for row in json_obj['vulnerabilities'][index]['cve']['descriptions']:
                        if row['lang']=='en':
                            description = row['value']
                            break
                    #Look for versionendincluding in configurations, any version before that is vulnerable
                    versionEndIncluding=None
                    versionEndExcluding=None
                    versionStartIncluding=None
                    versionStartExcluding=None
                    version=None
                    for row in json_obj['vulnerabilities'][index]['cve']['configurations']:
                        for node in row['nodes']:
                            for value in node['cpeMatch']:
                                if package not in value['criteria']:
                                    break
                                if 'versionEndIncluding' in value.keys():
                                    versionEndIncluding = value['versionEndIncluding']
                                if 'versionEndExcluding' in value.keys():
                                    versionEndExcluding = value['versionEndExcluding']
                                if 'versionStartIncluding' in value.keys():
                                    versionStartIncluding = value['versionStartIncluding']
                                if 'versionStartExcluding' in value.keys():
                                    versionStartExcluding = value['versionStartExcluding']
                            for value in node['cpeMatch']:
                                if versionEndIncluding==None and versionEndExcluding==None and versionStartIncluding==None and versionStartExcluding==None and package in value['criteria']:
                                    criteria_list = value['criteria'].split(':')
                                    version = criteria_list[5] if criteria_list[6] == '*' else criteria_list[5]+'-'+criteria_list[6]
                    print(f"CVE: {cve_id}")
                    print(f"Description: {description}")
                    if versionEndIncluding==None and versionEndExcluding==None and versionStartIncluding==None and versionStartExcluding==None:
                        print(version)
                    else:
                        print(versionEndIncluding, versionEndExcluding, versionStartIncluding, versionStartExcluding)
                    print()
                # try:
                #     temp_resp = retirejs.scan_endpoint(url)
                # except requests.exceptions.MissingSchema:
                #     #temp_resp = resp = retirejs.scan_endpoint("http://code.jquery.com/jquery-1.6.min.js")
                #     temp_resp = resp = retirejs.scan_endpoint('https://chmsdemo.greenfossil.com'+url)
                #if (temp_resp != []):
                    # if('vulnerabilities' in temp_resp[0]) :
                    #     package_vulnerabilities = temp_resp[0].get('vulnerabilities')
                    #     print(f"{package} is vulnerable, Details : {package_vulnerabilities}")
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
                    #     cwe_id = "CWE-1352"
                    #     # Insert a row into the MySQL table
                    #     vuln_yml = vuln_extract(cwe_id)
                    #     name = vuln_yml["name"]

                    #     insert_query = "INSERT INTO vulnerabilities (scan_id, vulnerability_name, vulnerability_id, url) VALUES (%s, %s, %s, %s)"
                    #     values = []
                    #     values.append([scan_id,name,cwe_id,user_input])
                    #     db_cursor.executemany(insert_query, values)# Insert multiple rows together
                    #     db_connection.commit()

                    #     db_cursor.close()
                    #     db_connection.close()




# json_obj = json.loads(resp.text)
#             #print(json_obj)
#             # print('Completed')
#             # exit(0)
#             # print(json_obj['vulnerabilities'][1]['cve'].keys())
#             # print(json_obj['vulnerabilities'][0]['cve']['configurations'])
#             for index in range(len(json_obj['vulnerabilities'])):
#                 cve_id = json_obj['vulnerabilities'][index]['cve']['id']
#                 description = ""
#                 for row in json_obj['vulnerabilities'][index]['cve']['descriptions']:
#                     if row['lang']=='en':
#                         description = row['value']
#                         break
#                 #Look for versionendincluding in configurations, any version before that is vulnerable
#                 versionEndIncluding=None
#                 versionEndExcluding=None
#                 versionStartIncluding=None
#                 versionStartExcluding=None
#                 version=None
#                 for row in json_obj['vulnerabilities'][index]['cve']['configurations']:
#                     for node in row['nodes']:
#                         for value in node['cpeMatch']:
#                             if 'jquery' not in value['criteria']:
#                                 break
#                             if 'versionEndIncluding' in value.keys():
#                                 versionEndIncluding = value['versionEndIncluding']
#                             if 'versionEndExcluding' in value.keys():
#                                 versionEndExcluding = value['versionEndExcluding']
#                             if 'versionStartIncluding' in value.keys():
#                                 versionStartIncluding = value['versionStartIncluding']
#                             if 'versionStartExcluding' in value.keys():
#                                 versionStartExcluding = value['versionStartExcluding']
#                         for value in node['cpeMatch']:
#                             if versionEndIncluding==None and versionEndExcluding==None and versionStartIncluding==None and versionStartExcluding==None and 'jquery' in value['criteria']:
#                                 criteria_list = value['criteria'].split(':')
#                                 version = criteria_list[5] if criteria_list[6] == '*' else criteria_list[5]+'-'+criteria_list[6]
#                 print(f"CVE: {cve_id}")
#                 print(f"Description: {description}")
#                 if versionEndIncluding==None and versionEndExcluding==None and versionStartIncluding==None and versionStartExcluding==None:
#                     print(version)
#                 else:
#                     print(versionEndIncluding, versionEndExcluding, versionStartIncluding, versionStartExcluding)
#                 print()
