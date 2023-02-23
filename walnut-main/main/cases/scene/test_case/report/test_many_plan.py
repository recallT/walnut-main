from falcons.check import Checker
from falcons.com.nick import feature, story, parametrize, fixture
from falcons.helper import mocks

from main.api import case as api
from main.api import project as prj
from main.api.sprint import SprintAdd
from main.params import testcase, proj


@fixture(scope='module')
def _data_storage():
    p = {}
    return p


# 初始化项目迭代
@fixture(scope='module', autouse=True)
def _sprint_add(_data_storage):
    spt_add = SprintAdd()
    p1 = proj.sprint_add()[0]
    spt_add.call(p1.json, **p1.extra)
    spt_add.is_response_code(200)

    sprint = spt_add.json()['sprints'][0]

    sprint_uuid = sprint['uuid']
    sprint_statuses = sprint['statuses']
    _data_storage |= {'sprint_uuid': sprint_uuid, 'statuses': sprint_statuses}


# 初始化5条测试计划数据
@fixture(scope='module', autouse=True)
def _plan_data(_data_storage):
    param = testcase.query_case_phase()[0]
    q = prj.ItemGraphql()
    q.call(param.json, **param.extra)
    q.is_response_code(200)

    # 获取各测试阶段给uuid
    stages = q.json()['data']['fields'][0]['options']
    stage_uuid = [n['uuid'] for n in stages]

    uuids = []
    # 新增测试计划
    for i in range(5):
        p = testcase.add_case_plan()
        p.json['plan']['plan_stage'] = stage_uuid[0]  # 选择冒烟阶段
        add = api.AddCasePlan()
        add.call(p.json, **p.extra)
        add.is_response_code(200)
        uuids.append(add.json()['plan']['uuid'])

    _data_storage |= {'plan_uuid': uuids}  # 5条测试计划的uuid


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


@feature('新建测试报告')
class TestManyPlan(Checker):

    @story('138517 选择多个测试计划创建测试报告')
    @parametrize('param', testcase.add_test_report())
    def test_add_report(self, param, _data_storage):
        param.json['variables']['testcase_plans'] = _data_storage['plan_uuid']
        param.json['variables']['name'] = f'many_plan_report_{mocks.num()}'
        add = self.call(prj.ItemGraphql, param)

        # 获取测试报告uuid
        key = add.json()['data']['addTestcaseReport']['key']
        _data_storage |= {'key': key, 'report_uuid': key.split('-')[1]}
