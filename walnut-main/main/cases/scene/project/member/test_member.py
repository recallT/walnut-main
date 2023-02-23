"""
@File    ：member
@Author  ：zhangyonghui
@Email   ：zhangyonghui@ones.ai
@Date    ：2022/6/06
@Desc    ：成员管理
"""

from falcons.check import Checker, go
from falcons.com.nick import story, feature, fixture, step

from main.actions.member import MemberAction
from main.api.project import UsesSearch, ProjectRoleDelete, ProjAddMembers, ProjDelMembers
from main.params import proj
from main.params.conf import member_list, update_proj_members


@fixture(scope='module', autouse=True)
def add_member_role():
    # 在配置中心中创建一个角色
    role_uuid = MemberAction.add_member_role().value('role.uuid')
    return role_uuid


@fixture(scope='module', autouse=True)
def del_member_role(add_member_role):
    """删除配置中心的角色信息"""
    yield
    MemberAction.del_member_role(add_member_role)


@feature('项目-成员管理')
class TestProjMember(Checker):

    @story('T119060 成员管理-项目成员：添加成员')
    def test_add_proj_member(self):
        # 查询系统内存在的member 成员uuid
        su_param = proj.program_search_user()[0]
        resp_user_uuid = go(UsesSearch, su_param).value('users[0].uuid')
        # 新增成员
        MemberAction.add_proj_member(resp_user_uuid)

    @story('T119010 成员管理-角色：添加项目成员中不存在的成员')
    @story('143972 成员管理-角色：添加项目成员中不存在的成员')
    def test_add_member_not_in_proj(self):
        role_uuid = MemberAction.add_member_role().value('role.uuid')
        MemberAction.add_proj_role(role_uuid)

        with step('添加成员到角色中'):
            su_param = proj.program_search_user()[0]
            resp = go(UsesSearch, su_param)

            if len(resp.value('users')) >= 2:
                
                resp_user_uuid = resp.value('users[1].uuid')
                param = update_proj_members([resp_user_uuid])[0]
                param.uri_args({"role_uuid": role_uuid})
                go(ProjAddMembers, param)
                MemberAction.del_member_role(role_uuid)

    @story('T143976 T144030成员管理-项目成员：移除成员')
    def test_del_proj_members(self):
        su_param = proj.program_search_user()[0]
        resp_user_uuid = go(UsesSearch, su_param).value('users[0].uuid')
        # 新增成员
        MemberAction.add_proj_member(resp_user_uuid)
        with step('点击 成员B 的移除图标'):
            MemberAction.del_proj_member([resp_user_uuid])

    @story('T119084 成员管理：添加角色')
    def test_add_proj_role(self, add_member_role):
        MemberAction.add_proj_role(add_member_role)

    @story('T119087 成员管理：移除没有成员的角色')
    def test_del_proj_role_not_member(self):
        role_uuid = MemberAction.add_member_role().value('role.uuid')
        MemberAction.add_proj_role(role_uuid)

        with step('移除没有成员的角色'):
            param = member_list()[0]
            param.uri_args({"role_uuid": role_uuid})
            self.call(ProjectRoleDelete, param)
            MemberAction.del_member_role(role_uuid)

    @story('T119088 成员管理：移除有成员的角色')
    def test_del_proj_role_have_member(self):
        role_uuid = MemberAction.add_member_role().value('role.uuid')
        MemberAction.add_proj_role(role_uuid)

        with step('添加成员到角色中'):
            su_param = proj.program_search_user()[0]
            resp_user_uuid = go(UsesSearch, su_param).value('users[0].uuid')
            param = update_proj_members([resp_user_uuid])[0]
            param.uri_args({"role_uuid": role_uuid})
            resp = go(ProjAddMembers, param)
        with step('移除有成员的角色'):
            param = member_list()[0]
            param.uri_args({"role_uuid": role_uuid})
            self.call(ProjectRoleDelete, param)
            MemberAction.del_member_role(role_uuid)

    @story('T143975 成员管理-角色：移除成员')
    def test_del_proj_role_member(self):
        role_uuid = MemberAction.add_member_role().value('role.uuid')
        MemberAction.add_proj_role(role_uuid)

        with step('添加成员到角色中'):
            su_param = proj.program_search_user()[0]
            resp_user_uuid = go(UsesSearch, su_param).value('users[0].uuid')
            param = update_proj_members([resp_user_uuid])[0]
            param.uri_args({"role_uuid": role_uuid})
            resp = go(ProjAddMembers, param)

        with step('从角色中移除成员'):
            param = update_proj_members([resp_user_uuid])[0]
            param.uri_args({"role_uuid": role_uuid})
            resp = go(ProjDelMembers, param)
            assert resp_user_uuid not in resp.value('role_members[1].members')
            MemberAction.del_member_role(role_uuid)

    @story('T119044 成员管理-添加角色弹框：检查角色可选项')
    def test_check_role_list(self):
        with step('前置条件 存在两个角色，一个被添加到项目内，一个未被添加到项目内'):
            role_a_uuid = MemberAction.add_member_role().value('role.uuid')
            role_b_uuid = MemberAction.add_member_role().value('role.uuid')
            MemberAction.add_proj_role(role_a_uuid)
        with step('列表检查'):
            resp = MemberAction.get_member_list()
            role_uuid_list = [uuid['role']['uuid'] for uuid in resp.value('role_members')]
            assert role_a_uuid in role_uuid_list
            assert role_b_uuid not in role_uuid_list
            MemberAction.del_member_role(role_a_uuid)
            MemberAction.del_member_role(role_b_uuid)
