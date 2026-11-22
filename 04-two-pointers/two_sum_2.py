'''
Problem: Two Sum II - Input Array Is Sorted
LeetCode: #11
Difficulty: Medium
Pattern: Two Pointers
Status: Hint
Date: 2026-11-22
'''
class Solution:
    def twoSum(self, numbers: list[int], target: int) -> list[int]:
        i=0
        j=len(numbers)-1
        while i<j:
            if numbers[i]+numbers[j]==target:return [i+1,j+1]
            elif numbers[i]+numbers[j]<target:i+=1
            else:j-=1
        