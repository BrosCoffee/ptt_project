import requests
from bs4 import BeautifulSoup
import re
import time
import json

# The following method catched all the PTT Food pages' URL from year 2004 to today
urls = ['https://www.ptt.cc/bbs/Food/index{}.html'.format(str(i)) for i in range(1,7007)]
urls = urls[::-1]
url_list = urls[0:2] # <-- Change the range to assign the pages to crawl

start = time.time()
print('The PTT crawler program starts...')
# Get all the articles' URL in the given page
content_list = []
comments_list = []
except_list = []

page = len(url_list)
for url in url_list:
    print('The', page, 'page', url,'starts:')
    #page -= 1
    res = requests.get(url, verify=False)
    #time.sleep(2)
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
        #time.sleep(2)
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
                # Clean all the links
                content = re.sub(
                    '(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])',
                    '', content)
                if len(main_content) >= 2:
                    
                    comments = main_content[1]  # This section is all the comments
                    comments = comments.split('.html')
                    # Get the IP address
                    ip_addr = comments[0].split('※ 文章網址')
                    ip_addr = ip_addr[0].split('來自: ')
                    ip_addr = ip_addr[1]
                    if '(' in ip_addr:
                        ip_addr = ip_addr.split('(')
                        ip_addr = ip_addr[0]
                        ip_addr = ip_addr.replace('\n', '')
                    else:
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
                        {'URL': url2, 'Title': title, 'Time': date, 'IP': ip_addr, 'Content': content, '推文': push,
                         '噓文': boo, '總回文數': total_comment_count})
                    comments_list.append({'URL': url2, 'Comment': all_comments})
            except:
                except_list.append(url2)    
        else:
            except_list.append(url2)
    page -= 1
with open('test_content.json', 'w', encoding='utf-8') as file:
    json.dump(content_list, file, ensure_ascii= False)
with open('test_comments.json', 'w', encoding='utf-8') as file:
    json.dump(comments_list, file, ensure_ascii= False)
with open('test_log.json', 'w', encoding='utf-8') as file:
    json.dump(except_list, file, ensure_ascii= False)
end = time.time()
minute = round((end - start) / 60)
second = round((end - start) % 60)

print('Total time:', minute, 'm', second, 's')

###############################################
import numpy as np
import pandas as pd

ptt = pd.read_json('test_content.json',encoding='utf-8');

# Get the Location from the ip
from selenium import webdriver
#from webdriver_manager.chrome import ChromeDriverManager #For Mac OS users
import time

ip_list = list(ptt['IP'])

print('The IP to Location program starts...')

city_list = []
count = len(ip_list)
start = time.time()
#driver = webdriver.Chrome(ChromeDriverManager().install()) #For Mac OS users
driver = webdriver.Chrome(executable_path="chromedriver.exe") #For Windows users
driver.get('https://www.ez2o.com/App/Net/IP')
for ip_addr in ip_list:
    print(count,'...')
    #time.sleep(2)
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
print('Total time:',minute,'m',second,'s')

