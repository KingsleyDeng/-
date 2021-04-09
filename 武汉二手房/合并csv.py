import os
import pandas as pd
import glob

# 查看同文件夹下的csv文件数
csv_list = glob.glob('*.csv')
print('共发现%s个CSV文件' % len(csv_list))
print('正在处理。。。。。。')
for i in csv_list:
    fr = open(i, 'rb').read()
    # 将结果保存到result.csv
    with open('result.csv', 'ab') as f :
        f.write(fr)

print('合并完毕')