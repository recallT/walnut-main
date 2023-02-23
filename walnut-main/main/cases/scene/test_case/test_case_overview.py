from falcons.check import Checker, go
from falcons.com.nick import feature, story, fixture, step

from main.api import case as api
from main.api import project as prj
from main.params import testcase
from main.params.const import ACCOUNT


# 初始化测试计划数据
@fixture(scope='module', autouse=True)
def _plan_add(_storage):
    # 获取各测试阶段各uuid
    param = testcase.query_case_phase()[0]
    res = go(prj.ItemGraphql, param)

    stages = res.value('data.fields[0].options')
    stage_uuid = [n['uuid'] for n in stages]

    # 获取测试计划状态
    prm = testcase.query_plan_status()
    res = go(prj.ItemGraphql, prm)

    status = res.value('data.fields[0].statuses')
    status_uuid = [n['uuid'] for n in status]  # 0未开始，1进行中，2已完成

    # 新增测试计划
    case_name = ['5', 'a', 'b', 'c', 'd', 'e']
    p = testcase.add_case_plan()
    p.json['plan']['plan_stage'] = stage_uuid[0]  # 选择冒烟阶段

    plan_uuids = []  # 存储测试计划uuid
    for name in case_name:
        p.json['plan']['name'] = name
        add = go(api.AddCasePlan, p)
        plan_uuids.append(add.json()['plan']['uuid'])

    # 流转部分测试计划状态
    parm = testcase.up_plan_status()
    parm.json['status'] = status_uuid[1]
    for p in (plan_uuids[2], plan_uuids[5]):  # 将测试计划b和测试计划e状态更新为进行中
        parm.uri_args({'plan_uuid': p})
        go(api.UpdatePlanStatus, parm)

    parm.json['status'] = status_uuid[2]
    parm.uri_args({'plan_uuid': plan_uuids[3]})  # 测试计划c状态更新为已完成
    go(api.UpdatePlanStatus, parm)

    _storage |= {'plan_uuid': plan_uuids, 'status_uuid': status_uuid}


# 初始化用例库数据
@fixture(scope='module', autouse=True)
def _library_add(_storage):
    # 查默认配置uuid
    prm = testcase.query_case_config_list()[0]
    gq = go(prj.ItemGraphql, prm)
    config_uuid = gq.json()['data']['testcaseFieldConfigs'][0]['uuid']

    # 新建用例库
    lib_name = ['5', 'a', 'b', 'c', 'd', 'e']
    lib_uuid = []

    param = testcase.add_case_library()[0]
    param.json_update('library.field_config_uuid', config_uuid)

    for name in lib_name:
        param.json_update('library.name', name)
        add = go(api.AddCaseLibrary, param)
        lib_uuid.append(add.value('library.uuid'))

    _storage |= {'lib_uuid': lib_uuid}


@fixture(scope='module', autouse=True)
def _del_plan(_storage):
    """删除测数据"""
    yield
    param = testcase.up_plan_status()
    if _storage['plan_uuid']:
        for uuid in _storage['plan_uuid']:
            param.uri_args({'plan_uuid': uuid})
            go(api.DeletePlan, param)

    if _storage['lib_uuid']:
        for uuid in _storage['lib_uuid']:
            param.uri_args({'library_uuid': uuid})
            go(api.DeleteLibrary, param)


@fixture(scope='module')
def _storage():
    return {}


@feature('测试用例-概览')
class TestCaseOverview(Checker):

    @story('121295 测试计划：检查列表排序')
    def test_plan_sort(self, _storage):
        p_uuid = _storage['plan_uuid']
        with step('列表排序'):
            param = testcase.query_plan_list()
            param.json_update('variables.filter',
                              {'status': {'category_notEqual': 'done'}, 'assigns_in': [ACCOUNT.user.owner_uuid]})

            res = self.call(prj.ItemGraphql, param)
            uuids = [n['uuid'] for n in res.value('data.buckets[0].testcasePlans')]

            # 较验排序为：b、e、5、a、d
            assert uuids[0] == p_uuid[2]  # b第一
            assert uuids[3] == p_uuid[1]  # a第四
            assert p_uuid[3] not in uuids  # 已完成c不在列表中

    @story('121298 测试计划：视图「未完成的」数据校验')
    @story('118719 测试计划状态：检查测试计划的可更改状态')
    @story('118720 测试计划状态：检查测试计划状态的变更')
    def test_view_undone(self, _storage):
        p_uuid = _storage['plan_uuid']
        s_uuid = _storage['status_uuid']

        with step('点击「未完成的」视图'):
            param = testcase.query_plan_list()
            param.json_update('variables.filter', {'status': {'category_notEqual': 'done'}})

            res = self.call(prj.ItemGraphql, param)
            uuids = [n['uuid'] for n in res.value('data.buckets[0].testcasePlans')]

            assert p_uuid[3] not in uuids  # 已完成c不在列表中

        with step('修改测试计划 a 的状态为已完成'):
            prm = testcase.up_plan_status()
            prm.json['status'] = s_uuid[2]
            prm.uri_args({'plan_uuid': p_uuid[1]})  # a状态更新为已完成
            self.call(api.UpdatePlanStatus, prm)

            res = self.call(prj.ItemGraphql, param)
            uuids = [n['uuid'] for n in res.value('data.buckets[0].testcasePlans')]

            # 测试计划 a 从列表中消失
            assert p_uuid[1] not in uuids

        with step('修改测试计划 a 的状态为进行中'):
            prm.json['status'] = s_uuid[1]  # a状态更新为进行中
            self.call(api.UpdatePlanStatus, prm)

            res = self.call(prj.ItemGraphql, param)
            names = [n['uuid'] for n in res.value('data.buckets[0].testcasePlans')]

            # 测试计划 a 从列表中消失
            assert p_uuid[1] in names

    @story('121299 测试计划：视图「我负责的」数据校验')
    def test_view_me(self, _storage):
        with step('修改测试计划 a 的负责人，去掉当前用户'):
            param = testcase.query_plan_list()
            param.json_update('variables.filter', {'status': {'category_notEqual': 'done'}})

            self.call(prj.ItemGraphql, param)
            # 用例未完成

    @story('121310 用例库：检查列表排序')
    def test_library_sort(self, _storage):
        l_uuid = _storage['lib_uuid']

        with step('查看列表排序'):
            param = testcase.overview_lib_list()[0]

            res = self.call(prj.ItemGraphql, param)
            uuids = [n['uuid'] for n in res.value('data.buckets[0].testcaseLibraries')]

            assert uuids[0] == l_uuid[0]

    @story('121313 用例库：检查置顶功能')
    def test_library_pin(self, _storage):
        l_uuid = _storage['lib_uuid']

        with step('点击用例库c前的置顶按钮，置顶用例库c'):
            param = testcase.pin_library()[0]
            param.uri_args({'library_uuid': l_uuid[3]})

            self.call(api.CaseLibraryPin, param)

            # 校验排序
            prm = testcase.overview_lib_list()[0]
            res = self.call(prj.ItemGraphql, prm)
            uuids = [n['uuid'] for n in res.value('data.buckets[0].testcaseLibraries')]

            assert uuids[0] == l_uuid[3]

        with step('取消用例库c的置顶按钮'):
            self.call(api.CaseLibraryUnPin, param)

            # 校验排序
            res = self.call(prj.ItemGraphql, prm)
            uuids = [n['uuid'] for n in res.value('data.buckets[0].testcaseLibraries')]

            assert uuids[0] == l_uuid[0]
