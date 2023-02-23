# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_issue_permission.py
@Author  ：zhangyonghui@ones.ai
@Date    ：2022/6/24 2:15 PM 
@Desc    ：项目-工作项权限
"""
import time

from falcons.check import Checker
from falcons.com.nick import feature, story, step, fixture, mark
from main.actions.issue import IssueAction as iis
from main.actions.member import MemberAction
from main.actions.task import TaskAction
from main.actions.task import TaskAction as ta
from main.api import third, project, issue
from main.helper.extra import Extra
from main.params import data, proj, conf
from main.params.third import add_sub_department
from falcons.com.meta import ApiMeta


@fixture(scope='module', autouse=True)
def permission_data():
    # 创建一个单独项目
    time.sleep(2)
    creator = Extra(ApiMeta)
    p_id = creator.new_project(f'项目工作项权限test')
    issue_type_uuid = TaskAction.issue_type_uuid('任务', project_uuid=p_id)[0]
    # 获取系统中存在的一个成员uuid
    member_uuid = MemberAction.get_member_uuid()
    data = {'p_id': p_id, 'member_uuid': member_uuid, 'issue_type_uuid': issue_type_uuid}
    return data


@fixture(scope='module', autouse=True)
def _del_project(permission_data):
    yield
    # 清除项目数据
    creator = Extra(ApiMeta)
    creator.del_project(permission_data['p_id'])


@fixture()
def get_pro_permission(permission_data):
    resp = iis.get_pro_permission_rules('任务', project_uuid=permission_data['p_id'])
    return resp


label = ApiMeta.env.label


@mark.skipif(label == 'private' or label == 'dev', reason='环境跳过权限用例')
@feature('工作项权限-任务')
class TestProjPermission(Checker):
    @classmethod
    def get_issue_permission_uuid(cls, resp, permission_type):
        uuid_list = [r['uuid'] for r in resp.value('permission_rules') if
                     r['permission'] == permission_type]
        return uuid_list

    @story('T132894 任务-工作项权限：编辑关注者权限（成员）')
    @story('T152198 新建团队-新建项目：检查新建项目邀请成员不受限')
    def test_issue_permission_update_task_watchers(self, get_pro_permission, permission_data):
        permission = 'update_task_watchers'
        with step('项目管理员清空任务的「编辑关注者」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员添加任务的「编辑关注者」权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T132932 任务-工作项权限：编辑任务权限（部门）')
    def test_issue_permission_update_tasks_department(self, get_pro_permission, permission_data):
        permission = 'update_tasks'
        with step('项目管理员清空任务的「编辑任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的属性-无权限编辑'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑任务」权限域添加部门1'):
            # 新增部门
            param = add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)
            depart_uuid = resp.json()['add_department']['uuid']
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': depart_uuid,
                          'user_domain_type': 'department'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('清除部门数据'):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story('T132933 任务-工作项权限：编辑任务权限（成员）')
    def test_issue_permission_update_tasks_member(self, get_pro_permission, permission_data):
        permission = 'update_tasks'
        with step('项目管理员清空任务的「编辑任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑任务」权限域添加成员A'):

            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T132934 任务-工作项权限：编辑任务权限（工作项创建者）')
    def test_issue_permission_update_tasks_creator(self, get_pro_permission, permission_data):
        permission = 'update_tasks'
        with step('项目管理员清空任务的「编辑任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑任务」权限域添加工作项创建者'):

            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_owner'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T132935 任务-工作项权限：编辑任务权限（工作项负责人）')
    def test_issue_permission_update_tasks_owner(self, get_pro_permission, permission_data):
        permission = 'update_tasks'
        with step('项目管理员清空任务的「编辑任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑任务」权限域添加工作项负责人'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T132935 任务-工作项权限：查看任务权限（工作项负责人）')
    @story('132948 任务-工作项权限：查看任务权限（工作项负责人）')
    def test_issue_permission_view_tasks_owner(self, get_pro_permission, permission_data):
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A查看任务A'):
            ...
            # todo:
        with step('项目管理员将任务的「查看任务」权限域添加工作项负责人'):

            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T132936 任务-工作项权限：编辑任务权限（工作项关注者）')
    def test_issue_permission_update_tasks_task_watchers(self, get_pro_permission, permission_data):
        permission = 'update_tasks'
        with step('项目管理员清空任务的「编辑任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑任务」权限域添加工作项负责人'):

            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_watchers'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T132937 任务-工作项权限：编辑任务权限（项目负责人）')
    def test_issue_permission_update_project_assign(self, get_pro_permission, permission_data):
        permission = 'update_tasks'
        with step('项目管理员清空任务的「编辑任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑任务」权限域添加工作项负责人'):

            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T133071 任务-工作项权限：删除任务权限（项目负责人）')
    def test_issue_permission_delete_project_assign(self, get_pro_permission, permission_data):
        permission = 'delete_tasks'
        with step('项目管理员清空任务的「删除任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A删除任务下的任务A'):
            ...
            # todo:
        with step('项目管理员将任务的「删除任务」权限添加项目负责人'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T132938 任务-工作项权限：编辑任务权限（项目角色）')
    def test_issue_permission_update_task_role(self, get_pro_permission, permission_data):
        # 新增角色
        role_uuid = MemberAction.add_member_role().value('role.uuid')
        permission = 'update_tasks'
        with step('项目管理员清空任务的「编辑任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑任务」权限域添加工作项负责人'):

            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': role_uuid,
                          'user_domain_type': 'role'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

        with step('删除角色'):
            MemberAction.del_member_role(role_uuid)

    @story('T132939 任务-工作项权限：编辑任务权限（用户组）')
    def test_issue_permission_update_task_group(self, get_pro_permission, permission_data):
        # 新增用户组
        param = data.user_group_add()[0]
        resp = self.call(project.UsesGroupAdd, param)
        group_uuid = resp.value('uuid')
        permission = 'update_tasks'
        with step('项目管理员清空任务的「编辑任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑任务」权限域添加用户组1'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': group_uuid,
                          'user_domain_type': 'group'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('清除用户组数据'):
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param, with_json=False)

    @story('T132900 任务-工作项权限：编辑关注者权限（用户组）')
    def test_issue_permission_update_task_watchers_group(self, get_pro_permission, permission_data):
        # 新增用户组
        param = data.user_group_add()[0]
        resp = self.call(project.UsesGroupAdd, param)
        group_uuid = resp.value('uuid')
        permission = 'update_task_watchers'
        with step('项目管理员清空任务的「编辑关注者」工作项状态权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员添加任务的「编辑关注者」权限域为用户组1'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': group_uuid,
                          'user_domain_type': 'group'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('清除用户组数据'):
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param, with_json=False)

    @story('T132940 任务-工作项权限：编辑任务权限（自定义单选成员属性）')
    def test_issue_permission_update_task_group1(self, get_pro_permission, permission_data):
        ...

    @story('T132941 任务-工作项权限：编辑任务权限（自定义多选成员属性）')
    def test_demo1(self):
        ...

    @story('T132946 任务-工作项权限：查看任务权限（成员）')
    def test_issue_permission_view_tasks_member(self, get_pro_permission, permission_data):
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将任务的「查看任务」权限域添加成员A'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T132959 任务-工作项权限：成为负责人权限（成员）')
    def test_issue_permission_be_assigned_member(self, get_pro_permission, permission_data):
        permission = 'be_assigned'
        with step('项目管理员清空任务的「成为负责人」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员添加任务的「成为负责人」权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T132967 任务-工作项权限：创建任务权限（成员）')
    def test_issue_permission_create_tasks_member(self, get_pro_permission, permission_data):
        permission = 'create_tasks'
        with step('项目管理员清空任务的「创建任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将任务的「创建任务」权限域添加为成员A'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T132975 任务-工作项权限：导出任务列表权限（成员）')
    def test_issue_permission_export_tasks_member(self, get_pro_permission, permission_data):
        permission = 'export_tasks'
        with step('项目管理员清空任务的「导出任务」列表权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A导出任务下的工作项'):
            ...
            # todo:
        with step('项目管理员清空任务的「导出任务」列表权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T132983 任务-工作项权限：更新任务状态权限（成员）')
    def test_issue_permission_transit_tasks_member(self, get_pro_permission, permission_data):
        permission = 'transit_tasks'
        with step('项目管理员清空任务的「更新任务状态」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将任务的「更新任务状态」权限域添加成员A'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T132996 任务-工作项权限：管理所有登记工时权限（成员）')
    def test_issue_permission_manage_task_record_manhours(self, get_pro_permission, permission_data):
        permission = 'manage_task_record_manhours'
        with step('项目管理员清空任务的「管理所有登记工时」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A下成员L的登记工时记录'):
            ...
            # todo:
        with step('项目管理员添加任务的「管理所有登记工时」权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T133022 任务-工作项权限：管理预估工时权限（成员）')
    def test_issue_permission_manage_task_assess_manhour(self, get_pro_permission, permission_data):
        permission = 'manage_task_assess_manhour'
        with step('项目管理员清空任务的「管理预估工时」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('登陆成员A编辑任务A预估工时'):
            ...
            # todo:
        with step('项目管理员添加任务的「管理预估工时」权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T133036 任务-工作项权限：管理自己登记工时权限（成员）')
    def test_issue_permission_manage_task_own_record(self, get_pro_permission, permission_data):
        permission = 'manage_task_own_record_manhours'
        with step('项目管理员清空任务的「管理自己登记工时」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A下A的登记工时记录'):
            ...
            # todo:
        with step('项目管理员添加任务的「管理自己登记工时」权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T133067 任务-工作项权限：删除任务权限（成员）')
    def test_issue_permission_delete_tasks(self, get_pro_permission, permission_data):
        permission = 'delete_tasks'
        with step('任务-工作项权限：删除任务权限（成员）'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A删除任务下的任务A'):
            ...
            # todo:
        with step('项目管理员将任务的「删除任务」权限添加成员A'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story('T132907 任务-工作项权限：编辑计划开始日期、计划完成日期权限（成员）')
    def test_issue_permission_update_task_field_field027(self, permission_data):
        issue_type_uuid = ta.issue_type_uuid('任务', uuid_type='uuid'
                                             , project_uuid=permission_data['p_id'])[0]
        param_g = proj.get_task_permission_list(issue_type_uuid)[0]
        resp = self.call(project.ItemGraphql, param_g)
        constraint_uuids = [r['issueTypeScopeFieldConstraints'][0]['uuid'] for r in resp.value('data.buckets') if
                            r['fieldUUID'] == 'field027-field028']
        with step('项目管理员清空任务的「编辑计划开始日期、计划完成日期」权限域 '):
            if len(constraint_uuids) != 0:
                param = conf.proj_constraints_del(constraint_uuids)[0]
                param.uri_args(
                    {'issue_type_uuid': permission_data['issue_type_uuid'], 'project_uuid': permission_data['p_id']})
                resp_del = self.call(issue.ProjConstraintsDelete, param)
                resp_del.check_response('code', 200)
        with step('成员A点击编辑任务A的计划开始日期、计划完成日期属性'):
            ...
            # todo
        with step('项目管理员将任务的「编辑计划开始日期、计划完成日期」权限域添加成员A'):
            param = proj.add_task_permission(issue_type_uuid, 'field027-field028')[0]
            param.json_update('items[0].user_domain_param', permission_data['member_uuid'])
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

    @story('T132907 任务-工作项权限：编辑截止日期权限')
    def test_issue_permission_update_task_field_field013(self, permission_data):
        issue_type_scope_uuid = ta.issue_type_uuid('任务', uuid_type='uuid'
                                                   , project_uuid=permission_data['p_id'])[0]
        param_g = proj.get_task_permission_list(issue_type_scope_uuid)[0]
        resp = self.call(project.ItemGraphql, param_g)
        constraint_uuids = [r['issueTypeScopeFieldConstraints'][0]['uuid'] for r in resp.value('data.buckets') if
                            r['fieldUUID'] == 'field013']
        with step('项目管理员清空任务的「编辑截止日期」权限域'):
            if len(constraint_uuids) != 0:
                param = conf.proj_constraints_del(constraint_uuids)[0]
                param.uri_args(
                    {'issue_type_uuid': permission_data['issue_type_uuid'], 'project_uuid': permission_data['p_id']})
                resp_del = self.call(issue.ProjConstraintsDelete, param)
                resp_del.check_response('code', 200)
        with step('成员A编辑任务A的截止日期属性'):
            ...
            # todo
        with step('项目管理员添加子任务的「编辑截止日期」权限域为成员A'):
            param = proj.add_task_permission(issue_type_scope_uuid, 'field013')[0]
            param.json_update('items[0].user_domain_param', permission_data['member_uuid'])
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

    @story('133063 任务-工作项权限：任务权限域（默认权限域）')
    def test_check_task_default_permission(self):
        """"""

    @story("T133010 任务-工作项权限：管理所有预估工时权限（工作项创建者）")
    def test_issue_permission_manage_assess_hour_task_owner(self, get_pro_permission, permission_data):
        permission = 'manage_task_assess_manhour'
        with step('项目管理员清空任务的「管理所有预估工时」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A下成员L的预估工时记录'):
            ...
            # todo:
        with step('项目管理员将任务的「管理所有预估工时」权限域添加「工作项创建者」'):

            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_owner'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

