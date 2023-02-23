"""# -*- coding: UTF-8 -*-
@Project ：walnut
@File    ：test_issue_permission.py
@Author  ：zhangyonghui@ones.ai
@Date    ：2022/6/24 2:15 PM
@Desc    ：项目设置-工作项类型-工作项通知权限
"""
import time
from falcons.check import Checker, go
from falcons.com.nick import feature, story, step, fixture
from main.actions.issue import IssueAction
from main.actions.task import TaskAction
from main.api import issue
from main.params.issue import add_notice_rules, notice_rules


@fixture(scope='module')
def add_notice_rule():
    resp = IssueAction.get_issue_notice_rule(issue_name='任务')
    issue_type_uuid = TaskAction.issue_type_uuid('任务')[0]

    notice_user_domains = resp.value('notice_rules[0].notice_user_domains')
    filter_condition = resp.value('notice_rules[0].filter_condition')
    condition = resp.value('notice_rules[0].condition')

    notice = {'notice_user_domains': notice_user_domains,
              'filter_condition': filter_condition, 'condition': condition, 'issue_type_uuid': issue_type_uuid
              }

    return notice


@feature('工作项类型-工作项提醒')
class TestIssueNoticeRules(Checker):

    @classmethod
    def get_global_notice_rules(cls, issue_type_uuid, token=None):
        param = notice_rules()[0]
        param.uri_args({'issue_type_uuid': issue_type_uuid})
        resp = go(issue.GlobalNoticeRule, param, token)
        return resp

    @story('T124366 工作项提醒：编辑提醒规则--配置中心')
    def test_update_global_notice_rule(self):
        issue_type_uuid = TaskAction.issue_type_uuid('任务')[0]
        resp = self.get_global_notice_rules(issue_type_uuid)
        with step('配置中心新增提醒规则'):
            param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field009')  # 创建时间
            param.json_update('action', 'now')
            param.json_update('notice_time', {'minute': 0})
            param.json_update('notice_user_domains', resp.value('notice_rules[0].notice_user_domains'))
            param.json_update('filter_condition', resp.value('notice_rules[0].filter_condition'))
            param.json_update('condition', resp.value('notice_rules[0].condition'))
            param.uri_args({'issue_type_uuid': issue_type_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('编辑提醒规则'):
            time.sleep(2)
            resp_1 = self.get_global_notice_rules(issue_type_uuid)
            # 和原始数据取差集 取新增的rule_uuid
            notice_rule_uuid = list(set([r['uuid'] for r in resp_1.value('notice_rules')]) - set(
                [r['uuid'] for r in resp.value('notice_rules')]))[0]
            param.json_update('notice_types', ["notice_center", "email"])
            param.json_update('action', 'after')
            param.json_update('notice_time', {'minute': 30})
            param.uri_args({'notice_rule_uuid': notice_rule_uuid})
            resp_add = self.call(issue.UpdateGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('删除提醒规则'):
            param = notice_rules()[0]
            param.uri_args({'issue_type_uuid': issue_type_uuid, 'notice_rule_uuid': notice_rule_uuid})
            resp = go(issue.DelGlobalNoticeRule, param)
            resp.check_response('code', 200)

    @story('T124423 工作项提醒：检查工作项提醒列表的默认规则（开箱）-任务')
    def test_task_default_notice_rule(self, add_notice_rule):
        resp = IssueAction.get_issue_notice_rule(issue_name='任务')
        resp_global = self.get_global_notice_rules(add_notice_rule['issue_type_uuid'])
        # assert len(resp.value('notice_rules')) == len(resp_global.value('notice_rules'))

    @story('T124437 工作项提醒：检查工作项提醒列表的默认规则（开箱）-子任务')
    def test_sub_task_default_notice_rule(self):
        resp = IssueAction.get_issue_notice_rule(issue_name='子任务')
        issue_type_uuid = TaskAction.issue_type_uuid('子任务')[0]
        resp_global = self.get_global_notice_rules(issue_type_uuid)
        # 配置中心的条数=项目内条数
        assert len(resp.value('notice_rules')) == len(resp_global.value('notice_rules'))

    @story('T124438 工作项提醒：检查工作项提醒列表的默认规则（开箱）--配置中心-任务')
    def test_global_task_default_notice_rule(self, add_notice_rule):
        resp = self.get_global_notice_rules(add_notice_rule['issue_type_uuid'])
        assert len(resp.value('notice_rules')) >= 1

    @story('T124437 工作项提醒：检查工作项提醒列表的默认规则（开箱）--配置中心-子任务')
    def test_global_sub_task_default_notice_rule(self):
        issue_type_uuid = TaskAction.issue_type_uuid('子任务')[0]
        resp = self.get_global_notice_rules(issue_type_uuid)
        resp.check_response('notice_rules[0].issue_type_uuid', issue_type_uuid)
        resp.check_response('notice_rules[0].notice_types[0]', 'notice_center')
        assert len(resp.value('notice_rules')) >= 1

    @story('T124922 工作项提醒：添加提醒规则（创建时间）（当时）')
    @story('T124885 删除提醒规则')
    def test_add_and_del_issue_notice_rules(self, add_notice_rule):
        issue_type_uuid = TaskAction.issue_type_uuid('任务')[0]
        with step('添加提醒规则（创建时间）（当时）'):
            param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field009')  # 创建时间
            param.json_update('action', 'now')
            param.json_update('notice_time', {'minute': 0})
            param.json_update('notice_user_domains', add_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', add_notice_rule['filter_condition'])
            param.json_update('condition', add_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': issue_type_uuid})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)
            param.uri_args({'issue_type_uuid': add_notice_rule['issue_type_uuid']})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)

        with step('点击 创建时间 当时 提醒规则后的 删除 操作按钮'):
            time.sleep(2)
            resp = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(add_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story('T124939 T124387工作项提醒：添加提醒规则（创建时间）（之后10分钟）')
    def test_add_notice_rule_after_10(self, add_notice_rule):
        with step('添加提醒规则（创建时间）（当时）'):
            param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field009')  # 创建时间
            param.json_update('action', 'after')  # 之后10分钟
            param.json_update('notice_time', {'minute': 10})
            param.json_update('notice_user_domains', add_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', add_notice_rule['filter_condition'])
            param.json_update('condition', add_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': add_notice_rule['issue_type_uuid']})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)
            resp_1 = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp_1.value('notice_rules[0].uuid')

        with step('更新提醒规则（创建时间）（当时）'):
            param.json_update('action', 'after')  # 之后10分钟
            param.json_update('notice_time', {'minute': 30})
            param.json_update('notice_types', ["notice_center", "email"])
            param.uri_args(
                {'issue_type_uuid': add_notice_rule['issue_type_uuid'], 'notice_rule_uuid': notice_rule_uuid})
            resp_add = self.call(issue.UpdateNoticeRules, param)
            resp_add.check_response('code', 200)

        with step('清除数据'):
            time.sleep(1)
            resp = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(add_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story('T125212 工作项提醒：添加提醒规则（截止日期）（当天 11:00）')
    def test_add_notice_rule_field013_after_day(self, add_notice_rule):
        with step('添加提醒规则（创建时间）（当时）'):
            with step('添加提醒规则（截止日期）（当时）'):
                param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field013')  # 截止日期
            param.json_update('action', 'that_day')  # 当天 11:00
            param.json_update('notice_time', {'day': 0, 'date_time': "11:00"})
            param.json_update('notice_user_domains', add_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', add_notice_rule['filter_condition'])
            param.json_update('condition', add_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': add_notice_rule['issue_type_uuid']})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)

        with step('清除数据'):
            time.sleep(1)
            resp = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(add_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story('T125238 工作项提醒：添加提醒规则（截止日期）（之后1天 14:00）')
    def test_add_notice_rule_field013_after_day1(self, add_notice_rule):
        with step('添加提醒规则（截止日期）（之后1天 14:00）'):
            param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field013')  # 截止日期
            param.json_update('action', 'after')  # 之后1天 14:00
            param.json_update('notice_time', {'day': 1, 'date_time': "14:00"})
            param.json_update('notice_user_domains', add_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', add_notice_rule['filter_condition'])
            param.json_update('condition', add_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': add_notice_rule['issue_type_uuid']})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)

        with step('清除数据'):
            time.sleep(1)
            resp = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(add_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story('T125261 工作项提醒：添加提醒规则（截止日期）（之前3天 09:00）')
    def test_add_notice_rule_field013_before_3day(self, add_notice_rule):
        with step('添加提醒规则（截止日期）（之前3天 09:00））'):
            param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field013')  # 截止日期
            param.json_update('action', 'before')  # 之前3天 09:00
            param.json_update('notice_time', {'day': 3, 'date_time': "09:00"})
            param.json_update('notice_user_domains', add_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', add_notice_rule['filter_condition'])
            param.json_update('condition', add_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': add_notice_rule['issue_type_uuid']})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)

        with step('清除数据'):
            time.sleep(1)
            resp = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(add_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story('T124813 工作项提醒：检查邮件提醒方式')
    def test_add_email_notice_types(self, add_notice_rule):
        with step('1、提醒时间选择：创建时间 当时 2、提醒方式勾选：邮件'):
            param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field009')
            param.json_update('action', 'now')
            param.json_update('notice_types', ['email'])  # 邮件提醒方式
            param.json_update('notice_time', {'minute': 0})
            param.json_update('notice_user_domains', add_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', add_notice_rule['filter_condition'])
            param.json_update('condition', add_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': add_notice_rule['issue_type_uuid']})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)
        with step('清除数据'):
            time.sleep(1)
            resp = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(add_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story('T124764 工作项提醒：检查同时添加两种提醒方式')
    @story('124754 工作项提醒：检查同时添加两种提醒方式')
    def test_add_email_and_notice_center_notice_types(self, add_notice_rule):
        with step('提醒方式勾选：通知中心、邮件'):
            param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field009')
            param.json_update('action', 'now')
            param.json_update('notice_types', ['email', 'notice_center'])  # 提醒方式 :通知中心、邮件
            param.json_update('notice_time', {'minute': 0})
            param.json_update('notice_user_domains', add_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', add_notice_rule['filter_condition'])
            param.json_update('condition', add_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': add_notice_rule['issue_type_uuid']})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)
        with step('清除数据'):
            time.sleep(1)
            resp = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(add_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story("T125047 工作项提醒：添加提醒规则（更新时间）（当时）")
    def test_add_notice_rules_update_now(self, add_notice_rule):

        with step('添加提醒规则（更新时间）（当时）'):
            param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field010')  # 创建时间
            param.json_update('action', 'now')
            param.json_update('notice_time', {'minute': 0})
            param.json_update('notice_user_domains', add_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', add_notice_rule['filter_condition'])
            param.json_update('condition', add_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': add_notice_rule['issue_type_uuid']})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)

        with step("清除 数据"):
            time.sleep(1)
            resp = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(add_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story("T125053 工作项提醒：添加提醒规则（更新时间）（之后20小时）")
    def test_add_notice_rule_update_after_20hour(self, add_notice_rule):
        with step('添加提醒规则（更新时间）（之后20小时）'):
            param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field010')  # 创建时间
            param.json_update('action', 'after')
            param.json_update('notice_time', {'hour': 20})
            param.json_update('notice_user_domains', add_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', add_notice_rule['filter_condition'])
            param.json_update('condition', add_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': add_notice_rule['issue_type_uuid']})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)

        with step("清除 数据"):
            time.sleep(1)
            resp = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(add_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story("T125072 工作项提醒：添加提醒规则（计划开始日期）（当天 11:00）")
    def test_add_notice_rules_plan_now(self, add_notice_rule):

        with step('添加提醒规则（计划开始日期）（当天11:00）'):
            param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field027')  # 创建时间
            param.json_update('action', 'that_day')
            param.json_update('notice_time', {"day": 0, "date_time": "11:00"})
            param.json_update('notice_user_domains', add_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', add_notice_rule['filter_condition'])
            param.json_update('condition', add_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': add_notice_rule['issue_type_uuid']})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)

        with step("清除 数据"):
            time.sleep(1)
            resp = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(add_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story("T125107 工作项提醒：添加提醒规则（计划开始日期）（之后2天 14:00）")
    def test_add_notice_rules_plan_after(self, add_notice_rule):
        with step('添加提醒规则（计划开始日期）（之后2天 14:00）'):
            param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field027')  # 创建时间
            param.json_update('action', 'after')
            param.json_update('notice_time', {"day": 2, "date_time": "14:00"})
            param.json_update('notice_user_domains', add_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', add_notice_rule['filter_condition'])
            param.json_update('condition', add_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': add_notice_rule['issue_type_uuid']})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)

        with step("清除 数据"):
            time.sleep(1)
            resp = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(add_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story("T125121 工作项提醒：添加提醒规则（计划开始日期）（之前1天 09:00）")
    def test_add_notice_rules_plan_before(self, add_notice_rule):
        with step('添加提醒规则（计划开始日期）（之前1天 09:00）'):
            param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field027')  # 创建时间
            param.json_update('action', 'before')
            param.json_update('notice_time', {"day": 1, "date_time": "09:00"})
            param.json_update('notice_user_domains', add_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', add_notice_rule['filter_condition'])
            param.json_update('condition', add_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': add_notice_rule['issue_type_uuid']})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)

        with step("清除 数据"):
            time.sleep(1)
            resp = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(add_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story("T125147 工作项提醒：添加提醒规则（计划完成日期）（当天 11:00）")
    def test_add_notice_rules_complete_plan(self, add_notice_rule):
        with step('添加提醒规则（计划完成日期）（当天11:00）'):
            param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field028')  # 创建时间
            param.json_update('action', 'that_day')
            param.json_update('notice_time', {"day": 0, "date_time": "11:00"})
            param.json_update('notice_user_domains', add_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', add_notice_rule['filter_condition'])
            param.json_update('condition', add_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': add_notice_rule['issue_type_uuid']})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)

        with step("清除 数据"):
            time.sleep(1)
            resp = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(add_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story("T125163 工作项提醒：添加提醒规则（计划完成日期）（之后1天 14:00）")
    @story('125166 工作项提醒：添加提醒规则（计划完成日期）（之后1天 14:00）')
    @story('125174 工作项提醒：添加提醒规则（计划完成日期）（之后1天 14:00）')
    def test_add_notice_rules_complete_plan_after1(self, add_notice_rule):
        with step('添加提醒规则（计划完成日期）（之后1天 14:00）'):
            param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field028')  # 创建时间
            param.json_update('action', 'after')
            param.json_update('notice_time', {"day": 1, "date_time": "14:00"})
            param.json_update('notice_user_domains', add_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', add_notice_rule['filter_condition'])
            param.json_update('condition', add_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': add_notice_rule['issue_type_uuid']})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)

        with step("清除 数据"):
            time.sleep(1)
            resp = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(add_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story("T125201 工作项提醒：添加提醒规则（计划完成日期）（之前3天 09:00")
    def test_add_notice_rules_complete_plan_before3(self, add_notice_rule):
        with step('添加提醒规则（计划完成日期）（之前3天 09:00）'):
            param = add_notice_rules()[0]
            param.json_update('field_uuid', 'field028')  # 创建时间
            param.json_update('action', 'before')
            param.json_update('notice_time', {"day": 3, "date_time": "09:00"})
            param.json_update('notice_user_domains', add_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', add_notice_rule['filter_condition'])
            param.json_update('condition', add_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': add_notice_rule['issue_type_uuid']})
            resp_add = self.call(issue.AddNoticeRules, param)
            resp_add.check_response('code', 200)

        with step("清除 数据"):
            time.sleep(1)
            resp = IssueAction.get_issue_notice_rule(issue_name='任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(add_notice_rule['issue_type_uuid'], notice_rule_uuid)