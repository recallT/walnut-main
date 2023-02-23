"""
@Desc：项目报表-新建报表
"""
from falcons.check import Checker
from falcons.com.nick import feature, story

from main.api import project as pro, more
from main.params import more


@feature('项目报表-新建报表')
class TestReportAdd(Checker):

    def add_report_and_check(self, detail_type, categories_name=None):
        """
        创建报表及校验
        :param detail_type  报告类型
        :param categories_name  报告类别名(需求分析，缺陷分析，任务分析，工时分析)
        """
        parm = more.proj_report_categories()[0]
        resp = self.call(pro.ItemGraphql, parm)

        if categories_name:
            category = [c['uuid'] for c in resp.value('data.reportCategories') if c['name'] == categories_name][0]
            param = more.add_proj_report(detail_type, category)[0]

        else:
            param = more.add_proj_report(detail_type)[0]

        resp = self.call(pro.ItemGraphql, param)
        report_key = resp.value('data.addProjectReport.key')

        # 校验
        pam = more.proj_reports()[0]
        resp = self.call(pro.ItemGraphql, pam)

        report_keys = [k['key'] for k in resp.value('data.projectReports')]
        assert report_key in report_keys

    @story('138481 新建报表-工时报表：工时总览')
    def test_manhour_overview_add(self):
        self.add_report_and_check('manhour_overview', '工时分析')

    @story('138482 新建报表-工作项报表：工作项分布统计')
    def test_task_distribution_add(self):
        self.add_report_and_check('task_distribution')

    @story('138483 新建报表-工作项报表：工作项趋势统计')
    def test_task_trend_add(self):
        self.add_report_and_check('task_trend')

    @story('138484 新建报表-工作项报表：工作项属性耗时跟踪')
    def test_single_selection_stay_duration(self):
        self.add_report_and_check('single_selection_stay_duration')

    @story('138485 新建报表-工作项报表：工作项属性滞留时长分析')
    def test_task_field_time_consuming_track(self):
        self.add_report_and_check('task_field_retention_duration')

    @story('138486 新建报表-缺陷报表：缺陷创建量和解决量趋势')
    def test_defect_created_solved_trend(self):
        self.add_report_and_check('defect_created_solved_trend', '缺陷分析')

    @story('138488 新建报表-缺陷报表：缺陷平均生存时长分布')
    def test_task_avg_survival_duration(self):
        self.add_report_and_check('task_avg_survival_duration', '缺陷分析')

    @story('138492 新建报表-缺陷报表：缺陷探测率和逃逸率分布')
    def test_defect_detect_escape_rate(self):
        self.add_report_and_check('defect_detect_escape_rate', '缺陷分析')

    @story('138493 新建报表-缺陷报表：重开缺陷分析')
    def test_defect_reopen_distribution(self):
        self.add_report_and_check('defect_reopen_distribution', '缺陷分析')

    @story('138494 新建报表-通用报表：单选项属性停留时间分布')
    def test_single_selection_stay_duration(self):
        self.add_report_and_check('single_selection_stay_duration')

    @story('138505 新建报表-需求报表：需求按时交付情况分布')
    def test_demand_delivery_situation(self):
        self.add_report_and_check('demand_delivery_situation')

    @story('138480 新建报表-工时报表：工时日志')
    def test_manhour_log(self):
        self.add_report_and_check('manhour_log', '工时分析')
