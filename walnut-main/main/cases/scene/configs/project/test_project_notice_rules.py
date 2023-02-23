# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_project_notice_rules.py
@Author  ：zhangyonghui@ones.ai
@Date    ：7/20/22 3:02 PM 
@Desc    ：配置中心-Project 工作项提醒
"""
import time

from falcons.check import Checker, go
from falcons.com.nick import feature, fixture, story, step

from main.actions.task import TaskAction
from main.api import issue
from main.params import issue as ss
from main.actions.issue import IssueAction as Ia


@fixture(scope='module', autouse=True)
def get_issue_uuid():
    issue_type_uuid = TaskAction.issue_type_uuid('任务')[0]
    return issue_type_uuid


@fixture(scope='module', autouse=True)
def get_sub_task_issue_uuid():
    issue_type_uuid = TaskAction.issue_type_uuid('子任务')[0]
    return issue_type_uuid


@fixture(scope='module')
def add_global_notice_rule(get_issue_uuid):
    issue_type_uuid = get_issue_uuid
    param = ss.notice_rules()[0]
    param.uri_args({'issue_type_uuid': issue_type_uuid})
    resp = go(issue.GlobalNoticeRule, param)
    notice_user_domains = resp.value('notice_rules[0].notice_user_domains')
    filter_condition = resp.value('notice_rules[0].filter_condition')
    condition = resp.value('notice_rules[0].condition')

    notice = {'notice_user_domains': notice_user_domains,
              'filter_condition': filter_condition, 'condition': condition, 'issue_type_uuid': issue_type_uuid
              }

    return notice


@fixture(scope='module', autouse=True)
def del_notice_rule(get_issue_uuid):
    """统一删除新增的任务工作项提醒"""
    # 先查一遍数据 查询原始存在的数据
    param = ss.notice_rules()[0]
    param.uri_args({'issue_type_uuid': get_issue_uuid})
    resp = go(issue.GlobalNoticeRule, param)
    notice_uuids = [r['uuid'] for r in resp.value('notice_rules')]
    yield
    resp = go(issue.GlobalNoticeRule, param)
    new_notice_uuids = [r['uuid'] for r in resp.value('notice_rules')]
    del_uuids = list(set(new_notice_uuids) - set(notice_uuids))
    param = ss.notice_rules()[0]
    for i in del_uuids:
        param.uri_args({'issue_type_uuid': get_issue_uuid, 'notice_rule_uuid': i})
        resp = go(issue.DelGlobalNoticeRule, param)
        resp.check_response('code', 200)


@fixture(scope='module', autouse=True)
def del_sub_notice_rule(get_sub_task_issue_uuid):
    """统一删除新增的子任务工作项提醒"""
    # 先查一遍数据 查询原始存在的数据
    param = ss.notice_rules()[0]
    param.uri_args({'issue_type_uuid': get_sub_task_issue_uuid})
    resp = go(issue.GlobalNoticeRule, param)
    notice_uuids = [r['uuid'] for r in resp.value('notice_rules')]
    yield
    resp = go(issue.GlobalNoticeRule, param)
    new_notice_uuids = [r['uuid'] for r in resp.value('notice_rules')]
    del_uuids = list(set(new_notice_uuids) - set(notice_uuids))
    param = ss.notice_rules()[0]
    for i in del_uuids:
        param.uri_args({'issue_type_uuid': get_sub_task_issue_uuid, 'notice_rule_uuid': i})
        resp = go(issue.DelGlobalNoticeRule, param)
        resp.check_response('code', 200)


@feature('配置中心-Project 工作项提醒')
class TestGlobalIssueNoticeRules(Checker):

    @classmethod
    def get_global_notice_rules(cls, issue_type_uuid, token=None):
        param = ss.notice_rules()[0]
        param.uri_args({'issue_type_uuid': issue_type_uuid})
        resp = go(issue.GlobalNoticeRule, param, token)
        return resp

    @story('T125083 工作项提醒：添加提醒规则（计划开始日期）（当天 11:00）')
    @story('T124378 工作项提醒：编辑提醒规则')
    @story('T124886 工作项提醒：删除提醒规则')
    @story('124877 工作项提醒：删除提醒规则')
    def test_global_notice_rule_add_del_update(self, add_global_notice_rule):
        notice = add_global_notice_rule
        resp = self.get_global_notice_rules(issue_type_uuid=notice['issue_type_uuid'])
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field027')  # 计划开始时间
            param.json_update('action', 'that_day')
            param.json_update('notice_time', {'day': 0, 'date_time': "11:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': notice['issue_type_uuid']})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('编辑提醒规则'):
            time.sleep(2)
            resp_1 = self.get_global_notice_rules(notice['issue_type_uuid'])
            # 和原始数据取差集 取新增的rule_uuid
            notice_rule_uuid = list(set([r['uuid'] for r in resp_1.value('notice_rules')]) - set(
                [r['uuid'] for r in resp.value('notice_rules')]))[0]
            param.json_update('notice_types', ["notice_center", "email"])
            param.json_update('notice_time', {'day': 0, 'date_time': "14:00"})
            param.uri_args({'notice_rule_uuid': notice_rule_uuid})
            resp_add = self.call(issue.UpdateGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('删除提醒规则'):
            param = ss.notice_rules()[0]
            param.uri_args({'issue_type_uuid': notice['issue_type_uuid'], 'notice_rule_uuid': notice_rule_uuid})
            resp = go(issue.DelGlobalNoticeRule, param)
            resp.check_response('code', 200)

    @story('T125036 工作项提醒：添加提醒规则（更新时间）（当时）')
    def test_add_global_update_time(self, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field010')  # 更新时间
            param.json_update('action', 'now')
            param.json_update('notice_time', {'minute': 0})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': notice['issue_type_uuid']})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125033 工作项提醒：添加提醒规则（更新时间）（当时）--子任务')
    def test_add_global_sub_task_update_time(self, get_sub_task_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field010')  # 更新时间
            param.json_update('action', 'now')
            param.json_update('notice_time', {'minute': 0})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_sub_task_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125060 工作项提醒：添加提醒规则（更新时间）（之后20小时）')
    def test_add_global_task_update_time_after(self, get_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field010')  # 更新时间
            param.json_update('action', 'after')
            param.json_update('notice_time', {'hour': 20})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125059 工作项提醒：添加提醒规则（更新时间）（之后20小时）-子任务')
    def test_add_global_sub_task_update_time_after(self, get_sub_task_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field010')  # 更新时间
            param.json_update('action', 'after')
            param.json_update('notice_time', {'hour': 20})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_sub_task_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125100 工作项提醒：添加提醒规则（计划开始日期）（之后2天 14:00）--子任务')
    def test_add_sub_global_notice_rules_after_plan_time_14(self, get_sub_task_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field027')  # 计划开始时间
            param.json_update('action', 'after')
            param.json_update('notice_time', {'day': 2, 'date_time': "14:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_sub_task_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125111 工作项提醒：添加提醒规则（计划开始日期）（之后2天 14:00）')
    def test_add_global_notice_rules_after_plan_time_14(self, get_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field027')  # 计划开始时间
            param.json_update('action', 'after')
            param.json_update('notice_time', {'day': 2, 'date_time': "14:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125124 工作项提醒：添加提醒规则（计划开始日期）（之前1天 09:00）')
    def test_add_global_notice_rules_before_plan_time_09(self, get_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field027')  # 计划开始时间
            param.json_update('action', 'before')
            param.json_update('notice_time', {'day': 1, 'date_time': "09:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125114 工作项提醒：添加提醒规则（计划开始日期）（之前1天 09:00）--子任务')
    def test_add_global_notice_rules_start_plan_time_09(self, get_sub_task_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field027')  # 计划开始时间
            param.json_update('action', 'before')
            param.json_update('notice_time', {'day': 1, 'date_time': "09:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_sub_task_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125144 工作项提醒：添加提醒规则（计划完成日期）（当天 11:00）')
    def test_add_global_notice_rules_plan_end_time_11(self, get_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field028')  # 计划开始时间
            param.json_update('action', 'that_day')
            param.json_update('notice_time', {'day': 0, 'date_time': "11:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125157 工作项提醒：添加提醒规则（计划完成日期）（当天 11:00）--子任务')
    def test_add_global_sub_notice_rules_plan_end_time_11(self, get_sub_task_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field028')  # 计划开始时间
            param.json_update('action', 'that_day')
            param.json_update('notice_time', {'day': 0, 'date_time': "11:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_sub_task_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125174 工作项提醒：添加提醒规则（计划完成日期）（之后1天 14:00）')
    def test_add_global_notice_plan_end_time_after_1(self, get_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field028')  # 计划完成时间
            param.json_update('action', 'after')
            param.json_update('notice_time', {'day': 1, 'date_time': "14:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125174 工作项提醒：添加提醒规则（计划完成日期）（之后1天 14:00）---子任务')
    def test_add_global_sub_notice_plan_end_time_after_1(self, get_sub_task_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field028')  # 计划完成时间
            param.json_update('action', 'after')
            param.json_update('notice_time', {'day': 1, 'date_time': "14:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_sub_task_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125197 工作项提醒：添加提醒规则（计划完成日期）（之前3天 09:00）')
    @story('125184 工作项提醒：添加提醒规则（计划完成日期）（之前3天 09:00）')
    @story('125197 工作项提醒：添加提醒规则（计划完成日期）（之前3天 09:00）')
    def test_add_global_notice_plan_end_time_after3(self, get_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field028')  # 计划完成时间
            param.json_update('action', 'before')
            param.json_update('notice_time', {'day': 3, 'date_time': "09:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125184 工作项提醒：添加提醒规则（计划完成日期）（之前3天 09:00）---子任务')
    def test_add_global_notice_plan_end_time_after3(self, get_sub_task_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field028')  # 计划完成时间
            param.json_update('action', 'before')
            param.json_update('notice_time', {'day': 3, 'date_time': "09:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_sub_task_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125216 工作项提醒：添加提醒规则（截止日期）（当天 11:00）')
    def test_add_global_notice_expiration_date1(self, get_sub_task_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field013')  # 截止日期
            param.json_update('action', 'that_day')
            param.json_update('notice_time', {'day': 0, 'date_time': "11:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_sub_task_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125226 工作项提醒：添加提醒规则（截止日期）（之后1天 14:00）')
    def test_add_global_notice_expiration_date2(self, get_sub_task_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field013')  # 截止日期
            param.json_update('action', 'after')
            param.json_update('notice_time', {'day': 1, 'date_time': "14:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_sub_task_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T125265 工作项提醒：添加提醒规则（截止日期）（之前3天 09:00）')
    def test_add_global_notice_expiration_date3(self, get_sub_task_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        with step('配置中心新增提醒规则'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field013')  # 截止日期
            param.json_update('action', 'before')
            param.json_update('notice_time', {'day': 3, 'date_time': "09:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': get_sub_task_issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

    @story('T124972 工作项提醒：添加提醒规则（发布日期）（当天 11:00）')
    @story('T124991 工作项提醒：添加提醒规则（发布日期）（之后1天 14:00）')
    @story('T125024 工作项提醒：添加提醒规则（发布日期）（之前3天 09:00）')
    def test_add_sub_task_global_notice_expiration_deploy_date(self, get_sub_task_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        issue_uuid = get_sub_task_issue_uuid
        with step('前置条件，添加属性到工作项中'):
            Ia.add_field_into_issue(field_type=['field036'], issue_type=[issue_uuid])
        with step('添加提醒规则（发布日期）（当天 11:00）'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field036')  # 发布日期
            param.json_update('action', 'that_day')
            param.json_update('notice_time', {'day': 0, 'date_time': "11:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('添加提醒规则（发布日期）（之后1天 14:00）'):
            param.json_update('action', 'after')
            param.json_update('notice_time', {'day': 1, 'date_time': "14:00"})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

        with step('添加提醒规则（发布日期）（之前3天 09:00）'):
            param.json_update('action', 'before')
            param.json_update('notice_time', {'day': 1, 'date_time': "14:00"})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(issue_uuid, 'field036')

    @story('T124969 工作项提醒：添加提醒规则（发布日期）（当天 11:00）')
    @story('T125002 工作项提醒：添加提醒规则（发布日期）（之后1天 14:00）')
    @story('T125021 工作项提醒：添加提醒规则（发布日期）（之前3天 09:00）')
    def test_add_global_notice_expiration_deploy_date(self, get_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        issue_uuid = get_issue_uuid
        with step('前置条件，添加属性到工作项中'):
            Ia.add_field_into_issue(field_type=['field036'], issue_type=[issue_uuid])
        with step('添加提醒规则（发布日期）（当天 11:00）'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', 'field036')  # 发布日期
            param.json_update('action', 'that_day')
            param.json_update('notice_time', {'day': 0, 'date_time': "11:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('添加提醒规则（发布日期）（之后1天 14:00）'):
            param.json_update('action', 'after')
            param.json_update('notice_time', {'day': 1, 'date_time': "14:00"})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

        with step('添加提醒规则（发布日期）（之前3天 09:00）'):
            param.json_update('action', 'before')
            param.json_update('notice_time', {'day': 1, 'date_time': "14:00"})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(issue_uuid, 'field036')


    @story('T125280 工作项提醒：添加提醒规则（自定义日期）（当天 11:00）')
    @story('T125299 工作项提醒：添加提醒规则（自定义日期）（之后10天 14:00）')
    @story('T125312 工作项提醒：添加提醒规则（自定义日期）（之前10天 09:00）')
    def test_add_global_notice_expiration_date(self, get_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        issue_uuid = get_issue_uuid
        with step('前置条件，添加属性到工作项中'):
            field_uuid = Ia.global_add_field(field_type=5, issue_type=[issue_uuid])
        with step('添加提醒规则（发布日期）（当天 11:00）'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', field_uuid)  #
            param.json_update('action', 'that_day')
            param.json_update('notice_time', {'day': 0, 'date_time': "11:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('添加提醒规则（发布日期）（之后10天 14:00）'):
            param.json_update('action', 'after')
            param.json_update('notice_time', {'day': 10, 'date_time': "14:00"})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

        with step('添加提醒规则（发布日期）（之前10天 09:00）'):
            param.json_update('action', 'before')
            param.json_update('notice_time', {'day': 10, 'date_time': "14:00"})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(issue_uuid, field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T125274 工作项提醒：添加提醒规则（自定义日期）（当天 11:00）')
    @story('T125295 工作项提醒：添加提醒规则（自定义日期）（之后10天 14:00）')
    @story('T125323 工作项提醒：添加提醒规则（自定义日期）（之前10天 09:00）')
    def test_add_sub_task_global_notice_expiration_date(self, get_sub_task_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        issue_uuid = get_sub_task_issue_uuid
        with step('前置条件，添加属性到工作项中'):
            field_uuid = Ia.global_add_field(field_type=5, issue_type=[issue_uuid])
        with step('添加提醒规则（发布日期）（当天 11:00）'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', field_uuid)  #
            param.json_update('action', 'that_day')
            param.json_update('notice_time', {'day': 0, 'date_time': "11:00"})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('添加提醒规则（发布日期）（之后10天 14:00）'):
            param.json_update('action', 'after')
            param.json_update('notice_time', {'day': 10, 'date_time': "14:00"})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

        with step('添加提醒规则（发布日期）（之前10天 09:00）'):
            param.json_update('action', 'before')
            param.json_update('notice_time', {'day': 10, 'date_time': "14:00"})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(issue_uuid, field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T125348 工作项提醒：添加提醒规则（自定义时间）（当时）')
    @story('T125367 工作项提醒：添加提醒规则（自定义时间）（之后5天）')
    @story('T125392 工作项提醒：添加提醒规则（自定义时间）（之前30分钟）')
    def test_add_sub_task_global_notice_expiration_time(self, get_sub_task_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        issue_uuid = get_sub_task_issue_uuid
        with step('前置条件，添加属性到工作项中'):
            field_uuid = Ia.global_add_field(field_type=6, issue_type=[issue_uuid])
        with step('添加提醒规则（发布日期）（当天 11:00）'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', field_uuid)  #
            param.json_update('action', 'now')
            param.json_update('notice_time', {'minute': 0})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('添加提醒规则（发布日期）（之后10天 14:00）'):
            param.json_update('action', 'after')
            param.json_update('notice_time', {'day': 5})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

        with step('添加提醒规则（自定义时间）（之前30分钟）'):
            param.json_update('action', 'before')
            param.json_update('notice_time', {'minute': 30})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(issue_uuid, field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T125337 工作项提醒：添加提醒规则（自定义时间）（当时）')
    @story('T125369 工作项提醒：添加提醒规则（自定义时间）（之后5天）')
    @story('T125395 工作项提醒：添加提醒规则（自定义时间）（之前30分钟）')
    def test_add_task_global_notice_expiration_time(self, get_issue_uuid, add_global_notice_rule):
        notice = add_global_notice_rule
        issue_uuid = get_issue_uuid
        with step('前置条件，添加属性到工作项中'):
            field_uuid = Ia.global_add_field(field_type=6, issue_type=[issue_uuid])
        with step('添加提醒规则（发布日期）（当天 11:00）'):
            param = ss.add_notice_rules()[0]
            param.json_update('field_uuid', field_uuid)  #
            param.json_update('action', 'now')
            param.json_update('notice_time', {'minute': 0})
            param.json_update('notice_user_domains', notice['notice_user_domains'])
            param.json_update('filter_condition', notice['filter_condition'])
            param.json_update('condition', notice['condition'])
            param.uri_args({'issue_type_uuid': issue_uuid})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('添加提醒规则（发布日期）（之后10天 14:00）'):
            param.json_update('action', 'after')
            param.json_update('notice_time', {'day': 5})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)

        with step('添加提醒规则（自定义时间）（之前30分钟）'):
            param.json_update('action', 'before')
            param.json_update('notice_time', {'minute': 30})
            resp_add = self.call(issue.AddGlobalNoticeRule, param)
            resp_add.check_response('code', 200)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(issue_uuid, field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)
