#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_issue_build_in.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/5 
@Desc    ：全局配置-系统工作项用例
"""

from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture, step, mark

from main.api import project as prj
from main.params import issue as ise

DEFAULT_FIELD = (
    '截止日期', '所属功能模块', '所属产品', '计划完成日期', '计划开始日期', '关联发布', '标题', '创建者', '负责人',
    '状态', '所属项目', '工作项类型', '关注者', '创建时间', '更新时间', '所属迭代', '优先级', 'ID', '描述',
    '预估工时', '已登记工时', '剩余工时', '预估偏差', '工时进度', '进度',)

MODULE_FIELD = '详情', '周期与进度', '子工作项', '关联内容', '测试情况', '关联 Wiki 页面', '文件', '工时', '代码关联'


@fixture(scope='module')
def _issue_storage() -> dict:
    """
    记录内置工作项类型信息
    :return:
    """
    p = ise.issue_check()[0]
    stamp = prj.TeamStampData()
    stamp.call(p.json, **p.extra)
    stamp.is_response_code(200)
    j = stamp.json()
    issue_types = [c for c in j['issue_type']['issue_types'] if c['built_in']]  # 内置工作项类型
    fields = [c for c in j['field']['fields'] if c['built_in']]  # 所有内置属性

    return {'fields': fields, 'issue_types': issue_types}


@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过开箱用例')
@mark.smoke
@feature('项目配置-全局配置-工作项')
class TestBuildInIssueFabu:
    name = '发布'

    @story('T123642 工作项属性：开箱后属性列表检查')
    def test_check_field_config(self, _issue_storage):
        """"""
        with step('查看属性列表'):
            """"""
            fields = DEFAULT_FIELD

            check_field(self.name, fields, _issue_storage)

    @story('T128278 关键属性：开箱后列表检查')
    def test_check_important_field_config(self, _issue_storage):
        """"""
        important = '发布日期', '负责人'

        check_important_field(self.name, important, _issue_storage)

    @story('模块标签页：开箱后列表检查')
    def test_check_module_field(self, _issue_storage):
        """"""

        important = MODULE_FIELD

        check_field(self.name, important, _issue_storage)


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过开箱用例')
@mark.smoke
@feature('项目配置-全局配置-工作项')
class TestBuildInIssueGongDan:
    name = '工单'

    @story('123640 工作项属性：开箱后属性列表检查')
    def test_check_field_config(self, _issue_storage):
        """"""
        with step('查看属性列表'):
            """"""
            fields = DEFAULT_FIELD

            check_field(self.name, fields, _issue_storage)

    @story('128276 关键属性：开箱后列表检查')
    def test_check_important_field_config(self, _issue_storage):
        """"""
        important = '优先级', '负责人'

        check_important_field(self.name, important, _issue_storage)

    @story('T131070 模块标签页：开箱后列表检查')
    def test_check_module_field(self, _issue_storage):
        """"""

        important = MODULE_FIELD

        check_field(self.name, important, _issue_storage)


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过开箱用例')
@mark.smoke
@feature('项目配置-全局配置-工作项')
class TestBuildInIssueDefeat:
    name = '缺陷'

    @story('123643 工作项属性：开箱后属性列表检查')
    def test_check_field_config(self, _issue_storage):
        """"""
        with step('查看属性列表'):
            """"""
            fields = DEFAULT_FIELD

            check_field(self.name, fields, _issue_storage)

    @story('128277 关键属性：开箱后列表检查')
    def test_check_important_field_config(self, _issue_storage):
        """"""
        important = '优先级', '负责人'

        check_important_field(self.name, important, _issue_storage)

    @story('131066 模块标签页：开箱后列表检查')
    def test_check_module_field(self, _issue_storage):
        """"""

        important = MODULE_FIELD

        check_field(self.name, important, _issue_storage)


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过开箱用例')
@mark.smoke
@feature('项目配置-全局配置-工作项')
class TestBuildInIssueTask:
    name = '任务'

    @story('123644 工作项属性：开箱后属性列表检查')
    def test_check_field_config(self, _issue_storage):
        """"""
        with step('查看属性列表'):
            """"""
            fields = DEFAULT_FIELD

            check_field(self.name, fields, _issue_storage)

    @story('128279 关键属性：开箱后列表检查')
    def test_check_important_field_config(self, _issue_storage):
        """"""
        important = '优先级', '负责人'

        check_important_field(self.name, important, _issue_storage)

    @story('131068 模块标签页：开箱后列表检查')
    def test_check_module_field(self, _issue_storage):
        """"""

        important = MODULE_FIELD

        check_field(self.name, important, _issue_storage)


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过开箱用例')
@mark.smoke
@feature('项目配置-全局配置-工作项')
class TestBuildInIssueDemand:
    name = '需求'

    @story('123645 工作项属性：开箱后属性列表检查')
    def test_check_field_config(self, _issue_storage):
        """"""
        with step('查看属性列表'):
            """"""
            fields = DEFAULT_FIELD

            check_field(self.name, fields, _issue_storage)

    @story('128280 关键属性：开箱后列表检查')
    def test_check_important_field_config(self, _issue_storage):
        """"""
        important = '优先级', '负责人'

        check_important_field(self.name, important, _issue_storage)

    @story('131069 模块标签页：开箱后列表检查')
    def test_check_module_field(self, _issue_storage):
        """"""

        important = MODULE_FIELD

        check_field(self.name, important, _issue_storage)


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过开箱用例')
@mark.smoke
@feature('项目配置-全局配置-工作项')
class TestBuildInIssueStory:
    name = '用户故事'

    @story('123646 工作项属性：开箱后属性列表检查')
    def test_check_field_config(self, _issue_storage):
        """"""
        with step('查看属性列表'):
            """"""
            fields = DEFAULT_FIELD

            check_field(self.name, fields, _issue_storage)

    @story('128281 关键属性：开箱后列表检查')
    def test_check_important_field_config(self, _issue_storage):
        """"""
        important = '工作项类型', '优先级', '所属迭代', '负责人',

        check_important_field(self.name, important, _issue_storage)

    @story('131071 模块标签页：开箱后列表检查')
    def test_check_module_field(self, _issue_storage):
        """"""

        important = MODULE_FIELD

        check_field(self.name, important, _issue_storage)


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过开箱用例')
@mark.smoke
@feature('项目配置-全局配置-工作项')
class TestBuildInIssueSubChecking:
    name = '子检查项'

    @story('123647 工作项属性：开箱后属性列表检查')
    def test_check_field_config(self, _issue_storage):
        """"""
        with step('查看属性列表'):
            """"""
            fields = DEFAULT_FIELD

            check_field(self.name, fields, _issue_storage)

    @story('128282 关键属性：开箱后列表检查')
    def test_check_important_field_config(self, _issue_storage):
        """"""
        important = '负责人', '截止日期'

        check_important_field(self.name, important, _issue_storage)

    @story('131072 模块标签页：开箱后列表检查')
    def test_check_module_field(self, _issue_storage):
        """"""

        important = MODULE_FIELD

        check_field(self.name, important, _issue_storage)


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过开箱用例')
@mark.smoke
@feature('项目配置-全局配置-工作项')
class TestBuildInIssueSubDemand:
    name = '子需求'

    @story('123648 工作项属性：开箱后属性列表检查')
    def test_check_field_config(self, _issue_storage):
        """"""
        with step('查看属性列表'):
            """"""
            fields = DEFAULT_FIELD

            check_field(self.name, fields, _issue_storage)

    @story('128284 关键属性：开箱后列表检查')
    def test_check_important_field_config(self, _issue_storage):
        """"""
        important = '负责人', '优先级'

        check_important_field(self.name, important, _issue_storage)

    @story('131073 模块标签页：开箱后列表检查')
    def test_check_module_field(self, _issue_storage):
        """"""

        important = MODULE_FIELD

        check_field(self.name, important, _issue_storage)


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过开箱用例')
@mark.smoke
@feature('项目配置-全局配置-工作项')
class TestBuildInIssueSubTask:
    name = '子任务'

    @story('123649 工作项属性：开箱后属性列表检查')
    @story('123650 工作项属性：开箱后属性列表检查')
    def test_check_field_config(self, _issue_storage):
        """"""
        with step('查看属性列表'):
            """"""
            fields = DEFAULT_FIELD

            check_field(self.name, fields, _issue_storage)

    @story('128285 关键属性：开箱后列表检查')
    def test_check_important_field_config(self, _issue_storage):
        """"""
        important = '负责人', '优先级'

        check_important_field(self.name, important, _issue_storage)

    @story('131075 模块标签页：开箱后列表检查')
    def test_check_module_field(self, _issue_storage):
        """"""

        important = MODULE_FIELD

        check_field(self.name, important, _issue_storage)


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

def check_important_field(name: str, important: tuple, store):
    """检查关键属性"""
    f_k = {m['uuid']: i for m in store.get('fields') for i in important if i == m['name']}
    issues = [m['default_configs']['default_field_configs']
              for m in store.get('issue_types')
              if m['name'] == name][0]
    important_k = [m['field_uuid'] for m in issues if m['is_important_field']]
    err_ = []
    for k, v in f_k.items():
        if k not in important_k:
            err_.append(v)
    assert not err_, f'关键属性没找到{err_}'


def check_field(name: str, fields: tuple, store):
    """检查属性"""
    f_k = {m['uuid']: i for m in store.get('fields') for i in fields if i == m['name']}
    issues = [m['default_configs']['default_field_configs']
              for m in store.get('issue_types')
              if m['name'] == name][0]
    important_k = [m['field_uuid'] for m in issues]
    err_ = []
    for k, v in f_k.items():
        if k not in important_k:
            err_.append(v)
    assert not err_, f'属性没找到{err_}'
