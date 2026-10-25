'''
Problem: Count Subarrays With Loose Bounds
LeetCode: #4089
Difficulty: Medium
Pattern: Array
Status: Hint
Date: 2026-10-25
'''
class Solution:
    def countSubarrays(self, nums: list[int], minK: int, maxK: int) -> int:
        c=0
        invalid=-1
        for i in range(len(nums)):
            if nums[i]<minK or nums[i]>maxK:invalid=i
            else:c+=i-invalid
        return c