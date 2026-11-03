import requests
import mysql.connector
import sys
import configparser
from os.path import dirname
sys.path.append(dirname(dirname(f'{__file__}')))
from v2.yaml_vuln import vuln_extract

def login(username, password) :
    login_info = {"loginId":username, "password":password}
    response = requests.post("https://chmsdemo.greenfossil.com/authenticate", data=login_info)
    session_cookie = response.cookies
    return session_cookie


if __name__ == "__main__":
    user_input = sys.argv[1] # this is the domain
    scan_id = int(sys.argv[2])

# retrieve info from config.ini
config = configparser.ConfigParser()
config.read("config.ini")
username = config.get('Advanced Scan Settings','scraping_username')
password = config.get('Advanced Scan Settings','scraping_password')
session_invalidation = config.get('Advanced Scan Settings','scan_for_session_invalidation')

if int(session_invalidation) == 1 :
    weak_session_mgmt = True
    #### login first to get APP_SESSION cookie #### 
    session_cookie = login(username, password)
    print(session_cookie)

    for cookie in session_cookie :
        if cookie.name == "APP_SESSION" :
            APP_SESSION = cookie
    
    # Logout
    response = requests.get("https://chmsdemo.greenfossil.com/logout", cookies=session_cookie)
    
    # Access dashboard using above session cookie
    response = requests.get("https://chmsdemo.greenfossil.com/", cookies=session_cookie)

    if response.url == "https://chmsdemo.greenfossil.com/login" : # if session cookie is invalid, it will redirect back to login
        weak_session_mgmt = False
        print("Session cookie is invalid.")

    ###################### WRITING AFFECTED URLS/ENDPOINTS TO DB #################
    if weak_session_mgmt :
        print("Session cookie can be reused.")
        db_host = config.get('SQL Database', 'db_host')
        db_user = config.get('SQL Database', 'db_user')
        db_password = config.get('SQL Database', 'db_password')

        db_connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database="vulnerabilities"
        )

        db_cursor = db_connection.cursor()
        cwe_id = "CWE-613"
        # Insert a row into the MySQL table
        vuln_yml = vuln_extract(cwe_id)
        name = vuln_yml["name"]

        insert_query = "INSERT INTO vulnerabilities (scan_id, vulnerability_name, vulnerability_id, url) VALUES (%s, %s, %s, %s)"
        values = []
        values.append([scan_id,name,cwe_id,user_input])
        db_cursor.executemany(insert_query, values)# Insert multiple rows together
        db_connection.commit()

        db_cursor.close()
        db_connection.close()
        