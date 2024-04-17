"""
Author: superb
Date: 2024/04/16
Version: 1.0
Desc: 读写工具函数合集
LastEditTime: 2024/04/16
"""

import os

# 写一个读取一个文件夹下所有文件名字的函数，返回一个列表，输入文件夹有可能有嵌套文件夹
def get_files_path(file_dir):
    """
    Get a list of all files in the given directory and its subdirectories.

    Args:
        file_dir (str): The directory to search for files.

    Returns:
        list: A list of file paths.
    """
    L = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            L.append(os.path.join(root, file))
    return L