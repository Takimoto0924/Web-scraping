import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import re
import time

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
options = webdriver.ChromeOptions()
options.add_argument('--user-agent=' + user_agent)
options.add_experimental_option('excludeSwitches', ['enable-logging'])

chromedriver = "C:\Python\chromedriver_win32\chromedriver.exe"
driver = webdriver.Chrome(chrome_options=options, executable_path=chromedriver)

def crawling(info_list, count):
    time.sleep(3)
    a_tag_list = driver.find_elements(By.CLASS_NAME, 'style_titleLink__oiHVJ')
    url_list = [a_tag.get_attribute('href') for a_tag in a_tag_list if not a_tag.find_elements(By.TAG_NAME, 'span')]
    
    driver.switch_to.window(driver.window_handles[1])
    for url in url_list:
        if count < count_max:
            info = scraping(url)
            info_list.append(info)
            count += 1
        else:
            driver.close()
            driver.quit()
            break

    else:
        get_next_url()
        info_list = crawling(info_list, count)
    
    return info_list

def get_next_url():
    driver.switch_to.window(driver.window_handles[0])
    next_link = driver.find_element(By.CLASS_NAME, "style_nextIcon__M_Me_").find_element(By.XPATH, "..")
    next_link.click()

def scraping(url):
    driver.get(url)
    time.sleep(3)
    name = driver.find_element(By.ID, "info-name").text
    phone = driver.find_element(By.CLASS_NAME, "number").text
    try:
        mail = driver.find_element(By.LINK_TEXT,"お店に直接メールする").get_attribute("href").removeprefix("mailto:")
    except:
        mail = ""
    address = driver.find_element(By.CLASS_NAME, "region").text
    re_address = divide_address(address)
    try:
        building = driver.find_element(By.CLASS_NAME, "locality").text
    except NoSuchElementException:
        building = ""
    try:
        url = driver.find_element(By.CLASS_NAME, "sv-of").get_attribute("href")
        driver.get(url)
        time.sleep(3)
        URL = driver.current_url
        SSL = URL.startswith("https://")
    except NoSuchElementException:
        try:
            url = driver.find_element(By.CLASS_NAME, "url").get_attribute("href")
            driver.get(url)
            time.sleep(3)
            URL = driver.current_url
            SSL = URL.startswith("https://")
        except NoSuchElementException:
            URL = ""
            SSL = ""
    return [name, phone, mail, *re_address.groups(), building, URL, SSL]

def divide_address(address):
    re_address = re.match(r'(...??[都道府県])([^\d]+)(.*)', address)
    return re_address

def csv(info_list):
    df = pd.DataFrame(info_list)
    fname = '1-2.csv'
    header = ["店舗名", "電話番号", "メールアドレス", "都道府県", "市区町村", "番地", "建物名", "URL", "SSL"]
    df.to_csv(fname, header=header, index=False, encoding="utf_8_sig")

info_list = []
count = 0
count_max = 50

url = 'https://r.gnavi.co.jp/area/jp/sushi/rs/'
driver.get(url)
driver.execute_script("window.open();")

info_list = crawling(info_list, count)
csv(info_list)