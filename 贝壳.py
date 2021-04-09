import re
import requests
import random
import pandas as pd
import time
import multiprocessing
from functools import partial


# 获取代理ip【快代理】
def get_proxies():
    # API接口，返回格式为json
    api_url = "http://dps.kdlapi.com/api/getdps/?orderid=941786894960981&num=10&signature=dbpdw01gumnq1trzxo4p85oyfn4562xf&pt=1&format=json&sep=1"

    # API接口返回的ip
    proxy_ip = requests.get(api_url).json()['data']['proxy_list']

    # 用户名密码认证(私密代理/独享代理)
    username = "460556933"
    password = "rb1qgnfw"

    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {'user': username, 'pwd': password, 'proxy': random.choice(proxy_ip)},
        "https": "https://%(user)s:%(pwd)s@%(proxy)s/" % {'user': username, 'pwd': password, 'proxy': random.choice(proxy_ip)}
    }

    return proxies


# 请求网页数据
def get_html(url, proxies, header):
    try:
        rep = requests.get(url, headers=header, proxies=proxies, timeout=6)
    except Exception as e:
        print(e)
        proxies = get_proxies()
    rep = requests.get(url, headers=header, proxies=proxies, timeout=6)
    while rep.status_code != 200:
        proxies = get_proxies()
        rep = requests.get(url, headers=header, proxies=proxies, timeout=6)

    html = rep.text
    html = re.sub('\s', '', html)  # 将html文本中非字符数据去掉

    return html, proxies


def main(layout):
    url = 'https://wh.ke.com/ershoufang/'
    header = {
        "Accept-Encoding": "Gzip",  # 使用gzip压缩传输数据让访问更快
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    }
    proxies = get_proxies()
    rep, proxies = get_html(url, proxies, header)

    text = rep
    ershoufang = re.findall(r'<divdata-role="ershoufang">(.*?)</div>', text)[0]
    areaUrls = re.findall('"href="/ershoufang/(.*?)/"title="', ershoufang)  # 城市 url地址
    areaNames = re.findall('在售二手房">(.*?)</a>', ershoufang)  # 城市 名称
    areaDict = dict(zip(areaNames, areaUrls))  # 城市 - url 字典表
    # 户型
    # layouts = ['l1','l2','l3','l4','l5']
    # 价格
    priceRanges = ['bp0ep200', 'bp200ep250', 'bp250ep300', 'bp300ep400', 'bp400ep500',
                   'bp500ep600', 'bp600ep700', 'bp700ep800', 'bp800ep1000', 'bp1000ep100000']
    num = 0
    # for layout in layouts:
    layout = layout
    for areaName in areaNames:
        areaUrl = areaDict[areaName]
        for priceRange in priceRanges:
            info_url = f'{url}{areaUrl}/{layout}{priceRange}'
            # info_url = 'https://bj.ke.com/ershoufang/'                       
            try:
                info_text, proxies = get_html(info_url, proxies, header)
            except Exception as e:
                print(e)
                continue

            # 搜索结果数量
            resultDes = re.findall(r'<h2class="totalfl">共找到<span>(\d+)</span>套<ahref', info_text)[0]
            print(f'{areaName}  价格区间在 {priceRange} 的 户型为 {layout} 房子 一共 {resultDes}个')
            # 获取结果页数 data-page="28"
            pages = re.findall(r'page-data=\'{"totalPage":(\d+),"curPage":1}\'', info_text)
            print(f'{pages}页数据')
            if int(resultDes) == 0:
                print(f'{areaName} 没有 价格区间在 {priceRange} 的 户型为 {layout} 房子！')
                continue
            # elif len(re.findall(r'data-page="(\d+)"', info_text))==0 :
            #     pages = 1
            else:
                pages = int(re.findall(r'page-data=\'{"totalPage":(\d+),"curPage":1}\'', info_text)[0])

            for page in range(1, pages + 1):
                items = []
                time.sleep(random.random())
                info_url = f'{url}{areaUrl}/pg{page}{layout}{priceRange}'
                try:
                    info_html, proxies = get_html(info_url, proxies, header)
                except Exception as e:
                    print(e)
                    continue

                sellListContent = re.findall(r'<ulclass="sellListContent"log-mod="list">(.*?)</ul>', info_html)[0]
                Lists = re.findall(r'<liclass="clear">(.*?)</li>', sellListContent)

                for List in Lists:
                    try:
                        # List = Lists[0]
                        # 获取房屋信息
                        item = {}
                        item['标题'] = re.findall(r'detail"title="(.*?)"data-hreftype=', List)[0]
                        item['房子ID'] = re.findall(r'housedel_id=(\d+)&', List)[0]
                        item['地址'] = re.findall(r'<ahref="(.*?)">(.*)</a>', List)[0][1]
                        item['详情页'] = re.findall(r'<ahref="(.*?)">(.*)</a>', List)[0][0]
                        item['详情'] = re.findall(r'<spanclass="houseIcon"></span>(.*?)</div>', List)[0]
                        item['总价'] = re.findall(r'<divclass="totalPrice"><span>(\d+\.?\d*)</span>(.*?)</div>', List)[0][0]
                        item['总价单位'] = re.findall(r'<divclass="totalPrice"><span>(\d+\.?\d*)</span>(.*?)</div>', List)[0][1]
                        item['均价'] = re.findall(r'<divclass="unitPrice".*<span>(.*?)</span></div></div></div>', List)[0]
                        item['关注人数'] = re.findall(r'<spanclass="starIcon"></span>(.*?)</div>', List)[0]
                        item['地区'] = areaName
                        item['价格区间'] = priceRange
                        item['户型'] = layout
                        # tags = re.findall(r'<divclass="tag">(.*?)</div>', List)
                        # if len(tags)==0:
                        #     item['tag'] = ''
                        # else:                            
                        #     tag = re.findall(r'>(.*?)</span>', tags)
                        #     item['tag'] = ','.join(tag)

                        items.append(item)
                        num = num + 1
                        print(f'{num}个房子信息已经采集!')

                    except Exception as e:
                        print(e)
                        print(item)
                        continue

                df = pd.DataFrame(items)
                df.to_csv(f'.\贝壳武汉二手房{layout}信息.csv', mode='a', index=False, header=None)


