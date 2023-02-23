#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_issue_config.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/5 
@Desc    ：全局配置-工作项配置用例
"""
import time

from falcons.com.nick import feature, story, parametrize, fixture, step, mark

from main.api import issue as api
from main.api import project as prj
from main.params import issue as ise


@fixture(scope='module')
def _issues_():
    """
    主要是记录key 用于清理测试数据
    :return:
    """
    return []


@fixture(scope='module', autouse=True)
def _clear_issue(_issues_):
    """
    用于清理测试数据
    :return:
    """
    yield
    print('Delete test issue type....')
    delete = api.IssueDelete()
    p = ise.delete_issue()[0]

    def _delete(issue_id):
        p.uri_args({'issue_uuid': issue_id})
        delete.call(**p.extra)

    for issue in _issues_:
        for c in range(10):
            print(f'Trying {c + 1}...')
            _delete(issue['uuid'])
            if delete.response.status_code == 200:
                break
            else:
                time.sleep(1)


@mark.smoke
@feature('项目配置-全局配置-工作项')
class TestAddIssue:

    @story('T123397 工作项类型：新建标准工作项类型')
    @parametrize('param', ise.add_standard_issue())
    def test_add_standard_issue(self, param, _issues_):
        """"""
        self.add_issue(_issues_, param)

    @story('T123398 工作项类型：新建子工作项类型')
    @parametrize('param', ise.add_sub_issue())
    def test_add_sub_issue(self, param, _issues_):
        """"""
        self.add_issue(_issues_, param)

    @story('T123343 工作项类型-工作项类型列表-操作：重命名（标准工作项）')
    @parametrize('param', ise.add_standard_issue())
    def test_rename_standard_issue(self, param, _issues_):
        """"""
        m = param.json['issue_type']['name']
        param.json['issue_type']['name'] = 'New' + m[3:]
        param.uri_args({'issue_uuid': _issues_[0]['uuid']})

        update = api.IssueUpdate()
        update.call(param.json, **param.extra)

        update.is_response_code(200)

    @story('T123336 工作项类型-工作项类型列表-操作：复制')
    @parametrize('param', ise.copy_issue())
    def test_copy_issue(self, param, _issues_):
        """"""
        param.json['copy_from'] = _issues_[0]['uuid']
        self.add_issue(_issues_, param)

    @story('123341 工作项类型-工作项类型列表-操作：删除工作项类型（系统工作项类型不可删除）')
    @parametrize('param', ise.delete_issue())
    def test_delete_issue_system(self, param):
        """"""
        with step('获取系统工作项UUID'):
            s_param = ise.show_issue_list()[0]
            stamps = prj.TeamStampData()
            stamps.call(s_param.json, **s_param.extra)

            stamps.is_response_code(200)
            list_issue = stamps.json()['issue_type']['issue_types']
            sys_issues = [c['uuid'] for c in list_issue if c['built_in']]

        param.uri_args({'issue_uuid': sys_issues[1]})

        delete = api.IssueDelete()
        delete.call(**param.extra)
        delete.is_response_code([403, 400])  # 403系统工作项不可删除/400选择的工作项正在被使用

    @story('T123347 工作项类型-工作项类型列表-列表行表头：工作项类型')
    @story('162025 工作项类型-工作项类型列表：默认工作项类型检查')
    @parametrize('param', ise.delete_issue())
    def test_sys_issue_range(self, param):
        """"""
        sys_names = '发布', '工单', '缺陷', '任务', '需求', '用户故事', '子检查项', '子任务', '子需求'
        with step('获取系统工作项'):
            s_param = ise.show_issue_list()[0]
            stamps = prj.TeamStampData()
            stamps.call(s_param.json, **s_param.extra)

            stamps.is_response_code(200)
            list_issue = stamps.json()['issue_type']['issue_types']
            names = [c['name'] for c in list_issue if c['built_in']]
        err_ = []
        for name in sys_names:
            if name not in names:
                err_.append(names)

        assert not err_, f'没找到系统工作项:{err_}'

    @story('T123349 工作项类型-工作项类型列表-列表行表头：类型')
    @parametrize('param', ise.delete_issue())
    def test_sys_issue_type(self, param):
        """"""
        issue_type = 0, 1  # 标准和子工作项类型
        with step('获取系统工作项'):
            s_param = ise.show_issue_list()[0]
            stamps = prj.TeamStampData()
            stamps.call(s_param.json, **s_param.extra)

            stamps.is_response_code(200)
            list_issue = stamps.json()['issue_type']['issue_types']
            types = [c['type'] for c in list_issue]
        err_ = []
        for ty in types:
            if ty not in issue_type:
                err_.append(ty)

        assert not err_, f'查到异常工作项类型:{err_}'

    @story('T123334 工作项类型-工作项类型列表-操作：编辑')
    @parametrize('param', ise.add_issue_field())
    def test_edit_issue_not_effect_in_project(self, param, _issues_):
        """"""
        issue_uuid = _issues_[0]['uuid']
        with step('应用工作项到项目中'):
            """"""
            p = ise.add_project_issue()[0]
            p.json['issue_type_uuids'] = [issue_uuid, ]

            add = api.IssueProjectAdd()
            add.call(p.json, **p.extra)
            add.is_response_code(200)

        with step('编辑原工作项类型属性'):
            """"""
            #
            # ori = self.get_field_uuid(issue_uuid)
            #
            # add = api.IssueFieldAdd()
            # #
            # param.uri_args({'issue_uuid': issue_uuid})
            # add.call(**param.extra)
            # add.is_response_code(200)
            # cur = self.get_field_uuid(issue_uuid)
            #
            # assert len(cur) > len(ori)

        with step('检查项目中对应工作项属性'):
            """"""

        with step('项目中清除使用'):
            """"""
            time.sleep(1)
            p = ise.delete_project_issue()[0]
            p.uri_args({'issue_uuid': issue_uuid})

            delete_i = api.IssueProjectDelete()
            delete_i.call(p.json, **p.extra)
            delete_i.is_response_code(200)

    @classmethod
    def get_field_uuid(cls, issue_uuid, token=None):
        p1 = ise.issue_field_config()[0]
        p1.uri_args({'issue_uuid': issue_uuid})
        ifc = api.IssueFieldConfig(token)
        ifc.call(**p1.extra)
        ifc.is_response_code(200)
        curr_field_uuid = [i['field_uuid'] for i in ifc.json()['items']]

        return curr_field_uuid

    @story('T123342 工作项类型-工作项类型列表-操作：删除工作项类型（已经被项目使用）')
    @parametrize('param', ise.delete_issue())
    def test_delete_issue_used_in_project(self, param, _issues_):
        """"""
        issue_uuid = _issues_[0]['uuid']
        with step('应用工作项到项目中'):
            """"""
            p = ise.add_project_issue()[0]
            p.json['issue_type_uuids'] = [issue_uuid, ]

            add = api.IssueProjectAdd()
            add.call(p.json, **p.extra)
            add.is_response_code(200)

        with step('删除工作项类型'):
            delete = api.IssueDelete()
            param.uri_args({'issue_uuid': issue_uuid})
            delete.call(**param.extra)
            delete.is_response_code(400)
            delete.check_response('type', 'InUse')

        with step('项目中清除使用'):
            """"""
            p = ise.delete_project_issue()[0]
            p.uri_args({'issue_uuid': issue_uuid})

            delete_i = api.IssueProjectDelete()
            delete_i.call(p.json, **p.extra)
            delete_i.is_response_code(200)

    @classmethod
    def add_issue(cls, store, param, token=None):
        add = api.IssuesAdd(token)
        add.call(param.json, **param.extra)
        icon = param.json['issue_type']['icon']
        name = param.json['issue_type']['name']

        add.is_response_code(200)
        add.check_response('icon', icon)
        add.check_response('name', name)

        with step('检查新建的工作项类型'):
            s_param = ise.show_issue_list()[0]
            stamps = prj.TeamStampData(token)
            stamps.call(s_param.json, **s_param.extra)

            stamps.is_response_code(200)
            list_issue = stamps.json()['issue_type']['issue_types']
            issue_names = [c['name'] for c in list_issue]
            issue_icon = [c['icon'] for c in list_issue if c['name'] == name]

            assert name in issue_names, '工作项名字不一致'
            assert icon in issue_icon, '图标配置不一致'
        # Store new issue for teardown step
        store.append(add.json())
