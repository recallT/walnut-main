#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_user.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/6 
@Desc    ： 成员相关接口测试案例
"""

from falcons.com.nick import parametrize, feature, fixture, story, mark

from main.api.project import (
    UsersMe, UsersUpdate, UsersCurrentTeam,
    UsersReqCode, UsersVerifyPasswd,
)
from main.params import data


@fixture(scope='class')
def _storage():
    """用于存储案例间共享的数据"""
    p = []

    return p


@feature('成员相关接口')
class TestCurrentUsers:
    @mark.smoke
    @story('获取用户当前团队')
    def test_current_team(self, admin_token):
        """获取用户当前团队"""

        me = UsersCurrentTeam()

        me.call()
        me.is_response_code(200)
        me.check_response('owner', admin_token['Ones-User-Id'])


@feature('成员相关接口')
class TestUsersApi:
    @mark.smoke
    @story('修改团队成员信息')
    @parametrize('param', data.update_user_info())
    def test_users_update(self, param):
        """修改团队成员信息"""

        me = UsersUpdate()

        me.call(param.json)
        me.is_response_code(200)
        # me.check_response('owner', admin_token['Ones-User-Id'])

    @story('获取成员信息')
    def test_user_me(self):
        """获取成员信息"""

        me = UsersMe()

        me.call()
        me.is_response_code(200)
        me.check_response('uuid', admin_token['Ones-User-Id'])

    @story('发送验证码')
    @parametrize('param', data.user_req_code())
    def test_user_request_code(self, param):
        """发送验证码"""

        me = UsersReqCode()

        me.call(param.json)
        me.is_response_code(200)

        # db data in `request_code` table
        # tobe clean.

    @story('发送验证码-已注册邮箱')
    @parametrize('param', data.user_req_code_registered())
    def test_user_request_code_registered(self, param):
        """发送验证码-已注册邮箱"""

        me = UsersReqCode()
        me.call(param.json)
        me.is_response_code([621, 804])

    @story('验证密码')
    @parametrize('param', data.user_verify_passwd())
    def test_user_request_password(self, param):
        """验证密码"""

        me = UsersVerifyPasswd()

        me.call(param.json)
        me.is_response_code(200)

    @story('验证密码-密码错误')
    @parametrize('param', data.user_verify_passwd())
    def test_user_verify_password_invalid(self, param):
        """验证密码-密码错误"""

        me = UsersVerifyPasswd()
        param.json['password'] = '0323232'
        me.call(param.json)
        me.is_response_code([400, 804])
