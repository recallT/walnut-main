#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_project_status.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/4 
@Desc    ： 全局配置-项目配置-项目状态测试用例
"""
from falcons.check import Checker
from falcons.com.nick import feature, story, parametrize, fixture, step

from main.api import project as api
from main.params import conf
from main.params.const import ACCOUNT


@fixture(scope='module')
def _status_storage():
    """
    主要是记录项目状态 用于清理测试数据
    :return:
    """
    return {}


@fixture(scope='module', autouse=True)
def _alise_key():
    """
    :return:
    """
    return {}


@fixture(scope='module', autouse=True)
def _new_status(_status_storage):
    """
    :return:
    """
    print('Get system status config....')
    status_param = conf.get_sys_status()[0]

    view = api.TeamView()
    view.call(status_param.json, **status_param.extra)
    view.is_response_code(200)
    item = view.json()['items'][0]

    _status_storage |= item

    print(f'Now statuses :{_status_storage}')


@fixture(scope='module', autouse=True)
def _restore_status(_status_storage):
    """
    :return:
    """
    yield
    print('Restore system status config....')
    param = conf.update_prj_status()[0]

    status_param = [s for s in _status_storage['statuses'] if s['built_in'] is True]
    item_key = _status_storage['key']
    param.json['item']['statuses'] = status_param
    param.uri_args({'item_key': item_key})

    view = api.ItemUpdate()

    view.call(param.json, **param.extra)
    view.is_response_code(200)


@feature('项目配置-全局配置-项目')
class TestProjectStatus(Checker):

    @story('T131559 全局项目配置 - 项目状态：新建进行中类型项目状态')
    @parametrize('param', conf.update_prj_status())
    def test_add_in_progress_status(self, param, _status_storage, _alise_key):
        """"""
        update = api.ItemUpdate()
        in_progress = {'name': 'Running', 'category': 'in_progress'}

        status_param = [s for s in _status_storage['statuses']]
        status_param.append(in_progress)
        param.json['item']['statuses'] = status_param

        param.uri_args({'item_key': _status_storage['key']})

        update.call(param.json, **param.extra)
        update.is_response_code(200)

        _status_storage = update.json()['item']
        _alise_key |= update.json()['item']

    @story('138347 项目状态：添加项目状态')
    @parametrize('param', conf.update_prj_status())
    def test_proj_status_add(self, param, _status_storage, _alise_key):
        with step('获取 project_status key'):
            parm = conf.get_sys_status()[0]
            del parm.json['query']['must'][3]
            del parm.json['view'][1]
            parm.json['query']['must'].append({"in": {"context.type": ["project"]}})
            parm.json['query']['must'].append({"in": {"context.project_uuid": [ACCOUNT.project_uuid]}})

            resp = self.call(api.TeamView, parm)
            proj_key = resp.value('items[0].key')

            _alise_key |= {'proj_key': proj_key}

        with step('选择状态添加'):
            param.json_update('item.statuses', _alise_key['statuses'])
            param.uri_args({'item_key': proj_key})
            self.call(api.ItemUpdate, param)

    @story('138350 项目状态：移除项目状态')
    @parametrize('param', conf.update_prj_status())
    def test_proj_status_del(self, param, _status_storage, _alise_key):
        status_param = [s for s in _alise_key['statuses'] if s['built_in'] is True]

        param.json_update('item.statuses', status_param)
        param.uri_args({'item_key': _alise_key['proj_key']})
        self.call(api.ItemUpdate, param)

    @story('T131547 全局项目配置 - 项目状态：编辑自定义项目状态的状态名称')
    @parametrize('param', conf.update_prj_status())
    def test_edit_edit_status_name(self, param, _status_storage):
        """"""
        update = api.ItemUpdate()
        for s in _status_storage['statuses']:
            if s['name'] == 'Running':
                s['name'] = 'NewRunning'
        param.json['item']['statuses'] = _status_storage['statuses']

        param.uri_args({'item_key': _status_storage['key']})

        update.call(param.json, **param.extra)
        update.is_response_code(200)

        _status_storage = update.json()['item']

    @story('T131546 全局项目配置 - 项目状态：编辑自定义项目状态的状态类型')
    @parametrize('param', conf.add_field('text'))
    def test_edit_edit_status_type(self, param, _status_storage):
        """"""
        update = api.ItemUpdate()
        for s in _status_storage['statuses']:
            if s['name'] == 'NewRunning':
                s['name'] = 'TodoStatus'
                s['type'] = 'to_do'
        param.json['item']['statuses'] = _status_storage['statuses']

        param.uri_args({'item_key': _status_storage['key']})

        update.call(param.json, **param.extra)
        update.is_response_code(200)

        _status_storage = update.json()['item']
