from falcons.com.nick import feature, story, fixture, parametrize, mark

from main.api import case as api
from main.api import project
from main.params import testcase


# 初始化10条测试计划数据
@fixture(scope='module', autouse=True)
def _plan_data(_data_storage):
    param = testcase.query_case_phase()[0]
    q = project.ItemGraphql()
    q.call(param.json, **param.extra)
    q.is_response_code(200)

    # 获取各测试阶段给uuid
    stages = q.json()['data']['fields'][0]['options']
    stage_uuid = [n['uuid'] for n in stages]

    uuids = []
    # 新增测试计划
    for i in range(10):
        p = testcase.add_case_plan()
        p.json['plan']['plan_stage'] = stage_uuid[0]  # 选择冒烟阶段
        add = api.AddCasePlan()
        add.call(p.json, **p.extra)
        add.is_response_code(200)
        uuids.append(add.json()['plan']['uuid'])

    _data_storage |= {'plan_uuid': uuids}  # 10条测试计划的uuid


# 测试计划状态
@fixture(scope='module', autouse=True)
def _plan_status(_data_storage):
    param = testcase.query_plan_status()
    q = project.ItemGraphql()
    q.call(param.json, **param.extra)
    q.is_response_code(200)

    status = q.json()['data']['fields'][0]['statuses']

    _data_storage |= {'status_uuid': [n['uuid'] for n in status]}


@fixture(scope='module')
def _data_storage():
    p = {}
    return p


@fixture(scope='module', autouse=True)
def _del_plan(_data_storage):
    """删除测试计划数据"""
    yield
    param = testcase.up_plan_status()
    q = api.DeletePlan()
    for uuid in _data_storage['plan_uuid']:
        param.uri_args({'plan_uuid': uuid})
        q.call(**param.extra)
        q.is_response_code(200)


@mark.smoke
@feature('测试计划首页')
class TestPlanHome:

    @story('T118657 计划列表排序')
    @story('130834 检查排序功能：默认排序')
    def test_plan_sort(self):
        param = testcase.query_plan_list()

        q = project.ItemGraphql()
        q.call(param.json, **param.extra)

        q.is_response_code(200)

    @story('流转计划状态')
    @parametrize('sta_num, plan_num', [(1, 0), (2, 2)])  # 定义状态和测试计划, 进行中&第一个用例、已完成&第三个用例
    def test_turn_plan_status(self, _data_storage, sta_num, plan_num):
        param = testcase.up_plan_status()
        param.json['status'] = _data_storage['status_uuid'][sta_num]  # 流转成进行中状态
        param.uri_args({'plan_uuid': _data_storage['plan_uuid'][plan_num]})

        up = api.UpdatePlanStatus()
        up.call(param.json, **param.extra)

        up.is_response_code(200)

    @story('T118671 视图列表"进行中"状态检查')
    def test_view_status(self, _data_storage):
        param = testcase.query_plan_list()
        param.json['variables']['filter'] = {'status_in': [_data_storage['status_uuid'][1]]}  # 进行中状态

        q = project.ItemGraphql()
        q.call(param.json, **param.extra)

        q.is_response_code(200)
        # q.check_response('data.buckets[0].testcasePlans[0].uuid', _data_storage['plan_uuid'][0])

    @story('T118674 视图计数')
    def test_view_count(self):
        param = testcase.query_plan_list()

        q = project.ItemGraphql()
        q.call(param.json, **param.extra)

        q.is_response_code(200)

    @story('118675 测试计划 - 首页：视图检查')
    def test_view_order(self):
        param = testcase.query_plan_status()
        q = project.ItemGraphql()
        q.call(param.json, **param.extra)
        q.is_response_code(200)

        # 视图顺序为：未开始、进行中、已完成
        q.check_response('data.fields[0].statuses[0].name', '未开始')
        q.check_response('data.fields[0].statuses[1].name', '进行中')
        q.check_response('data.fields[0].statuses[2].name', '已完成')
