#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_case_library.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/11/19 
@Desc    ：
"""

from falcons.com.nick import parametrize, feature, story

from main.api.case import CopyCase
from main.params.proj import copy_case


@feature('测试DEMO')
class TestCaseLibrary:
    @story('案例拷贝')
    @parametrize('params', (copy_case(),))
    def test_copy_case_success(self, params):
        """测试Demo"""
        cc = CopyCase()

        json, extra = params

        # 调用接口
        cc.call(json, **extra)
        # 检查接口响应码
        cc.is_response_code(200)
        # 检查测试响应数据
        cc.check_response('not_found_cases_object[0].uuid', 'SjfNsZAW')
        cc.check_response('not_found_cases_object[1].uuid', 'WT1RDPrj')
