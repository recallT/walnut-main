#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_filed.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/7 
@Desc    ：添加自定义属性测试案例
"""

from falcons.com.nick import parametrize, feature, fixture, story, mark
from falcons.helper import mocks

from main.api.project import FieldsAdd, FieldDelete, FieldUpdate
from main.params import data


@fixture(scope='module')
def _storage():
    """用于存储案例间共享的数据"""
    p = []
    return p


@feature('全局属性相关接口')
class TestProjectsField:
    @mark.smoke
    @story('添加全局属性')
    @parametrize('param', data.fields_add())
    def test_field_add(self, param, _storage):
        """添加全局属性"""

        field = FieldsAdd()

        field.call(param.json, **param.extra)
        # # 检查接口响应码
        field.is_response_code(200)
        # 缓存field 所有字段
        _storage.append(field.json()['field'])
        field.check_response('field.name', param.json['field']['name'])
        field.check_response('field.type', param.json['field']['type'])

    @story('添加全局属性-Name Too Long')
    @parametrize('param', data.fields_add()[:1])
    def test_field_add_name_too_long(self, param, _storage):
        """添加全局属性"""

        field = FieldsAdd()
        param.json['field']['name'] = param.json['field']['name'] * 3
        field.call(param.json, **param.extra)
        # # 检查接口响应码
        field.is_response_code(801)

    @story('添加全局属性-Invalid Type')
    @parametrize('param', data.fields_add()[:1])
    def test_field_add_name_invalid_type(self, param, _storage):
        """添加全局属性"""

        field = FieldsAdd()
        param.json['field']['type'] = 800
        field.call(param.json, **param.extra)
        # # 检查接口响应码
        field.is_response_code(801)

    @story('更新全局属性')
    @parametrize('param', data.field_update())
    def test_field_update(self, param, _storage):
        """更新全局属性"""

        field = FieldUpdate()
        for s in _storage:
            _new = {'name': f'{s["name"]}-New',
                    'type': s['type'],
                    'uuid': s['uuid'],
                    }
            if len(_new['name']) > 30:
                _new['name'] = _new['name'][:8] + mocks.ones_uuid()

            param.uri_args({'field_uuid': s['uuid']})
            param.json['field'] |= _new
            field.call(param.json, **param.extra)
            field.is_response_code(200)

            field.check_response('field.name', _new['name'])

    @mark.smoke
    @story('删除全局属性')
    @parametrize('param', data.field_delete())
    def test_field_delete(self, param, _storage):
        """删除全局属性"""

        field = FieldDelete()
        for s in _storage:
            param.uri_args({'field_uuid': s['uuid']})
            field.call(**param.extra)
            # 检查接口响应码
            field.is_response_code(200)
