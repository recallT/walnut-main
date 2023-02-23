#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_config.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/24 
@Desc    ：甘特图权限配置测试用例
"""
from falcons.check import Checker
from falcons.com.env import User
from falcons.com.nick import feature, story, parametrize, step, fixture
from falcons.com.ones import unify_login

from main.api import project as prj
from main.params import plan, auth


@fixture(scope='module', autouse=True)
def _member_storage():
    """"""
    return []


@feature('甘特图')
class TestGantt(Checker):

    @story('T22810 权限管理-添加成员创建甘特图权限')
    @parametrize('param', plan.add_member())
    def test_add_member(self, param, _member_storage):
        """"""
        with step('添加一个成员到团队'):
            p = auth.invitation()[0]
            _member = {'email': p.json['invite_settings'][0]['email'],
                       'password': '',
                       'uuid': '',
                       }

            ia = self.call(prj.InvitationsAdd, p)

            h = auth.invitation_history()[0]

            ih = self.call(prj.InvitationsHistory, h)

            # 邀请码
            invite_code = [c['code'] for c in ih.json()['invitations'] if c['email'] == _member['email']]

            jt = auth.join_team()[0]
            jt.json |= {'email': _member['email'], 'invite_code': invite_code[0]}

            aj = self.call(prj.AuthInviteJoin, jt)
            # 获取新成员uuid 和密码
            _member |= {'uuid': aj.json()['user']['uuid'], 'password': jt.json['password']}

            # 缓存成员信息
            _member_storage.append(_member)

        with step('添加权限'):
            """"""
            p_rules = auth.permission_rules()[0]

            pr = self.call(prj.PermissionRules, p_rules)

            # 获取成员创建甘特图的权限UUID
            # cgc = [c['user_domain_param'] for c in pr.json()['permission_rules'] if
            #        c['permission'] == 'create_gantt_chart' and c['user_domain_type'] == 'single_user']
            param.json['permission_rule']['user_domain_param'] = _member['uuid']
            self.call(prj.PermissionAdd, param)

    @story('T22811 权限管理-团队内成员创建甘特图')
    @parametrize('param', plan.create_gantt())
    def test_member_add_gant(self, param, _member_storage):
        """"""
        with step('成员登录'):
            u = _member_storage[0]
            member_token = unify_login(User(u['email'], u['password']))

            gan_add = self.call(prj.ItemsAdd, param, member_token)

            gan_add.check_response('item.name', param.json['item']['name'])
