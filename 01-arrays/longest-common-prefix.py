'''
Problem: Longest Common Prefix
LeetCode: #14
Difficulty: Easy
Pattern: Array
Status: Hint
Date: 2026-08-27
'''

class Solution:
    def longestCommonPrefix(self, strs):
        l=list(zip(*strs))
        s=''
        for i in l:
            if len(set(i))==1:
                s+=i[0]
            else:
                break
        return s