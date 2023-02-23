# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_issue_sub_task_notice.py
@Author  ：zhangyonghui@ones.ai
@Date    ：2022/6/28 2:15 PM 
@Desc    ：工作项类型-工作项提醒-子任务
"""

from falcons.check import Checker
from falcons.com.nick import feature, story, step, fixture
from main.actions.issue import IssueAction
from main.actions.task import TaskAction
from main.api import issue as iss
from main.params import issue
from main.params.issue import notice_rules


@fixture(scope='module')
def get_notice_rule():
    resp = IssueAction.get_issue_notice_rule(issue_name='子任务')
    issue_type_uuid = TaskAction.issue_type_uuid('子任务')[0]
    notice_user_domains = resp.value('notice_rules[0].notice_user_domains')
    filter_condition = resp.value('notice_rules[0].filter_condition')
    condition = resp.value('notice_rules[0].condition')

    data = {'notice_user_domains': notice_user_domains,
            'filter_condition': filter_condition, 'condition': condition, 'issue_type_uuid': issue_type_uuid
            }
    return data


@feature('工作项类型-子任务-工作项提醒')
class TestIssueSubTaskNoticeRules(Checker):

    def get_global_notice_rules(self, issue_type_uuid, token=None):
        param = notice_rules()[0]
        param.uri_args({'issue_type_uuid': issue_type_uuid})
        resp = self.call(iss.GlobalNoticeRule, param, token)
        return resp

    @story('T124932 工作项提醒：添加提醒规则（创建时间）（当时）')
    @story('124936 工作项提醒：添加提醒规则（创建时间）（当时）')
    @story('124916 工作项提醒：添加提醒规则（创建时间）（当时）')
    @story('T124878 删除提醒规则')
    def test_add_and_del_issue_notice_rules(self, get_notice_rule):
        with step('添加提醒规则（创建时间）（当时）'):
            param = issue.add_notice_rules()[0]
            param.json_update('field_uuid', 'field009')  # 创建时间
            param.json_update('action', 'now')
            param.json_update('notice_time', {'minute': 0})
            param.json_update('notice_user_domains', get_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', get_notice_rule['filter_condition'])
            param.json_update('condition', get_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': get_notice_rule['issue_type_uuid']})
            resp_add = self.call(iss.AddNoticeRules, param)
            resp_add.check_response('code', 200)
        with step('点击 创建时间 当时 提醒规则后的 删除 操作按钮'):
            resp = IssueAction.get_issue_notice_rule(issue_name='子任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(get_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story('T124932 工作项提醒：添加提醒规则（创建时间）（当时）--配置中心')
    def test_update_global_notice_rule(self, get_notice_rule):
        resp = self.get_global_notice_rules(get_notice_rule['issue_type_uuid'])
        with step('配置中心新增提醒规则'):
            param = issue.add_notice_rules()[0]
            param.json_update('field_uuid', 'field009')  # 创建时间
            param.json_update('action', 'now')
            param.json_update('notice_time', {'minute': 0})
            param.json_update('notice_user_domains', resp.value('notice_rules[0].notice_user_domains'))
            param.json_update('filter_condition', resp.value('notice_rules[0].filter_condition'))
            param.json_update('condition', resp.value('notice_rules[0].condition'))
            param.uri_args({'issue_type_uuid': get_notice_rule['issue_type_uuid']})
            resp_add = self.call(iss.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('编辑提醒规则'):
            resp_1 = self.get_global_notice_rules(get_notice_rule['issue_type_uuid'])
            # 和原始数据取差集 取新增的rule_uuid
            notice_rule_uuid = list(set([r['uuid'] for r in resp_1.value('notice_rules')]) - set(
                [r['uuid'] for r in resp.value('notice_rules')]))[0]
            param.json_update('notice_types', ["notice_center", "email"])
            param.json_update('action', 'after')
            param.json_update('notice_time', {'minute': 30})
            param.uri_args({'notice_rule_uuid': notice_rule_uuid})
            resp_add = self.call(iss.UpdateGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('删除提醒规则'):
            param = issue.notice_rules()[0]
            param.uri_args(
                {'issue_type_uuid': get_notice_rule['issue_type_uuid'], 'notice_rule_uuid': notice_rule_uuid})
            resp = self.call(iss.DelGlobalNoticeRule, param)
            resp.check_response('code', 200)

    @story('T124939 工作项提醒：添加提醒规则（创建时间）（之后10分钟）')
    @story('T124387 工作项提醒：添加提醒规则（创建时间）（之后10分钟）')
    @story('124945 工作项提醒：添加提醒规则（创建时间）（之后10分钟）')
    @story("T124950 工作项提醒：添加提醒规则（创建时间）（之后10分钟）")
    def test_sub_task_add_notice_rule_after_10(self, get_notice_rule):
        with step('添加提醒规则（创建时间）（当时）'):
            param = issue.add_notice_rules()[0]
            param.json_update('field_uuid', 'field009')  # 创建时间
            param.json_update('action', 'after')
            param.json_update('notice_time', {'minute': 10})
            param.json_update('notice_types', ["notice_center", "email"])
            param.json_update('notice_user_domains', get_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', get_notice_rule['filter_condition'])
            param.json_update('condition', get_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': get_notice_rule['issue_type_uuid']})
            resp_add = self.call(iss.AddNoticeRules, param)
            resp_add.check_response('code', 200)
        with step('点击 创建时间 当时 提醒规则后的 删除 操作按钮'):
            resp = IssueAction.get_issue_notice_rule(issue_name='子任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(get_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story('T125027 工作项提醒：添加提醒规则（更新时间）（当时）')
    def test_sub_task_add_notice_rule_update_time(self, get_notice_rule):
        with step('添加提醒规则（更新时间）（当时）'):
            param = issue.add_notice_rules()[0]
            param.json_update('field_uuid', 'field010')  # 更新时间
            param.json_update('action', 'now')
            param.json_update('notice_time', {'minute': 0})
            param.json_update('notice_user_domains', get_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', get_notice_rule['filter_condition'])
            param.json_update('condition', get_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': get_notice_rule['issue_type_uuid']})
            resp_add = self.call(iss.AddNoticeRules, param)
            resp_add.check_response('code', 200)
        with step('点击 更新时间 当时 提醒规则后的 删除 操作按钮'):
            resp = IssueAction.get_issue_notice_rule(issue_name='子任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(get_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story('T125070 工作项提醒：添加提醒规则（计划开始日期）（当天 11:00）')
    @story("T125091 工作项提醒：添加提醒规则（计划开始日期）（当天 11:00）")
    def test_sub_task_add_notice_rule_plan_start_time(self, get_notice_rule):
        with step('添加提醒规则（计划开始日期）（当时）'):
            param = issue.add_notice_rules()[0]
            param.json_update('field_uuid', 'field027')  # 更新时间
            param.json_update('action', 'that_day')
            param.json_update('notice_time', {'day': 0, 'date_time': "11:00"})
            param.json_update('notice_user_domains', get_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', get_notice_rule['filter_condition'])
            param.json_update('condition', get_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': get_notice_rule['issue_type_uuid']})
            resp_add = self.call(iss.AddNoticeRules, param)
            resp_add.check_response('code', 200)
        with step('点击 计划开始日期 当时 提醒规则后的 删除 操作按钮'):
            resp = IssueAction.get_issue_notice_rule(issue_name='子任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(get_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story('T125136 工作项提醒：添加提醒规则（计划完成日期）（当天 11:00）')
    def test_sub_task_add_notice_rule_plan_end_time(self, get_notice_rule):
        with step('添加提醒规则（计划完成日期）（当时）'):
            param = issue.add_notice_rules()[0]
            param.json_update('field_uuid', 'field028')  # 更新时间
            param.json_update('action', 'that_day')
            param.json_update('notice_time', {'day': 0, 'date_time': "11:00"})
            param.json_update('notice_user_domains', get_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', get_notice_rule['filter_condition'])
            param.json_update('condition', get_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': get_notice_rule['issue_type_uuid']})
            resp_add = self.call(iss.AddNoticeRules, param)
            resp_add.check_response('code', 200)
        with step('点击 计划完成日期 当时 提醒规则后的 删除 操作按钮'):
            resp = IssueAction.get_issue_notice_rule(issue_name='子任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(get_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story('T125213 工作项提醒：添加提醒规则（截止日期）（当天 11:00）')
    def test_sub_task_add_notice_rule_field013_after_day(self, get_notice_rule):
        with step('添加提醒规则（截止日期）（当天 11:00）'):
            param = issue.add_notice_rules()[0]
            param.json_update('field_uuid', 'field013')  # 截止日期
            param.json_update('action', 'that_day')  # 当天 11:00
            param.json_update('notice_time', {'day': 0, 'date_time': "11:00"})
            param.json_update('notice_user_domains', get_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', get_notice_rule['filter_condition'])
            param.json_update('condition', get_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': get_notice_rule['issue_type_uuid']})
            resp_add = self.call(iss.AddNoticeRules, param)
            resp_add.check_response('code', 200)
        with step('点击 规则（截止日期） 删除 操作按钮'):
            resp = IssueAction.get_issue_notice_rule(issue_name='子任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(get_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story("T125236 工作项提醒：添加提醒规则（截止日期）（之后1天 14:00）")
    def test_sub_task_add_notice_rule_field013_after_day1(self, get_notice_rule):
        with step('添加提醒规则（截止日期）（之后1天 14:00）'):
            param = issue.add_notice_rules()[0]
            param.json_update('field_uuid', 'field013')  # 截止日期
            param.json_update('action', 'after')  # 当天 11:00
            param.json_update('notice_time', {'day': 1, 'date_time': "14:00"})
            param.json_update('notice_user_domains', get_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', get_notice_rule['filter_condition'])
            param.json_update('condition', get_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': get_notice_rule['issue_type_uuid']})
            resp_add = self.call(iss.AddNoticeRules, param)
            resp_add.check_response('code', 200)
        with step('点击 规则（截止日期） 删除 操作按钮'):
            resp = IssueAction.get_issue_notice_rule(issue_name='子任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(get_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story("T125267 工作项提醒：添加提醒规则（截止日期）（之前3天 09:00）")
    def test_sub_task_add_notice_rule_field013_before_day3(self, get_notice_rule):
        with step('添加提醒规则（截止日期）（之前3天 09:00）'):
            param = issue.add_notice_rules()[0]
            param.json_update('field_uuid', 'field013')  # 截止日期
            param.json_update('action', 'before')  # 当天 11:00
            param.json_update('notice_time', {'day': 3, 'date_time': "09:00"})
            param.json_update('notice_user_domains', get_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', get_notice_rule['filter_condition'])
            param.json_update('condition', get_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': get_notice_rule['issue_type_uuid']})
            resp_add = self.call(iss.AddNoticeRules, param)
            resp_add.check_response('code', 200)
        with step('点击 规则（截止日期） 删除 操作按钮'):
            resp = IssueAction.get_issue_notice_rule(issue_name='子任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(get_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story("T125110 工作项提醒：添加提醒规则（计划开始日期）（之后2天 14:00）")
    def test_sub_task_add_notice_rule_plan_start_time_after_day2(self, get_notice_rule):
        with step('添加提醒规则（计划开始日期）（之后2天 14:00）'):
            param = issue.add_notice_rules()[0]
            param.json_update('field_uuid', 'field027')  # 更新时间
            param.json_update('action', 'after')
            param.json_update('notice_time', {'day': 2, 'date_time': "14:00"})
            param.json_update('notice_user_domains', get_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', get_notice_rule['filter_condition'])
            param.json_update('condition', get_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': get_notice_rule['issue_type_uuid']})
            resp_add = self.call(iss.AddNoticeRules, param)
            resp_add.check_response('code', 200)
        with step('点击 计划开始日期 当时 提醒规则后的 删除 操作按钮'):
            resp = IssueAction.get_issue_notice_rule(issue_name='子任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(get_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story("T125125 工作项提醒：添加提醒规则（计划开始日期）（之前1天 09:00）")
    def test_sub_task_add_notice_rule_plan_start_time_before_day1(self, get_notice_rule):
        with step('添加提醒规则（计划开始日期）（之前1天 09:00）'):
            param = issue.add_notice_rules()[0]
            param.json_update('field_uuid', 'field027')  # 更新时间
            param.json_update('action', 'before')
            param.json_update('notice_time', {'day': 1, 'date_time': "09:00"})
            param.json_update('notice_user_domains', get_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', get_notice_rule['filter_condition'])
            param.json_update('condition', get_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': get_notice_rule['issue_type_uuid']})
            resp_add = self.call(iss.AddNoticeRules, param)
            resp_add.check_response('code', 200)
        with step('点击 计划开始日期 当时 提醒规则后的 删除 操作按钮'):
            resp = IssueAction.get_issue_notice_rule(issue_name='子任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(get_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story("T125165 工作项提醒：添加提醒规则（计划完成日期）（之后1天 14:00）")
    def test_sub_task_add_notice_rule_plan_end_time_after_day1(self, get_notice_rule):
        with step('添加提醒规则（计划完成日期）（之后1天）'):
            param = issue.add_notice_rules()[0]
            param.json_update('field_uuid', 'field028')  # 更新时间
            param.json_update('action', 'after')
            param.json_update('notice_time', {'day': 1, 'date_time': "14:00"})
            param.json_update('notice_user_domains', get_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', get_notice_rule['filter_condition'])
            param.json_update('condition', get_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': get_notice_rule['issue_type_uuid']})
            resp_add = self.call(iss.AddNoticeRules, param)
            resp_add.check_response('code', 200)
        with step('点击 计划完成日期 当时 提醒规则后的 删除 操作按钮'):
            resp = IssueAction.get_issue_notice_rule(issue_name='子任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(get_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story("T125192 工作项提醒：添加提醒规则（计划完成日期）（之前3天 09:00）")
    def test_sub_task_add_notice_rule_plan_end_time_before_day3(self, get_notice_rule):
        with step('添加提醒规则（计划完成日期）（之前3天）'):
            param = issue.add_notice_rules()[0]
            param.json_update('field_uuid', 'field028')  # 更新时间
            param.json_update('action', 'before')
            param.json_update('notice_time', {'day': 3, 'date_time': "09:00"})
            param.json_update('notice_user_domains', get_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', get_notice_rule['filter_condition'])
            param.json_update('condition', get_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': get_notice_rule['issue_type_uuid']})
            resp_add = self.call(iss.AddNoticeRules, param)
            resp_add.check_response('code', 200)
        with step('点击 计划完成日期 当时 提醒规则后的 删除 操作按钮'):
            resp = IssueAction.get_issue_notice_rule(issue_name='子任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(get_notice_rule['issue_type_uuid'], notice_rule_uuid)

    @story("T125062 工作项提醒：添加提醒规则（更新时间）（之后20小时）")
    def test_sub_task_notice_rule_plan_update_time_after_20hour(self, get_notice_rule):
        with step('添加提醒规则（更新时间）（之后20小时）'):
            param = issue.add_notice_rules()[0]
            param.json_update('field_uuid', 'field010')  # 更新时间
            param.json_update('action', 'after')
            param.json_update('notice_time', {'hour': 20})
            param.json_update('notice_user_domains', get_notice_rule['notice_user_domains'])
            param.json_update('filter_condition', get_notice_rule['filter_condition'])
            param.json_update('condition', get_notice_rule['condition'])
            param.uri_args({'issue_type_uuid': get_notice_rule['issue_type_uuid']})
            resp_add = self.call(iss.AddNoticeRules, param)
            resp_add.check_response('code', 200)
        with step('点击 计划完成日期 当时 提醒规则后的 删除 操作按钮'):
            resp = IssueAction.get_issue_notice_rule(issue_name='子任务')
            notice_rule_uuid = resp.value('notice_rules[0].uuid')
            IssueAction.del_notice_rule(get_notice_rule['issue_type_uuid'], notice_rule_uuid)
