'''
Problem: Concatenation of Array
LeetCode: #1929
Difficulty: Easy
Pattern: Array
Status: Independent
Date: 2026-08-23
'''

class Solution:
    def getConcatenation(self, nums):
        n=len(nums)
        ans=nums+nums
        return ans