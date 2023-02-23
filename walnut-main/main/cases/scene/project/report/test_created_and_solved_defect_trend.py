"""
@Desc：项目报表-缺陷分析-缺陷创建量与解决量趋势
@Author  ：zhangweiyu@ones.ai
"""
import json

from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, step

from main.actions.task import TaskAction
from main.actions.issue import IssueTypeAction
from . import ReportInfo
from main.params import filter

report_name = '缺陷创建量与解决量趋势'


@fixture(scope='module')
def _report_key():
    # 创建一个缺陷任务
    TaskAction.new_issue(issue_type_name='缺陷')

    report_key = ReportInfo.report_key(report_name)

    return report_key


@fixture(scope='module')
def _storage():
    return {}


@fixture(scope='module')
def _filter_config():
    issue_types = IssueTypeAction.get_issue_types()
    defect_uuid = [i['uuid'] for i in issue_types if i['name'] == '缺陷'][0]
    sub_demand_uuid = [i['uuid'] for i in issue_types if i['name'] == '子需求'][0]
    sub_task_uuid = [i['uuid'] for i in issue_types if i['name'] == '子任务'][0]
    config = filter.defect_report_default_filter(defect_uuid, [sub_demand_uuid, sub_task_uuid])
    return config


@feature(f'缺陷分析')
class TestCreateAndSolveDefectTrend(Checker):

    @story('T24344 缺陷创建量与解决量趋势：查看默认配置')
    def test_created_solved_defect_default_config(self, _report_key, _filter_config):
        config = ReportInfo.report_config(_report_key)
        with step('查看分析维度（X轴）'):
            assert config['dimensions'][0]['date_interval'] == '1d'
            assert config['dimensions'][0]['date_range'] == '30d'
        with step('查看分析指标（Y轴）'):
            assert config['dimensions'][1]['config']['show_created_amount'], 'Y轴-缺陷创建量，没有开启'
            assert config['dimensions'][1]['config']['show_solved_amount'], 'Y轴-缺陷解决量，没有开启'
        with step('查看筛选数据来源'):
            assert config['filter'] == _filter_config, '筛选器的默认配置不正确'

    @story('T131819 缺陷创建量与解决量趋势-编辑报表：修改分析维度（X轴）选项值')
    def test_created_solved_defect_update_config(self, _report_key):
        config = ReportInfo.report_config(_report_key)
        with step('修改分析维度（X轴）选项'):
            config['dimensions'][0]['date_range'] = '7d'
            ReportInfo.update_report_info(_report_key, {'config': config})

    @story('T131841 缺陷创建量与解决量趋势：图表详情数据源')
    def test_created_solved_defect_data_source(self, _report_key):
        config = ReportInfo.report_config(_report_key)
        resp = ReportInfo.report_peek("defect_created_solved_trend", config)
        labels = set([lab['label'] for lab in resp.value('datasets')])
        assert {'缺陷创建量', '缺陷解决量'} == labels
