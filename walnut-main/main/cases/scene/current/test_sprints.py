#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_sprints.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/14 
@Desc    ：迭代场景测试用例
"""

from falcons.com.nick import feature, story, fixture, parametrize, step, mark

from main.api.sprint import SprintAdd, SprintStatusUpdate, SprintDelete
from main.params import proj


@fixture(scope='class')
def _storage():
    """"""
    p = {}
    return p


@mark.smoke
@feature('迭代概览')
class TestSprints:
    """测试迭代"""

    @story('更新迭代状态')
    @parametrize('param', proj.sprint_add())
    def test_sprint_add(self, param, _storage):
        spt_add = SprintAdd()
        p1 = proj.sprint_add()[0]
        spt_add.call(p1.json, **p1.extra)
        spt_add.is_response_code(200)

        sprint = spt_add.json()['sprints'][0]

        sprint_uuid = sprint['uuid']
        sprint_statuses = sprint['statuses']
        _storage |= {'sprint_uuid': sprint_uuid, 'statuses': sprint_statuses}

    @story('更新迭代状态')
    @parametrize('param', proj.sprint_status())
    def test_update_sprint_status(self, param, _storage):
        sprint_statuses = _storage['statuses']

        step_name, p = param
        p.uri_args({'sprint_uuid': _storage['sprint_uuid']})
        for sp in sprint_statuses:
            for x in p.json['sprint_statuses']:
                if x['category'] == sp['category']:
                    x['status_uuid'] = sp['status_uuid']

        with step(step_name):
            spt_update = SprintStatusUpdate()
            # 调用接口
            spt_update.call(p.json, **p.extra)
            # 检查接口响应码
            spt_update.is_response_code(200)

    @story('删除迭代')
    @parametrize('param', proj.sprint_delete())
    def test_sprint_delete(self, param, _storage):
        with step('Delete Sprint'):
            spt_delete = SprintDelete()
            param.uri_args({'sprint_uuid': _storage['sprint_uuid']})
            spt_delete.call(**param.extra)
            spt_delete.is_response_code(200)
