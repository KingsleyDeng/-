import pandas as pd
import re

df = pd.read_excel('result.xlsx')
df.sort_values(by='总价')

# 车位条件，不一定严谨
mask = ((df['详情'].str.contains('地下室'))
           #         & (df['详情'].str.contains('1室'))
           #         &(~df['详情'].str.contains(r'地下室\(共[2-9]|[1-9]\d+层\)'))
           ) | ((df['详情'].str.contains('底层')) & (df['详情'].str.contains('1室'))
                & (~df['详情'].str.contains(r'底层\(共[2-9]|[1-9]\d+层\)'))
                )

#%%
# 房子
house = df[~mask]
#%%
# 车位
carport = df[mask]
#%%
carport.sort_values(by='总价')
#%%
house.sample(10)

# 详情信息解析
s = '中楼层(共9层)|2007年建|1室1厅|24.78平米|北'
# s = '地下室|2014年建|1室0厅|39.52平米|东'
# s = '底层(共2层)5室3厅|326.56平米|东南西北'
# s = '地下室1室0厅|11.9平米|南'
# re.split(r'(.+?)(\(共(.*)层\))*(\|((.*)年建)*\|)*?(\d+室.*?)\|(.*)平米\|(.*)',s)
re.split(r'(.+?)(?:\(共(.*)层\))?(?:\|(.*)年建\|)*?(\d+室.*?)\|(.*)平米\|(.*)',s)
for i, s in enumerate(house['详情'].to_list()):
    try:
        a = re.split(r'(.+?)(\(共(.*)层\))*(\|(.*)年建\|)*?(\d+室.*?)\|(.*)平米\|(.*)',s)
    except Exception as e:
        print(e)
        print(s,i)

houseData = house.copy()

#%%
houseData.loc[:,'楼层'] = houseData['详情'].apply(lambda x : re.split(r'(.+?)(?:\(共(.*)层\))?(?:\|(.*)年建\|)*?(\d+室.*?)\|(.*)平米\|(.*)',x)[1])
houseData.loc[:,'楼高'] = houseData['详情'].apply(lambda x : re.split(r'(.+?)(?:\(共(.*)层\))?(?:\|(.*)年建\|)*?(\d+室.*?)\|(.*)平米\|(.*)',x)[2])
houseData.loc[:,'建筑年份'] = houseData['详情'].apply(lambda x : re.split(r'(.+?)(?:\(共(.*)层\))?(?:\|(.*)年建\|)*?(\d+室.*?)\|(.*)平米\|(.*)',x)[3])
houseData.loc[:,'户型'] = houseData['详情'].apply(lambda x : re.split(r'(.+?)(?:\(共(.*)层\))?(?:\|(.*)年建\|)*?(\d+室.*?)\|(.*)平米\|(.*)',x)[4])
houseData.loc[:,'面积'] = houseData['详情'].apply(lambda x : re.split(r'(.+?)(?:\(共(.*)层\))?(?:\|(.*)年建\|)*?(\d+室.*?)\|(.*)平米\|(.*)',x)[5])
houseData.loc[:,'朝向'] = houseData['详情'].apply(lambda x : re.split(r'(.+?)(?:\(共(.*)层\))?(?:\|(.*)年建\|)*?(\d+室.*?)\|(.*)平米\|(.*)',x)[6])
#%%
houseData.reset_index(drop=True, inplace=True)
#%%
houseData.sort_values(by='总价')
#%%
# 均价信息解析
houseData['均价'] = houseData['均价'].str.extract(r'(\d+)')
#%%
houseData['发布时间'] = houseData['关注人数'].str.extract(r'\/(\d+[年|月|日])')
#%%
houseData['关注人数'] = houseData['关注人数'].str.extract(r'(\d+)人关注')
#%%
houseData.head()
#%%
houseData.columns
#%%
ershoufang = houseData[[ '房子ID', '地址',  '总价', '总价单位', '均价', '关注人数', '地区',
                       '价格区间', '户型', '楼层', '楼高', '建筑年份', '面积', '朝向', '发布时间']]
#%%
ershoufang
#%%
ershoufang.info()
#%%
ershoufang.loc[:,['均价','关注人数']] = ershoufang.loc[:,['均价','关注人数']].astype(int)
#%%
ershoufang['面积'] = ershoufang['面积'].astype(float)
#%%
ershoufang.sort_values(by='均价')
#%%
# 二手房源数
ershoufang.房子ID.nunique()
#%%
ershoufang.to_excel(r'武汉二手房data.xlsx',index=None)
