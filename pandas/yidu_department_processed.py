#!/usr/bin/env python
# coding: utf-8

# In[1274]:


import pandas as pd
import numpy as np
import codecs

from openpyxl import load_workbook


# ## 第一步

# In[1275]:


pd.set_option('display.max_rows',2000) 
department_standard = pd.read_excel('/Users/litianhao/Desktop/科室数据审核后0527-1.xlsx',sheet_name="yidu-科室标准",dtype=str,keep_default_na=True)
department_standard = department_standard.iloc[:,0:2]
# department_standard = department_standard.dropna(how='all')

samemean_df = pd.read_excel('/Users/litianhao/Desktop/科室数据审核后0527-1.xlsx',sheet_name="同义词表",dtype=str,keep_default_na=False)
samemean_df = samemean_df.dropna(how='all')

guiyi_df = pd.read_excel('/Users/litianhao/Desktop/科室数据审核后0527-1.xlsx',sheet_name="归一表",dtype=str,keep_default_na=True)
guiyi_df = guiyi_df.dropna(how='all')
guiyi_df.index = range(len(guiyi_df))


# In[1276]:


#处理字符串空格
def del_space(x):
    if type(x) == type('a'):
        x = x.strip()
    return x


# In[1277]:


department_standard = department_standard.applymap(del_space)
guiyi_df = guiyi_df.applymap(del_space)
samemean_df = samemean_df.applymap(del_space)


# In[1278]:



for i in range(len(guiyi_df)):
    if pd.isna(guiyi_df.iloc[i,0]):
        guiyi_df.iloc[i,0] = guiyi_df.iloc[i-1,0]
        guiyi_df.iloc[i,1] = guiyi_df.iloc[i-1,1]
#         if pd.isna(guiyi_df.iloc[i,3]):
#             guiyi_df.iloc[i,3] = guiyi_df.iloc[i-1,3]
for i in range(len(guiyi_df)):
    if pd.isna(guiyi_df.iloc[i,2]):
        guiyi_df.iloc[i,2] = guiyi_df.iloc[i,1]


# In[1279]:


guiyi_df['一级科室'] = np.nan
guiyi_df['二级科室'] = np.nan
for i in range(len(guiyi_df)):
    if len(guiyi_df.iloc[i,0]) == 2:
        pass
    elif len(guiyi_df.iloc[i,0]) == 4:
        guiyi_df.iloc[i,0],guiyi_df.iloc[i,3] = guiyi_df.iloc[i,0][:2],guiyi_df.iloc[i,0]
    elif len(guiyi_df.iloc[i,0]) == 6:
        guiyi_df.iloc[i,0],guiyi_df.iloc[i,3],guiyi_df.iloc[i,4] = np.nan,guiyi_df.iloc[i,0][:4],guiyi_df.iloc[i,0]


# In[1284]:


guiyi_df = pd.DataFrame(guiyi_df,columns=['YD编码','一级科室','二级科室','YD科室','待归一词'])
guiyi_df = guiyi_df.drop_duplicates(subset=['YD编码','一级科室','二级科室'])
guiyi_df.loc[:,['YD编码','一级科室','二级科室']].to_excel('sturcture.xlsx',index = None)


# In[1243]:


guiyi_df1 = guiyi_df.copy()
for index in range(len(guiyi_df1)):
    if not pd.isnull(guiyi_df1.loc[index,'一级科室']):
        guiyi_df1.drop([index],inplace=True)
guiyi_df1.to_excel('1.xlsx',index = None)


# In[1273]:


guiyi_df2 = guiyi_df.copy()
for index in range(len(guiyi_df2)):
    if not pd.isnull(guiyi_df2.loc[index,'二级科室']) or pd.isnull(guiyi_df2.loc[index,'一级科室']):
        guiyi_df2.drop([index],inplace=True)
guiyi_df2.to_excel('2.xlsx',index = None)


# In[1245]:


guiyi_df3 = guiyi_df.copy()
for index in range(len(guiyi_df3)):
    if not pd.isnull(guiyi_df3.loc[index,'YD编码']):
        guiyi_df3.drop([index],inplace=True)
guiyi_df3.to_excel('3.xlsx',index = None)


# ## 2

# In[1246]:


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


# In[1247]:


for line in samemean_list:
    samemean_df_standard = samemean_df_standard.append([line[0]]*(len(line)-1))
    samemean_df_standard1 = samemean_df_standard1.append(line[1:])
all_df = pd.concat([samemean_df_standard,samemean_df_standard1],axis=1)
all_df = all_df.applymap(del_space)


# In[1248]:


all_df.columns = ['a','b']
all_df.index = range(len(all_df))


# ## 3

# In[1249]:


tongyi1 = pd.merge(left=guiyi_df1,right=all_df,how='outer',left_on='待归一词',right_on='a').dropna(subset = ['YD编码','一级科室','二级科室'],how = 'all').dropna(subset = ['a','b'],how = 'all')
tongyi1[['YD编码','b']].to_excel('tongyi_1.xlsx',index = None)


# In[1250]:


tongyi2 = pd.merge(left=guiyi_df2,right=all_df,how='outer',left_on='待归一词',right_on='a').dropna(subset = ['YD编码','一级科室','二级科室'],how = 'all').dropna(subset = ['a','b'],how = 'all')
tongyi2[['一级科室','b']].to_excel('tongyi_2.xlsx',index = None)


# In[1251]:


tongyi3 = pd.merge(left=guiyi_df3,right=all_df,how='outer',left_on='待归一词',right_on='a').dropna(subset = ['YD编码','一级科室','二级科室'],how = 'all').dropna(subset = ['a','b'],how = 'all')
tongyi3[['二级科室','b']].to_excel('tongyi_3.xlsx',index = None)


# In[1252]:


get_bug = pd.merge(left=guiyi_df,right=all_df,how='outer',left_on='待归一词',right_on='a')


# In[900]:


with codecs.open('not_match.txt','w','utf8')as w:
    for x in not_match:
        w.write(x+'\n')
    


# In[1253]:


not_match = []
for index in range(len(get_bug)):
    if pd.isnull(get_bug.loc[index,'YD编码']) and pd.isnull(get_bug.loc[index,'一级科室']) and pd.isnull(get_bug.loc[index,'二级科室']):
        not_match.append((get_bug.loc[index,'a']))
not_match = list(set(not_match))


# In[1254]:


not_match


# ## 结束
