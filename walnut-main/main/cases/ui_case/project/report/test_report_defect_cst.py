import time

from falcons.com.nick import story, feature

from main.cases.ui_case.elem_opt import OnesRedio, OnesSelect
from main.cases.ui_case.links import prj_report_link, PrjReportDefectLinks


@feature('项目报表-缺陷创建量与解决量趋势')
class TestPrjReportDefectCst:

    @story('T131817 缺陷创建量与解决量趋势-编辑报表：默认分析维度（X轴）')
    def test_edit_x_axis(self, project_page):
        link = prj_report_link(PrjReportDefectLinks.EDIT_CREATE_SOLVE_TREND, "缺陷分析",
                               "缺陷创建量与解决量趋势")
        project_page.driver.go_to(link)
        d = project_page.driver

        sel1 = OnesSelect(d, '数据周期')
        assert sel1.get_value() == '每天'
        assert sel1.get_options() == ['每天', '每周', '每月']
        sl2 = OnesSelect(d, '时间范围')
        assert sl2.get_value() == '最近30天'
        assert sl2.get_options() == ['最近7天', '最近30天', '最近90天', '全部']
        rad1 = OnesRedio(d, '统计方式')
        assert rad1.option_checked() == '新增趋势'
        assert rad1.get_options() == ['新增趋势', '累计趋势']
        rad2 = OnesRedio(d, '是否包含周末')
        assert rad2.option_checked() == '是'
        assert rad2.get_options() == ['是', '否']
