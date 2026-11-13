# Problem: 1. Two Sum
# Link: https://leetcode.com/problems/two-sum/
# Difficulty: Easy
# Approach: one pass with a hash map of value -> index; look up target - x before storing x
# Time: O(n)   Space: O(n)


class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        seen = {}
        for i, x in enumerate(nums):
            if target - x in seen:
                return [seen[target - x], i]
            seen[x] = i
        return []
