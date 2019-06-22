import numpy as np
import pandas as pd

# Convert IP into city name
# Base on the city name convert into North(1), Middel(2), South(3), East(4), and others(0) 
north = ['Keelung','Keelung City','Zhubei','Taipei','New Taipei City',' Taipei County','Taoyuan District','Hsinchu','Yilan County','Yilan','Zhongzheng','Datong','Zhongshan','Songshan','Da’an','Wanhua','Xinyi','Shilin','Beitou','Neihu','Nangang','Wenshan','Ren’ai','Anle','Nuannuan','Qidu','Wanli','Jinshan','Banqiao','Xizhi','Shenkeng','Shiding','Ruifang','Pingxi','Shuangxi','Gongliao','Xindian','Pinglin','Wulai','Yonghe','Zhonghe','Tucheng','Sanxia','Shulin','Yingge','Sanchong','Xinzhuang','Taishan','Linkou','Luzhou','Wugu','Bali','Tamsui','Sanzhi','Shimen','Toucheng','Jiaoxi','Zhuangwei','Yuanshan','Luodong','Sanxing','Datong','Wujie','Dongshan','Su’ao','Nan’ao','Xiangshan','Zhubei','Hukou','Xinfeng','Xinpu','Guanxi','Qionglin','Baoshan','Zhudong','Wufeng','Hengshan','Jianshi','Beipu','Emei','Zhongli','Pingzhen','Longtan','Yangmei','Xinwu','Guanyin','Guishan','Bade','Daxi','Fuxing','Dayuan','Luzhu','']
middle = ['Miaoli','Miaoli City','Yuanlin','Toufen Township','Taichung','Taichung City','Huwei','Nantou City','Puli Town','Douliu','Chang-hua','Yunlin County','Zhunan','Toufen','Sanwan','Nanzhuang','Shitan','Houlong','Tongxiao','Yuanli','Zaoqiao','Touwu','Gongguan','Dahu','Tai’an','Tongluo','Sanyi','Xihu','Zhuolan','Central Taichung','East Taichung','South Taichung','West Taichung','North Taichung','Beitun','Xitun','Nantun','Taiping','Dali','Wufeng','Wuri','Fengyuan','Houli','Shigang','Dongshi','Heping','Xinshe','Tanzi','Daya','Shengang','Dadu','Shalu','Longjing','Wuqi','Qingshui','Dajia','Waipu','Fenyuan','Huatan','Shengang','Yuanlin','Shetou','Yongjing','Puxin','Xihu','Dacun','Puyan','Tianzhong','Beidou','Tianwei','Pitou','Xizhou','Zhutang','Erlin','Dacheng','Fangyuan','Ershui','Zhongliao','Caotun','Guoxing','Puli','Ren’ai','Mingjian','Jiji','Shuili','Yuchi','Xinyi','Zhushan','Lugu','Dounan','Dapi','Huwei','Tuku','Baozhong','Dongshi','Taixi','Lunbei','Mailiao','Douliu','Linnei','Gukeng','Citong','Xiluo','Erlun','Beigang','Shuilin','Kouhu','Sihu','Yuanzhang',]
south = ['Chiayi City','Tainan City','Kaohsiung City','Pingtung City','Fanlu','Meishan','Zhuqi','Alishan','Zhongpu','Dapu','Shuishang','Lucao','Taibao','Puzi','Dongshi','Liujiao','Xingang','Minxiong','Dalin','Xikou','Yizhu','Budai','Anping','Annan','Yongkang','Guiren','Xinhua','Zuozhen','Yujing','Nanxi','Nanhua','Rende','Guanmiao','Longqi','Guantian','Madou','Jiali','Xigang','Qigu','Jiangjun','Xuejia','Beimen','Xinying','Houbi','Baihe','Dongshan','Liujia','Xiaying','Liuying','Yanshui','Shanhua','Danei','Shanshang','Xinshi','Anding','Xinxing','Qianjin','Lingya','Yancheng','Gushan','Qijin','Qianzhen','Sanmin','Nanzi','Xiaogang','Zuoying','Renwu','Dashe','Gangshan','Luzhu','Alian','Tianliao','Yanchao','Qiaotou','Ziguan','Mituo','Yong’an','Hunei','Fengshan','Daliao','Linyuan','Niaosong','Dashu','Qishan','Meinong','Liugui','Neimen','Shanlin','Jiaxian','Taoyuan','Namaxia','Maolin','Qieding','Sandimen','Wutai','Majia','Jiuru','Ligang','Gaoshu','Yanpu','Changzhi','Linluo','Zhutian','Neipu','Wandan','Chaozhou','Taiwu','Laiyi','Wanluan','Kanding','Xinpi','Nanzhou','Linbian','Donggang','Liuqiu','Jiadong','Xinyuan','Fangliao','Fangshan','Chunri','Shizi','Checheng','Mudan','Hengchun','Manzhou']
east = ['Hualien City','Hualien County','Taitung County','Taitung City','Ludao','Lanyu','Yanping','Beinan','Luye','Guanshan','Haiduan','Chishang','Donghe','Chenggong','Changbin','Taimali','Jinfeng','Dawu','Daren','Hualien','Xincheng','Xiulin','Ji’an','Shoufeng','Fenglin','Guangfu','Fengbin','Ruisui','Wanrong','Yuli','Zhuoxi','Fuli']

file_name = './3_5_content.json' # 1. Choose the file. Must run "IP_to_Location5" FIRST!!
ptt = pd.read_json(file_name)
city_list = list(ptt['City'])

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

ptt['Area'] = area_code

with open('3_5_test_content.json'.format(file_name), 'w', encoding='utf-8') as file: # Change the output file name
    ptt.to_json(file, force_ascii=False, orient='records')
print('Finished.')
