# coding:utf-8


"""
注意事项：
1、邀请源码仅供小伙伴们交流学习，严禁用于牟取任何不正当利益。
2、代码底层架构较老，可以对程序进行二改升级。
3、二改的代码外部分享时必须标注原架构开发者【B站-纸鸢花的花语】。
4、以上事项违反或无视者均无权使用或二改邀请源码。

程序开发者升级建议：
    1、增强个人身份信息随机性，可对请求中的UA、ua、email、iPhoneModel里的参数编写随机函数。
    2、增强客户端信息随机性，可对请求中的客户端version[本程序中为固定值1.38.0]、加密的Salts值[每个版本都有不同Salts]进行随机化。
    3、增强IP信息随机性，可对请求时的IP信息进行代理，使用特殊方法使请求时的IP地址随机化。
    4、增强人为操作真实性，尽量模拟人为操作中的请求方法，本程序只对关键请求进行模拟，未做模拟人为操作的过度修饰。
    5、纸鸢小屋Q群【801730999[技术群有验证]、891085087、187860349】，十分欢迎技术大佬加入技术群，研究各种黑科技技术；其他小伙伴也可在闲聊群中吃瓜趣事。
"""
import poplib
import string
from email.parser import Parser
import json
import uuid
import hashlib
import time
import random
from email.header import decode_header
import yaml
import re

# ==============验证码加密函数=============
from bs4 import BeautifulSoup


def r(e, t):
    n = t - 1
    if n < 0:
        n = 0
    r = e[n]
    u = r['row'] // 2 + 1
    c = r['column'] // 2 + 1
    f = r['matrix'][u][c]
    l = t + 1
    if l >= len(e):
        l = t
    d = e[l]
    p = l % d['row']
    h = l % d['column']
    g = d['matrix'][p][h]
    y = e[t]
    m = 3 % y['row']
    v = 7 % y['column']
    w = y['matrix'][m][v]
    b = i(f) + o(w)
    x = i(w) - o(f)
    return [s(a(i(f), o(f))), s(a(i(g), o(g))), s(a(i(w), o(w))), s(a(b, x))]


def i(e):
    return int(e.split(",")[0])


def o(e):
    return int(e.split(",")[1])


def a(e, t):
    return str(e) + "^⁣^" + str(t)


def s(e):
    t = 0
    n = len(e)
    for r in range(n):
        t = u(31 * t + ord(e[r]))
    return t


def u(e):
    t = -2147483648
    n = 2147483647
    if e > n:
        return t + (e - n) % (n - t + 1) - 1
    if e < t:
        return n - (t - e) % (n - t + 1) + 1
    return e


def c(e, t):
    return s(e + "⁣" + str(t))


def img_secret(e, t, n):
    return {
        'ca': r(e, t),
        'f': c(n, t)
    }


def item_compare(img_list, mode_list):
    score = 0
    rank = 0
    for i in range(3):
        for j in range(3):
            if img_list[i][j] != mode_list[i][j]:
                score += 1
    # print(core)
    if score == 2:
        rank += 1
    return rank


def list_compare(frames):
    score_list = []
    flag = 0
    for frame in frames:
        img_list = frame["matrix"]
        scores = 0
        for mode_frame in frames:
            mode_list = mode_frame["matrix"]
            one_score = item_compare(img_list, mode_list)
            scores += one_score
        score_list.append(scores)
        flag += 1
    # print(score_list)
    for i in range(12):
        if score_list[i] == 11:
            print("Currently verify the correct serial number of the image：", i)
            return i


# ============请求参数信息预处理============


# 设置请求头基本信息
basicRequestHeaders_1 = {
    "Accept-Language": "zh",
    "Content-Type": "application/json; charset=utf-8",
    "Host": "user.mypikpak.com",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "content-type": "application/json"
}

basicRequestHeaders_2 = {
    "x-requested-with": "com.pikcloud.pikpak",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-encoding": "gzip, deflate",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "cookie": "mainHost=user.mypikpak.com"
}

