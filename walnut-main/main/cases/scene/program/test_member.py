#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_member.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/28 
@Desc    ：
"""
from falcons.com.nick import story, step, parametrize, fixture, feature

from main.api import project as pj
from main.params import proj


@fixture(scope='session', autouse=True)
def fx_program():
    """用于测试的项目集"""
    p = proj.add_program()[0]
    ia = pj.ItemsAdd()
    ia.call(p.json, **p.extra)
    ia.is_response_code(200)
    # {
    #   "item": {
    #     "item_type": "program",
    #     "key": "program-DqRFPErm",
    #     "uuid": "DqRFPErm"
    #   }
    # }
    s = ia.json()['item']
    s |= {'name': p.json["item"]["name"]}
    print(f'Create test plan: {s["name"]}:{s["uuid"]}')

    return s


@fixture(scope='session', autouse=True)
def clear_program(fx_program):
    """删除用于测试的项目集"""
    yield
    print(f'Delete test plan: {fx_program["name"]}')
    del_param = proj.delete_program()[0]
    del_param.uri_args({'item_key': fx_program['key']})
    del_item = pj.ItemDelete()
    del_item.call(**del_param.extra)
    del_item.is_response_code(200)


@fixture(scope='session')
def _member_storage():
    """


    :return:
    """

    su_param = proj.program_search_user()[0]

    us = pj.UsesSearch()
    us.call(su_param.json, **su_param.extra)
    us.is_response_code(200)

    users = [u['uuid'] for u in us.json()['users']]

    return users


@fixture(scope='session')
def _role_storage(fx_program):
    """


    :param fx_program:
    :return:
    """

    role_param = proj.list_program_role()[0]
    item = pj.ItemGraphql()
    role_param.json['variables']['filter']['context'] |= {'programUUID_equal': fx_program['uuid']}
    item.call(role_param.json, **role_param.extra)
    role_uuid = {r['name']: r['key'] for r in item.json()['data']['roles']}  # 获取角色配置key

    return role_uuid


@feature('项目集')
class TestProgramsMemberAdmin:
    """项目集管理员案例"""

    @story('23069 项目集成员-添加项目集管理员')
    def test_program_admin_member_add(self, fx_program, _role_storage, _member_storage):
        """"""

        with step('添加项目集管理员'):
            if _member_storage:
                add_user_param = proj.add_program_user()[0]
                add_user_param.json['item']['members'] = _member_storage[:5]
                add_user_param.uri_args({'item_key': _role_storage['项目集管理员']})
                item_update = pj.ItemUpdate()
                item_update.call(add_user_param.json, **add_user_param.extra)
                item_update.is_response_code(200)

    @story('成员管理-项目集下成员列表信息')
    @parametrize('param', proj.list_program_role())
    def test_program_admin_member_list(self, param, fx_program):
        """"""
        item = pj.ItemGraphql()
        param.json['variables']['filter']['context'] |= {'programUUID_equal': fx_program['uuid']}

        item.call(param.json, **param.extra)
        item.is_response_code(200)

    @story('23065 项目集成员-删除项目集成员')
    @parametrize('param', proj.add_program_user())
    def test_program_admin_member_delete(self, param, _role_storage, _member_storage, fx_program):
        """"""

        param.json['item']['members'] = _member_storage[0:4]
        param.uri_args({'item_key': _role_storage['项目集管理员']})
        item_update = pj.ItemUpdate()
        item_update.call(param.json, **param.extra)
        item_update.is_response_code(200)

    @story('23070 项目集成员-批量删除项目集成员')
    @parametrize('param', proj.add_program_user())
    def test_program_admin_member_delete_batch(self, param, _role_storage, fx_program):
        """"""
        item = pj.ItemGraphql()

        param.json['item']['members'] = []
        param.uri_args({'item_key': _role_storage['项目集管理员']})
        item_update = pj.ItemUpdate()
        item_update.call(param.json, **param.extra)
        item_update.is_response_code(200)

    @story('23076 项目集负责人信息')
    def test_program_member_delete(self, fx_program):
        """"""
    #     tep = pj.ItemGraphql()
    #
    #     tep.call(param.json, **param.extra)
    #
    #     tep.is_response_code(200)
    #     assign = tep.json()['data']['programs'][0]['assign']
    #     assert assign['name'] == 'Test Admin'
