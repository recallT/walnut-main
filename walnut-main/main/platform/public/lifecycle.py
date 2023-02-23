import os
import sys


def plugin_enable():
    # 获取方法运行的路径
    print('\n#####: ', os.getcwd())  # 获取当前工作目录路径
    print('\n#####: ', os.path.abspath('.'))  # 获取当前工作目录路径
    print('\n#####: ', os.path.abspath('..'))  # 获取当前工作的父目录
    print('\n#####: ', os.path.abspath('../..'))  # 获取当前工作的父目录的父目录
    print('\n#####: ', os.path.realpath(__file__))  # 获取当前工作的父目录的父目录

    print(sys._getframe().f_code.co_filename)  # 当前位置所在的文件名
    print(sys._getframe().f_code.co_name)  # 当前位置所在的函数名
    print(sys._getframe().f_lineno)  # 当前位置所在的行号

    # 读取config.json文件
    file = open('config.json', mode='r', encoding='utf-8')

    print('\nfile: ', file)

    # 获取插件包

    # 解析过程文件
