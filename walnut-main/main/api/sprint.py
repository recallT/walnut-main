#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：sprint.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/7 
@Desc    ：
"""
from falcons.ops import ProjectOps


class SprintAdd(ProjectOps):
    """迭代-添加"""
    uri = '/team/{team_uuid}/project/{project_uuid}/sprints/add'
    name = '迭代-添加'
    api_type = 'POST'


class SprintStatusUpdate(ProjectOps):
    """迭代状态更新"""
    uri = '/team/{team_uuid}/project/{project_uuid}/sprint/{sprint_uuid}/sprint_statuses/update'
    name = '迭代状态更新'
    api_type = 'POST'


class SprintStatuses(ProjectOps):
    """迭代状态列表"""
    uri = '/team/{team_uuid}/project/{project_uuid}/sprint_statuses'
    name = '迭代状态列表'
    api_type = 'GET'


class SprintDelete(ProjectOps):
    """迭代删除"""
    uri = '/team/{team_uuid}/project/{project_uuid}/sprint/{sprint_uuid}/delete'
    name = '迭代删除'
    api_type = 'POST'


class SprintUpdate(ProjectOps):
    """迭代更新"""
    uri = '/team/{team_uuid}/project/{project_uuid}/sprints/update'
    name = '迭代更新'
    api_type = 'POST'


class SprintFieldAdd(ProjectOps):
    """迭代属性添加"""
    uri = '/team/{team_uuid}/project/{project_uuid}/sprint_fields/add'
    name = '迭代属性添加'
    api_type = 'POST'


class SprintFieldUpdate(ProjectOps):
    """迭代属性变更"""
    uri = '/team/{team_uuid}/project/{project_uuid}/sprint/{sprint_uuid}/sprint_field/{field_uuid}/update'
    name = '迭代属性变更'
    api_type = 'POST'


class SprintFieldDelete(ProjectOps):
    """迭代属性删除"""
    uri = '/team/{team_uuid}/project/{project_uuid}/sprint_field/{field_uuid}/delete'
    name = '迭代属性删除'
    api_type = 'POST'


class BurnDown(ProjectOps):
    """迭代燃尽图"""
    uri = '/team/{team_uuid}/project/{project_uuid}/sprint/{sprint_uuid}/burndown'
    name = '迭代燃尽图'
    api_type = 'GET'


class SprintStatusAdd(ProjectOps):
    """项目设置-新增迭代阶段"""
    uri = '/team/{team_uuid}/project/{project_uuid}/sprint_statuses/add'
    name = '新增迭代阶段'
    api_type = 'POST'


class SprintStageUpdate(ProjectOps):
    """项目设置-更新迭代阶段"""
    uri = '/team/{team_uuid}/project/{project_uuid}/sprint_status/{status_uuid}/update'
    name = '更新迭代阶段'
    api_type = 'POST'


class SprintStatusDelete(ProjectOps):
    """项目设置-删除迭代阶段"""
    uri = '/team/{team_uuid}/project/{project_uuid}/sprint_status/{status_uuid}/delete'
    name = '更新迭代阶段'
    api_type = 'POST'


class ProSprintFieldUpdate(ProjectOps):
    """项目设置-迭代属性变更"""
    uri = '/team/{team_uuid}/project/{project_uuid}/sprint_field/{field_uuid}/update'
    name = '项目设置-迭代属性变更'
    api_type = 'POST'


class ProSprintField(ProjectOps):
    """项目迭代属性"""
    uri = '/team/{team_uuid}/project/{project_uuid}/sprint_fields'
    name = '项目迭代属性'
    api_type = 'GET'


class SprintFieldPosition(ProjectOps):
    """迭代属性位置排序"""
    uri = '/team/{team_uuid}/project/{project_uuid}/sprint_fields/position'
    name = '迭代属性位置排序'
    api_type = 'POST'
