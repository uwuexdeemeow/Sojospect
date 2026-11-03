import time
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import configparser

def create_webdriver():
    try:
        # Try creating a Chrome webdriver
        chrome_options = Options()
        chrome_options.add_argument("headless")
        return webdriver.Chrome(options=chrome_options)
    except:
        try:
            # Try creating a Firefox webdriver
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.add_argument("headless") 
            return webdriver.Firefox(options=firefox_options)
        except:
            try:
                from selenium.webdriver.edge.options import Options as EdgeOptions
                # Try creating an Edge webdriver
                options = EdgeOptions()
                options.use_chromium = True
                options.add_argument("headless")
                return webdriver.Edge(options=options)
            except:
                raise Exception("No suitable browser found")

target_url = 'https://chmsdemo.greenfossil.com/'
driver = create_webdriver()

def userLogin(url, username, password):
    login_url = url + '/login'
    driver.maximize_window()
    driver.get(login_url)
    driver.find_element(By.ID, 'loginId').send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password, Keys.RETURN)
    time.sleep(5)
    return driver.current_url

def getCookie(username, password):
    userLogin(target_url, username, password)
    time.sleep(5)
    cookies = driver.get_cookies()
    return cookies

def analyseConfig(feature):
    config = configparser.ConfigParser()
    config.read('config.ini')
    return int(config['Advanced Scan Settings'][feature])