# UA表，随机信息采集
uaList = [{'model': 'MI-ONE PLUS', 'name': ' 小米 1 联通版'}, {'model': 'MI-ONE C1', 'name': ' 小米 1 电信版'},
          {'model': 'MI-ONE', 'name': ' 小米 1 青春版'}, {'model': '2012051', 'name': ' 小米 1S 联通版'},
          {'model': '2012053', 'name': ' 小米 1S 电信版'}, {'model': '2012052', 'name': ' 小米 1S 青春版'},
          {'model': '2012061', 'name': ' 小米 2 联通版'}, {'model': '2012062', 'name': ' 小米 2 电信版'},
          {'model': '2013012', 'name': ' 小米 2S 联通版'}, {'model': '2013021', 'name': ' 小米 2S 电信版'},
          {'model': '2012121', 'name': ' 小米 2A 联通版'}, {'model': '2013061', 'name': ' 小米 3 移动版'},
          {'model': '2013062', 'name': ' 小米 3 联通版'}, {'model': '2013063', 'name': ' 小米 3 电信版'},
          {'model': '2014215', 'name': ' 小米 4 联通 3G 版'}, {'model': '2014218', 'name': ' 小米 4 电信 3G 版'},
          {'model': '2014216', 'name': ' 小米 4 移动 4G 版'}, {'model': '2014719', 'name': ' 小米 4 联通 4G 版'},
          {'model': '2014716', 'name': ' 小米 4 电信 4G 版'}, {'model': '2014726', 'name': ' 小米 4 电信 4G 合约版'},
          {'model': '2015015', 'name': ' 小米 4i 国际版'}, {'model': '2015561', 'name': ' 小米 4c 全网通版'},
          {'model': '2015562', 'name': ' 小米 4c 移动合约版'}, {'model': '2015911', 'name': ' 小米 4S 全网通版'},
          {'model': '2015201', 'name': ' 小米 5 标准版'}, {'model': '2015628', 'name': ' 小米 5 高配版 / 尊享版'},
          {'model': '2015105', 'name': ' 小米 5 国际版'}, {'model': '2015711', 'name': ' 小米 5s 全网通版'},
          {'model': '2016070', 'name': ' 小米 5s Plus 全网通版'}, {'model': '2016089', 'name': ' 小米 5c 移动版'},
          {'model': 'MDE2', 'name': ' 小米 5X 全网通版'}, {'model': 'MDT2', 'name': ' 小米 5X 移动 4G+ 版'},
          {'model': 'MCE16', 'name': ' 小米 6 全网通版'}, {'model': 'MCT1', 'name': ' 小米 6 移动 4G+ 版'},
          {'model': 'M1804D2SE', 'name': ' 小米 6X 全网通版'}, {'model': 'M1804D2ST', 'name': ' 小米 6X 移动 4G+ 版'},
          {'model': 'M1804D2SC', 'name': ' 小米 6X 联通电信定制版'}, {'model': 'M1803E1A', 'name': ' 小米 8 全网通版'},
          {'model': 'M1803E1T', 'name': ' 小米 8 移动 4G+ 版'}, {'model': 'M1803E1C', 'name': ' 小米 8 联通电信定制版'},
          {'model': 'M1807E8S', 'name': ' 小米 8 透明探索版'}, {'model': 'M1807E8A', 'name': ' 小米 8 屏幕指纹版'},
          {'model': 'M1805E2A', 'name': ' 小米 8 SE 全网通版'},
          {'model': 'M1808D2TE', 'name': ' 小米 8 青春版 全网通版'},
          {'model': 'M1808D2TT', 'name': ' 小米 8 青春版 移动 4G+ 版'},
          {'model': 'M1808D2TC', 'name': ' 小米 8 青春版 联通电信定制版'},
          {'model': 'M1808D2TG', 'name': ' 小米 8 Lite 国际版'}, {'model': 'M1902F1A', 'name': ' 小米 9 全网通版'},
          {'model': 'M1902F1T', 'name': ' 小米 9 移动 4G+ 版'}, {'model': 'M1902F1C', 'name': ' 小米 9 联通电信定制版'},
          {'model': 'M1902F1G', 'name': ' 小米 9 国际版'}, {'model': 'M1908F1XE', 'name': ' 小米 9 Pro 5G 全网通版'},
          {'model': 'M1903F2A', 'name': ' 小米 9 SE 全网通版'}, {'model': 'M1903F2G', 'name': ' 小米 9 SE 国际版'},
          {'model': 'M1903F10G', 'name': ' 小米 9T 国际版'}, {'model': 'M1903F11G', 'name': ' 小米 9T Pro 国际版'},
          {'model': 'M1904F3BG', 'name': ' 小米 9 Lite 国际版'},
          {'model': 'M2001J2E M2001J2C', 'name': ' 小米 10 全网通版'}, {'model': 'M2001J2G', 'name': ' 小米 10 国际版'},
          {'model': 'M2001J2I', 'name': ' 小米 10 印度版'},
          {'model': 'M2001J1E M2001J1C', 'name': ' 小米 10 Pro 全网通版'},
          {'model': 'M2001J1G', 'name': ' 小米 10 Pro 国际版'},
          {'model': 'M2002J9E', 'name': ' 小米 10 青春版 全网通版'},
          {'model': 'M2002J9G', 'name': ' 小米 10 Lite 国际版'}, {'model': 'M2002J9S', 'name': ' 小米 10 Lite 韩国版'},
          {'model': 'M2002J9R XIG01', 'name': ' 小米 10 Lite 日本版 (KDDI)'},
          {'model': 'M2007J1SC', 'name': ' 小米 10 至尊纪念版 全网通版'},
          {'model': 'M2007J3SY', 'name': ' 小米 10T 国际版'}, {'model': 'M2007J3SP', 'name': ' 小米 10T 印度版'},
          {'model': 'M2007J3SG', 'name': ' 小米 10T Pro 国际版'},
          {'model': 'M2007J3SI', 'name': ' 小米 10T Pro 印度版'},
          {'model': 'M2007J17G', 'name': ' 小米 10T Lite 国际版'}, {'model': 'M2007J17I', 'name': ' 小米 10i 印度版'},
          {'model': 'M2102J2SC', 'name': ' 小米 10S 全网通版'}, {'model': 'M2011K2C', 'name': ' 小米 11 全网通版'},
          {'model': 'M2011K2G', 'name': ' 小米 11 国际版'}, {'model': 'M2102K1AC', 'name': ' 小米 11 Pro 全网通版'},
          {'model': 'M2102K1C', 'name': ' 小米 11 Ultra 全网通版'},
          {'model': 'M2102K1G', 'name': ' 小米 11 Ultra 国际版'},
          {'model': 'M2101K9C', 'name': ' 小米 11 青春版 全网通版'},
          {'model': 'M2101K9G', 'name': ' 小米 11 Lite 5G 国际版'},
          {'model': 'M2101K9R', 'name': ' 小米 11 Lite 5G 日本版'},
          {'model': 'M2101K9AG', 'name': ' 小米 11 Lite 4G 国际版'},
          {'model': 'M2101K9AI', 'name': ' 小米 11 Lite 4G 印度版'},
          {'model': '2107119DC', 'name': ' Xiaomi 11 青春活力版 全网通版'},
          {'model': '2109119DG', 'name': ' Xiaomi 11 Lite 5G NE 国际版'},
          {'model': '2109119DI', 'name': ' Xiaomi 11 Lite NE 5G 印度版'},
          {'model': 'M2012K11G', 'name': ' 小米 11i 国际版'}, {'model': 'M2012K11AI', 'name': ' 小米 11X 印度版'},
          {'model': 'M2012K11I', 'name': ' 小米 11X Pro 印度版'}, {'model': '21081111RG', 'name': ' Xiaomi 11T 国际版'},
          {'model': '2107113SG', 'name': ' Xiaomi 11T Pro 国际版'},
          {'model': '2107113SI', 'name': ' Xiaomi 11T Pro 印度版'},
          {'model': '2107113SR', 'name': ' Xiaomi 11T Pro 日本版'},
          {'model': '21091116I', 'name': ' Xiaomi 11i 印度版'},
          {'model': '21091116UI', 'name': ' Xiaomi 11i HyperCharge 印度版'},
          {'model': '2201123C', 'name': ' Xiaomi 12 全网通版'}, {'model': '2201123G', 'name': ' Xiaomi 12 国际版'},
          {'model': '2112123AC', 'name': ' Xiaomi 12X 全网通版'}, {'model': '2112123AG', 'name': ' Xiaomi 12X 国际版'},
          {'model': '2201122C', 'name': ' Xiaomi 12 Pro 全网通版'},
          {'model': '2201122G', 'name': ' Xiaomi 12 Pro 国际版'},
          {'model': '2207122MC', 'name': ' Xiaomi 12 Pro 天玑版 全网通版'},
          {'model': '2203129G', 'name': ' Xiaomi 12 Lite 国际版'},
          {'model': '2203129I', 'name': ' Xiaomi 12 Lite 印度版'},
          {'model': '2206123SC', 'name': ' Xiaomi 12S 全网通版'},
          {'model': '2206122SC', 'name': ' Xiaomi 12S Pro 全网通版'},
          {'model': '2203121C', 'name': ' Xiaomi 12S Ultra 全网通版'},
          {'model': '22071212AG', 'name': ' Xiaomi 12T 国际版'},
          {'model': '22081212UG', 'name': ' Xiaomi 12T Pro 国际版'},
          {'model': '22081212R 22200414R', 'name': ' Xiaomi 12T Pro 日本版 (SIM Free)'},
          {'model': 'A201XM', 'name': ' Xiaomi 12T Pro 日本版 (SoftBank)'},
          {'model': '2211133C', 'name': ' Xiaomi 13 全网通版'}, {'model': '2211133G', 'name': ' Xiaomi 13 国际版'},
          {'model': '2210132C', 'name': ' Xiaomi 13 Pro 全网通版'},
          {'model': '2210132G', 'name': ' Xiaomi 13 Pro 国际版'},
          {'model': '2304FPN6DC', 'name': ' Xiaomi 13 Ultra 全网通版'},
          {'model': '2304FPN6DG', 'name': ' Xiaomi 13 Ultra 国际版'},
          {'model': '2210129SG', 'name': ' Xiaomi 13 Lite 国际版'},
          {'model': '2306EPN60G', 'name': ' Xiaomi 13T 国际版'}, {'model': '2306EPN60R', 'name': ' Xiaomi 13T 日本版'},
          {'model': '23078PND5G', 'name': ' Xiaomi 13T Pro 国际版'},
          {'model': '2014616', 'name': ' 小米 Note 双网通版'}, {'model': '2014619', 'name': ' 小米 Note 全网通版'},
          {'model': '2014618', 'name': ' 小米 Note 移动合约版'}, {'model': '2014617', 'name': ' 小米 Note 联通合约版'},
          {'model': '2015011', 'name': ' 小米 Note 国际版'}, {'model': '2015021', 'name': ' 小米 Note 顶配版 双网通版'},
          {'model': '2015022', 'name': ' 小米 Note 顶配版 全网通版'},
          {'model': '2015501', 'name': ' 小米 Note 顶配版 移动合约版'},
          {'model': '2015211', 'name': ' 小米 Note 2 全网通版'},
          {'model': '2015212', 'name': ' 小米 Note 2 移动 4G+ 版'},
          {'model': '2015213', 'name': ' 小米 Note 2 全网通版 (全球频段)'},
          {'model': 'MCE8', 'name': ' 小米 Note 3 全网通版'}, {'model': 'MCT8', 'name': ' 小米 Note 3 移动 4G+ 版'},
          {'model': 'M1910F4G', 'name': ' 小米 Note 10 国际版'},
          {'model': 'M1910F4S', 'name': ' 小米 Note 10 Pro 国际版'},
          {'model': 'M2002F4LG', 'name': ' 小米 Note 10 Lite 国际版'},
          {'model': '2016080', 'name': ' 小米 MIX 全网通版'},
          {'model': 'MDE5', 'name': ' 小米 MIX 2 黑色陶瓷版 全网通版'},
          {'model': 'MDT5', 'name': ' 小米 MIX 2 黑色陶瓷版 移动 4G+ 版'},
          {'model': 'MDE5S', 'name': ' 小米 MIX 2 全陶瓷尊享版'},
          {'model': 'M1803D5XE', 'name': ' 小米 MIX 2S 全网通版'},
          {'model': 'M1803D5XA', 'name': ' 小米 MIX 2S 尊享版 (全球频段)'},
          {'model': 'M1803D5XT', 'name': ' 小米 MIX 2S 移动 4G+ 版'},
          {'model': 'M1803D5XC', 'name': ' 小米 MIX 2S 联通电信定制版'},
          {'model': 'M1810E5E', 'name': ' 小米 MIX 3 全网通版'},
          {'model': 'M1810E5A', 'name': ' 小米 MIX 3 全网通版 (全球频段)'},
          {'model': 'M1810E5GG', 'name': ' 小米 MIX 3 5G'}, {'model': 'M2011J18C', 'name': ' MIX FOLD 小米折叠屏手机'},
          {'model': '2106118C', 'name': ' Xiaomi MIX 4'}, {'model': '22061218C', 'name': ' Xiaomi MIX Fold 2'},
          {'model': '2308CPXD0C', 'name': ' Xiaomi MIX Fold 3'},
          {'model': '2016001', 'name': ' 小米 Max 标准版 全网通版'},
          {'model': '2016002', 'name': ' 小米 Max 标准版 国际版'}, {'model': '2016007', 'name': ' 小米 Max 高配版'},
          {'model': 'MDE40', 'name': ' 小米 Max 2 全网通版'}, {'model': 'MDT4', 'name': ' 小米 Max 2 移动 4G+ 版'},
          {'model': 'MDI40', 'name': ' 小米 Max 2 印度版'}, {'model': 'M1804E4A', 'name': ' 小米 Max 3 全网通版'},
          {'model': 'M1804E4T', 'name': ' 小米 Max 3 移动 4G+ 版'},
          {'model': 'M1804E4C', 'name': ' 小米 Max 3 联通电信定制版'},
          {'model': 'M1904F3BC', 'name': ' 小米 CC9 全网通版'}, {'model': 'M1904F3BT', 'name': ' 小米 CC9 美图定制版'},
          {'model': 'M1906F9SC', 'name': ' 小米 CC9e 全网通版'},
          {'model': 'M1910F4E', 'name': ' 小米 CC9 Pro 全网通版'},
          {'model': '2109119BC', 'name': ' Xiaomi Civi 全网通版'},
          {'model': '2109119BC', 'name': ' Xiaomi Civi 1S 全网通版'},
          {'model': '2209129SC', 'name': ' Xiaomi Civi 2 全网通版'},
          {'model': '23046PNC9C', 'name': ' Xiaomi Civi 3 全网通版'},
          {'model': 'M1901F9E', 'name': ' 小米 Play 全网通版'}, {'model': 'M1901F9T', 'name': ' 小米 Play 移动 4G+ 版'},
          {'model': 'MDG2', 'name': ' 小米 A1 国际版'}, {'model': 'MDI2', 'name': ' 小米 A1 印度版'},
          {'model': 'M1804D2SG', 'name': ' 小米 A2 国际版'}, {'model': 'M1804D2SI', 'name': ' 小米 A2 印度版'},
          {'model': 'M1805D1SG', 'name': ' 小米 A2 Lite 国际版'}, {'model': 'M1906F9SH', 'name': ' 小米 A3 国际版'},
          {'model': 'M1906F9SI', 'name': ' 小米 A3 印度版'}, {'model': 'A0101', 'name': ' 小米平板'},
          {'model': '2015716', 'name': ' 小米平板 2'}, {'model': 'MCE91', 'name': ' 小米平板 3'},
          {'model': 'M1806D9W', 'name': ' 小米平板 4 Wi-Fi 版'}, {'model': 'M1806D9E', 'name': ' 小米平板 4 LTE 版'},
          {'model': 'M1806D9PE', 'name': ' 小米平板 4 Plus LTE 版'},
          {'model': '21051182C', 'name': ' 小米平板 5 国行版'}, {'model': '21051182G', 'name': ' 小米平板 5 国际版'},
          {'model': 'M2105K81AC', 'name': ' 小米平板 5 Pro Wi-Fi 版'},
          {'model': 'M2105K81C', 'name': ' 小米平板 5 Pro 5G'},
          {'model': '22081281AC', 'name': ' 小米平板 5 Pro 12.4 英寸'},
          {'model': '23043RP34C', 'name': ' Xiaomi Pad 6 国行版'},
          {'model': '23043RP34G', 'name': ' Xiaomi Pad 6 国际版'},
          {'model': '23043RP34I', 'name': ' Xiaomi Pad 6 印度版'}, {'model': '23046RP50C', 'name': ' Xiaomi Pad 6 Pro'},
          {'model': '2307BRPDCC', 'name': ' Xiaomi Pad 6 Max 14'}, {'model': '2013022', 'name': ' 红米手机 移动版'},
          {'model': '2013023', 'name': ' 红米手机 联通版'}, {'model': '2013029', 'name': ' 红米 1S 联通版'},
          {'model': '2013028', 'name': ' 红米 1S 电信版'}, {'model': '2014011', 'name': ' 红米 1S 移动 3G 版'},
          {'model': '2014501', 'name': ' 红米 1S 移动 4G 版'}, {'model': '2014813', 'name': ' 红米 2 移动版'},
          {'model': '2014112', 'name': ' 红米 2 移动合约版'}, {'model': '2014811', 'name': ' 红米 2 联通版'},
          {'model': '2014812', 'name': ' 红米 2 电信版'}, {'model': '2014821', 'name': ' 红米 2 电信合约版'},
          {'model': '2014817', 'name': ' 红米 2 国际版'}, {'model': '2014818', 'name': ' 红米 2 印度版'},
          {'model': '2014819', 'name': ' 红米 2 巴西版'}, {'model': '2014502', 'name': ' 红米 2A 标准版'},
          {'model': '2014512 2014055', 'name': ' 红米 2A 增强版'}, {'model': '2014816', 'name': ' 红米 2A 高配版'},
          {'model': '2015811 2015815', 'name': ' 红米 3 全网通 标准版'},
          {'model': '2015812', 'name': ' 红米 3 移动合约 标准版'},
          {'model': '2015810', 'name': ' 红米 3 联通合约 标准版'},
          {'model': '2015817 2015819', 'name': ' 红米 3 全网通 高配版'},
          {'model': '2015818', 'name': ' 红米 3 联通合约 高配版'}, {'model': '2015816', 'name': ' 红米 3 国际版'},
          {'model': '2016030', 'name': ' 红米 3S 全网通版'}, {'model': '2016031', 'name': ' 红米 3S 国际版'},
          {'model': '2016032', 'name': ' 红米 3S Prime 印度版'}, {'model': '2016037', 'name': ' 红米 3S 印度版'},
          {'model': '2016036', 'name': ' 红米 3X 全网通版'}, {'model': '2016035', 'name': ' 红米 3X 移动合约版'},
          {'model': '2016033', 'name': ' 红米 3X 全网通版 (联通定制)'}, {'model': '2016090', 'name': ' 红米 4 标准版'},
          {'model': '2016060', 'name': ' 红米 4 高配版'}, {'model': '2016111', 'name': ' 红米 4A 全网通版'},
          {'model': '2016112', 'name': ' 红米 4A 移动 4G+ 版'}, {'model': '2016117', 'name': ' 红米 4A 国际版'},
          {'model': '2016116', 'name': ' 红米 4A 印度版'}, {'model': 'MAE136', 'name': ' 红米 4X 全网通版'},
          {'model': 'MAT136', 'name': ' 红米 4X 移动 4G+ 版'}, {'model': 'MAG138', 'name': ' 红米 4X 国际版'},
          {'model': 'MAI132', 'name': ' 红米 4 印度版'}, {'model': 'MDE1', 'name': ' 红米 5 全网通版'},
          {'model': 'MDT1', 'name': ' 红米 5 移动 4G+ 版'}, {'model': 'MDG1', 'name': ' 红米 5 国际版'},
          {'model': 'MDI1', 'name': ' 红米 5 印度版'}, {'model': 'MEE7', 'name': ' 红米 5 Plus 全网通版'},
          {'model': 'MET7', 'name': ' 红米 5 Plus 移动 4G+ 版'}, {'model': 'MEG7', 'name': ' 红米 5 Plus 国际版'},
          {'model': 'MCE3B', 'name': ' 红米 5A 全网通版'}, {'model': 'MCT3B', 'name': ' 红米 5A 移动 4G+ 版'},
          {'model': 'MCG3B', 'name': ' 红米 5A 国际版'}, {'model': 'MCI3B', 'name': ' 红米 5A 印度版'},
          {'model': 'M1804C3DE', 'name': ' 红米 6 全网通版'}, {'model': 'M1804C3DT', 'name': ' 红米 6 移动 4G+ 版'},
          {'model': 'M1804C3DC', 'name': ' 红米 6 联通电信定制版'},
          {'model': 'M1804C3DG M1804C3DH', 'name': ' 红米 6 国际版'}, {'model': 'M1804C3DI', 'name': ' 红米 6 印度版'},
          {'model': 'M1805D1SE', 'name': ' 红米 6 Pro 全网通版'},
          {'model': 'M1805D1ST', 'name': ' 红米 6 Pro 移动 4G+ 版'},
          {'model': 'M1805D1SC', 'name': ' 红米 6 Pro 联通电信定制版'},
          {'model': 'M1805D1SI', 'name': ' 红米 6 Pro 印度版'}, {'model': 'M1804C3CE', 'name': ' 红米 6A 全网通版'},
          {'model': 'M1804C3CT', 'name': ' 红米 6A 移动 4G+ 版'},
          {'model': 'M1804C3CC', 'name': ' 红米 6A 联通电信定制版'},
          {'model': 'M1804C3CG M1804C3CH', 'name': ' 红米 6A 国际版'},
          {'model': 'M1804C3CI', 'name': ' 红米 6A 印度版'}, {'model': 'M1810F6LE', 'name': ' Redmi 7 全网通版'},
          {'model': 'M1810F6LT', 'name': ' Redmi 7 运营商全网通版'},
          {'model': 'M1810F6LG M1810F6LH', 'name': ' Redmi 7 国际版'},
          {'model': 'M1810F6LI', 'name': ' Redmi 7 印度版'}, {'model': 'M1903C3EE', 'name': ' Redmi 7A 全网通版'},
          {'model': 'M1903C3ET', 'name': ' Redmi 7A 移动 4G+ 版'},
          {'model': 'M1903C3EC', 'name': ' Redmi 7A 联通电信定制版'},
          {'model': 'M1903C3EG M1903C3EH', 'name': ' Redmi 7A 国际版'},
          {'model': 'M1903C3EI', 'name': ' Redmi 7A 印度版'}, {'model': 'M1908C3IE', 'name': ' Redmi 8 全网通版'},
          {'model': 'M1908C3IC', 'name': ' Redmi 8 运营商全网通版'},
          {'model': 'M1908C3IG M1908C3IH', 'name': ' Redmi 8 国际版'},
          {'model': 'M1908C3II', 'name': ' Redmi 8 印度版'}, {'model': 'M1908C3KE', 'name': ' Redmi 8A 全网通版'},
          {'model': 'M1908C3KG M1908C3KH', 'name': ' Redmi 8A 国际版'},
          {'model': 'M1908C3KI', 'name': ' Redmi 8A 印度版'},
          {'model': 'M2001C3K3I', 'name': ' Redmi 8A Dual 印度版 / Redmi 8A Pro 国际版'},
          {'model': 'M2004J19C', 'name': ' Redmi 9 全网通版'}, {'model': 'M2004J19G', 'name': ' Redmi 9 国际版'},
          {'model': 'M2004J19I', 'name': ' Redmi 9 Prime 印度版'},
          {'model': 'M2004J19AG', 'name': ' Redmi 9 国际版 (NFC)'},
          {'model': 'M2006C3LC', 'name': ' Redmi 9A 全网通版'}, {'model': 'M2006C3LG', 'name': ' Redmi 9A 国际版'},
          {'model': 'M2006C3LVG', 'name': ' Redmi 9AT 国际版'},
          {'model': 'M2006C3LI', 'name': ' Redmi 9A 印度版 / Redmi 9A Sport 印度版'},
          {'model': 'M2006C3LII', 'name': ' Redmi 9i 印度版 / Redmi 9i Sport 印度版'},
          {'model': 'M2006C3MG', 'name': ' Redmi 9C 国际版'}, {'model': 'M2006C3MT', 'name': ' Redmi 9C 泰国版'},
          {'model': 'M2006C3MNG', 'name': ' Redmi 9C NFC 国际版'},
          {'model': 'M2006C3MII', 'name': ' Redmi 9 印度版 / Redmi 9 Activ 印度版'},
          {'model': 'M2010J19SG', 'name': ' Redmi 9T 国际版'}, {'model': 'M2010J19SI', 'name': ' Redmi 9 Power 印度版'},
          {'model': 'M2010J19SR', 'name': ' Redmi 9T 日本版'}, {'model': 'M2010J19ST', 'name': ' Redmi 9T 泰国版'},
          {'model': 'M2010J19SY', 'name': ' Redmi 9T 国际版 (NFC)'},
          {'model': 'M2010J19SL', 'name': ' Redmi 9T 拉美版'}, {'model': '21061119AG', 'name': ' Redmi 10 国际版'},
          {'model': '21061119AL', 'name': ' Redmi 10 拉美版'},
          {'model': '21061119BI', 'name': ' Redmi 10 Prime 印度版'},
          {'model': '21061119DG', 'name': ' Redmi 10 国际版 (NFC)'},
          {'model': '21121119SG', 'name': ' Redmi 10 2022 国际版'},
          {'model': '21121119VL', 'name': ' Redmi 10 2022 拉美版'},
          {'model': '22011119TI', 'name': ' Redmi 10 Prime 2022 印度版'},
          {'model': '22011119UY', 'name': ' Redmi 10 2022 国际版 (NFC)'},
          {'model': '22041219G', 'name': ' Redmi 10 5G 国际版'},
          {'model': '22041219I', 'name': ' Redmi 11 Prime 5G 印度版'},
          {'model': '22041219NY', 'name': ' Redmi 10 5G 国际版 (NFC)'},
          {'model': '220333QAG', 'name': ' Redmi 10C 国际版'},
          {'model': '220333QBI', 'name': ' Redmi 10 印度版 / Redmi 10 Power 印度版'},
          {'model': '220333QNY', 'name': ' Redmi 10C 国际版 (NFC)'}, {'model': '220333QL', 'name': ' Redmi 10C 拉美版'},
          {'model': '220233L2C', 'name': ' Redmi 10A 全网通版'}, {'model': '220233L2G', 'name': ' Redmi 10A 国际版'},
          {'model': '220233L2I', 'name': ' Redmi 10A 印度版 / Redmi 10A Sport 印度版'},
          {'model': '22071219AI', 'name': ' Redmi 11 Prime 印度版'},
          {'model': '23053RN02A', 'name': ' Redmi 12 国际版'}, {'model': '23053RN02I', 'name': ' Redmi 12 印度版'},
          {'model': '23053RN02L', 'name': ' Redmi 12 拉美版'},
          {'model': '23053RN02Y', 'name': ' Redmi 12 国际版 (NFC)'},
          {'model': '23077RABDC', 'name': ' Redmi 12 5G 全网通版'},
          {'model': '23076RN8DY', 'name': ' Redmi 12 5G 国际版 (NFC)'},
          {'model': '23076RN4BI', 'name': ' Redmi 12 5G 印度版'},
          {'model': '22120RN86C', 'name': ' Redmi 12C 全网通版'}, {'model': '22120RN86G', 'name': ' Redmi 12C 国际版'},
          {'model': '2212ARNC4L', 'name': ' Redmi 12C 拉美版'},
          {'model': '22126RN91Y', 'name': ' Redmi 12C 国际版 (NFC)'},
          {'model': '2014018', 'name': ' 红米 Note 联通 3G 标准版'},
          {'model': '2013121', 'name': ' 红米 Note 联通 3G 增强版'},
          {'model': '2014017', 'name': ' 红米 Note 移动 3G 标准版'},
          {'model': '2013122', 'name': ' 红米 Note 移动 3G 增强版'},
          {'model': '2014022', 'name': ' 红米 Note 移动 4G 增强版'},
          {'model': '2014021', 'name': ' 红米 Note 联通 4G 增强版'},
          {'model': '2014715', 'name': ' 红米 Note 4G 国际版'}, {'model': '2014712', 'name': ' 红米 Note 4G 印度版'},
          {'model': '2014915', 'name': ' 红米 Note 移动 4G 双卡版'},
          {'model': '2014912', 'name': ' 红米 Note 联通 4G 双卡版'},
          {'model': '2014916', 'name': ' 红米 Note 电信 4G 双卡版'},
          {'model': '2014911', 'name': ' 红米 Note 移动 4G 双卡合约版'},
          {'model': '2014910', 'name': ' 红米 Note 电信 4G 双卡合约版'},
          {'model': '2015052', 'name': ' 红米 Note 2 移动版'}, {'model': '2015051', 'name': ' 红米 Note 2 双网通版'},
          {'model': '2015712', 'name': ' 红米 Note 2 双网通高配版'},
          {'model': '2015055', 'name': ' 红米 Note 2 移动合约版'},
          {'model': '2015056', 'name': ' 红米 Note 2 移动合约高配版'},
          {'model': '2015617', 'name': ' 红米 Note 3 双网通版'},
          {'model': '2015611', 'name': ' 红米 Note 3 移动合约版'},
          {'model': '2015112 2015115', 'name': ' 红米 Note 3 全网通版'},
          {'model': '2015116', 'name': ' 红米 Note 3 国际版'}, {'model': '2015161', 'name': ' 红米 Note 3 台湾特制版'},
          {'model': '2016050', 'name': ' 红米 Note 4 全网通版'}, {'model': '2016051', 'name': ' 红米 Note 4 移动版'},
          {'model': '2016101', 'name': ' 红米 Note 4X 高通 全网通版'},
          {'model': '2016130', 'name': ' 红米 Note 4X 高通 移动 4G+ 版'},
          {'model': '2016100 2016102', 'name': ' 红米 Note 4 国际版 / 红米 Note 4X 高通 国际版'},
          {'model': 'MBE6A5', 'name': ' 红米 Note 4X MTK 全网通版'},
          {'model': 'MBT6A5', 'name': ' 红米 Note 4X MTK 移动 4G+ 版'},
          {'model': 'MEI7', 'name': ' 红米 Note 5 印度版'}, {'model': 'MEE7S', 'name': ' 红米 Note 5 全网通版'},
          {'model': 'MET7S', 'name': ' 红米 Note 5 移动 4G+ 版'},
          {'model': 'MEC7S', 'name': ' 红米 Note 5 联通电信定制版'},
          {'model': 'M1803E7SG M1803E7SH', 'name': ' 红米 Note 5 国际版'},
          {'model': 'MEI7S', 'name': ' 红米 Note 5 Pro 印度版'},
          {'model': 'MDE6', 'name': ' 红米 Note 5A 全网通 标准版'},
          {'model': 'MDT6', 'name': ' 红米 Note 5A 移动 4G+ 标准版'},
          {'model': 'MDG6', 'name': ' 红米 Note 5A 国际版 标准版'}, {'model': 'MDI6', 'name': ' 红米 Y1 Lite 印度版'},
          {'model': 'MDE6S', 'name': ' 红米 Note 5A 全网通 高配版'},
          {'model': 'MDT6S', 'name': ' 红米 Note 5A 移动 4G+ 高配版'},
          {'model': 'MDG6S', 'name': ' 红米 Note 5A 国际版 高配版'}, {'model': 'MDI6S', 'name': ' 红米 Y1 印度版'},
          {'model': 'M1806E7TG M1806E7TH', 'name': ' 红米 Note 6 Pro 国际版'},
          {'model': 'M1806E7TI', 'name': ' 红米 Note 6 Pro 印度版'},
          {'model': 'M1901F7E', 'name': ' Redmi Note 7 全网通版'},
          {'model': 'M1901F7T', 'name': ' Redmi Note 7 移动 4G+ 版'},
          {'model': 'M1901F7C', 'name': ' Redmi Note 7 联通电信定制版'},
          {'model': 'M1901F7G M1901F7H', 'name': ' Redmi Note 7 国际版'},
          {'model': 'M1901F7I', 'name': ' Redmi Note 7 印度版 / Redmi Note 7S 印度版'},
          {'model': 'M1901F7BE', 'name': ' Redmi Note 7 Pro 全网通版'},
          {'model': 'M1901F7S', 'name': ' Redmi Note 7 Pro 印度版'},
          {'model': 'M1908C3JE', 'name': ' Redmi Note 8 全网通版'},
          {'model': 'M1908C3JC', 'name': ' Redmi Note 8 运营商全网通版'},
          {'model': 'M1908C3JG M1908C3JH', 'name': ' Redmi Note 8 国际版'},
          {'model': 'M1908C3JI', 'name': ' Redmi Note 8 印度版'},
          {'model': 'M1908C3XG', 'name': ' Redmi Note 8T 国际版'},
          {'model': 'M1908C3JGG', 'name': ' Redmi Note 8 (2021) 国际版'},
          {'model': 'M1906G7E', 'name': ' Redmi Note 8 Pro 全网通版'},
          {'model': 'M1906G7T', 'name': ' Redmi Note 8 Pro 运营商全网通版'},
          {'model': 'M1906G7G', 'name': ' Redmi Note 8 Pro 国际版'},
          {'model': 'M1906G7I', 'name': ' Redmi Note 8 Pro 印度版'},
          {'model': 'M2010J19SC', 'name': ' Redmi Note 9 4G 全网通版'},
          {'model': 'M2007J22C', 'name': ' Redmi Note 9 5G 全网通版'},
          {'model': 'M2003J15SS', 'name': ' Redmi Note 9 国际版'},
          {'model': 'M2003J15SI', 'name': ' Redmi Note 9 印度版'},
          {'model': 'M2003J15SG', 'name': ' Redmi Note 9 国际版 (NFC)'},
          {'model': 'M2007J22G', 'name': ' Redmi Note 9T 5G 国际版'},
          {'model': 'M2007J22R A001XM', 'name': ' Redmi Note 9T 5G 日本版 (SoftBank)'},
          {'model': 'M2007J17C', 'name': ' Redmi Note 9 Pro 5G 全网通版'},
          {'model': 'M2003J6A1G', 'name': ' Redmi Note 9S 国际版'},
          {'model': 'M2003J6A1R', 'name': ' Redmi Note 9S 日本版 / Redmi Note 9S 韩国版'},
          {'model': 'M2003J6A1I', 'name': ' Redmi Note 9 Pro 印度版'},
          {'model': 'M2003J6B1I', 'name': ' Redmi Note 9 Pro Max 印度版'},
          {'model': 'M2003J6B2G', 'name': ' Redmi Note 9 Pro 国际版'},
          {'model': 'M2101K7AG', 'name': ' Redmi Note 10 国际版'},
          {'model': 'M2101K7AI', 'name': ' Redmi Note 10 印度版'},
          {'model': 'M2101K7BG', 'name': ' Redmi Note 10S 国际版'},
          {'model': 'M2101K7BI', 'name': ' Redmi Note 10S 印度版'},
          {'model': 'M2101K7BNY', 'name': ' Redmi Note 10S 国际版 (NFC)'},
          {'model': 'M2101K7BL', 'name': ' Redmi Note 10S 拉美版'},
          {'model': 'M2103K19C', 'name': ' Redmi Note 10 5G 全网通版 / Redmi Note 11SE 全网通版'},
          {'model': 'M2103K19I', 'name': ' Redmi Note 10T 5G 印度版'},
          {'model': 'M2103K19G', 'name': ' Redmi Note 10 5G 国际版'},
          {'model': 'M2103K19Y', 'name': ' Redmi Note 10T 国际版'},
          {'model': 'M2104K19J XIG02', 'name': ' Redmi Note 10 JE 日本版 (KDDI)'},
          {'model': '22021119KR', 'name': ' Redmi Note 10T 日本版 (SIM Free)'},
          {'model': 'A101XM', 'name': ' Redmi Note 10T 日本版 (SoftBank)'},
          {'model': 'M2101K6G', 'name': ' Redmi Note 10 Pro 国际版'},
          {'model': 'M2101K6T', 'name': ' Redmi Note 10 Pro 泰国版'},
          {'model': 'M2101K6R', 'name': ' Redmi Note 10 Pro 日本版'},
          {'model': 'M2101K6P', 'name': ' Redmi Note 10 Pro 印度版'},
          {'model': 'M2101K6I', 'name': ' Redmi Note 10 Pro Max 印度版'},
          {'model': 'M2104K10AC', 'name': ' Redmi Note 10 Pro 5G 全网通版'},
          {'model': '2109106A1I', 'name': ' Redmi Note 10 Lite 印度版'},
          {'model': '21121119SC', 'name': ' Redmi Note 11 4G 全网通版'},
          {'model': '2201117TG', 'name': ' Redmi Note 11 国际版'},
          {'model': '2201117TI', 'name': ' Redmi Note 11 印度版'},
          {'model': '2201117TL', 'name': ' Redmi Note 11 拉美版'},
          {'model': '2201117TY', 'name': ' Redmi Note 11 国际版 (NFC)'},
          {'model': '21091116AC', 'name': ' Redmi Note 11 5G 全网通版'},
          {'model': '21091116AI', 'name': ' Redmi Note 11T 5G 印度版'},
          {'model': '22041219C', 'name': ' Redmi Note 11E 5G 全网通版'},
          {'model': '2201117SG', 'name': ' Redmi Note 11S 国际版'},
          {'model': '2201117SI', 'name': ' Redmi Note 11S 印度版'},
          {'model': '2201117SL', 'name': ' Redmi Note 11S 拉美版'},
          {'model': '2201117SY', 'name': ' Redmi Note 11S 国际版 (NFC)'},
          {'model': '22087RA4DI', 'name': ' Redmi Note 11 SE 印度版'},
          {'model': '22031116BG', 'name': ' Redmi Note 11S 5G 国际版'},
          {'model': '21091116C', 'name': ' Redmi Note 11 Pro 全网通版'},
          {'model': '2201116TG', 'name': ' Redmi Note 11 Pro 国际版'},
          {'model': '2201116TI', 'name': ' Redmi Note 11 Pro 印度版'},
          {'model': '2201116SC', 'name': ' Redmi Note 11E Pro 全网通版'},
          {'model': '2201116SG', 'name': ' Redmi Note 11 Pro 5G 国际版'},
          {'model': '2201116SR', 'name': ' Redmi Note 11 Pro 5G 日本版'},
          {'model': '2201116SI', 'name': ' Redmi Note 11 Pro+ 5G 印度版'},
          {'model': '21091116UC', 'name': ' Redmi Note 11 Pro+ 全网通版'},
          {'model': '21091116UG', 'name': ' Redmi Note 11 Pro+ 5G 国际版'},
          {'model': '22041216C', 'name': ' Redmi Note 11T Pro 全网通版'},
          {'model': '22041216UC', 'name': ' Redmi Note 11T Pro+ 全网通版'},
          {'model': '22095RA98C', 'name': ' Redmi Note 11R 5G 全网通版'},
          {'model': '23021RAAEG', 'name': ' Redmi Note 12 国际版'},
          {'model': '23027RAD4I', 'name': ' Redmi Note 12 印度版'},
          {'model': '23028RA60L', 'name': ' Redmi Note 12 拉美版'},
          {'model': '23021RAA2Y', 'name': ' Redmi Note 12 国际版 (NFC)'},
          {'model': '22101317C', 'name': ' Redmi Note 12 5G 全网通版 / Redmi Note 12R Pro 全网通版'},
          {'model': '22111317G', 'name': ' Redmi Note 12 5G 国际版'},
          {'model': '22111317I', 'name': ' Redmi Note 12 5G 印度版'},
          {'model': '23076RA4BC', 'name': ' Redmi Note 12R 全网通版'},
          {'model': '2303CRA44A', 'name': ' Redmi Note 12S 国际版'},
          {'model': '2303ERA42L', 'name': ' Redmi Note 12S 拉美版'},
          {'model': '23030RAC7Y', 'name': ' Redmi Note 12S 国际版 (NFC)'},
          {'model': '2209116AG', 'name': ' Redmi Note 12 Pro 国际版'},
          {'model': '22101316C', 'name': ' Redmi Note 12 Pro 全网通版'},
          {'model': '22101316G', 'name': ' Redmi Note 12 Pro 5G 国际版'},
          {'model': '22101316I', 'name': ' Redmi Note 12 Pro 5G 印度版'},
          {'model': '22101316UCP', 'name': ' Redmi Note 12 Pro+ 全网通版'},
          {'model': '22101316UG', 'name': ' Redmi Note 12 Pro+ 5G 国际版'},
          {'model': '22101316UP', 'name': ' Redmi Note 12 Pro+ 5G 印度版'},
          {'model': '22101316UC', 'name': ' Redmi Note 12 探索版 全网通版'},
          {'model': '22101320C', 'name': ' Redmi Note 12 Pro 极速版 全网通版'},
          {'model': '23054RA19C', 'name': ' Redmi Note 12T Pro 全网通版'},
          {'model': '23049RAD8C', 'name': ' Redmi Note 12 Turbo 全网通版'},
          {'model': 'M2004J7AC', 'name': ' Redmi 10X 5G 全网通版'},
          {'model': 'M2004J7BC', 'name': ' Redmi 10X Pro 5G 全网通版'},
          {'model': 'M2003J15SC', 'name': ' Redmi 10X 4G 全网通版'},
          {'model': 'M1903F10A', 'name': ' Redmi K20 全网通版'},
          {'model': 'M1903F10C', 'name': ' Redmi K20 运营商全网通版'},
          {'model': 'M1903F10I', 'name': ' Redmi K20 印度版'},
          {'model': 'M1903F11A', 'name': ' Redmi K20 Pro 全网通版'},
          {'model': 'M1903F11C', 'name': ' Redmi K20 Pro 运营商全网通版'},
          {'model': 'M1903F11I', 'name': ' Redmi K20 Pro 印度版'},
          {'model': 'M1903F11A', 'name': ' Redmi K20 Pro 尊享版 全网通版'},
          {'model': 'M2001G7AE', 'name': ' Redmi K30 5G 全网通版 / Redmi K30 5G 极速版'},
          {'model': 'M2001G7AC', 'name': ' Redmi K30 5G 全网通版'},
          {'model': 'M2001G7AC', 'name': ' Redmi K30i 5G 全网通版'},
          {'model': 'M1912G7BE', 'name': ' Redmi K30 4G 全网通版'},
          {'model': 'M1912G7BC', 'name': ' Redmi K30 4G 运营商全网通版'},
          {'model': 'M2001J11C', 'name': ' Redmi K30 Pro 全网通版'},
          {'model': 'M2001J11C M2001J11E', 'name': ' Redmi K30 Pro 变焦版 全网通版'},
          {'model': 'M2006J10C', 'name': ' Redmi K30 至尊纪念版 全网通版'},
          {'model': 'M2007J3SC', 'name': ' Redmi K30S 至尊纪念版 全网通版'},
          {'model': 'M2012K11AC', 'name': ' Redmi K40 全网通版'},
          {'model': 'M2012K11C', 'name': ' Redmi K40 Pro 全网通版 / Redmi K40 Pro+ 全网通版'},
          {'model': 'M2012K10C', 'name': ' Redmi K40 游戏增强版 全网通版'},
          {'model': '22021211RC', 'name': ' Redmi K40S 全网通版'},
          {'model': '22041211AC', 'name': ' Redmi K50 全网通版'},
          {'model': '22011211C', 'name': ' Redmi K50 Pro 全网通版'},
          {'model': '21121210C', 'name': ' Redmi K50 电竞版 全网通版'},
          {'model': '22081212C', 'name': ' Redmi K50 至尊版 全网通版'},
          {'model': '22041216I', 'name': ' Redmi K50i 印度版'}, {'model': '23013RK75C', 'name': ' Redmi K60 全网通版'},
          {'model': '22127RK46C', 'name': ' Redmi K60 Pro 全网通版'},
          {'model': '22122RK93C', 'name': ' Redmi K60E 全网通版'},
          {'model': '23078RKD5C', 'name': ' Redmi K60 至尊版 全网通版'},
          {'model': '2016020', 'name': ' 红米 Pro 标准版'}, {'model': '2016021', 'name': ' 红米 Pro 高配版 / 尊享版'},
          {'model': 'M1803E6E', 'name': ' 红米 S2 全网通版'}, {'model': 'M1803E6T', 'name': ' 红米 S2 移动 4G+ 版'},
          {'model': 'M1803E6C', 'name': ' 红米 S2 联通电信定制版'},
          {'model': 'M1803E6G M1803E6H', 'name': ' 红米 S2 国际版'}, {'model': 'M1803E6I', 'name': ' 红米 Y2 印度版'},
          {'model': 'M1810F6G', 'name': ' Redmi Y3 国际版'}, {'model': 'M1810F6I', 'name': ' Redmi Y3 印度版'},
          {'model': 'M1903C3GG M1903C3GH', 'name': ' Redmi Go 国际版'},
          {'model': 'M1903C3GI', 'name': ' Redmi Go 印度版'}, {'model': '220733SG', 'name': ' Redmi A1 国际版'},
          {'model': '220733SH 220733SI', 'name': ' Redmi A1 印度版'}, {'model': '220733SL', 'name': ' Redmi A1 拉美版'},
          {'model': '220733SFG', 'name': ' Redmi A1+ 国际版'},
          {'model': '220733SFH 220743FI', 'name': ' Redmi A1+ 印度版'},
          {'model': '23028RNCAG', 'name': ' Redmi A2+ 国际版'}, {'model': '22081283C', 'name': ' Redmi Pad 国行版'},
          {'model': '22081283G', 'name': ' Redmi Pad 国际版'}, {'model': '23073RPBFC', 'name': ' Redmi Pad SE 国行版'},
          {'model': '23073RPBFG', 'name': ' Redmi Pad SE 国际版'},
          {'model': '23073RPBFL', 'name': ' Redmi Pad SE 拉美版'}, {'model': 'M1805E10A', 'name': ' POCO F1'},
          {'model': 'M2004J11G', 'name': ' POCO F2 Pro 国际版'}, {'model': 'M2012K11AG', 'name': ' POCO F3 国际版'},
          {'model': 'M2104K10I', 'name': ' POCO F3 GT 印度版'}, {'model': '22021211RG', 'name': ' POCO F4 国际版'},
          {'model': '22021211RI', 'name': ' POCO F4 印度版'}, {'model': '21121210G', 'name': ' POCO F4 GT 国际版'},
          {'model': '21121210I', 'name': ' POCO F4 GT 印度版'}, {'model': '23049PCD8G', 'name': ' POCO F5 国际版'},
          {'model': '23049PCD8I', 'name': ' POCO F5 印度版'}, {'model': '23013PC75G', 'name': ' POCO F5 Pro 国际版'},
          {'model': 'M1912G7BI', 'name': ' POCO X2 印度版'}, {'model': 'M2007J20CI', 'name': ' POCO X3 印度版'},
          {'model': 'M2007J20CG', 'name': ' POCO X3 NFC 国际版'},
          {'model': 'M2007J20CT', 'name': ' POCO X3 NFC 泰国版'},
          {'model': 'M2102J20SG', 'name': ' POCO X3 Pro 国际版'},
          {'model': 'M2102J20SI', 'name': ' POCO X3 Pro 印度版'}, {'model': '21061110AG', 'name': ' POCO X3 GT 国际版'},
          {'model': '2201116PG', 'name': ' POCO X4 Pro 5G 国际版'},
          {'model': '2201116PI', 'name': ' POCO X4 Pro 5G 印度版'},
          {'model': '22041216G', 'name': ' POCO X4 GT 国际版'},
          {'model': '22041216UG', 'name': ' POCO X4 GT Pro 国际版'},
          {'model': '22111317PG', 'name': ' POCO X5 5G 国际版'}, {'model': '22111317PI', 'name': ' POCO X5 5G 印度版'},
          {'model': '22101320G', 'name': ' POCO X5 Pro 5G 国际版'},
          {'model': '22101320I', 'name': ' POCO X5 Pro 5G 印度版'}, {'model': 'M2004J19PI', 'name': ' POCO M2 印度版'},
          {'model': 'M2003J6CI', 'name': ' POCO M2 Pro 印度版'}, {'model': 'M2010J19CG', 'name': ' POCO M3 国际版'},
          {'model': 'M2010J19CT', 'name': ' POCO M3 泰国版'}, {'model': 'M2010J19CI', 'name': ' POCO M3 印度版'},
          {'model': 'M2103K19PI', 'name': ' POCO M3 Pro 5G 印度版'},
          {'model': '22041219PG', 'name': ' POCO M4 5G 国际版'}, {'model': '22041219PI', 'name': ' POCO M4 5G 印度版'},
          {'model': '2201117PG', 'name': ' POCO M4 Pro 国际版'}, {'model': '2201117PI', 'name': ' POCO M4 Pro 印度版'},
          {'model': '21091116AG', 'name': ' POCO M4 Pro 5G 国际版'},
          {'model': '22031116AI', 'name': ' POCO M4 Pro 5G 印度版'}, {'model': '22071219CG', 'name': ' POCO M5 国际版'},
          {'model': '22071219CI', 'name': ' POCO M5 印度版'}, {'model': '2207117BPG', 'name': ' POCO M5s 国际版'},
          {'model': '23076PC4BI', 'name': ' POCO M6 Pro 5G 印度版'}, {'model': 'M2006C3MI', 'name': ' POCO C3 印度版'},
          {'model': '211033MI', 'name': ' POCO C31 印度版'}, {'model': '220333QPG', 'name': ' POCO C40 国际版'},
          {'model': '220333QPI', 'name': ' POCO C40 印度版'},
          {'model': '220733SPH 220733SPI', 'name': ' POCO C50 印度版'},
          {'model': '2305EPCC4G', 'name': ' POCO C51 国际版'}, {'model': '22127PC95G', 'name': ' POCO C55 国际版'},
          {'model': 'XMWT01', 'name': ' 小米手表'}, {'model': 'FYJ01QP', 'name': ' 小米米家翻译机'},
          {'model': '21051191C', 'name': ' CyberDog 仿生四足机器人'}]


