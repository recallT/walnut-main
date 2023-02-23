"""
@Desc：项目设置-权限配置-项目权限
"""
import time

from falcons.check import Checker
from falcons.com.nick import feature, story, step, fixture

from main.actions.member import MemberAction
from main.actions.pro import ProjPermissionAction
from main.api import project as prj, third
from main.params import data, third as thr
from main.params.const import ACCOUNT
from . import permission_rules
from main.params.third import add_sub_department


@fixture(scope='module')
def perm_rule_uuid():
    """权限uuid"""

    return {}


@feature('项目权限')
class TestProjPermission(Checker):

    @story('147970 查看项目：添加成员域（所有人）')
    def test_browse_proj_add_everyone(self, perm_rule_uuid):
        rule_uuid = ProjPermissionAction.add_permission('everyone')

        perm_rule_uuid |= {'everyone': rule_uuid}

    @story('147989 查看项目：添加成员域（成员）')
    def test_browse_proj_add_single_user(self, perm_rule_uuid):
        rule_uuid = ProjPermissionAction.add_permission('single_user',
                                                        user_domain_param=ACCOUNT.user.owner_uuid)

        perm_rule_uuid |= {'single_user': rule_uuid}

    @story('147969 查看项目：添加成员域（部门）')
    def test_browse_proj_add_department(self, perm_rule_uuid):
        with step('前置条件'):
            # 存在部门A
            param = thr.add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)

            depart_uuid = resp.json()['add_department']['uuid']

        with step('选择部门A添加'):
            rule_uuid = ProjPermissionAction.add_permission('department', user_domain_param=depart_uuid)

            perm_rule_uuid |= {'department': rule_uuid}

        with step('清除部门数据'):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story('147981 查看项目：添加成员域（用户组）')
    def test_browse_proj_add_group(self, perm_rule_uuid):
        with step('前置条件'):
            # 存在用户组
            param = data.user_group_add()[0]
            resp = self.call(prj.UsesGroupAdd, param)

            group_uuid = resp.value('uuid')

        with step('选择用户组A添加'):
            rule_uuid = ProjPermissionAction.add_permission('group', user_domain_param=group_uuid)

            perm_rule_uuid |= {'department': rule_uuid}

        with step('清除用户组数据'):
            param.uri_args({'group_uuid': group_uuid})
            self.call(prj.UsesGroupDelete, param, with_json=False)

    @story('147993 查看项目：添加成员域（项目负责人）')
    def test_browse_proj_proj_assign(self, perm_rule_uuid):
        rule_uuid = ProjPermissionAction.add_permission('project_assign')

        perm_rule_uuid |= {'project_assign': rule_uuid}

    @story('147995 查看项目：添加成员域（项目管理员）')
    def test_browse_proj_add_proj_admin(self):
        """"""

    @story('147977 查看项目：添加成员域（角色）')
    def test_browse_proj_role(self, perm_rule_uuid):
        with step('前置条件'):
            # 存在角色
            role_uuid = MemberAction.add_member_role().value('role.uuid')

        with step('选择角色A添加'):
            rule_uuid = ProjPermissionAction.add_permission('role', user_domain_param=role_uuid)

            perm_rule_uuid |= {'role': rule_uuid}
            perm_rule_uuid |= {'role_uuid': role_uuid}

    @story('147982 查看项目：删除项目负责人')
    def test_browse_proj_del_proj_assign(self, perm_rule_uuid):
        ProjPermissionAction.del_permission(perm_rule_uuid['project_assign'])

    @story('148001 项目权限：新建项目后，项目权限默认成员域列表检查')
    def test_check_proj_default_permission(self):
        # 获取项目权限规则
        resp = permission_rules()

        with step('检查「查看项目」默认成员域'):
            browse_perm = [p['user_domain_type'] for p in resp['permission_rules'] if
                           p['permission'] == 'browse_project']

            assert 'project_administrators', 'role' in browse_perm  # 项目管理员，项目成员

        with step('检查「管理项目」默认成员域'):
            manage_perm = [p['user_domain_type'] for p in resp['permission_rules'] if
                           p['permission'] == 'manage_project']

            assert 'project_assign' in manage_perm  # 项目负责人

        with step('检查「查看项目报表」默认成员域'):
            view_report_perm = [p['user_domain_type'] for p in resp['permission_rules'] if
                                p['permission'] == 'view_project_reports']

            assert ['project_administrators', 'role'] == view_report_perm  # 项目管理员，项目成员

    @story('147984 管理项目：添加成员域（成员）')
    @story("T147987 项目权限-管理项目：删除成员域")
    def test_manage_proj_add_single_user(self, perm_rule_uuid):
        rule_uuid = ProjPermissionAction.add_permission('single_user', 'manage_project',
                                                        ACCOUNT.user.owner_uuid)

        perm_rule_uuid |= {'manage_single_user': rule_uuid}
        # 删除成员域
        ProjPermissionAction.del_permission(perm_rule_uuid['manage_single_user'])

    @story('147990 查看项目：删除成员域（角色）')
    def test_browse_proj_del_role(self, perm_rule_uuid):
        ProjPermissionAction.del_permission(perm_rule_uuid['role'])

        # 清除配置中心-角色
        time.sleep(1)
        MemberAction.del_member_role(perm_rule_uuid['role_uuid'])

    @story("T148003 项目权限-查看项目报表：添加成员域（成员）")
    @story("T147991 项目权限-查看项目报表：删除成员域")
    def test_browse_proj_report_add_del_member(self, perm_rule_uuid):
        rule_uuid = ProjPermissionAction.add_permission('single_user', 'view_project_reports',
                                                        ACCOUNT.user.owner_uuid)
        perm_rule_uuid |= {'view_project_report_user': rule_uuid}
        # 删除成员
        ProjPermissionAction.del_permission(perm_rule_uuid['view_project_report_user'])

    @story("T147998 项目权限-查看项目报表：添加成员域（项目负责人）")
    @story("T147975 项目权限-查看项目报表：删除项目负责人")
    def test_browse_proj_report_add_proj_leader(self, perm_rule_uuid):
        rule_uuid = ProjPermissionAction.add_permission('project_assign', 'view_project_reports')
        """保存添加「项目负责人」的uuid"""
        perm_rule_uuid |= {'browse_project_assign': rule_uuid}
        """删除「项目负责人」"""
        ProjPermissionAction.del_permission(perm_rule_uuid['browse_project_assign'])

    @story("T147988 项目权限-查看项目报表：添加成员域（项目管理员）")
    def test_browse_proj_report_add_project_admin(self, perm_rule_uuid):
        """先获取成员域，清空"""
        # response = permission_rules(project_uuid=ACCOUNT.project_uuid)
        # with step("先获取和删除成员域的列表"):
        #     rule_uuid = [p['uuid'] for p in response['permission_rules'] if
        #                  p['permission'] == 'view_project_reports']
        #     for i in range(len(rule_uuid)):
        #         ProjPermissionAction.del_permission(rule_uuid[i])
        # with step("成员域 添加「项目管理员」"):
        #     uuid = ProjPermissionAction.add_permission('project_administrators', 'view_project_reports')
        #     """保存添加「项目管理员」的uuid"""
        #     perm_rule_uuid |= {'browse_project_administrators': uuid}
        # """删除「项目管理员」"""
        # ProjPermissionAction.del_permission(perm_rule_uuid['browse_project_administrators'])

    @story("T148004 项目权限-查看项目报表：添加成员域（部门）")
    def test_browse_proj_report_add_department(self, perm_rule_uuid):
        #  新增部门
        param = add_sub_department()[0]
        resp = self.call(third.ADDSubDepartment, param)
        depart_uuid = resp.json()['add_department']['uuid']
        rule_uuid = ProjPermissionAction.add_permission('department', 'view_project_reports', user_domain_param=depart_uuid)
        """保存添加「部门」的uuid"""
        perm_rule_uuid |= {'browse_department': rule_uuid}
        """删除「部门」"""
        ProjPermissionAction.del_permission(perm_rule_uuid['browse_department'])

    @story("T147994 项目权限-查看项目报表：添加成员域（用户组）")
    def test_browse_proj_report_add_group(self, perm_rule_uuid):
        #  新增用户组
        param = data.user_group_add()[0]
        resp = self.call(prj.UsesGroupAdd, param)
        group_uuid = resp.value('uuid')
        rule_uuid = ProjPermissionAction.add_permission('group', 'view_project_reports', user_domain_param=group_uuid)
        """保存添加「用户组」的uuid"""
        perm_rule_uuid |= {'browse_group': rule_uuid}
        """删除「用户组」"""
        ProjPermissionAction.del_permission(perm_rule_uuid['browse_group'])

    @story("T147979 项目权限-查看项目报表：添加成员域（所有人）")
    def test_browse_proj_report_add_everyone(self, perm_rule_uuid):
        rule_uuid = ProjPermissionAction.add_permission('everyone', 'view_project_reports')
        """保存「所有人」的uuid"""
        perm_rule_uuid |= {'browse_everyone': rule_uuid}
        """删除「所有人」"""
        ProjPermissionAction.del_permission(perm_rule_uuid['browse_everyone'])

    @story("T147999 项目权限-查看项目报表：添加成员域（角色）")
    def test_browse_proj_add_project_role(self, perm_rule_uuid):
        #  新增角色
        role_uuid = MemberAction.add_member_role().value('role.uuid')
        rule_uuid = ProjPermissionAction.add_permission('role', 'view_project_reports', user_domain_param=role_uuid)
        """保存添加「角色」的uuid"""
        perm_rule_uuid |= {'browse_role': rule_uuid}
        """删除「角色」"""
        ProjPermissionAction.del_permission(perm_rule_uuid['browse_role'])

    @story("T147986 项目权限-管理项目：添加成员域（部门）")
    def test_manage_proj_add_member(self, perm_rule_uuid):
        #  新增部门
        param = add_sub_department()[0]
        resp = self.call(third.ADDSubDepartment, param)
        depart_uuid = resp.json()['add_department']['uuid']
        rule_uuid = ProjPermissionAction.add_permission('department', 'manage_project', user_domain_param=depart_uuid)
        """保存添加「部门」的uuid"""
        perm_rule_uuid |= {'manage_department': rule_uuid}
        """删除「部门」"""
        ProjPermissionAction.del_permission(perm_rule_uuid['manage_department'])

    @story("T147971 项目权限-管理项目：添加成员域（角色）")
    def test_manage_proj_add_role(self, perm_rule_uuid):
        #  新增角色
        role_uuid = MemberAction.add_member_role().value('role.uuid')
        rule_uuid = ProjPermissionAction.add_permission('role', 'manage_project', user_domain_param=role_uuid)
        """保存添加「角色」的uuid"""
        perm_rule_uuid |= {'manage_role': rule_uuid}
        """删除「角色」"""
        ProjPermissionAction.del_permission(perm_rule_uuid['manage_role'])

    @story("T148000 项目权限-管理项目：添加成员域（所有人）")
    def test_manage_proj_add_everyone(self, perm_rule_uuid):
        rule_uuid = ProjPermissionAction.add_permission('everyone', 'manage_project')
        """保存添加「所有人」的uuid"""
        perm_rule_uuid |= {'manage_everyone': rule_uuid}
        """删除「所有人」"""
        ProjPermissionAction.del_permission(perm_rule_uuid['manage_everyone'])

    @story("T148002 项目权限-管理项目：添加成员域（用户组）")
    def test_manage_proj_add_group(self, perm_rule_uuid):
        #  新增用户组
        param = data.user_group_add()[0]
        resp = self.call(prj.UsesGroupAdd, param)
        group_uuid = resp.value('uuid')
        rule_uuid = ProjPermissionAction.add_permission('group', 'manage_project', user_domain_param=group_uuid)
        """保存添加「用户组」的uuid"""
        perm_rule_uuid |= {'manage_group': rule_uuid}
        """删除「用户组」"""
        ProjPermissionAction.del_permission(perm_rule_uuid['manage_group'])

    @story("T147992 项目权限-管理项目：添加成员域（项目负责人）")
    def test_manage_proj_add_project_assign(self, perm_rule_uuid):
        response = permission_rules(project_uuid=ACCOUNT.project_uuid)
        with step("先获取和删除成员域的列表"):
            rule_uuid = [p['uuid'] for p in response['permission_rules'] if
                         p['permission'] == 'manage_project']
            for i in range(len(rule_uuid)):
                ProjPermissionAction.del_permission(rule_uuid[i])
        with step("成员域 添加「项目负责人」"):
            uuid = ProjPermissionAction.add_permission('project_assign', 'manage_project')
            """保存添加「项目负责人」的uuid"""
            perm_rule_uuid |= {'manage_project_assign': uuid}
