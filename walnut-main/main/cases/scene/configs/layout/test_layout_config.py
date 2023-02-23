#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_layout_config.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/6 
@Desc    ：全局配置-项目配置-视图配置测试用例
"""

from falcons.check import Checker, go
from falcons.com.nick import feature, story, fixture, step, parametrize

from main.api import project as prj, layout as lay, issue as i
from main.params import conf, issue
from . import add_layout, delete_layout

DEFAULT_FIELD = (
    'Android缺陷视图配置', '发布视图配置', '工单视图配置', 'iOS缺陷视图配置', '缺陷视图配置',
    '任务视图配置', 'Web缺陷视图配置', '需求视图配置', '用户故事视图配置', '子检查项视图配置', '子任务视图配置', '子需求视图配置',
)


@fixture(scope='module')
def _layout_storage():
    """
    记录内置工作项类型信息
    :return:
    """
    return []


@fixture(scope='module')
def _issue_uuid():
    return []


@fixture(scope='module', autouse=True)
def _clear_layout(_layout_storage, _issue_uuid):
    """

    :return:
    """
    yield
    if _layout_storage:
        for u in _layout_storage:
            delete_layout(u)

    # 清除自定义工作项
    if _issue_uuid:
        prm = issue.delete_issue()[0]
        prm.uri_args({'issue_uuid': _issue_uuid[0]})
        go(i.IssueDelete, prm)


@feature('项目配置-全局配置-视图配置')
class TestLayoutConfigList(Checker):

    @classmethod
    def get_layout_info(cls, param, token=None):
        graph = prj.ItemGraphql(token)
        graph.call(param.json, **param.extra)
        graph.is_response_code(200)
        issues = [g for g in graph.json()['data']['issueTypeLayouts']]

        return issues

    @story('135391 视图配置：开箱后视图配置列表检查')
    @parametrize('param', conf.layout_list())
    def test_check_default_layout_config(self, param):
        """"""
        issues = self.get_layout_info(param)
        with step('查看属性列表'):
            """"""

            check_view(DEFAULT_FIELD, issues)

    @story('135393 视图配置：新建工作项类型后检查视图配置列表')
    @parametrize('param', conf.layout_add())
    def test_check_layout_add(self, param, _layout_storage):
        """"""
        with step('添加一个新的视图'):
            new_layout = add_layout('工单')

            # 缓存视图UUID
            _layout_storage.append(new_layout['layout_uuid'])

        with step('检查视图配置列表'):
            """"""
            issues = self.get_layout_info(conf.layout_list()[0])
            check_view((new_layout['name'],), issues, built_in=False)

    @story('138967 新建视图配置：新建系统工作项类型视图配置')
    @parametrize('param', conf.layout_add())
    def test_system_issue_layout_add(self, param, _layout_storage):
        with step('选择工作项类型为：任务'):
            new_layout = add_layout('任务')

            _layout_storage.append(new_layout['layout_uuid'])

        with step('检查视图配置列表'):
            issues = self.get_layout_info(conf.layout_list()[0])
            check_view((new_layout['name'],), issues, built_in=False)

    @story('138966 新建视图配置：新建工作项类型，校验自动生成的视图配置')
    @parametrize('param', issue.add_standard_issue())
    def test_add_issue_check_layout(self, param, _issue_uuid):
        with step('新建自定义工作项类型'):
            resp = self.call(i.IssuesAdd, param)

            issue_uuid = resp.value('uuid')
            issue_name = resp.value('name')

            _issue_uuid.append(issue_uuid)

        with step('查看全局配置方案-视图配置'):
            parm = conf.layout_list()[0]
            res = self.call(prj.ItemGraphql, parm)

            layout_info = [d for d in res.value('data.issueTypeLayouts') if d['issueType']['uuid'] == issue_uuid][0]
            assert layout_info.get('name') == issue_name + '视图配置'

    @story('138968 新建视图配置：新建自定义工作项类型视图配置')
    @parametrize('param', conf.layout_add())
    def test_customize_issue_layout_add(self, param, _issue_uuid, _layout_storage):
        with step('选择工作项类型为：自定义类型'):
            param.json_update('issue_type_uuid', _issue_uuid[0])
            resp = self.call(lay.LayoutAdd, param)

            _layout_storage.append(resp.value('layout_uuid'))

    @story('119230 单独配置新建表单：发布配置校验')
    def test_push_config_check(self):
        """发布配置校验"""

    @story('119231 单独配置新建表单：快速配置默认值校验')
    @parametrize('param', conf.layout_draft_get())
    def test_layout_config_default_check(self, param, _layout_storage):
        param.uri_args({'layout_uuid': _layout_storage[0]})
        self.call(lay.LayoutDraftGet, param)

    @story('138970 新建视图：默认视图配置方案内容校验')
    @parametrize('param', conf.layout_draft_get())
    def test_default_layout_content_check(self, param, _layout_storage):
        param.uri_args({'layout_uuid': _layout_storage[0]})
        resp = self.call(lay.LayoutDraftGet, param)

        resp.check_response('data.sync_form_from_view', True)


def check_view(fields: tuple, store, built_in=True):
    """检查属性"""
    issue_names = [s['name'] for s in store if s['builtIn'] is built_in]
    err_ = []
    for k in fields:
        if k not in issue_names:
            err_.append(k)
    assert not err_, f'视图配置没找到{err_}'