# 获取UA
def get_User_Agent(client_id, device_id, ua_key, timestamp, phoneModel, phoneBuilder, version):
    # UA = "ANDROID-com.pikcloud.pikpak/1.38.0 protocolversion/200 accesstype/ clientid/" + client_id + " clientversion/1.38.0 action_type/ networktype/WIFI sessionid/ deviceid/" + device_id + " providername/NONE devicesign/div101." + ua_key + " refresh_token/ sdkversion/1.1.0.110000 datetime/" + timestamp + " usrno/ appname/android-com.pikcloud.pikpak session_origin/ grant_type/ appid/ clientip/ devicename/" + phoneBuilder.capitalize() + "_" + phoneModel.capitalize() + " osversion/13 platformversion/10 accessmode/ devicemodel/" + phoneModel
    UA = "ANDROID-com.pikcloud.pikpak/" + version +" protocolversion/200 accesstype/ clientid/" + client_id + " clientversion/" + version+" action_type/ networktype/WIFI sessionid/ deviceid/" + device_id + " providername/NONE devicesign/div101." + ua_key + " refresh_token/ sdkversion/1.1.0.110000 datetime/" + timestamp + " usrno/ appname/android-com.pikcloud.pikpak session_origin/ grant_type/ appid/ clientip/ devicename/" + phoneBuilder.capitalize() + "_" + phoneModel.capitalize() + " osversion/13 platformversion/10 accessmode/ devicemodel/" + phoneModel
    return UA


