#!/usr/bin/env python
# coding: utf-8

# In[1819]:


import pandas as pd
import numpy as np
import codecs
from tqdm import tqdm
from openpyxl import load_workbook


# ## 第一步

# In[1820]:


pd.set_option('display.max_rows',2000) 
department_standard = pd.read_excel('/Users/litianhao/Desktop/科室数据审核后0527-1.xlsx',sheet_name="yidu-科室标准",dtype=str,keep_default_na=True)
department_standard = department_standard.iloc[:,0:2]
# department_standard = department_standard.dropna(how='all')

samemean_df = pd.read_excel('/Users/litianhao/Desktop/科室数据审核后0527-1.xlsx',sheet_name="同义词表",dtype=str,keep_default_na=False)
samemean_df = samemean_df.dropna(how='all')

guiyi_df = pd.read_excel('/Users/litianhao/Desktop/科室数据审核后0527-1.xlsx',sheet_name="归一表",dtype=str,keep_default_na=True)
guiyi_df = guiyi_df.dropna(how='all')
guiyi_df.index = range(len(guiyi_df))


# In[1821]:


#处理字符串空格
def del_space(x):
    if type(x) == type('a'):
        x = x.strip()
    return x
department_standard = department_standard.applymap(del_space)
guiyi_df = guiyi_df.applymap(del_space)
samemean_df = samemean_df.applymap(del_space)


# In[1822]:


for i in range(len(guiyi_df)):
    if pd.isna(guiyi_df.iloc[i,0]):
        guiyi_df.iloc[i,0] = guiyi_df.iloc[i-1,0]
        guiyi_df.iloc[i,1] = guiyi_df.iloc[i-1,1]
#         if pd.isna(guiyi_df.iloc[i,3]):
#             guiyi_df.iloc[i,3] = guiyi_df.iloc[i-1,3]
for i in range(len(guiyi_df)):
    if pd.isna(guiyi_df.iloc[i,2]):
        guiyi_df.iloc[i,2] = guiyi_df.iloc[i,1]


# In[1823]:


guiyi_df['一级科室'] = np.nan
guiyi_df['二级科室'] = np.nan
for i in range(len(guiyi_df)):
    if len(guiyi_df.iloc[i,0]) == 2:
        pass
    elif len(guiyi_df.iloc[i,0]) == 4:
        guiyi_df.iloc[i,0],guiyi_df.iloc[i,3] = guiyi_df.iloc[i,0][:2],guiyi_df.iloc[i,0]
    elif len(guiyi_df.iloc[i,0]) == 6:
        guiyi_df.iloc[i,0],guiyi_df.iloc[i,3],guiyi_df.iloc[i,4] = np.nan,guiyi_df.iloc[i,0][:4],guiyi_df.iloc[i,0]


# ## 结构

# In[1824]:


guiyi_df = pd.DataFrame(guiyi_df,columns=['YD编码','一级科室','二级科室','YD科室','待归一词'])
guiyi_df_s = guiyi_df.copy()
guiyi_df_s = guiyi_df_s.drop_duplicates(subset=['YD编码','一级科室','二级科室'])
guiyi_df_s.loc[:,['YD编码','一级科室','二级科室']].to_excel('sturcture.xlsx',index = None,header = None)


# In[1825]:


guiyi_df1 = guiyi_df.copy()
for index in range(len(guiyi_df1)):
    if not pd.isnull(guiyi_df1.loc[index,'一级科室']):
        guiyi_df1.drop([index],inplace=True)
guiyi_part1 = guiyi_df1.iloc[:,[0,3,4]]
guiyi_part1.index = range(len(guiyi_part1))
# guiyi_df1.to_excel()

guiyi_df2 = guiyi_df.copy()
for index in range(len(guiyi_df2)):
    if not pd.isnull(guiyi_df2.loc[index,'二级科室']) or pd.isnull(guiyi_df2.loc[index,'一级科室']):
        guiyi_df2.drop([index],inplace=True)
