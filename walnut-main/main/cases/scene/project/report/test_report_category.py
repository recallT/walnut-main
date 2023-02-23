"""
@Desc：场景用例：项目报表-报表分组
"""
from falcons.check import Checker
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, step, fixture
from falcons.helper import mocks
import time

from main.api import project as pro, more
from main.helper.extra import Extra
from main.params import more
from main.actions.pro import PrjAction, PrjSettingAction
from main.actions.issue import IssueTypeAction


@fixture(scope='module', autouse=True)
def prepare():
    # 创建一个单独项目
    time.sleep(2)
    creator = Extra(ApiMeta)
    pid = creator.new_project(f'ApiTest-Report-{mocks.ones_uuid()}')
    # 给项目添加一个报表分组（自定义）
    group_key = PrjAction.add_report_group(pid)
    # 配置中心-新建一个自定义的工作项类型
    it = IssueTypeAction.create_issue_type()
    yield {'project_uuid': pid,
           'group_key': group_key,
           'issue_type_uuid': it.value('uuid'),
           'issue_type_name': it.value('name')}
    # 当项目中的自定义工作项没有移除，则重新移除再从全局配置中移除
    del_res = IssueTypeAction.delete_issue_type(it.value('uuid'))
    if 'type' in del_res.json().keys() and del_res.value('type') == 'InUse':
        PrjSettingAction.del_issue_type(issue_type_uuid=it.value('uuid'), project_uuid=pid)
        # 从全局配置再移除一次
        IssueTypeAction.delete_issue_type(it.value('uuid'))

    creator.del_project(pid)


