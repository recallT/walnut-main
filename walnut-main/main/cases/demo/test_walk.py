#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_walk.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/28 
@Desc    ：
"""
from falcons.helper.functions import collect_module

from main.config import RunVars


def test_walk():
    """"""
    collect_module(RunVars.working_path)
