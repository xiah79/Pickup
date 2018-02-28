import hashlib
import json
import os
import requests
import collections
import time

NAME = ''
ID   = ''
PWD  = ''
TEXT = ''

#获取当前日期
def get_date():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

#密码 MD5加密
def pwd_md5(src):
    m = hashlib.md5()
    m.update(src.encode('UTF-8'))
    return m.hexdigest()

#获取项目编码
def param1_json():
    lists = [{'0':ID}]
    dic = collections.OrderedDict()
    dic['method'] = 'getGsxmByYggh'
    dic['serviceId']='portal.CheckWorkService'
    dic['body'] = lists
    return dic
# 提交日志
def param2_json():
    lists = [{
                 "yggh": ID,
                 "gzrz": TEXT,
                 "flag": 5,
                 "housename": "",
                 "rzqk": "1",
                 "zfid": "",
                 "kqrq": get_date().split(' ')[0],
                 "ccbz": 0,
                 "rztjsj": get_date()
             }]
    dic = collections.OrderedDict()
    dic['schema']='portal.main.entry.T_KQB'
    dic['serviceId']='portal.CheckWorkService'
    dic['method']='saveKqb'
    dic['body']=lists
    return dic

# url = "http://web.bsoft.com.cn/portal/logon/myRoles"
# val = {"url": "logon/myRoles",
#        "uid": ID,
#        "pwd": pwd_md5(PWD)}

def func():
    url = "http://web.bsoft.com.cn/portal/logon/myRoles"
    val = {"url": "logon/myRoles",
           "uid": ID,
           "pwd": pwd_md5(PWD)}

    r = requests.post(url, data=json.dumps(val))
    r.encoding = 'utf-8'
    header = r.headers
    print(r.status_code)
    value = header['Set-Cookie'].split(';')[0][11:]
    print(header['Set-Cookie'])

    str = json.loads(r.text)
    url='http://web.bsoft.com.cn/portal/logon/myApps?urt=%s&deep=3&number=1'%(str['body'][0]['id'])
    # head = {'User-Agent','Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'}
    cookies = {'JSESSIONID':value}
    rs = requests.get(url, cookies = cookies)
    print(rs.status_code)
    print(rs.request.headers)


    url = 'http://web.bsoft.com.cn/portal/*.jsonRequest'
    data = json.dumps(param2_json())
    # cookies = {'JSESSIONID':value, '5900':'%u590F%u6656@undefined'}
    str = NAME.encode('unicode-escape').decode('utf-8').replace('\\','%')+'@undefined'
    cookies = {'JSESSIONID':value, ID:str}
    headers = {'Host':'web.bsoft.com.cn',
               'Referer':'http://web.bsoft.com.cn/portal/index.html',
               'content-type': 'application/json',
               'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
               'X-Requested-With':'XMLHttpRequest'
              }
    rs = requests.post(url, data=data, cookies=cookies, headers=headers)
    rs.encoding = 'utf-8'

    print(rs.request.headers)
    print(rs.text)

with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    # print(type(data))

    for l in data:
        for d, x in l.items():
            # print("key:" + d + ",value:" + str(x))
            if d.upper() == 'NAME':
                NAME = str(x)
            elif d.upper() == 'ID':
                ID = str(x)
            elif d.upper() == 'PWD':
                PWD = str(x)
            else:
                TEXT = str(x)
        func()

    f.close()
# def test():
#     data = json.dumps(param1_json())
#     cookies = {'JSESSIONID': '317700EAE2ABBC7ABF0EE80082679729', '5900': '%u590F%u6656@undefined'}
#     headers = {'Host': 'web.bsoft.com.cn',
#                'Referer': 'http://web.bsoft.com.cn/portal/index.html',
#                'content-type': 'application/json',
#                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
#                'X-Requested-With': 'XMLHttpRequest'
#                }
#     rs = requests.post(url, data=data, cookies=cookies, headers=headers)
#
#     return rs
#
# t = test()
# print(t.text)