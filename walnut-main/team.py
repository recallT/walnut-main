#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：team.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/7/11
@Desc    ：
"""
import argparse

from falcons.helper.team import add_team

parser = argparse.ArgumentParser(description='自定义命令行参数')

parser.add_argument('--sprint', dest='sprint', help='后端迭代编号')

parser.add_argument('--team-name', dest='team_name', default='',
                    help='自定义团队名称')

if __name__ == '__main__':
    args = parser.parse_args()
    new_user = add_team(args.sprint, args.team_name)

    print('New Team:', new_user.email)
