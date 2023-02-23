"""
@Desc：项目报表-需求按时交付情况分布
"""
from falcons.check import Checker, go
from falcons.com.nick import feature, story, fixture, step
from main.actions.task import TaskAction
from main.api import project as prj, task as ts
from main.params import more, task
from main.api.const.field import name_to_key
from . import ReportInfo


@fixture(scope='module')
def _report_key():
    report_key = ReportInfo.report_key(report_name)

    return report_key


@fixture(scope='module')
def report_config(_report_key, _storage):
    # 创建迭代
    sprint_uuid = TaskAction.sprint_add()

    _storage |= {'sprint': sprint_uuid}

    # 创建一个需求
    task_uuid = TaskAction.new_issue(issue_type_name='需求')[0]
    # 工作项选择所属迭代
    parm = task.task_detail_edit()[0]
    parm.json_update('tasks[0].uuid', task_uuid)
    parm.json['tasks'][0] |= {'field_values': [
        {
            "field_uuid": "field011",
            "type": 7,
            "value": sprint_uuid
        }
    ]}
    go(ts.TaskUpdate3, parm)

    config = ReportInfo.report_config(_report_key)

    return config


@fixture(scope='module')
def _storage():
    return {}


report_name = '需求按时交付情况分布'


@feature('需求按时交付情况分布')
class TestDemandDeliverySituation(Checker):

    @story('139208 需求按时交付情况-编辑态-分析维度（X轴）： 排序方式')
    def test_demand_delivery_situation_x_axis_sort(self, report_config, _report_key):
        # 按降序排序
        report_config['dimensions'][0]['order'] = 'asc'

        ReportInfo.update_report_info(_report_key, {'config': report_config})

    @story('139218 需求按时交付情况-编辑态：编辑分析维度（X轴）')
    def test_demand_delivery_situation_edit_x_axis(self, report_config, _report_key):
        with step('切换属性默认升序排序'):
            report_config['dimensions'][0]['order'] = 'desc'

        with step('切换‘选择维度’为工作项类型，然后升序'):
            report_config['dimensions'][0]['field_uuid'] = name_to_key('工作项类型')

            ReportInfo.update_report_info(_report_key, {'config': report_config})

        with step('切换‘选择维度’为需求数升序'):
            report_config['dimensions'][0]['order_by'] = 'task_count'

            ReportInfo.update_report_info(_report_key, {'config': report_config})

        with step('切换‘选择维度’为需求数升序'):
            report_config['dimensions'][0]['order_by'] = 'demand_delivered_count'

            ReportInfo.update_report_info(_report_key, {'config': report_config})

    @story('139223 需求按时交付情况-编辑态：编辑筛选')
    def test_demand_delivery_situation_edit_filter(self, report_config, _report_key, _storage):
        with step('清空筛选条件，添加筛选为：所属迭代包含A'):
            report_config['filter']['must'][1] = {
                'should': [{'must': [{'in': {'field_values.field011': [_storage['sprint']]}}]}]}

            ReportInfo.report_peek('demand_delivery_situation', report_config)

        with step('添加筛选条件为：创建时间 等于 今天'):
            report_config['filter']['must'][1]['should'][0]['must'].append({
                "date_range": {
                    "field_values.field009": {
                        "equal": "today"
                    }
                }
            })

            ReportInfo.update_report_info(_report_key, {'config': report_config})

    @story('139239 需求按时交付情况：查看态')
    def test_demand_delivery_situation_data_source(self, report_config):
        resp = ReportInfo.report_peek('demand_delivery_situation', report_config)

        labels = [lab['label'] for lab in resp.value('datasets')]

        if labels:
            assert '需求数' in labels

    @story('139219 需求按时交付情况-编辑态：编辑分析指标（Y轴）')
    def test_demand_delivery_situation_edit_y_axis(self, report_config, _report_key):
        with step('点击‘编辑’；分析指标（Y轴）-关闭‘需求数’'):
            report_config['dimensions'][1]['config']['show_demand_count'] = False

        with step('分析指标（Y轴）-关闭‘按时交付需求数’'):
            report_config['dimensions'][1]['config']['show_punctuality_demand_count'] = False

            resp = ReportInfo.report_peek('demand_delivery_situation', report_config)
            resp.check_response('total', 0)

        with step('点击保存'):
            ReportInfo.update_report_info(_report_key, {'config': report_config})

    @story('139240 需求按时交付情况：导出报表')
    def test_demand_delivery_situation_export(self):
        """"""

    @story('139241 需求按时交付情况：另存为')
    def test_demand_delivery_situation_save(self):
        """"""

    @story('139242 需求按时交付情况：图表详情数据源')
    def test_demand_delivery_situation_data_source(self):
        """"""

    @story('139243 需求按时交付情况：删除')
    def test_demand_delivery_situation_delete(self):
        """"""