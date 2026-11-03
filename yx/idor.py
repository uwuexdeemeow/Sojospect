import requests
import configparser
import random
import re
import subprocess
import json
import mysql.connector
import sys
from os.path import dirname
sys.path.append(dirname(dirname(f'{__file__}')))
from v2.yaml_vuln import vuln_extract

def generate_random_dob():
    day = random.randint(1, 31)
    month = random.randint(1, 12)
    year = random.randint(1950, 2000)  # Adjust the range based on your preferences

    # Ensure correct number of digits for day and month
    day_str = str(day).zfill(2)
    month_str = str(month).zfill(2)

    # Format the date of birth
    dob = f"{day_str}/{month_str}/{year}"
    return dob

def generate_random_nric():
    # Use '0123456789' for the first three characters and 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for the last character
    first_three_chars = ''.join(random.choices('0123456789', k=3))
    last_char = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    return first_three_chars + last_char

def login(username, password) :
    login_info = {"loginId":username, "password":password}
    response = requests.post("https://chmsdemo.greenfossil.com/authenticate", data=login_info)
    session_cookie = response.cookies
    return session_cookie

# create two users
def create_test_user(cookie, newuser_info) :
    
    response = requests.post("https://chmsdemo.greenfossil.com/user/new", cookies=cookie, data=newuser_info) 

    # check if user exist
    if response.status_code != 400 :
        # extract id from url
        returned_url = response.url
        pattern = re.compile(r'\d+')
        numbers = pattern.findall(returned_url)
        extracted_id = ''
        for found in numbers :
            extracted_id = found
        # set password
        newpwd = {"newpassword":"password", "repeatpassword":"password", "APP_CSRF_TOKEN":""}
        response = requests.post(f"https://chmsdemo.greenfossil.com/user/{extracted_id}/password/adminreset", cookies=cookie, data=newpwd)
        
if __name__ == "__main__":
    user_input = sys.argv[1] # this is the domain
    scan_id = int(sys.argv[2])

# retrieve info from config.ini
config = configparser.ConfigParser()
config.read("config.ini")
username = config.get('Advanced Scan Settings','scraping_username')
password = config.get('Advanced Scan Settings','scraping_password')
filename = config.get('Advanced Scan Settings', 'mapped_file')
idor = config.get('Advanced Scan Settings','idor')

if int(idor) == 1 :
    cookie = login(username, password)
    print(cookie)

    # creating 2 users
    for i in range(2) :
        data = {"salutationOpt":"", 
                "nicknameOpt":"",
                "lastname":"Tan",
                "firstnameOpt":"John",
                "phoneticnameOpt":"",
                "nricPrefixOpt":"",
                "partialNricOpt":generate_random_nric(),
                "loginIdOpt":f"idortestuser{i+1}",
                "dobOpt":generate_random_dob(),
                "gender":"Male",
                "highestEduLevelOpt":"",
                "religionOpt":"",
                "nationalityOpt":"",
                "raceOpt":"",
                "maritalStatusOpt":"",
                "weddingDateOpt":"",
                "status":"Active",
                "remarksOpt":"",
                "APP_CSRF_TOKEN":""}

        create_test_user(cookie, data)

        # change value in config.ini
        config.set('Advanced Scan Settings', 'scraping_username', data['loginIdOpt'])
        config.set('Advanced Scan Settings', 'scraping_password', 'password')
        config.set('Advanced Scan Settings', 'mapped_file', f'crawl-{data["loginIdOpt"]}.txt')
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        # start crawling
        script_path = "v2.0/crawler-new.py"
        script_arguments = ["https://chmsdemo.greenfossil.com", "1"] # args can be removed once test suite is completed

        # Use subprocess to run the script
        process = subprocess.Popen(["python", script_path] + script_arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for the process to finish and capture the output
        stdout, stderr = process.communicate()

        # # Print the output and error, if any
        print("Script Output:", stdout.decode())
        print("Script Error:", stderr.decode())

        # Get the return code of the process
        return_code = process.returncode
        print("Return Code:", return_code)

    # set back to initial value
    config.set('Advanced Scan Settings', 'scraping_username', username)
    config.set('Advanced Scan Settings', 'scraping_password', password)
    config.set('Advanced Scan Settings', 'mapped_file', filename)
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    # testing for idor
    url_list1 = []
    with open('crawl-idortestuser1.txt','r') as crawl_file:
        for i in (crawl_file.readlines()):
            data_dict = json.loads(i) #Data is now a dictionary from json loads
            #To get parent url
            if data_dict['Method'] == "GET" :
                url_list1.append(data_dict['URL'])

    url_list2 = []
    with open('crawl-idortestuser2.txt','r') as crawl_file:
        for i in (crawl_file.readlines()):
            data_dict = json.loads(i) #Data is now a dictionary from json loads
            #To get parent url
            if data_dict['Method'] == "GET" :
                url_list2.append(data_dict['URL'])
    
    # remove contents in file
    # with open('crawl-idortestuser1.txt', 'w'):
    #     pass 
    # with open('crawl-idortestuser2.txt', 'w'):
    #     pass
 
    set1 = set(url_list1)
    set2 = set(url_list2)
    unique_list_user2 = list(set2 - set1)
    cookie = login("idortestuser1", "password")

    affected_urls = []
    for url in unique_list_user2 :
        response = requests.get(url, cookies=cookie) # using user1 to access user2 objects

        if response.status_code == 403 :
            print(url + " : " + response.reason)
        
        elif response.status_code == 200 :
            affected_urls.append(url)
            print(url + ": accessible")
            print("Website is vulnerable to IDOR")
        else :
            print(f"Status Code : {response.status_code} {response.reason}")
            sys.exit()
    
    if len(affected_urls) > 0 :
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
        cwe_id = "CWE-639"
        # Insert a row into the MySQL table
        vuln_yml = vuln_extract(cwe_id)
        name = vuln_yml["name"]

        insert_query = "INSERT INTO vulnerabilities (scan_id, vulnerability_name, vulnerability_id, url) VALUES (%s, %s, %s, %s)"
        values = []
        for url in affected_urls :
            values.append([scan_id,name,cwe_id,url])
        db_cursor.executemany(insert_query, values)# Insert multiple rows together
        db_connection.commit()

        db_cursor.close()
        db_connection.close()