# items = []
# def main(layout):
#     num = 0
#     get_data(layout, areaNames, areaDict, priceRanges, url)

if __name__ == '__main__':
    # url  ='https://nj.ke.com/ershoufang/'
    # header = {
    #     "Accept-Encoding": "Gzip",  # 使用gzip压缩传输数据让访问更快
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    # }
    # proxies = get_proxies()
    # rep, proxies = get_html(url, proxies)

    # text = rep
    # ershoufang = re.findall(r'<divdata-role="ershoufang">(.*?)</div>', text)[0]
    # areaUrls = re.findall('"href="/ershoufang/(.*?)/"title="', ershoufang) # 城市 url地址
    # areaNames = re.findall('在售二手房">(.*?)</a>', ershoufang) # 城市 名称
    # areaDict = dict(zip(areaNames, areaUrls)) # 城市 - url 字典表
    # # 户型
    # layouts = ['l1','l2','l3','l4','l5']
    # # 价格
    # priceRanges = ['bp0ep200','bp200ep250','bp250ep300','bp300ep400','bp400ep500',
    #                'bp500ep600','bp600ep700','bp700ep800','bp800ep1000','bp1000ep100000']

    # areaName = areaNames[0]
    # areaUrl = areaDict[areaName]
    # layout = layouts[0]
    # priceRange = priceRanges[0]
    # layouts = ['l1','l2','l3','l4','l5']
    pool = multiprocessing.Pool(processes=5)
    layouts = ['l1', 'l2', 'l3', 'l4', 'l5','l6']
    pool.map(main, layouts)
    pool.close()
    pool.join()
