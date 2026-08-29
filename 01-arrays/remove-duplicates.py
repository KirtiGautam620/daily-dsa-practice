'''
Problem: Remove duplicates from sorted array
LeetCode: #26
Difficulty: Easy
Pattern: Array
Status: Independent
Date: 2026-08-27
'''

class Solution:
    def removeDuplicates(self, nums):
        n=set(nums)
        return len(n)