# 获取ua
def get_user_agent():
    tmp1 = random.randrange(90, 120)
    tmp2 = random.randrange(5200, 5500)
    tmp3 = random.randrange(90, 180)
    tmp_version = str(tmp1) + ".0." + str(tmp2) + "." + str(tmp3)
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/' + tmp_version + ' Safari/537.36 '
    print(ua)
    return ua


# md5加密算法
def get_hash(str):
    obj = hashlib.md5()
    obj.update(str.encode("utf-8"))
    result = obj.hexdigest()
    return result


# 获取captcha_sign
def get_sign(orgin_str, version):
    # salts = [{'alg': 'md5', 'salt': 'Z1GUH9FPdd2uR48'},
    #          {'alg': 'md5', 'salt': 'W4At8CN00YeICfrhKye'},
    #          {'alg': 'md5', 'salt': 'WbsJsexMTIj+qjuVNkTZUJxqUkdf'},
    #          {'alg': 'md5', 'salt': 'O56bcWMoHaTXey5QnzKXDUETeaVSD'},
    #          {'alg': 'md5', 'salt': 'nAN3jBriy8/PXGAdsn3yPMU'},
    #          {'alg': 'md5', 'salt': '+OQEioNECNf9UdRe'},
    #          {'alg': 'md5', 'salt': '2BTBxZ3IbPnkrrfd/'},
    #          {'alg': 'md5', 'salt': 'gBip5AYtm53'},
    #          {'alg': 'md5', 'salt': '9FMyrvjZFZJT5Y+b1NeSYfs5'},
    #          {'alg': 'md5', 'salt': '0cIBtEVWYCKdIOlOXnTJPhLGU/y5'},
    #          {'alg': 'md5', 'salt': '92j4I+ZiMyxFx6Q'},
    #          {'alg': 'md5', 'salt': 'xNFN9RnUlu218s'},
    #          {'alg': 'md5', 'salt': 'UZcnnQ2nkaY0S'}
    #          ]

    salts = [
        {"version": "1.38.0",
         "value": [{"alg": "md5", "salt": "Z1GUH9FPdd2uR48"}, {"alg": "md5", "salt": "W4At8CN00YeICfrhKye"},
                   {"alg": "md5", "salt": "WbsJsexMTIj+qjuVNkTZUJxqUkdf"},
                   {"alg": "md5", "salt": "O56bcWMoHaTXey5QnzKXDUETeaVSD"},
                   {"alg": "md5", "salt": "nAN3jBriy8/PXGAdsn3yPMU"}, {"alg": "md5", "salt": "+OQEioNECNf9UdRe"},
                   {"alg": "md5", "salt": "2BTBxZ3IbPnkrrfd/"}, {"alg": "md5", "salt": "gBip5AYtm53"},
                   {"alg": "md5", "salt": "9FMyrvjZFZJT5Y+b1NeSYfs5"},
                   {"alg": "md5", "salt": "0cIBtEVWYCKdIOlOXnTJPhLGU/y5"}, {"alg": "md5", "salt": "92j4I+ZiMyxFx6Q"},
                   {"alg": "md5", "salt": "xNFN9RnUlu218s"}, {"alg": "md5", "salt": "UZcnnQ2nkaY0S"}]},
        {"version": "1.38.1",
         "value": [{"alg": "md5", "salt": "sVRsKvECgdAkti8"}, {"alg": "md5", "salt": "YeEMzxPksk2EeU6kSdTVEyhhXHyc"},
                   {"alg": "md5", "salt": "dPua"}, {"alg": "md5", "salt": "t003Rb3eQlHTvCNFt6uKF0VU9Fs28QQAEs"},
                   {"alg": "md5", "salt": "KaEndY5nN5bTr"}, {"alg": "md5", "salt": "SNdlBZmTC5pDEe"},
                   {"alg": "md5", "salt": ""}, {"alg": "md5", "salt": "fmKfAxx0h"},
                   {"alg": "md5", "salt": "HArL3jm190Jh5/"}, {"alg": "md5", "salt": "mCdNl7GDDtGJc1253HrWUymZ2orSEE"},
                   {"alg": "md5", "salt": "jrLINFDF1j850mvltFrYTFrCd+M1wDP6CWHCKC8"}, {"alg": "md5", "salt": "jcWxpA"},
                   {"alg": "md5", "salt": "XGTbi9Egkq2IW6D0CE81vu+VbaZS3mI3gPlvy"}, {"alg": "md5", "salt": "ro"},
                   {"alg": "md5", "salt": "plHF"}]},
        {"version": "1.39.0",
         "value": [{"alg": "md5", "salt": "e1d0IwHdz+CJLzskoFto8SSKobPWMwcz"}, {"alg": "md5", "salt": "wUU7Rz/wpuHy"},
                   {"alg": "md5", "salt": "dye78dKP7wgEFMebN/Z11VVPAAtueAVR3TcMFZPCO0F9mBQqbk/qpHy9Yqr0no"},
                   {"alg": "md5", "salt": "Cpx1E/O+bo+vTguIiLosm3zR9Y1N"},
                   {"alg": "md5", "salt": "uqyFMWT5R6TxXji2DhHxlNYY3"},
                   {"alg": "md5", "salt": "7afNTr/GwzoNJCLXJVm+nEMBa2w8PiwBfm"},
                   {"alg": "md5", "salt": "glbIrXW34T5ceIBUhsAOzT1R0XSHnTwv1mqtg1r"}, {"alg": "md5", "salt": "l"},
                   {"alg": "md5", "salt": "51sgGDapT73pQMI664"}]},
        {"version": "1.40.0",
         "value": [{"alg": "md5", "salt": "MNn/o2kDbAdap6iyA62c31+odfAXm"},
                    {"alg": "md5", "salt": "GU2DNPxJQz8Zd/HZhKe+Vpr3nydASi"},
                    {"alg": "md5", "salt": "Mr"},
                    {"alg": "md5", "salt": "9yuMfCUj3370cqowx0iLT4WI"},
                    {"alg": "md5", "salt": "sEtFM"},
                    {"alg": "md5", "salt": "57O4iXpaXLGJ5CuIXlKWm"},
                    {"alg": "md5", "salt": "jIPlqvJR/1fNI3v4IvFcRv2IlzSuUc"},
                    {"alg": "md5", "salt": "p0u2aV"},
                    {"alg": "md5", "salt": "AnHbAEWs+4ggDbg37bbpULXK2NFyFHSE"},
                    {"alg": "md5", "salt": "X3v/UHqblw2VHjeCJHamvXyB"},
                    {"alg": "md5", "salt": "Lxe9yYKLa7JBTw3AKivrzs+CqdGO39K"},
                    {"alg": "md5", "salt": "lkz8Q4viV1+U"}, {"alg": "md5", "salt": "VH2I"}]},
        {"version": "1.40.1",
         "value": [{"alg": "md5", "salt": "/+CkcDXbE1nma"},
                    {"alg": "md5", "salt": "AenjaF3Why5nRJNdaCqtWfX/tmRofc4N2M"},
                    {"alg": "md5", "salt": "N"},
                    {"alg": "md5", "salt": "9Mj9ryxBkc8Y9x6yYAxoyqVjpIgnETN/cdXG0n+ep2E9g+of+X7"},
                    {"alg": "md5", "salt": "S3szFWh7ziO7zSfmR8HKB+4HdjaTmgo91Ut+6ngvZQNquR"},
                    {"alg": "md5",
                     "salt": "AZ+GiFSnM3BolbBJH3yUy2OxmGeh1swnB2yz4P8kC9aQHiUWRXSok07u4"},
                    {"alg": "md5", "salt": ""},
                    {"alg": "md5", "salt": "iTP0hdaZLa6Pl9ChHDVedunfoMSnb32XHOEirAuj9AdZs/iTYk"}]},
        {"version": "1.40.2",
         "value": [{"alg": "md5", "salt": "UmrmnIWHIM21FeXRG0znfomWR7wSN8q9TmZI/"}, {"alg": "md5", "salt": "/AZYp"},
                   {"alg": "md5", "salt": "sQMU74"}, {"alg": "md5", "salt": "EcVGhmFRGDDdUimM8BAu8muZs9wxeht5L+Hxnti3"},
                   {"alg": "md5", "salt": "8N1"}, {"alg": "md5", "salt": "nHKvehDlck0Rw"},
                   {"alg": "md5", "salt": "bARBSOK9ZLseRzNcSTdkpu8d+4u1"}, {"alg": "md5", "salt": "yYUYosxQWCS"},
                   {"alg": "md5", "salt": "H8xkd+u"}, {"alg": "md5", "salt": "u7Hwt"},
                   {"alg": "md5", "salt": "YgEvMyvwV2hw3RyQJnOcNU4pniiE28Q7S"},
                   {"alg": "md5", "salt": "3NcwBuLYpgwFXdZQj"},
                   {"alg": "md5", "salt": "X9HLp8LGXjku14J1k1+I1nGK4NBZjQqhkqdV48tg2fbmo"}]},
        {"version": "1.40.3",
         "value": [{"alg": "md5", "salt": "6Wwu"}, {"alg": "md5", "salt": "caGf/9xk9qDEO3eBxEHig0"},
                   {"alg": "md5", "salt": "qO6FubP/pkJGl+y"}, {"alg": "md5", "salt": "dRsJ0sF9C"},
                   {"alg": "md5", "salt": "82GQv"}, {"alg": "md5", "salt": "fMIWctW09a0P4kwplXYj6"},
                   {"alg": "md5", "salt": "LEMFx070vHZH"}, {"alg": "md5", "salt": "PapQk45XYRM82f4fokIk2+biLoVgPEsC"},
                   {"alg": "md5", "salt": "6C9x50NIS4Bqli"}, {"alg": "md5", "salt": "0zsq4lAkHpmTNsR1jLtnArVhnCNuwz"},
                   {"alg": "md5", "salt": "4kN5ZRsNWKXndR9GgSdZ"},
                   {"alg": "md5", "salt": "PoxkARWhSmZ+CiJoeV7HSh/SVMX"}, {"alg": "md5", "salt": "pVU"},
                   {"alg": "md5", "salt": "N8N"}, {"alg": "md5", "salt": "CoVmbhLWt8uqjvYrW0xFnBLSPkOuX4d2"}]},
        {"version": "1.41.0",
         "value": [{"alg": "md5", "salt": "Wcpe+bWhLidcpKx+NbicS9tmSq8RbVTFk6Arf"},
                    {"alg": "md5", "salt": "/WcDjchZab"}, {"alg": "md5", "salt": "YWRJGUPI/lD"},
                    {"alg": "md5", "salt": "R"},
                    {"alg": "md5", "salt": "9Kba0Nkh7vz5CGWxgFCyqJ/BdjnJIx8KU5r/WTR6Ae"},
                    {"alg": "md5", "salt": "tmUQGnovPWmNvB0UAQbDZnJMg57jGzUv7"},
                    {"alg": "md5", "salt": "sPsOQdEqCp19PUDMYfg1//"},
                    {"alg": "md5", "salt": "mvhuvTJROSortMaGzK5rZi209sBTZq+WitI"},
                    {"alg": "md5", "salt": "Qox5BNaQfdishhmAKGr"},
                    {"alg": "md5", "salt": "R2JW9N8bRUEizf+pkWg/o9iJKG34bdpSjEe"},
                    {"alg": "md5", "salt": "FvDT"}]},
        {"version": "1.42.6",
         "value": [{"alg": "md5", "salt": "frupTFdxwcJ5mcL3R8"}, {"alg": "md5", "salt": "jB496fSFfbWLhWyqV"},
                   {"alg": "md5", "salt": "xYLtzn8LT5h3KbAalCjc/Wf"},
                   {"alg": "md5", "salt": "PSHSbm1SlxbvkwNk4mZrJhBZ1vsHCtEdm3tsRiy1IPUnqi1FNB5a2F"},
                   {"alg": "md5", "salt": "SX/WvPCRzgkLIp99gDnLaCs0jGn2+urx7vz/"},
                   {"alg": "md5", "salt": "OGdm+dgLk5EpK4O1nDB+Z4l"},
                   {"alg": "md5", "salt": "nwtOQpz2xFLIE3EmrDwMKe/Vlw2ubhRcnS2R23bwx9wMh+C3Sg"},
                   {"alg": "md5", "salt": "FI/9X9jbnTLa61RHprndT0GkVs18Chd"}]},
        {"version": "1.43.4",
         "value": [{"alg": "md5", "salt": "Zx+7tFIUgelyWJNaayncroBYipNqZfFJKT"}, {"alg": "md5", "salt": "rdhgox"},
                   {"alg": "md5", "salt": "tbnC7VF5YS0zXQiRPh2RZKBcXah"}, {"alg": "md5", "salt": "qQA7KT0wyL"},
                   {"alg": "md5", "salt": "NZl7p4NvU2oeFSjrDXJThrA/UnqwMKKK6HX34TB"}, {"alg": "md5", "salt": "VKt69a"},
                   {"alg": "md5", "salt": "YbwfCJ9tZV3Jf+"}, {"alg": "md5", "salt": "OpYK"},
                   {"alg": "md5", "salt": "arBOLuxsz2x"}, {"alg": "md5", "salt": "3F0PF5isIDeuuzz0FLvSANMU8tXzaQD"},
                   {"alg": "md5", "salt": "gXIj1ukvnm4SmBy0ICvr7DBObLO83R0154/"},
                   {"alg": "md5", "salt": "i6HQBEn8Ukbjw+HGnaZUjRGvD1kOsIQ"}]}
    ]

    salt_value = []

    for salt in salts:
        if salt["version"] == version:
            salt_value = salt["value"]
            break

    for salt in salt_value:
        if len(salt) > 0:
           temp = orgin_str + salt["salt"]
        orgin_str = get_hash(temp)


    print("Sign：", orgin_str)
    return orgin_str


