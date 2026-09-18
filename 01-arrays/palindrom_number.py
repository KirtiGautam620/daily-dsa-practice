'''
Problem: Palindrome Number
LeetCode: #9
Difficulty: Easy
Pattern: Array
Status: Independent
Date: 2026-09-18
'''

class Solution:
    def isPalindrome(self, x: int) -> bool:
        r=x
        rev=0
        while x>0:
            rem=x%10
            rev=rev*10+rem
            x=x//10
        return rev==r
