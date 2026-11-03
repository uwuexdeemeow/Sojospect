import requests
import random
from bs4 import BeautifulSoup
import mysql.connector
import sys
import configparser
from os.path import dirname
sys.path.append(dirname(dirname(f'{__file__}')))
from v2.yaml_vuln import vuln_extract


letters = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D',
    'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
    'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
]
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']


def login(username, password) :
    login_info = {"loginId":username, "password":password} # REMEMBER TO CHANGE HARDCODED LOGINID AND PASSWORD
    response = requests.post("https://chmsdemo.greenfossil.com/authenticate", data=login_info)
    session_cookie = response.cookies
    return session_cookie

def rand_pwd() :
    password_list = []
    for char in range(1, 4 + 1):
        password_list.append(random.choice(letters))

    for char in range(1, 3 + 1):
        password_list.append(random.choice(numbers))

    for char in range(1, 1 + 1):
        password_list.append(random.choice(symbols))

    random.shuffle(password_list)
    password = ''.join(password_list)
    return password


if __name__ == "__main__":
    user_input = sys.argv[1] # this is the domain
    scan_id = int(sys.argv[2])

# retrieve info from config.ini
config = configparser.ConfigParser()
config.read("config.ini")
username = config.get('Advanced Scan Settings','scraping_username')
password = config.get('Advanced Scan Settings','scraping_password')
test_csrf = config.get('Advanced Scan Settings','testforcsrf')


if int(test_csrf) == 1 :
    csrf_protected = False
    #### login first to get APP_SESSION cookie #### 
    session_cookie = login(username, password)
    print(session_cookie)
    
    ### Check is APP_SESSION is using SameSite : lax or strict
    for cookie in session_cookie :
        if cookie.name == "APP_SESSION" :
            APP_SESSION = cookie
    
    sameSite_value = APP_SESSION.get_nonstandard_attr("SameSite")
    if sameSite_value.casefold() != "lax" or sameSite_value.casefold() != "strict" :
        csrf_protected = True
        print(f"APP_SESSION is using SameSite value : {sameSite_value}")

    else :
        changepwd_url = ""
        response = requests.get("https://chmsdemo.greenfossil.com/dashboard", cookies=session_cookie)
        # print(response.url)
        page_source = response.text
        soup = BeautifulSoup(page_source, features="html.parser")
        # Find all the links in the webpage
        for link in soup.find_all("a"):
            url_in_link = link.get("href")
            if url_in_link == None :
                continue
            elif "/user/password" in url_in_link :
                changepwd_url = f"https://chmsdemo.greenfossil.com/{url_in_link}"
                break
        
        newpwd = rand_pwd()
        changepwd_form = {"oldpassword":password, "newpassword":newpwd, "repeatpassword":newpwd}
        response = requests.post(changepwd_url, cookies=session_cookie, data=changepwd_form)

        session_cookie = login(username, newpwd)
        # print(session_cookie)
        if len(session_cookie) == 0 : # can't login using new password - password is not changed
            csrf_protected = True
            print("Password is not changed, App is CSRF-protected.")

        else : ### password is changed
            # csrf_protected = False
            print("CSRF Token is not validated.")
        
            ### CHANGE BACK PASSWORD ###
            count = 0
            while count < 6 : 
                current_pwd = newpwd
                newpwd = rand_pwd()
                # print(newpwd)
                changepwd_form = {"oldpassword":current_pwd, "newpassword":newpwd, "repeatpassword":newpwd}
                response = requests.post(changepwd_url, cookies=session_cookie, data=changepwd_form)
                count += 1
            
            changepwd_form = {"oldpassword":newpwd, "newpassword":password, "repeatpassword":password}
            response = requests.post(changepwd_url, cookies=session_cookie, data=changepwd_form)
            ############################
    
    ###################### WRITING AFFECTED URLS/ENDPOINTS TO DB #################
    if not csrf_protected :
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
        cwe_id = "CWE-352"
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
        