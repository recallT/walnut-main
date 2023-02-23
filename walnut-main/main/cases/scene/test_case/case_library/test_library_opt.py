from falcons.com.nick import feature, story, fixture, parametrize, step
from main.api import case as api
from main.api import project
from main.params import testcase
from . import add_case_library


# 初始化用例库
@fixture(scope='module', autouse=True)
def _storage():
    return add_case_library()


# 创建新用例属性配置
@fixture(scope='module', autouse=True)
def _config(_storage):
    param = testcase.add_filed_config()[0]

    add = project.ItemsAdd()
    add.call(param.json, **param.extra)
    add.is_response_code(200)

    new_config_uuid = add.json()['item']['uuid']

    return {'new_config_uuid': new_config_uuid}


# 删除用于测试的用例属性配置
@fixture(scope='module', autouse=True)
def _clean_field_config(_config):
    yield
    param = testcase.del_field_config()[0]
    param.uri_args({'config_uuid': _config['new_config_uuid']})

    d = api.DeleteTestCaseFieldConfig()
    d.call(**param.extra)
    d.is_response_code(200)


@fixture(scope='class')
def _data():
    return []


@feature('用例库操作')
class TestLibraryOpt:

    @story('用例库详情')
    @story('T148501 超级管理员：删除用例库')
    @story('23360 用例库设置-更多：删除用例库')
    @story('141222 用例库设置 - 更多：删除用例库')
    @story('T148500 测试管理管理员：删除用例库')
    def test_case_library_detail(self, _storage):
        param = testcase.query_library_detail()[0]
        param.json['variables']['libraryFilter']['uuid_in'] = [_storage['uuid']]

        q = project.ItemGraphql()
        q.call(param.json, **param.extra)

        q.is_response_code(200)
        # 校验用例库设置名称
        q.check_response('data.testcaseLibraries[0].name', 'test新建用例库', check_type='contains')
        # 校验用例库属性配置
        q.check_response('data.testcaseLibraries[0].testcaseFieldConfig.name', '默认配置')

    @story('141255 用例库信息：更改用例库名称')
    def test_up_library_name(self, _storage):
        param = testcase.update_library_config()[0]

        with step('修改用例库名称'):
            param.json['library']['uuid'] = _storage['uuid']
            param.json['library']['field_config_uuid'] = _storage['config_uuid']
            param.uri_args({'library_uuid': _storage['uuid']})

        up = api.UpdateLibraryConfig()

        with step('点击更新信息按钮'):
            up.call(param.json, **param.extra)
            up.is_response_code(200)
            up.check_response('library.name', 'update用例库名')

    @story('T141243 添加模块')
    @parametrize('frequency', range(5))
    def test_add_library_module(self, frequency, _storage):
        param = testcase.add_library_module()[0]
        param.uri_args({'library_uuid': _storage['uuid']})

        add = api.AddLibraryModule()
        add.call(param.json, **param.extra)

        add.is_response_code(200)

    @story('T141244 添加子模块')
    def test_add_sub_module(self, _storage, _data):
        q = testcase.query_modules_library()[0]
        q.json['variables']['moduleFilter']['testcaseLibrary_in'] = [_storage['uuid']]
        q.uri_args({'library_uuid': _storage['uuid']})

        qg = project.ItemGraphql()
        qg.call(q.json, **q.extra)
        qg.is_response_code(200)

        # 获取用例库下的所有模块
        modules = qg.json()['data']['testcaseModules']
        for mod in modules:
            _data.append(mod['uuid'])

        with step('点击新建子模块；点击确定'):
            param = testcase.add_library_module()[0]
            param.json['module']['parent_uuid'] = _data[0]
            param.uri_args({'library_uuid': _storage['uuid']})

            add = api.AddLibraryModule()
            add.call(param.json, **param.extra)
            add.is_response_code(200)

    @story('T141245 重命名模块')
    def test_up_library_module(self, _storage, _data):
        param = testcase.update_library_module()[0]
        param.json['module']['uuid'] = _data[0]
        param.uri_args({'library_uuid': _storage['uuid']})

        up = api.UpdateLibraryModule()
        up.call(param.json, **param.extra)

        up.is_response_code(200)

    @story('T141240 删除模块')
    def test_del_module(self, _storage, _data):
        param = testcase.delete_library_module()[0]
        param.json['module_uuid'] = _data[0]
        param.uri_args({'library_uuid': _storage['uuid']})

        d = api.DeleteLibraryModule()
        d.call(param.json, **param.extra)

        d.is_response_code(200)
        d.check_response('type', 'OK')

    @story('权限配置：默认权限')
    def test_permission_config(self, _storage):
        param = testcase.query_library_detail()[0]
        param.json['variables']['libraryFilter']['uuid_in'] = [_storage['uuid']]

        q = project.ItemGraphql()
        q.call(param.json, **param.extra)

        # 校验权限配置有默认「测试管理」管理员权限
        q.check_response('data.testcaseLibraries[0].members[0].type', 'testcase_administrators')

    @story('141256 用例库信息：更改用例属性配置')
    @story('141257 用例库信息：页面检查')
    def test_up_library_config(self, _storage, _config):
        param = testcase.update_library_config()[0]
        with step('修改用例属性配置'):
            param.json['library']['uuid'] = _storage['uuid']
            param.json['library']['field_config_uuid'] = _config['new_config_uuid']
            param.uri_args({'library_uuid': _storage['uuid']})

        up = api.UpdateLibraryConfig()
        with step('点击更新信息按钮'):
            up.call(param.json, **param.extra)

            up.is_response_code(200)
            up.check_response('library.field_config_uuid', _config['new_config_uuid'])

    @story('141261 用例库：列表置顶')
    def test_pin_library(self, _storage):
        param = testcase.pin_library()[0]
        param.uri_args({'library_uuid': _storage['uuid']})

        pin = api.CaseLibraryPin()
        with step('点击「用例库」的置顶icon'):
            pin.call(param.json, **param.extra)
            pin.is_response_code(200)

    @story('取消置顶用例库')
    def test_un_pin_library(self, _storage):
        param = testcase.pin_library()[0]
        param.uri_args({'library_uuid': _storage['uuid']})

        pin = api.CaseLibraryUnPin()
        with step('点击取消「用例库」的置顶icon'):
            pin.call(param.json, **param.extra)
            pin.is_response_code(200)

    @story('141258 用例库：列表计数')
    def test_library_count(self):
        param = testcase.query_library_list()[0]

        q = project.ItemGraphql()
        q.call(param.json, **param.extra)

        len(q.json()['data']['testcaseLibraries'])
        q.is_response_code(200)

    @story('141259 用例库：列表排序')
    @parametrize('name', ('A-用例库', 'Z-用例库'))
    def test_library_sort(self, name, _config):
        param = testcase.add_case_library()[0]
        param.json['library']['field_config_uuid'] = _config['new_config_uuid']
        param.json['library']['name'] = name
        add_libra = api.AddCaseLibrary()
        add_libra.call(param.json, **param.extra)
        add_libra.is_response_code(200)

        # 检查用例库列表排序按字母正序排序
        data = testcase.query_library_list()[0]
        q = project.ItemGraphql()
        q.call(data.json, **data.extra)
        q.is_response_code(200)

        # 并发时跟其他用例冲突
        # if name == 'A-用例库':
        #     q.check_response('data.testcaseLibraries[0].name', name)  # 字母A排在最前
        # elif name == 'Z-用例库':
        #     q.check_response('data.testcaseLibraries[-1].name', name)  # 字母Z排在最后

    @story('T141237 调整功能模块位置')
    @parametrize('order', ('brother', 'child'))  # brother兄弟层级\child父级
    def test_module_brother_sort(self, order, _data, _storage):
        param = testcase.modules_sort()[0]
        # 获取某个用例进行排序
        param.json['module_uuid'] = _data[2]
        param.json['previous_uuid'] = _data[4]
        param.json['previous_relation'] = order

        param.uri_args({'library_uuid': _storage['uuid']})

        sort = api.ModulesSort()
        sort.call(param.json, **param.extra)
        sort.is_response_code(200)
