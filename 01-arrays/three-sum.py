'''
Problem: 3Sum
LeetCode: #1
Difficulty: Easy
Pattern: Array
Status: Independent
Date: 2026-08-24
'''
class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        l=set()
        for i in range(len(nums)):
            d={}
            rem=0
            for j in range(i+1,len(nums)):
                rem=-nums[i]-nums[j]
                if rem in d:
                    a=[nums[i],nums[j],rem]
                    l.add(tuple(sorted(a)))
                    # if a not in l:
                    #     l.append(a)
                d[nums[j]]=j
        return [list(i) for i in l]