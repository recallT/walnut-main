from falcons.check import Checker, go
from falcons.com.nick import feature, story, parametrize, step, fixture
from falcons.helper import mocks

from main.api import case as api
from main.api import project as prj
from main.params import testcase


@fixture(scope='module')
def _data_storage():
    p = {}
    return p


# 初始化测试计划数据
@fixture(scope='module', autouse=True)
def _plan_data(_data_storage):
    param = testcase.query_case_phase()[0]
    q = go(prj.ItemGraphql, param)

    # 获取各测试阶段给uuid
    stages = q.json()['data']['fields'][0]['options']
    stage_uuid = [n['uuid'] for n in stages]

    # 新增测试计划
    p = testcase.add_case_plan()
    p.json['plan']['plan_stage'] = stage_uuid[0]  # 选择冒烟阶段
    add = go(api.AddCasePlan, p)

    _data_storage |= {'plan_uuid': add.json()['plan']['uuid']}


@fixture(scope='module', autouse=True)
def _del_plan(_data_storage):
    """删除测试计划数据"""
    yield
    param = testcase.up_plan_status()
    param.uri_args({'plan_uuid': _data_storage['plan_uuid']})

    go(api.DeletePlan, param)


@feature('测试报告操作')
class TestReportOpt(Checker):

    @story('T138516 新建报告')
    @parametrize('param', testcase.add_test_report())
    def test_add_report(self, param, _data_storage):
        param.json['variables']['testcase_plans'] = [_data_storage['plan_uuid']]

        with step('点击新建：报告名称必填校验'):
            add = self.call(prj.ItemGraphql, param, status_code=400)
            add.check_response('errcode', 'InvalidParameter.TestcaseReport.Name.Empty')

        with step('选择 测试计划；点击 确定'):
            param.json['variables']['name'] = f'report_test_{mocks.num()}'
            add = self.call(prj.ItemGraphql, param)

            # 获取测试报告uuid
            key = add.json()['data']['addTestcaseReport']['key']
            _data_storage |= {'key': key, 'report_uuid': key.split('-')[1]}

        with step('查看详情-概览'):
            param.uri_args({'report_uuid': _data_storage['report_uuid']})

            view = self.call(api.ViewReport, param, with_json=False)
            view.check_response('reports[0].summary', '[\"1\",\"2\",\"3\",\"4\",\"5\"]', check_type='contains')

    @story('T118616 导出报告')
    @parametrize('param', testcase.export_report())
    def test_exp_report(self, param, _data_storage):
        with step('点击[导出文档]'):
            param.uri_args({'report_uuid': _data_storage['report_uuid']})
            ex = self.call(api.ExportReport, param)
            ex.check_response('type', 'OK')

    @story('T118631 编辑报告')
    @parametrize('param', testcase.up_report())
    def test_up_report(self, param, _data_storage):
        with step('修改名称'):
            param.json['uuid'] = _data_storage['report_uuid']
            param.uri_args({'report_uuid': _data_storage['report_uuid']})

            self.call(api.UpdateReport, param)

            # 验证修改后的名称是否正常
            view = self.call(api.ViewReport, param, with_json=False)
            view.check_response('reports[0].title', 'test修改测试报告')

        with step('编辑组件-添加富文本模版'):
            param.json[
                'summary'] = '{\"components\":[\"1\",\"2\",\"3\",\"4\",\"5\",\"1643015534722\"],\"contentMap\":' \
                             '{\"richTextComponentTitleSet\":{\"1643015534722\":\"自定义富文本\"},' \
                             '\"richTextComponentContentSet\":{}}}'

            self.call(api.UpdateReport, param)

    @story('118626 测试报告详情-删除测试用例结果分布组件')
    @story('118627 测试报告详情-删除测试用例所属模块分布组件')
    @story('118628 测试报告详情-删除概览组件')
    @story('118629 测试报告详情-删除关联缺陷列表组件')
    @story('118630 测试报告详情-删除缺陷优先级分布组件')
    @parametrize('param', testcase.up_del_module())
    def test_del_module(self, param, _data_storage):
        with step('编辑组件-删除列表组件'):
            param.json['uuid'] = _data_storage['report_uuid']
            param.uri_args({'report_uuid': _data_storage['report_uuid']})

            self.call(api.UpdateReport, param)


@feature('测试报告详情')
class TestReportDetail(Checker):

    @story('T118617 编辑概览')
    @parametrize('param', testcase.up_report())
    def test_up_overview(self, param, _data_storage):
        param.json['uuid'] = _data_storage['report_uuid']
        param.uri_args({'report_uuid': _data_storage['report_uuid']})

        with step('编辑「开始时间」'):
            param.json['start_time'] = mocks.now_timestamp()

            up = self.call(api.UpdateReport, param)
            up.check_response('type', 'OK')

        with step('编辑「结束时间」'):
            param.json['end_time'] = mocks.day_timestamp()

            up = self.call(api.UpdateReport, param)
            up.check_response('type', 'OK')

        with step('编辑「测试结论」'):
            param.json['summary'] = '{\"components\":[\"1\",\"2\",\"3\",\"4\"],\"contentMap\":' \
                                    '{\"richTextComponentTitleSet\":{},\"richTextComponentContentSet\":' \
                                    '{\"1\":\"<p>测试总结评论啦啦啦！！</p>\\n\"}}}'

            up = self.call(api.UpdateReport, param)
            up.check_response('type', 'OK')


@feature('测试报告列表')
class TestReportList(Checker):

    @story('T118633 列表排序')
    @parametrize('param', testcase.report_list())
    def test_report_sort(self, param):
        with step('创建人 降序'):
            param.json['variables']['orderBy'] |= {"owner": {"namePinyin": "DESC"}}
            self.call(prj.ItemGraphql, param)

        with step('创建时间 降序'):
            param.json['variables']['orderBy'] |= {"createTime": "DESC"}
            self.call(prj.ItemGraphql, param)

    @story('T135615 搜索测试报告')
    @parametrize('param', testcase.report_list())
    def test_search_report(self, param):
        with step('通过 测试报告名称 搜索'):
            param.json['variables'] = {"filter": {"name_match": "test"}}
            q = self.call(prj.ItemGraphql, param)
            q.check_response('data.buckets[0].pageInfo.count', 1)

        with step('输入无法命中的关键字'):
            param.json['variables'] = {"filter": {"name_match": "NoKey"}}
            q = self.call(prj.ItemGraphql, param)
            q.check_response('data.buckets[0].pageInfo.count', 0)

    @story('T135313 删除报告')
    @parametrize('param', testcase.del_test_report())
    def test_del_report(self, param, _data_storage):
        with step('确认删除'):
            param.json['variables']['key'] = _data_storage['key']
            self.call(prj.ItemGraphql, param)