# guiyi_df2.to_excel('2.xlsx',index = None)
guiyi_part2 = guiyi_df2.iloc[:,[1,3,4]]
guiyi_part2.index = range(len(guiyi_part2))

guiyi_df3 = guiyi_df.copy()
for index in range(len(guiyi_df3)):
    if not pd.isnull(guiyi_df3.loc[index,'YD编码']):
        guiyi_df3.drop([index],inplace=True)
guiyi_part3 = guiyi_df3.iloc[:,[2,3,4]]
guiyi_part3.index = range(len(guiyi_part3))
# guiyi_df3.to_excel('3.xlsx',index = None)


# In[1826]:


pd.concat([guiyi_part1,guiyi_part2,guiyi_part3],axis=1,ignore_index=True).to_excel('guiyi.xlsx',index = None,header=False)


# ## 2

# In[1827]:


samemean_df_standard = pd.DataFrame()
samemean_df_standard1 = pd.DataFrame()
samemean_list = []
i = 0
for index in range(len(samemean_df)):
    samemean_list.append(list(samemean_df.loc[index,:]))
samemean_list_plus = []

for line in samemean_list:
    mid = []
    for word in line:
        if word:
            mid.append(word)
    samemean_list_plus.append(mid)
samemean_list = samemean_list_plus


# In[1828]:


for line in samemean_list:
    samemean_df_standard = samemean_df_standard.append([line[0]]*(len(line)-1))
    samemean_df_standard1 = samemean_df_standard1.append(line[1:])
all_df = pd.concat([samemean_df_standard,samemean_df_standard1],axis=1)
all_df = all_df.applymap(del_space)


# In[1829]:


all_df.columns = ['a','b']
all_df.index = range(len(all_df))


# ## 3

# In[1830]:


tongyi1 = pd.merge(left=guiyi_df1,right=all_df,how='outer',left_on='待归一词',right_on='a').dropna(subset = ['YD编码','一级科室','二级科室'],how = 'all').dropna(subset = ['a','b'],how = 'all')
tongyi1.index = range(len(tongyi1))
# tongyi1[['YD编码','b']].to_excel('tongyi_1.xlsx',index = None)


# In[1831]:


tongyi2 = pd.merge(left=guiyi_df2,right=all_df,how='outer',left_on='待归一词',right_on='a').dropna(subset = ['YD编码','一级科室','二级科室'],how = 'all').dropna(subset = ['a','b'],how = 'all')
tongyi2.index = range(len(tongyi2))
# tongyi2[['一级科室','b']].to_excel('tongyi_2.xlsx',index = None)


# In[1832]:


tongyi3 = pd.merge(left=guiyi_df3,right=all_df,how='outer',left_on='待归一词',right_on='a').dropna(subset = ['YD编码','一级科室','二级科室'],how = 'all').dropna(subset = ['a','b'],how = 'all')
tongyi3.index = range(len(tongyi3))
# tongyi3[['二级科室','b']].to_excel('tongyi_3.xlsx',index = None)


# In[1833]:


# with codecs.open('not_match.txt','w','utf8')as w:
#     for x in not_match:
#         w.write(x+'\n')
    


# In[1834]:


get_bug = pd.merge(left=guiyi_df,right=all_df,how='outer',left_on='待归一词',right_on='a')

not_match = []
for index in range(len(get_bug)):
    if pd.isnull(get_bug.loc[index,'YD编码']) and pd.isnull(get_bug.loc[index,'一级科室']) and pd.isnull(get_bug.loc[index,'二级科室']):
        not_match.append((get_bug.loc[index,'a']))
not_match = list(set(not_match))


# In[1835]:


pd.concat([tongyi1[['YD编码','b']],tongyi2[['一级科室','b']],tongyi3[['二级科室','b']]],axis = 1).to_excel('tongyi.xlsx',index = None,header = False)


# ## 标准科室构建结束

# ## 医院科室与标准科室关联

# In[1894]:


