#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：layout.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/5 
@Desc    ：
"""
from falcons.ops import ProjectOps


class LayoutAdd(ProjectOps):
    """添加视图"""
    name = '添加视图'
    uri = '/team/{team_uuid}/layouts/add'
    api_type = 'POST'


class LayoutUpdate(ProjectOps):
    """更新视图"""
    name = '更新视图'
    uri = '/team/{team_uuid}/layout/{layout_uuid}/update'
    api_type = 'POST'


class LayoutDelete(ProjectOps):
    """删除视图"""
    name = '删除视图'
    uri = '/team/{team_uuid}/layout/{layout_uuid}/delete'
    api_type = 'POST'


class LayoutProjectAdd(ProjectOps):
    """添加视图到项目"""
    name = '添加视图到项目'
    uri = '/team/{team_uuid}/project/{project_uuid}/layouts/add'
    api_type = 'POST'


class LayoutProjectDelete(ProjectOps):
    """删除项目内视图"""
    name = '删除项目内视图'
    uri = '/team/{team_uuid}/project/{project_uuid}/layout/{layout_uuid}/delete'
    api_type = 'POST'


class LayoutFieldAdd(ProjectOps):
    """视图添加属性"""
    name = '视图添加属性'
    uri = '/team/{team_uuid}/layout/{layout_uuid}/fields/add'
    api_type = 'POST'


class LayoutFieldConfig(ProjectOps):
    """获取视图的属性配置信息"""
    name = '获取视图属性配置信息'
    uri = '/team/{team_uuid}/layout/{layout_uuid}/fields/field_config'
    api_type = 'GET'


class LayoutTypes(ProjectOps):
    """获取视图类型列表"""
    name = '获取视图类型列表'
    uri = '/team/{team_uuid}/layouts'
    api_type = 'GET'


class LayoutTypeConfigs(ProjectOps):
    """获取视图类型配置列表"""
    name = '获取视图类型配置列表'
    uri = '/team/{team_uuid}/Layout_type_configs'
    api_type = 'GET'


class LayoutDraftGet(ProjectOps):
    """视图草稿"""
    name = '获取-视图草稿'
    uri = '/team/{team_uuid}/layout/{layout_uuid}/draft'
    api_type = 'GET'


class LayoutDraftSet(ProjectOps):
    """视图草稿"""
    name = '保存-视图草稿'
    uri = '/team/{team_uuid}/layout/{layout_uuid}/draft'
    api_type = 'POST'


class LayoutDraftDrop(ProjectOps):
    """取消修改-视图草稿"""
    name = '取消修改-视图草稿'
    uri = '/team/{team_uuid}/layout/{layout_uuid}/draft/drop'
    api_type = 'POST'


class LayoutDraftPublish(ProjectOps):
    """发布-视图草稿"""
    name = '发布-视图草稿'
    uri = '/team/{team_uuid}/layout/{layout_uuid}/draft/publish'
    api_type = 'POST'


class ProjLayoutCopy(ProjectOps):
    """项目配置-视图另存为"""
    name = '项目配置-视图另存为'
    uri = '/team/{team_uuid}/issue_type_scope/{issue_type_scope}/layout/copy'
    api_type = 'POST'


class ProjSwitchLayout(ProjectOps):
    """项目设置-视图切换"""
    name = '项目设置-视图切换'
    uri = '/team/{team_uuid}/issue_type_scope/{issue_type_scope}/layout/update'
    api_type = 'POST'


class GlobalLayoutCopy(ProjectOps):
    """全局配置-视图另存为"""
    name = '全局配置-视图另存为'
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/layout/copy'
    api_type = 'POST'


class GlobalSwitchLayout(ProjectOps):
    name = '全局配置-视图切换'
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/layout/update'
    api_type = 'POST'


class GlobalTabConfigUpdate(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/tab_configs/update'
    name = '全局配置-更新模块标签页'
    api_type = 'POST'


class GlobalIssueTabConfigs(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/tab_configs'
    name = '全局配置工作项-模块标签页配置'
    api_type = 'GET'
