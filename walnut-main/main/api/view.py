#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：view.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/7 
@Desc    ：
"""
from falcons.ops import ProjectOps


class ViewDelete(ProjectOps):
    name = '删除组件视图-视图类型：公共'
    uri = '/team/{team_uuid}/container_component/{component_uuid}/view/{view_uuid}/delete'
    api_type = 'POST'


class UserViewDelete(ProjectOps):
    """删除组件视图"""
    name = '删除组件视图-视图类型：私人'
    uri = '/team/{team_uuid}/container_component/{component_uuid}/user_view/{view_uuid}/delete'
    api_type = 'POST'


class ViewUpdate(ProjectOps):
    """更新组件视图"""
    name = '更新组件视图'
    uri = '/team/{team_uuid}/container_component/{component_uuid}/view/{view_uuid}/update'
    api_type = 'POST'


class ViewsAdd(ProjectOps):
    """添加组件视图"""
    name = '添加组件视图'
    uri = '/team/{team_uuid}/container_component/{component_uuid}/user_views/add'
    api_type = 'POST'


class UserView(ProjectOps):
    name = '用户视图列表'
    uri = '/team/{team_uuid}/container_component/{component_uuid}/user_views'
    api_type = 'GET'
