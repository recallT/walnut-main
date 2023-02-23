"""
@Desc：项目报表-缺陷分析-缺陷解决者停留时间分布
"""
import copy

from falcons.check import Checker
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture, step
from main.actions.issue import IssueTypeAction
from main.helper.extra import Extra
from . import ReportInfo, get_defect_severity_default_di_value
from main.params import filter
from main.actions.pro import PrjAction
import time

report_name = '缺陷解决者停留时间分布'


@fixture(scope='module', autouse=True)
def add_project():
    # 创建一个单独项目
    time.sleep(2)
    project_uuid = PrjAction.new_project(index=3, name=f'Apitest-报表-{report_name}')
    return project_uuid


@fixture(scope='module', autouse=True)
def del_project(add_project):
    yield
    # 清除项目数据
    creator = Extra(ApiMeta)
    creator.del_project(add_project)


@fixture(scope='module')
def _report_key(add_project):
    report_key = ReportInfo.report_key(report_name, project_uuid=add_project)
    return report_key


@fixture(scope='module')
def _filter_config(add_project):
    issue_types = IssueTypeAction.get_issue_types()
    defect_uuid = [i['uuid'] for i in issue_types if i['name'] == '缺陷'][0]
    sub_demand_uuid = [i['uuid'] for i in issue_types if i['name'] == '子需求'][0]
    sub_task_uuid = [i['uuid'] for i in issue_types if i['name'] == '子任务'][0]
    config = filter.defect_report_default_filter(defect_uuid, [sub_demand_uuid, sub_task_uuid],
                                                 project_uuid=add_project)
    return config


@feature(f'缺陷分析-{report_name}')
class TestDefectSolverStayTimeDistribute(Checker):

    @story(f'T151210 缺陷分析-缺陷解决者停留时间分布报表：默认报表配置')
    def test_defect_solver_stay_time_default_config(self, add_project, _report_key, _filter_config):
        config: dict = ReportInfo.report_config(_report_key, project_uuid=add_project)
        with step('检查图标类型'):
            typ = ReportInfo.report_type(_report_key, project_uuid=add_project)
            assert typ == 'single_selection_stay_duration'
        with step('检查x轴配置'):
            assert len(config['dimensions']) == 1
            assert config['dimensions'][0] == {
                'aggregation': 'terms',
                'field_uuid': 'field040'
            }
        with step('检查筛选配置'):
            assert config['filter'] == _filter_config