def get_ua_key(device_id):
    rank_1 = hashlib.sha1((device_id + "com.pikcloud.pikpak1appkey").encode("utf-8")).hexdigest()
    rank_2 = get_hash(rank_1)
    return device_id + rank_2


# ============邮箱接口函数，需自行配置============


# 自定义邮箱接口，可配置自己的邮箱API接口实现自动化
def get_email():
    # 手动输入
    return input("请输入接收验证码的邮箱：")

def get_email_auto():
    # 自动生成

    # cloudflare对接QQ
    # prefix = ''.join(random.choices(string.ascii_letters + string.digits, k=10))  # 生成长度为10的随机字符串
    # email = f"{prefix}@jcxiaozhan.top"
    # return email

    # https://tempmail.plus/
    domain_list = ['mailto.plus', 'fexpost.com', 'fexbox.org', 'mailbox.in.ua', 'rover.info', 'chitthi.in', 'fextemp.com', 'any.pink', 'merepost.com']
    domain = random.choice(domain_list)
    # 随机新邮箱
    # prefix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))  # 生成长度为10的随机字符串
    prefix = ''.join(random.choices(string.ascii_lowercase, k=6))
    email = f"{prefix}@{domain}"
    return email

# 解析邮件内容
def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def extract_h2_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    h2_tag = soup.find('h2')
    if h2_tag:
        return h2_tag.get_text()
    else:
        return None