###############################################
# Convert IP into city name
# Base on the city name convert into North(1), Middel(2), South(3), East(4), and others(0) 
north = ['Keelung','Keelung City','Zhubei','Taipei','New Taipei City',' Taipei County','Taoyuan District','Hsinchu','Yilan County','Yilan','Zhongzheng','Datong','Zhongshan','Songshan','Da’an','Wanhua','Xinyi','Shilin','Beitou','Neihu','Nangang','Wenshan','Ren’ai','Anle','Nuannuan','Qidu','Wanli','Jinshan','Banqiao','Xizhi','Shenkeng','Shiding','Ruifang','Pingxi','Shuangxi','Gongliao','Xindian','Pinglin','Wulai','Yonghe','Zhonghe','Tucheng','Sanxia','Shulin','Yingge','Sanchong','Xinzhuang','Taishan','Linkou','Luzhou','Wugu','Bali','Tamsui','Sanzhi','Shimen','Toucheng','Jiaoxi','Zhuangwei','Yuanshan','Luodong','Sanxing','Datong','Wujie','Dongshan','Su’ao','Nan’ao','Xiangshan','Zhubei','Hukou','Xinfeng','Xinpu','Guanxi','Qionglin','Baoshan','Zhudong','Wufeng','Hengshan','Jianshi','Beipu','Emei','Zhongli','Pingzhen','Longtan','Yangmei','Xinwu','Guanyin','Guishan','Bade','Daxi','Fuxing','Dayuan','Luzhu','']
middle = ['Miaoli','Miaoli City','Yuanlin','Toufen Township','Taichung','Taichung City','Huwei','Nantou City','Puli Town','Douliu','Chang-hua','Yunlin County','Zhunan','Toufen','Sanwan','Nanzhuang','Shitan','Houlong','Tongxiao','Yuanli','Zaoqiao','Touwu','Gongguan','Dahu','Tai’an','Tongluo','Sanyi','Xihu','Zhuolan','Central Taichung','East Taichung','South Taichung','West Taichung','North Taichung','Beitun','Xitun','Nantun','Taiping','Dali','Wufeng','Wuri','Fengyuan','Houli','Shigang','Dongshi','Heping','Xinshe','Tanzi','Daya','Shengang','Dadu','Shalu','Longjing','Wuqi','Qingshui','Dajia','Waipu','Fenyuan','Huatan','Shengang','Yuanlin','Shetou','Yongjing','Puxin','Xihu','Dacun','Puyan','Tianzhong','Beidou','Tianwei','Pitou','Xizhou','Zhutang','Erlin','Dacheng','Fangyuan','Ershui','Zhongliao','Caotun','Guoxing','Puli','Ren’ai','Mingjian','Jiji','Shuili','Yuchi','Xinyi','Zhushan','Lugu','Dounan','Dapi','Huwei','Tuku','Baozhong','Dongshi','Taixi','Lunbei','Mailiao','Douliu','Linnei','Gukeng','Citong','Xiluo','Erlun','Beigang','Shuilin','Kouhu','Sihu','Yuanzhang',]
south = ['Chiayi City','Tainan City','Kaohsiung City','Pingtung City','Fanlu','Meishan','Zhuqi','Alishan','Zhongpu','Dapu','Shuishang','Lucao','Taibao','Puzi','Dongshi','Liujiao','Xingang','Minxiong','Dalin','Xikou','Yizhu','Budai','Anping','Annan','Yongkang','Guiren','Xinhua','Zuozhen','Yujing','Nanxi','Nanhua','Rende','Guanmiao','Longqi','Guantian','Madou','Jiali','Xigang','Qigu','Jiangjun','Xuejia','Beimen','Xinying','Houbi','Baihe','Dongshan','Liujia','Xiaying','Liuying','Yanshui','Shanhua','Danei','Shanshang','Xinshi','Anding','Xinxing','Qianjin','Lingya','Yancheng','Gushan','Qijin','Qianzhen','Sanmin','Nanzi','Xiaogang','Zuoying','Renwu','Dashe','Gangshan','Luzhu','Alian','Tianliao','Yanchao','Qiaotou','Ziguan','Mituo','Yong’an','Hunei','Fengshan','Daliao','Linyuan','Niaosong','Dashu','Qishan','Meinong','Liugui','Neimen','Shanlin','Jiaxian','Taoyuan','Namaxia','Maolin','Qieding','Sandimen','Wutai','Majia','Jiuru','Ligang','Gaoshu','Yanpu','Changzhi','Linluo','Zhutian','Neipu','Wandan','Chaozhou','Taiwu','Laiyi','Wanluan','Kanding','Xinpi','Nanzhou','Linbian','Donggang','Liuqiu','Jiadong','Xinyuan','Fangliao','Fangshan','Chunri','Shizi','Checheng','Mudan','Hengchun','Manzhou']
east = ['Hualien City','Hualien County','Taitung County','Taitung City','Ludao','Lanyu','Yanping','Beinan','Luye','Guanshan','Haiduan','Chishang','Donghe','Chenggong','Changbin','Taimali','Jinfeng','Dawu','Daren','Hualien','Xincheng','Xiulin','Ji’an','Shoufeng','Fenglin','Guangfu','Fengbin','Ruisui','Wanrong','Yuli','Zhuoxi','Fuli']

city_list2 = list(ptt['City'])

area_code = []
for city in city_list2:
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

ptt['Area'] = area_code


###############################################
ptt = ptt[ptt['Content'].notnull()]

# Clean the content and append a new column to the dataframe
content_list = list(ptt['Content'])

ptt_content_clean = []

for i in range(len(content_list)):
    #clean space
    ptt_content_clean_space = content_list[i]
    a2 = ptt_content_clean_space.replace(' ','')
    #clean url
    url_pattern = r'((http|ftp|https):\/\/)?[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'
    text = re.sub(url_pattern, ' ', a2)
    #clean all marks
    ptt_content = re.sub('[^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a]','',text)
    #clean XD
    final_ptt_content = re.sub('XDD*','',ptt_content)
    ptt_content_clean.append(final_ptt_content)


# Adding a new column named 'Clean'
ptt['Clean'] = ptt_content_clean
# Dropping the original 'Content' column
ptt = ptt.drop(labels='Content', axis= 1)
# Rename 'Clean' to 'Content'
ptt = ptt.rename(index = str , columns = {'Clean':'Content'})
#ptt = ptt.drop(labels='Comment', axis= 1)

# Insert into the database
import mysql.connector

cnx = mysql.connector.connect(user='ray', password='Taiwan#1',
                              host='127.0.0.1',
                              database='ptt_db')
cursor = cnx.cursor()
for i in range(0,len(ptt)):
    
    content_list = {'Area': int(ptt.iloc[i]['Area']),'City': str(ptt.iloc[i]['City']),'Title': str(ptt.iloc[i]['Title']),'URL': str(ptt.iloc[i]['URL']), 
                    'IP': str(ptt.iloc[i]['IP']),'Content': str(ptt.iloc[i]['Content']),
                    '總回文數': int(ptt.iloc[i]['總回文數']), 'Time': str(ptt.iloc[i]['Time']),'噓文': int(ptt.iloc[i]['噓文']),
                    '推文': int(ptt.iloc[i]['推文'])}    
    #Insert into Database
    add_article = ("INSERT INTO test"
                   "(Area,City,Title,URL,IP,Content,總回文數,Time,噓文,推文) "
                   "VALUES (%(Area)s,%(City)s,%(Title)s, %(URL)s, %(IP)s,%(Content)s,%(總回文數)s,%(Time)s,%(噓文)s,%(推文)s)")
    # Insert new article
    cursor.execute(add_article,content_list)
    # Make sure data is committed to the database
    cnx.commit()
    print(i,":",'Inserted into the database.')
cursor.close()
cnx.close()
with open('clean_test_content.json','w',encoding='utf-8') as file: # 3. Remember to change the output file name!! 
    ptt.to_json(file,force_ascii=False,orient='records')
print('Finished')