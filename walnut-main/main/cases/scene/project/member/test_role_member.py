"""
@File    ：test_role_member
@Author  ：xiechunwei
@Date    ：2022/8/15 14:19
@Desc    ：项目-成员组件-成员角色管理
"""

from falcons.check import Checker
from falcons.com.nick import story, feature, fixture, step
from main.actions.member import MemberAction
from main.api import project as prj
from main.params import proj, conf
from main.params.const import ACCOUNT



@fixture(scope='module')
def role_opt():
    # 在配置中心中创建一个角色
    role_uuid = MemberAction.add_member_role().value('role.uuid')

    # 项目内添加角色
    MemberAction.add_proj_role(role_uuid)

    yield role_uuid

    # 使用完后删除角色
    MemberAction.del_member_role(role_uuid)


@feature('角色管理')
class TestRoleMember(Checker):

    def search_member(self):
        """搜索默认成员normal的uuid"""
        su_param = proj.program_search_user()[0]
        resp = self.call(prj.UsesSearch, su_param)

        return resp.value('users[1].uuid')

    @story('143969 成员管理-角色：检查可添加成员')
    @story('119058 成员管理-项目成员：检查可添加成员')
    @story('23618 查看成员列表')
    def test_check_member_list(self):
        with step('查看成员列表左栏, 展示项目角色'):
            resp = MemberAction.get_member_list()
            role_name = [n['role']['name'] for n in resp.value('role_members')]

            assert len(role_name) >= 1

    @story('23617 搜索成员')
    @story('23083 添加成员')
    @story('23081 添加角色')
    @story('23621 角色中添加成员')
    def test_role_add_member(self, role_opt):
        with step('搜索成员'):
            user_uuid = self.search_member()

        with step('点击添加成员'):
            param = conf.update_proj_members([user_uuid])[0]
            param.uri_args({"role_uuid": role_opt})

            self.call(prj.ProjAddMembers, param)

    @story('23084 移除成员')
    @story('119012 成员管理-角色：移除成员')
    def test_delete_member(self, role_opt):
        with step('搜索成员'):
            user_uuid = self.search_member()

        with step('点击对应成员 操作中的移除按钮'):
            param = conf.update_proj_members([user_uuid])[0]
            param.uri_args({"role_uuid": role_opt})

            self.call(prj.ProjDelMembers, param)

    @story('119011 成员管理-角色：添加项目成员中已存在的成员')
    @story('143966 成员管理-角色：添加项目成员中已存在的成员')
    def test_add_member_in_proj(self, role_opt):
        with step('点击添加成员'):
            param = conf.update_proj_members([ACCOUNT.user.owner_uuid])[0]
            param.uri_args({"role_uuid": role_opt})

            resp = self.call(prj.ProjAddMembers, param)

        with step('点击查看项目成员，成员总数不变'):
            member = [n['role']['uuid'] for n in resp.value('role_members') if n['role']['name'] == '项目成员']
            assert len(member) >= 1

    @story('23082 移除角色')
    def test_delete_role(self, role_opt):
        with step('点击「移除角色」'):
            param = conf.member_list()[0]
            param.uri_args({"role_uuid": role_opt})
            self.call(prj.ProjectRoleDelete, param)