@feature('项目报表-报表分组')
class TestReportCategory(Checker):

    # def check_in_groups(self, group_key, groups) -> bool:
    #     return group_key in [g['key'] for g in groups]
    #
    # def check_in_reports(self, report_key, reports, group_key=None):
    #     return

    @story('T44245 报表分组：新建分组')
    def test_add_report_category(self, prepare):
        param = more.proj_report_add_group(prepare['project_uuid'])[0]
        res = self.call(pro.ItemGraphql, param)
        assert res.value('data.addReportCategory.key'), '新建报表分组失败'

    @story('T44244 报表分组：重命名分组')
    def test_update_report_category_name(self, prepare):
        key = prepare['group_key']
        with step('修改报表分组的名称'):
            name = 'update_group_name'
            update_param = more.report_categories_update(key, name)[0]
            update_res = self.call(pro.ItemGraphql, update_param)
            assert update_res.value('data.updateReportCategory.key') == key
        with step('检查报表分组list中，报表分组名称更新'):
            groups = PrjAction.get_report_groups(prepare['project_uuid'])
            assert [g for g in groups if g['key'] == key][0]['name'] == name, '更新报表名称失败'

    @story('T44242 报表分组：查看分组列表')
    def test_check_report_category_list(self, prepare):
        list_param = more.proj_report_categories(prepare['project_uuid'])[0]
        list_res = self.call(pro.ItemGraphql, list_param)
        groups = list_res.value('data.reportCategories')
        assert len(groups) > 0
        custom_group = [g for g in groups if g['key'] == prepare['group_key']][0]
        assert custom_group['canDelete'] and custom_group['canUpdate'], '新增分组不可删除、可编辑'

    @story('T117431 报表分组：分组排序')
    def test_report_categorys_sort(self, prepare):
        list_param = more.proj_report_categories(prepare['project_uuid'])[0]
        list_res = self.call(pro.ItemGraphql, list_param)
        groups = list_res.value('data.reportCategories')
        createtimes = [g['createTime'] for g in groups]
        sort_creatimes = createtimes.copy()
        sort_creatimes.sort()
        assert createtimes == sort_creatimes, '排序不正确，没有按照创建时间排序'
        assert prepare['group_key'] in [g['key'] for g in groups], '添加的报表分组不在列表中'

    @story('T44241 报表分组：删除分组和报表')
    def test_category_delete(self, prepare):
        project_uuid = prepare['project_uuid']
        with step('前置操作：添加分组a且其下有报表ra'):
            group_key = PrjAction.add_report_group(project_uuid)
            report_key = PrjAction.add_report(group_key=group_key, project_uuid=project_uuid)
        with step('删除分组和报表'):
            del_param = more.report_category_delete(group_key, is_report_delete=True)[0]
            res = self.call(pro.ItemGraphql, del_param)
            assert res.value('data.deleteReportCategory.key') == group_key
        with step('检查分组列表和报表列表：均从列表中清除'):
            rsl = PrjAction.get_reports_groups(project_uuid)
            assert group_key not in [g['key'] for g in rsl['groups']], '分组未被清除'
            assert report_key not in [r['key'] for r in rsl['reports']], '报表未被清除'

    @story('T44243 报表分组：删除分组：存在报表')
    def test_report_and_category_delete(self, prepare):
        project_uuid = prepare['project_uuid']
        with step('前置操作：添加分组a且其下有报表ra'):
            add_group_key = PrjAction.add_report_group(project_uuid)
            add_report_key = PrjAction.add_report(group_key=add_group_key, project_uuid=project_uuid)
        with step('删除分组'):
            del_param = more.report_category_delete(add_group_key, is_report_delete=False)[0]
            res = self.call(pro.ItemGraphql, del_param)
            assert res.value('data.deleteReportCategory.key') == add_group_key
        with step('检查分组列表和报表列表: 分组被删，报表没有被删，且归类到无分组'):
            rsl = PrjAction.get_reports_groups(project_uuid)
            groups = rsl["groups"]
            reports = rsl['reports']
            assert add_group_key not in [g['key'] for g in groups], '分组未被清除'
            assert add_report_key in [r['key'] for r in reports], '报表不应被清除，但是被清除了'
            r: dict = [r for r in reports if r['key'] == add_report_key][0]
            assert r["reportCategory"]['key'] == "report_category-", '报表未归类到无分组'

    @story('T117432 报表分组：项目下添加工作项，查看报表分组')
    def test_impact_of_new_issue_type(self, prepare):
        issue_type_uuid = prepare['issue_type_uuid']
        issue_type_name = prepare['issue_type_name']
        project_uuid = prepare['project_uuid']
        with step('添加自定义工作项类型到项目中'):
            PrjSettingAction.add_issue_type(issue_type_uuid, project_uuid)
        with step('查看报表分组和报表列表：自动生成对应的分组和报表'):
            rsl = PrjAction.get_reports_groups(project_uuid=project_uuid)
            groups = rsl['groups']
            reports = rsl['reports']
            group = [g for g in groups if g['name'] == f'{issue_type_name}分析'][0]
            assert group, '添加工作项类型，没有自动生成分组'
            r_names = [r['name'] for r in reports if r['reportCategory']['name'] == f'{issue_type_name}分析']
            assert len(r_names) == 9, '添加工作项类型，生成报表不是9张'
            assert r_names.sort() == [f'{issue_type_name}创建者分布',
                                      f'{issue_type_name}负责人分布',
                                      f'{issue_type_name}负责人停留时间分布',
                                      f'{issue_type_name}每日累计趋势',
                                      f'{issue_type_name}每日新增趋势',
                                      f'{issue_type_name}每日状态趋势',
                                      f'{issue_type_name}状态分布',
                                      f'{issue_type_name}状态滞留时间分析',
                                      f'{issue_type_name}状态-负责人分布'].sort(), '添加工作项类型，生成的9张报表，名称错误'

        with step('后置操作：移除工作项类型'):
            PrjSettingAction.del_issue_type(issue_type_uuid, project_uuid)

    def get_and_check_reports_names(self, project_uuid, group_name: [dict], expect_reports_names: [str], err_tip: str):
        res = PrjAction.get_reports_groups(project_uuid)
        reports = res['reports']
        actual_reports_names = [r['name'] for r in reports if r['reportCategory']['name'] == group_name]
        actual_reports_names.sort()
        expect_reports_names.sort()
        diff_list = [a for a in actual_reports_names + expect_reports_names if
                     (a not in actual_reports_names) or (a not in expect_reports_names)]
        assert actual_reports_names == expect_reports_names, f"{err_tip}，差异：{diff_list}"

    @story('T122343 工时分析：默认预置报表')
    def test_default_reports_for_work_hour_analysis(self, prepare):
        expect_reports_names = ['成员工时日志报表',
                                '成员 (登记人)-迭代工时总览',
                                '成员 (登记人)-每天工时总览',
                                '成员 (登记人)-每月工时总览',
                                '成员 (登记人)-每周工时总览',
                                '成员 (登记人)-状态类型工时总览',
                                '成员 (负责人)-迭代工时总览',
                                '成员 (负责人)-每天工时总览',
                                '成员 (负责人)-每月工时总览',
                                '成员 (负责人)-每周工时总览',
                                '成员 (负责人)-状态类型工时总览',
                                '迭代工时日志报表',
                                '每日工时日志报表',
                                '每月工时日志报表',
                                '每周工时日志报表']
        self.get_and_check_reports_names(prepare['project_uuid'], '工时分析', expect_reports_names, '工时分析的预置报表不正确，请检查')

    @story('T139286 需求分析：默认预置报表')
    def test_default_reports_for_demand_analysis(self, prepare):
        expect_reports_names = ["需求按时交付情况分布",
                                "需求创建者分布",
                                "需求负责人分布",
                                "需求负责人停留时间分布",
                                "需求每日累计趋势",
                                "需求每日新增趋势",
                                "需求每日状态趋势",
                                "需求平均生存时长分布",
                                "需求状态分布",
                                "需求状态滞留时间分析",
                                "需求状态-负责人分布"]
        self.get_and_check_reports_names(prepare['project_uuid'], '需求分析', expect_reports_names, '需求分析的预置报表不正确，请检查')

    @story('T133127 任务分析：默认预置报表')
    def test_default_reports_for_task_analysis(self, prepare):
        expect_reports_names = [
            "任务创建者分布",
            "任务负责人分布",
            "任务负责人停留时间分布",
            "任务每日累计趋势",
            "任务每日新增趋势",
            "任务每日状态趋势",
            "任务状态分布",
            "任务状态滞留时间分析",
            "任务状态-负责人分布",
        ]
        self.get_and_check_reports_names(prepare['project_uuid'], '任务分析', expect_reports_names, '任务分析的预置报表不正确，请检查')

    @story('TT131962 缺陷分析：默认预置报表')
    def test_default_reports_for_bug_analysis(self, prepare):
        expect_reports_names = ['缺陷创建量与解决量趋势',
                                '缺陷创建者分布',
                                '缺陷负责人分布',
                                '缺陷负责人停留时间分布',
                                '缺陷每日累计趋势',
                                '缺陷每日新增趋势',
                                '缺陷每日状态趋势',
                                '缺陷平均生存时长分布',
                                '缺陷探测率和逃逸率分布',
                                '缺陷状态分布',
                                '缺陷状态滞留时间分析',
                                '缺陷状态-负责人分布',
                                '缺陷 DI 值负责人比较',
                                '缺陷 DI 值每日累计趋势',
                                '重开缺陷分布']
        self.get_and_check_reports_names(prepare['project_uuid'], '缺陷分析', expect_reports_names, '缺陷分析的预置报表不正确，请检查')

    @story('T131957 缺陷分析-更多：删除分组和报表（有缺陷工作项类型）')
    def test_delete_group_with_exist_bug_issuetype(self, prepare):
        with step('前置条件：项目存在缺陷工作项类型'):
            PrjSettingAction.add_issue_type_by_name('缺陷')
        with step('分组-缺陷分析：删除分组和报表'):
            groups = PrjAction.get_report_groups(prepare['project_uuid'])
            bug_group = [g for g in groups if g['name'] == '缺陷分析'][0]
            assert not bug_group['canDelete'], '项目存在缺陷工作类型时，其报表和分组不可删除'
            assert not bug_group['canUpdate'], '项目存在缺陷工作类型时，其分组名称不可编辑'

    @story('T131956 缺陷分析-更多：删除分组和报表（无缺陷工作项类型）')
    def test_delete_group_with_no_bug_issuetype(self, prepare):
        with step('前置条件：项目不存在缺陷工作项类型'):
            PrjSettingAction.del_issue_type_by_name('缺陷', project_uuid=prepare['project_uuid'])
        with step('分组-缺陷分析：检查"删除分组和报表"的状态（可删除）'):
            all = PrjAction.get_reports_groups(prepare['project_uuid'])
            groups = all['groups']
            reports = all['reports']
            bug_group = [g for g in groups if g['name'] == '缺陷分析'][0]
            assert bug_group['canDelete'], '项目存在缺陷工作类型时，其报表和分组可删除'
            assert not bug_group['canUpdate'], '项目存在缺陷工作类型时，其分组名称不可编辑'
        with step('分组-缺陷分析：确认删除分组和报表'):
            del_param = more.report_category_delete(bug_group['key'], is_report_delete=True)[0]
            self.call(pro.ItemGraphql, del_param)
            r_keys_bug = [r['key'] for r in reports if r['reportCategory']['key'] == bug_group['key']]
            rsl = PrjAction.get_reports_groups(prepare['project_uuid'])
            r_keys_now = [r['key'] for r in rsl['reports']]
            assert bug_group['key'] not in [g['key'] for g in rsl['groups']], '缺陷分析的报表分组未被清除'
            assert not [k for k in r_keys_bug if k in r_keys_now], '缺陷分析的报表未被清除'
        with step('后置处理：添加缺陷工作项类型'):
            PrjSettingAction.add_issue_type_by_name('缺陷', project_uuid=prepare['project_uuid'])
