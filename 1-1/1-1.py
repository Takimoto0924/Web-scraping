import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import time

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
header = {'User-Agent': user_agent}

def crawling(url, info_list, count):
    response = requests.get(url, headers=header)
    time.sleep(3)
    bs = BeautifulSoup(response.content, 'html.parser')
    a_tag_list = bs.find_all('a', class_ = 'style_titleLink__oiHVJ')
    url_list = [a_tag.get('href') for a_tag in a_tag_list if not a_tag.find('span')]

    for url in url_list:
        if count < count_max:
            info = scraping(url)
            info_list.append(info)
            count += 1
        else:
            break

    else:
        url = get_next_url(bs)
        info_list = crawling(url, info_list, count)
    
    return info_list

def get_next_url(bs):
    next_link = bs.find("div", class_="style_pageNation__AZy1A").find_all("a")
    url = 'https://r.gnavi.co.jp' + next_link[-2].get("href")
    return url

def scraping(url):
    response = requests.get(url, headers=header)
    time.sleep(3)
    bs = BeautifulSoup(response.content, 'html.parser')
    info = bs.find("table", class_="basic-table")
    name = info.find(id="info-name").text
    phone = info.find("span", class_="number").text
    mail = ""
    address = info.find("span", class_="region").text
    re_address = divide_address(address)
    try:
        building = info.find("span", class_="locality").text
    except AttributeError:
        building = ""
    return [name, phone, mail, *re_address.groups(), building, "", ""]

def divide_address(address):
    re_address = re.match(r'(...??[都道府県])([^\d]+)(.*)', address)
    return re_address

def csv(info_list):
    df = pd.DataFrame(info_list)
    fname = '1-1.csv'
    header = ["店舗名", "電話番号", "メールアドレス", "都道府県", "市区町村", "番地", "建物名", "URL", "SSL"]
    df.to_csv(fname, header=header, index=False, encoding="utf_8_sig")

info_list = []
count = 0
count_max = 50

url = 'https://r.gnavi.co.jp/area/jp/sushi/rs/'

info_list = crawling(url, info_list, count)
csv(info_list)