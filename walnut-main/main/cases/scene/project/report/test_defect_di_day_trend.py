"""
@Desc：项目报表-缺陷分析-缺陷DI值每日累计趋势
@Author  ：Zhangweiyu
"""
import copy
import json

from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, step

from main.actions.pro import PrjAction
from . import ReportInfo, get_defect_severity_default_di_value

report_name = '缺陷 DI 值每日累计趋势'


@fixture(scope='module')
def _report_key():
    report_key = ReportInfo.report_key(report_name)

    return report_key


@feature(f'缺陷分析')
class TestDefectDIDayTrend(Checker):

    @story(f'T131929 {report_name}-编辑报表：分析维度（X轴）')
    def test_defect_di_day_trend_x_config(self, _report_key):
        config: dict = ReportInfo.report_config(_report_key)
        with step('检查选择维度默认值'):
            assert config['dimensions'][0]['date_interval'] == '1d'
            assert config['dimensions'][0]['date_range'] == '30d'
            assert config['dimensions'][0]['is_accumulative']
            assert config['dimensions'][0]['include_weekend']
            assert config['dimensions'][0]['aggregation'] == 'date_histogram'
            assert config['dimensions'][0]['field_uuid'] == 'field009', 'x轴不是创建时间'

    @story('T131936 {report_name}-编辑报表：缺陷严重程度的权重属性值')
    def test_defect_di_day_trend_severity_options(self, _report_key):
        with step('检查缺陷严重程度的权重默认属性值'):
            config: dict = ReportInfo.report_config(_report_key)
            s_level_weights = config['dimensions'][1]['config']['severity_level_weight']
            actual_options_uuids = [s['uuid'] for s in s_level_weights]
            severity_options = PrjAction.get_severity_level()
            expect_options_uuids = [p['uuid'] for p in severity_options]
            assert len(s_level_weights) == len(severity_options), '严重程度DI配置项个数不对'
            assert actual_options_uuids == expect_options_uuids

    @story('T131937 缺陷DI值每日累计趋势-编辑报表：缺陷严重程度的权重属性值对应默认值')
    def test_defect_di_day_trend_severity_config(self, _report_key):
        config: dict = ReportInfo.report_config(_report_key)
        with step('检查缺陷严重程度的权重属性值对应默认值'):
            severity_config = config['dimensions'][1]['config']['severity_level_weight']
            # 获取属性-严重程度的选项配置
            expect_s_config = get_defect_severity_default_di_value()
            assert severity_config == expect_s_config, 'y轴：缺陷严重程度的DI值配置不正确'

    @story('T131949 缺陷DI值每日累计趋势-编辑报表：修改分析维度（X轴）选项值')
    def test_defect_di_day_trend_edit_x(self, _report_key):
        config: dict = ReportInfo.report_config(_report_key)
        new_config = copy.deepcopy(config)
        with step('编辑x轴：数据周期：每天，时间范围：最近7天'):
            new_config['dimensions'][0]['date_range'] = '7d'
            new_config['dimensions'][0]['date_interval'] = '1d'
            ReportInfo.update_report_info(_report_key, {'config': json.dumps(new_config)})
        with step('检查编辑信息生效'):
            last_config = ReportInfo.report_config(_report_key)
            assert last_config['dimensions'][0]['date_interval'] == '1d'
            # assert last_config['dimensions'][0]['date_range'] == '7d'
