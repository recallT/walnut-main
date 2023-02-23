"""
@Desc：项目报表-任务状态分布
"""
from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, step

from main.actions.task import TaskAction
from main.api import project as prj
from main.api.const.field import name_to_key
from main.params import more
from . import ReportInfo


@fixture(scope='module')
def _report_key():
    report_key = ReportInfo.report_key(report_name)

    return report_key


@fixture(scope='module')
def report_config(_report_key):
    # 创建一个任务
    TaskAction.new_issue()

    config = ReportInfo.report_config(_report_key)

    return config


@fixture(scope='module')
def _storage():
    return {}


report_name = '任务状态分布'


@feature('任务状态分布报表')
class TestTaskDistribute(Checker):

    @story('134518 任务状态分布-编辑态-分析维度（X轴）：默认值')
    def test_task_distribute_x_axis_default(self, report_config):
        # 默认为状态
        assert name_to_key('状态') in report_config['dimensions'][0]['field_uuid']
        # 排序默认 升序排序
        assert 'asc' in report_config['dimensions'][0]['order']

    @story('134517 任务状态分布-编辑态-分析维度（X轴）： 排序方式')
    def test_task_distribute_x_axis_sort(self, report_config, _report_key):
        # 按降序排序
        report_config['dimensions'][0]['order'] = 'desc'

        ReportInfo.update_report_info(_report_key, {'config': report_config})

    @story('134520 任务状态分布-编辑态-分析维度（Y轴）：默认值')
    def test_task_distribute_y_axis_default(self, report_config):
        with step('分析维度（Y轴）默认为选择维度为空'):
            y_axis = list(report_config['dimensions'][1].keys())  # 获取y轴的字段key

            assert 'field_uuid' not in y_axis

    @story('134522 任务状态分布-编辑态-筛选：默认值')
    def test_task_distribute_filter_default(self, report_config):
        issue_uuid = TaskAction.issue_type_uuid()
        sub_task_uuid = TaskAction.issue_type_uuid('子任务')
        sub_demand_uuid = TaskAction.issue_type_uuid('子需求')

        must = [m['should'][0]['must'] for m in report_config['filter']['must'] if 'should' in m][0]

        include = [m['in']['field_values.field007'] for m in must if 'in' in m][0]
        not_contain = [m['not_in']['field_values.field021'] for m in must if 'not_in' in m][0]

        with step('查看‘筛选’，工作项类型-包含-任务'):
            assert issue_uuid == include

        with step('子工作项类型-不包含-子需求、子任务'):
            assert sub_task_uuid[0], sub_demand_uuid[0] in not_contain

    @story('134548 任务状态分布：导出报表')
    def test_task_distribute_export_report(self, report_config, _report_key):
        report_uuid = _report_key.split('-')[1]

        with step('重开缺陷分布，点击删除'):
            text = ReportInfo.export_report('task_distribution', report_uuid, report_config)

            if '工作项数量' in text:
                assert '工作项数量' in text

    @story('134550 任务状态分布：图表详情数据源')
    def test_task_distribute_data_source(self, report_config):
        resp = ReportInfo.report_peek('task_distribution', report_config)

        labels = [lab['label'] for lab in resp.value('datasets')]

        if '工作项数量' in labels:
            assert '工作项数量' in labels

    @story('134527 任务状态分布-编辑态：编辑分析维度（X轴）')
    def test_task_distribute_edit_x_axis(self, report_config, _report_key):
        with step('切换属性默认升序排序'):
            report_config['dimensions'][0]['order'] = 'desc'

        with step('切换‘选择维度’为工作项类型，然后升序'):
            report_config['dimensions'][0]['field_uuid'] = name_to_key('工作项类型')

            ReportInfo.update_report_info(_report_key, {'config': report_config})

        with step('切换‘选择维度’为工作项降序'):
            report_config['dimensions'][0]['order'] = 'asc'

            ReportInfo.update_report_info(_report_key, {'config': report_config})

    @story('134532 任务状态分布-编辑态：编辑筛选')
    def test_task_distribute_edit_filter(self, report_config, _report_key):
        with step('存在迭代A'):
            sprint_uuid = TaskAction.sprint_add()

        with step('清空筛选条件，添加筛选为：所属迭代包含A'):
            report_config['filter']['must'][1]['should'][0]['must'] = [{'in': {'field_values.field011': [sprint_uuid]}}]

            ReportInfo.report_peek('task_distribution', report_config)

        with step('添加筛选条件为：创建时间 等于 今天'):
            report_config['filter']['must'][1]['should'][0]['must'].append({
                "date_range": {
                    "field_values.field009": {
                        "equal": "today"
                    }
                }
            })

            ReportInfo.update_report_info(_report_key, {'config': report_config})

    @story('134549 任务状态分布：另存为')
    def test_task_distribute_save(self, report_config, _storage):
        # 获取分组为 任务分析 uuid
        parm = more.proj_report_categories()[0]
        resp = self.call(prj.ItemGraphql, parm)

        group_uuid = [c['uuid'] for c in resp.value('data.reportCategories') if c['name'] == '任务分析'][0]

        with step('调整报表名称,另存为'):
            rep_key = ReportInfo.report_save_as('task_distribution', group_uuid, report_config)

            _storage |= {'rep_key': rep_key}

    @story('任务状态分布：删除')
    def test_task_distribute_delete(self, _storage):
        with step('删除另存为的报表'):
            param = more.proj_report_delete(_storage['rep_key'])[0]
            resp = self.call(prj.ItemGraphql, param)

            resp.check_response('data.deleteProjectReport.key', _storage['rep_key'])