raw = pd.read_excel('/Users/litianhao/Desktop/processed/completed/yidu-departmentnode_mapping.xlsx',sheet_name='tongyi',skiprows = 7,header=None,dtype=str)
node_3_tongyi = raw[[4,5]].rename(columns={4:'a',5:'b'}).dropna(subset = ['a','b'])
node_2_tongyi = raw[[2,3]].rename(columns={2:'a',3:'b'}).dropna(subset = ['a','b'])
node_1_tongyi = raw[[0,1]].rename(columns={0:'a',1:'b'}).dropna(subset = ['a','b'])


# In[1895]:


tongyi = pd.concat([node_1_tongyi,node_2_tongyi,node_3_tongyi],ignore_index=True)


# In[1896]:


raw1 = pd.read_excel('/Users/litianhao/Desktop/processed/completed/yidu-departmentnode_mapping.xlsx',sheet_name='guiyi',skiprows = 7,dtype=str,header=None)
node_3_guiyi = raw1[[6,8]].rename(columns={6:'a',8:'b'}).dropna(subset = ['a','b'])
node_2_guiyi = raw1[[3,5]].rename(columns={3:'a',5:'b'}).dropna(subset = ['a','b'])
node_1_guiyi = raw1[[0,2]].rename(columns={0:'a',2:'b'}).dropna(subset = ['a','b'])
guiyi = pd.concat([node_1_guiyi,node_2_guiyi,node_3_guiyi],ignore_index=True)


# In[1897]:


guiyi_tongyi = pd.concat([guiyi,tongyi],ignore_index=True)
guiyi_tongyi = guiyi_tongyi.sort_values(by = 'a')
guiyi_tongyi.index = range(len(guiyi_tongyi))


# In[1899]:


guiyi_tongyi = guiyi_tongyi.drop_duplicates(subset = ['a','b'])


# In[1900]:


hospital_department_name = pd.read_excel('/Users/litianhao/Desktop/processed/completed/administrative-hospital-department-node_mapping.xlsx',skiprows=6)[['Unnamed: 0','s:name','Unnamed: 2','s:name.1','Unnamed: 4','s:name.2']]
len(hospital_department_name.drop_duplicates())


# In[1901]:


result = pd.merge(left=hospital_department_name,right=guiyi_tongyi,how='left',left_on='s:name.2',right_on='b')


# In[1887]:


# result = result.rename(columns = {'s:name.2':'医院二级节点名称','a':'yidu科室编号','b':'科室数据审核后0527-1/同义/归一名称'})
# result.to_excel('医院_yidu科室关联结果.xlsx',index = None)
# result.drop_duplicates().sort_values(by = 'yidu科室编号').to_excel('医院_yidu科室关联结果_去重版.xlsx',index = None)


# In[1902]:


hospital_department = pd.read_excel('/Users/litianhao/Desktop/processed/completed/administrative-hospital-department-node_mapping.xlsx',skiprows=6).iloc[:,[0,1,2,3,4,5]]


# In[1905]:


pd.merge(left = hospital_department,right = result,left_on = ['Unnamed: 0','s:name','Unnamed: 2','s:name.1','Unnamed: 4','s:name.2'],right_on = ['Unnamed: 0','s:name','Unnamed: 2','s:name.1','Unnamed: 4','s:name.2'],how = 'right').iloc[:,[0,1,2,3,4,5,6]].to_excel('finish.xlsx',index = None,header = None)


# 数量为7336，修改之后还可用上面代码但要去重复

# In[1909]:


num = pd.merge(left = hospital_department,right = result,left_on = ['Unnamed: 0','s:name','Unnamed: 2','s:name.1','Unnamed: 4','s:name.2'],right_on = ['Unnamed: 0','s:name','Unnamed: 2','s:name.1','Unnamed: 4','s:name.2'],how = 'right').loc[:,['a']]


# In[1910]:


#查空值
i = 0
for x in num['a']:
    if type(x) == type('a'):
        pass
    else:print(x,i)
    i+=1

