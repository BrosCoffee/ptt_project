import time
import json
import numpy as np
import pandas as pd
import datetime
import requests
import re
from bs4 import BeautifulSoup 
from selenium import webdriver


# # The following method catched all the PTT Food pages' URL from year 2004 to today
# urls = ['https://www.ptt.cc/bbs/Food/index{}.html'.format(str(i)) for i in range(7000,7003)]
# urls = urls[::-1]
# url_list = urls[1:2] # <-- Change the range to assign the pages to crawl

res = requests.get('https://www.ptt.cc/bbs/Food/index.html', verify=False)
soup = BeautifulSoup(res.text,'html.parser')

page_url_list = []

#取得上一頁的ptt_page_url
page_url = soup.select('a.btn.wide')[1]
ptt_page_url = 'https://www.ptt.cc'+page_url.get('href')
res2 = requests.get(ptt_page_url)
new_url =BeautifulSoup(res2.text,'html.parser')

#將上一頁的ptt_page_url的index分割
page_now = ptt_page_url.split('index')[1].replace(".html","")
page_number = int(page_now)
page_number = page_number + 2
for i in range(page_number):
    web_url = f'https://www.ptt.cc/bbs/Food/index{i}.html'
    page_url_list.append(web_url)

#取得最後2頁的ptt_page_url (可變)
url_list = page_url_list[-4:] # <= change here!!!

start = time.time()
print('PTT program starts...')
# Get all the articles' URL in the given page
content_list = []
comments_list = []
except_list = []

page = len(url_list)
for url in url_list:
    print('The', page, 'page', url,'starts:')
    #page -= 1
    res = requests.get(url, verify=False)
#     time.sleep(2)
    html_str = res.text
    soup = BeautifulSoup(html_str)

    title_list = []

    for i in soup.select('.title a'):
        route = 'https://www.ptt.cc' + i.get('href')
        title_list.append(route)
    # print(title_list)
    num = len(title_list)
    # Finally, we are able to get the contents
    for url2 in title_list:
        print('The page',page,num, url2)
        num -= 1
#         time.sleep(2)
        r2 = requests.get(url2)
        soup = BeautifulSoup(r2.text, 'html')
        main_content = soup.select('#main-content')

        info = soup.select('.article-metaline')
        # The main content is the whole thing except the article's info
        info = [i.text for i in info]
        # Get the title
        if info != []:
            try:
                title = info[1]
                # Get the time
                date = info[2].replace('時間', '')
                info.insert(1, '看板Food')
                info_str = ''.join(info)
                # Clean the title, author, and other info
                main_content = main_content[0].text.replace(info_str, '')

                # Split the whole thing into the main content and the comments sections
                main_content = main_content.split('※ 發信站: 批踢踢實業坊')
                content = main_content[0]  # This is the main content
                # Start clean the content
                # Clean out '\n'
                content = content.replace('\n', '')  
                #clean url
                url_pattern = r'((http|ftp|https):\/\/)?[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'
                text = re.sub(url_pattern, ' ', content)
                #clean all marks
                ptt_content = re.sub('[^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a]','',text)
                #clean XD
                content = re.sub('XDD*','',ptt_content) 
            
                if len(main_content) >= 2:
                    
                    comments = main_content[1]  # This section is all the comments
                    comments = comments.split('.html')
                    # Get the IP address
                    ip_addr = comments[0].split('※ 文章網址')
                    ip_addr = ip_addr[0].split('來自: ')
                    ip_addr = ip_addr[1]
                    ip_addr = ip_addr.replace('\n', '')
                    comments = comments[1]
                    comments = comments.split('\n')
                    
                    # Count pushes and boos, and append all comments
                    push = 0
                    boo = 0
                    comment_count = 0
                    all_comments = ''
                    for i in comments:
                        if len(i) != 0:
                            if i[0] == '推':
                                push += 1
                            elif i[0] == '噓':
                                boo += 1
                            elif i[0] == '→':
                                comment_count += 1
                            i = i.split(' ')
                            if i[0] != '※':
                                i = i[2:-2]
                                i = ''.join(i)
                                all_comments += i

                    total_comment_count = comment_count + push + boo

                    content_list.append(
                        {'url': url2, 'title': title, 'time': date, 'ip': ip_addr, 'content': content, 'push': push,
                         'boo': boo, 'total': total_comment_count})
                    comments_list.append({'url': url2, 'comment': all_comments})
            except:
                except_list.append(url2)    
        else:
            except_list.append(url2)
    page -= 1


