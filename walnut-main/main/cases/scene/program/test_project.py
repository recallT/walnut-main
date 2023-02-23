#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_project.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/28 
@Desc    ：
"""
from falcons.com.nick import story, parametrize, fixture, feature

from main.actions.pro import PrjAction
from main.api import project as pj
from main.params import proj


@fixture(scope='session', autouse=True)
def fx_program():
    """用于测试的项目集"""
    p = proj.add_program()[0]
    ia = pj.ItemsAdd()
    ia.call(p.json, **p.extra)
    ia.is_response_code(200)
    # {
    #   "item": {
    #     "item_type": "program",
    #     "key": "program-DqRFPErm",
    #     "uuid": "DqRFPErm"
    #   }
    # }
    s = ia.json()['item']
    s |= {'name': p.json["item"]["name"]}
    print(f'Create test plan :{s["name"]} : {s["uuid"]}')

    # 单独创建2个用于测试的项目
    projects = []
    for i in range(2):
        p_id = PrjAction.new_project()
        projects.append(p_id)
    print({'program': s, 'projects': projects})
    yield {'program': s, 'projects': projects}

    # 删除用于测试的项目集
    print(f'Delete test plan: {s["name"]}')
    del_param = proj.delete_program()[0]
    del_param.uri_args({'item_key': s['key']})
    del_item = pj.ItemDelete()
    del_item.call(**del_param.extra)
    del_item.is_response_code(200)

    # 删除项目
    if projects:
        for p_uuid in projects:
            PrjAction.delete_project(p_uuid)


@feature('项目集')
class TestProgramsProject:
    """项目集添加项目"""

    @story('项目集-添加项目')
    @parametrize('param', proj.program_add_project())
    def test_program_project_add(self, param, fx_program):
        """"""

        param.json['items'][0] |= {'parent': fx_program['program']['uuid'], 'project': fx_program['projects'][0]}
        item_add = pj.ItemBatchAdd()
        item_add.call(param.json, **param.extra)
        item_add.is_response_code(200)

    @story('23053 项目集-批量添加项目')
    @parametrize('param', proj.program_add_project())
    def test_program_project_add_batch(self, param, fx_program):
        """"""

        p = []
        for c in fx_program['projects'][1:]:
            p.append({
                'item_type': 'program',
                'parent': fx_program['program']['uuid'],  # 项目集UUID
                'related_type': 'project',
                'project': c  # 项目UUID
            })
        param.json['items'] = p
        item_add = pj.ItemBatchAdd()
        item_add.call(param.json, **param.extra)
        item_add.is_response_code(200)

    @story('项目集-删除项目')
    @parametrize('param', proj.program_delete_project())
    def test_program_project_delete(self, param, fx_program):
        """"""
        # 拉取测试集信息先
        gq_param = proj.list_program()[0]
        gq_param.json['variables']['filter']['ancestors_in'].append(fx_program['program']['uuid'])
        gq = pj.ItemGraphql()
        gq.call(gq_param.json, **gq_param.extra)
        projects = [{'key': d['key'], 'name': d['name']} for d in gq.json()['data']['programs'] if
                    d['relatedType'] == 'project']
        if projects:
            param.json['keys'] = [projects[0]['key'], ]
            item_delete = pj.ItemsBatchDelete()
            item_delete.call(param.json, **param.extra)
            item_delete.is_response_code(200)

    @story('23051 项目集-批量删除项目')
    @parametrize('param', proj.program_delete_project())
    def test_program_project_delete_batch(self, param, fx_program):
        """"""

        gq_param = proj.list_program()[0]
        gq_param.json['variables']['filter']['ancestors_in'].append(fx_program['program']['uuid'])
        gq = pj.ItemGraphql()
        gq.call(gq_param.json, **gq_param.extra)
        projects = [{'key': d['key'], 'name': d['name']} for d in gq.json()['data']['programs'] if
                    d['relatedType'] == 'project']
        if projects:
            param.json['keys'] = [p['key'] for p in projects]
            item_delete = pj.ItemsBatchDelete()
            item_delete.call(param.json, **param.extra)
            item_delete.is_response_code(200)
