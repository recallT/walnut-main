from falcons.com.nick import feature, story, fixture, parametrize, step
from main.api import case as api
from main.api import project
from main.params import proj, testcase
from . import add_case_library


# 初始化用例库
@fixture(scope='module', autouse=True)
def _storage():
    return add_case_library()


# 获取用例属性配置
@fixture(scope='module', autouse=True)
def _case_priority(_storage, _data_storage):
    param = testcase.query_library_case_edit()[0]
    param.json['variables']['fieldFilter']['context']['fieldConfigUUID_in'] = [_storage['config_uuid']]
    param.json['variables']['moduleFilter']['testcaseLibrary_in'] = [_storage['uuid']]

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


@fixture(scope='module')
def _data_storage():
    p = {}
    return p


@feature('用例库中用例操作')
class TestLibraryCase:

    @story('T139007 新建用例')
    @story('141266 用例库：新建用例库')
    @story('T149458 超级管理员：创建用例')
    @story('139008 用例库详情：新建用例弹窗检查')
    @story('141250 用例库详情：显示默认值')
    def test_add_case(self, _storage, _data_storage):
        param = testcase.add_case()[0]
        param.json['item']['priority'] = _data_storage['pri_uuid'][0]
        param.json['item']['type'] = _data_storage['type_uuid'][0]
        param.json['item']['module_uuid'] = _storage['module_uuid']
        param.json['item']['testcase_module'] = _storage['module_uuid']
        param.json['item']['library_uuid'] = _storage['uuid']
        param.json['item']['testcase_library'] = _storage['uuid']

        add = project.ItemsAdd()

        with step('在「用例库A」下点击「新建用例」'):
            # 必填项为空
            add.call(param.json, **param.extra)
            add.is_response_code(400)
            add.check_response('errcode', 'InvalidParameter.TestcaseCase.Name.Empty')

            # 必填项不为空
            param.json['item']['name'] = 'test新建用例'
            add.call(param.json, **param.extra)
            add.is_response_code(200)
            add.check_response('item.name', 'test新建用例')

            case_uuid = add.json()['item']['uuid']
            _data_storage |= {'case_uuid': [case_uuid]}

    @story('T118721 复制用例')
    def test_copy_case(self, _storage, _data_storage):
        param = proj.copy_case()[0]

        with step('点击「选择用例」'):
            param.json['target_library_uuid'] = _storage['uuid']
            param.json['target_module_uuid'] = _storage['module_uuid']
            param.json['case_uuids'] = _data_storage['case_uuid']
            param.uri_args({'lib_uuid': _storage['uuid']})

        with step('点击确定'):
            copy = api.CopyCase()
            copy.call(param.json, **param.extra)
            copy.is_response_code(200)

        _data_storage |= {'cp_case_uuid': copy.json()['success_cases']}

    @story('118722 移动用例')
    def test_move_case(self, _storage, _data_storage):
        # 先创建新的用例库，做移动场景
        data = testcase.query_case_config_list()[0]
        q = project.ItemGraphql()
        q.call(data.json, **data.extra)
        config_uuid = q.json()['data']['testcaseFieldConfigs'][0]['uuid']

        param = testcase.add_case_library()[0]
        param.json['library']['field_config_uuid'] = config_uuid
        param.json['library']['name'] = 'move用例库'
        add_libra = api.AddCaseLibrary()
        add_libra.call(param.json, **param.extra)
        add_libra.is_response_code(200)

        # 获取new用例库uuid、module_uuid
        uuid = add_libra.json()['library']['uuid']
        module_uuid = add_libra.json()['library']['modules'][0]['uuid']
        _data_storage |= {'new_lib_uuid': uuid}
        _data_storage |= {'new_mod_uuid': module_uuid}

        # 移动用例
        with step('选择用例、选择用例库'):
            move_param = testcase.move_case()[0]
            move_param.json['target_library_uuid'] = uuid
            move_param.json['target_module_uuid'] = module_uuid
            move_param.json['case_uuids'] = _data_storage['case_uuid']
            move_param.uri_args({'library_uuid': _storage['uuid']})

        move = api.MoveLibraryCase()

        with step('点击确定'):
            move.call(move_param.json, **move_param.extra)
            move.is_response_code(200)

        # 检查原用例库中不存在被移出的用例
        # original_data = query_library_cast_list()[0]
        # original_data.json['variables']['testCaseFilter'][0]['testcaseLibrary_in'] = _storage['uuid']
        # original_data.json['variables']['libraryFilter']['uuid_in'] = _storage[uuid]
        #
        # original = ItemGraphql()
        # original.call(original_data.json, **original_data.extra)

    @story('新建1000条用例')
    @parametrize('param', testcase.add_case())
    def test_add_case_1000(self, param, _storage, _data_storage):
        param.json['item']['priority'] = _data_storage['pri_uuid'][0]
        param.json['item']['type'] = _data_storage['type_uuid'][0]
        param.json['item']['module_uuid'] = _storage['module_uuid']
        param.json['item']['testcase_module'] = _storage['module_uuid']
        param.json['item']['library_uuid'] = _storage['uuid']
        param.json['item']['testcase_library'] = _storage['uuid']

        add = project.ItemsAdd()

        # 存储所有用例uuid
        all_uuid = []

        for num in range(1, 5):
            param.json['item']['name'] = f'test新建用例_{num}'

            add.call(param.json, **param.extra)
            add.is_response_code(200)
            add.check_response('item.name', f'test新建用例_{num}')
            all_uuid.append(add.json()['item']['uuid'])

        _data_storage |= {'all_uuid': all_uuid}

    @story('移动1000条用例')
    @parametrize('param', testcase.move_case())
    def test_move_case_1000(self, param, _storage, _data_storage):
        param.json['target_library_uuid'] = _data_storage['new_lib_uuid']
        param.json['target_module_uuid'] = _data_storage['new_mod_uuid']
        param.json['case_uuids'] = _data_storage['all_uuid']
        param.uri_args({'library_uuid': _storage['uuid']})

        move = api.MoveLibraryCase()
        move.call(param.json, **param.extra)
        move.is_response_code(200)

    @story('T119242 导出全部用例')
    @parametrize('param', testcase.export_case())
    def test_export_all_case(self, param, _data_storage):
        with step('选择导出全部用例'):
            param.json['library_uuid'] = _data_storage['new_lib_uuid']
            param.json['case_uuids'] = _data_storage['all_uuid']
            param.uri_args({'library_uuid': _data_storage['new_lib_uuid']})

        export = api.ExportLibraryCase()

        with step('点击确定'):
            export.call(param.json, **param.extra)
            export.is_response_code(200)

    @story('T119243 导出选中用例')
    @story('119245 导出用例：导出选中用例')
    @parametrize('param', testcase.export_case())
    def test_export_part_case(self, param, _data_storage):
        with step('选中4条用例，点击导出选中用例'):
            param.json['library_uuid'] = _data_storage['new_lib_uuid']
            param.json['case_uuids'] = _data_storage['all_uuid'][:4]
            param.uri_args({'library_uuid': _data_storage['new_lib_uuid']})

            export = api.ExportLibraryCase()
            export.call(param.json, **param.extra)
            export.is_response_code(200)

    @story('T135335 删除用例')
    @story('T149459 超级管理员：删除用例')
    @parametrize('param', testcase.delete_case())
    def test_delete_case(self, param, _data_storage):
        with step('选中多条用例，点击删除'):
            param.json['case_uuids'] = _data_storage['all_uuid'][:2]
            param.uri_args({'library_uuid': _data_storage['new_lib_uuid']})

        delete = api.DeleteLibraryCase()

        with step('点击确定'):
            delete.call(param.json, **param.extra)
            delete.is_response_code(200)
            delete.check_response('errcode', 'OK')

    @story('T135616 搜索用例')
    @story('141265 用例库：搜索')
    def test_search_case(self, _data_storage):
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0]['testcaseLibrary_in'] = [_data_storage['new_lib_uuid']]
        param.json['variables']['libraryFilter']['uuid_in'] = [_data_storage['new_lib_uuid']]

        q = project.ItemGraphql()
        q.call(param.json, **param.extra)
        q.is_response_code(200)

        # 获取到name、id，搜索使用
        case_name = q.json()['data']['buckets'][0]['testcaseCases'][0]['name']
        case_id = q.json()['data']['buckets'][0]['testcaseCases'][0]['number']

        with step('输入id进行搜索'):
            param.json['variables'] |= {'search': {'keyword': case_id}}
            q = project.ItemGraphql()
            q.call(param.json, **param.extra)
            q.is_response_code(200)
            q.check_response('data.buckets[0].testcaseCases[0].number', case_id)

        with step('输入name进行搜索'):
            param.json['variables'] |= {'search': {'keyword': case_name}}
            q = project.ItemGraphql()
            q.call(param.json, **param.extra)
            q.is_response_code(200)
            q.check_response('data.buckets[0].testcaseCases[0].name', case_name)

        with step('输入无法命中的关键字'):
            param.json['variables'] |= {'search': {'keyword': '无命中'}}
            q = project.ItemGraphql()
            q.call(param.json, **param.extra)
            q.is_response_code(200)

    @story('用例升序排序')
    @story('141270 用例库详情：用例列表排序')
    @parametrize('data', ({"type": {"value": "ASC"}}, {"namePinyin": "ASC"}, {"assign": {"name": "ASC"}},
                          {"priority": {"value": "ASC"}}))
    def test_case_sort(self, data, _storage):
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0]['testcaseLibrary_in'] = [_storage['uuid']]
        param.json['variables']['libraryFilter']['uuid_in'] = [_storage['uuid']]
        # 根据不同用例类型排序
        param.json['variables']['orderByFilter'] |= data

        q = project.ItemGraphql()
        q.call(param.json, **param.extra)

        q.is_response_code(200)

    @story('用例降序排序')
    @story('141269 用例列表-默认排序')
    @parametrize('data', ({"type": {"value": "DESC"}}, {"namePinyin": "DESC"}, {"assign": {"name": "DESC"}},
                          {"priority": {"value": "DESC"}}))
    def test_case_sort(self, data, _storage):
        param = testcase.query_library_cast_list()[0]
        param.json['variables']['testCaseFilter'][0]['testcaseLibrary_in'] = [_storage['uuid']]
        param.json['variables']['libraryFilter']['uuid_in'] = [_storage['uuid']]
        # 根据不同用例类型排序
        param.json['variables']['orderByFilter'] |= data

        q = project.ItemGraphql()
        q.call(param.json, **param.extra)

        q.is_response_code(200)

    @story('T128817 用例关联到测试计划')
    def test_case_rel_plan(self, _data_storage):
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

        plan_uuid = add.json()['plan']['uuid']
        case_uuid = _data_storage['cp_case_uuid']

        # 关联测试计划
        with step('选择多条用例，点击关联计划'):
            rp = testcase.case_rel_plan()[0]
            rp.json['case_uuids'] = case_uuid
            rp.uri_args({'plan_uuid': plan_uuid})

        with step('点击确定'):
            rel = api.CaseRelPlan()
            rel.call(rp.json, **rp.extra)
            rel.is_response_code(200)

        with step('清除测试计划数据'):
            param = testcase.up_plan_status()
            q = api.DeletePlan()
            param.uri_args({'plan_uuid': plan_uuid})
            q.call(**param.extra)
            q.is_response_code(200)

    @story('148232 批量用例关联到测试计划')
    def test_batch_case_rel_plan(self):
        """"""

    @story('139009 用例库详情：新建用例，勾选继续创建下一个')
    def test_create_next_case(self):
        """"""