"""
@Desc：项目报表-缺陷探测率和逃逸率分布
"""
from falcons.check import Checker, go
from falcons.com.nick import feature, story, fixture, step, skip
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
def _storage():
    return {}


report_name = '缺陷探测率和逃逸率分布'


@skip
@feature('项目报表-缺陷探测率和逃逸率分布')
class TestDefectEscapeRate(Checker):

    @story('132780 缺陷探测率和逃逸率分布-编辑报表：编辑图表x轴')
    def test_defect_escape_rate_edit_x_axis(self, ):
        """"""

    @story('132790 缺陷探测率和逃逸率分布-更多：更改所属分组')
    def test_defect_escape_rate_update_group(self, ):
        """"""

    @story('132796 缺陷探测率和逃逸率分布-更多：添加到仪表盘（概览）')
    def test_defect_escape_rate_add_proj_overview(self, ):
        """"""

    @story('132797 缺陷探测率和逃逸率分布-更多：添加到仪表盘（仪表盘）')
    def test_defect_escape_rate_add_dashboard(self, ):
        """"""

    @story('132799 缺陷探测率和逃逸率分布：导出报表')
    def test_defect_escape_rate_export_report(self):
        """"""

    @story('132800 缺陷探测率和逃逸率分布：另存为')
    def test_defect_escape_rate_save(self, ):
        """"""

    @story('132802 缺陷探测率和逃逸率分布：图表详情数据源')
    def test_defect_escape_rate_data_source(self, ):
        """"""
