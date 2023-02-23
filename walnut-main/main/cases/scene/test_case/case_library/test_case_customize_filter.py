import time

from falcons.com.nick import feature, story, fixture, step
from falcons.helper import mocks

from main.api import case as api, project
from main.params import testcase, proj


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

    uuids = []
    add = project.ItemsAdd()
    # 创建3条用例
    for name in names:
        param.json['item']['name'] = name
        add.call(param.json, **param.extra)
        add.is_response_code(200)
        uuids.append(add.json()['item']['uuid'])

    _data_storage |= {'case_uuid': uuids}


@fixture(scope='module', autouse=True)
def _clean_filter_fields(_case_lib):
    yield
    param = testcase.query_filter_fields(_case_lib['conf_uuid'])[0]

    q = project.ItemGraphql()
    q.call(param.json, **param.extra)
    q.is_response_code(200)

    keys = []
    fields = q.json()['data']['fields']
    for field in fields:
        if not field['builtIn']:
            keys.append([field['key']])

    # 先删除用例属性配置关联
    p = proj.delete_program()[0]
    d = project.ItemDelete()
    for key in keys:
        p.uri_args({'item_key': key[0]})
        d.call(**p.extra)
        d.is_response_code(200)

    # 再删除用例属性
    param1 = testcase.query_global_fields()[0]
    qg = project.ItemGraphql()
    qg.call(param1.json, **param1.extra)
    qg.is_response_code(200)

    global_keys = []
    ff = qg.json()['data']['fields']
    for f in ff:
        if not f['builtIn']:
            global_keys.append([f['key']])

    p1 = proj.delete_program()[0]
    d1 = project.ItemDelete()

    time.sleep(1)
    for key in global_keys:
        p1.uri_args({'item_key': key[0]})
        d1.call(**p1.extra)
        d1.is_response_code(200)


