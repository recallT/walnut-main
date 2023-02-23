#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_gantt_group.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/28 
@Desc    ：甘特图分组操作用例
"""
from falcons.com.nick import feature, story, parametrize, fixture

from main.api import project as prj
from main.params import plan


@fixture(scope='module', autouse=True)
def _gantt():
    """
    创建用于测试的甘特图
    :return:
    """
    print('New Gantt....')
    g_param = plan.create_gantt()[0]
    gan_add = prj.ItemsAdd()
    gan_add.call(g_param.json, **g_param.extra)
    gan_add.is_response_code(200)

    return gan_add.json()['item']


@fixture(scope='module')
def _group():
    """
    分组信息
    eg:
      {
        "assign": null,
        "create_time": 1640676724,
        "gantt_chart_uuid": "NH53XMAw",
        "gantt_data_type": "group",
        "item_type": "gantt_data",
        "key": "gantt_data-9aPVggSx",
        "name": "new group",
        "name_pinyin": "new group",
        "owner": "7tMnkPmX",
        "parent": "",
        "path": "9aPVggSx",
        "plan_end_time": 57599,
        "plan_start_time": -28800,
        "position": 200000,
        "progress": 0,
        "uuid": "9aPVggSx"
      }

    :return:
    """
    return []


@fixture(scope='module', autouse=True)
def _clean_gantt(_gantt):
    """
    删除用于测试的甘特图
    :return:
    """
    yield
    print('Delete gantt....')
    g_param = plan.delete_item()[0]
    g_param.uri_args({'item_key': _gantt['key']})
    gan_add = prj.ItemDelete()
    gan_add.call(g_param.json, **g_param.extra)
    gan_add.is_response_code(200)


@feature('甘特图')
class TestGanttGroup:
    @story('T22856 分组管理：新建分组')
    @parametrize('param', plan.create_group())
    def test_create_group(self, param, _gantt, _group):
        """"""
        param.json['item']['gantt_chart_uuid'] = _gantt['uuid']
        gan_add = prj.ItemsAdd()
        gan_add.call(param.json, **param.extra)
        gan_add.is_response_code(200)
        _group.append(gan_add.json()['item'])

    @story('T22857 更新分组信息')
    @parametrize('param', plan.update_group())
    def test_update_group(self, param, _gantt, _group):
        """"""
        param.json['item']['gantt_chart_uuid'] = _gantt['uuid']
        param.json['item']['uuid'] = _group[0]['uuid']
        param.uri_args({'item_key': _group[0]['key']})
        gan_update = prj.ItemUpdate()
        gan_update.call(param.json, **param.extra)
        gan_update.is_response_code(200)

        gan_update.check_response('item.name', param.json['item']['name'])
        _group[0] = gan_update.json()['item']  # store new task info

    @story('T22858 将分组转化为任务')
    @parametrize('param', plan.group_to_task())
    def test_group_to_task(self, param, _gantt, _group):
        """"""

        # new group
        p1 = plan.create_group()[0]
        p1.json['item']['gantt_chart_uuid'] = _gantt['uuid']
        gan_add = prj.ItemsAdd()
        gan_add.call(p1.json, **p1.extra)
        gan_add.is_response_code(200)
        item = gan_add.json()['item']
        param.uri_args({'item_key': item['key']})
        gan_update = prj.ItemUpdate()
        gan_update.call(param.json, **param.extra)
        gan_update.is_response_code(200)

        _group.append(item)

    @story('T22850 将分组转化为里程碑')
    @parametrize('param', plan.group_to_milestone())
    def test_group_to_milestone(self, param, _gantt, _group):
        """"""

        p1 = plan.create_group()[0]
        p1.json['item']['gantt_chart_uuid'] = _gantt['uuid']
        gan_add = prj.ItemsAdd()
        gan_add.call(p1.json, **p1.extra)
        gan_add.is_response_code(200)
        item = gan_add.json()['item']

        param.uri_args({'item_key': item['key']})
        gan_update = prj.ItemUpdate()
        gan_update.call(param.json, **param.extra)
        gan_update.is_response_code(200)

        _group.append(item)

    @story('T22860 删除分组')
    @parametrize('param', plan.delete_item())
    def test_delete_group(self, param, _group):
        """"""

        gan_delete = prj.ItemDelete()
        for t in _group:
            param.uri_args({'item_key': t['key']})
            gan_delete.call(param.json, **param.extra)
            gan_delete.is_response_code(200)
