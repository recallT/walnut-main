#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_product_config.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/6 
@Desc    ：全局配置-项目管理配置-产品属性-测试用例
"""

from falcons.com.nick import feature, story, parametrize, fixture, mark

from main.api import project as api
from main.params import conf


@fixture(scope='module')
def _product_storage():
    """
    主要是记录key 用于清理测试数据
    :return:
    """
    return []


@mark.smoke
@feature('项目配置-全局配置-产品')
class TestProductConfig:

    @story('T118988 产品属性：开箱后产品属性列表检查')
    @parametrize('param', conf.view_product())
    def test_default_check(self, param):
        """"""
        default_field = '创建日期', '产品名称', '产品负责人', '产品创建人', '未开始工作项数', '工作项数', '已完成工作项数'

        view = api.TeamView()
        view.call(param.json, **param.extra)
        view.is_response_code(200)

        fields = [f['name'] for f in view.json()['items'] if f['built_in']]
        err_ = []
        for d in default_field:
            if d not in fields:
                err_.append(d)

        assert not err_, f'有未包含的系统产品属性{err_}'

    @story('T138519 新建产品属性（单行文本）')
    @parametrize('param', conf.add_product('text'))
    def test_add_single_text(self, param, _product_storage):
        """"""

        add = api.ItemsAdd()
        add.call(param.json, **param.extra)

        add.is_response_code(200)
        add.check_response('item.built_in', False)
        add.check_response('item.name', param.json['item']['name'])

        # Save product info
        _product_storage.append(add.json()['item'])

    @story('T117458 编辑产品属性：编辑单行文本属性')
    @parametrize('param', conf.update_product())
    def test_update_product_name(self, param, _product_storage):
        """"""
        param.uri_args({'item_key': _product_storage[0]['key']})

        update = api.ItemUpdate()
        update.call(param.json, **param.extra)

        update.is_response_code(200)
        update.check_response('item.built_in', False)
        update.check_response('item.name', param.json['item']['name'])

        # Update product info
        _product_storage = [(update.json()['item']), ]

    @story('T135314 删除产品属性：删除单行文本属性')
    @parametrize('param', conf.delete_product_field())
    def test_delete_product_field(self, param, _product_storage):
        """"""
        param.uri_args({'item_key': _product_storage[0]['key']})

        delete = api.ItemDelete()
        delete.call(param.json, **param.extra)

        delete.is_response_code(200)
