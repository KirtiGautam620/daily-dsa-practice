'''
Problem: Valid Anagram
LeetCode: #242
Difficulty: Easy
Pattern: Array
Status: Independent
Date: 2026-08-23
'''

class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        d1={}
        for i in s:
            if i not in d1:
                d1[i]=1
            else:
                d1[i]+=1
        d2={}
        for i in t:
            if i not in d2:
                d2[i]=1
            else:
                d2[i]+=1
        for i in s:
            if i in t:
                if d1[i]==d2[i]:
                    continue
                else:
                    return False
            else:
                return False
        for i in t:
            if i in s:
                if d1[i]==d2[i]:
                    continue
                else:
                    return False
            else:
                return False
        return True
