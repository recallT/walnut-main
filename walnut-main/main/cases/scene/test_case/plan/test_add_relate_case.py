from falcons.com.nick import feature, story, fixture, parametrize
from falcons.helper import mocks

from main.api import case as api
from main.api import project
from main.params import testcase


# 初始化用例库
@fixture(scope='module', autouse=True)
def _case_lib():
    # 查默认配置uuid
    q = testcase.query_case_config_list()[0]
    gq = project.ItemGraphql()
    gq.call(q.json, **q.extra)
    config_uuid = gq.json()['data']['testcaseFieldConfigs'][0]['uuid']

    # 新建用例库
    param = testcase.add_case_library()[0]
    param.json['library']['field_config_uuid'] = config_uuid
    add = api.AddCaseLibrary()
    add.call(param.json, **param.extra)
    add.is_response_code(200)

    data = {'lib_uuid': add.json()['library']['uuid'],
            'module_uuid': add.json()['library']['modules'][0]['uuid'],
            'conf_uuid': config_uuid}

    return data


@fixture(scope='module')
def _data_storage():
    p = {}
    return p


# 获取用例属性配置
@fixture(scope='module', autouse=True)
def _case_priority(_case_lib, _data_storage):
    param = testcase.query_library_case_edit()[0]
    param.json['variables']['fieldFilter']['context']['fieldConfigUUID_in'] = [_case_lib['conf_uuid']]
    param.json['variables']['moduleFilter']['testcaseLibrary_in'] = [_case_lib['lib_uuid']]

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
    return _data_storage


# 用例名全局变量
names = ['示例用例1', '示例用例2', '示例用例23']


# 初始化用例
@fixture(scope='module', autouse=True)
def _case_data(_case_lib, _case_priority, _data_storage):
    param = testcase.add_case()[0]
    param.json['item']['priority'] = _case_priority['pri_uuid'][1]
    param.json['item']['type'] = _case_priority['type_uuid'][0]
    param.json['item']['module_uuid'] = _case_lib['module_uuid']
    param.json['item']['testcase_module'] = _case_lib['module_uuid']
    param.json['item']['library_uuid'] = _case_lib['lib_uuid']
    param.json['item']['testcase_library'] = _case_lib['lib_uuid']

    all_uuid = []
    add = project.ItemsAdd()
    # 创建3条用例
    for name in names:
        param.json['item']['name'] = name
        add.call(param.json, **param.extra)
        add.is_response_code(200)

        all_uuid.append(add.json()['item']['uuid'])  # 保存所有用例的uuid

    _data_storage |= {'all_uuid': all_uuid}


# 初始化测试计划
@fixture(scope='module', autouse=True)
def _plan_data(_data_storage):
    param = testcase.query_case_phase()[0]
    q = project.ItemGraphql()
    q.call(param.json, **param.extra)
    q.is_response_code(200)

    # 获取各测试阶段的uuid
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


