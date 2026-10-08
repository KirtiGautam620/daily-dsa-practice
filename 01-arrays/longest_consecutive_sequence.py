'''
Problem: Longest Consecutive Sequence
LeetCode: #128
Difficulty: Medium
Pattern: Array
Status: Independent
Date: 2026-10-08
'''
class Solution:
    def longestConsecutive(self, nums):
        nums=set(nums)
        nums=list(nums)
        nums.sort()
        p=[]
        c=1
        d=1
        if nums==[]:return 0
        for i in range(1,len(nums)):
            if nums[i]-nums[i-1]==1:
                c+=1
            else:
                c=1
            d=max(c,d)

        return d
        