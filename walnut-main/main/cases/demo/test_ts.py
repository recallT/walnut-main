"""
# -*- coding: utf-8 -*-
# Author: TangS
# FileName: test_ts.py
# DateTime: 2022/9/7 10:56
# SoftWare: PyCharm
"""
from main.actions.task import TaskAction


def test_demo(self):
    # proj_uuid 项目ID，在URL链接中，处于project/项目id
    ise = TaskAction.new_issue_batch(batch_no=5, proj_uuid='B9ei3VVVc3UGEn4J')
