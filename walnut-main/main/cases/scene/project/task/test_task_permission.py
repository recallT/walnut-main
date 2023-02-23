# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_task_permission.py
@Author  ：zhangyonghui@ones.ai
@Date    ：2022/6/17 5:05 PM 
@Desc    ：任务/工作项权限/属性修改权限
"""
from falcons.check import Checker
from falcons.com.nick import story, step, feature
from main.actions.task import TaskAction as ta
from main.api import project, issue
from main.api.project import ItemGraphql
from main.params import proj, conf


@feature('任务-作项权限-属性修改权限')
class TestProjTaskPermission(Checker):

    @story('T144541 属性修改权限-编辑工作项-有工作项编辑权限：属性修改权限规则为空')
    def test_demo1(self):
        ...

    @story('T144544 属性修改权限-编辑工作项-有工作项编辑权限：无属性修改权限')
    def test_demo1(self):
        ...

    @story('T144680 属性修改权限-编辑工作项：无工作项编辑权限')
    def test_demo1(self):
        ...

    @story('T144530 属性修改权限-创建工作项-无修改属性权限：属性必填无默认值')
    def test_demo1(self):
        ...

    @story('T144536 属性修改权限-创建工作项-无修改属性权限：属性必填有默认值')
    def test_demo1(self):
        ...

    @story('T144539 属性修改权限-创建工作项-无修改属性权限：属性非必填')
    def test_demo1(self):
        ...

    @story('T144523 属性修改权限-创建工作项：修改属性权限规则为空')
    def test_demo1(self):
        ...

    @story('T144529 属性修改权限-创建工作项：有修改属性权限')
    def test_demo1(self):
        ...

    @story('T144587 属性修改权限-新建规则-选择工作项属性：系统属性')
    def test_demo1(self):
        ...

    @story('144516  属性修改权限：新建规则')
    @story('144594 属性修改权限：删除规则')
    def test_add_and_del_new_rule(self):
        with step('属性修改权限：新建规则'):
            issue_type_uuid = ta.issue_type_uuid('任务', uuid_type='uuid')[0]
            param = proj.add_task_permission(issue_type_uuid, 'field011')[0]
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)
            # 查询生成的constraint_uuids
            param_g = proj.get_task_permission_list(issue_type_uuid)[0]
            resp = self.call(ItemGraphql, param_g)
            constraint_uuids = [r['issueTypeScopeFieldConstraints'][0]['uuid'] for r in resp.value('data.buckets') if
                                r['fieldUUID'] == 'field011']
        with step('属性修改权限：删除规则'):
            issue_type_uuid = ta.issue_type_uuid('任务')[0]
            param = conf.proj_constraints_del(constraint_uuids)[0]
            param.uri_args({'issue_type_uuid': issue_type_uuid})
            resp = self.call(issue.ProjConstraintsDelete, param)
            resp.check_response('code', 200)
