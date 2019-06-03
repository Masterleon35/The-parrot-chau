#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests
import json
from tqdm import tqdm


# In[4]:


full_address_list = list(pd.read_excel('/Users/litianhao/Desktop/processed/completed/company-node_mapping.xlsx',header=None,keep_default_na=False).loc[:,2])


# In[13]:


p_c_ad = []
for address in tqdm(full_address_list):
    address = address.strip()
    if address:
        param = {
            'key':'820921c611b0b12418ce4bba206efeea',
            'keywords':address,
            'output':'JSON'
        }
        result = requests.get('https://restapi.amap.com/v3/place/text?',params=param)
        result_dic = json.loads(result.text)
        try:result_dic['pois']
        except:print(result_dic)
        else:
            if result_dic['pois']:
                if result_dic['pois'][0]['adname']:
                    p_c_ad.append(result_dic['pois'][0]['adname'])
                elif result_dic['pois'][0]['cityname']:
                    p_c_ad.append(result_dic['pois'][0]['cityname'])
                elif result_dic['pois'][0]['pname']:
                    p_c_ad.append(result_dic['pois'][0]['pname'])
                else:
                    p_c_ad.append('')
            else:p_c_ad.append('')
    else:p_c_ad.append('')


# In[25]:


raw = pd.read_excel('/Users/litianhao/Desktop/processed/completed/company-node_mapping.xlsx',header=None,keep_default_na=False)
raw.loc[:,3] = p_c_ad
raw.to_excel('/Users/litianhao/Desktop/step1.xlsx',header=None,index=None)
need_change = pd.read_excel('/Users/litianhao/Desktop/step1.xlsx',header=None,keep_default_na=False)
standard_num_list = pd.read_excel('/Users/litianhao/Desktop/processed/行政区/administrative-area-node_mapping.xlsx',header=None,keep_default_na=False)


# In[28]:


for index in tqdm(range(7,399)):
    info = need_change.loc[index,3]
    if '+' in info:
        info1 = info.split('+')[0]
        info2 = info.split('+')[1]
        for index1 in range(6,2806):
            if standard_num_list.loc[index1,2] == info1 and standard_num_list.loc[index1,6] == info2:
                num = standard_num_list.loc[index1,5]
                need_change.loc[index,6] = num
                need_change.loc[index,5] = ''
                need_change.loc[index,4] = ''
                break
            elif standard_num_list.loc[index1,2] == info1 and standard_num_list.loc[index1,4] == info2:
                num = standard_num_list.loc[index1,3]
                need_change.loc[index,5] = num
                need_change.loc[index,4] = ''
                break
            elif standard_num_list.loc[index1,4] == info1 and standard_num_list.loc[index1,6] == info2:
                num = standard_num_list.loc[index1,5]
                need_change.loc[index,6] = num
                need_change.loc[index,5] = ''
                need_change.loc[index,4] = ''
                break
            elif standard_num_list.loc[index1,4] == info1:
                num = standard_num_list.loc[index1,3]
                need_change.loc[index,5] = num
#                 break
            elif standard_num_list.loc[index1,2] == info1:
                num = standard_num_list.loc[index1,3]
                need_change.loc[index,4] = num
#                 break
            
                
    else:
        for index1 in range(6,2806):
            if standard_num_list.loc[index1,6] == info:
                num = standard_num_list.loc[index1,5]
                need_change.loc[index,6] = num
                break
            elif standard_num_list.loc[index1,4] == info:
                num = standard_num_list.loc[index1,3]
                need_change.loc[index,5] = num
                break
            elif standard_num_list.loc[index1,2] == info:
                num = standard_num_list.loc[index1,1]
                need_change.loc[index,4] = num
                break
            
            
                
        
        
                


# In[30]:


changed = pd.DataFrame(need_change,columns=[0,1,2,4,5,6,7,8,9,10])
changed.to_excel('/Users/litianhao/Desktop/2.xlsx',index=None,header=None,columns=None)

