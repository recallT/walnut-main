"""
@Desc：项目设置-权限配置-项目权限
"""
from falcons.check import Checker
from falcons.com.nick import feature, story, step, fixture
from main.actions.pro import ProjPermissionAction
from main.actions.task import team_stamp
from main.api import project as prj, third
from main.params import data, third as thr
from main.params.const import ACCOUNT
from . import permission_rules


@fixture(scope='module')
def perm_rule_uuid():
    """权限uuid"""

    return {}


@feature('项目权限')
class TestSprintPermission(Checker):

    @story('119521 迭代权限-成为迭代负责人：检查成为迭代负责人权限默认状态')
    def test_check_sprint_default_permission(self):
        # 获取项目权限规则
        resp = permission_rules()

        with step('查看「成为迭代负责人」权限点的默认成员域'):
            assigned_sprint = [p['user_domain_type'] for p in resp['permission_rules'] if
                               p['permission'] == 'be_assigned_to_sprint']

            assert 'project_administrators', 'role' in assigned_sprint

    @story('119523 迭代权限-成为迭代负责人：添加成员域（成员）')
    def test_sprint_perm_add_single_user(self, perm_rule_uuid):
        rule_uuid = ProjPermissionAction.add_permission('single_user', 'be_assigned_to_sprint',
                                                        ACCOUNT.user.owner_uuid)

        perm_rule_uuid |= {'sprint_single_user': rule_uuid}

    @story('119531 迭代权限-成为迭代负责人：移除成员域（成员）')
    def test_sprint_perm_del_single_user(self, perm_rule_uuid):
        ProjPermissionAction.del_permission(perm_rule_uuid['sprint_single_user'])

    @story('119539 迭代权限-管理迭代：检查管理迭代权限默认状态')
    def test_check_manage_sprint_default_permission(self):
        # 获取项目权限规则
        resp = permission_rules()

        with step('成员A查看「管理迭代」权限点的默认成员域'):
            manage_sprint = [p['user_domain_type'] for p in resp['permission_rules'] if
                             p['permission'] == 'manage_sprints']

            assert 'project_administrators' in manage_sprint

    @story('T119522 迭代权限-成为迭代负责人：添加成员域（部门）')
    def test_be_assigned_to_sprint_perm_add_department(self, perm_rule_uuid):
        with step('前置条件'):
            # 存在部门A
            param = thr.add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)

            depart_uuid = resp.json()['add_department']['uuid']

        with step('选择部门A添加'):
            rule_uuid = ProjPermissionAction.add_permission('department', 'be_assigned_to_sprint', depart_uuid)

            perm_rule_uuid |= {'department': rule_uuid}

        with step('清除部门数据'):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story('119541 迭代权限-管理迭代：添加成员域（部门）')
    @story("T119549 迭代权限-管理迭代：移除成员域（部门）")
    def test_manage_sprint_perm_add_department(self, perm_rule_uuid):
        with step('前置条件'):
            # 存在部门A
            param = thr.add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)

            depart_uuid = resp.json()['add_department']['uuid']

        with step('选择部门A添加'):
            rule_uuid = ProjPermissionAction.add_permission('department', 'manage_sprints', depart_uuid)

            perm_rule_uuid |= {'department': rule_uuid}

        with step('清除部门数据'):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story('119542 迭代权限-管理迭代：添加成员域（成员）')
    def test_manage_sprint_perm_add_single_user(self, perm_rule_uuid):
        rule_uuid = ProjPermissionAction.add_permission('single_user', 'manage_sprints',
                                                        ACCOUNT.user.owner_uuid)

        perm_rule_uuid |= {'single_user': rule_uuid}

    @story('119543 迭代权限-管理迭代：添加成员域（所有人）')
    def test_manage_sprint_perm_add_everyone(self, perm_rule_uuid):
        rule_uuid = ProjPermissionAction.add_permission('everyone', 'manage_sprints')

        perm_rule_uuid |= {'everyone': rule_uuid}

    @story('119544 迭代权限-管理迭代：添加成员域（项目负责人）')
    def test_manage_sprint_perm_add_proj_assign(self, perm_rule_uuid):
        rule_uuid = ProjPermissionAction.add_permission('project_assign', 'manage_sprints')

        perm_rule_uuid |= {'project_assign': rule_uuid}

    @story('119545 迭代权限-管理迭代：添加成员域（特殊角色-项目管理员）')
    def test_manage_sprint_perm_add_proj_admin(self, perm_rule_uuid):
        """"""
    @story('119547 迭代权限-管理迭代：添加成员域（项目角色-项目成员）')
    def test_manage_sprint_perm_add_role(self, perm_rule_uuid):
        # 获取项目成员 user_domain_param
        resp = team_stamp({'role': 0})
        proj_uuid = [p['uuid'] for p in resp['role']['roles'] if p['name'] == '项目成员'][0]

        with step('管理迭代成员域添加：项目成员'):
            rule_uuid = ProjPermissionAction.add_permission('role', 'manage_sprints', proj_uuid)

            perm_rule_uuid |= {'project_assign': rule_uuid}

    @story('119548 迭代权限-管理迭代：添加成员域（用户组）')
    @story("T119556 迭代权限-管理迭代：移除成员域（用户组）")
    def test_manage_sprint_perm_add_group(self, perm_rule_uuid):
        # 存在用户组
        param = data.user_group_add()[0]
        resp = self.call(prj.UsesGroupAdd, param)

        group_uuid = resp.value('uuid')

        with step('选择用户组A添加'):
            rule_uuid = ProjPermissionAction.add_permission('group', 'manage_sprints', group_uuid)

            perm_rule_uuid |= {'department': rule_uuid}

        with step('清除用户组数据'):
            param.uri_args({'group_uuid': group_uuid})
            self.call(prj.UsesGroupDelete, param, with_json=False)

    @story('119550 迭代权限-管理迭代：移除成员域（成员）')
    def test_manage_sprint_perm_del_single_user(self, perm_rule_uuid):
        ProjPermissionAction.del_permission(perm_rule_uuid['single_user'])

    @story("T119551 迭代权限-管理迭代：移除成员域（特殊角色-所有人）")
    def test_manage_sprint_perm_del_everyone(self, perm_rule_uuid):
        ProjPermissionAction.del_permission(perm_rule_uuid['everyone'])

    @story("T119552 迭代权限-管理迭代：移除成员域（特殊角色-项目负责人）")
    def test_manage_sprint_perm_del_project_assign(self, perm_rule_uuid):
        ProjPermissionAction.del_permission(perm_rule_uuid['project_assign'])