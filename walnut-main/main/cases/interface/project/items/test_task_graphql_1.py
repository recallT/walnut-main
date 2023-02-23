#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_task_graphql_2.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/10 
@Desc    ：任务管理筛选器测试用例
"""

from falcons.com.nick import feature, story, mark, parametrize, step

from main.api.project import ItemGraphql
from main.params import graphql


@mark.smoke
@feature('任务管理-任务筛选')
class TestTaskFilter:

    @story('不勾选自定义复制的数据')
    @parametrize('param', graphql.task_graphql_1())
    def test_task_filter_1(self, param):
        """不勾选自定义复制的数据"""
        cpy = ItemGraphql()
        # 调用接口
        cpy.call(param.json, **param.extra)
        # 检查接口响应码
        cpy.is_response_code(200)


@mark.smoke
@feature('项目列表-筛选-系统属性')
class TestProjectFilter:

    @story('筛选-系统属性')
    @parametrize('param', graphql.project_graphql())
    def test_project_filter(self, param):
        """筛选-系统属性"""
        cpy = ItemGraphql()
        step_name, p = param
        with step(step_name):
            # 调用接口
            cpy.call(p.json, **p.extra)
            # 检查接口响应码
            cpy.is_response_code(200)
