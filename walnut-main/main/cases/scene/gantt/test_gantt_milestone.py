#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_gantt_milestone.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/28 
@Desc    ：甘特图里程碑的操作用例
"""
from falcons.com.nick import feature, story, parametrize, fixture

from main.api import project as prj
from main.params import plan


@fixture(scope='module', autouse=True)
def _gantt():
    """
    用于测试的甘特图
    :return:
    """
    print('New gantt....')
    g_param = plan.create_gantt()[0]
    gan_add = prj.ItemsAdd()
    gan_add.call(g_param.json, **g_param.extra)
    gan_add.is_response_code(200)

    return gan_add.json()['item']


@fixture(scope='module')
def _milestone():
    """
    里程碑信息
    eg:
      {
        "assign": "2gxf3b4H",
        "create_time": 1640678752,
        "gantt_chart_uuid": "NH53XMAw",
        "gantt_data_type": "milestone",
        "item_type": "gantt_data",
        "key": "gantt_data-YEdqXUtw",
        "name": "new milestone",
        "name_pinyin": "new milestone",
        "owner": "7tMnkPmX",
        "parent": "",
        "path": "YEdqXUtw",
        "plan_end_time": 1640664000,
        "plan_start_time": 1640664000,
        "position": 400000,
        "progress": 0,
        "uuid": "YEdqXUtw"
      }

    :return:
    """
    return []


@fixture(scope='module', autouse=True)
def _clean_gantt(_gantt):
    """
    用于测试的甘特图
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
class TestGanttMilestone:
    @story('T22862 里程碑管理：新建里程碑')
    @parametrize('param', plan.create_milestone())
    def test_create_milestone(self, param, _gantt, _milestone):
        """"""
        param.json['item']['gantt_chart_uuid'] = _gantt['uuid']
        gan_add = prj.ItemsAdd()
        gan_add.call(param.json, **param.extra)
        gan_add.is_response_code(200)
        _milestone.append(gan_add.json()['item'])

    @story('T22863 更新里程碑信息')
    @parametrize('param', plan.update_milestone())
    def test_update_milestone(self, param, _gantt, _milestone):
        """"""
        param.json['item']['gantt_chart_uuid'] = _gantt['uuid']
        param.json['item']['uuid'] = _milestone[0]['uuid']
        param.uri_args({'item_key': _milestone[0]['key']})
        gan_update = prj.ItemUpdate()
        gan_update.call(param.json, **param.extra)
        gan_update.is_response_code(200)

        gan_update.check_response('item.name', param.json['item']['name'])
        gan_update.check_response('item.progress', param.json['item']['progress'])
        _milestone[0] = gan_update.json()['item']  # Store new milestone info

    @story('T22865 将里程碑转化为任务')
    @parametrize('param', plan.milestone_to_task())
    def test_milestone_to_task(self, param, _gantt, _milestone):
        """"""

        # new milestone
        p1 = plan.create_milestone()[0]
        p1.json['item']['gantt_chart_uuid'] = _gantt['uuid']
        gan_add = prj.ItemsAdd()
        gan_add.call(p1.json, **p1.extra)
        gan_add.is_response_code(200)
        item = gan_add.json()['item']
        param.uri_args({'item_key': item['key']})
        gan_update = prj.ItemUpdate()
        gan_update.call(param.json, **param.extra)
        gan_update.is_response_code(200)

        _milestone.append(item)

    @story('T22868 删除里程碑')
    @parametrize('param', plan.delete_item())
    def test_delete_milestone(self, param, _milestone):
        """"""

        gan_delete = prj.ItemDelete()
        for t in _milestone:
            param.uri_args({'item_key': t['key']})
            gan_delete.call(param.json, **param.extra)
            gan_delete.is_response_code(200)