@feature('添加关联用例操作')
class TestAddRelateCase:

    # 135795 添加关联用例 - 筛选系统属性：根据「用例ID」筛选（等于）
    # 135806 添加关联用例 - 筛选自定义属性：根据「自定义单选菜单」筛选（包含）
    @story('135869 属性筛选')
    @story('135787 添加关联用例 - 筛选系统属性：根据「创建时间」筛选（等于）（准确日期）')
    @story('135792 添加关联用例 - 筛选系统属性：根据「前置条件」筛选（包含）')
    @story('135798 添加关联用例 - 筛选系统属性：根据「用例名称」筛选（包含）')
    @story('135800 添加关联用例 - 筛选系统属性：根据「用例维护人」筛选（包含）')
    @parametrize('key, value, expect', [('createTime_range', {'equal': f'{mocks.date_today()}'}, 3),  # 属性-创建时间
                                        ('name_match', names[0], 1),  # 属性-用例名称
                                        ('condition_match', '前置条件', 3),  # 属性-前置条件
                                        ('assign_in', ['$currentUser'], 3),  # 属性-用例维护人(自己)
                                        ])
    def test_filter(self, _case_lib, _data_storage, key, value, expect):
        p = testcase.rel_case_filter()
        p.json['variables']['testCaseFilter'] = [{
            "testcaseLibrary_in": [
                _case_lib['lib_uuid']
            ],
            key: value,
            "relatedPlans_notIn": [
                _data_storage['plan_uuid']
            ]
        }]

        q = project.ItemGraphql()
        q.call(p.json, **p.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', expect)

    @story('135802 属性筛选-优先级')
    def test_filter_pri(self, _case_lib, _data_storage):
        p = testcase.rel_case_filter()
        p.json['variables']['testCaseFilter'] = [{
            "testcaseLibrary_in": [
                _case_lib['lib_uuid']
            ],
            "priority_in": [_data_storage['pri_uuid'][1]],  # 查询优先级是P1的用例
            "relatedPlans_notIn": [
                _data_storage['plan_uuid']
            ]
        }]

        q = project.ItemGraphql()
        q.call(p.json, **p.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 3)

    @story('135796 属性筛选-用例类型')
    def test_filter_type(self, _data_storage, _case_lib):
        p = testcase.rel_case_filter()
        p.json['variables']['testCaseFilter'] = [{
            "testcaseLibrary_in": [
                _case_lib['lib_uuid']
            ],
            'type_in': [_data_storage['type_uuid'][0]],  # 获取用例类型-功能测试
            "relatedPlans_notIn": [
                _data_storage['plan_uuid']
            ]
        }]

        q = project.ItemGraphql()
        q.call(p.json, **p.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 3)

    @story('135974 检查筛选器可选属性')
    def test_plan_filter(self):
        attributes = (
            '创建时间', '所属模块', '用例ID', '用例类型', '用例名称', '用例维护人', '优先级'
        )

        p = testcase.plan_global_field()
        q = project.ItemGraphql()
        q.call(p.json, **p.extra)
        q.is_response_code(200)

        fields = q.json()['data']['fields']
        conf_names = set([n['name'] for n in fields])

        not_exist = []
        for attr in attributes:
            if attr not in conf_names:
                not_exist.append(attr)

        if not_exist:
            raise AssertionError('系统属性不存在')

    @story('135774 关联用例')
    def test_relate_case(self, _case_lib, _data_storage):
        # 查询需关联用例的uuid
        p = testcase.query_test_case()
        p.json['variables']['testCaseFilter'] = [{
            "testcaseLibrary_in": [
                _case_lib['lib_uuid']
            ],
            "relatedPlans_notIn": [
                _data_storage['plan_uuid']
            ]
        }]

        q = project.ItemGraphql()
        q.call(p.json, **p.extra)

        q.is_response_code(200)

        case_uuids = [n['uuid'] for n in q.json()['data']['testcaseCases']]

        # 添加关联用例
        c = testcase.up_plan_info()
        c.uri_args({'plan_uuid': _data_storage['plan_uuid']})
        jsr = {'case_uuids': case_uuids}

        add = api.CaseRelPlan()
        add.call(jsr, **c.extra)
        add.is_response_code(200)

    @story('151317 导出用例：删除用例属性后，导出全部用例')
    def test_export_part_case(self, _data_storage):
        param = testcase.export_plan_case()
        param.json['plan_uuid'] = _data_storage['plan_uuid']
        param.json['case_uuids'] = _data_storage['all_uuid'][:2]  # 选中前两个用例进行导出
        param.uri_args({'plan_uuid': _data_storage['plan_uuid']})

        export = api.ExportPlanCase()
        export.call(param.json, **param.extra)
        export.is_response_code(200)

    @story('119244 测试计划-导出全部用例')
    def test_export_part_case(self, _data_storage):
        param = testcase.export_plan_case()
        param.json['plan_uuid'] = _data_storage['plan_uuid']
        param.json['case_uuids'] = _data_storage['all_uuid']
        param.uri_args({'plan_uuid': _data_storage['plan_uuid']})

        export = api.ExportPlanCase()
        export.call(param.json, **param.extra)
        export.is_response_code(200)

    @story('130839 检查搜索功能：关键字匹配')
    def test_search_plan_case(self, _data_storage):
        param = testcase.search_plan_case()
        param.json['variables']['search']['keyword'] = '示例'
        param.json['variables']['testCaseFilter'][0]['testcasePlan_in'] = [_data_storage['plan_uuid']]
        param.json['variables']['planFilter']['uuid_in'] = [_data_storage['plan_uuid']]

        q = project.ItemGraphql()
        q.call(param.json, **param.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 3)

    @story('130839 检查搜索功能：关键字匹配')
    def test_search_plan_case(self, _data_storage):
        param = testcase.search_plan_case()
        param.json['variables']['search']['keyword'] = '%%*'
        param.json['variables']['testCaseFilter'][0]['testcasePlan_in'] = [_data_storage['plan_uuid']]
        param.json['variables']['planFilter']['uuid_in'] = [_data_storage['plan_uuid']]

        q = project.ItemGraphql()
        q.call(param.json, **param.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 0)

# @fixture(scope='module', autouse=True)
# def _del_plan():
#     """删除所有测试计划数据"""
#     yield
#     p = testcase.query_plan_list()
#
#     gq = project.ItemGraphql()
#     gq.call(p.json, **p.extra)
#     gq.is_response_code(200)
#
#     plans = gq.json()['data']['buckets'][0]['testcasePlans']
#     uuids = [p['uuid'] for p in plans]
#
#     param = testcase.up_plan_status()
#     d = project.DeletePlan()
#
#     for uuid in uuids:
#         param.uri_args({'plan_uuid': uuid})
#         d.call(**param.extra)
#         d.is_response_code(200)
