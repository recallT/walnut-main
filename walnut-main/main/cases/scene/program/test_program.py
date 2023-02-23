#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_program.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/27 
@Desc    ： 项目集测试用例
"""

from falcons.com.nick import story, parametrize, step, fixture, feature

from main.actions.pro import PrjAction
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
    print(f'Create test plan:{s["name"]} : {s["uuid"]}')

    return s


@fixture(scope='session', autouse=True)
def clear_program(fx_program):
    """删除用于测试的项目集"""
    yield
    print(f'Delete test plan:{fx_program["name"]}')
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


@fixture(scope='session', autouse=True)
def clear_program(fx_program):
    """删除用于测试的项目集"""
    yield

    # 删除测试项目
    p_uuid = fx_program['project_uuid']

    PrjAction.delete_project(p_uuid)

    print(f'Create test plan: {fx_program["name"]}')
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
class TestPrograms:

    @story('T23055 新建项目-在项目集下新建项目')
    @parametrize('param', proj.add_project()[1:2])
    def test_add_project_in_program(self, param, fx_program):
        """"""
        param.json['project'] |= {'program_uuid': fx_program['uuid']}

        add_proj = pj.AddProject()

        add_proj.call(param.json, **param.extra)
        add_proj.is_response_code(200)
        add_proj.check_response('project.name', param.json['project']['name'])
        add_proj.check_response('project.program_uuid', param.json['project']['program_uuid'])

        # 缓存项目UUID 用于测试数据清理
        fx_program |= {'project_uuid': param.json_value('project.uuid')}

    @story('状态分组-查看项目集下的项目分组')
    @parametrize('param', proj.add_project()[1:2])
    def test_show_group_in_program(self, param, fx_program):
        """"""
        pass

    @story('T23043 支持拆分-新建子项目集')
    @story('T22569 结构化管理：项目集树状列表展示')
    @parametrize('param', proj.add_program())
    def test_add_sub_program(self, param, fx_program):
        """"""
        with step('新建子项目集B'):
            param.json['item'] |= {'parent': fx_program['uuid']}

            add_item = pj.ItemsAdd()

            add_item.call(param.json, **param.extra)
            add_item.is_response_code(200)

            sub_program_uuid = add_item.json()['item']['uuid']
            sub_program_key = add_item.json()['item']['key']

        with step('检查子项目集在A项目集下'):
            item_g = pj.ItemGraphql()
            p = proj.list_program()[0]
            p.json['variables']['filter']['ancestors_in'].append(fx_program['uuid'])

            item_g.call(p.json, **p.extra)
            item_g.is_response_code(200)

            resp_programs = item_g.json()['data']['programs']

            sub_info = [r for r in resp_programs if r['uuid'] == sub_program_uuid]

            assert sub_info[0]['parent'] == fx_program['uuid']
            assert sub_info[0]['key'] == sub_program_key

    @story('147264 新建项目集：不添加项目')
    def test_program_no_add_proj(self):
        """"""