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
from selenium.webdriver.common.keys import Keys

def get_name(list_i):
    name = list_i.find_all('span')[1].get_text()
    return name

def get_player_info(p):
    spans = p.find_all('span')
    name = spans[1].get_text()
    pct = spans[6].get_text()
    pdict = {name: {'pct': pct, 'page': page_n}}
    return pdict
                    
data_loc = "data/contests/"
url = "https://www.fanduel.com/contests"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
browser = webdriver.Chrome('C:/Users/mworley/chromedriver.exe', 
                           chrome_options=options)
browser.get(url)


print 'logging in'
login_user = browser.find_element_by_id('forms.login.email')
login_user.send_keys('mworles@gmail.com')
login_pwd = browser.find_element_by_id('forms.login.password')
login_pwd.send_keys('kentucky2')
submit = browser.find_element_by_id('forms.login.submit')
submit.click()

time.sleep(2)
print 'selecting history'
btn = browser.find_element_by_link_text('History')
btn.click()


time.sleep(4)
print 'compiling contests'
soup = bsoup(browser.page_source, 'html.parser')

"""
tables = soup.find_all('table')

contests = []

for t in tables:
    #tb = t.find('tbody')
    cr = t.find_all('tr')[-1]
    hd = cr.find('th').find('span').get_text()
    ct = cr.find('td').find('span').get_text()
    contests.append([hd, ct])

print 'opening contest'
link_text = contests[0][-1]

link = browser.find_element_by_link_text(cel_text)
link.click()
"""

cid = str(38547)
file_name = 'own_' + cid + '.csv'
ctag = 'games/38547/contests'
cel = soup.select_one("a[href*=%s]" % (ctag))
cel_text = cel.find('span').get_text()
link = browser.find_element_by_link_text(cel_text)
link.click()
print 'opening contest %s' % (cid)

time.sleep(2)

try:
    prog = pd.read_csv('data/contests/progress/' + cid + '.csv', index_col=0)
    pages_read = prog.values.tolist()
    print pages_read
    page_progress = prog['page'].max()
    own_df = pd.read_csv(data_loc + file_name)
    own_df = own_df.set_index('name')
    own_pct = own_df.to_dict('index')
except:
    own_pct = {}
    pages_read = []

csoup = bsoup(browser.page_source, 'html.parser')
pagin = csoup.find('div', {'class': 'pagination-status'})
n_pages = int(pagin.get_text().split(' ')[-1])


if len(own_pct.keys()) > 0:
    page_entry = browser.find_element_by_tag_name('input')
    page_n = page_progress + 1
    n_del = len(str(page_n))
    while n_del > 0:
        page_entry.send_keys(Keys.BACKSPACE)
        n_del -= 1
    page_entry.send_keys(str(page_n))
else:
    page_n = 1

last_entry_name = ''

while page_n < n_pages:
    print 'page %s of %s' % (page_n, n_pages)

    soup = bsoup(browser.page_source, 'html.parser')
    eds = soup.find_all('div', {'class': 'user-info'})
    enames = [e.find_all('span')[2].get_text() for e in eds]
    enames = [n.replace('\n','').strip() for n in enames]
    uis = [enames.index(x) for x in enames]
    uis = list(set(uis))
    uis = [x + 1 for x in uis]
    uis = [x for x in uis if x < 8]
    keep_names = [enames[(x-1)] for x in uis]


    if keep_names[0] == last_entry_name and len(uis) == 1:
        pass
    else:
        if keep_names[0] == last_entry_name:
            uis = uis[1:]
        
        page_new = []
        
        for li_n in uis:
            try:
                lixp = "//*[@id='global-view']/div/div/div/div[7]/ol/li[%s]" % (li_n)
                target = browser.find_element_by_xpath(lixp)
                actions = ActionChains(browser)
                actions.move_to_element(target).perform()
                target.click()

                try:
                    element = WebDriverWait(browser, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//*[@id='global-view']/div/div/div/div[8]/div[2]/div"))
                        )
                finally:
                    pass
                    
                soup = bsoup(browser.page_source, 'html.parser')
                entry_lu = soup.find('div', {'class': 'live-comparison-entry active'})
                
                ps = entry_lu.find_all('li')
                
                entry_names = map(get_name, ps)
                new_names = [x for x in entry_names if x not in own_pct.keys()]
                new_i = [entry_names.index(n) for n in new_names]
                new_p = [ps[i] for i in new_i]
                if len(new_names) != 0:
                    print new_names
                page_new.extend(new_names)
                
                for p in new_p:
                    own_pct.update(get_player_info(p))
                
                browser.execute_script("scroll(0, 0);")
            except:
                print 'selection error'
            
            time.sleep(2)
        
        op = pd.DataFrame.from_dict(own_pct, orient='index')
        op.index.name = 'name'
        op.to_csv('data/contests/' + file_name)
        dbox = "c:/users/mworley/dropbox/gh_data/lineup_maker/"
        op.to_csv(dbox + file_name)
    
    pages_read.append([page_n, len(page_new)])
    last_entry_name = keep_names[-1]
    dfpr = pd.DataFrame(pages_read, columns=['page', 'new_names'])
    dfpr.to_csv('data/contests/progress/' + cid + '.csv')
    dfpr.to_csv(dbox + cid + '.csv')

    nxt_xp = '//*[@id="global-view"]/div/div/div/div[6]/div[2]/nav/div[2]/button[3]'
    browser.execute_script("scroll(0, 0);")
    nxt = browser.find_element_by_xpath(nxt_xp)
    nxt.click()
    time.sleep(2)

    page_n += 1
