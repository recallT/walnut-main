"""
@Desc：项目报表-重开缺陷分布
"""
import json

from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, step, mark
from falcons.com.meta import ApiMeta
from main.actions.task import TaskAction, team_stamp, proj_team_stamp
from main.api import project as prj
from main.api.const.field import name_to_key
from main.params import more
from . import ReportInfo


@fixture(scope='module')
def _report_key():
    # 创建一个缺陷任务
    TaskAction.new_issue(issue_type_name='缺陷')

    report_key = ReportInfo.report_key(report_name)

    return report_key


@fixture(scope='module')
def _storage():
    return {}


report_name = '重开缺陷分布'
label = ApiMeta.env.label


@mark.skipif(label == 'private' or label == 'dev', reason='因环境状态不一致，跳过用例')
@feature('重开缺陷分布报表')
class TestReopenDefectDistribute(Checker):

    @story('141431 重开缺陷分布-更多：重命名')
    def test_reopen_defect_rename(self, _report_key):
        with step('点击‘更多’-‘重命名’，编辑报表名称'):
            ReportInfo.update_report_info(_report_key, {'name': report_name})

    @story('141410 重开缺陷分布-编辑态：编辑分析维度（Y轴）')
    def test_reopen_defect_edit_y_axis(self, _report_key):
        config = ReportInfo.report_config(_report_key)

        with step('关闭‘缺陷总数’'):
            config['dimensions'][1]['config']['show_defect_count'] = False  # 关闭缺陷总数

            ReportInfo.update_report_info(_report_key, {'config': config})

    @story('141416 重开缺陷分布-编辑态：修改分析维度（X轴）为单行文本')
    def test_reopen_defect_edit_x_axis(self, _report_key):
        config = ReportInfo.report_config(_report_key)

        with step('切换属性默认升序排序'):
            config['dimensions'][0]['order'] = 'desc'

        with step('切换‘选择维度’为工作项升序'):
            config['dimensions'][0]['field_uuid'] = name_to_key('工作项类型')

            ReportInfo.update_report_info(_report_key, {'config': config})

        with step('切换‘选择维度’为工作项降序'):
            config['dimensions'][0]['order'] = 'asc'

            ReportInfo.update_report_info(_report_key, config)

    @story('141418 重开缺陷分布-编辑态：指定缺陷重开工作流(默认目标状态)')
    def test_reopen_defect_default_workflow(self, _report_key):
        config = ReportInfo.report_config(_report_key)
        # 获取指定缺陷工作流的默认目标状态
        pre_statuses = [p for p in config['dimensions'][1]['config']['pre_statuses']]

        # 无法指定缺陷重开工作流的目标状态：重新打开
        # assert len(pre_statuses) == 3

    @story('141429 重开缺陷分布-更多：添加到仪表盘（项目概览）')
    def test_reopen_defect_add_proj_overview(self, _report_key):
        # 获取项目概览组件uuid
        stamp_resp = proj_team_stamp({'component': 0})
        c_uuid = [d['uuid'] for d in stamp_resp['component']['components'] if '概览' in d['name']][0]
        # 报表uuid
        report_uuid = _report_key.split('-')[1]

        with step('更多-添加到仪表盘-项目概览'):
            param = more.report_add_dashboard_proj_overview(report_uuid, c_uuid, report_name)[0]
            resp = self.call(prj.ItemGraphql, param)

            resp.value('data.addCard.key')

    @story('141430 重开缺陷分布-更多：添加到仪表盘（仪表盘）')
    def test_reopen_defect_add_dashboard(self, _report_key):
        # 获取仪表盘uuid
        stamp_resp = team_stamp({'dashboard': 0})
        d_uuid = [d['uuid'] for d in stamp_resp['dashboard']['dashboards'] if d['pinned'] == True][0]

        # 报表uuid
        report_uuid = _report_key.split('-')[1]

        with step('更多-添加到仪表盘'):
            param = more.report_add_dashboard_card(report_uuid, d_uuid, report_name)[0]
            param.uri_args({'dashboard_uuid': d_uuid})
            resp = self.call(prj.DashboardCardAdd, param)

            resp.check_response('card.dashboard_uuid', d_uuid)

    @story('141423 重开缺陷分布-更多：更改所属分组')
    def test_reopen_defect_update_group(self, _report_key, _storage):
        with step('前置条件'):
            # 存在分组A
            param = more.proj_report_add_group()[0]
            resp = self.call(prj.ItemGraphql, param)

            group_key = resp.value('data.addReportCategory.key')
            group_uuid = group_key.split('-')[1]

            _storage |= {'group_uuid': group_uuid}

        with step('更改所属分组，选择分组A'):
            par = more.report_update_group(_report_key, group_uuid)[0]
            self.call(prj.ItemGraphql, par)

            # 校验分组下报表数量+1
            parm = more.get_proj_report()[0]
            res = self.call(prj.ItemGraphql, parm)
            g_key = [u['key'] for u in res.value('data.projectReports') if u['reportCategory']['uuid'] == group_uuid]

            assert len(g_key) == 1

    @story('141407 重开缺陷分布-编辑态-分析维度（X轴）：选项值')
    def test_reopen_defect_latitude_default(self):
        """"""

    @story('141414 重开缺陷分布-编辑态：编辑指定缺陷重开工作流')
    def test_reopen_defect_edit_status(self, _report_key):
        # 获取状态：已验证 uuid
        stamp_resp = proj_team_stamp({'transition': 0})
        scope_uuid = \
            [s['issue_type_scope_uuid'] for s in stamp_resp['transition']['transitions'] if s['name'] == '已验证'][0]
        end_status_uuid = \
            [s['end_status_uuid'] for s in stamp_resp['transition']['transitions'] if s['name'] == '已验证'][0]

        with step('目标变更状态为：已验证'):
            param = more.issue_type_scope_equal(scope_uuid, end_status_uuid)[0]
            res = self.call(prj.ItemGraphql, param)

        with step('开始状态选择：已修复'):
            status_uuid = [u['startStatus']['uuid'] for u in res.value('data.transitions') if
                           u['startStatus']['name'] == '已修复']

            config = ReportInfo.report_config(_report_key)
            config['dimensions'][1]['pre_statuses'] = status_uuid
            config['dimensions'][1]['reopen_status'] = end_status_uuid

            ReportInfo.update_report_info(_report_key, {'config': config})

    @story('141432 重开缺陷分布：导出报表')
    def test_reopen_defect_export_report(self, _report_key):
        config = ReportInfo.report_config(_report_key)
        report_uuid = _report_key.split('-')[1]

        with step('重开缺陷分布，点击删除'):
            text = ReportInfo.export_report('defect_reopen_distribution', report_uuid, config)

            if text != '\n':
                assert '缺陷总数' in text

    @story('141433 重开缺陷分布：另存为')
    def test_reopen_defect_save(self, _report_key, _storage):
        config = ReportInfo.report_config(_report_key)

        with step('调整报表名称,另存为'):
            param = more.add_proj_report('defect_reopen_distribution', _storage['group_uuid'])[0]
            param.json_update('variables.config', json.dumps(config))
            resp = self.call(prj.ItemGraphql, param)

            new_rep_key = resp.value('data.addProjectReport.key')

            _storage |= {'rep_key': new_rep_key}

        # with step('清理分组数据'):
        #     # 清除新建的分组和报表数据
        #     d = more.group_report_delete()
        #     d['variables']['key'] = _group_uuid[0]
        #     param = more.graphql_body(d)[0]
        #
        #     self.call(prj.ItemGraphql, param)

    @story('141425 重开缺陷分布-更多：删除')
    def test_reopen_defect_delete(self, _storage):
        with step('删除另存为的报表'):
            param = more.proj_report_delete(_storage['rep_key'])[0]
            resp = self.call(prj.ItemGraphql, param)

            resp.check_response('data.deleteProjectReport.key', _storage['rep_key'])

    @story('141436 重开缺陷分布：图表详情数据源')
    def test_reopen_defect_data_source(self, _report_key):
        config = ReportInfo.report_config(_report_key)

        resp = ReportInfo.report_peek('defect_reopen_distribution', config)

        labels = set([lab['label'] for lab in resp.value('datasets')])

        if labels:
            assert {'缺陷总数', '重开缺陷数', '缺陷重开率'} == labels
