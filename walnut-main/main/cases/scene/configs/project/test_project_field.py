#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_project_field.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/4 
@Desc    ： 全局配置-项目配置-属性测试用例
"""
import time

from falcons.check import Checker
from falcons.com.nick import feature, story, parametrize, fixture
from falcons.helper import mocks

from main.api import project as api
from main.params import conf


@fixture(scope='module')
def _field_storage():
    """
    主要是记录key 用于清理测试数据
    :return:
    """
    return {}


@fixture(scope='module')
def _alias_key():
    """
    :return:
    """
    return []


@fixture(scope='module', autouse=True)
def _new_field(_field_storage):
    """
    :return:
    """
    print('Add test field....')
    p = conf.add_options()[0]
    d = api.ItemsAdd()
    d.call(p.json, **p.extra)
    d.is_response_code(200)

    _field_storage.update(d.json()['item'])


@feature('项目配置-全局配置-项目')
class TestManageField(Checker):

    @story('T117562 编辑项目属性：编辑属性名称')
    @parametrize('param', conf.add_field('text'))
    def test_edit_field_name(self, param, _field_storage):
        """"""

        param.json = {'item': _field_storage}
        n = mocks.random_string()
        param.json['item']['name'] = n
        param.uri_args({'item_key': _field_storage['key']})
        resp = self.call(api.ItemUpdate, param)

        resp.check_response('item.name', param.json['item']['name'])

    @story('T117564 编辑项目属性：编辑属性选项值')
    @parametrize('param', conf.add_field('text'))
    def test_edit_field_option(self, param, _field_storage):
        """"""

        param.json = {'item': _field_storage}
        options = param.json['item']['options']
        tmp = options[0]

        options[0] = options[1]
        options[1] = tmp
        param.uri_args({'item_key': _field_storage['key']})

        resp = self.call(api.ItemUpdate, param)
        resp.check_response('item.options[0].uuid', param.json['item']['options'][0]['uuid'])

    @story('T138322 项目属性：删除自定义项目属性（已经被项目使用）')
    @parametrize('param', conf.delete_field())
    def test_delete_field_inuse(self, param, _field_storage, _alias_key):
        """"""
        # Use field in configs
        f_param = conf.add_field_to_project()[0]
        f_param.json['item']['aliases'] = _field_storage['aliases']

        add = self.call(api.ItemsAdd, f_param)
        # Storage alias key
        _alias_key.append(add.json()['item']['key'])

        param.uri_args({'item_key': _field_storage['key']})

        delete = self.call(api.ItemDelete, param, status_code=400)
        delete.check_response('type', 'InUse')

    @story('T138321 项目属性：删除自定义项目属性（没有被项目使用）')
    @parametrize('param', conf.delete_field())
    def test_delete_field_unused(self, param, _field_storage, _alias_key):
        """"""

        print(f'Issue key: {_alias_key}')
        if _alias_key:  # Delete field in configs first

            param.uri_args({'item_key': _alias_key[0]})
            self.call(api.ItemDelete, param)

        time.sleep(1)
        param.uri_args({'item_key': _field_storage['key']})
        self.call(api.ItemDelete, param)

    @story('T138337 项目属性：项目属性列表')
    @parametrize('param', conf.view_product())
    def test_project_field_list(self, param):
        """"""

        self.call(api.ItemsView, param)
