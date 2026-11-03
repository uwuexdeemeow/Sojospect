# from seleniumBot import driver
# from seleniumBot import getCookie
# from seleniumBot import analyseConfig
# from selenium.webdriver.common.by import By 
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import mysql.connector
# import configparser
# import sys
# from os.path import dirname
# sys.path.append(dirname(dirname(f'{__file__}')))
# from v2.yaml_vuln import vuln_extract

# if __name__ == "__main__":
#     scan_id = int(sys.argv[2])
# # Load the configuration file
# config = configparser.ConfigParser()
# config.read('config.ini')

# db_host = config.get('SQL Database', 'db_host')
# db_user = config.get('SQL Database', 'db_user')
# db_password = config.get('SQL Database', 'db_password')

# username = config.get('Advanced Scan Settings','scraping_username')
# password = config.get('Advanced Scan Settings','scraping_password')

# db_connection = mysql.connector.connect(
#     host=db_host,
#     user=db_user,
#     password=db_password,
#     database="vulnerabilities"
# )

# db_cursor = db_connection.cursor()


# if analyseConfig('scan_for_sessionreplay') != 1:
#     print('feature not enabled')
#     driver.quit()
#     quit()
# else:
#     user1 = username  
#     password1 = password  
#     user2 = 'U0000029'  
#     password2 = password

#     user1Cookie = getCookie(user1, password1)['value']
#     driver.execute_script('window.open('')')
#     driver.switch_to.window(driver.window_handles[1])
#     user2Cookie = getCookie(user2, password2)

#     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.profile img')))
#     originalProfile = driver.find_element(By.CSS_SELECTOR, 'span.profile img').get_attribute('src')
#     print(originalProfile)

#     user2Cookie['value'] = user1Cookie
#     driver.delete_cookie('APP_SESSION')
#     driver.add_cookie(user2Cookie)
#     driver.refresh()

#     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.profile img')))
#     newProfile = driver.find_element(By.CSS_SELECTOR, 'span.profile img').get_attribute('src')
#     print(newProfile)

#     if originalProfile != newProfile:
#         db_cursor = db_connection.cursor()
#         cwe_id = "CAPAC-593"
#         vuln_yml = vuln_extract(cwe_id)
#         name = vuln_yml['name']
#         # Insert a row into the MySQL table
#         insert_query = "INSERT INTO vulnerabilities (scan_id, vulnerability_name, vulnerability_id, url, additional_information) VALUES (%s, %s, %s, %s, %s)"
#         values = (scan_id, name, cwe_id, "https://chmsdemo.greenfossil.com", None) #Change this in the later part, don't hardcode
#         db_cursor.execute(insert_query, values)
#         db_connection.commit()

#         db_cursor.close()
#         db_connection.close()
#         result = 'Session replay was successful'
#         print(result)
#     else:
#         result = 'Session replay was unsuccessful'
#         print(result)