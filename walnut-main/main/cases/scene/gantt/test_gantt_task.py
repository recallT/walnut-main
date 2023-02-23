#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_gantt_task.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/28 
@Desc    ：甘特图向下的操作用例
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
def _task():
    """
    任务信息
    eg:
      {
        "assign": null,
        "create_time": 1640673729,
        "gantt_chart_uuid": "NH53XMAw",
        "gantt_data_type": "task",
        "item_type": "gantt_data",
        "key": "gantt_data-D94hRbSX",
        "name": "test task",
        "name_pinyin": "test task",
        "owner": "7tMnkPmX",
        "parent": "",
        "path": "D94hRbSX",
        "plan_end_time": 1640707199,
        "plan_start_time": 1640620800,
        "position": 100000,
        "progress": 0,
        "uuid": "D94hRbSX"
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
class TestGanttTask:
    @story('T22846 任务管理：新建任务')
    @parametrize('param', plan.create_task())
    def test_create_task(self, param, _gantt, _task):
        """"""
        param.json['item']['gantt_chart_uuid'] = _gantt['uuid']
        gan_add = prj.ItemsAdd()
        gan_add.call(param.json, **param.extra)
        gan_add.is_response_code(200)
        _task.append(gan_add.json()['item'])
        print(f"First task : {gan_add.json()['item']}")

    @story('T22885 快速新建子节点对象：新建任务')
    @parametrize('param', plan.create_task())
    def test_create_sub_task(self, param, _gantt, _task):
        """"""
        param.json['item']['gantt_chart_uuid'] = _gantt['uuid']
        param.json['item']['parent'] = _task[0]['uuid']

        gan_add = prj.ItemsAdd()
        gan_add.call(param.json, **param.extra)
        gan_add.is_response_code(200)

    @story('T22887 快速新建子节点对象：新建分组')
    @parametrize('param', plan.create_group())
    def test_create_sub_group(self, param, _gantt, _task):
        """"""
        param.json['item']['gantt_chart_uuid'] = _gantt['uuid']
        param.json['item']['parent'] = _task[0]['uuid']

        gan_add = prj.ItemsAdd()
        gan_add.call(param.json, **param.extra)
        gan_add.is_response_code(200)

    @story('T22886 快速新建子节点对象：新建里程碑')
    @parametrize('param', plan.create_milestone())
    def test_create_sub_milestone(self, param, _gantt, _task):
        """"""
        param.json['item']['gantt_chart_uuid'] = _gantt['uuid']
        param.json['item']['parent'] = _task[0]['uuid']

        gan_add = prj.ItemsAdd()
        gan_add.call(param.json, **param.extra)
        gan_add.is_response_code(200)

    @story('T22847 更新任务信息')
    @parametrize('param', plan.update_task())
    def test_update_task(self, param, _gantt, _task):
        """"""
        param.json['item']['gantt_chart_uuid'] = _gantt['uuid']
        param.json['item']['uuid'] = _task[0]['uuid']
        param.uri_args({'item_key': _task[0]['key']})
        gan_update = prj.ItemUpdate()
        gan_update.call(param.json, **param.extra)
        gan_update.is_response_code(200)

        gan_update.check_response('item.name', param.json['item']['name'])
        gan_update.check_response('item.progress', param.json['item']['progress'])

        _task[0] = gan_update.json()['item']  # Store new task info

    @story('T22849 将任务转化为分组')
    @parametrize('param', plan.task_to_group())
    def test_task_to_group(self, param, _gantt, _task):
        """"""

        # new task
        p1 = plan.create_task()[0]
        p1.json['item']['gantt_chart_uuid'] = _gantt['uuid']
        gan_add = prj.ItemsAdd()
        gan_add.call(p1.json, **p1.extra)
        gan_add.is_response_code(200)
        item = gan_add.json()['item']
        param.uri_args({'item_key': item['key']})
        gan_update = prj.ItemUpdate()
        gan_update.call(param.json, **param.extra)
        gan_update.is_response_code(200)
        print(f' Now task is : {item}')
        # _task.append(item)

    @story('T22850 将任务转化为里程碑')
    @parametrize('param', plan.task_to_milestone())
    def test_task_to_milestone(self, param, _gantt, _task):
        """"""

        p1 = plan.create_task()[0]
        p1.json['item']['gantt_chart_uuid'] = _gantt['uuid']
        gan_add = prj.ItemsAdd()
        gan_add.call(p1.json, **p1.extra)
        gan_add.is_response_code(200)
        item = gan_add.json()['item']

        param.uri_args({'item_key': item['key']})
        gan_update = prj.ItemUpdate()
        gan_update.call(param.json, **param.extra)
        gan_update.is_response_code(200)

        print(f' Now task is : {item}')
        # _task.append(item)

    @story('T22852 删除任务')
    @parametrize('param', plan.delete_item())
    def test_delete_task(self, param, _task):
        """"""

        gan_delete = prj.ItemDelete()
        for t in _task:
            param.uri_args({'item_key': t['key']})
            gan_delete.call(param.json, **param.extra)
            gan_delete.is_response_code(200)
