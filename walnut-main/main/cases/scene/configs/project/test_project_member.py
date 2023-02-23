#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_project_member.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/4 
@Desc    ：项目管理-成员管理用例
"""

from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, parametrize, fixture
from falcons.helper import mocks

from main.api import project as api
from main.helper.extra import Extra
from main.params import conf


@fixture(scope='module')
def _conf_storage():
    """
    主要是记录key 用于清理测试数据
    :return:
    """
    return []


@fixture(scope='module')
def _proj():
    """
    新建一个测试项目，用于测试成员管理及删除
    :return:
    """
    creator = Extra(ApiMeta)
    proj_uuid = creator.new_project(mocks.random_string().capitalize())

    return proj_uuid


@fixture(scope='module', autouse=True)
def _clear_proj(_proj):
    """
    用于清理测试项目
    :return:
    """
    yield
    print('Delete test project....')
    # delete = Init(ApiMeta.constant)
    # delete.del_project(_proj)


@feature('项目配置-全局配置-项目')
class TestProjectMemberConf:

    @story('T147984 项目管理-项目详情-管理项目：添加成员域（成员）')
    @parametrize('param', conf.add_member())
    def test_add_member_view_proj(self, param, _proj):
        """"""

    @story('T137877 项目管理-项目详情：删除项目')
    @parametrize('param', conf.delete_project())
    def test_delete_project(self, param, _proj):
        """"""
        d = api.DeleteProject()
        param.uri_args({'project_uuid': _proj})
        d.call(**param.extra)
        d.is_response_code(200)
