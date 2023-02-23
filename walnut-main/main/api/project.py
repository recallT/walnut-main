#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：pro.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/11/18 
@Desc    ：项目api定义


"""
from falcons.ops import ProjectOps


# ------------------------------------------------------------------------------------


class LoginAuth(ProjectOps):
    """登录接口"""
    uri = '/auth/login'
    name = '认证登录'
    api_type = 'POST'


class TokenInfo(ProjectOps):
    """获取token信息"""
    uri = '/auth/token_info'
    name = '获取token信息'
    api_type = 'GET'


class AuthInviteJoin(ProjectOps):
    """加入团队"""
    uri = '/auth/invite_join_team'
    name = '加入团队'
    api_type = 'POST'


class ResetPasswdLink(ProjectOps):
    """重置密码链接"""
    uri = '/team/{team_uuid}/user/{member_uuid}/reset_password_link'
    name = '重置密码链接'
    api_type = 'GET'


class DeleteMember(ProjectOps):
    """删除成员"""
    uri = '/team/{team_uuid}/delete_member'
    name = '删除成员'
    api_type = 'POST'


class DeleteMembersBatch(ProjectOps):
    """批量删除成员"""
    uri = '/team/{team_uuid}/delete_members'
    name = '批量删除成员'
    api_type = 'POST'


class ResetPasswdMail(ProjectOps):
    """重置密码连接邮箱"""
    uri = '/team/{team_uuid}/user/{member_uuid}/reset_password_email'
    name = '重置密码邮箱'
    api_type = 'GET'


class InvitationsAdd(ProjectOps):
    """邀请成员"""
    uri = '/team/{team_uuid}/invitations/add_batch'
    name = '邀请成员'
    api_type = 'POST'


class InvitationsHistory(ProjectOps):
    """邀请成员记录"""
    uri = '/team/{team_uuid}/invitations'
    name = '邀请成员记录'
    api_type = 'GET'


class TeamView(ProjectOps):
    uri = '/team/{team_uuid}/items/view'
    name = '查看团队信息'
    api_type = 'POST'


class TeamInfo(ProjectOps):
    uri = '/team/{team_uuid}/info'
    name = '团队信息'
    api_type = 'GET'


class TeamUpdate(ProjectOps):
    uri = '/team/{team_uuid}/update_info'
    name = '更新队信息'
    api_type = 'POST'


class TeamStampData(ProjectOps):
    uri = '/team/{team_uuid}/stamps/data'
    name = 'StampsData'
    api_type = 'POST'


class TeamEvalPermissions(ProjectOps):
    """团队赋权信息"""
    uri = '/team/{team_uuid}/filter_evaluated_permissions'
    name = '团队赋权信息'
    api_type = 'POST'


class CheckEmail(ProjectOps):
    """邮箱验证"""
    uri = '/auth/check_email'
    name = '邮箱验证'
    api_type = 'POST'


class PermissionAdd(ProjectOps):
    """权限添加"""
    uri = '/team/{team_uuid}/permission_rules/add'
    name = '权限添加'
    api_type = 'POST'


class PermissionDelete(ProjectOps):
    """权限删除"""
    uri = '/team/{team_uuid}/permission_rule/{rule_uuid}/delete'
    name = '权限删除'
    api_type = 'POST'


class PermissionRules(ProjectOps):
    """权限规则配置"""
    uri = '/team/{team_uuid}/context_permission_rules'
    name = '权限规则配置'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
class TeamConfigsUpdate(ProjectOps):
    """团队配置更新"""
    uri = '/team/{team_uuid}/configs/update'
    name = '团队配置更新'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
class UsersCurrentTeam(ProjectOps):
    """获取用户当前团队"""
    uri = '/users/current_team'
    name = '获取用户当前团队'
    api_type = 'GET'


class UsersUpdate(ProjectOps):
    """修改团队成员信息"""
    uri = '/users/update'
    name = '修改团队成员信息'
    api_type = 'POST'


class UsersMe(ProjectOps):
    """获取当前用户信息"""
    uri = '/users/me'
    name = '获取当前用户信息'
    api_type = 'GET'


class DisableMembers(ProjectOps):
    """禁用成员"""
    uri = '/organization/{org_uuid}/disable_members'
    name = '禁用成员'
    api_type = 'POST'


class UsersReqCode(ProjectOps):
    """发送验证码"""
    uri = '/users/request_code'
    name = '获取当前用户信息'
    api_type = 'POST'


class UsersVerifyPasswd(ProjectOps):
    """验证密码"""
    uri = '/users/verify_password'
    name = '验证密码'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

class UsesGroupList(ProjectOps):
    """获取用户组列表"""
    uri = '/team/{team_uuid}/usergroups'
    name = '获取用户组列表'
    api_type = 'GET'


class UsesGroupAdd(ProjectOps):
    """创建用户组"""
    uri = '/team/{team_uuid}/usergroups/add'
    name = '创建用户组'
    api_type = 'POST'


class UsesGroupUpdate(ProjectOps):
    """更新用户组"""
    uri = '/team/{team_uuid}/usergroup/{group_uuid}/update'
    name = '更新用户组'
    api_type = 'POST'


class UsesGroupDelete(ProjectOps):
    """删除用户组"""
    uri = '/team/{team_uuid}/usergroup/{group_uuid}/delete'
    name = '删除用户组'
    api_type = 'POST'


class UsesSearch(ProjectOps):
    """搜索用户"""
    uri = '/team/{team_uuid}/users/search'
    # /team/XqWswpUJ/users/search?e=true
    name = '搜索用户'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

class TeamSearch(ProjectOps):
    """团队搜索"""
    uri = '/team/{team_uuid}/search'
    name = '团队搜索'
    api_type = 'GET'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------


class AddProject(ProjectOps):
    """添加项目"""
    uri = '/team/{team_uuid}/projects/add'
    name = '添加项目'
    api_type = 'POST'


class CopyProject(ProjectOps):
    """拷贝项目"""
    uri = '/team/{team_uuid}/projects/copy2'
    name = '拷贝项目'
    api_type = 'POST'


class MyProject(ProjectOps):
    """获取当前用户项目列表"""
    uri = '/team/{team_uuid}/projects/my_project'
    name = '获取当前用户项目列表'
    api_type = 'GET'


class DeleteProject(ProjectOps):
    """删除项目"""
    uri = '/team/{team_uuid}/project/{project_uuid}/delete'
    name = '删除项目'
    api_type = 'POST'


class ProjectComponent(ProjectOps):
    uri = '/team/{team_uuid}/container/project_manage/project_list/projects_component'
    name = '项目组件'
    api_type = 'GET'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------


class VersionAdd(ProjectOps):
    """添加版本"""
    uri = '/team/{team_uuid}/versions/add'
    name = '添加版本'
    api_type = 'POST'


class VersionList(ProjectOps):
    """获取版本列表"""
    uri = '/team/{team_uuid}/versions'
    name = '获取版本列表'
    api_type = 'GET'


class VersionUpdate(ProjectOps):
    """更新版本信息"""
    uri = '/team/{team_uuid}/version/{version_uuid}/update'
    name = '更新版本信息'
    api_type = 'POST'


class VersionDelete(ProjectOps):
    """删除版本信息"""
    uri = '/team/{team_uuid}/version/{version_uuid}/delete'
    name = '删除版本信息'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

class RolesAdd(ProjectOps):
    """添加角色"""
    uri = '/team/{team_uuid}/roles/add'
    name = '添加角色'
    api_type = 'POST'


class RoleUpdate(ProjectOps):
    """更新角色"""
    uri = '/team/{team_uuid}/role/{role_uuid}/update'
    name = '更新角色'
    api_type = 'POST'


class RoleDelete(ProjectOps):
    """删除角色"""
    uri = '/team/{team_uuid}/role/{role_uuid}/delete'
    name = '删除角色'
    api_type = 'POST'


class ProjectRoleAdd(ProjectOps):
    """项目添加角色"""
    uri = '/team/{team_uuid}/project/{project_uuid}/roles/add'
    name = '项目添加角色'
    api_type = 'POST'


class ProjectRoleDelete(ProjectOps):
    """项目移除角色"""
    uri = '/team/{team_uuid}/project/{project_uuid}/role/{role_uuid}/delete'
    name = '项目移除角色'
    api_type = 'POST'


class ProjectRoleMembers(ProjectOps):
    """项目角色列表"""
    uri = '/team/{team_uuid}/project/{project_uuid}/role_members'
    name = '项目角色列表'
    api_type = 'GET'


class ProjAddMembers(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/role/{role_uuid}/members/update'
    name = '项目内新增成员'
    api_type = 'POST'


class ProjDelMembers(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/role/{role_uuid}/members/delete'
    name = '项目内删除成员'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

class ItemsAdd(ProjectOps):
    """添加Item"""
    uri = '/team/{team_uuid}/items/add'
    name = '添加Item'
    api_type = 'POST'


class ItemsView(ProjectOps):
    """查看Item"""
    uri = '/team/{team_uuid}/items/view'
    name = '查看Item'
    api_type = 'POST'


class ItemUpdate(ProjectOps):
    """更新Item"""
    uri = '/team/{team_uuid}/item/{item_key}/update'
    name = '更新Item'
    api_type = 'POST'


class ItemDelete(ProjectOps):
    """删除Item"""
    uri = '/team/{team_uuid}/item/{item_key}/delete'
    name = '删除Item'
    api_type = 'POST'


class ItemsBatchDelete(ProjectOps):
    """批量删除Items"""
    uri = '/team/{team_uuid}/items/batch_delete'
    name = '批量删除Items'
    api_type = 'POST'


class ItemBatchAdd(ProjectOps):
    """批量添加Item"""
    uri = '/team/{team_uuid}/items/batch_add'
    name = '批量添加Item'
    api_type = 'POST'


class ItemGraphql(ProjectOps):
    """Item Graphql查询"""
    uri = '/team/{team_uuid}/items/graphql'
    name = 'Item Graphql查询'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
class GanttSync(ProjectOps):
    """甘特图同步"""
    uri = '/team/{team_uuid}/gantt_chart/{gantt_uuid}/sync'
    name = '甘特图同步'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

class FieldsAdd(ProjectOps):
    """全局属性-新增"""
    uri = '/team/{team_uuid}/fields/add'
    name = '全局属性-新增'
    api_type = 'POST'


class FieldUpdate(ProjectOps):
    """全局属性-更新"""
    uri = '/team/{team_uuid}/field/{field_uuid}/update'
    name = '全局属性-更新'
    api_type = 'POST'


class FieldDelete(ProjectOps):
    """全局属性-删除"""
    uri = '/team/{team_uuid}/field/{field_uuid}/delete'
    name = '全局属性-删除'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

class Notice(ProjectOps):
    """消息通知"""
    uri = '/team/{team_uuid}/notices?type=1&limit=200'
    name = '消息通知'
    api_type = 'GET'


class NoticeUpdate(ProjectOps):
    """更新通知"""
    uri = '/team/{team_uuid}/notice/update'
    name = '更新通知'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

class QueuesList(ProjectOps):
    """消息列表"""
    uri = '/team/{team_uuid}/queues/list'
    name = '消息列表'
    api_type = 'GET'


class HiddenProgress(ProjectOps):
    """关闭消息"""
    uri = '/team/{team_uuid}/queues/hidden_progress'
    name = '关闭消息'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------


class DashboardCardAdd(ProjectOps):
    """创建卡片"""
    uri = '/team/{team_uuid}/dashboard/{dashboard_uuid}/cards/add'
    name = '创建卡片'
    api_type = 'POST'


class DashboardCardLayout(ProjectOps):
    """卡片视图"""
    uri = '/team/{team_uuid}/dashboard/{dashboard_uuid}/cards/layout'
    name = '卡片视图'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------


class DevopsAdd(ItemsAdd):
    """"""
    name = '添加Jenkins'


class DevopsSync(ItemGraphql):
    """"""
    name = '同步Jenkins'


class DevopsDelete(ProjectOps):
    uri = '/team/{team_uuid}/item/devops_ci_sync-{devops_uuid}/delete'
    name = '删除Jenkins'
    api_type = 'POST'


class DevopsUpdate(ProjectOps):
    uri = '/team/{team_uuid}/item/devops_ci_sync-{devops_uuid}/update'
    name = '更新Jenkins'
    api_type = 'POST'


class PipePin(ProjectOps):
    uri = '/team/{team_uuid}/devops/pipeline/{pipeline_uuid}/pin'
    name = '置顶Pipeline'
    api_type = 'POST'


class PipeUnPin(ProjectOps):
    uri = '/team/{team_uuid}/devops/pipeline/{pipeline_uuid}/unpin'
    name = '取消置顶Pipeline'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

class ComponentsAdd(ProjectOps):
    """项目添加组件"""
    uri = '/team/{team_uuid}/project/{project_uuid}/components/add'
    name = '项目添加组件'
    api_type = 'POST'


class UpdateComponents(ProjectOps):
    """项目更新组件"""
    uri = '/team/{team_uuid}/project/{project_uuid}/components/update'
    name = '项目更新组件'
    api_type = 'POST'


class ComponentSort(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/components/sort'
    name = '项目组件排序'
    api_type = 'POST'


class ComponentUpdate(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/component/{component_uuid}/update'
    name = '项目组件更新'
    api_type = 'POST'


class ComponentDelete(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/components/delete/{comp_uuid}'
    name = '项目删除组件'
    api_type = 'POST'


class ProjectStamp(ProjectOps):
    """项目标记数据"""
    uri = '/team/{team_uuid}/project/{project_uuid}/stamps/data'
    name = '项目标记数据'
    api_type = 'POST'


class PrjExternalActivities(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/activities/{activity_uuid}/external_activities'
    name = '项目外部活动'
    api_type = 'POST'


class ExportProjectPlan(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/project_plan/export'
    name = '导出项目计划'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

class ProjectIssueFieldAdd(ProjectOps):
    """项目添加工作项属性"""
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_uuid}/fields/add'
    name = '项目添加工作项属性'
    api_type = 'POST'


class ProjectIssueFieldDelete(ProjectOps):
    """项目删除工作项属性"""
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_uuid}/field/{field_uuid}/delete'
    name = '项目删除工作项属性'
    api_type = 'POST'


class ProjectIssueFieldUpdate(ProjectOps):
    """项目更新工作项属性"""
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_uuid}/field/{field_uuid}/update'
    name = '项目更新工作项属性'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------


class ProStepPropertiesUpdate(ProjectOps):
    """process_uuid： 添加属性步骤流转过程的uuid"""
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_type_uuid}/transition/{process_uuid}/update'
    name = '属性步骤变更'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# deploy 发布


class GetDeployStatus(ProjectOps):
    """"""
    uri = '/team/{team_uuid}/task/{tasks_uuid}/transitions'
    name = '发布状态步骤获取'
    api_type = 'GET'


class DeployUpdateStatusPublish(ProjectOps):
    uri = '/team/{team_uuid}/task/{tasks_uuid}/commit_publish_version'
    name = '发布状态更新为已发布'
    api_type = "POST"


class UpdateTransitStatus(ProjectOps):
    uri = '/team/{team_uuid}/task/{tasks_uuid}/new_transit'
    name = '修改任务状态'
    api_type = "POST"


class DeleteIsuTask(ProjectOps):
    uri = '/team/{team_uuid}/task/{tasks_uuid}/delete'
    name = '项目内删除组件任务'
    api_type = "POST"


class DeploySetTask(ProjectOps):
    uri = '/team/{team_uuid}/task/{tasks_uuid}/batch_set_publish_version'
    name = '规划至发布'
    api_type = 'POST'


class DeployInfo(ProjectOps):
    uri = '/team/{team_uuid}/task/{tasks_uuid}/info'
    name = '发布关联信息'
    api_type = 'GET'


class GlobalStepPropertiesUpdate(ProjectOps):
    """全局配置工作项属性步骤变更"""
    uri = '/team/{team_uuid}/issue_type/{issue_type_uuid}/transition/{process_uuid}/update'
    name = '全局配置添加工作项属性步骤变更'
    api_type = 'POST'


class LinkRelatedTask(ProjectOps):
    """关联工作项"""
    uri = '/team/{team_uuid}/task/{tasks_uuid}/related_tasks'
    name = '关联工作项'
    api_type = 'POST'


class DeleteLinkRelatedTask(ProjectOps):
    """移除关联工作项"""
    uri = '/team/{team_uuid}/task/{tasks_uuid}/delete/related_tasks'
    name = '移除关联工作项'
    api_type = 'POST'


# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
class RelationDocument(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/component/{component_uuid}/related_wiki_pages/update'
    name = '文档组件关联WIKI'
    api_type = 'POST'


class RelatedWikiPagesInfo(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/component/{component_uuid}/related_wiki_pages'
    name = '文档管理wiki页面信息查询'
    api_type = 'GET'


class ExportProjReport(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/reports/export'
    name = '项目内导出报表'
    api_type = 'POST'


class WordFlowUpdate(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_type}/task_status/{task_status}/update'
    name = '更新工作项工作流状态'
    api_type = 'POST'


class AddTaskField(ProjectOps):
    uri = '/team/{team_uuid}/do_setting/task_field/batch_apply'
    name = '添加属性到工作项'
    api_type = 'POST'


class UpdateProject(ProjectOps):
    uri = '/team/{team_uuid}/item/project-{project_uuid}/update'
    name = '项目修改'
    api_type = 'POST'


class LocalFieldConfig(ProjectOps):
    uri = '/team/{team_uuid}/issue_type_scope/{issue_type_scope}/local_field_configs2'
    name = '获取工作项视图属性'
    api_type = 'GET'


class GetAllProject(ProjectOps):
    uri = '/team/{team_uuid}/stamps/data?t=project,all_project'
    name = '获取所有项目'
    api_type = 'POST'


class AddIssueType(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_types/add'
    name = '项目设置-添加工作项类型'
    api_type = 'POST'


class DeleteIssueType(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/issue_type/{issue_type_uuid}/delete'
    name = '项目设置-删除工作项类型'
    api_type = 'POST'


# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
class PinProject(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/pin'
    name = '项目置顶'
    api_type = 'POST'


class UnpinProject(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/unpin'
    name = '取消项目置顶'
    api_type = 'POST'
