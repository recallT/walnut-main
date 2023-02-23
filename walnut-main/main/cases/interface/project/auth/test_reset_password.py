#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_reset_password.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/2 
@Desc    ：认证重置测试案例
"""
from falcons.com.nick import feature, story, parametrize, mark

from main.api.project import ResetPasswdLink, ResetPasswdMail
from main.params.data import reset_passwd


@feature('重置密码接口')
class TestResetPasswd:
    @mark.smoke
    @story('重置密码链接成功')
    @parametrize('param', reset_passwd())
    def test_reset_password_link_success(self, param):
        """重置链接成功"""

        reset_pwd = ResetPasswdLink()
        email = param.json.pop('email')
        # 调用接口
        reset_pwd.call(param.json, **param.extra)
        # 检查接口响应码
        reset_pwd.is_response_code(200)

        # code = reset_passwd_code(email)
        # 去掉数据库检查，preview1 环境 不能连接数据库
        # # # 检查测试响应数据
        # reset_pwd.check_response('reset_password_link', code, 'contains')

    @story('重置密码邮箱失败-Wrong-Member')
    @parametrize('param', reset_passwd())
    def test_reset_password_link_fail_wrong_member(self, param):
        """重置链接成功"""

        reset_pwd = ResetPasswdLink()
        param.json.pop('email')
        extra = param.extra
        extra['uri_args'] |= {'member_uuid': 999}
        # 调用接口
        # wrong url :404
        reset_pwd.call(**extra)
        # 检查接口响应码
        reset_pwd.is_response_code(404)

    @story('重置密码邮箱失败-Wrong-Team')
    @parametrize('param', reset_passwd())
    def test_reset_password_link_fail_wrong_team(self, param):
        """重置链接成功"""

        reset_pwd = ResetPasswdLink()
        param.json.pop('email')
        param.extra['uri_args'] |= {'team_uuid': 999}  # team not exists.
        # 调用接口
        reset_pwd.call(**param.extra)
        # 检查接口响应码
        reset_pwd.is_response_code(403)

    @story('重置密码邮箱失败-404')
    @parametrize('param', reset_passwd())
    def test_reset_password_mail_fail_404(self, param):
        """重置链接成功"""

        reset_pwd = ResetPasswdLink()
        param.json.pop('email')
        # 调用接口
        # wrong url :404
        extra = param.extra
        extra['uri_args'] |= {'member_uuid': 999}
        reset_pwd.call(**param.extra)
        # 检查接口响应码
        reset_pwd.is_response_code(404)

    @story('重置密码邮箱成功')
    @parametrize('param', reset_passwd())
    def test_reset_password_mail_success(self, param):
        """重置邮件成功"""

        reset_pwd = ResetPasswdMail()
        param.json.pop('email')
        # 调用接口
        reset_pwd.call(param.json, **param.extra)
        # 检查接口响应码
        reset_pwd.is_response_code(200)
        # code = reset_passwd_code(email)
        # # 检查测试响应数据
        reset_pwd.check_response('type', 'OK')
