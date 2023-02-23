"""
@File    ：test_project_member.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/4/28
@Desc    ：项目-全局配置-项目成员配置测试用例
"""

import time

from falcons.check import Checker, go
from falcons.com.nick import story, fixture, step, parametrize, feature
from falcons.com.ones import unify_login

from main.actions.issue import IssueAction
from main.actions.member import MemberAction
from main.actions.task import TaskAction
from main.api import project as api, project
from main.api.issue import AddSubScription, DelSubScription
from main.params import devops, issue, proj
from main.params.data import delete_member


@fixture(scope='module', autouse=True)
def normal_member():
    """
    新建一个普通用户供测试使用

    :return:
    """

    user = MemberAction.new_member()
    return user


@fixture(scope='module')
def normal_token(normal_member):
    """普通用户登陆后的head信息"""
    return unify_login(normal_member)


@fixture(scope='module')
def clear_member(normal_member):
    """删除测试用户"""
    yield
    d_param = delete_member()[0]
    d_param.json_update('member', normal_member.uuid)
    go(api.DeleteMember, d_param)


@fixture(scope='module')
def rule_uuid():
    """权限uuid 缓存"""
    return {'read': '', 'manage': ''}


@feature('全局配置')
class TestGlobalProjectMember(Checker):
    """"""

    @story('T147984 项目管理-项目详情-管理项目：添加成员域（成员）')
    @parametrize('param', devops.user_permission_add('manage_project'))
    def test_add_member_to_manage_project(self, param, normal_member, normal_token, rule_uuid):
        """"""
        with step('添加成员域（成员）'):
            param.json_update('permission_rule.user_domain_param', normal_member.uuid)
            resp = self.call(api.PermissionAdd, param)
            rule_uuid |= {'manage': resp.value('permission_rule.uuid')}
        with step('成员B登录系统-顶部导航中有：项目设置'):
            eval_param = devops.eval_permission('manage_project')[0]
            eval_resp = self.call(api.TeamEvalPermissions, eval_param, normal_token)
            assert eval_resp.value('evaluated_permissions')

    @story('项目管理-项目详情-管理项目：删除成员域')
    @parametrize('param', devops.permission_delete())
    def test_del_member_to_manage_project(self, param, normal_member, normal_token, rule_uuid):
        """"""
        param.uri_args({'rule_uuid': rule_uuid['manage']})
        self.call(api.PermissionDelete, param)

        with step('成员B登录系统-顶部导航中有：项目设置'):
            eval_param = devops.eval_permission('manage_project')[0]
            eval_resp = self.call(api.TeamEvalPermissions, eval_param, normal_token)
            assert not eval_resp.value('evaluated_permissions')

    @story('137865 项目管理-项目详情-查看项目：添加成员域（成员）')
    @parametrize('param', devops.user_permission_add('browse_project'))
    def test_add_member_to_view_project(self, param, normal_member, normal_token, rule_uuid):
        """"""

        with step('添加成员域（成员）'):
            param.json_update('permission_rule.user_domain_param', normal_member.uuid)
            resp = self.call(api.PermissionAdd, param)
            rule_uuid |= {'read': resp.value('permission_rule.uuid')}
        with step('成员B登录系统-顶部导航中有：项目设置'):
            eval_param = devops.eval_permission('browse_project')[0]
            eval_resp = self.call(api.TeamEvalPermissions, eval_param, normal_token)
            assert eval_resp.value('evaluated_permissions')

    @story('137862 项目管理-项目详情-查看项目：删除成员域（成员）')
    @parametrize('param', devops.permission_delete())
    def test_del_member_to_view_project(self, param, normal_member, normal_token, rule_uuid):
        """"""
        param.uri_args({'rule_uuid': rule_uuid['read']})
        self.call(api.PermissionDelete, param)

        with step('成员B登录系统-顶部导航中有：项目设置'):
            time.sleep(2)
            eval_param = devops.eval_permission('browse_project')[0]
            eval_resp = self.call(api.TeamEvalPermissions, eval_param, normal_token)

            if not eval_resp.value('evaluated_permissions'):
                assert not eval_resp.value('evaluated_permissions')

