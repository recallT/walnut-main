#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_user_group.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/6 
@Desc    ：用户组接口测试用例
"""

from falcons.com.nick import parametrize, feature, fixture, story, mark
from falcons.helper.codes import RunSql

from main.api.project import (
    UsesGroupList,
    UsesGroupAdd,
    UsesGroupUpdate, UsesGroupDelete,
)
from main.params import data


@fixture(scope='class')
def _storage():
    """用于存储案例间共享的数据"""
    p = []

    return p


@fixture(autouse=True, scope='module')
def clean_group_db():
    """清除测试数据"""
    yield
    print('Clean user_group data.')
    r = RunSql()
    sql = """delete from {prefix}user_group where status='2' and name='New name Update';"""
    s = r.run(sql)
    print(f'{s} records deleted.')


@feature('用户组相关接口')
class TestUserGroup:
    @mark.smoke
    @story('创建用户组')
    @parametrize('param', data.user_group_add())
    def test_user_group_add(self, param, _storage):
        """创建用户组"""

        ug = UsesGroupAdd()

        ug.call(param.json, **param.extra)

        _storage.append(ug.json()['uuid'])  # Store user group uuid

        ug.is_response_code(200)
        ug.check_response('name', param.json['name'])

    @story('创建用户组')
    @parametrize('param', data.user_group_add())
    def test_user_group_add_fail(self, param, _storage):
        """创建用户组"""

        ug = UsesGroupAdd()
        param.json['name'] = ''  # no name
        ug.call(param.json, **param.extra)

        ug.is_response_code(801)

    @story('更新用户组')
    @parametrize('param', data.user_group_update())
    def test_user_group_update(self, param, _storage):
        """更新用户组"""

        ug = UsesGroupUpdate()

        # update uuid
        for uid in _storage:
            param.json['uuid'] = uid
            param.extra['uri_args']['group_uuid'] = uid
            ug.call(param.json, **param.extra)

            ug.is_response_code(200)

    @story('更新用户组')
    @parametrize('param', data.user_group_update())
    def test_user_group_update_404(self, param):
        """创建用户组"""

        ug = UsesGroupUpdate()
        param.json['uuid'] = 'fakeuuid'
        param.extra['uri_args']['group_uuid'] = 'fakeuuid'
        ug.call(param.json, **param.extra)

        ug.is_response_code(404)

    @mark.smoke
    @story('获取用户组列表')
    @parametrize('param', data.user_group_list())
    def test_user_group_list(self, param):
        """获取用户组列表"""

        ug = UsesGroupList()

        ug.call(**param.extra)
        ug.is_response_code(200)

    @story('141211 用户组列表：删除用户组')
    @parametrize('param', data.user_group_update())
    def test_user_group_delete(self, param, _storage):
        """删除用户组"""

        ug = UsesGroupDelete()
        for uid in _storage:
            param.extra['uri_args']['group_uuid'] = uid
            ug.call(**param.extra)
            ug.is_response_code(200)

    @story('删除用户组')
    @parametrize('param', data.user_group_update())
    def test_user_group_delete_404(self, param, _storage):
        """删除用户组"""

        ug = UsesGroupDelete()
        param.extra['uri_args']['group_uuid'] = 'empty'
        ug.call(**param.extra)
        ug.is_response_code(404)
