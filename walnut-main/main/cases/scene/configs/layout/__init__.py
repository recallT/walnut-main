#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：__init__.py.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/6
@Desc    ：
"""
from falcons.check import go

from main.api import layout as lay
from main.api import project as prj
from main.params import conf


def add_layout(name):
    """
    创建视图

    :param name: 工作项类型名
    :return:
    """
    p = conf.issue_type_stamp()[0]
    g = go(prj.TeamStampData, p)

    #  获取工作项UUID
    issue_uuid = [t['uuid'] for t in g.json()['issue_type']['issue_types'] if t['name'] == name][0]

    param = conf.layout_add()[0]

    param.json['issue_type_uuid'] = issue_uuid
    layout_name = param.json['name']

    add = go(lay.LayoutAdd, param)

    return {'name': layout_name, 'layout_uuid': add.json()['layout_uuid']}


def delete_layout(uuid):
    """
    删除视图

    :param uuid:
    :return:
    """
    print('Delete layout...')
    p = conf.layout_delete()[0]
    p.uri_args({'layout_uuid': uuid})
    go(lay.LayoutDelete, p)
