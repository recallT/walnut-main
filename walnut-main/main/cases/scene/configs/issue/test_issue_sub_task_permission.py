# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_issue_sub_task_permission.py
@Author  ：zhangyonghui@ones.ai
@Date    ：7/21/22 5:17 PM 
@Desc    ：配置中心--子任务-工作项权限
"""
import random

from falcons.check import Checker
from falcons.com.nick import feature, fixture, story, step

from main.actions.member import MemberAction
from main.actions.task import TaskAction
from main.api import issue
from main.cases.scene.configs.issue import IssueConfig
from main.params import conf
from main.params.const import ACCOUNT


@fixture(scope='module', autouse=True)
def get_data():
    issue_type_uuid = TaskAction.issue_type_uuid('子任务')[0]
    member_uuids = ACCOUNT.user.owner_uuid
    data = {'issue_type_uuid': issue_type_uuid, 'member_uuids': member_uuids}
    return data


@feature('全局配置-工作项权限-子任务')
class TestSubTaskIssuePermission(Checker):

    @story('T142100 子任务-工作项权限：编辑子任务权限')
    def test_global_sub_task_permission_update_tasks(self, get_data):
        with step('点击子任务的编辑子任务权限添加成员域，查看可选成员域'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type=get_data['issue_type_uuid'], user_domain_type='single_user', permission='update_tasks',
                user_domain_param=get_data['member_uuids'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(get_data['issue_type_uuid'], rule_uuid)

    @story('T142113 子任务-工作项权限：查看子任务权限')
    def test_global_sub_task_permission_view_tasks(self, get_data):
        with step('点击子任务的查看子任务权限添加成员域，查看可选成员域'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type=get_data['issue_type_uuid'], user_domain_type='single_user', permission='view_tasks',
                user_domain_param=get_data['member_uuids'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(get_data['issue_type_uuid'], rule_uuid)

    @story('T142126 子任务-工作项权限：成为负责人权限')
    def test_global_sub_task_permission_be_assigned(self, get_data):
        with step('添加成员到权限中'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type=get_data['issue_type_uuid'], user_domain_type='single_user', permission='be_assigned',
                user_domain_param=get_data['member_uuids'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(get_data['issue_type_uuid'], rule_uuid)

    @story('T142134 子任务-工作项权限：创建子任务权限')
    def test_global_sub_task_permission_create_tasks(self, get_data):
        with step('添加成员到权限中'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type=get_data['issue_type_uuid'], user_domain_type='single_user', permission='create_tasks',
                user_domain_param=get_data['member_uuids'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(get_data['issue_type_uuid'], rule_uuid)

    @story('T142142 子任务-工作项权限：导出子任务列表权限')
    def test_global_sub_task_permission_export_tasks(self, get_data):
        with step('添加成员到权限中'):
            # 拉一个随机团队成员 避免失败
            member_uuids = MemberAction.get_member_uuid()


            rule_uuid = IssueConfig.issue_permission_add(
                issue_type=get_data['issue_type_uuid'],
                user_domain_type='single_user',
                permission='export_tasks',
                user_domain_param=member_uuids)

        with step('删除成员'):
            IssueConfig.issue_permission_del(get_data['issue_type_uuid'], rule_uuid)

    @story('T142150 子任务-工作项权限：更新子任务状态权限')
    def test_global_sub_task_permission_project_assign(self, get_data):
        with step('添加成员到权限中'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type=get_data['issue_type_uuid'], user_domain_type='single_user', permission='transit_tasks',
                user_domain_param=get_data['member_uuids'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(get_data['issue_type_uuid'], rule_uuid)

    @story('T142163 子任务-工作项权限：管理所有登记工时权限')
    def test_global_sub_task_permission_manage_task_record_manhours(self, get_data):
        with step('添加成员到权限中'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type=get_data['issue_type_uuid'], user_domain_type='single_user',
                permission='manage_task_record_manhours',
                user_domain_param=get_data['member_uuids'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(get_data['issue_type_uuid'], rule_uuid)

    @story('T142176 子任务-工作项权限：管理所有预估工时权限')
    def test_global_sub_task_permission_manage_task_assess_manhour(self, get_data):
        with step('添加成员到权限中'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type=get_data['issue_type_uuid'], user_domain_type='single_user',
                permission='manage_task_assess_manhour',
                user_domain_param=get_data['member_uuids'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(get_data['issue_type_uuid'], rule_uuid)

    @story('T142189 子任务-工作项权限：管理预估工时权限')
    def test_global_sub_task_permission_manage_task_own_assess_manhour(self, get_data):
        with step('添加成员到权限中'):
            # 拉一个随机团队成员 避免失败
            member_uuids = MemberAction.get_member_uuid()


            rule_uuid = IssueConfig.issue_permission_add(
                issue_type=get_data['issue_type_uuid'], user_domain_type='single_user',
                permission='manage_task_own_assess_manhour',
                user_domain_param=member_uuids)

        with step('删除成员'):
            IssueConfig.issue_permission_del(get_data['issue_type_uuid'], rule_uuid)

    @story('T142229 子任务-工作项权限：删除子任务权限')
    def test_global_sub_task_permission_delete_tasks(self, get_data):
        with step('添加成员到权限中'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type=get_data['issue_type_uuid'], user_domain_type='single_user',
                permission='delete_tasks',
                user_domain_param=get_data['member_uuids'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(get_data['issue_type_uuid'], rule_uuid)

    @story('T142061 子任务-工作项权限：编辑关注者权限')
    def test_global_sub_task_permission_update_task_watchers(self, get_data):
        with step('添加成员到权限中'):
            # 拉一个随机团队成员 避免失败
            member_uuids = MemberAction.get_member_uuid()


            rule_uuid = IssueConfig.issue_permission_add(
                issue_type=get_data['issue_type_uuid'], user_domain_type='single_user',
                permission='update_task_watchers',
                user_domain_param=member_uuids)

        with step('删除成员'):
            IssueConfig.issue_permission_del(get_data['issue_type_uuid'], rule_uuid)

    @story('T142203 子任务-工作项权限：管理自己的登记工时权限')
    def test_global_sub_task_permission_manage_task_own_record_manhours(self, get_data):
        with step('添加成员到权限中'):
            # 拉一个随机团队成员 避免失败
            member_uuids = MemberAction.get_member_uuid()

            rule_uuid = IssueConfig.issue_permission_add(
                issue_type=get_data['issue_type_uuid'], user_domain_type='single_user',
                permission='manage_task_own_record_manhours',
                user_domain_param=member_uuids)

        with step('删除成员'):
            IssueConfig.issue_permission_del(get_data['issue_type_uuid'], rule_uuid)

    @story('T142074 子任务-工作项权限：编辑计划开始日期、计划完成日期权限')
    def test_global_sub_task_permission_plan_time(self, get_data):
        param = conf.constraints(get_data['member_uuids'], 'field027-field028')[0]
        param.json_update('constraints[0].user_domain_type', 'single_user')
        param.uri_args({'issue_uuid': get_data['issue_type_uuid']})
        resp = self.call(issue.ConstraintsAdd, param, status_code=[200, 409])

        if resp.response.status_code == 200:
            constraints_uuid = [c['uuid'] for c in resp.value('default_configs.default_constraints') if
                                c['field_uuid'] == 'field027-field028' and c['user_domain_param'] == get_data[
                                    'member_uuids']]
            param_del = conf.constraints_del()[0]
            param_del.json_update('constraint_uuids', constraints_uuid)
            param_del.uri_args({'issue_uuid': get_data['issue_type_uuid']})
            resp_del = self.call(issue.ConstraintsDelete, param_del)
            assert constraints_uuid not in [c['uuid'] for c in resp_del.value('default_configs.default_constraints')]

    @story('T142087 子任务-工作项权限：编辑截止日期权限')
    def test_global_sub_task_permission_expiration_date(self, get_data):
        param = conf.constraints(get_data['member_uuids'], 'field013')[0]
        param.json_update('constraints[0].user_domain_type', 'single_user')
        param.uri_args({'issue_uuid': get_data['issue_type_uuid']})
        resp = self.call(issue.ConstraintsAdd, param, status_code=[200, 409])

        if resp.response.status_code == 200:
            constraints_uuid = [c['uuid'] for c in resp.value('default_configs.default_constraints') if
                                c['field_uuid'] == 'field013' and c['user_domain_param'] == get_data[
                                    'member_uuids']]
            param_del = conf.constraints_del()[0]
            param_del.json_update('constraint_uuids', constraints_uuid)
            param_del.uri_args({'issue_uuid': get_data['issue_type_uuid']})
            resp_del = self.call(issue.ConstraintsDelete, param_del)
            assert constraints_uuid not in [c['uuid'] for c in resp_del.value('default_configs.default_constraints')]
