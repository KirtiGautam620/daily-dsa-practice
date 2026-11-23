'''
Problem: Best Time to Buy and Sell Stock
LeetCode: #121
Difficulty: Easy
Pattern: Sliding Window
Status: Hint
Date: 2026-11-23
'''
class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        mx=0
        mn=prices[0]
        for i in range(len(prices)):
            profit=prices[i]-mn
            mx=max(mx,profit)
            mn=min(mn,prices[i])
        return mx