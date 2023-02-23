"""
@Desc：项目报表-缺陷分析-缺陷DI负责人比较
@Author  ：zhangweiyu@ones.ai
"""
import copy
import json

from falcons.check import Checker
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture, step

from main.actions.issue import IssueAction
from main.actions.task import TaskAction
from main.actions.pro import PrjAction
from main.api import task as tk, project as prj
from main.helper.extra import Extra
from main.params.const import ACCOUNT
from main.params import more

from . import ReportInfo, get_defect_severity_default_di_value
import time

report_name = '缺陷 DI 值负责人比较'


@fixture(scope='module', autouse=True)
def add_project():
    # 创建一个单独项目
    time.sleep(2)
    project_uuid = PrjAction.new_project(index=3, name=f'Apitest-报表-{report_name}')
    yield project_uuid
    # 清除项目数据
    creator = Extra(ApiMeta)
    creator.del_project(project_uuid)


@fixture(scope='module')
def add_bugs(add_project) -> [str]:
    issue_uuids = []
    for i in range(3):
        issue_uuid = TaskAction.new_issue(issue_type_name='缺陷', proj_uuid=add_project)
        issue_uuids.append(issue_uuid)
    return issue_uuids


@fixture(scope='module')
def _report_key(add_project):
    report_key = ReportInfo.report_key(report_name, project_uuid=add_project)
    return report_key


