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

def replace_cookie_value(cookies, new_value) :

    for cookie in cookies :
        if cookie.name == "APP_SESSION" :
            cookie.value = new_value

    return cookies

if __name__ == "__main__":
    user_input = sys.argv[1] # this is the domain
    scan_id = int(sys.argv[2])

# retrieve info from config.ini
config = configparser.ConfigParser()
config.read("config.ini")
username = config.get('Advanced Scan Settings','scraping_username')
password = config.get('Advanced Scan Settings','scraping_password')
session_fixation = config.get('Advanced Scan Settings','scan_for_session_fixation')

if int(session_fixation) == 1 :
    session_fixation = True

    # Browse to website to get a session identifier
    response = requests.get(user_input)
    session_identifier = response.request.headers['COOKIE'].split("APP_SESSION=")[1]

    ### login first to get APP_SESSION cookie ###
    session_cookie = login(username, password)
    print(session_cookie)
    
    returned_cookie = session_cookie["APP_SESSION"] # application returns new/protected session identifier
    
    if session_identifier != returned_cookie :
        # no session fixation
        session_fixation = False
        print("New session token is returned")

        # IN CASE, check if the initial session identifier can be used as an authenicated user
        session_identifier = replace_cookie_value(session_cookie, session_identifier) # fn is to put cookie in cookie jar format
        response = requests.get(user_input, cookies=session_identifier)
        # print(response.cookies)
        if response.url == "https://chmsdemo.greenfossil.com/login" :
            session_fixation = False
            print("Session identifier is invalid")

        else : # if it does not redirects to login page --> cookie is valid
            session_fixation = True
            print("There is Session Fixation")

    else : # check if it is a valid session identifier
        session_identifier = replace_cookie_value(session_cookie, session_identifier) # fn is to put cookie in cookie jar format
        response = requests.get(user_input, cookies=session_identifier)
        if response.url == "https://chmsdemo.greenfossil.com/login" :
            session_fixation = False
            print("Session identifier is invalid")

        else : # if it does not redirects to login page --> cookie is valid
            session_fixation = True
            print("There is Session Fixation")

    ###################### WRITING AFFECTED URLS/ENDPOINTS TO DB #################
    if session_fixation :
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
        cwe_id = "CWE-384"
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
        