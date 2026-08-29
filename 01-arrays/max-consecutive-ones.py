'''
Problem: Max Consecutive Ones
LeetCode: #485
Difficulty: Easy
Pattern: Array
Status: Independent
Date: 2026-08-29
'''

class Solution:
    def findMaxConsecutiveOnes(self, nums):
        c=0
        mx=0
        for i in range(len(nums)):
            if nums[i]==0:
                mx=max(mx,c)
                c=0
            else:
                c+=1
        mx=max(mx,c)
        return mx
