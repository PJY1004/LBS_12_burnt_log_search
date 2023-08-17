import ftplib
import os
import pandas as pd
from datetime import datetime
import gzip
import shutil
import tkinter as tk
import win32api

def soc_burnt():
    ans = name.get()  # entry창에 적힌 데이터를 변수 a로 입력받음.
    folder_path = "./"  # folder_path 상엔 항상 빈파일이라도 monitor_standard.CSV가 위치해야함!
    g = open(folder_path + ans + "_LBUF_Burnt_Log.csv", 'w')
    g.write("Number,Site,Test Name,Channel,Low,Measured(mA),High,Force,Loc,File Name\n")
    g.close()

    def item_search():
        for each_file_name in os.listdir("./"):
            if ("std" in each_file_name) or ("_F_" in each_file_name):
                os.remove("./" + each_file_name)

        for each_file_name in os.listdir(folder_path):
            if each_file_name[-8:] == '.stxt.gz':

                file_name = folder_path + each_file_name
                with gzip.open(file_name, 'rb') as f_in:
                    with open(file_name[:-3], 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(file_name)
                file_name = folder_path + each_file_name[:-3]

                b = open(folder_path + "monitor_standard.CSV", 'r')
                lines = b.readlines()
                monitor_standard = {'모니터링 ITEM': [],  # 모니터링 ITEM : Test Item
                                    'detect value(mA)': [],  # detect value(mA) : 해당 item의 burnt warning 기준
                                    'detect limit': [],
                                    # detect limit : 해당 item의 burnt warning 횟수 기준.. limit 횟수 초과로 기준 이상을 감지하면 로그를 저장함.
                                    'detect count': []}  # detect count : 추후에 이 변수에 limit 초과 횟수를 저장해 로그 저장 여부를 결정하게 됨.
                monitor_standard_count = 0
                for line in lines:  # 'monitor_standard.CSV'파일의 내용을 저장해 사용할 수 있도록 함.
                    monitor_standard_count += 1
                    if monitor_standard_count >= 2:
                        line = line.split(',')
                        monitor_standard['모니터링 ITEM'].append(line[0])
                        monitor_standard['detect value(mA)'].append(float(line[1]))
                        monitor_standard['detect limit'].append(int(line[2]))
                        monitor_standard['detect count'].append(0)
                b.close

                ########## 단위 감지해 계산하기 쉽게 변환하는 함수 unit ##########
                def unit(lst):  # mili, micro 단위 쓰지 않고 계산할 수 있도록 mA 단위는 1000, uA 단위는 100000으로 나눔.
                    if lst[4] == 'N/A':
                        if lst[6] == 'mA':
                            lst[5] = float(lst[5]) / 1000
                        if lst[6] == 'uA':
                            lst[5] = float(lst[5]) / 1000000
                        if lst[6] == 'nA':
                            lst[5] = float(lst[5]) / 1000000000
                    else:
                        if lst[7] == 'mA':
                            lst[6] = float(lst[6]) / 1000
                        if lst[7] == 'uA':
                            lst[6] = float(lst[6]) / 1000000
                        if lst[7] == 'nA':
                            lst[6] = float(lst[6]) / 1000000000
                    return lst

                #################################################################

                ########## 단위변환 원상복귀시키는 함수 unit_reverse ##########
                def unit_reverse(lst):  # mili, micro 단위로 다시 환산함.
                    if lst[4] == 'N/A':
                        if lst[6] == 'mA':
                            lst[5] = round(float(lst[5]) * 1000, 4)
                        if lst[6] == 'uA':
                            lst[5] = round(float(lst[5]) * 1000, 4)
                        if lst[6] == 'nA':
                            lst[5] = round(float(lst[5]) * 1000, 4)
                        del lst[6]
                    else:
                        if lst[7] == 'mA':
                            lst[6] = round(float(lst[6]) * 1000, 4)
                        if lst[7] == 'uA':
                            lst[6] = round(float(lst[6]) * 1000, 4)
                        if lst[7] == 'nA':
                            lst[6] = round(float(lst[6]) * 1000, 4)
                        del lst[7]

                    return lst

                ###############################################################
                file_path = file_name
                print("reading..", file_path)

                # 찾아낸 가장 최근 수정된 .stxt(현재 진행 중인 test log)를 읽음
                f = open(file_path, 'r')  # 복사본 읽기(read 모드로 열기)
                new_item_line = [['Number', 'Site', 'Test_Name', 'Channel', 'Low', 'Measured(mA)', 'High', 'Force',
                                  'Loc','File Name']]  # ['Number','Site','Test Name','Pin','Channel','Low','Measured','High','Force','Loc'] 가 데이터프레임 1행 될 것..
                lines = f.readlines()

                # 모니터링 대상 item에 대해 limit값을 넘을 시 test log의 해당 item명과 몇번째 line인지를 출력창에 표시.
                i = 0
                print("\n[" + str(
                    datetime.now()) + "]\n--------------------------------------------------")  # 현재 날짜 및 시간 그리고 구분선 "-----" 출력함.
                for line in lines:  # lines는 읽은 (COPY) 파일의 각 줄이 라나의 요소가 되는 리스트로
                    i += 1
                    for a in range(0, len(monitor_standard['모니터링 ITEM'])):  #
                        if monitor_standard['모니터링 ITEM'][a] in line:
                            line = unit(line.split())
                            if line[4] == 'N/A':
                                if (line[5] >= monitor_standard['detect value(mA)'][a] / 1000):
                                    new_item_line.append(line)
                                    print("(warning)", monitor_standard['모니터링 ITEM'][a], "-> line", i)
                                    monitor_standard['detect count'][a] += 1
                            else:
                                if (line[6] >= monitor_standard['detect value(mA)'][a] / 1000):
                                    new_item_line.append(line)
                                    print("(warning)", monitor_standard['모니터링 ITEM'][a], "-> line", i)
                                    monitor_standard['detect count'][a] += 1
                print("\n")
                # 파일 닫기
                f.close()

                # 모니터링 대상 item을 출력창에 표시함.
                print(pd.DataFrame(monitor_standard), "\n")

                send_item = []
                for count in range(0, len(monitor_standard['detect count'])):
                    if monitor_standard['detect limit'][count] < monitor_standard['detect count'][count]:
                        send_item.append(monitor_standard['모니터링 ITEM'][count])

                record_line = []
                for item in send_item:
                    for i in range(0, len(new_item_line)):
                        if item in new_item_line[i]:
                            record_line.append(new_item_line[i])

                g = open(folder_path + ans + "_LBUF_Burnt_Log.csv", 'a')
                for i in range(0, len(record_line)):
                    record = str(unit_reverse(record_line[i]))[2:-2]
                    record = record.replace("\', \'", " ")
                    record = record.replace("\', ", " ")
                    record = record.replace(", \'", " ")
                    record = record.replace(" mA", "mA")
                    record = record.replace(" uA", "uA")
                    record = record.replace(" nA", "nA")
                    record = record.replace(' ', ',')
                    record = record.replace(',(F)', '')
                    g.writelines(record + "," + each_file_name +  "\n")

                g.close()

                # if len(record_line) == 0:
                os.remove(file_name)

    # ftp 정보
    host = '11.114.114.100'
    user = 'lbavidata'
    passwd = 'lbs123'
    # create a new FTP() instance
    f = ftplib.FTP()

    # connect to our FTP site
    f.connect(host, 21)

    # log into the FTP site
    f.login(user, passwd)

    f.cwd('/sleds2/vol1/data/flex/stdf')

    # 로컬 PC의 저장 경로
    localpath = "./"
    count = 0
    file_name_list = f.nlst()
    f.quit()

    for each_file_name in file_name_list:
        if ('.stxt.gz' in each_file_name) and ('_P_' in each_file_name):
            if (ans in each_file_name):
                count += 1
                # create a new FTP() instance
                f = ftplib.FTP()

                # connect to our FTP site
                f.connect(host, 21)

                # log into the FTP site
                f.login(user, passwd)

                f.cwd('/sleds2/vol1/data/flex/stdf')

                local_filename = os.path.join(localpath, each_file_name)

                with open(local_filename, 'wb') as save_f:
                    f.retrbinary("RETR " + each_file_name, save_f.write)

                f.quit()

                if (count % 20) == 0:
                    item_search()
                    print(ans+" 자료 : ", count, "개째..")

    item_search()
    print(count,"개째..")
    win32api.MessageBox(0, "끝!", "작업 완료", 16)

win = tk.Tk()
win.geometry("220x100")

name = tk.StringVar()

win.title("SOC burnt search")

tk.Label(win, text="찾는 날짜(YYYYMMDD)를 입력하세요.").grid(column=1, row=0)

entry = tk.Entry(win, textvariable=name)
entry.place(x = 32.5,
        y = 20,
        width=160,
        height=20)


button = tk.Button(text="Search", command=soc_burnt)
button.place(x = 75,
        y = 50,
        width=70,
        height=40)
win.mainloop()
