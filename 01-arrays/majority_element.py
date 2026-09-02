'''
Problem: Majority Element
LeetCode: #169
Difficulty: Easy
Pattern: Array
Status: Independent
Date: 2026-09-02
'''
class Solution:
    def majorityElement(self, nums):
        d={}
        for i in range(len(nums)):
            if nums[i] in d:
                d[nums[i]]+=1
            else:
                d[nums[i]]=1
        mx=-1
        ans=-1
        for k,v in d.items():
            if v>=mx:
                mx=v
                ans=k
        return ans
            