#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：issue.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/5 
@Desc    ：
"""
from falcons.ops import ProjectOps


class IssuesAdd(ProjectOps):
    """添加工作项类型"""
    name = '添加工作项类型'
    uri = '/team/{team_uuid}/issue_types/add'
    api_type = 'POST'


class IssueUpdate(ProjectOps):
    """更新工作项类型"""
    name = '更新工作项类型'
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/update'
    api_type = 'POST'


class IssueDelete(ProjectOps):
    """删除工作项类型"""
    name = '删除工作项类型'
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/delete'
    api_type = 'POST'


class IssueProjectAdd(ProjectOps):
    """添加工作项类型到项目"""
    name = '添加工作项类型到项目'
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_types/add'
    api_type = 'POST'


class IssueProjectDelete(ProjectOps):
    """删除项目内工作项类型"""
    name = '删除项目内工作项类型'
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_uuid}/delete'
    api_type = 'POST'


class IssueFieldAdd(ProjectOps):
    """工作项类型添加属性"""
    name = '工作项类型添加属性'
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/fields/add'
    api_type = 'POST'


class IssueFieldUpdate(ProjectOps):
    """工作项类型属性更新"""
    name = '工作项类型属性更新'
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/field/{field_uuid}/update'
    api_type = 'POST'


class IssueFieldDelete(ProjectOps):
    """工作项类型删除属性"""
    name = '工作项类型删除属性'
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/field/{field_uuid}/delete'
    api_type = 'POST'


class IssueFieldConfig(ProjectOps):
    """获取工作项类型的属性配置信息"""
    name = '获取工作项类型属性配置信息'
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/fields/field_config'
    api_type = 'GET'


class IssueTypes(ProjectOps):
    """获取工作项类型类型列表"""
    name = '获取工作项类型类型列表'
    uri = '/team/{team_uuid}/issue_types'
    api_type = 'GET'


class IssueTypeConfigs(ProjectOps):
    """获取工作项类型类型配置列表"""
    name = '获取工作项类型类型配置列表'
    uri = '/team/{team_uuid}/issue_type_configs'
    api_type = 'GET'


class CopyIssueTypeConfig(ProjectOps):
    """从已有项目中复制工作项"""
    name = '从已有项目中复制工作项'
    uri = '/team/{team_uuid}/project/{project_uuid}/copy_issue_type_configs'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# 全局配置-工作项状态

class StatusAdd(ProjectOps):
    """全局工作项状态新增"""
    uri = '/team/{team_uuid}/task_statuses/add'
    name = '新增工作项状态'
    api_type = 'POST'


class StatusDelete(ProjectOps):
    """全局工作项状态删除"""
    uri = '/team/{team_uuid}/task_status/{status_uuid}/delete'
    name = '删除工作项状态'
    api_type = 'POST'


class StatusUpdate(ProjectOps):
    """全局工作项状态更新"""
    uri = '/team/{team_uuid}/task_status/{status_uuid}/update'
    name = '更新工作项状态'
    api_type = 'POST'


class IssueStatusAdd(ProjectOps):
    """全局工作项-工作流状态新增"""
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/task_statuses/add'
    name = '全局工作项-工作流状态新增'
    api_type = 'POST'


class IssueStepAdd(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_type}/transitions/add'
    name = '全局工作项-工作项新增步骤'
    api_type = 'POST'


class IssueStepDel(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_type}/transition/{transitions_uuid}/delete'
    name = '全局工作项-工作项删除步骤'
    api_type = 'POST'


class IssueStepUpdate(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_type}/task_status/{task_status}/update'
    name = '全局工作项-工作流状态更新'
    api_type = 'POST'



class IssueStatusDelete(ProjectOps):
    """全局工作项-工作流状态删除"""
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/task_status/{status_uuid}/delete'
    name = '全局工作项-工作流状态删除'
    api_type = 'POST'


class IssueStatusUpdate(ProjectOps):
    """全局工作项-工作流状态更新"""
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/task_statuses/update'
    name = '全局工作项-工作流状态更新'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# 工作项类型-工作项权限

class ConstraintsAdd(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/constraints/add'
    name = '属性权限规则新增'
    api_type = 'POST'


class ConstraintsDelete(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/constraints/delete'
    name = '属性权限规则删除'
    api_type = 'POST'


class PermissionRulesAdd(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/permission_rules/add'
    name = '全局工作项权限添加'
    api_type = 'POST'


class ProjConstraintsDelete(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_type_uuid}/constraints/delete'
    name = '项目内属性权限规则删除'
    api_type = 'POST'


class PermissionRulesDelete(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_uuid}/permission_rule/{rule_uuid}/delete'
    name = '全局工作项权限删除'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# 工作项类型-属性与视图-模块标签页

class ProjTabConfigUpdate(ProjectOps):
    uri = '/team/{team_uuid}/issue_type_scope/{issue_type_scope}/tab_configs/update'
    name = '更新模块标签页'
    api_type = 'POST'


class IssueTabConfigs(ProjectOps):
    uri = '/team/{team_uuid}/issue_type_scope/{issue_type_scope}/tab_configs'
    name = '工作项-模块标签页配置'
    api_type = 'GET'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# 工作项类型-工作项工作流

class ProjWorkflowStatusUpdate(ProjectOps):
    # 项目工作流状态变更
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_type_uuid}/task_status/{status_uuid}/update'
    name = '项目工作流状态变更'
    api_type = 'POST'


class ProjWorkflowStatusAdd(ProjectOps):
    # 添加项目工作流工作项状态
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_type_uuid}/task_statuses/add'
    name = '添加项目工作流工作项状态'
    api_type = 'POST'


class ProjWorkflowStatusDelete(ProjectOps):
    # 删除项目工作流工作项状态
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_type_uuid}/task_status/{status_uuid}/delete'
    name = '删除项目工作流工作项状态'
    api_type = 'POST'


class ProjWorkflowTransitionAdd(ProjectOps):
    # 添加项目工作流步骤
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_type_uuid}/transitions/add'
    name = '添加项目工作流步骤'
    api_type = 'POST'


class ProjWorkflowTransitionDelete(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_type_uuid}/transition/{transition_uuid}/delete'
    name = '删除项目工作流步骤'
    api_type = 'POST'


class SortIssueType(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_types/position'
    name = '工作项类型排序'
    api_type = 'POST'


class TaskSort(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_type_uuid}/task_status_configs/position'
    name = '工作项状态排序'
    api_type = 'POST'


class GlobalNoticeRule(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_type_uuid}/notice_rules'
    name = '配置中心工作项提醒列表'
    api_type = 'GET'


class AddGlobalNoticeRule(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_type_uuid}/notice_rules/add'
    name = '配置中心新增工作项提醒列表'
    api_type = 'POST'


class UpdateGlobalNoticeRule(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_type_uuid}/notice_rule/{notice_rule_uuid}/update'
    name = '配置中心更新工作项提醒列表'
    api_type = 'POST'


class DelGlobalNoticeRule(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_type_uuid}/notice_rule/{notice_rule_uuid}/delete'
    name = '配置中心删除工作项提醒列表'
    api_type = 'POST'


class AddNoticeRules(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_type_uuid}/notice_rules/add'
    name = '新增工作项提醒'
    api_type = 'POST'


class DelNoticeRules(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_type_uuid}/notice_rule/{notice_rule_uuid}/delete'
    name = '删除工作项提醒'
    api_type = 'POST'


class UpdateNoticeRules(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_type_uuid}/notice_rule/{notice_rule_uuid}/update'
    name = 'update工作项提醒'
    api_type = 'POST'


class GetNoticeRules(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_type_uuid}/notice_rules'
    name = '获取项目内工作项提醒'
    api_type = 'GET'


class GetNoticeConfig(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_type_uuid}/notice_configs'
    name = '获取配置中心工作项通知列表'
    api_type = 'GET'


class AddSubScription(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_type_uuid}/notice_config/{notice_config_uuid}/add_subscription'
    name = '添加工作项通知成员域'
    api_type = 'POST'


class DelSubScription(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_type_uuid}/notice_config/{notice_config_uuid}/delete_subscription'
    name = '删除工作项通知成员域'
    api_type = 'POST'


class UpdateNoticeMethods(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_type_uuid}/notice_config/{notice_config_uuid}/update_methods'
    name = '更新通知方式'
    api_type = 'POST'


class UpdateAllNoticeMethods(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_type_uuid}/notice_configs/update_methods'
    name = '更新通知方式'
    api_type = 'POST'


class ImportantFieldUpdate(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_type_uuid}/important_fields/update'
    name = '关键属性排序'
    api_type = 'POST'


class PostActionUpdate(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_type_uuid}/transition/{transition_uuid}/update'
    name = '添加后置动作&步骤更新'
    api_type = 'POST'


class DelIssuePermission(ProjectOps):
    uri = '/team/{team_uuid}/permission_rule/{permission_rule_uuid}/delete'
    name = '删除工作项权限域'
    api_type = 'POST'


class CreateIssueType(ProjectOps):
    uri = '/team/{team_uuid}/issue_types/add'
    name = '全局配置-添加工作项类型'
    api_type = 'POST'


class DeleteIssueType(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_type_uuid}/delete'
    name = '全局配置-删除工作项类型'
    api_type = 'POST'


class GlobalPostActionUpdate(ProjectOps):
    uri = '/team/{team_uuid}/issue_type/{issue_type_uuid}/transition/{transition_uuid}/update'
    name = '配置中心-工作项工作流-后置动作'
    api_type = 'POST'
