#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_project_role.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/4 
@Desc    ： 全局配置-项目配置-项目角色测试用例
"""
from falcons.com.nick import feature, story, parametrize, fixture, step

from main.api import project as api
from main.params import conf


@fixture(scope='module')
def _role_storage():
    """
    主要是记录项目角色 用于清理测试数据
    :return:
    """
    return {}


@fixture(scope='module', autouse=True)
def _clear_role(_role_storage):
    """
    清理测试角色
    :return:
    """
    yield
    print('Delete role')
    p = conf.delete_field()[0]
    role_uuid = _role_storage['uuid']
    p.uri_args({'role_uuid': role_uuid})
    delete = api.RoleDelete()
    delete.call(**p.extra)
    delete.is_response_code(200)


@feature('项目配置-全局配置-项目')
class TestProjectRole:

    @story('T137958 项目角色：新建角色')
    @parametrize('param', conf.role_add())
    def test_add_role(self, param, _role_storage):
        """"""

        role_add = api.RolesAdd()
        role_add.call(param.json, **param.extra)
        role_add.is_response_code(200)
        role_add.check_response('role.name', param.json['role']['name'])
        _role_storage |= role_add.json()['role']

    @story('T137947 项目角色：检查列表系统角色的表现')
    @parametrize('param', conf.role_configs())
    def test_role_list(self, param, _role_storage):
        """"""
        stamps = api.TeamStampData()
        stamps.call(param.json, **param.extra)
        stamps.is_response_code(200)
        roles = [r['uuid'] for r in stamps.json()['role']['roles']]

        assert _role_storage['uuid'] in roles, '未查到新建的角色信息'

    @story('T137959 项目角色：重命名自定义项目角色（未被项目添加）')
    @parametrize('param', conf.update_role())
    def test_role_update_unused(self, param, _role_storage):
        """"""
        param.json['role']['uuid'] = _role_storage['uuid']
        param.uri_args({'role_uuid': _role_storage['uuid']})

        update = api.RoleUpdate()
        update.call(param.json, **param.extra)
        update.is_response_code(200)
        update.check_response('role.name', param.json['role']['name'])

    @story('T137960 项目角色：重命名自定义项目角色（已被项目添加）')
    @parametrize('param', conf.role_add())
    def test_role_update_inuse(self, param, _role_storage):
        """"""
        with step('添加角色到项目'):
            r_a = conf.project_roles_add()[0]
            a = api.ProjectRoleAdd()
            r_a.json['role_uuids'].append(_role_storage['uuid'])
            a.call(r_a.json, **r_a.extra)
            a.is_response_code(200)

        param.json['role']['uuid'] = _role_storage['uuid']
        param.uri_args({'role_uuid': _role_storage['uuid']})

        update = api.RoleUpdate()
        update.call(param.json, **param.extra)
        update.is_response_code(200)
        update.check_response('role.name', param.json['role']['name'])

        with step('移除项目内角色'):
            r_a = conf.project_roles_add()[0]
            d = api.ProjectRoleDelete()
            r_a.uri_args({'role_uuid': _role_storage['uuid']})
            d.call(r_a.json, **r_a.extra)
            d.is_response_code(200)
