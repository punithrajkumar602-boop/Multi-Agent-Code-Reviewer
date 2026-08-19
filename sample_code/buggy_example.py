"""
Sample file with intentional style, bug, and test-coverage issues,
used to demo the multi-agent reviewer without needing a live GitHub PR.
"""
import os


def calc_avg(nums):
    total = 0
    for i in range(len(nums)):
        total = total + nums[i]
    return total / len(nums)


def GetUserData(userId):
    data = {}
    data["id"] = userId
    return data


def divide(a, b):
    return a / b


def read_file(path):
    f = open(path)
    content = f.read()
    return content
