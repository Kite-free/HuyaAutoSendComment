# 功能实现：在虎牙中自动发送需要的弹幕，赠送礼物
from turtle import width
from selenium import webdriver
import os
options = webdriver.ChromeOptions()  #添加启动参数option
import time
import json
from tkinter import *
from tkinter import ttk
import threading

def read_config(config_path='./config.json'):
    f = open(config_path,'r')
    config =json.loads(f.read())
    return config

#将从浏览器复制过来的cookie转换成字典形式
def cookie_regular(cookie,driver):
    re_cookie = {}
    for k_v in cookie.split(';'):
        k,v = k_v.split('=', 1)
        re_cookie[k.strip()] = v.replace('"','')
    for key,value in re_cookie.items():
        driver.add_cookie(cookie_dict={'domain':'.huya.com','name':key,'value':value,"expires": '','path': '/','httpOnly': False,'HostOnly': False,'Secure': False})

# 赠送特定数量礼物
def send_gift(driver,num):
    config = read_config()
    gift_xpath = config["gift_xpath"] # 通过xpath获取虎粮礼物元素
    confirm_xpath = config["confirm_xpath"] # 通过xpath获取验证赠送礼物的按钮元素
    driver.find_element_by_xpath(gift_xpath).click() 
    time.sleep(0.5)
    driver.find_element_by_xpath(confirm_xpath).click()
    time.sleep(0.5)
    for i in range(num-1):
        driver.find_element_by_xpath(gift_xpath).click() 
        time.sleep(0.5)

# 初始化携带cookie打开虎牙网站
def initDriver(input_url,cookie,progress_bar,app):
    options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
    # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    options.add_argument('--headless')
    #打开浏览器时加载已有的用户数据 包括cookie
    # profile_dir = r"D:\chromeConfig\User Data"
    # options.add_argument("user-data-dir="+os.path.abspath(profile_dir))
    driver = webdriver.Chrome(chrome_options=options)    # Chrome浏览器
    driver.get(input_url)
    progress_bar["value"] = 5
    app.update()
    # driver.maximize_window()
    cookie_regular(cookie,driver)
    driver.refresh()
    progress_bar["value"] = 10
    app.update()
    driver.implicitly_wait(10)
    time.sleep(2) #给予浏览器缓冲时间加载dom元素
    progress_bar["value"] = 20
    app.update()
    return driver

# 在特定直播间自动发送弹幕
def send_text(driver,num,comment,progress_bar,app):
    config = read_config() # 读取配置文件
    textarea_xpath = config["textarea_xpath"] #通过xpath获取输入框元素
    send_xpath = config["send_xpath"] # 通过xpath获取发送弹幕按钮元素
    try:
        progress_bar_value = 20
        for i in range(num):
            progress_bar_value += 80/num
            driver.find_element_by_xpath(textarea_xpath).click()
            time.sleep(0.5)
            driver.find_element_by_xpath(textarea_xpath).clear()
            driver.find_element_by_xpath(textarea_xpath).send_keys(comment)
            time.sleep(0.5)
            driver.find_element_by_xpath(send_xpath).click()
            time.sleep(0.5)
            progress_bar["value"] = progress_bar_value
            app.update()
        # progress_bar["value"] = 100
        # app.update()
        driver.quit()
    except Exception:
        driver.quit()

def start_send_text(room_number,input_comment,comment_number,cookie_number,progress_bar,app):
    input_url = "https://www.huya.com/"+room_number
    config = read_config()
    cookie = config["cookies"][int(cookie_number)]
    progress_bar["value"] = 5
    app.update()
    driver = initDriver(input_url,cookie,progress_bar,app)
    input_number = int(comment_number)
    send_text(driver,input_number,input_comment,progress_bar,app)

def initApp():
    app = Tk()
    app.title("虎牙弹幕自动发送程序")
    app.geometry('350x200')
    label_title = Label(app, text="请填写以下参数：")
    label_title.grid(column=0, row=0,columnspan=2)

    label_room_number = Label(app, text="请输入虎牙房间号：")
    label_room_number.grid(column=0, row=1,sticky=W)
    input_room_number = Entry(app,width=20)
    input_room_number.grid(column=1, row=1,sticky=E)

    label_comment_content = Label(app, text="请输入要发送的弹幕：")
    label_comment_content.grid(column=0, row=2,sticky=W)
    input_comment_content = Entry(app,width=20)
    input_comment_content.grid(column=1, row=2,sticky=E)

    label_comment_number = Label(app, text="请输入要发送的弹幕数量：")
    label_comment_number.grid(column=0, row=3,sticky=W)
    input_comment_number = Entry(app,width=20)
    input_comment_number.grid(column=1, row=3,sticky=E)

    label_cookie_number = Label(app, text="请输入配置文件中cookie的编号:")
    label_cookie_number.grid(column=0, row=4,sticky=W)
    input_cookie_number = Entry(app,width=20)
    input_cookie_number.grid(column=1, row=4,sticky=E)
    def __start_app(row_num):
        progress_bar = ttk.Progressbar(app, length=300, mode="determinate",
                        maximum=100,orient=HORIZONTAL)
        progress_bar.grid(column=0, row=row_num,padx=5, pady=5,columnspan=2,rowspan=1)
        width_pix = (row_num-6)*30+200
        app.geometry('350x'+ str(width_pix))
        app.update()
        room_number = input_room_number.get()
        input_comment = input_comment_content.get()
        comment_number = input_comment_number.get()
        cookie_number = input_cookie_number.get()
        start_send_text(room_number,input_comment,comment_number,cookie_number,progress_bar,app)
        progress_bar.destroy()
        row_num -= 1
        
    def start_app(*args):
        global row_num
        T = threading.Thread(target=__start_app,args=(row_num,))
        row_num += 1
        T.start()

    btn = Button(app, text="发送弹幕",command=start_app) #,background = "blue", fg = "white"
    btn.grid(column=0, row=5,padx=5, pady=5,columnspan=2,rowspan=1)


    # coding=utf-8
    def center_window(w, h):
        # 获取屏幕 宽、高
        ws = app.winfo_screenwidth()
        hs = app.winfo_screenheight()
        # 计算 x, y 位置
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        app.geometry('%dx%d+%d+%d' % (w, h, x, y))
    center_window(350, 200)
    app.mainloop()
   
if __name__ == "__main__":
    row_num = 6
    initApp()
    # config = read_config() # 读取配置文件
    # textarea_xpath = config["textarea_xpath"] #通过xpath获取输入框元素
    # send_xpath = config["send_xpath"] # 通过xpath获取发送弹幕按钮元素
    # gift_xpath = config["gift_xpath"] #  # 通过xpath获取虎粮礼物元素
    # confirm_xpath = config["confirm_xpath"] # 通过xpath获取验证赠送礼物的按钮元素
    # input_url = config["input_url"] # 读取访问地址URL 
    # cookie = config["cookies"][1] #读取预存的cookie值
    # try:
    #     driver = initDriver(input_url,cookie)
    #     # send_gift(driver,5)
    #     send_text(driver,3,"胖 妞")
    #     driver.get("https://www.huya.com/328737")
    #     time.sleep(2)
    #     send_text(driver,3,"666")
    #     # driver.quit()
    # except Exception:
    #     driver.quit()
    # driver.quit()



