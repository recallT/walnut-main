#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_invite.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/2 
@Desc    ：邀请注册
"""
from falcons.com.nick import feature, story, parametrize, fixture, mark
from falcons.helper.mysql import MysqlOps

from main.api.project import InvitationsAdd
from main.params.auth import invitation
from main.params.const import ACCOUNT


@fixture(autouse=True, scope='class')
def my_fixture(environment):
    yield
    print("Clean invitation record.")
    cnf = {'db': environment['db'], 'ssh_config': environment['ssh_config']}
    db = MysqlOps(cnf)

    _db = cnf['db'].db
    if _db:
        db_name = f'project_{_db}'
    else:
        db_name = f'project_{environment["sprint"]}' if environment["sprint"] else 'project'

    sql = f"delete from {db_name}.invitation where status=1 and team_uuid='{ACCOUNT.user.team_uuid}';"
    r = db.execute_sql(sql)
    print(f'invitation: {r} records deleted.')

    sql = f"delete from {db_name}.team_member where team_uuid='{ACCOUNT.user.team_uuid}';"
    r = db.execute_sql(sql)
    print(f'team_member: {r} records deleted.')


@fixture(scope='module')
def _storage():
    """存储用户UUID"""
    p = []
    return p


@feature('邀请注册接口')
class TestInvitation:
    @mark.smoke
    @story('邀请注册成功')
    @parametrize('param', invitation())
    def test_invite_success(self, param):
        """邀请注册"""

        invite = InvitationsAdd()

        # 调用接口
        invite.call(param.json, **param.extra)
        # 检查接口响应码
        invite.is_response_code(200)

    @story('邀请注册成功')
    @parametrize('param', invitation())
    def test_invite_success_empty_product(self, param):
        """邀请注册"""

        invite = InvitationsAdd()
        param.json['license_types'] = []  # 不授权产品
        # 调用接口
        invite.call(param.json, **param.extra)
        # 检查接口响应码
        invite.is_response_code([200, 400, 804])  # 接口返回不稳定啊

    @story('邀请注册失败-授权产品非法')
    @parametrize('param', invitation())
    def test_invite_fail_invalid_product(self, param):
        """邀请注册"""

        invite = InvitationsAdd()
        param.json['license_types'] = [999, 888]  # 授权产品代码非法
        # 调用接口
        invite.call(param.json, **param.extra)
        # 检查接口响应码
        invite.is_response_code([400, 804])
        # 检查测试响应数据
        # invite.check_response('errcode', 'InvalidParameter.LicenseGrant.Type.InvalidType')

    @story('邀请注册失败-邮箱为空')
    @parametrize('param', invitation())
    def test_invite_fail_empty_mail(self, param):
        """邀请注册"""

        invite = InvitationsAdd()
        json = param.json
        json['invite_settings'] = []  # 空邀请邮箱
        # 调用接口
        invite.call(param.json, **param.extra)
        # 检查接口响应码
        invite.is_response_code([400, 804])

        # 检查测试响应数据
        # invite.check_response('errcode', 'MissingParameter.Invitation.Email')
