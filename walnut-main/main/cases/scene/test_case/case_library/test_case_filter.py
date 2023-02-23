from falcons.check import go
from falcons.com.nick import feature, story, fixture, parametrize, step
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
def _case_data(_case_lib, _case_priority):
    param = testcase.add_case()[0]
    param.json['item']['priority'] = _case_priority['pri_uuid'][1]
    param.json['item']['type'] = _case_priority['type_uuid'][0]
    param.json['item']['module_uuid'] = _case_lib['module_uuid']
    param.json['item']['testcase_module'] = _case_lib['module_uuid']
    param.json['item']['library_uuid'] = _case_lib['lib_uuid']
    param.json['item']['testcase_library'] = _case_lib['lib_uuid']

    add = project.ItemsAdd()
    # 创建3条用例
    for name in names:
        param.json['item']['name'] = name
        add.call(param.json, **param.extra)
        add.is_response_code(200)


@feature('用例库筛选器')
class TestCaseFilter:

    @story('T130835 筛选器是否存在可选属性')
    def test_filter_attribute(self, _case_lib, _data_storage):
        attributes = (
            '创建时间', '所属模块', '用例ID', '用例类型', '用例名称', '用例维护人', '优先级'
        )
        param = testcase.query_library_case_edit()[0]
        param.json['variables']['fieldFilter']['context']['fieldConfigUUID_in'] = [_case_lib['conf_uuid']]
        param.json['variables']['moduleFilter']['testcaseLibrary_in'] = [_case_lib['lib_uuid']]

        q = project.ItemGraphql()
        q.call(param.json, **param.extra)

        fields = q.json()['data']['fields']

        conf_names = set([n['name'] for n in fields])
        not_exist = []
        for attr in attributes:
            if attr not in conf_names:
                not_exist.append(attr)

        if not_exist:
            raise AssertionError('系统属性不存在')

    @story('T135312 筛选:且筛选')
    def test_filter_and(self, _case_lib, _data_storage):
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['libraryFilter']['uuid_in'] = [_case_lib['lib_uuid']]
        # 根据全称+优先级搜索(已有p1的数据)
        param.json['variables']['testCaseFilter'][0] = {'testcaseLibrary_in': [_case_lib['lib_uuid']],
                                                        'name_match': names[0],
                                                        'priority_in': [_data_storage['pri_uuid'][1]]}

        q = api.CaseFilter()

        q.call(param.json, **param.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 1)
        q.check_response('data.buckets[0].testcaseCases[0].name', names[0])

        # 根据全称+优先级搜索(没有p0的数据)
        param.json['variables']['testCaseFilter'][0] = {'testcaseLibrary_in': [_case_lib['lib_uuid']],
                                                        'name_match': '示例',
                                                        'priority_in': [_data_storage['pri_uuid'][0]]}  # 选择优先级为P0

        q.call(param.json, **param.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 0)

    @story('T135310 筛选:或筛选')
    def test_filter_or(self, _case_lib, _data_storage):
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['libraryFilter']['uuid_in'] = [_case_lib['lib_uuid']]
        # 或筛选，输入没有相对应优先级的数据
        param.json['variables']['testCaseFilter'] = [
            {'testcaseLibrary_in': [_case_lib['lib_uuid']],
             'name_match': names[0]},
            {'testcaseLibrary_in': [_case_lib['lib_uuid']],
             'priority_in': [_data_storage['pri_uuid'][0]]}  # 选择优先级为P0，原数据为P1，或筛选可查出数据
        ]

        q = api.CaseFilter()

        q.call(param.json, **param.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 1)

    @story('T135235 筛选:创建时间（等于）')
    def test_create_time(self, _case_lib, _data_storage):
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0] = {'testcaseLibrary_in': [_case_lib['lib_uuid']],
                                                        'createTime_range': {'equal': f'{mocks.date_today()}'}}

        q = api.CaseFilter()

        q.call(param.json, **param.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 3)

        # 获取所有用例id
        ids = q.json()['data']['buckets'][0]['testcaseCases']
        _data_storage |= {'id': [id['number'] for id in ids]}

    @story('T135243 筛选:用例ID（等于）')
    def test_case_id(self, _case_lib, _data_storage):
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0] = {"testcaseLibrary_in": [_case_lib['lib_uuid']],
                                                        "number_equal": _data_storage['id'][1]}

        q = api.CaseFilter()

        q.call(param.json, **param.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].testcaseCases[0].name', names[1])

    @story('T135244 筛选:用例类型（包含）')
    def test_case_type(self, _case_lib, _data_storage):
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0] = {"testcaseLibrary_in": [_case_lib['lib_uuid']],
                                                        "type_in": [_data_storage['type_uuid'][0]]}  # 获取类型:功能测试uuid

        q = api.CaseFilter()

        q.call(param.json, **param.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 3)

    @story('T135246 筛选:用例名称（包含）')
    @parametrize('name', (names[0], '用例2'))
    def test_case_name(self, name, _case_lib):
        param = testcase.query_library_cast_list()[0]
        # 根据名称搜索
        param.json['variables']['testCaseFilter'][0] = {'testcaseLibrary_in': [_case_lib['lib_uuid']],
                                                        'name_match': name}

        q = api.CaseFilter()
        q.call(param.json, **param.extra)
        q.is_response_code(200)

        if name == '示例用例1':
            q.check_response('data.buckets[0].pageInfo.count', 1)
            q.check_response('data.buckets[0].testcaseCases[0].name', names[0])
        elif name == '用例2':
            q.check_response('data.buckets[0].pageInfo.count', 2)

    @story('T135250 筛选:用例优先级（包含）')
    def test_case_priority(self, _case_lib, _data_storage):
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0] = {'testcaseLibrary_in': [_case_lib['lib_uuid']],
                                                        'priority_in': [_data_storage['pri_uuid'][1]]}

        q = api.CaseFilter()
        q.call(param.json, **param.extra)

        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 3)

    @story('T135240 筛选:所属模块（包含）')
    def test_module(self, _case_lib):
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0] = {'testcaseLibrary_in': [_case_lib['lib_uuid']],
                                                        'pathModules': {'uuid_in': [_case_lib['module_uuid']]}}

        q = api.CaseFilter()
        q.call(param.json, **param.extra)

        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 3)

    @story('T135248 筛选:用例维护人（包含）')
    @parametrize('assign', ('$currentUser', '$*userStatus:4'))
    def test_case_assign(self, assign, _case_lib):  # 维护人为自己和被禁用者
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0] = {'testcaseLibrary_in': [_case_lib['lib_uuid']],
                                                        'assign_in': [assign]}

        q = api.CaseFilter()
        q.call(param.json, **param.extra)
        q.is_response_code(200)

        if assign == '$currentUser':
            q.check_response('data.buckets[0].pageInfo.count', 3)
        else:
            q.check_response('data.buckets[0].pageInfo.count', 0)
