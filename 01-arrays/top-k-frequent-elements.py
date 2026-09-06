'''
Problem: Top K Frequent Elements
LeetCode: #347
Difficulty: Medium
Pattern: Array
Status: Independent
Date: 2026-09-06
'''
nums = [1,2,1,2,1,2,3,1,3,2]
k =2
l=[]
d={}
for i in nums:
    if i in d:
        d[i]+=1
    else:
        d[i]=1
mx=(max(d.values()))
sorted_d=dict(sorted(d.items(),key=lambda x:-x[1]))
for key,values in d.items():
    l.append(key)
    k-=1
    if k==0:
        print(l)
        break
print(sorted_d)
print(l)
print(d)