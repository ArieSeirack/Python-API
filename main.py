import os
import requests
import json
import time
import csv
from PyQt5.QtWidgets import QApplication,QMainWindow, QWidget, QFileDialog

from interface import Ui_MainWindow

# 链接url
def get_to_link():
    try:
        r = requests.get("https://box.maoyan.com/promovie/api/box/second.json")
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        print("链接错误！！！")
        return ''

    # json化字符串


def json_text(text):
    jd = json.loads(text)
    return jd


# 返回实时日期
def date_time(jd):
    ja = jd['data']
    date = ja['queryDate']  # 返回日期
    alltime = ja['updateInfo'].split()[1]  # 返回时间
    money = ja['totalBox'] + ja['totalBoxUnit']  # 返回总票房，格式为数字+‘万’
    return date, alltime, money


# 返回影片票房
def movie_price(jd):
    jl = jd['data']['list']
    for i, jls in enumerate(jl, 1):
        name = jls['movieName']  # 影片名

        try:
            days = jls['releaseInfo'][2]  # 上映时间
            if jls['releaseInfo'][3]!='天':
                days += jls['releaseInfo'][3]
        except:
            days = '点映'


        '''if jls['releaseInfo'][2] == '场':  # 不知道为什么会是“场”
            days = '点映'
        else:
            if jls['releaseInfo'][3] != '天':
                num2 = jls['releaseInfo'][3]
            else:
                num2=''

            days = jls['releaseInfo'][2]+num2  # 上映时间'''

        totalmoney = jls['sumBoxInfo']  # 影片总票房
        mainmoney = jls['boxInfo']  # 综合票房
        moneyrate = jls['boxRate']  # 票房占比
        shownumber = jls['showInfo']  # 排片场次
        showrate = jls['showRate']  # 排片占比
        people = jls['avgShowView']  # 场均人次
        showpeople = jls['avgSeatView']  # 上座率

        yield i, name, days, totalmoney, mainmoney, moneyrate, shownumber, showrate, people, showpeople

    # 创建文件夹


def makeasocket(path):
    if not os.path.exists(path):
        os.makedirs(path)

    # 保存到csv中


def save_to_csv(path, date, alltime, money, movie_price):  # 这个保存是append添加，不是rewrite的添加方法
    with open(path + '猫眼电影专业版实时数据.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(['日期', date, '', '时间', alltime, '', '总票房', money])
        writer.writerow(['排名', '影片名', '上映时间(/天)', '影片总票房', '综合票房(/万)', '票房占比(%)', '排片场次', '排片占比(%)', '场均人次', '上座率(%)'])
        for movie in movie_price:
            writer.writerow(
                [movie[0], movie[1], movie[2], movie[3], movie[4], movie[5], movie[6], movie[7], movie[8], movie[9]])

# 10个格子分别代表对应位置的数据


import sys
from PyQt5.QtWidgets import QApplication, QMainWindow



class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)




def main():
    path = 'D:/数据/猫眼电影专业版数据/'
    makeasocket(path)  # 创建文件夹
    text = get_to_link()
    jd = json_text(text)
    app = QApplication(sys.argv)
    myWin = MyMainWindow()

    date, alltime, money = date_time(jd)

    # 显示主数据栏
    myWin.DateShow.setText(date)
    myWin.TimeShow.setText(alltime)
    myWin.SumShow.setText(money)

    ranklist = []
    rlist = ''
    namelist = []
    nlist = ''
    cursumlist = []
    cslist = ''
    showdaylist = []
    sdlist = ''
    totalboxlist = []
    tblist = ''

    print('***' * 46)
    print('{:>10s}:{}{:>10s}:{}{:>10s}：{}'.format('日期', date, '时间', alltime, '总票房', money))
    print('---' * 46)
    print('{:^6s}{:^20s}{:^10s}{:^12s}{:^12s}{:^10s}{:^10s}{:^6s}{:^6s}{:^6s}'.format('排名', '影片名', '上映时间(/天)',
                                                                                      '影片总票房(/亿)', '综合票房(/万)',
                                                                                      '票房占比(%)', '排片场次', '排片占比(%)',
                                                                                      '场均人次', '上座率(%)'))
    print('---' * 46)
    for movie in movie_price(jd):
        print('{:^6d}{:^20s}{:^20s}{:^20s}{:^12s}{:^11s}{:^13s}{:^10s}{:^10s}{:^10s}'.format(movie[0], movie[1],
                                                                                             movie[2], movie[3],
                                                                                             movie[4], movie[5],
                                                                                             movie[6], movie[7],
                                                                                             movie[8], movie[9]))

        print('---' * 46)
        myWin.comboBox_ChooseName.addItem(movie[1])
        ranklist.append(str(movie[0]))
        namelist.append(movie[1])
        showdaylist.append(movie[2])
        totalboxlist.append(movie[3])
        cursumlist.append(movie[4])

    for rank in ranklist:
        rlist += rank
        rlist += '\n'

    for name in namelist:
        nlist += name
        nlist += '\n'

    for sd in showdaylist:
        sdlist += sd
        sdlist += '\n'

    for cursum in cursumlist:
        cslist += cursum
        cslist += '万\n'

    for tb in totalboxlist:
        tblist += tb
        tblist += '\n'

    myWin.RankList.setText(rlist)
    myWin.NameList.setText(nlist)
    myWin.ShowDaysList.setText(sdlist)
    myWin.CurSumList.setText(cslist)
    myWin.TotalBoxList.setText(tblist)



    def showdetails():
        name = myWin.comboBox_ChooseName.currentText()
        for n in movie_price(jd):
            if n[1] == name:
                myWin.BoxRate.setText(n[5])
                myWin.ShowNumber.setText(n[6])
                myWin.ShowRate.setText(n[7])
                myWin.avgPeople.setText(n[8])
                myWin.ShowPeople.setText(n[9])
        myWin.MovieName.setText(name)

    myWin.ChooseConfirmed.clicked.connect(showdetails)

    # save_to_csv(path, date, alltime, money, movie_price(jd))

    myWin.show() # 显示窗口
    sys.exit(app.exec_())  # 进入这个GUI的循环之后就不会出来了直到关闭





if __name__ == "__main__":
    main()
    '''app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())  # 进入这个GUI的循环之后就不会出来了直到关闭'''

