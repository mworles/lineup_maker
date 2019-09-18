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



    

data_loc = "data/contests/"
url = "https://www.fanduel.com/contests"

#def scrape_url(url):
browser = webdriver.Chrome('C:/Users/mworley/chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
browser.get(url)

#login = browser.find_element_by_link_text('Log in')
#login.click()

login_user = browser.find_element_by_id('forms.login.email')
login_user.send_keys('mworles@gmail.com')
login_pwd = browser.find_element_by_id('forms.login.password')
login_pwd.send_keys('kentucky2')
submit = browser.find_element_by_id('forms.login.submit')
submit.click()

time.sleep(2)
btn = browser.find_element_by_link_text('History')
btn.click()

time.sleep(5)
soup = bsoup(browser.page_source, 'html.parser')
tables = soup.find_all('table')

contests = []

for t in tables:
    #tb = t.find('tbody')
    cr = t.find_all('tr')[-1]
    hd = cr.find('th').find('span').get_text()
    ct = cr.find('td').find('span').get_text()
    contests.append([hd, ct])

link_text = contests[0][-1]
link = browser.find_element_by_link_text(link_text)
link.click()

#entry = browser.find_element_by_xpath('//*[@id="global-view"]/div/div/div/div[7]/ol/li[1]')
#entry.click()

time.sleep(3)
entries = browser.find_elements_by_tag_name('li')[0:10]
"""
entries[0].click()

time.sleep(2)
soup = bsoup(browser.page_source, 'html.parser')
entry_lu = soup.find('div', {'class': 'live-comparison-entry active'})
ps = entry_lu.find_all('li')
for p in ps:
    spans = p.find_all('span')
    text = [s.get_text() for s in spans]
    print text
    #p.find('span', {'data-test-id': 'data-chunk-value'})
    #print p.get_text()
"""

"""
//*[@id="global-view"]/div/div/div/div[7]/ol/li[1]/div[2]
soup = bsoup(browser.page_source, 'html.parser')
entry_lu = soup.find('div', {'class': 'live-comparison-entry active'})
entry_li = entry_lu.find_all('li')
print len(li)
"""
#soup = bsoup(browser.page_source, 'html.parser')
"""
tables = soup.find_all('table')
t = tables[8]
rows = t.find_all('tr')
cols, row_data = get_data(rows)
cols.append('pos')
df = pd.DataFrame(row_data, columns=cols)
"""
"""
f = 'fd_' + str(y) + '_' + str(w) + '.csv'
print "writing .csv file: %s" % (f)
df.to_csv(data_loc + f)
time.sleep(1)

browser.quit()
"""