# Automatic naming the file 
today = str(datetime.date.today())
today = today.replace('-','_')

with open('ptt_content{}.json'.format(today), 'w', encoding='utf-8') as file:
    json.dump(content_list, file, ensure_ascii= False)
with open('ptt_comment{}.json'.format(today), 'w', encoding='utf-8') as file:
    json.dump(comments_list, file, ensure_ascii= False)
with open('ptt_log{}.json'.format(today), 'w', encoding='utf-8') as file:
    json.dump(except_list, file, ensure_ascii= False)

##############################################

##讀取剛才爬好的檔案
file_name = 'ptt_content{}.json'.format(today)
ptt_today = pd.read_json(file_name, encoding = 'utf-8')

#過濾掉標題有公告的列
ptt_new = ptt_today[ptt_today['title'].str.contains('公告') != True]    
    
#將ptt_id有(台灣的分割)
ip_cut = ptt_new['ip'].to_string()
ip_adress = ip_cut.split()

#將取好乾淨ptt_ip存回df
ptt_new['ip'] = ip_adress[1:len(ip_adress):3]


##############################################
# Convert IP into city name
# Base on the city name convert into North(1), Middel(2), South(3), East(4), and others(0) 

ip_list = list(ptt_new['ip'])

print('Convert IP into city name. Starts...')

city_list = []
count = len(ip_list)
start = time.time()
#driver = webdriver.Chrome(ChromeDriverManager().install()) #For Mac OS users
driver = webdriver.Chrome(executable_path="chromedriver.exe") #For Windows users
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

ptt_new['city'] = city_list

##############################################
# Convert IP into city name
# Base on the city name convert into North(1), Middel(2), South(3), East(4), and others(0) 


north = ['Keelung','Keelung City','Zhubei','Taipei','New Taipei City',' Taipei County','Taoyuan District','Hsinchu','Yilan County','Yilan']
middle = ['Miaoli','Miaoli City','Yuanlin','Toufen Township','Taichung','Taichung City','Huwei','Nantou City','Puli Town','Douliu','Chang-hua','Yunlin County']
south = ['Chiayi City','Tainan City','Kaohsiung City','Pingtung City']
east = ['Hualien City','Hualien County','Taitung County','Taitung City']

city_list = list(ptt_new['city'])

area_code = []
for city in city_list:
    if city in north:
        area_code.append(1)
    elif city in middle:
        area_code.append(2)
    elif city in south:
        area_code.append(3)
    elif city in east:
        area_code.append(4)
    else:
        area_code.append(0)

ptt_new['area'] = area_code

# with open('ptt_new_10page_content_final.json'.format(file_name), 'w', encoding='utf-8') as file: # Change the output file name
#     ptt.to_json(file, force_ascii=False, orient='records')

##############################################
##將ptt_time分割
#取week
weekday_cut = ptt_new['time'].to_string()
weekday = weekday_cut.split()
#將取好乾淨ptt_week另存df欄位
ptt_new['weekday'] = weekday[1:len(weekday):6]


#取month
month_cut = ptt_new['time'].to_string()
month = month_cut.split()
ptt_new['month'] = month[2:len(month):6]

#取day
day_cut = ptt_new['time'].to_string()
day = day_cut.split()
ptt_new['day'] = day[3:len(weekday):6]

#取time
time_cut = ptt_new['time'].to_string()
time = time_cut.split()
ptt_new['time2'] = time[4:len(weekday):6]
 
#取year
year_cut = ptt_new['time'].to_string()
year = year_cut.split()
ptt_new['year'] = weekday[5:len(weekday):6]

##############################################
##轉換weekday成數字
ptt_new['weekday'].replace('Mon',1,inplace= True) #inplace = true改變原數據
ptt_new['weekday'].replace('Tue',2,inplace= True)
ptt_new['weekday'].replace('Wed',3,inplace= True)
ptt_new['weekday'].replace('Thu',4,inplace= True)
ptt_new['weekday'].replace('Fri',5,inplace= True)
ptt_new['weekday'].replace('Sat',6,inplace= True)
ptt_new['weekday'].replace('Sun',7,inplace= True)

