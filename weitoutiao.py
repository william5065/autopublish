#!/usr/bin/python3
#encoding: utf-8
'''
@File: weitoutiao.py
@Author:limz
@Time: 2019年03月20日21时
'''

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import requests
from authcode import math_img
import os
import shutil

#下载
def getpic(path, url):
    res = requests.get(url)
    with open(path, 'wb') as file:
        file.write(res.content)
        file.flush()

#生成运动轨迹列表
def get_track(distance):
    track = []
    current = 0
    mid = distance*3/4
    t = random.randint(2, 3)/10
    v = 0
    while current < distance:
          if current < mid:
             a = 2
          else:
             a = -3
          v0 = v
          v = v0+a*t
          move = v0*t+1/2*a*t*t
          current += move
          track.append(round(move))
    return track

#登陆
def login(url, username, password):
    driver = webdriver.Chrome(r'D:\Program Files\CentBrowser\CentBrowser\Application\chromedriver.exe')
    #driver = webdriver.Chrome(r'C:\Users\ADMIN\AppData\Local\CentBrowser\Application\chromedriver.exe')
    driver.get(url)
    driver.maximize_window()
    driver.implicitly_wait(10)

    #跳转到账号密码登录
    driver.find_element_by_id('login-type-account').click()

    input1 = driver.find_element_by_id('user-name')
    input2 = driver.find_element_by_id('password')
    input1.send_keys(username)
    input2.send_keys(password)
    time.sleep(0.2)

    #获取打开滑块验证码页面的元素点击进入滑块验证码页面
    driver.find_element_by_id('bytedance-login-submit').click()
    time.sleep(5)

    return driver

# 获取验证码
def get_authcode(driver, target, image):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    imageurl = soup.find(attrs={"id": "validate-big"}).get("src")
    targeturl = soup.find(attrs={"class": "validate-block"}).get("src")
    getpic(image, imageurl)
    getpic(target, targeturl)

#执行滑动实现登陆
def track(driver, image, target, value, url):

    # 获取验证码
    get_authcode(driver, target, image)

    # 获取需要滑动的距离
    distance = math_img(image, target, value)
    # 如果距离为0则重新打开
    if distance == 0:
        driver.close()
        driver = login(url, username, password)
        get_authcode(driver, target, image)

    track_list = get_track(distance+3) #距离多加3，模拟人工操作
    time.sleep(2)
    slideblock = driver.find_element_by_class_name("drag-button")
    ActionChains(driver).click_and_hold(slideblock).perform()
    time.sleep(0.2)

    # 根据轨迹拖拽圆球
    for track in track_list:
        ActionChains(driver).move_by_offset(xoffset=track,yoffset=0).perform()
    # 模拟人工滑动超过缺口位置返回至缺口的情况，数据来源于人工滑动轨迹，同时还加入了随机数，都是为了更贴近人工滑动轨迹
    imitate=ActionChains(driver).move_by_offset(xoffset=-1, yoffset=0)
    time.sleep(0.015)
    imitate.perform()
    time.sleep(random.randint(6, 10)/10)
    imitate.perform()
    time.sleep(0.04)
    imitate.perform()
    time.sleep(0.012)
    imitate.perform()
    time.sleep(0.019)
    imitate.perform()
    time.sleep(0.033)
    ActionChains(driver).move_by_offset(xoffset=1, yoffset=0).perform()
    # 放开圆球
    ActionChains(driver).pause(random.randint(6, 14)/10).release(slideblock).perform()
    time.sleep(2)
    #务必记得加入quit()或close()结束进程，不断测试电脑只会卡卡西
    #driver.close()

#遍历目录下所以文件
def gci(path):
    """this is a statement"""
    parents = os.listdir(path)
    for parent in parents:
        if parent == "forgifs" or parent == "hilariousgifs":
            pass
        else:
            child = os.path.join(path,parent)
            #print(child)
            if os.path.isdir(child):
                gci(child)
            else:
                filepath.append(child)
                #print(child)

#获取新文件
def get_newfile(count):
    gci(path)
    filelist = []
    imgs = {}
    for i in range(count):
        oldfile = filepath.pop(random.randint(0, len(filepath) - 1))
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        newfile = os.path.join(newpath, os.path.basename(oldfile))
        filelist.append(newfile)
        shutil.copyfile(oldfile, newfile)
        print("已复制新文件：%s" % newfile)
        os.remove(oldfile)
        print("已删除旧文件：%s" % oldfile)
    for file in filelist:
        filename = os.path.basename(file)
        if filename.endswith('.gif'):
            name = filename.split('.')[0]
            imgs[file] = name
    return imgs

#上传图片
def uploadpic(imgs):
    i = 1
    names = []
    for img in imgs:
        driver.find_element_by_xpath('//*[@id="weitoutiao"]/div/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[' + str(i) + ']/input').send_keys(img)
        names.append(imgs[img])
        i += 1
        time.sleep(5)
    #driver.find_element_by_xpath("//button[@data-e2e='imageUploadConfirm-btn']").click()
    return names

#给图片加名字
def uploadname():
    m = 1
    for name in names:
        if m > 1:
            name = "1" + name
        for n in name:
            driver.find_element_by_xpath('//div[@class="ql-editor"]/tt-image[' + str(
                m) + ']/div/div[@class="pgc-img-caption-wrapper"]/input').send_keys(n)
        time.sleep(1)
        m += 1

if __name__ == '__main__':
    image = "image.jpg"            #验证码大图
    target = "target.png"          #验证小图
    value = 0.7                    #验证吗识别阈值
    username = "18215565025"       #用户名
    password = "Wanglihong123"     #密码
    url = "https://sso.toutiao.com/login/?service=https://mp.toutiao.com/sso_confirm/?redirect_url=JTJG"    #登陆地址
    path = r"E:\ziyuan\gif"        #资源路径
    newpath = r"E:\自媒体\已发表\GIF\{0}\{1}".format(time.strftime("%Y%m%d", time.localtime()), "头条号")    #新图片存放路径
    filepath = []                  #保存新图片路径
    count = 3                     #筛选图片数量

    #打开登陆页面获取验证码
    print("登陆中...")
    driver = login(url, username, password)

    #滑动验证并登陆
    print("滑动验证中...")
    track(driver, image, target, value, url)

    #点击发布按钮
    time.sleep(9)
    driver.find_elements_by_class_name('tui2-menu-item')[1].click()

    #点击微头条
    driver.find_element_by_xpath('//*[@id="graphic"]/div/div[1]/div[1]/div/div[3]').click()

    #点击上传
    time.sleep(4)
    driver.find_element_by_xpath('//*[@id="weitoutiao"]/div/div[2]/div/div[2]/div/div[1]/div/i').click()

    #从本地资源中随机选择图片
    time.sleep(2)
    print("筛选图片...")
    imgs = get_newfile(count)

    #上传图片
    print("上传图片...")
    names = uploadpic(imgs)

    #随机从名字中生成一个标题
    print("添加标题...")
    title = names[random.randint(0, len(names)-1)]
    #加标题
    driver.find_element_by_xpath('//*[@id="weitoutiao"]/div/div[2]/div/div[1]/textarea').send_keys(title)
    time.sleep(5)

    #发表
    time.sleep(2)
    print("发布")
    driver.find_element_by_xpath('//*[@id="weitoutiao"]/div/div[2]/div/button').click()