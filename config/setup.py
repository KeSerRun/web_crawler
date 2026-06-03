'''用于检查目录结构和创建必要的文件夹'''
import os

def setup_directories(directories:list=[]):
    # 创建目录
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f'Created directory: {directory}')
        else:
            print(f'Directory already exists: {directory}')