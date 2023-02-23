"""
@Desc: 项目设置-子任务-工作项权限
"""

import time

from falcons.com.nick import feature, fixture, mark, story, step
from main.actions.member import MemberAction
from main.helper.extra import Extra
from main.actions.task import TaskAction
from falcons.com.meta import ApiMeta
from main.actions.issue import IssueAction as iis
from falcons.check import Checker, go
from main.params import data, proj, conf
from main.api import project, third, issue
from main.params.third import add_sub_department


@fixture(scope='module', autouse=True)
def permission_data():
    # 创建一个单独项目
    time.sleep(2)
    creator = Extra(ApiMeta)
    p_id = creator.new_project(f'子任务工作项权限-测试')
    issue_type_uuid = TaskAction.issue_type_uuid('子任务', project_uuid=p_id)[0]
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
    resp = iis.get_pro_permission_rules('子任务', project_uuid=permission_data['p_id'])
    return resp


label = ApiMeta.env.label


@mark.skipif(label == 'private' or label == 'dev', reason='环境跳过权限用例')
@feature('项目设置-子任务-工作项权限')
class TestSubTaskPermission(Checker):
    @classmethod
    def get_issue_permission_uuid(cls, resp, permission_type):
        """获取权限成员域的列表"""
        uuid_list = [r['uuid'] for r in resp.value('permission_rules') if
                     r['permission'] == permission_type]
        return uuid_list

    @classmethod
    def del_update_task_field(cls, issue_type_uuid1, project_uuid, uuid):
        """对 任务工作项权限的 一些成员域进行清除操作"""
        issue_type_uuid = TaskAction.issue_type_uuid('子任务', uuid_type='uuid'
                                                     , project_uuid=project_uuid)[0]
        param_g = proj.get_task_permission_list(issue_type_uuid)[0]
        resp = go(project.ItemGraphql, param_g)

        constraint_uuids = [r['issueTypeScopeFieldConstraints'][0]['uuid'] for r in resp.value('data.buckets') if
                            r['fieldUUID'] == uuid]
        with step('项目管理员删除任务 权限域 的第一个 '):
            if len(constraint_uuids) != 0:
                param = conf.proj_constraints_del(constraint_uuids)[0]
                param.uri_args(
                    {'issue_type_uuid': issue_type_uuid1, 'project_uuid': project_uuid})
                resp_del = go(issue.ProjConstraintsDelete, param)
                resp_del.check_response('code', 200)
        return issue_type_uuid

    @story("T142089 子任务-工作项权限：编辑截止日期权限（部门）")
    @story("T142096 子任务-工作项权限：编辑截止日期权限（用户组）")
    def test_sub_task_permission_edit_date_depart(self, get_pro_permission, permission_data):
        issue_type_uuid1 = permission_data['issue_type_uuid']
        project_uuid = permission_data['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid, 'field013')
        with step('成员A点击编辑任务A的日期属性'):
            ...
            # todo
        with step('项目管理员将任务的「编辑截止日期」权限域添加 用户组'):
            # 新增用户组
            param = data.user_group_add()[0]
            resp = self.call(project.UsesGroupAdd, param)
            group_uuid = resp.value('uuid')

            param = proj.add_task_permission(issue_type_uuid, 'field013')[0]
            param.json_update('items[0].user_domain_param', group_uuid)
            param.json_update('items[0].user_domain_type', 'group')
            self.call(project.ItemBatchAdd, param)

        with step('项目管理员将任务的「编辑截止日期」权限域添加 部门'):
            # 新增部门
            param = add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)
            depart_uuid = resp.json()['add_department']['uuid']

            param = proj.add_task_permission(issue_type_uuid, 'field013')[0]
            param.json_update('items[0].user_domain_param', depart_uuid)
            param.json_update('items[0].user_domain_type', 'department')
            self.call(project.ItemBatchAdd, param)

        with step('清除用户组、部门数据'):
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param, with_json=False)
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story("T142095 子任务-工作项权限：编辑截止日期权限（项目角色）")
    def test_sub_task_permission_edit_date_role(self, get_pro_permission, permission_data):
        issue_type_uuid1 = permission_data['issue_type_uuid']
        project_uuid = permission_data['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid, 'field013')
        with step('成员A点击编辑任务A的日期属性'):
            ...
            # todo
        with step('项目管理员将任务的「编辑截止日期」权限域添加 「项目角色」'):
            # 新增 项目角色
            role_uuid = MemberAction.add_member_role().value('role.uuid')

            param = proj.add_task_permission(issue_type_uuid, 'field013')[0]
            param.json_update('items[0].user_domain_param', role_uuid)
            param.json_update('items[0].user_domain_type', 'role')
            self.call(project.ItemBatchAdd, param)
        with step('删除角色'):
            MemberAction.del_member_role(role_uuid)

    @story("T142094 子任务-工作项权限：编辑截止日期权限（项目负责人）")
    def test_sub_task_permission_edit_date_project_assign(self, get_pro_permission, permission_data):
        issue_type_uuid1 = permission_data['issue_type_uuid']
        project_uuid = permission_data['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid, 'field013')
        with step('成员A点击编辑任务A的日期属性'):
            ...
            # todo
        with step('项目管理员将任务的「编辑截止日期」权限域添加 「项目负责人」'):
            param = proj.add_task_permission(issue_type_uuid, 'field013')[0]
            param.json_update('items[0].user_domain_param', '')
            param.json_update('items[0].user_domain_type', 'project_assign')
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

    @story("T142093 子任务-工作项权限：编辑截止日期权限（工作项关注者）")
    def test_sub_task_permission_edit_date_task_watchers(self, get_pro_permission, permission_data):
        issue_type_uuid1 = permission_data['issue_type_uuid']
        project_uuid = permission_data['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid, 'field013')
        with step('成员A点击编辑任务A的日期属性'):
            ...
            # todo
        with step('项目管理员将任务的「编辑截止日期」权限域添加 「工作项关注者」'):
            param = proj.add_task_permission(issue_type_uuid, 'field013')[0]
            param.json_update('items[0].user_domain_param', '')
            param.json_update('items[0].user_domain_type', 'task_watchers')
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

    @story("T142092 子任务-工作项权限：编辑截止日期权限（工作项负责人）")
    def test_sub_task_permission_edit_date_task_assign(self, get_pro_permission, permission_data):
        issue_type_uuid1 = permission_data['issue_type_uuid']
        project_uuid = permission_data['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid, 'field013')
        with step('成员A点击编辑任务A的日期属性'):
            ...
            # todo
        with step('项目管理员将任务的「编辑截止日期」权限域添加 「工作项负责人」'):
            param = proj.add_task_permission(issue_type_uuid, 'field013')[0]
            param.json_update('items[0].user_domain_param', '')
            param.json_update('items[0].user_domain_type', 'task_assign')
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

    @story("T142091 子任务-工作项权限：编辑截止日期权限（工作项创建者）")
    def test_sub_task_permission_edit_date_task_owner(self, get_pro_permission, permission_data):
        issue_type_uuid1 = permission_data['issue_type_uuid']
        project_uuid = permission_data['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid, 'field013')
        with step('成员A点击编辑任务A的日期属性'):
            ...
            # todo
        with step('项目管理员将任务的「编辑截止日期」权限域添加 「工作项创建者」'):
            param = proj.add_task_permission(issue_type_uuid, 'field013')[0]
            param.json_update('items[0].user_domain_param', '')
            param.json_update('items[0].user_domain_type', 'task_owner')
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

    @story("T142109 子任务-工作项权限：编辑子任务权限（用户组）")
    def test_sub_task_permission_edit_group(self, get_pro_permission, permission_data):
        permission = 'update_tasks'
        with step('项目管理员清空任务的「编辑子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A的属性'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑子任务」权限域添加「用户组」'):
            # 新增用户组
            param1 = data.user_group_add()[0]
            resp = self.call(project.UsesGroupAdd, param1)
            group_uuid = resp.value('uuid')
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': group_uuid,
                          'user_domain_type': 'group'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('清除 用户组数据'):
            param1.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param1, with_json=False)

    @story("T142108 子任务-工作项权限：编辑子任务权限（项目角色）")
    def test_sub_task_permission_edit_role(self, get_pro_permission, permission_data):
        permission = 'update_tasks'
        with step("删除权限域"):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step("成员A编辑子任务A的属性"):
            ...
            # todo:
        with step("「编辑子任务」的权限域添加「项目角色」"):
            # 新增角色
            role_uuid = MemberAction.add_member_role().value('role.uuid')
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': role_uuid,
                          'user_domain_type': 'role'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step("删除角色"):
            MemberAction.del_member_role(role_uuid)

    @story("T142102 子任务-工作项权限：编辑子任务权限（部门）")
    def test_sub_task_permission_edit_depart(self, get_pro_permission, permission_data):
        permission = 'update_tasks'
        with step("删除权限域"):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step("成员A编辑子任务A的属性"):
            ...
            # todo:
        with step("「编辑子任务」的权限域添加「部门」"):
            # 新增部门
            param1 = add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param1)
            depart_uuid = resp.json()['add_department']['uuid']
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': depart_uuid,
                          'user_domain_type': 'department'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step("删除 部门"):
            param1.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param1, with_json=False)

    @story("T142104 子任务-工作项权限：编辑子任务权限（工作项创建者）")
    def test_sub_permission_edit_task_owner(self, get_pro_permission, permission_data):
        permission = 'update_tasks'
        with step('项目管理员清空任务的「编辑任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑子任务」权限域添加工作项创建者'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_owner'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T142068 子任务-工作项权限：编辑关注者权限（项目负责人）")
    def test_issue_permission_edit_task_proj_assign(self, get_pro_permission, permission_data):
        permission = 'update_task_watchers'
        with step('项目管理员清空子任务的「编辑关注者」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将子任务的「编辑关注者」权限域添加「项目负责人」'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'project_assign'}  # 项目负责人
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T142105 子任务-工作项权限：编辑子任务权限（工作项负责人）")
    def test_sub_task_permission_edit_task_assign(self, get_pro_permission, permission_data):
        permission = 'update_tasks'
        with step('项目管理员清空任务的「编辑子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A的属性'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑任务」权限域添加「工作项负责人」'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T142106 子任务-工作项权限：编辑子任务权限（工作项关注者）")
    def test_sub_task_permission_edit_task_watchers(self, get_pro_permission, permission_data):
        permission = 'update_tasks'
        with step('项目管理员清空任务的「编辑子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A的属性'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑任务」权限域添加「工作项关注者」'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_watchers'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T142107 子任务-工作项权限：编辑子任务权限（项目负责人）")
    def test_sub_task_permission_edit_project_assign(self, get_pro_permission, permission_data):
        permission = 'update_tasks'
        with step('项目管理员清空任务的「编辑子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A的属性'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑任务」权限域添加「项目负责人」'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T142115 子任务-工作项权限：查看子任务权限（部门）")
    def test_sub_task_permission_watch_depart(self, get_pro_permission, permission_data):
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step("「查看子任务」的权限域 添加「部门」"):
            # 新增部门
            param = add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)
            depart_uuid = resp.json()['add_department']['uuid']

            param_dict ={'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                         'user_domain_param': depart_uuid,
                         'user_domain_type': 'department'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step("删除 部门"):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story("T142121 子任务-工作项权限：查看子任务权限（项目角色）")
    def test_sub_task_permission_watch_role(self, get_pro_permission, permission_data):
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step("成员A查看子任务A"):
            ...
            # todo:
        with step("「查看子任务」的权限域 添加 「项目角色」"):
            # 新增角色
            role_uuid = MemberAction.add_member_role().value('role.uuid')

            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': role_uuid,
                          'user_domain_type': 'role'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step("删除 角色"):
            MemberAction.del_member_role(role_uuid)

    @story("T142122 子任务-工作项权限：查看子任务权限（用户组）")
    def test_sub_task_permission_watch_group(self, get_pro_permission, permission_data):
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step("成员A查看子任务A"):
            ...
            # todo:
        with step("「查看子任务」的权限域 添加 「用户组」"):
            # 新增 用户组
            param = data.user_group_add()[0]
            resp = self.call(project.UsesGroupAdd, param)
            group_uuid = resp.value('uuid')

            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param':group_uuid,
                          'user_domain_type': 'group'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step("删除 用户组"):
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param)

    @story("T142120 子任务-工作项权限：查看子任务权限（项目负责人）")
    def test_sub_task_permission_watch_project_assign(self, get_pro_permission, permission_data):
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step("成员A查看子任务A"):
            ...
            # todo:
        with step("「查看子任务」的权限域 添加 「项目负责人」"):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T142119 子任务-工作项权限：查看子任务权限（工作项关注者）")
    def test_sub_task_permission_watch_task_watchers(self, get_pro_permission, permission_data):
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step("成员A查看子任务A"):
            ...
            # todo:
        with step("「查看子任务」的权限域 添加 「工作项关注者」"):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_watchers'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T142117 子任务-工作项权限：查看子任务权限（工作项创建者）")
    def test_sub_task_permission_watch_task_owner(self, get_pro_permission, permission_data):
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step("成员A查看子任务A"):
            ...
            # todo:
        with step("「查看子任务」的权限域 添加 「工作项创建者」"):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_owner'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T142118 子任务-工作项权限：查看子任务权限（工作项负责人）")
    def test_sub_task_permission_watch_task_assign(self, get_pro_permission, permission_data):
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step("成员A查看子任务A"):
            ...
            # todo:
        with step("「查看子任务」的权限域 添加 「工作项负责人」"):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T142231 子任务-工作项权限：删除子任务权限（部门）")
    def test_sub_task_permission_del_task_depart(self, get_pro_permission, permission_data):
        permission = 'delete_tasks'
        with step('项目管理员清空任务的「删除子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step("「删除子任务」的权限域 添加「部门」"):
            # 新增部门
            param = add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)
            depart_uuid = resp.json()['add_department']['uuid']

            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': depart_uuid,
                          'user_domain_type': 'department'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step("删除 部门"):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story("T142132 子任务-工作项权限：成为负责人权限（用户组）")
    def test_sub_task_permission_be_assign_group(self, get_pro_permission, permission_data):
        permission = 'be_assigned'
        with step('项目管理员清空任务的「成为负责人」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step("成员A创建子任务的工作项"):
            ...
            # todo:
        with step("「成为负责人」的权限域 添加 「用户组」"):
            # 新增 用户组
            param = data.user_group_add()[0]
            resp = self.call(project.UsesGroupAdd, param)
            group_uuid = resp.value('uuid')

            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param':group_uuid,
                          'user_domain_type': 'group'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step("删除 用户组"):
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param)

    @story("T142128 子任务-工作项权限：成为负责人权限（部门）")
    def test_sub_task_permission_be_assign_depart(self, get_pro_permission, permission_data):
        permission = 'be_assigned'
        with step('项目管理员清空任务的「成为负责人」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step("「成为负责人」的权限域 添加「部门」"):
            # 新增部门
            param = add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)
            depart_uuid = resp.json()['add_department']['uuid']

            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': depart_uuid,
                          'user_domain_type': 'department'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step("删除 部门"):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story("T142218 子任务-工作项权限：管理自己预估工时权限（部门）")
    def test_sub_task_permission_estimate_hour_depart(self, get_pro_permission, permission_data):
        permission = 'manage_task_own_assess_manhour'
        with step('项目管理员清空任务的「成为负责人」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step("「成为负责人」的权限域 添加「部门」"):
            # 新增部门
            param = add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)
            depart_uuid = resp.json()['add_department']['uuid']

            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': depart_uuid,
                          'user_domain_type': 'department'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step("删除 部门"):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story("T142234 子任务-工作项权限：删除子任务权限（工作项负责人）")
    def test_sub_task_permission_del_sub_task_assign(self, get_pro_permission, permission_data):
        permission = 'delete_tasks'
        with step('项目管理员清空任务的「删除子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step("「删除子任务」的权限域 添加「工作项负责人」"):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T142235 子任务-工作项权限：删除子任务权限（工作项关注者）")
    def test_sub_task_permission_del_sub_task_watchers(self, get_pro_permission, permission_data):
        permission = 'delete_tasks'
        with step('项目管理员清空任务的「删除子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step("「删除子任务」的权限域 添加「工作项关注者」"):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_watchers'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
