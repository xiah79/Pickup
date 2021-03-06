import pandas as pd
import numpy as np
import requests
import json
import copy
import datetime
import cx_Oracle
from dateutil.relativedelta import relativedelta

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

def getLastDate(d, n):
    now = datetime.datetime.strptime(d, '%Y-%m-%d')
    nd = now + relativedelta(months = n)

    return nd.strftime('%Y-%m-%d')

ds = {}
dic = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [],
     11: [], 12: [], 13: [], 14: [], 15: [], 16: [], 17: [], 18: [], 19: []}
index = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

global jgid
date = '2018-07-01'
month = int(date.split('-')[1]) - 1

#db
username="omr_sa"
userpwd="selectsa"
host="172.31.10.214"
port=1521
dbname="orcl"

field = {0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H', 8:'I', 9:'J', 10:'K', 11:'L'}
dsn=cx_Oracle.makedsn(host, port, dbname)
conn=cx_Oracle.connect(username, userpwd, dsn)
cursor = conn.cursor()

dept_list1 = ['3828','3829','3830','3801','3802','3827','3800','3804','3805','3806','3807','3808','3809','3810',
              '3811','3812','3813','3850','3814','3815','3816','3817','3818','3820','3822','3823','3821','3826','3844',
              '3834','3835','3836','3861','3845','3846','3000','3849','3837','3839','3840','3841','3851','3852','3853',
              '3854','3855','3856','3857','3858','3859','3505','3501','3162','191','192','3819']

#本院科室列表
# dept_list1 = ['6006','303','304','7031','305','306','307','308','309','310','328','302','317','312','313','314','315',
#               '316','43','551','150','552','9000','25','101','42','206','202','15','221','553','7022','24','512','207',
#               '78','321','8013','7363','16','121','120','1000','19','17','75','7056','23','188','189','190','94']
#南院科室列表
# dept_list2 = ['6006','3828','3829','3830','3801','3802','3827','3800','3804','3805','3806','3807','3808','3809','3810',
#               '3811','3812','3813','3850','3814','3815','3816','3817','3818','3820','3822','3823','3821','3826','3844',
#               '3834','3835','3836','3861','3845','3846','3000','3849','3837','3839','3840','3841','3851','3852','3853',
#               '3854','3855','3856','3857','3858','3859','3505','3501','3162','191','192','3819']

list1 = ['jgzb_chb', 'jgzb_hhb']
url = 'http://172.31.10.212:8080/platform/html/main.html'

cookies = {'0000':'%u4E13%u5BB6@photo/0000.jpg', 'JSESSIONID':'07FE8F88C8B1EECD71BDED66C160F5BE'}
res = requests.get(url, params={'_dc':'1516002508895'}, cookies = cookies)
res.encoding = 'utf-8'

if res.status_code == 200:

    url = 'http://172.31.10.212:82/iENM/auth/mgzb/get/data/list.pt'

    cookies = {'JSESSIONID':'1DB4A540E258848460DAB284DAD8FD61',
               'sample.tokenSecret':'adb18c860f951482a8a12c02b6e5e092',
               'sample.accessToken':'d03a902b0df76f1abcbe53ed7948c4ce',
               'SSO':'true'
              }

    from_dara = {'hldy':'303',
                 'tjfs':'2',
                 'kssj':'2017-01-01',
                 'jssj':'2017-02-01',
                 'bblx':'jgzb_hhb',
                 'hljb':'3',
                 'ztbb':'1'}

    print('共计 %s 个科室' % len(dept_list1))
    for it in range(len(dept_list1)):
        ds = copy.deepcopy(dic)
        from_dara['hldy'] = dept_list1[it]
        print(str(it+1)+ '.开始抓取[' + dept_list1[it] + ']的数据....')
        for j in range(1):
            d = getLastDate(date, j)
            from_dara['kssj'] = d
            from_dara['jssj'] = getLastDate(d, 1)

            r = requests.post(url, data=from_dara, cookies=cookies)
            r.encoding = 'utf-8'

            # if j == 2:
            #     print(r.text)
            data = json.loads(r.text)
            jgid = data['jgId']
            for d in data['data']:
                if d == 'datas':

                    lists = data['data'][d]

                    for i, l in enumerate(lists):
                        if is_number(l['value']):
                            v = float(l['value'])
                        else:
                            v = 0.0

                        if l['sensitiveId'] in list1:
                            if v > 0:
                                v = round((1/v), 3)
                        elif '100%' in l['sensitiveExpress']:
                            v = round(v * 100, 3)
                        elif '1000%' in l['sensitiveExpress']:
                            v = round(v * 1000, 3)
                        else:
                            v = round(v, 3)
                        # print("%2s %s %s" % (i, l['sensitiveName'], v))
                        ds[i].append(v)

                        # db2
                        params = {"jgid": jgid, "dept_code": dept_list1[it], "class": i+1}
                        sql = "select %s from IENM_SENSITIVE_2018 where jgid=:jgid and dept_code=:dept_code and class=:class" % field[month]

                        cursor.execute(sql, params)
                        result = cursor.fetchall()
                        num = cursor.rowcount

                        #sql = "update IENM_SENSITIVE_2018 set %s=%.3f where jgid=:jgid and dept_code=:dept_code and class=:class" % (field[month], v)
                        if num == 0:
                            # insert
                            sql = "insert into IENM_SENSITIVE_2018(CLASS, DEPT_CODE, %s, JGID) VALUES (:class, :dept_code, %.3f, :jgid)" %(field[month], v)
                        else:
                            # update
                            sql = "update IENM_SENSITIVE_2018 set %s=%.3f where jgid=:jgid and dept_code=:dept_code and class=:class" % (field[month], v)
                        print(sql)

                        cursor.execute(sql, params)
            print('   已完成' + str(j+1) + '月的数据抓取...')
        # db3
        conn.commit()

        # cursor.close()
        # conn.close()
        # s = []
        # for i in range(len(ds)):
        #     s.append(ds[i])
        #
        # col  = pd.DataFrame(np.array(index, dtype=np.number).reshape(19, 1), columns=['id'],
        #                     index=index)
        # dept = pd.DataFrame(np.array([dept_list1[it]] * 19).reshape(19, 1), columns=['dept_code'],
        #                     index=index)
        # df   = pd.DataFrame(np.array(s),
        #                     index=index)
        # code = pd.DataFrame(np.array([jgid] * 19).reshape(19, 1), columns=['jgid'],
        #                     index=index)
        #
        # frams = [col, dept, df, code]
        # dt = pd.concat(frams, axis=1)
        # dt.to_excel('c:/data/'+ dept_list1[it] + '.xlsx')
        # print('['+dept_list1[it] + ']的文件已生成！')

    print('共计'+ str(len(dept_list1)) +'个科室文件已全部创建完毕！')
    cursor.close()
    conn.close()
