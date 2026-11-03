import os
import time
import json
import configparser
from seleniumBot import driver
from seleniumBot import userLogin
from seleniumBot import analyseConfig
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
import sys
import json
from os.path import dirname
sys.path.append(dirname(dirname(f'{__file__}')))
from v2.yaml_vuln import vuln_extract


if __name__ == "__main__":
    user_input = int(sys.argv[1])
    scan_id = int(sys.argv[2])

url_to_inject = []
with open('crawl.txt','r') as crawl_file:
    for i in (crawl_file.readlines()):
        data_dict = json.loads(i) #Data is now a dictionary from json loads
        #Examples to read data
        #To print all fields
        for key in data_dict.keys():
            if(key.startswith("Param_")):
                if data_dict[key]['type'] == 'file' :  # for injection filter type - text, for file upload filter file
                    url_to_inject.append(data_dict)

# Load the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

db_host = config.get('SQL Database', 'db_host')
db_user = config.get('SQL Database', 'db_user')
db_password = config.get('SQL Database', 'db_password')
username = config['Advanced Scan Settings']['scraping_username']
password = config['Advanced Scan Settings']['scraping_password']

db_connection = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database="vulnerabilities"
)

target_url = user_input
fileList = []
for filename in os.listdir('testFiles'):
    fileList.append(os.path.join('testFiles', filename))

homePage = userLogin(target_url, username, password)
role = driver.find_element(By.CSS_SELECTOR, 'span.label').text


if role == 'Administrator':
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.dropdown')))
    homePage = driver.find_element(By.CSS_SELECTOR, 'div.dropdown div a').get_attribute('href')
    driver.get(homePage+'/editPhoto')


elif role != 'Administrator':
    driver.get(homePage+'/editPhoto')


fileUpload = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'imageUpload')))
unrestricted_count = 0
for i in range(len(fileList)):
    time.sleep(10)
    print(fileList[i])
    fileUpload.send_keys(os.path.realpath(fileList[i]))
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.message')))
        message = driver.find_element(By.CSS_SELECTOR, 'div.message').text
    except TimeoutException:
        unrestricted_count += 1
if unrestricted_count > 0:
    db_cursor = db_connection.cursor()
    # Insert a row into the MySQL table
    cwe_id = "CWE-434"
    vuln_yml = vuln_extract(cwe_id)
    name = vuln_yml["name"]
    #Try not to hardcode CHANGE this url
    url = homePage + '/editPhoto'
    url_dict = {
        'url':url
    }
    url_dict_json = json.dumps(url_dict)
    insert_query = "INSERT INTO vulnerabilities (scan_id, vulnerability_name, vulnerability_id, url, additional_information) VALUES (%s, %s, %s, %s, %s)"
    values = (scan_id,name,cwe_id,user_input,url_dict_json)
    db_cursor.execute(insert_query, values)
    db_connection.commit()

    db_cursor.close()
    db_connection.close()

    message = 'Unrestricted file upload vulnerability detected'
else:
    message = 'Unrestricted file upload vulnerability not detected'

print('finished testing')
driver.quit()
print(message)