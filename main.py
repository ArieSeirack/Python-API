import os
import requests
import json
import csv
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
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


# 返回实时日期，处理各个数据
def date_time(jd):
    ja = jd['data']
    date = ja['queryDate']  # 返回日期
    alltime = ja['updateInfo'].split()[1]  # 返回时间
    money = ja['totalBox'] + ja['totalBoxUnit']  # 返回总票房，格式为数字+‘万’
    return date, alltime, money


# 返回影片票房，处理各个数据
def movie_price(jd):
    jl = jd['data']['list']
    for i, jls in enumerate(jl, 1):
        name = jls['movieName']  # 影片名

        try:
            days = jls['releaseInfo'][2]  # 上映时间
            if jls['releaseInfo'][3] != '天':
                days += jls['releaseInfo'][3]
        except:
            days = '点映'

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


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)


class Film():
    # 初始化类，十个属性分别为排名，名字，上映天数，总票房，当日票房，票房占比，排片场次，排片占比，场均人数，上座率
    def __init__(self, ra, na, sd, tm, mm, mr, sn, sr, pp, sp):
        self.rank = ra
        self.name = na
        self.showday = sd
        self.totalmoney = tm
        self.mainmoney = mm
        self.moneyrate = mr
        self.shownumber = sn
        self.showrate = sr
        self.people = pp
        self.showpeople = sp

    def details(self):  # 返回票房占比，排片场次，排片占比，场均人数，上座率
        yield self.moneyrate, self.shownumber, self.showrate, self.people, self.showpeople


def main():  # 程序运行的主函数
    #用来储存电影list
    filmlist = []
    # 用来暂存影片信息的一些list，
    rlist = ''
    nlist = ''
    cslist = ''
    sdlist = ''
    tblist = ''

    text = get_to_link()  # 获取数据
    jd = json_text(text)  # json化
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    date, alltime, money = date_time(jd)  # 获取当前的日期和时间以及当日总票房

    # 两个自定义的槽函数
    def savetofile():  # 按钮点击后将实时数据保存到文件
        path = 'D:/数据/猫眼电影专业版数据/'
        makeasocket(path)  # 创建文件夹
        save_to_csv(path, date, alltime, money, movie_price(jd))
        QMessageBox.information(myWin, "保存提示", "保存成功！",
                                        QMessageBox.Yes, QMessageBox.Yes)

    def showdetails():  # 按钮点击后显示出所选影片的具体信息
        name = myWin.comboBox_ChooseName.currentText()
        for fi in filmlist:  # 此处在电影列表中寻找名字为当前所要查询的电影，然后打印出它的详细信息
            if fi.name == name:
                deinf = fi.details()  # 创造一个生成器实例
                info = next(deinf)  # 执行next方法获取一组返回值
                myWin.BoxRate.setText(info[0])
                myWin.ShowNumber.setText(info[1])
                myWin.ShowRate.setText(info[2])
                myWin.avgPeople.setText(info[3])
                myWin.ShowPeople.setText(info[4])
                myWin.MovieName.setText(name)
                break

    # 显示主数据栏
    myWin.DateShow.setText(date)
    myWin.TimeShow.setText(alltime)
    myWin.SumShow.setText(money)

    # 两个信号和两个槽的连接
    myWin.ChooseConfirmed.clicked.connect(showdetails)
    myWin.FileSave.clicked.connect(savetofile)

    for movie in movie_price(jd):  # 从json化的数据中获取各个影片的主要信息
        # 赋予certainmovie实例各个属性
        cmovie = Film(
            movie[0], movie[1], movie[2], movie[3], movie[4],
            movie[5], movie[6], movie[7], movie[8], movie[9])

        filmlist.append(cmovie)
        myWin.comboBox_ChooseName.addItem(cmovie.name)

    # 分别获取各影片的各个信息，储存在各list中
    for fi in filmlist:
        rlist += str(fi.rank)+'\n'
        nlist += fi.name+'\n'
        sdlist += fi.showday+'\n'
        cslist += fi.mainmoney+'万\n'
        tblist += fi.totalmoney+'\n'

    # 显示各电影的主要信息
    myWin.RankList.setText(rlist)
    myWin.NameList.setText(nlist)
    myWin.ShowDaysList.setText(sdlist)
    myWin.CurSumList.setText(cslist)
    myWin.TotalBoxList.setText(tblist)

    myWin.show()  # 显示窗口
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
