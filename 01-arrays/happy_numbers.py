'''
Problem: Happy Number
LeetCode: #202
Difficulty: Easy
Pattern: Array
Status: Independent
Date: 2026-09-16
'''
class Solution:
    def isHappy(self, n: int) -> bool:
        s=set()
        while n!=1:
            if n in s: 
                return False
            s.add(n)
            a=0
            while n>0:
                dig=n%10
                a+=dig**2
                n//=10
            n=a
        return True