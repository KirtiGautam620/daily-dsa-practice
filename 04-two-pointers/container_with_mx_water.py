'''
Problem: Container With Most Water
LeetCode: #11
Difficulty: Medium
Pattern: Two Pointers
Status: Hint
Date: 2026-11-22
'''
class Solution:
    def maxArea(self, height):
        area=0
        mx=0
        i=0
        j=len(height)-1
        while i<=j:
            width=j-i
            h=min(height[i],height[j])
            area=width*h
            mx=max(mx,area)
            if height[i]<height[j]:i+=1
            else:j-=1
        return mx