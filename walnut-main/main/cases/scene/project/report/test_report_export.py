# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_report_export.py
@Author  ：zhangyonghui@ones.ai
@Date    ：2022/6/15 4:50 PM 
@Desc    ：项目内工时报表导出
"""
from falcons.check import Checker
from falcons.com.nick import story, step, feature, mark

from main.actions.pro import PrjAction
from main.api.project import ExportProjReport
from main.params import more


@mark.smoke
@feature('项目内工时报表导出')
class TestProjReportExport(Checker):

    @story('T144914 T142577 导出工时报表：成员 (登记人)-每天工时总览')
    def test_export_user_everyday_working_hours(self):
        report_uuid, report_type, dimensions = PrjAction.proj_report_list('工时分析', '成员 (登记人)-每天工时总览')

        with step('导出成员 (登记人)-每天工时总览'):
            param = more.export_proj_report(report_type, report_uuid, dimensions)[0]
            self.call(ExportProjReport, param)

    @story('T144905 导出工时报表：迭代工时日志报表')
    def test_export_sprint_log_working_hours(self):
        report_uuid, report_type, dimensions = PrjAction.proj_report_list('工时分析', '迭代工时日志报表')

        with step('导出迭代工时日志报表'):
            param = more.export_proj_report(report_type, report_uuid, dimensions)[0]
            self.call(ExportProjReport, param)

    @story('T144917 导出工时报表：每日工时日志报表')
    def test_export_everyday_log_working_hours(self):
        report_uuid, report_type, dimensions = PrjAction.proj_report_list('工时分析', '每日工时日志报表')

        with step('导出每日工时日志报表'):
            param = more.export_proj_report(report_type, report_uuid, dimensions)[0]
            self.call(ExportProjReport, param)

    @story('T144918 导出工时报表：成员 (负责人)-状态类型工时总览')
    def test_export_task_type_working_hours(self):
        report_uuid, report_type, dimensions = PrjAction.proj_report_list('工时分析', '成员 (负责人)-状态类型工时总览')

        with step('导出成员(负责人) - 状态类型工时总览'):
            param = more.export_proj_report(report_type, report_uuid, dimensions)[0]
            self.call(ExportProjReport, param)

    @story('T144902 导出工时报表：成员 (负责人)-迭代工时总览')
    def test_export_user_sprint_working_hours(self):
        report_uuid, report_type, dimensions = PrjAction.proj_report_list('工时分析', '成员 (负责人)-迭代工时总览')

        with step('导出成员 (负责人)-迭代工时总览'):
            param = more.export_proj_report(report_type, report_uuid, dimensions)[0]
            self.call(ExportProjReport, param)

    @story('T144916 导出工时报表：每月工时日志报表')
    def test_export_every_month_log_working_hours(self):
        report_uuid, report_type, dimensions = PrjAction.proj_report_list('工时分析', '每月工时日志报表')

        with step('导出每月工时日志报表'):
            param = more.export_proj_report(report_type, report_uuid, dimensions)[0]
            self.call(ExportProjReport, param)

    @story('144908 导出工时报表：导出工作项登记工时')
    def test_export_task_register_hour(self):
        """"""
