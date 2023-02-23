#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_project_config.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/4 
@Desc    ： 全局配置-项目配置测试用例
"""
import time

from falcons.com.nick import feature, story, parametrize, fixture

from main.api import project as api
from main.params import conf


@fixture(scope='module')
def _field_store():
    """
    主要是记录key 用于清理测试数据
    :return:
    """
    return []


@fixture(scope='module', autouse=True)
def _clear_field(_field_store):
    """
    主要是记录key 用于清理测试数据
    :return:
    """
    yield
    print('Delete test field....')
    p = conf.add_options()[0]

    d = api.ItemDelete()

    def _delete(item_key):
        p.uri_args({'item_key': item_key})
        d.call(**p.extra)

    for c in _field_store:
        for i in range(10):
            print(f'Trying {i + 1}...')
            _delete(c['key'])
            if d.response.status_code == 200:
                break
            else:
                time.sleep(1)


@feature('项目配置-全局配置-项目')
class TestNewProjectField:
    @classmethod
    def go(cls, param, storage, code=200, token=None):
        add = api.ItemsAdd(token)
        add.call(param.json, **param.extra)
        add.is_response_code(code)
        if code == 200:
            add.check_response('item.name', param.json['item']['name'])

            storage.append(add.json()['item'])

    @story('T138971 新建项目属性：单行文本类型')
    @parametrize('param', conf.add_field('text'))
    def test_add_single_text(self, param, _field_store):
        """"""
        self.go(param, _field_store)

    @story('T138972 新建项目属性：单选菜单类型')
    @parametrize('param', conf.add_options())
    def test_add_single_menu(self, param, _field_store):
        """"""
        self.go(param, _field_store)

    @story('T138973 新建项目属性：单选成员类型')
    @parametrize('param', conf.add_field('user'))
    def test_add_user(self, param, _field_store):
        """"""
        self.go(param, _field_store)

    @story('T138974 新建项目属性：多行文本类型')
    @parametrize('param', conf.add_field('multi_line_text'))
    def test_add_multi_line_text(self, param, _field_store):
        """"""
        self.go(param, _field_store)

    @story('T138975 新建项目属性：多选菜单类型')
    @parametrize('param', conf.add_options('multi_option'))
    def test_add_textarea(self, param, _field_store):
        """"""
        self.go(param, _field_store)

    @story('T138976 新建项目属性：多选成员类型')
    @parametrize('param', conf.add_field('user_list'))
    def test_add_user_list(self, param, _field_store):
        """"""
        self.go(param, _field_store)

    @story('T138977 新建项目属性：浮点数类型')
    @parametrize('param', conf.add_field('float'))
    def test_add_float(self, param, _field_store):
        """"""
        self.go(param, _field_store)

    @story('T138978 新建项目属性：日期类型')
    @parametrize('param', conf.add_field('date'))
    def test_add_date(self, param, _field_store):
        """"""
        self.go(param, _field_store)

    @story('T138979 新建项目属性：时间类型')
    @parametrize('param', conf.add_field('time'))
    def test_add_time(self, param, _field_store):
        """"""
        self.go(param, _field_store)

    @story('T138982 新建项目属性：整数类型')
    @story('T138983 新建项目属性：支持添加属性类型')
    @parametrize('param', conf.add_field('integer'))
    def test_add_integer(self, param, _field_store):
        """"""
        self.go(param, _field_store)

    @story('T138980 新建项目属性：属性名称重名校验')
    @parametrize('param', conf.add_field('text'))
    def test_add_name_exists(self, param, _field_store):
        """"""
        param.json['item']['name'] = _field_store[0]['name']
        self.go(param, _field_store, code=409)  # 409 NameExists
