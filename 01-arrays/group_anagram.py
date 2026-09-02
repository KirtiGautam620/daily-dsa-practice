'''
Problem: Group Anagrams
LeetCode: #49
Difficulty: Medium
Pattern: Array
Status: Hint
Date: 2026-09-02
'''

strs = ["eat","tea","tan","ate","nat","bat"]
# [["bat"],["nat","tan"],["ate","eat","tea"]]
a=[]
d={}
for i in strs:
    s="".join(sorted(i))
    if s in d:
        d[s].append(i)
    else:
        d[s]=[s]
for k,v in d.items():
    a.append(v)
print(a)
print(d)