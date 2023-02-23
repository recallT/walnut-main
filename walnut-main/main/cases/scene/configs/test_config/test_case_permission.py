# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_case_permission.py
@Author  ：zhangyonghui@ones.ai
@Date    ：8/11/22 2:15 PM 
@Desc    ：配置中心-测试管理-权限配置
"""
from falcons.check import Checker
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, step, fixture

from main.actions import sprint
from main.actions.case import CaseAction
from main.actions.member import MemberAction
from main.actions.task import TaskAction
from main.api import case, project
from main.helper.extra import Extra
from main.params import testcase, proj
from main.params.const import ACCOUNT


@fixture(scope='module', autouse=True)
def get_member():
    member_uuid = MemberAction.get_member_uuid()
    return member_uuid


@fixture(scope='module', autouse=True)
def get_issue_uuid():
    issue_type_uuid = TaskAction.issue_type_uuid('缺陷')[0]
    return issue_type_uuid


@feature('配置中心-用例属性')
class TestCasePermission(Checker):

    @story('T148489 配置中心-权限配置-删除用例库：添加成员域')
    @story('T148546 配置中心-权限配置-删除用例库：移除成员域')
    def test_add_and_del_permission_delete_library(self, get_member):
        with step('配置中心-权限配置-删除用例库：添加成员域'):
            uuid = CaseAction.add_testcase_permission(permission='delete_library', user_domain_param=get_member,
                                                      user_domain_type='single_user')
        with step("权限操作验证"):
            # todo
            ...
        with step('权限配置-删除用例库：移除成员域'):
            CaseAction.del_testcase_permission(permission_rule_uuid=uuid)

    @story('T148487 配置中心-权限配置-管理用例库：添加成员域')
    @story('T148542 配置中心-权限配置-管理用例库：移除成员域')
    @story('T131598 权限配置-管理用例库：删除成员域')
    @story('T131601 权限配置-管理用例库：添加成员域（成员）')
    def test_add_and_del_permission_manage_library(self, get_member):
        with step('配置中心-权限配置-删除用例库：添加成员域'):
            uuid = CaseAction.add_testcase_permission(permission='manage_library', user_domain_param=get_member,
                                                      user_domain_type='single_user')
        with step("权限操作验证"):
            # todo
            ...
        with step('权限配置-删除用例库：移除成员域'):
            CaseAction.del_testcase_permission(permission_rule_uuid=uuid)

    @story('T131580 权限配置-管理测试报告：添加成员域（成员）')
    def test_add_and_del_permission_manage_report(self, get_member):
        with step('配置中心-权限配置-管理测试报告：添加成员域'):
            uuid = CaseAction.add_testcase_permission(permission='manage_report', user_domain_param=get_member,
                                                      user_domain_type='single_user')
        with step("权限操作验证"):
            # todo
            ...
        with step('权限配置-管理测试报告：移除成员域'):
            CaseAction.del_testcase_permission(permission_rule_uuid=uuid)

    @story('T131587 权限配置-管理测试计划：添加成员域（成员）')
    def test_add_and_del_permission_manage_plans(self, get_member):
        with step('配置中心-权限配置-管理测试报告：添加成员域'):
            uuid = CaseAction.add_testcase_permission(permission='manage_plans', user_domain_param=get_member,
                                                      user_domain_type='single_user')
        with step("权限操作验证"):
            # todo
            ...
        with step('权限配置-管理测试报告：移除成员域'):
            CaseAction.del_testcase_permission(permission_rule_uuid=uuid)

    @story('T128850 关联项目配置详情页-默认成员：添加成员域')
    @story('T128848 关联项目配置详情页-默认成员：删除成员域')
    def test_testcase_default_member_permission(self):
        # 查询成员数据信息
        su_param = proj.program_search_user()[0]
        resp = self.call(project.UsesSearch, su_param)
        user = resp.value('users[0]')
        member_uuid = user['uuid']
        with step('关联项目配置详情页-默认成员：添加成员域'):
            param_add = testcase.add_testcase_default_member_permission()[0]
            param_add.json_update('user_domain_param', member_uuid)
            self.call(case.AddTestCaseDefaultMemberPermission, param_add)

        with step('关联项目配置详情页-默认成员：删除成员域'):
            param_del = testcase.del_testcase_default_member_permission()[0]
            param_del.json_update('user', user)
            param_del.json_update('name', user['name'])
            param_del.json_update('subText', user['email'])
            param_del.json_update('members', [member_uuid])
            param_del.json_update('user_domain_param', member_uuid)
            self.call(case.DelTestCaseDefaultMemberPermission, param_del)

    @story('T128852 关联项目配置详情页：关闭需求跟踪组件功能')
    @story('T128855 关联项目配置详情页：启用需求跟踪组件功能')
    def test_set_relation_project_demand_components(self):
        issue_type_uuid = TaskAction.issue_type_uuid('缺陷')[0]
        with step('「需求跟踪」组件选择：不启用'):
            param = testcase.update_testcase_related_project()[0]
            param.json_update('issue_type_uuid', issue_type_uuid)
            self.call(case.UpdateTestCaseConfig, param)
            # todo 顶部导航无：需求跟踪断言
        with step('「需求跟踪」组件选择：启用'):
            param = testcase.update_testcase_related_project()[0]
            param.json_update('issue_type_uuid', issue_type_uuid)
            param.json_update('show_issue_track', True)
            self.call(case.UpdateTestCaseConfig, param)
            # todo 顶部导航有：需求跟踪断言

    @story('T128856 关联项目配置详情页：修改执行结果属性配置')
    def test_update_testcase_result_config(self, get_issue_uuid):
        with step('修改执行结果属性配置'):
            param = testcase.testcase_result_field_set()[0]
            param.json_update('check_points[0].is_must', True)
            param.json_update('check_points[1].is_must', True)
            param.json_update('check_points[6].is_must', True)
            param.json_update('check_points[7].is_must', True)
            param.json_update('issue_type_uuid', get_issue_uuid)
            self.call(case.UpdateTestCaseConfig, param)
        with step("还原数据"):
            param.json_update('check_points[0].is_must', False)
            param.json_update('check_points[1].is_must', False)
            param.json_update('check_points[6].is_must', False)
            param.json_update('check_points[7].is_must', False)
            self.call(case.UpdateTestCaseConfig, param)

    @story('T128847 关联项目配置详情页-默认成员：默认成员域检查')
    @story('T128854 关联项目配置详情页：默认工作项类型检查')
    def test_testcase_default_member_permission(self, get_issue_uuid):
        creator = Extra(ApiMeta)
        p_t4 = creator.new_project(f'瀑布项目-test', project_type='project-t4')
        p_t2 = creator.new_project(f'通用项目-test', project_type='project-t2')
        with step('查看「默认成员」成员域'):
            param = {'testcase_config': 0}
            resp = sprint.team_stamp(param=param)
            configs = [r for r in resp.value('testcase_config.configs') if
                       r['project_uuid'] == ACCOUNT.project_uuid][0]
            user_domain_types = [f['user_domain_type'] for f in configs['members']]
            assert "testcase_administrators" in user_domain_types
        with step('敏捷项目默认工作项类型检查：缺陷'):
            default_issue_uuid = configs['issue_type_uuid']
            assert default_issue_uuid == get_issue_uuid

        with step("成员A进入配置中心-测试管理配置-关联项目配置-瀑布项目：默认工作项-任务"):
            issue_type_uuid = TaskAction.issue_type_uuid('任务')[0]

            configs = [r for r in resp.value('testcase_config.configs') if
                       r['project_uuid'] == p_t4][0]
            assert configs['issue_type_uuid'] == issue_type_uuid

        with step("成员A进入配置中心-测试管理配置-关联项目配置-通用项目：默认工作项-任务"):
            configs = [r for r in resp.value('testcase_config.configs') if
                       r['project_uuid'] == p_t2][0]
            assert configs['issue_type_uuid'] == issue_type_uuid

        with step("删除数据"):
            creator.del_project(p_t4)
            creator.del_project(p_t2)

    @story('T128851 关联项目配置详情页-默认缺陷对应工作项类型：切换工作项类型')
    def test_update_testcase_config_issue_type(self, get_issue_uuid):
        with step("切换工作项类型,切换为需求"):
            issue_type_uuid = TaskAction.issue_type_uuid('需求')[0]
            param = testcase.update_testcase_related_project()[0]
            param.json_update('issue_type_uuid', issue_type_uuid)
            param.json_update('show_issue_track', False)
            self.call(case.UpdateTestCaseConfig, param)
        with step('还原数据'):
            param.json_update('issue_type_uuid', get_issue_uuid)
            self.call(case.UpdateTestCaseConfig, param)
