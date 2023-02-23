"""
@File    ：test_project_conf.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/4/28
@Desc    ： 项目-全局配置-项目配置测试用例
"""
from falcons.check import Checker, go
from falcons.com.nick import story, fixture, step, parametrize, feature, mark

from main.api import project as api
from main.params import conf


@fixture(scope='module')
def roles():
    """
    新建几个角色供测试用
    产品经理/设计师/开发/测试角色

    :return:
    """

    t_roles = dict()
    for _ in range(4):
        param = conf.role_add()[0]
        resp = go(api.RolesAdd, param)
        t_roles |= {
            resp.value('role.uuid'): resp.value('role.name')
        }

    return t_roles


@mark.smoke
@feature('全局配置')
class TestGlobalProjectConf(Checker):
    #
    # @story('项目管理-成员-角色：检查新建项目后项目角色默认值（配置中心-项目角色无相应角色）')
    # def test_a(self, roles):
    # 一个开箱配置 暂不实现
    #     pass

    @story('T152243 项目管理-成员-角色：检查新建项目后项目角色默认值（配置中心-项目角色有相应角色）')
    @parametrize('param', conf.stamps_role())
    def test_check_project_default_role(self, param, roles):
        with step('查看成员-角色页面已有角色类型'):
            role_uuids = self.get_roles()

            for k in roles.keys():
                assert k in role_uuids

    @story('T152229 项目管理-成员-角色：移除项目角色（测试）')
    def test_delete_role_tester(self, roles):
        """"""
        deleted_key = list(roles.keys())[0]
        self.del_role(deleted_key, '测试')

    @story('T152228 项目管理-成员-角色：移除项目角色（产品经理）')
    def test_delete_role_pm(self, roles):
        """"""
        deleted_key = list(roles.keys())[1]

        self.del_role(deleted_key, '产品经理')

    @story('T152230 项目管理-成员-角色：移除项目角色（开发）')
    def test_delete_role_developer(self, roles):
        """"""
        deleted_key = list(roles.keys())[2]

        self.del_role(deleted_key, '开发')

    @story('T152231 项目管理-成员-角色：移除项目角色（设计师）')
    def test_delete_role_designer(self, roles):
        """"""
        deleted_key = list(roles.keys())[3]

        self.del_role(deleted_key, '设计师')

    def del_role(self, deleted_key, name, token=None):
        with step(f'删除{name}角色'):
            param = conf.role_delete()[0]
            param.uri_args({'role_uuid': deleted_key})
            self.call(api.RoleDelete, param, token)
        with step('查看项目角色-添加角色中下拉框'):
            role_uuids = self.get_roles(token)

            assert deleted_key not in role_uuids, f'角色未删除{roles[deleted_key]}'

    def get_roles(self, token=None):
        with step('查看项目角色-添加角色中下拉框'):
            r_param = conf.stamps_role()[0]
            resp = self.call(api.TeamStampData, r_param, token)
            role_uuids = [r['uuid'] for r in resp.value('role.roles')]

            return role_uuids