# 接收验证码接口，可配置自己的邮箱API接口实现自动化
def get_verification_code():
    # 手动输入验证码
    return input("请输入接收到的验证码：")

def get_verification_code_auto(email):
    import requests

    # try:
    #     # 自动化读取QQ邮箱验证码
    #     # 添加第一次读取的5秒延时
    #     time.sleep(5)
    #
    #     email = '349636607@qq.com'
    #     password = 'xdnyupqzbfxebjce'  # 这个密码不是邮箱登录密码，是pop3服务密码
    #     pop3_server = 'pop.qq.com'
    #
    #     # 连接到POP3服务器:
    #     server = poplib.POP3_SSL(pop3_server, 995)
    #     # # 可以打开或关闭调试信息:
    #     # server.set_debuglevel(1)
    #     # # 可选:打印POP3服务器的欢迎文字:
    #     # print(server.getwelcome().decode('utf-8'))
    #     # 身份认证:
    #     server.user(email)
    #     server.pass_(password)
    #     # stat()返回邮件数量和占用空间:
    #     # print('Messages: %s. Size: %s' % server.stat())
    #     # list()返回所有邮件的编号:
    #     resp, mails, octets = server.list()
    #     # 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
    #     # print(mails)
    #     # 获取最新一封邮件, 注意索引号从1开始:
    #     index = len(mails)
    #     print('未读邮件的数量', index)
    #
    #     # 使用循环每5秒重新读取，直到获取到h2_content为止
    #     while True:
    #         resp, lines, octets = server.retr(index)  # 修改此处
    #         # lines存储了邮件的原始文本的每一行,
    #         # 可以获得整个邮件的原始文本:
    #         msg_content = b'\r\n'.join(lines).decode('utf-8')
    #         # 稍后解析出邮件:
    #         msg = Parser().parsestr(msg_content)
    #         content = msg.get_payload(decode=True)
    #         h2_content = extract_h2_content(content)
    #
    #         if h2_content:
    #             break  # 如果获取到h2_content，跳出循环
    #
    #         # 如果未获取到h2_content，等待5秒后重新读取
    #         time.sleep(5)
    #
    #     # 可以根据邮件索引号直接从服务器删除邮件:
    #     server.dele(index)  # 修改此处
    #     # 关闭连接:
    #     server.quit()
    #     return str(h2_content)
    # except Exception:
    #     input("QQ邮件读取失败，按任意键退出程序！")
    #     exit(0)

    # https://tempmail.plus/
    retries = 1
    while retries < 20:
        print(f"邮件读取次数：{retries}")
        response = requests.get(f'https://tempmail.plus/api/mails?email={email}&first_id=0&epin=')
        data = response.json()
        if data.get("mail_list"):
            mail_id = data["mail_list"][0]["mail_id"]
            if mail_id != '':
                # 获取邮件id，再次请求
                mail_page = requests.get(f'https://tempmail.plus/api/mails/{mail_id}?email={email}&epin=')
                line_str = mail_page.json().get("text")
                return re.search(r'\n(\d+)\n', line_str).group(1)
            else:
                continue
        time.sleep(1)
        retries += 1
    input("Tempmail网站邮件读取失败，按任意键退出程序！")
    exit(0)

