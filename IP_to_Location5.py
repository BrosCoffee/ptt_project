# Convert IP into city name
# Base on the city name convert into North(1), Middel(2), South(3), East(4), and others(0) 
import numpy as np
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager #For Mac OS users
import time

file_name = './3_5_content.json' # 1. Choose the file
ptt = pd.read_json(file_name)
ip_list = list(ptt['IP'])

print('The program starts...')

city_list = []
count = len(ip_list)
start = time.time()
driver = webdriver.Chrome(ChromeDriverManager().install()) #For Mac OS users
#driver = webdriver.Chrome(executable_path="chromedriver.exe") #For Windows users
driver.get('https://www.ez2o.com/App/Net/IP')
for ip_addr in ip_list:
    print(count,'...')
    count -= 1
    elem = driver.find_element_by_xpath("//input[@id='QueryIP']").clear()
    elem = driver.find_element_by_xpath("//input[@id='QueryIP']")
    elem.send_keys(ip_addr) # ex: 218.173.71.162
    elem = driver.find_element_by_xpath("//button[@class='btn btn-primary']")
    elem.click()
    elem = driver.find_element_by_xpath("//tbody/tr[@class='active'][3]/td[2]")
    city_list.append(elem.text)
driver.close()
end = time.time()

minute = round((end - start)/60)
second = round((end - start)%60)

ptt['City'] = city_list
with open('3_5_content.json', 'w', encoding='utf-8') as file: # 2. Change the name for the output file
        ptt.to_json(file, force_ascii=False, orient='records')
print('Finished')
print('Total time:',minute,'m',second,'s')