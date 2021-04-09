# 请求网页数据函数
import random
import re
from datetime import time

import requests
from fake_useragent import UserAgent


def get_proxies():
    pass


def get_html(url, proxies):
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


# 循环请求每页数据
num = 0
for page in range(1, pages + 1):
    items = []
    time.sleep(random.random())
    info_url = f'{url}/pg{page}'
    try:
        info_html, proxies = get_html(info_url, proxies)
    except Exception as e:
        print(e)
        continue

    # 找出所有的数据条目
    sellListContent = re.findall(r'<ulclass="sellListContent"log-mod="list">(.*?)</ul>', info_html)[0]
    Lists = re.findall(r'<liclass="clear">(.*?)</li>', sellListContent)

    for List in Lists:
        try:
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
            # item['地区'] = areaName
            # item['价格区间'] = priceRange
            # item['户型'] = layout
            items.append(item)
            num = num + 1
            print(f'{num}个房子信息已经采集!')

        except Exception as e:
            print(e)
            print(item)
            continue

if __name__ == '__main__':
    url = 'https://wh.ke.com/ershoufang/'
    ua = UserAgent(verify_ssl=False)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    }