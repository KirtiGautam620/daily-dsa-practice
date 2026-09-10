'''
Problem: Set Mismatch
LeetCode: #645
Difficulty: Easy
Pattern: Array
Status: Independent
Date: 2026-09-10
'''

class Solution:
    def findErrorNums(nums):
        sett=set()
        l=[]
        for i in nums:
            if i in sett:
                dup=i
            else:
                sett.add(i)
        l.append(dup)
        # print(dup)
        # print(sett)
        for i in range(1,len(nums)+1):
            if i in nums:
                continue
            else:
                l.append(i)
        # print(l)
        return l