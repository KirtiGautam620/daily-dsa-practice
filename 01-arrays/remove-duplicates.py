'''
Problem: Remove duplicates from sorted array
LeetCode: #26
Difficulty: Easy
Pattern: Array
Status: Independent
Date: 2026-08-27
'''

class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        j=0
        for i in range(1,len(nums)):
            if nums[j]!=nums[i]:
                j+=1
                nums[j]=nums[i]
        return j+1        
        