@feature('测试用例自定义属性筛选')
class TestCaseCustomizeFilter:

    @story('135252 筛选:自定义文本')
    def test_cus_text(self, _case_lib):
        # 新建'自定义文本'用例属性
        p = testcase.add_attrib('text')[0]
        p.json['item']['name'] = f'文本用例属性-{mocks.num()}'

        add = project.ItemsAdd()
        add.call(p.json, **p.extra)
        add.is_response_code(200)

        ali_uuid = add.json()['item']['aliases']  # 获取属性uuid

        # 用例属性配置
        pp = testcase.add_case_attrib_config()[0]
        pp.json['item']['aliases'] = add.json()['item']['aliases']
        pp.json['item']['context']['field_config_uuid'] = _case_lib['conf_uuid']

        ad = project.ItemsAdd()
        ad.call(pp.json, **pp.extra)
        ad.is_response_code(200)

        # 检查 自定义文本 属性筛选
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0] = {'testcaseLibrary_in': [_case_lib['lib_uuid']],
                                                        f'_{ali_uuid[0]}_match': '文本筛选test'}

        q = api.CaseFilter()
        q.call(param.json, **param.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 0)

    @story('135254 筛选:自定义单选菜单')
    def test_cus_single_choice(self, _case_lib):
        # 新建'自定义单选菜单'用例属性
        p = testcase.add_attrib('option')[0]
        p.json['item']['name'] = f'单选用例属性-{mocks.num()}'
        p.json['item'] |= {'options': [
            {
                "value": "test1",
                "color": "#fff",
                "bg_color": "#307fe2"
            },
            {
                "value": "test2",
                "color": "#fff",
                "bg_color": "#00b388"
            }
        ]}  # 添加单选菜单选项

        add = project.ItemsAdd()
        add.call(p.json, **p.extra)
        add.is_response_code(200)

        ali_uuid = add.json()['item']['aliases']  # 获取属性uuid
        opt_uuid = add.json()['item']['options'][0]['uuid']  # 获取选项uuid

        # 用例属性配置
        pp = testcase.add_case_attrib_config()[0]
        pp.json['item']['aliases'] = add.json()['item']['aliases']
        pp.json['item']['context']['field_config_uuid'] = _case_lib['conf_uuid']

        ad = project.ItemsAdd()
        ad.call(pp.json, **pp.extra)
        ad.is_response_code(200)

        # 检查 自定义单选菜单 属性筛选
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0] = {'testcaseLibrary_in': [_case_lib['lib_uuid']],
                                                        f'_{ali_uuid[0]}_in': [opt_uuid]}

        q = api.CaseFilter()
        q.call(param.json, **param.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 0)

    @story('135258 筛选:自定义单选成员')
    def test_cus_single_member(self, _case_lib):
        # 新建'自定义单选成员'用例属性
        p = testcase.add_attrib('user')[0]
        p.json['item']['name'] = f'单成用例属性-{mocks.num()}'

        add = project.ItemsAdd()
        add.call(p.json, **p.extra)
        add.is_response_code(200)

        ali_uuid = add.json()['item']['aliases']  # 获取属性uuid

        # 用例属性配置
        pp = testcase.add_case_attrib_config()[0]
        pp.json['item']['aliases'] = add.json()['item']['aliases']
        pp.json['item']['context']['field_config_uuid'] = _case_lib['conf_uuid']

        ad = project.ItemsAdd()
        ad.call(pp.json, **pp.extra)
        ad.is_response_code(200)

        # 检查 自定义单选成员 属性筛选
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0] = {'testcaseLibrary_in': [_case_lib['lib_uuid']],
                                                        f'_{ali_uuid[0]}_in': ['$currentUser']}

        q = api.CaseFilter()
        q.call(param.json, **param.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 0)

    @story('135262 筛选:自定义多选菜单')
    def test_cus_many_choice(self, _case_lib):
        # 新建'自定义多选菜单'用例属性
        p = testcase.add_attrib('multi_option')[0]
        p.json['item']['name'] = f'多选用例属性-{mocks.num()}'
        p.json['item'] |= {'options': [
            {
                "value": "test1",
                "color": "#fff",
                "bg_color": "#307fe2"
            },
            {
                "value": "test2",
                "color": "#fff",
                "bg_color": "#00b388"
            }
        ]}  # 添加多选菜单选项

        add = project.ItemsAdd()
        add.call(p.json, **p.extra)
        add.is_response_code(200)

        ali_uuid = add.json()['item']['aliases']  # 获取属性uuid
        opt_uuid1 = add.json()['item']['options'][0]['uuid']  # 获取选项uuid
        opt_uuid2 = add.json()['item']['options'][1]['uuid']

        # 用例属性配置
        pp = testcase.add_case_attrib_config()[0]
        pp.json['item']['aliases'] = add.json()['item']['aliases']
        pp.json['item']['context']['field_config_uuid'] = _case_lib['conf_uuid']

        ad = project.ItemsAdd()
        ad.call(pp.json, **pp.extra)
        ad.is_response_code(200)

        # 检查 自定义多选菜单 属性筛选
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0] = {'testcaseLibrary_in': [_case_lib['lib_uuid']],
                                                        f'_{ali_uuid[0]}_in': [opt_uuid1, opt_uuid2]}

        q = api.CaseFilter()
        q.call(param.json, **param.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 0)

    @story('135266 筛选:自定义多选成员')
    def test_cus_many_choice(self, _case_lib):
        # 新建'自定义多选成员'用例属性
        p = testcase.add_attrib('user_list')[0]
        p.json['item']['name'] = f'多成员例属性-{mocks.num()}'

        add = project.ItemsAdd()
        add.call(p.json, **p.extra)
        add.is_response_code(200)

        ali_uuid = add.json()['item']['aliases']  # 获取属性uuid

        # 用例属性配置
        pp = testcase.add_case_attrib_config()[0]
        pp.json['item']['aliases'] = add.json()['item']['aliases']
        pp.json['item']['context']['field_config_uuid'] = _case_lib['conf_uuid']

        ad = project.ItemsAdd()
        ad.call(pp.json, **pp.extra)
        ad.is_response_code(200)

        # 检查 自定义多选成员 属性筛选
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0] = {'testcaseLibrary_in': [_case_lib['lib_uuid']],
                                                        f'_{ali_uuid[0]}_in': ['$currentUser']}

        q = api.CaseFilter()
        q.call(param.json, **param.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 0)

    @story('135273 筛选:自定义浮点数')
    def test_cus_float(self, _case_lib, _data_storage):
        # 新建'自定义浮点数'用例属性
        p = testcase.add_attrib('float')[0]
        p.json['item']['name'] = f'浮点数用例属性-{mocks.num()}'

        add = project.ItemsAdd()
        add.call(p.json, **p.extra)
        add.is_response_code(200)

        ali_uuid = add.json()['item']['aliases']  # 获取属性uuid

        # 用例属性配置
        pp = testcase.add_case_attrib_config()[0]
        pp.json['item']['aliases'] = add.json()['item']['aliases']
        pp.json['item']['context']['field_config_uuid'] = _case_lib['conf_uuid']

        ad = project.ItemsAdd()
        ad.call(pp.json, **pp.extra)
        ad.is_response_code(200)

        # 更新用例-自定义浮点数值
        p_float = {
            "query": "\n          mutation UPDATE_TEST_CASE {\n            updateTestcaseCase (key: $key _%s: $_%s item_type: $item_type) {\n              key\n            }\n          }\n        " % (
                ali_uuid[0], ali_uuid[0]),
            "variables": {
                "key": f"testcase_case-{_data_storage['case_uuid'][0]}",  # 更新第一个用例
                f"_{ali_uuid[0]}": 188000,
                "item_type": "testcase_case"
            }
        }
        qg = project.ItemGraphql()
        qg.call(p_float, **p.extra)
        qg.is_response_code(200)

        with step('选项条件选择：自定义浮点数'):
            param = testcase.query_library_cast_list()[0]
            param.json['variables']['testCaseFilter'][0] = {'testcaseLibrary_in': [_case_lib['lib_uuid']],
                                                            f'_{ali_uuid[0]}_equal': 188000}

            q = api.CaseFilter()
            q.call(param.json, **param.extra)
            q.is_response_code(200)
            q.check_response('data.buckets[0].pageInfo.count', 1)

    @story('135284 筛选:自定义日期')
    def test_cus_date(self, _case_lib):
        # 新建'自定义日期'用例属性
        p = testcase.add_attrib('date')[0]
        p.json['item']['name'] = f'日期用例属性-{mocks.num()}'

        add = project.ItemsAdd()
        add.call(p.json, **p.extra)
        add.is_response_code(200)

        ali_uuid = add.json()['item']['aliases']  # 获取属性uuid

        # 用例属性配置
        pp = testcase.add_case_attrib_config()[0]
        pp.json['item']['aliases'] = add.json()['item']['aliases']
        pp.json['item']['context']['field_config_uuid'] = _case_lib['conf_uuid']

        ad = project.ItemsAdd()
        ad.call(pp.json, **pp.extra)
        ad.is_response_code(200)

        # 检查 自定义日期 属性筛选
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0] = {'testcaseLibrary_in': [_case_lib['lib_uuid']],
                                                        f'_{ali_uuid[0]}_range': {'equal': f'{mocks.date_today()}'}}

        q = api.CaseFilter()
        q.call(param.json, **param.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 0)

    @story('135306 筛选:自定义整数')
    @story('135718 TestCase 配置中心 - 用例属性配置详情页：删除用例属性')
    def test_cus_int(self, _case_lib):
        # 新建'自定义整数'用例属性
        p = testcase.add_attrib('integer')[0]
        p.json['item']['name'] = f'整数用例属性-{mocks.num()}'

        add = project.ItemsAdd()
        add.call(p.json, **p.extra)
        add.is_response_code(200)

        ali_uuid = add.json()['item']['aliases']  # 获取属性uuid

        # 用例属性配置
        pp = testcase.add_case_attrib_config()[0]
        pp.json['item']['aliases'] = add.json()['item']['aliases']
        pp.json['item']['context']['field_config_uuid'] = _case_lib['conf_uuid']

        ad = project.ItemsAdd()
        ad.call(pp.json, **pp.extra)
        ad.is_response_code(200)

        # 检查 自定义整数 属性筛选
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0] = {'testcaseLibrary_in': [_case_lib['lib_uuid']],
                                                        f'_{ali_uuid[0]}_equal': 8}

        q = api.CaseFilter()
        q.call(param.json, **param.extra)
        q.is_response_code(200)
        q.check_response('data.buckets[0].pageInfo.count', 0)
