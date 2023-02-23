import time

from falcons.com.nick import story, feature

from main.cases.ui_case.elem_opt import OnesRedio, OnesSelect
from main.cases.ui_case.links import prj_report_link, PrjReportDefectLinks


@feature('项目报表-缺陷DI值负责人比较')
class TestPrjReportDefectCst:

    @story('T131919 缺陷DI值负责人比较：图表说明')
    def test_report_detail_tip(self, project_page):
        link = prj_report_link(PrjReportDefectLinks.DI_OWNER_COMPARE, "缺陷分析",
                               "缺陷 DI 值负责人比较")
        project_page.driver.go_to(link)
        d = project_page.driver
        l_question = '//div[text()="图表"]/div'
        d.find_element(l_question).click()
        project_page.main_page.assert_page_contains('DI 值是衡量软件质量的高低的指标之一，本质是将缺陷数量按严重程度进行加权汇总。')
        project_page.main_page.assert_page_contains('推荐的计算规则如下：')
        project_page.main_page.assert_page_contains('DI 值公式 = 致命问题单数量 * 10 + 严重问题单数量 * 3 + 一般问题单数量 * 1 + 提示问题单数量 * 0.1')
        project_page.main_page.assert_page_contains('注意：此报表会根据系统属性「严重程度」来标识缺陷的严重程度')

    @story('T131897 缺陷DI值负责人比较-编辑报表：编辑图表y轴')
    def test_report_edit_y(self, project_page):
        link = prj_report_link(PrjReportDefectLinks.EDIT_DI_OWNER_COMPARE, "缺陷分析",
                               "缺陷 DI 值负责人比较")
        project_page.driver.go_to(link)
        l_di = '//div[.="分析指标（Y轴）"]/../div[@class="project-report-editor-section-content"]/div'
        di = project_page.driver.find_element(l_di)
        assert di.get_attribute('textContent') == 'DI 值'
