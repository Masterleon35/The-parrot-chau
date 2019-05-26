#!/usr/bin/env python
# coding: utf-8

# ![201811301632250.png](attachment:201811301632250.png)

# In[94]:


M = 1E100
matrix_test1 = [[0, 9, M, M, M, 14, 15, M],
                  [9, 0, 24, M, M, M, M, M],
                  [M, 24, 0, 6, 2, 18, M, 19],
                  [M, M, 6, 0, 11, M, M, 6],
                  [M, M, 2, 11, 0, 30, 20, 16],
                  [14, M, 18, M, 30, 0, 5, M],
                  [15, M, M, M, 20, 5, 0, 44],
                  [M, M, 19, 6, 16, M, 44, 0]]


# ![20180908090320346.jpeg](attachment:20180908090320346.jpeg)

# In[96]:


M = 1E100
matrix_test2 = [[0, 12, M, M, M, 16, 14],
            [12, 0, 10, M, M, 7, M],
            [M, 10, 0, 3, 5, 6, M],
            [M, M, 3, 0, 4, M, M],
            [M, M, 5, 4, 0, 2, 8],
            [16, 7, 6, M, 2, 0, 9],
            [14, M, M, M, 8, 9, 0]]


# ![%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7%202019-05-05%20%E4%B8%8B%E5%8D%886.17.27.png](attachment:%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7%202019-05-05%20%E4%B8%8B%E5%8D%886.17.27.png)

# In[98]:


matrix_test3 = [
[M, 1,1,M,1,M, 1,1,1,M,M, M,M,M,M,M, M,M,M,M,M],
[1, M,1,M,M,1, M,M,M,M,M, M,M,M,M,M, M,M,M,M,M],
[1, 1,M,1,M,M, M,M,M,M,M, M,M,M,M,M, M,M,M,M,M],
[M, M,1,M,1,M, M,M,M,M,M, M,M,M,M,M, M,M,M,M,M],
[1, M,M,1,M,M, M,M,M,1,1, 1,M,M,M,M, M,M,M,M,M],
[M, 1,M,M,M,M, 1,M,M,M,M, M,M,M,M,M, M,M,M,M,M],
[1, M,M,M,M,1, M,1,M,M,M, M,M,M,M,M, M,M,M,M,M],
[1, M,M,M,M,M, 1,M,1,M,M, M,M,M,M,M, M,M,M,M,M],
[1, M,M,M,M,M, M,1,M,1,M, M,1,M,M,M, M,M,M,M,M],
[M, M,M,M,1,M, M,M,1,M,M, 1,M,M,M,M, M,M,M,M,M],
[M, M,M,M,1,M, M,M,M,M,M, 1,M,1,M,M, M,M,M,M,M],
[M, M,M,M,1,M, M,M,M,1,1, M,M,1,1,M, M,M,M,M,M],
[M, M,M,M,M,M, M,M,1,M,M, M,M,M,1,M, M,M,M,M,M],
[M, M,M,M,M,M, M,M,M,M,1, 1,M,M,1,M, M,1,1,M,M],
[M, M,M,M,M,M, M,M,M,M,M, 1,1,1,M,1, 1,M,M,M,M],
[M, M,M,M,M,M, M,M,M,M,M, M,M,M,1,M, 1,M,1,1,M],
[M, M,M,M,M,M, M,M,M,M,M, M,M,M,1,1, M,M,M,M,1],
[M, M,M,M,M,M, M,M,M,M,M, M,M,1,M,M, M,M,1,M,M],
[M, M,M,M,M,M, M,M,M,M,M, M,M,1,M,1, M,1,M,1,M],
[M, M,M,M,M,M, M,M,M,M,M, M,M,M,M,1, M,M,1,M,1],
[M, M,M,M,M,M, M,M,M,M,M, M,M,M,M,M, 1,M,M,1,M]
]


# ![%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7%202019-05-05%20%E4%B8%8B%E5%8D%886.50.49.png](attachment:%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7%202019-05-05%20%E4%B8%8B%E5%8D%886.50.49.png)

# In[100]:


matrix_test4 = [
[M,1,M,M,M,M,M,M,M,M,M,1],
[1,M,1,M,M,M,M,M,M,M,M,1],
[M,1,M,1,M,M,M,M,M,1,M,M],
[M,M,1,M,1,M,M,1,M,M,M,M],
[M,M,M,1,M,1,M,M,M,M,M,M],
[M,M,M,M,1,M,1,M,M,M,M,M],
[M,M,M,M,M,1,M,1,M,M,M,M],
[M,M,M,1,M,M,1,M,1,1,M,M],
[M,M,M,M,M,M,M,1,M,M,M,M],
[M,M,1,M,M,M,M,1,M,M,1,M],
[M,M,M,M,M,M,M,M,M,1,M,1],
[1,1,M,M,M,M,M,M,M,M,1,M]
]


# In[92]:


def dijkstra(matrix,exit_node_list):
    '''增加虚点的算法'''
    #增加虚点
    M = 1E100
    node_index = len(matrix)
    exit_node_list = [1,2,3]
    for row in matrix:
        if matrix.index(row) in exit_node_list:
            row.append(0)
        else:
            row.append(M)
    last_row = [M]*len(matrix)
    for index in exit_node_list:
        last_row[index] = 0
    matrix.append(last_row)     
    n_columns = len(matrix)
    n_rows = len(matrix[0])
    if node_index >= n_columns or n_columns != n_rows:
        print('Error!')
        return
    found = [node_index]        # 已找到最短路径的节点
    cost = [M] * n_columns          # node_index位置的node到已找到最短路径的节点的最短距离
    cost[node_index] = 0
    path = [[]]*n_columns           # node_index位置的node到其他节点的最短路径
    path[node_index] = [node_index]
    while len(found) < n_columns:   # 当已找到最短路径的节点小于n时
        min_value = M+1
        col = -1
        row = -1
        for f in found:     # 以已找到最短路径的节点所在行为搜索对象
            for i in [x for x in range(n_columns) if x not in found]:   # 只搜索没找出最短路径的列
                if matrix[f][i] + cost[f] < min_value:  # 找出最小值
                    min_value = matrix[f][i] + cost[f]  # 在某行找到最小值要加上node_index位置的node到该行的最短路径
                    row = f         # 记录所在行列
                    col = i
        if col == -1 or row == -1:  # 若没找出最小值且节点还未找完，说明图中存在不连通的节点
            break
        found.append(col)           # 在found中添加已找到的节点
        cost[col] = min_value       # node_index到该节点的最短距离即为min_value
        path[col] = path[row][:]    # 复制node_index到已找到节点的上一节点的路径
        path[col].append(col)       # 再其后添加已找到节点即为node_index位置的node到该节点的最短路
    path.pop()
    for x in path:x.pop(0)
    path = [x[::-1] for x in path]
    cost.pop(-1)
    result = zip(path,cost)
    return result


# In[95]:


list(dijkstra(matrix_test1,[1,2,3]))


# In[97]:


list(dijkstra(matrix_test2,[1,2,3]))


# In[99]:


list(dijkstra(matrix_test3,[1,2,3]))


# In[101]:


list(dijkstra(matrix_test4,[1,2,3]))