@feature(f'缺陷分析')
class TestDefectDIOwnerCompare(Checker):

    @story(f'T131896 {report_name}-编辑报表：编辑图表x轴')
    def test_defect_dioc_x_config(self, add_project, _report_key, add_bugs: [str]):
        config: dict = ReportInfo.report_config(_report_key, project_uuid=add_project)
        with step('检查选择维度默认值'):
            assert config['dimensions'][0]['field_uuid'] == 'field004', 'x轴默认不是负责人'
            assert config['dimensions'][0]['order'] == 'asc', 'x轴默认不是顺序排序'
            assert config['dimensions'][0]['limit'] == 10, 'x轴默认不是显示前10'
            assert config['dimensions'][0]['aggregation'] == 'terms'
        with step('检查排序方式默认选项'):
            assert config['dimensions'][0]['order_by'] == 'default'
        with step('切换排序方式=DI值'):
            edit_config = copy.deepcopy(config)
            edit_config['dimensions'][0]['order_by'] = 'defect_di_value'
            ReportInfo.report_peek('defect_di_value_distribution', edit_config).json()

    @story(f'T131902 {report_name}-编辑报表：缺陷严重程度的权重属性值')
    def test_defect_dioc_severity_options(self, add_project, _report_key):
        config: dict = ReportInfo.report_config(_report_key, project_uuid=add_project)
        with step('检查缺陷严重程度的权重属性值对应默认值'):
            severity_level_weight = config['dimensions'][1]['config']['severity_level_weight']
            actual_options_uuids = [s['uuid'] for s in severity_level_weight]
            # 获取属性-严重程度的选项配置
            severity_options = PrjAction.get_severity_level()
            expect_options_uuids = [p['uuid'] for p in severity_options]
            assert len(severity_level_weight) == len(severity_options), '严重程度DI配置项个数不对'
            assert actual_options_uuids == expect_options_uuids

    @story(f'T131903 {report_name}-编辑报表：缺陷严重程度的权重属性值对应默认值')
    def test_defect_dioc_severity_config(self, add_project, _report_key):
        config: dict = ReportInfo.report_config(_report_key, project_uuid=add_project)
        with step('检查缺陷严重程度的权重属性值对应默认值'):
            # 获取属性-严重程度的选项配置
            expect_y_config = get_defect_severity_default_di_value()
            assert config['dimensions'][1]['config']['severity_level_weight'] == expect_y_config

    @story('T44250 报表配置：报表另存为')
    def test_defect_dioc_save_as(self, add_project, _report_key):
        report_info = ReportInfo.report_info(_report_key, project_uuid=add_project)
        groups = PrjAction.get_report_groups(project_uuid=add_project)
        demand_group = [g for g in groups if g['name'] == '需求分析'][0]
        with step('报表另存为'):
            k = ReportInfo.report_save_as(report_info['reportType'], demand_group['uuid'],
                                          report_info['config'], project_uuid=add_project)
            assert k, '检查点失败：报表另存为成功'

        with step('查看报表列表'):
            rl = ReportInfo.report_list(project_uuid=add_project)
            rr = [r for r in rl if r['key'] == k]
            assert rr, '检查点失败：报表列表展示另存为的新报表'
            r = rr[0]
            assert r['reportCategory']['uuid'] == demand_group['uuid'], '检查点失败：所属分组为需求分析'
            assert r['config'] == json.dumps(report_info['config']), '检查点失败：与原报表数据不一致'

    @story('T44252 报表配置：报表重命名')
    def test_defect_dioc_rename(self, add_project, _report_key):
        with step('修改报表名称'):
            report = ReportInfo.report_info(_report_key, project_uuid=add_project)
            name = f"{report['name']}-重命名"
            ReportInfo.update_report_info(_report_key, param={"name": name})
        with step('查看报表名称'):
            r = ReportInfo.report_info(_report_key, project_uuid=add_project)
            assert r['name'] == name

    @story('T44249 报表配置：更改报表所属分组')
    def test_defect_dioc_change_group(self, add_project, _report_key):
        with step('更改报表所属分组'):
            groups = PrjAction.get_report_groups(project_uuid=add_project)
            g = [g for g in groups if g['name'] == '需求分析'][0]
            ReportInfo.update_report_info(_report_key, param={"report_category": g['uuid']})
        with step('查看更改的需求分析分组'):
            r = ReportInfo.report_info(_report_key, project_uuid=add_project)
            assert r['reportCategory']['uuid'] == g['uuid']

    @story('T44248 报表配置：导出报表')
    def test_defect_dioc_export(self, add_project, _report_key):
        with step('导出报表'):
            r = ReportInfo.report_info(_report_key, project_uuid=add_project)
            # 创建一个致命bug
            b_p = TaskAction.new_issue(issue_type_name='缺陷', proj_uuid=add_project, param_only=True)
            severity = IssueAction.get_field(field_name='严重程度')
            fatal_uuid = [p['uuid'] for p in severity['options'] if p['value'] == '致命'][0]
            b_p.json['tasks'][0]['field_values'].append({
                "field_uuid": "field038",
                "type": 1,
                "value": fatal_uuid
            })
            self.call(tk.TaskAdd, b_p)
            t = ReportInfo.export_report(r['reportType'], r['uuid'], r['config'], project_uuid=add_project)
            assert t.find('负责人') >= -1
            assert t.find('DI 值,10') >= -1

    @story('T44251 报表配置：添加到仪表盘：项目概览')
    def test_defect_dioc_add_to_dashboard(self, add_project, _report_key):
        with step('添加到仪表盘：项目概览'):
            # 获取报告信息
            r = ReportInfo.report_info(_report_key, project_uuid=add_project)
            # 获取概览组件
            c = PrjAction.get_component('概览', project_uuid=add_project)
            param = more.report_add_dashboard_proj_overview(r['uuid'], c['uuid'], r['name'], project_uuid=add_project)[
                0]
            res = self.call(prj.ItemGraphql, param)
            card_key = res.value('data.addCard.key')
            assert card_key, '检查点失败：添加到项目概览成功'
        with step('查看项目概览'):
            info_param = more.prj_overview_dashboard(c['uuid'])[0]
            res = self.call(prj.ItemGraphql, info_param)
            cards = res.value('data.cards')
            card = [c for c in cards if c['key'] == card_key]
            assert card, '检查点失败：添加成功，项目概览展示该报表数据'

    @story('T44253 报表配置：删除报表')
    def test_defect_dioc_delete(self, add_project, _report_key):
        with step('删除报表'):
            param = more.proj_report_delete(_report_key)[0]
            res = self.call(prj.ItemGraphql, param)
            res.check_response('data.deleteProjectReport.key', _report_key), '删除报表失败～'
        with step('查看报表列表'):
            rs = ReportInfo.report_list(project_uuid=add_project)
            assert not [r for r in rs if r['key'] == _report_key]