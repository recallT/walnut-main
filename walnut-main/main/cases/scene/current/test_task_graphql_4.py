#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_task_graphql_2.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/10 
@Desc    ：任务管理筛选器测试用例
"""

from falcons.com.nick import feature, story, mark, parametrize

from main.api.project import ItemGraphql
from main.params import graphql


@mark.smoke
@feature('任务管理-任务筛选')
class TestTaskFilter4:

    @story('不勾选自定义复制的数据')
    @parametrize('param', graphql.task_graphql_4())
    def test_task_filter_4(self, param):
        """不勾选自定义复制的数据"""
        cpy = ItemGraphql()
        # 调用接口
        cpy.call(param.json, **param.extra)
        # 检查接口响应码
        cpy.is_response_code(200)
