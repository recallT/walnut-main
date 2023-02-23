"""
@Desc：项目报表-成员 (登记人)-迭代工时总览
"""
from falcons.check import Checker, go
from falcons.com.nick import feature, story, fixture, step

from main.actions.task import TaskAction
from main.api import project as prj, task as ts
from main.params import more, task
from . import ReportInfo


@fixture(scope='module')
def _report_key():
    report_key = ReportInfo.report_key(report_name)

    return report_key


@fixture(scope='module')
def report_config(_report_key):
    # 创建一个任务
    task_uuid = TaskAction.new_issue()[0]
    # 添加预计工时
    param = task.assess_man_hour()[0]
    param.uri_args({'task_uuid': task_uuid})
    go(ts.TaskAssessManHourUpdate, param)
    # 登记工时
    parm = task.add_man_hour()[0]
    parm.json_update('variables.task', task_uuid)
    go(prj.ItemGraphql, parm)

    config = ReportInfo.report_config(_report_key)

    return config


@fixture(scope='module')
def _storage():
    return {}


report_name = '成员 (登记人)-迭代工时总览'


@feature('成员 (登记人)-迭代工时总览报表操作')
class TestManHourOverview(Checker):

    @story('142503 「成员（登记人）-迭代工时总览」-编辑态-筛选：默认值')
    def test_manhour_overview_filter_default(self, report_config):
        with step('筛选条件为空'):
            default = []
            for m in report_config['filter']['must']:
                default += list(m.keys())

            assert 'should' not in default

    @story('142528 「成员（登记人）-迭代工时总览」：图表详情数据源')
    def test_manhour_overview_data_source(self, report_config):
        resp = ReportInfo.report_peek('manhour_overview', report_config)

        labels = [lab['label'] for lab in resp.value('datasets')]

        if labels:
            assert '未设置' in labels

    @story('142508 「成员（登记人）-迭代工时总览」-编辑态：编辑分析维度（X轴）')
    def test_manhour_overview_edit_x_axis(self, report_config, _report_key):
        with step('切换‘选择维度’ 部门，按属性默认降序排序'):
            report_config['dimensions'][0]['aggregation'] = 'department'
            report_config['dimensions'][0]['order_by'] = 'default'

            ReportInfo.update_report_info(_report_key, {'config': report_config})

        with step('切换属性默认升序排序'):
            report_config['dimensions'][0]['order'] = 'asc'
            ReportInfo.report_peek('manhour_overview', report_config)

        with step('切换‘排序方式’为按合计登记工时 降序'):
            report_config['dimensions'][0]['order_by'] = 'record_manhour'
            report_config['dimensions'][0]['order'] = 'desc'

            ReportInfo.update_report_info(_report_key, {'config': report_config})

    @story('142509 「成员（登记人）-迭代工时总览」-编辑态：编辑分析维度（Y轴）')
    def test_manhour_overview_edit_y_axis(self, report_config, _report_key):
        with step('选择维度：工作项，按顺序显示前 10 个选项值，按属性默认 降序'):
            report_config['dimensions'][1]['aggregation'] = 'task'

            ReportInfo.update_report_info(_report_key, {'config': report_config})

        with step('选择维度：周，按顺序显示前 10 个选项值，按合计登记工时 降序'):
            report_config['dimensions'][1]['aggregation'] = 'user'
            report_config['dimensions'][1]['order_by'] = 'record_manhour'
            report_config['dimensions'][1]['order'] = 'asc'

            ReportInfo.update_report_info(_report_key, {'config': report_config})

    @story('142513 「成员（登记人）-迭代工时总览」-编辑态：编辑筛选')
    def test_manhour_overview_edit_filter(self, report_config, _report_key):
        with step('存在迭代A'):
            sprint_uuid = TaskAction.sprint_add()

        with step('清空筛选条件，添加筛选为：所属迭代包含A'):
            report_config['filter']['must'].append(
                {'should': [{'must': [{'in': {'field_values.field011': [sprint_uuid]}}]}]})

            ReportInfo.report_peek('manhour_overview', report_config)

        with step('添加筛选条件为：创建时间 等于 今天'):
            report_config['filter']['must'][1]['should'][0]['must'].append({
                "date_range": {
                    "field_values.field009": {
                        "equal": "today"
                    }
                }
            })

            ReportInfo.update_report_info(_report_key, {'config': report_config})

    @story('142514 「成员（登记人）-迭代工时总览」-编辑态：分析维度（X轴）默认值')
    def test_manhour_overview_x_axis_default(self):
        """"""

    @story('142516 「成员（登记人）-迭代工时总览」-编辑态：分析维度（Y轴）默认值')
    def test_manhour_overview_y_axis_default(self):
        """"""

    @story('142527 「成员（登记人）-迭代工时总览」：另存为')
    def test_manhour_overview_save(self, report_config, _storage):
        parm = more.proj_report_categories()[0]
        resp = self.call(prj.ItemGraphql, parm)

        group_uuid = [c['uuid'] for c in resp.value('data.reportCategories') if c['name'] == '工时分析'][0]

        with step('调整报表名称,另存为'):
            rep_key = ReportInfo.report_save_as('manhour_overview', group_uuid, report_config)

            _storage |= {'rep_key': rep_key}

    @story('142528 成员（登记人）-迭代工时总览：删除')
    def test_manhour_overview_delete(self, report_config, _storage):
        with step('删除另存为的报表'):
            param = more.proj_report_delete(_storage['rep_key'])[0]
            resp = self.call(prj.ItemGraphql, param)

            resp.check_response('data.deleteProjectReport.key', _storage['rep_key'])
