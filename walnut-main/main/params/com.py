#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：com.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/7 
@Desc    ：
"""
from falcons.ops import generate_param


def gen_stamp(keys: dict):
    """

    :param keys:
            {k1: 0,k2:0 }
        'component_template', #  组件模板
        'dashboard', #  仪表盘
        'department', #  部门信息
        'field', #  属性
        'field_config', #  属性配置
        'group', #
        'issue_type', #  工作项
        'issue_type_config', #  工作项配置
        'pipeline', #  pipline
        'product_component_template', #  产品组件模板
        'project', #  产品
        'project_template', #  项目模板
        'role', #  角色
        'role_config', #  角色配置
        'sprint', #  迭代
        'task_link_type', #  关联工作项类型
        'task_status', #  工作项状态
        'task_status_config', #  工作项状态配置
        'team', #  团队信息
        'team_member', #  团队成员
        'transition', #  后置动作
    :return:
    """

    return generate_param(keys)[0]


def issue_type():
    return generate_param({})[0]
