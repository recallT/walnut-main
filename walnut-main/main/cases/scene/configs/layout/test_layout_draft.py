#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_layout_draft.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/6 
@Desc    ：视图详情编辑-测试用例
"""

from falcons.com.nick import feature, story, fixture, step

from main.api import layout as lay
from main.api import project as prj
from main.cases.scene.configs.layout import add_layout, delete_layout
from main.params import conf


@fixture(scope='module')
def _sample_layout() -> dict:
    """
    创建测试视图

    :return:
    """
    new_layout = add_layout('任务')
    return new_layout


@feature('项目配置-全局配置-视图配置')
class TestEditLayout:

    @story('117523 编辑视图配置：设置属性默认值')
    def test_set_default_value(self, _sample_layout):
        """"""
        lay_uid = {'layout_uuid': _sample_layout['layout_uuid']}
        # 1. 获取草稿
        with step('获取草稿'):
            dg = conf.layout_draft_get()[0]
            dg.uri_args(lay_uid)

            draft = lay.LayoutDraftGet()
            draft.call(**dg.extra)
            draft_data = draft.json()['data']
        # 2. 编辑草稿 将 【描述】  field016  单行文本 添加默认值

        # 更新属性字段内容
        fs = conf.field_stamp()[0]
        stamps = prj.TeamStampData()
        stamps.call(fs.json, **fs.extra)
        fields = stamps.json()['field']['fields']
        for curr in draft_data['field_configs']:
            for v in fields:
                if curr['field_uuid'] == v['uuid']:
                    curr |= {'uuid': v['uuid'], 'options': v['options'], 'name': v['name'],
                             'name_pinyin': v['name_pinyin']}

        default_val = 'My Default Value'
        with step('设置属性默认值'):
            for f in draft_data['field_configs']:
                if f['field_uuid'] == 'field016':
                    f['default_value'] = default_val

            dg = conf.layout_draft_set()[0]
            dg.uri_args(lay_uid)
            dg.json['data'] = draft_data

            draft = lay.LayoutDraftSet()
            draft.call(dg.json, **dg.extra)
            draft_data_new = draft.json()['data']

        # 3. 检查草稿
        with step('检查默认设置成功'):
            val = [d['default_value'] for d in draft_data_new['field_configs'] if d['field_uuid'] == 'field016'][0]

            assert val == default_val, '默认值设置失败'

    @story('117524 编辑视图配置：设置属性为必填')
    def test_set_required(self, _sample_layout):
        """"""
        lay_uid = {'layout_uuid': _sample_layout['layout_uuid']}
        # 1. 获取草稿
        with step('获取草稿'):
            dg = conf.layout_draft_get()[0]
            dg.uri_args(lay_uid)

            draft = lay.LayoutDraftGet()
            draft.call(**dg.extra)
            draft_data = draft.json()['data']

        # 2. 编辑草稿 将 【描述】  field016  单行文本 设置为必填
        required = True
        with step('设置属性默认值'):
            for f in draft_data['field_configs']:
                if f['field_uuid'] == 'field016':
                    f['required'] = True

            dg = conf.layout_draft_set()[0]
            dg.uri_args(lay_uid)
            dg.json['data'] = draft_data

            draft = lay.LayoutDraftSet()
            draft.call(dg.json, **dg.extra)
            draft_data_new = draft.json()['data']

        # 3. 检查草稿
        with step('检查必填设置成功'):
            val = [d['required'] for d in draft_data_new['field_configs'] if d['field_uuid'] == 'field016'][0]

            assert val is required, '必填设置失败'

    @story('135331 删除视图配置：删除未在使用的视图配置方案')
    def test_delete_layout(self, _sample_layout):
        delete_layout(_sample_layout['layout_uuid'])
