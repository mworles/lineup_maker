import pandas as pd
import numpy as np
from urllib import urlopen
from bs4 import BeautifulSoup as bsoup
import re
import csv
import datetime
import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def make_url(year, week):
    url_base = "http://rotoguru1.com/cgi-bin/fyday.pl?"
    url = url_base + 'week=' + str(w) + '&year=' + str(year) + '&game=fd'
    return url

def get_data(soup_rows):
    row_data = []
    for r in soup_rows:
        if 'b' in [tag.name for tag in r.find_all()]:
            cols = [b.get_text() for b in r.find_all('b')]
            pos = cols[0].strip()
            cols[0] = 'name'
        else:
            row = [td.get_text() for td in r.find_all('td')]
            if len(row) <=1:
                pass
            else:
                row = map(lambda x: x.replace('$', ''), row)
                row = map(lambda x: x.replace('@', 'awy'), row)
                row = map(lambda x: x.replace('v.', 'hm'), row)
                row.append(pos)
                row_data.append(row)
    return cols, row_data

def scrape_url(url):
    browser = webdriver.Chrome('C:/Users/mworley/chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    browser.get(url)
    soup = bsoup(browser.page_source, 'html.parser')
    tables = soup.find_all('table')
    t = tables[8]
    rows = t.find_all('tr')
    cols, row_data = get_data(rows)
    cols.append('pos')
    df = pd.DataFrame(row_data, columns=cols)
    return df

data_loc = "data/points/"
url_base = "http://rotoguru1.com/cgi-bin/fyday.pl?"

years = [2018]
weeks = range(1, 18)

week_dict = {}

for y in years:
    week_dict[y] = weeks
    
week_dict[2019] = [1]

for y in week_dict.keys():
    for w in week_dict[y]:
        url = make_url(y, w)
        df = scrape_url(url)
        f = 'fd_' + str(y) + '_' + str(w) + '.csv'
        print "writing .csv file: %s" % (f)
        df.to_csv(data_loc + f)
        time.sleep(1)

browser.quit()
