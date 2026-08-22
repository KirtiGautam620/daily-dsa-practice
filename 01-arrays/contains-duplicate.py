'''
# Problem: Contains Duplicate
# LeetCode: #217
# Difficulty: Easy
# Pattern: Hashing
# Status: Independent
# Date: 2026-08-23
# '''

class Solution:
    def containsDuplicate(self, nums):
        d={}
        for i in nums:
            if i not in d:
                d[i]=1
            else:
                d[i]+=1
        for k,v in d.items():
            if v>=2:
                return True
        return False
