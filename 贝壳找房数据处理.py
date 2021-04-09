import pandas as pd
import re

df = pd.read_excel('贝壳在售二手房数据20201228.xlsx')
df.sort_values(by='总价')

mask = ((df['详情'].str.contains('地下室'))) | ((df['详情'].str.contains('底层')) & (df['详情'].str.contains('1室'))
                                           & (~df['详情'].str.contains(r'底层\(共[2-9]|[1-9]\d+层\)'))
                                           )

# 房子
house = df[~mask]

# 车位
carport = df[mask]
carport.sort_values(by='总价')
