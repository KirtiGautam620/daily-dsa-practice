'''
Problem: Longest Substring Without Repeating Characters
LeetCode: #3
Difficulty: Medium
Pattern: Sliding Window
Status: Hint
Date: 2026-11-23
'''
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        ans=0
        curr=''
        for right in range(len(s)):
            while s[right] in curr:
                curr=curr[1:]
            curr+=s[right]
            ans=max(ans,len(curr))
        return ans