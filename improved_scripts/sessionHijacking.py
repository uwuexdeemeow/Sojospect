from seleniumBot import driver
from seleniumBot import create_webdriver
from seleniumBot import getCookie
from seleniumBot import analyseConfig
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
import configparser
import sys
from os.path import dirname
sys.path.append(dirname(dirname(f'{__file__}')))
from v2.yaml_vuln import vuln_extract

if __name__ == "__main__":
    user_input = sys.argv[1]
    scan_id = int(sys.argv[2])

url = user_input

# Load the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

db_host = config.get('SQL Database', 'db_host')
db_user = config.get('SQL Database', 'db_user')
db_password = config.get('SQL Database', 'db_password')

username = config.get('Advanced Scan Settings','scraping_username')
password = config.get('Advanced Scan Settings','scraping_password')

db_connection = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database="vulnerabilities"
)

db_cursor = db_connection.cursor()


if analyseConfig('scan_for_sessionreplay') != 1 :
    print('feature not enabled')
    driver.quit()
    quit()
else:
    user1Cookie = getCookie(username, password)
    print(user1Cookie)
    print("Login Successful\n")
    driver.delete_all_cookies()
    driver.quit()

    # new web driver to hijack session
    new_driver = create_webdriver()
    print(f"Cookie is cleared in browser. - {new_driver.get_cookies()}")

    login_url = new_driver.get(url)
    new_driver.add_cookie(user1Cookie[0])
    new_driver.refresh() # need double check if refresh at login will redirect to dashboard,etc.

    if new_driver.current_url != login_url :
        print("Session is hijacked.")
        db_cursor = db_connection.cursor()
        cwe_id = "CAPEC-593"
        vuln_yml = vuln_extract(cwe_id)
        name = vuln_yml['name']
        # Insert a row into the MySQL table
        insert_query = "INSERT INTO vulnerabilities (scan_id, vulnerability_name, vulnerability_id, url, additional_information) VALUES (%s, %s, %s, %s, %s)"
        values = (scan_id, name, cwe_id, "https://chmsdemo.greenfossil.com", None) #Change this in the later part, don't hardcode
        db_cursor.execute(insert_query, values)
        db_connection.commit()

        db_cursor.close()
        db_connection.close()
    else:
        result = 'Session replay was unsuccessful'
        print(result)