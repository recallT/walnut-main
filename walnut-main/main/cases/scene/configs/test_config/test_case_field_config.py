from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, step
from falcons.helper import mocks

from main.actions.case import CaseAction
from main.api import case, project as prj, project
from main.params import testcase as tc


@fixture(scope='module', autouse=True)
def library_add(_storage):
    add = CaseAction.library_add()

    _storage |= {'library_uuid': add.value('library.uuid'),
                 'module_uuid': add.json()['library']['modules'][0]['uuid']}


@fixture(scope='module')
def _storage():
    p = {}
    return p


@fixture(scope='module', autouse=True)
def _clean_data(_storage):
    yield

    # 删除用例属性配置
    CaseAction.del_field_config(_storage['copy_uuid'])


@feature('配置中心-用例属性配置')
class TestCaseFiledConfig(Checker):

    @classmethod
    def add_testcase_config(cls, field_type, library_uuid, opt=None):
        """
        添加测试用例属性 并添加到用例属性配置中
        校验用例库属性是否存在
        校验用例属性配置中是否存在
        删除新增数据
        :param field_type: 属性类型
        :param library_uuid: 用例库UUID
        :param opt: 选项值
        :return:
        """

        field_name = 'testcase-config-' + mocks.num()
        with step('点击 选择属性 下拉框，选择用例属性 单选菜单，点击确定'):
            items, field_key = CaseAction.attrib_add(field_type, field_name, option=opt)

        with step('进入用例库 a 的详情页，点击新建用例，查看右侧属性'):
            res = CaseAction.case_lib_field_config(library_uuid)
            names = [f['name'] for f in res.value('data.fields')]

            assert field_name in names
        with step('进入用例属性配置 - 默认配置的编辑页，查看属性名称'):
            res = CaseAction.case_field_config()
            config_names = [f['name'] for f in res.value('data.fields')]

            assert field_name in config_names

        with step('删除数据'):
            CaseAction.del_test_field(field_key=items.value('item.key'))
            CaseAction.del_test_field(field_key=field_key)

    @story('T135731 TestCase 配置中心 - 用例属性配置：检查列表默认配置表现')
    @story('T135734 TestCase 配置中心 - 用例属性配置：列表检查')
    def test_check_case_config_list(self):
        q = tc.query_case_config_list()[0]
        resp = self.call(project.ItemGraphql, param=q)
        names = [r['name'] for r in resp.value('data.testcaseFieldConfigs')]
        assert '默认配置' in names

    @story('T135719 TestCase 配置中心 - 用例属性配置详情页：添加单行文本类型用例属性')
    def test_add_testcase_config_text(self, _storage):
        self.add_testcase_config(field_type='text', library_uuid=_storage['library_uuid'])

    @story('T135720 TestCase 配置中心 - 用例属性配置详情页：添加单选菜单类型用例属性')
    def test_add_testcase_config_option(self, _storage):
        options = [{"value": "11", "color": "#fff", "bg_color": "#307fe2"}]
        self.add_testcase_config(field_type='option', library_uuid=_storage['library_uuid'], opt=options)

    @story('T135721 TestCase 配置中心 - 用例属性配置详情页：添加单选成员类型用例属性')
    def test_add_testcase_config_user(self, _storage):
        self.add_testcase_config(field_type='user', library_uuid=_storage['library_uuid'])

    @story('T135722 TestCase 配置中心 - 用例属性配置详情页：添加多行文本类型用例属性')
    def test_add_testcase_config_multi_line_text(self, _storage):
        self.add_testcase_config(field_type='multi_line_text', library_uuid=_storage['library_uuid'])

    @story('T135723 TestCase 配置中心 - 用例属性配置详情页：添加多选菜单类型用例属性')
    def test_add_testcase_config_multi_option(self, _storage):
        options = [{"value": "11", "color": "#fff", "bg_color": "#307fe2"}]
        self.add_testcase_config(field_type='multi_option', library_uuid=_storage['library_uuid'], opt=options)

    @story('T135724 TestCase 配置中心 - 用例属性配置详情页：添加多选成员类型用例属性')
    def test_add_testcase_config_user_list(self, _storage):
        self.add_testcase_config(field_type='user_list', library_uuid=_storage['library_uuid'])

    @story('T135725 TestCase 配置中心 - 用例属性配置详情页：添加浮点数类型用例属性')
    def test_add_testcase_config_float(self, _storage):
        self.add_testcase_config(field_type='float', library_uuid=_storage['library_uuid'])

    @story('T135726 TestCase 配置中心 - 用例属性配置详情页：添加日期类型用例属性')
    def test_add_testcase_config_date(self, _storage):
        self.add_testcase_config(field_type='date', library_uuid=_storage['library_uuid'])

    @story('T135727 TestCase 配置中心 - 用例属性配置详情页：添加时间类型用例属性')
    def test_add_testcase_config_time(self, _storage):
        self.add_testcase_config(field_type='time', library_uuid=_storage['library_uuid'])

    @story('T135728 TestCase 配置中心 - 用例属性配置详情页：添加整数类型用例属性')
    def test_add_testcase_config_integer(self, _storage):
        self.add_testcase_config(field_type='integer', library_uuid=_storage['library_uuid'])

    @story('T135712 TestCase 配置中心 - 用例属性配置详情页：检查列表系统属性表现')
    def test_check_testcase_config_list(self):
        default_values = {'用例ID', '所属用例库', '备注', '用例维护人', '优先级', '用例类型', '所属模块', '用例名称', '创建时间', '前置条件'}
        res = CaseAction.case_field_config()
        values = [r['name'] for r in res.value('data.fields')]
        assert set(values) >= default_values

    @story('T135709 TestCase 配置中心 - 用例属性配置详情页：编辑系统属性优先级的属性默认值')
    def test_check_testcase_config_default_values(self, _storage):
        res = CaseAction.case_field_config()
        with step('优先级属性已包含：P0、P1、P2、P3、P4'):
            default_values = {'P3', 'P4', 'P1', 'P0', 'P2'}
            options = [r['options'] for r in res.value('data.fields') if r['name'] == '优先级'][0]
            values = [f['value'] for f in options]
            assert set(values) >= default_values

        with step('点击优先级的属性默认值下拉列表，选择P0'):
            p0_uuid = [f['uuid'] for f in options if f['value'] == 'P0']
            key = [r['key'] for r in res.value('data.fields') if r['name'] == '优先级'][0]
            CaseAction.update_config_default_values(field_key=key, default_value_uuid=p0_uuid)

        with step('进入用例库 a中，点击新建用例，查看优先级属性的默认值'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            default_value = [r['defaultValue'] for r in res.value('data.fields') if r['name'] == '优先级'][0]
            assert default_value == p0_uuid
        with step('找到优先级的属性默认值下拉框，点击清空按钮'):
            CaseAction.update_config_default_values(field_key=key, default_value_uuid=None)

        with step('进入用例库 a中，点击新建用例，查看优先级属性的默认值'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            default_value = [r['defaultValue'] for r in res.value('data.fields') if r['name'] == '优先级'][0]
            assert default_value is None

    @story('T135708 TestCase 配置中心 - 用例属性配置详情页：编辑系统属性用例类型的属性默认值')
    def test_check_testcase_config_default_values_case_type(self, _storage):
        res = CaseAction.case_field_config()
        with step('用例类型属性已包含：功能测试、性能测试、接口测试'):
            default_values = {'功能测试', '性能测试', '接口测试'}
            options = [r['options'] for r in res.value('data.fields') if r['name'] == '用例类型'][0]
            values = [f['value'] for f in options]
            assert set(values) >= default_values

        with step('点击用例类型的属性默认值下拉列表，选择功能测试'):
            p_uuid = [f['uuid'] for f in options if f['value'] == '功能测试']
            key = [r['key'] for r in res.value('data.fields') if r['name'] == '用例类型'][0]
            CaseAction.update_config_default_values(field_key=key, default_value_uuid=p_uuid)

        with step('进入用例库 a中，点击新建用例，查看用例类型属性的默认值'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            default_value = [r['defaultValue'] for r in res.value('data.fields') if r['name'] == '用例类型'][0]
            assert default_value == p_uuid
        with step('找到用例类型的属性默认值下拉框，点击清空按钮'):
            CaseAction.update_config_default_values(field_key=key, default_value_uuid=None)

        with step('进入用例库 a中，点击新建用例，查看用例类型属性的默认值'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            default_value = [r['defaultValue'] for r in res.value('data.fields') if r['name'] == '用例类型'][0]
            assert default_value is None

    @story('T135711 TestCase 配置中心 - 用例属性配置详情页：编辑自定义属性的属性默认值')
    def test_check_testcase_config_default_values_self_defining(self, _storage):
        with step('前置条件：存在一个自定义属性'):
            field_name = '自定义属性-' + mocks.num()
            opts = [
                {
                    "value": "test_1",
                    "color": "#fff",
                    "bg_color": "#307fe2"
                },
                {
                    "value": "test_2",
                    "color": "#fff",
                    "bg_color": "#00b388"
                }
            ]
            items, field_key = CaseAction.attrib_add('option', field_name, opts)

        with step('点击自定义属性默认值下拉列表，选择test_1'):
            res = CaseAction.case_field_config()
            options = [r['options'] for r in res.value('data.fields') if r['name'] == field_name][0]
            key = [r['key'] for r in res.value('data.fields') if r['name'] == field_name][0]
            p_uuid = [f['uuid'] for f in options if f['value'] == 'test_1']
            CaseAction.update_config_default_values(field_key=key, default_value_uuid=p_uuid)

        with step('进入用例库 a中，点击新建用例，查看属性的默认值'):
            resp = CaseAction.case_lib_field_config(_storage['library_uuid'])
            default_value = [r['defaultValue'] for r in resp.value('data.fields') if r['name'] == field_name][0]
            assert default_value == p_uuid
        with step('找到属性默认值下拉框，点击清空按钮'):
            CaseAction.update_config_default_values(field_key=key, default_value_uuid=None)

        with step('进入用例库 a中，点击新建用例，查看属性的默认值'):
            response = CaseAction.case_lib_field_config(_storage['library_uuid'])
            default_value = [r['defaultValue'] for r in response.value('data.fields') if r['name'] == field_name][0]
            assert default_value is None

        with step('删除数据'):
            CaseAction.del_test_field(field_key=items.value('item.key'))
            CaseAction.del_test_field(field_key=field_key)

    @story('T135732 TestCase 配置中心 - 用例属性配置：检查默认配置的属性默认值（新建团队开箱）')
    def test_check_default_values(self):
        res = CaseAction.case_field_config()
        with step('用例类型属性'):
            options = [r['options'] for r in res.value('data.fields') if r['name'] == '用例类型'][0]
            values = [f['value'] for f in options]
            assert '功能测试' in values
        with step('优先级属性'):
            options = [r['options'] for r in res.value('data.fields') if r['name'] == '优先级'][0]
            values = [f['value'] for f in options]
            assert 'P0' in values

    @story('135737 新建用例属性配置')
    def test_add_field_config(self, _storage):
        with step('输入配置名称点击确定'):
            param = tc.add_filed_config()[0]
            add = self.call(prj.ItemsAdd, param)

            key, name, uuid = add.value('item.key'), add.value('item.name'), add.value('item.uuid')

            _storage |= {'custom_config_key': key, 'custom_uuid': uuid}  # 存储自定义配置属性key和uuid

        with step('新建用例库弹窗中点击下拉用例属性配置'):
            prm = tc.case_field_config_list()[0]
            res = self.call(prj.ItemGraphql, prm)

            assert name in [n['name'] for n in res.value('data.testcaseFieldConfigs')]

    @story('135738 重命名用例属性配置')
    def test_rename_field_config(self, _storage):
        with step('修改为配置2，点击确定'):
            CaseAction.attrib_update(field_name, _storage['custom_config_key'])

        with step('新建用例库弹窗中点击下拉用例属性配置'):
            prm = tc.case_field_config_list()[0]
            res = self.call(prj.ItemGraphql, prm)

            assert field_name in [n['name'] for n in res.value('data.testcaseFieldConfigs')]

    @story('135733 检查新建用例属性配置的属性默认值')
    def test_field_config_default(self, _storage):
        """属性配置默认值"""

        with step('查看 配置 详情页'):
            param = tc.query_filter_fields(_storage['custom_uuid'])[0]
            gq = self.call(prj.ItemGraphql, param)

            priority = [d['defaultValue'] for d in gq.value('data.fields') if d['name'] == '优先级'][0]
            case_type = [d['defaultValue'] for d in gq.value('data.fields') if d['name'] == '用例类型'][0]

            assert priority is None, case_type is None

    @story('135730 复制用例属性配置')
    def test_copy_field_config(self, _storage):
        with step('输入复制配置名称，点击确定'):
            param = tc.field_copy()[0]
            param.json_update('source_field_config', _storage['custom_uuid'])

            cp = self.call(case.CaseFieldConfigCopy, param)
            cp_uuid, cp_name = cp.value('uuid'), cp.value('name')

            _storage |= {'copy_uuid': f'testcase_field_config-{cp_uuid}'}

        with step('新建用例库弹窗中点击下拉用例属性配置'):
            prm = tc.case_field_config_list()[0]
            res = self.call(prj.ItemGraphql, prm)

            assert cp_name in [n['name'] for n in res.value('data.testcaseFieldConfigs')]

    @story('135735 删除用例属性配置（未被用例库使用）')
    def test_del_unused_field_config(self, _storage):
        """删除未使用属性配置"""

        with step('点击删除'):
            # 删除用例属性配置
            CaseAction.del_field_config(_storage['custom_config_key'])

        with step('新建用例库弹窗中点击下拉用例属性配置'):
            prm = tc.case_field_config_list()[0]
            res = self.call(prj.ItemGraphql, prm)

            assert field_name not in [n['name'] for n in res.value('data.testcaseFieldConfigs')]

    @story('135736 删除用例属性配置（已被用例库使用）')
    def test_del_used_field_config(self):
        """删除已使用属性配置"""

        with step('前置条件'):
            # add属性配置
            param = tc.add_filed_config()[0]
            add = self.call(prj.ItemsAdd, param)
            key, name = add.value('item.key'), add.value('item.name')

            # add用例库
            config_uuid = CaseAction.field_config(name)  # 获取add属性配置UUID
            prm = tc.library_add()[0]
            prm.json_update('library.field_config_uuid', config_uuid[0])
            self.call(case.AddCaseLibrary, prm)

        with step('点击删除'):
            # 删除用例属性配置
            CaseAction.del_field_config(key)  # code应为400，实际200前端有处理，接口未做

    @story('135729 用例属性配置：编辑用例属性配置')
    def test_edit_case_field_config(self):
        """"""


field_name = f'配置{mocks.num()}'
