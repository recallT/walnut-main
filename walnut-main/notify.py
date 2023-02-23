#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：notify.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/12 
@Desc    ：构建结果 企业微信消息通知
"""
import sys

from main.helper import Notify

if __name__ == '__main__':
    name = sys.argv[1]

    notify = Notify(name)

    notify.run()
    notify.get_job_json()
    print(notify.job_json)
    # print(notify.get_user_name())
