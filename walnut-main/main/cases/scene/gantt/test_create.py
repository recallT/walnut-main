#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_config.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/24 
@Desc    ：甘特图测试用例
"""

from falcons.check import Checker
from falcons.com.nick import feature, story, parametrize, fixture

from main.api import project as prj
from main.params import plan


@fixture(scope='module')
def _gan_storage():
    """
    eg:
        {
          "item": {
            "create_time": 1640671442,
            "import_config": {
              "projects": []
            },
            "item_type": "gantt_chart",
            "key": "gantt_chart-5aHNoJq2",
            "name": "Gantt-kmLZ",
            "name_pinyin": "Gantt-kmLZ",
            "owner": "7tMnkPmX",
            "shared": false,
            "sync_from_project": true,
            "sync_to_project": true,
            "uuid": "5aHNoJq2"
          }
        }
    :return:
    """
    return []


@feature('甘特图')
class TestGanttCreate(Checker):
    @story('T22825 新建甘特图：不选择数据源')
    @parametrize('param', plan.create_gantt())
    def test_create_gan_no_project(self, param, _gan_storage):
        """"""
        param.json['item']['import_config']['projects'] = []  # 不选择数据源

        gan_add = self.call(prj.ItemsAdd, param)
        gan_add.check_response('item.name', param.json['item']['name'])

        _gan_storage.append(gan_add.json())

    @story('T22828 新建甘特图：选择数据源来自ONES Project')
    @parametrize('param', plan.create_gantt())
    def test_add_gant_with_project(self, param, _gan_storage):
        """"""

        gan_add = self.call(prj.ItemsAdd, param)
        gan_add.check_response('item.name', param.json['item']['name'])

        _gan_storage.append(gan_add.json())

    # @story('同步设置：甘特图数据还原到ONES Project')
    # @parametrize('param', plan.gantt_sync_to_proj())
    # def test_gant_sync_project(self, param, _gan_storage):
    #     """"""
    #
    #     gan_add = prj.ItemUpdate()
    #     gan_add.call(param.json, **param.extra)
    #     gan_add.is_response_code(200)

    @story('T22883 同步设置：甘特图数据同步到ONES Project')
    @parametrize('param', plan.gantt_sync_to_proj())
    def test_gant_sync_project(self, param, _gan_storage):
        """"""

        g_uuid = _gan_storage[0]['item']['uuid']
        # 先在甘特图下创建一个任务，用于同步
        a_param = plan.create_task()[0]
        a_param.json['item']['gantt_chart_uuid'] = g_uuid

        gan_add = self.call(prj.ItemsAdd, a_param)
        task_uuid = gan_add.json()['item']['uuid']

        param.json['uuids'] = [task_uuid, ]
        param.uri_args({'gantt_uuid': g_uuid})

        self.call(prj.GanttSync, param)

    @story('T22900 同步设置：同步到「ONES Project」功能开关')
    @story('T22899 同步设置：自动更新导入的项目和迭代')
    @parametrize('param', plan.gantt_close_sync())
    def test_close_sync(self, param, _gan_storage):
        """"""
        g_uuid = _gan_storage[0]['item']['uuid']
        g_key = _gan_storage[0]['item']['key']
        param.json['item']['uuid'] = g_uuid
        param.uri_args({'item_key': g_key})

        gan_update = self.call(prj.ItemUpdate, param)
        gan_update.check_response('item.sync_to_project', False)

    @story('T22894 甘特图名称：修改甘特图名称')
    @parametrize('param', plan.update_gantt())
    def test_modify_gantt_name(self, param, _gan_storage):
        """"""
        item = _gan_storage[0]['item']
        param.json['item']['uuid'] = item['uuid']
        param.uri_args({'item_key': item['key']})

        gan_update = self.call(prj.ItemUpdate, param)
        gan_update.check_response('item.name', param.json['item']['name'])

        _gan_storage[0] = gan_update.json()

    @story('T23720 可见范围：修改甘特图可见范围为共享')
    @parametrize('param', plan.share_gantt())
    def test_share_gantt(self, param, _gan_storage):
        """"""
        item = _gan_storage[0]['item']
        param.json['item']['uuid'] = item['uuid']
        param.uri_args({'item_key': item['key']})

        gan_update = self.call(prj.ItemUpdate, param)
        gan_update.check_response('item.name', param.json['item']['name'])
        gan_update.check_response('item.shared', True)

        _gan_storage[0] = gan_update.json()

    @story('T22895 可见范围：修改甘特图可见范围为私人')
    @parametrize('param', plan.private_gantt())
    def test_private_gantt(self, param, _gan_storage):
        """"""
        item = _gan_storage[0]['item']
        param.json['item']['uuid'] = item['uuid']
        param.uri_args({'item_key': item['key']})

        gan_update = self.call(prj.ItemUpdate, param)

        gan_update.check_response('item.name', param.json['item']['name'])
        gan_update.check_response('item.shared', False)

        _gan_storage[0] = gan_update.json()

    @story('T22898 删除甘特图')
    @parametrize('param', plan.delete_item())
    def test_delete_gantt(self, param, _gan_storage):
        """"""
        gantt_keys = [g['item']['key'] for g in _gan_storage]
        gan_add = prj.ItemDelete()

        for key in gantt_keys:
            param.uri_args({'item_key': key})
            gan_add.call(param.json, **param.extra)
            gan_add.is_response_code(200)
            gan_add.check_response('code', 200)
