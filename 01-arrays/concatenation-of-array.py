'''
Problem: Concatenation of array
Leetcode: #1929
Difficulty: Easy
Pattern: Array

Status:  🟢 Independent

Time Complexity: 0(n)
Space Complexity: 0(n)

Key Learning:
create a new array by concating
'''

class Solution:
    def getConcatenation(self, nums):
        n=len(nums)
        ans=nums+nums
        return ans