# ============全部网络请求============


# 初始化人机验证网页
# url,captcha_token,expires_in
def part2(client_id, captcha_token, device_id, captcha_sign, email, timestamp, User_Agent, version):
    import requests

    url = "https://user.mypikpak.com/v1/shield/captcha/init"

    querystring = {"client_id": client_id}

    payload = {
        "action": "POST:/v1/auth/verification",
        "captcha_token": captcha_token,
        "client_id": client_id,
        "device_id": device_id,
        "meta": {
            "captcha_sign": "1." + captcha_sign,
            "user_id": "",
            "package_name": "com.pikcloud.pikpak",
            # "client_version": "1.38.0",
            "client_version": version,
            "email": email,
            "timestamp": timestamp
        },
        "redirect_uri": "xlaccsdk01://xbase.cloud/callback?state=harbor"
    }
    headers = {
        "X-Device-Id": device_id,
        "User-Agent": User_Agent,
    }
    headers.update(basicRequestHeaders_1)

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 获取图片列表
# pid,traceid,frames,result
def part3(device_id, user_agent, referer):
    import requests

    url = "https://user.mypikpak.com/pzzl/gen"

    querystring = {"deviceid": device_id, "traceid": ""}

    headers = {
        "Host": "user.mypikpak.com",
        "accept": "application/json, text/plain, */*",
        "user-agent": user_agent,
        "referer": referer,
    }
    headers.update(basicRequestHeaders_2)

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 验证图片序号
# result
def part4(pid, device_id, trace_id, f, n, p, a, c, referer, user_agent):
    import requests

    url = "https://user.mypikpak.com/pzzl/verify"

    querystring = {"pid": pid,
                   "deviceid": device_id, "traceid": trace_id, "f": f,
                   "n": n, "p": p, "a": a, "c": c}

    headers = {
        "Host": "user.mypikpak.com",
        "accept": "application/json, text/plain, */*",
        "user-agent": user_agent,
        "referer": referer,
    }
    headers.update(basicRequestHeaders_2)

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 发送验证码
# code,captcha_token,expires_in
def part5(device_id, captcha_token, pid, trace_id, user_agent, referer):
    import requests

    url = "https://user.mypikpak.com/credit/v1/report"

    querystring = {"deviceid": device_id,
                   "captcha_token": captcha_token,
                   "type": "pzzlSlider", "result": "0", "data": pid,
                   "traceid": trace_id}

    headers = {
        "Host": "user.mypikpak.com",
        "accept": "application/json, text/plain, */*",
        "user-agent": user_agent,
        "referer": referer,
    }
    headers.update(basicRequestHeaders_2)
    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 验证验证码1
