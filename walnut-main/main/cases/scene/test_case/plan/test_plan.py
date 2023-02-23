from falcons.com.nick import feature, story, fixture
from falcons.helper import mocks

from main.api import case as api
from main.api import project
from main.params import testcase


# 初始化用例库
@fixture(scope='module', autouse=True)
def _case_lib():
    param = testcase.add_case_library()[0]

    data = testcase.query_case_config_list()[0]
    q = project.ItemGraphql()
    q.call(data.json, **data.extra)
    config_uuid = q.json()['data']['testcaseFieldConfigs'][0]['uuid']

    param.json['library']['field_config_uuid'] = config_uuid
    add_libra = api.AddCaseLibrary()
    add_libra.call(param.json, **param.extra)

    add_libra.is_response_code(200)
    add_libra.check_response('library.name',
                             param.json['library']['name'])

    uuid = add_libra.json()['library']['uuid']
    module_uuid = add_libra.json()['library']['modules'][0]['uuid']

    return {'uuid': uuid, 'module_uuid': module_uuid, 'config_uuid': config_uuid}


@fixture(scope='module')
def _data_storage():
    p = {}
    return p


# 获取用例属性配置
@fixture(scope='module', autouse=True)
def _case_priority(_case_lib, _data_storage):
    param = testcase.query_library_case_edit()[0]
    param.json['variables']['fieldFilter']['context']['fieldConfigUUID_in'] = [_case_lib['config_uuid']]
    param.json['variables']['moduleFilter']['testcaseLibrary_in'] = [_case_lib['uuid']]

    q = project.ItemGraphql()
    q.call(param.json, **param.extra)

    # 获取用例库优先级等级uuid和显示值(P0\P1)
    fields = q.json()['data']['fields']

    priority_uuids = [f for f in fields if f['name'] == '优先级']
    case_type = [f for f in fields if f['name'] == '用例类型']

    _data_storage |= {
        'pri_uuid': [n['uuid'] for n in priority_uuids[0]['options']],
        'pri_value': [n['value'] for n in priority_uuids[0]['options']],
        'type_uuid': [n['uuid'] for n in case_type[0]['options']]
    }


# 添加用例模块
@fixture(scope='module', autouse=True)
def _add_lib_module(_case_lib, _data_storage):
    # 添加模块
    param = testcase.add_library_module()[0]
    param.uri_args({'library_uuid': _case_lib['uuid']})

    add = api.AddLibraryModule()
    for i in range(3):
        add.call(param.json, **param.extra)
        add.is_response_code(200)

    # 获取所有模块uuid
    q = testcase.query_modules_library()[0]
    q.json['variables']['moduleFilter']['testcaseLibrary_in'] = [_case_lib['uuid']]
    q.uri_args({'library_uuid': _case_lib['uuid']})

    qg = project.ItemGraphql()
    qg.call(q.json, **q.extra)
    qg.is_response_code(200)

    modules = qg.json()['data']['testcaseModules']
    _data_storage |= {'all_mod': [mod['uuid'] for mod in modules]}


# 初始化测试计划数据
@fixture(scope='module', autouse=True)
def _plan_data(_data_storage):
    param = testcase.query_case_phase()[0]
    q = project.ItemGraphql()
    q.call(param.json, **param.extra)
    q.is_response_code(200)

    # 获取各测试阶段给uuid
    stages = q.json()['data']['fields'][0]['options']
    stage_uuid = [n['uuid'] for n in stages]

    # 新增测试计划
    p = testcase.add_case_plan()
    p.json['plan']['plan_stage'] = stage_uuid[0]  # 选择冒烟阶段
    add = api.AddCasePlan()
    add.call(p.json, **p.extra)
    add.is_response_code(200)

    _data_storage |= {'plan_uuid': add.json()['plan']['uuid']}


@fixture(scope='module', autouse=True)
def _del_plan(_data_storage):
    """删除测试计划数据"""
    yield
    param = testcase.up_plan_status()
    q = api.DeletePlan()
    param.uri_args({'plan_uuid': _data_storage['plan_uuid']})
    q.call(**param.extra)
    q.is_response_code(200)


@feature('测试计划')
class TestPlan:

    @story('用例库不同模块下创建用例')
    def test_mod_add_case(self, _case_lib, _data_storage):
        param = testcase.add_case()[0]
        param.json['item']['priority'] = _data_storage['pri_uuid'][1]
        param.json['item']['type'] = _data_storage['type_uuid'][0]
        param.json['item']['module_uuid'] = _case_lib['module_uuid']
        param.json['item']['library_uuid'] = _case_lib['uuid']
        param.json['item']['testcase_library'] = _case_lib['uuid']

        case_uuids = []
        add = project.ItemsAdd()
        # 在不同模块下创建用例
        for mod in _data_storage['all_mod']:
            param.json['item']['testcase_module'] = mod
            param.json['item']['name'] = f'示例用例{mocks.num()}'
            add.call(param.json, **param.extra)
            add.is_response_code(200)

            case_uuids.append(add.json()['item']['uuid'])

        # 添加关联用例
        c = testcase.up_plan_info()
        c.uri_args({'plan_uuid': _data_storage['plan_uuid']})
        jsr = {'case_uuids': case_uuids}

        add = api.CaseRelPlan()
        add.call(jsr, **c.extra)
        add.is_response_code(200)

    @story('122331 功能模块与列表联动-所有用例')
    def test_mod_join_list(self, _data_storage):
        # 查询测试计划模块uuid
        p = testcase.plan_case_mod()[0]
        p.json['variables']['planFilter']['uuid_equal'] = _data_storage['plan_uuid']

        gq = project.ItemGraphql()
        gq.call(p.json, **p.extra)
        gq.is_response_code(200)

        case_modules = gq.json()['data']['testcasePlans'][0]['testcaseModules']
        mods_uuid = [mod['uuid'] for mod in case_modules]

        # 查看模块联动的用例数是否正确
        s = testcase.plan_case_list()
        s.json['variables']['testCaseFilter'] = [{"testcasePlan_in": [_data_storage['plan_uuid']],
                                                  "testcaseCase": {"path_match": mods_uuid[1]}}]  # 使用第二个模块
        s.json['variables']['planFilter']['uuid_in'].append(_data_storage['plan_uuid'])

        sq = project.ItemGraphql()
        sq.call(s.json, **s.extra)
        sq.is_response_code(200)
        sq.check_response('data.buckets[0].pageInfo.count', 1)
