#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_auth.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/2 
@Desc    ：认证登录测试案例
"""
from falcons.com.nick import feature, story, mark

from main.api.auth import LoginAuth, TokenInfo
from main.api.project import CheckEmail
from main.params.const import ACCOUNT


@feature('认证登录接口')
class TestAuth:
    @mark.smoke
    @story('登录成功')
    def test_auth_success(self):
        """登录成功"""

        add_p = LoginAuth()
        u = ACCOUNT.user
        json = {'email': u.email, 'password': u.passwd}
        # 调用接口
        add_p.call(json)
        # 检查接口响应码
        add_p.is_response_code(200)

        # 检查测试响应数据
        add_p.check_response('user.email', json['email'])
        add_p.check_response('user.status', 1)

    @story('登录失败-wrong-passwd')
    def test_auth_failed(self):
        """登录失败"""

        add_p = LoginAuth()
        u = ACCOUNT.user
        json = {'email': u.email, 'password': u.passwd + '1'}
        # 调用接口
        add_p.call(json)
        # 检查接口响应码
        add_p.is_response_code(401)

        # 检查测试响应数据
        # add_p.check_response('reason', 'InvalidPassword')

    @story('登录失败-wrong-param')
    def test_auth_failed_wrong_param(self):
        """登录失败"""

        add_p = LoginAuth()
        u = ACCOUNT.user
        json = {'email': u.email, 'passwd': u.passwd}
        # 调用接口
        add_p.call(json)
        # 检查接口响应码
        add_p.is_response_code(801)

        # 检查测试响应数据
        add_p.check_response('reason', 'InvalidFormat')


@feature('获取Token接口')
class TestTokenInfo:
    @mark.smoke
    @story('获取token成功')
    def test_token_info_success(self):
        """获取token成功"""

        token_info = TokenInfo()
        # 调用接口
        token_info.call()
        # 检查接口响应码
        token_info.is_response_code(200)
        h = token_info.session.headers
        # 检查测试响应数据
        token_info.check_response('user.token', h['Ones-Auth-token'])

    @story('获取token-请求token不合法')
    def test_auth_failed_no_header(self):
        """获取token失败"""

        token_info = TokenInfo()
        # 调用接口
        token_info.session.headers['Ones-Auth-token'] = ''
        token_info.call()
        # 检查接口响应码
        token_info.is_response_code(802)


@feature('验证邮箱接口')
class TestCheckEmail:
    @mark.smoke
    @story('验证邮箱通过')
    def test_check_email_success(self):
        """验证邮箱通过"""

        chick_email = CheckEmail()
        # 调用接口
        chick_email.call({'email': 'abc@ones.ai'})
        # 检查接口响应码
        chick_email.is_response_code(200)

    @story('验证邮箱非法')
    def test_check_email_invalid(self):
        """验证邮箱非法"""

        chick_email = CheckEmail()
        # 调用接口
        chick_email.call({'email': 'abc.ai'})
        # 检查接口响应码
        chick_email.is_response_code(801)