# verification_id,expires_in,slected_channel
def part6(client_id, captcha_token, email, device_id, User_Agent):
    import requests

    url = "https://user.mypikpak.com/v1/auth/verification"

    querystring = {"client_id": client_id}

    payload = {
        "captcha_token": captcha_token,
        "email": email,
        "locale": "zh-CN",
        "target": "ANY",
        "client_id": client_id
    }
    headers = {
        "X-Device-Id": device_id,
        "User-Agent": User_Agent,
    }
    headers.update(basicRequestHeaders_1)

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 验证验证码2
# verification_token,expires_in
def part8(client_id, verification_id, verification_code, device_id, User_Agent):
    import requests

    url = "https://user.mypikpak.com/v1/auth/verification/verify"

    querystring = {"client_id": client_id}

    payload = {
        "client_id": client_id,
        "verification_id": verification_id,
        "verification_code": verification_code
    }
    headers = {
        "X-Device-Id": device_id,
        "User-Agent": User_Agent,
    }
    headers.update(basicRequestHeaders_1)

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 安全验证
# captcha_token,expires_in
def part8_1(client_id, captcha_token, device_id, captcha_sign, email, timestamp, User_Agent, version):
    import requests

    url = "https://user.mypikpak.com/v1/shield/captcha/init"

    querystring = {"client_id": client_id}

    payload = {
        "action": "POST:/v1/auth/signup",
        "captcha_token": captcha_token,
        "client_id": client_id,
        "device_id": device_id,
        "meta": {
            "captcha_sign": "1." + captcha_sign,
            "user_id": "",
            "package_name": "com.pikcloud.pikpak",
            # "client_version": "1.38.0",
            "client_version": version,
            "email": email,
            "timestamp": timestamp
        },
        "redirect_uri": "xlaccsdk01://xbase.cloud/callback?state=harbor"
    }
    headers = {
        "Host": "user.mypikpak.com",
        "x-device-id": device_id,
        "user-agent": User_Agent,
        "accept-language": "zh",
        "content-type": "application/json",
        "accept-encoding": "gzip"
    }

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 注册账号
# access_token,expires_in,sub
def part9(client_id, captcha_token, client_secret, email, name, password, verification_token, device_id, User_Agent):
    import requests

    url = "https://user.mypikpak.com/v1/auth/signup"

    querystring = {"client_id": client_id}

    payload = {
        "captcha_token": captcha_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "email": email,
        "name": name,
        "password": password,
        "verification_token": verification_token
    }
    headers = {
        "X-Device-Id": device_id,
        "User-Agent": User_Agent,
    }
    headers.update(basicRequestHeaders_1)

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 安全验证
# captcha_token,expires_in
def part10(client_id, captcha_token, device_id, captcha_sign, user_id, timestamp, User_Agent, version):
    import requests

    url = "https://user.mypikpak.com/v1/shield/captcha/init"

    querystring = {"client_id": client_id}

    payload = {
        "action": "POST:/vip/v1/activity/invite",
        "captcha_token": captcha_token,
        "client_id": client_id,
        "device_id": device_id,
        "meta": {
            "captcha_sign": "1." + captcha_sign,
            "user_id": user_id,
            "package_name": "com.pikcloud.pikpak",
            # "client_version": "1.38.0",
            "client_version": version,
            "timestamp": timestamp
        },
        "redirect_uri": "xlaccsdk01://xbase.cloud/callback?state=harbor"
    }
    headers = {
        "X-Device-Id": device_id,
        "User-Agent": User_Agent,
    }
    headers.update(basicRequestHeaders_1)

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


def one_invite(user_id, phoneModel, phoneBuilder, invite_code, captcha_token, device_id, access_token, User_Agent, version):
    import requests

    url = "https://api-drive.mypikpak.com/vip/v1/activity/invite"

    payload = {
        "data": {
            "sdk_int": "33",
            "uuid": device_id,
            "userType": "1",
            "userid": user_id,
            "userSub": "",
            "product_flavor_name": "cha",
            "language_system": "zh-CN",
            "language_app": "zh-CN",
            "build_version_release": "13",
            "phoneModel": phoneModel,
            "build_manufacturer": phoneBuilder,
            "build_sdk_int": "33",
            "channel": "official",
            "versionCode": "10150",
            # "versionName": "1.38.0",
            "versionName": version,
            "installFrom": "other",
            "country": "PL"
        },
        "apk_extra": {"channel": "official"}
    }
    headers = {
        "Host": "api-drive.mypikpak.com",
        "authorization": "Bearer " + access_token,
        "product_flavor_name": "cha",
        "x-captcha-token": captcha_token,
        "x-client-version-code": "10150",
        "x-device-id": device_id,
        "user-agent": User_Agent,
        "country": "PL",
        "accept-language": "zh-CN",
        "x-peer-id": device_id,
        "x-user-region": "2",
        "x-system-language": "zh-CN",
        "x-alt-capability": "3",
        "accept-encoding": "gzip",
        "content-type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)


# 邀请码填写
def part_invite(user_id, phoneModel, phoneBuilder, invite_code, captcha_token, device_id, access_token, User_Agent):
    import requests

    url = "https://api-drive.mypikpak.com/vip/v1/order/activation-code"

    payload = {"activation_code": invite_code}
    headers = {
        "Host": "api-drive.mypikpak.com",
        "authorization": "Bearer " + access_token,
        "product_flavor_name": "cha",
        "x-captcha-token": captcha_token,
        "x-client-version-code": "10150",
        "x-device-id": device_id,
        "user-agent": User_Agent,
        "country": "DK",
        "accept-language": "zh-CN",
        "x-peer-id": device_id,
        "x-user-region": "2",
        "x-system-language": "zh-CN",
        "x-alt-capability": "3",
        "content-length": "30",
        "accept-encoding": "gzip",
        "content-type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)


def part11(user_id, phoneModel, phoneBuilder, invite_code, captcha_token, device_id, access_token, User_Agent, version):
    import requests

    url = "https://api-drive.mypikpak.com/vip/v1/activity/invite"

    payload = {
        "data": {
            "sdk_int": "33",
            "uuid": device_id,
            "userType": "1",
            "userid": user_id,
            "userSub": "",
            "product_flavor_name": "cha",
            "language_system": "zh-CN",
            "language_app": "zh-CN",
            "build_version_release": "13",
            "phoneModel": phoneModel,
            "build_manufacturer": phoneBuilder,
            "build_sdk_int": "33",
            "channel": "spread",
            "versionCode": "10142",
            # "versionName": "1.38.0",
            "versionName": version,
            "installFrom": "other",
            "country": "NO"
        },
        "apk_extra": {
            "channel": "spread",
            "invite_code": invite_code
        }
    }
    headers = {
        "Host": "api-drive.mypikpak.com",
        "authorization": "Bearer " + access_token,
        "product_flavor_name": "cha",
        "x-captcha-token": captcha_token,
        "x-client-version-code": "10142",
        "x-device-id": device_id,
        "user-agent": User_Agent,
        "country": "NO",
        "accept-language": "zh-CN",
        "x-peer-id": device_id,
        "x-user-region": "2",
        "x-system-language": "zh-CN",
        "x-alt-capability": "3",
        "accept-encoding": "gzip",
        "content-type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)


# 程序运行主函数
def start():
    # 配置项初始化
    # 参数值
    invite_code = "验证码信息为空！"
    email = '邮箱信息为空！'
    verification_code = '邮箱验证码为空！'

    # 运行模式
    invite_code_mode = 1
    email_mode = 1
    verification_code_mode = 1

    # 版本
    version_list = ['1.38.0', '1.38.1', '1.39.0', '1.40.0', '1.40.1', '1.40.2', '1.40.3', '1.41.0', '1.42.6', '1.43.4']
    version = random.choice(version_list)
    print(f"本次运行所使用的版本为：{version}")

    # 读取配置文件
    try:
        with open('config.yaml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            invite_code_mode = config['invitationCode']['mode']
            invite_code = config['invitationCode']['value']
            email_mode = config['email']['mode']
            verification_code_mode = config['verificationCode']['mode']
    except Exception:
        input("配置文件读取异常，按任意键退出程序！")
        exit(0)

    # 邀请码
    if invite_code_mode == 2:
        print(f"本次邀请码为：{invite_code}")
    else:
        invite_code = input("请输入你的账号邀请码：")

    # 客户端id
    client_id = "YNxT9w7GMdWvEOKa"
    # 设备id
    device_id = str(uuid.uuid4()).replace("-", "")
    # 当前时间戳
    timestamp = str(int(time.time()) * 1000)

    # 新用户邮箱
    if email_mode == 2:
        email = get_email_auto()
        print(f"新邮箱信息：{email}")
    else:
        email = get_email()
        print(f"新邮箱信息：{email}")

    # 获取签证信息
    # org_str = client_id + "1.38.0" + "com.pikcloud.pikpak" + device_id + timestamp
    org_str = client_id + version + "com.pikcloud.pikpak" + device_id + timestamp
    captcha_sign = get_sign(org_str, version)
    print(f"captcha_sign：{captcha_sign}")

    # 设备信息
    randomPhone = random.choice(uaList)
    print(f"device_info：{randomPhone}")

    phoneModel = randomPhone['model']
    phoneBuilder = "XIAOMI"
    ua_key = get_ua_key(device_id)
    User_Agent = get_User_Agent(client_id, device_id, ua_key, timestamp, phoneModel, phoneBuilder, version)
    user_agent = get_user_agent()
    time.sleep(1)
    action2 = part2(client_id, "", device_id, captcha_sign, email, timestamp, user_agent, version)

    # pid,traceid,frames,result
    action3 = part3(device_id, user_agent, action2['url'])

    select_id = list_compare(action3['frames'])
    img_data = img_secret(action3['frames'], select_id, action3['pid'])
    print(img_data)

    # result
    action4 = part4(action3['pid'], device_id, action3['traceid'], img_data['f'], img_data['ca'][0], img_data['ca'][1],
                    img_data['ca'][2], img_data['ca'][3], action2['url'], user_agent)
    time.sleep(1)
    # code,captcha_token,expires_in
    action5 = part5(device_id, action2["captcha_token"], action3['pid'], action3['traceid'], user_agent, action2['url'])

    # verification_id,expires_in,slected_channel
    action6 = part6(client_id, action5["captcha_token"], email, device_id, user_agent)

    # 获取验证码
    if verification_code_mode == 2:
        verification_code = get_verification_code_auto(email)
        print(f"注册验证码：{verification_code}")
    else:
        verification_code = get_verification_code()
        print(f"注册验证码：{verification_code}")

    # verification_token,expires_in
    action8 = part8(client_id, action6['verification_id'], verification_code, device_id, User_Agent)

    timestamp = str(int(time.time()) * 1000)
    # org_str = client_id + "1.38.0" + "com.pikcloud.pikpak" + device_id + timestamp
    org_str = client_id + version + "com.pikcloud.pikpak" + device_id + timestamp
    captcha_sign = get_sign(org_str,version)
    User_Agent = get_User_Agent(client_id, device_id, ua_key, timestamp, phoneModel, phoneBuilder, version)

    action8_1 = part8_1(client_id, action2["captcha_token"], device_id, captcha_sign, email, timestamp, User_Agent, version)
    client_secret = "dbw2OtmVEeuUvIptb1Coyg"
    time.sleep(1)
    # access_token,expires_in,sub
    # 账号的昵称设置
    name = email.split("@")[0]
    # 账号的密码设置
    password = "......00"
    action9 = part9(client_id, action8_1['captcha_token'], client_secret, email, name, password,
                    action8['verification_token'], device_id, User_Agent)
    time.sleep(1)
    # captcha_token,expires_in
    action10 = part10(client_id, action8_1['captcha_token'], device_id, captcha_sign, action9['sub'], timestamp,
                      User_Agent, version)

    # 邀请填写
    one_invite(action9['sub'], phoneModel, phoneBuilder, invite_code, action10['captcha_token'], device_id,
               action9['access_token'], User_Agent, version)
    part_invite(action9['sub'], phoneModel, phoneBuilder, invite_code, action10['captcha_token'], device_id,
                action9['access_token'], User_Agent)

    # print("===========邀请成功=============")
    # print("邮箱：", email)
    # print("密码：", password)
    # print("用户名：", name)
    # input("===========结束运行=============")

    # 账号写入文件
    with open("README.md", "w", encoding='utf-8') as file:
        file.write("\n### 今日账号\n")
        file.write("\n邮箱： " + email + "\n")
        file.write("密码： " + password + "\n")
        file.write("用户名： " + name + "\n")
    exit(0)


if __name__ == '__main__':
    print("==============================================")
    print("              PikPak 自动邀请程序")
    print("              ================")
    print("               作者：John.Cena")
    print("            架构开发者：【B站-纸鸢花的花语】")
    print("==============================================")
    start()
