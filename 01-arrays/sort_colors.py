'''
Problem: Sort Colors
LeetCode: #75
Difficulty: Medium
Pattern: Array
Status: Independent
Date: 2026-09-04
'''

class Solution:
    def sortColors(self, nums) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        n0,n1,n2=0,0,0
        n0=nums.count(0)
        n1=nums.count(1)
        n2=nums.count(2)
        nums[:n1+1]=[0]*n0
        nums[n1:n1+n2+1]=[1]*n1
        nums[n1+n2:]=[2]*n2
        return nums
        