##轉換month成數字
ptt_new['month'].replace('Jan',1,inplace= True) #inplace = true改變原數據
ptt_new['month'].replace('Feb',2,inplace= True)
ptt_new['month'].replace('Mar',3,inplace= True)
ptt_new['month'].replace('Apr',4,inplace= True)
ptt_new['month'].replace('May',5,inplace= True)
ptt_new['month'].replace('Jun',6,inplace= True)
ptt_new['month'].replace('Jul',7,inplace= True)
ptt_new['month'].replace('Aug',8,inplace= True)
ptt_new['month'].replace('Sep',9,inplace= True)
ptt_new['month'].replace('Oct',10,inplace= True)
ptt_new['month'].replace('Nov',11,inplace= True)
ptt_new['month'].replace('Dec',12,inplace= True)

##合併year,month,day欄位成date欄位
year = ptt_new['year'].astype('str')
month = ptt_new['month'].astype('str')
day = ptt_new['day'].astype('str')
ptt_new['date'] = year+'/'+month+'/'+day

#drop time欄位
ptt_new = ptt_new.drop("time", axis = 1)

#修改time2名稱成time
ptt_new = ptt_new.rename(columns={'time2':'time'})

##############################################
# Insert into the database
import mysql.connector
import time
cnx = mysql.connector.connect(user='june', password='june',
                              host='192.168.35.119',
                              database='ptt_db')
cursor = cnx.cursor()
query = ("SELECT url FROM test_update;")  # check the id list, and use it as the base to either UPDATE or INSERT 
cursor.execute(query)

url_list =[]

for i in cursor:
    url_list.append(i[0])
    

for i in range(len(ptt_new)):
    content_list = {'area': int(ptt_new.iloc[i]['area']),'city': str(ptt_new.iloc[i]['city']), 
                        'content': str(ptt_new.iloc[i]['content']),'time': str(ptt_new.iloc[i]['time']),'title': str(ptt_new.iloc[i]['title']),
                        'day': str(ptt_new.iloc[i]['day']),'weekday': str(ptt_new.iloc[i]['weekday']),'year': str(ptt_new.iloc[i]['year']),
                        'month': str(ptt_new.iloc[i]['month']),'date': str(ptt_new.iloc[i]['date']),'time': str(ptt_new.iloc[i]['time']),
                        'push': int(ptt_new.iloc[i]['push']),'boo': int(ptt_new.iloc[i]['boo']),'total': int(ptt_new.iloc[i]['total']),'ip': str(ptt_new.iloc[i]['ip']),'url': str(ptt_new.iloc[i]['url'])}
    if ptt_new.iloc[i]['url'] in url_list: # Update  
        #Insert into Database
        update_article = "UPDATE test_update SET date = %(date)s, year = %(year)s, month = %(month)s, day = %(day)s , area = %(area)s, city = %(city)s , weekday = %(weekday)s, time = %(time)s, title = %(title)s ,push = %(push)s, boo = %(boo)s, total = %(total)s, ip = %(ip)s, content = %(content)s WHERE url = %(url)s"
        # Insert new article
        cursor.execute(update_article,content_list)
        # Make sure data is committed to the database
        cnx.commit()
        print(i,":",'Updated the database.')
    else: # Insert    
        #Insert into Database
        add_article = ("INSERT test_update "
                       "(url,area,city,content,ip,date,time,title, weekday,year,month,day, push, boo, total) "
                       "VALUES (%(url)s, %(area)s, %(city)s, %(content)s, %(ip)s , %(date)s ,%(time)s, %(title)s ,%(weekday)s,%(year)s,%(month)s,%(day)s,%(push)s,%(boo)s ,%(total)s);")
        # Insert new article
        cursor.execute(add_article,content_list)
        # Make sure data is committed to the database
        cnx.commit()
        print(i,":",'Inserted into the database.')
        
cursor.close()
cnx.close()
##############################################
        
end = time.time()
minute = round((end - start) / 60)
second = round((end - start) % 60)
print('Finished')
print('Total time:', minute, 'm', second, 's')