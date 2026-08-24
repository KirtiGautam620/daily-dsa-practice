'''
Problem: Two Sum
LeetCode: #1
Difficulty: Easy
Pattern: Array
Status: Independent
Date: 2026-08-24
'''

class Solution:
    def twoSum(self, nums, target):
        for i in range(len(nums)):
            val=target-nums[i]
            for j in range(i+1,len(nums)):
                if nums[j]==val:
                    return i,j