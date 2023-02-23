"""
@Desc：项目报表-缺陷分析-缺陷创建者分布
@Author  ：zhangweiyu@ones.ai
"""
import copy
import json

from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, step
from falcons.helper import mocks

from main.actions.sprint import SprintAction
from main.actions.task import TaskAction
from main.actions.issue import IssueTypeAction
from . import ReportInfo
from main.params import filter

report_name = '缺陷创建者分布'


@fixture(scope='module', autouse=True)
def add_sprint():
    sprint_uuid = SprintAction.sprint_add()
    return sprint_uuid


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
class TestDefectCreatorDistribute(Checker):

    @story(f'T131852 缺陷创建者分布-编辑态-筛选：默认值')
    def test_defect_creator_default_filter_config(self, _report_key, _filter_config):
        config = ReportInfo.report_config(_report_key)
        with step('查看筛选数据来源'):
            assert config['filter'] == _filter_config, '筛选的默认配置不正确'

    @story(f'T131845 缺陷创建者分布-编辑态-分析维度（X轴）：默认值')
    def test_defect_creator_default_x_ais_config(self, _report_key):
        config = ReportInfo.report_config(_report_key)
        with step('查看x轴默认配置'):
            assert config['dimensions'][0]['field_uuid'] == 'field003', '默认维度不正确，应该是创建者'

            assert config['dimensions'][0]['limit'] == 10, '默认顺序显示个数错误'

            assert config['dimensions'][0]['order'] == 'asc' \
                   and config['dimensions'][0]['order_by'] == 'default', '默认没有按照升序排序'

    @story(f'T131850 缺陷创建者分布-编辑态-分析维度（Y轴）：默认值')
    def test_defect_creator_default_y_ais_config(self, _report_key):
        config = ReportInfo.report_config(_report_key)
        with step('查看y轴默认配置'):
            assert 'field_uuid' not in config['dimensions'][1].keys(), '选择维度不为空'

    @story(f'T131881 缺陷创建者分布：查看态')
    def test_defect_creator_report_type(self, _report_key, add_sprint):
        report_type = ReportInfo.report_type(_report_key)

        assert report_type == 'task_distribution'

    @story('T131861 缺陷创建者分布-编辑态：编辑筛选')
    def test_created_solved_defect_update_config(self, _report_key, add_sprint):
        config = ReportInfo.report_config(_report_key)
        new_config = copy.deepcopy(config)
        with step('编辑-添加筛选条件：所属迭代包含A，创建日期等于今天'):
            new_config['filter']['must'][1]['should'][0]['must'] += [{
                'in': {
                    'field_values.field011': [
                        add_sprint]
                }
            },
                {
                    'date_range': {
                        'field_values.field009': {
                            'equal': f'{mocks.date_today()}'
                        }
                    }
                }]
            ReportInfo.update_report_info(_report_key, {'config': json.dumps(new_config)})
