from falcons.check import Checker, go
from falcons.com.nick import feature, story, fixture, step, parametrize
from falcons.helper import mocks

from main.actions.case import CaseAction
from main.api import case, project as prj, project
from main.params import proj as p, conf, testcase
from main.params import testcase as tc


@fixture(scope='class', autouse=True)
def library_add(_storage):
    add = CaseAction.library_add()

    _storage |= {'library_uuid': add.value('library.uuid'),
                 'module_uuid': add.json()['library']['modules'][0]['uuid']}


@fixture(scope='class')
def _storage():
    p = {}
    return p


@fixture(autouse=True)
def _clean_data(_storage):
    yield

    # 删除用例属性和属性配置详情
    if 'filed_config_key' in _storage:
        CaseAction.del_case_field_and_config(_storage['filed_config_key'], _storage['filed_key'])

    # 删除用例属性配置
    if 'config_key' in _storage:
        CaseAction.del_field_config(_storage['config_key'])


@feature('配置中心-用例属性')
class TestConfigCaseFiled(Checker):

    @story('23038 新建用例库')
    @story('147497 新建用例库')
    @story('147499 新建用例库')
    @story('T149465 超级管理员：新建用例库')
    @story('121315 概览 - 用例库：新建用例库')
    @story('135672 编辑用例属性：用例类型删除选项值（用例类型选项未被选用）')
    def test_del_not_selected_value(self, _storage):
        """删除未被选用的选项值"""

        with step('前置条件'):
            field_name = '示例单选菜单属性'
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
                },
                {
                    "value": "test_3",
                    "color": "#fff",
                    "bg_color": "#f1b300"
                }
            ]
            items, key = CaseAction.attrib_add('option', field_name, opts)

            _storage |= {'filed_config_key': items.value('item.key'),
                         'filed_key': key}  # 缓存新配置的测试用例属性key和新添加的用例属性key

        with step('选项值 test_3 后点击删除按钮'):
            opts.pop(2)  # 将test_3 数据移除
            CaseAction.attrib_update(field_name, key, opts)

        with step('进入用例库 a 的详情页，点击新建用例，查看用例类型下拉列表'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            # 获取属性的选项值
            lib_values = [option['value'] for f in res.value('data.fields') if f['name'] == field_name for option in
                          f['options']]

            assert 'test_3' not in lib_values

        with step('进入用例属性配置 - 默认配置的编辑页，查看用例类型的属性默认值下拉列表'):
            res = CaseAction.case_field_config()
            case_values = [option['value'] for f in res.value('data.fields') if f['name'] == field_name for option in
                           f['options']]

            assert 'test_3' not in case_values

    @story('135673 编辑用例属性：用例类型删除选项值（用例类型选项已被选用）')
    def test_del_selected_value(self, _storage):
        """删除已被选用的选项值"""

        with step('前置条件'):
            field_name = '示例属性值被选'
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
            items, key = CaseAction.attrib_add('option', field_name, opts)

            _storage |= {'filed_config_key': items.value('item.key'),
                         'filed_key': key}

            # 用例库下新增用例
            CaseAction.case_add(_storage['library_uuid'], field_name, 'test_1')

        with step('选项值 test_1 后点击删除按钮'):
            opts.pop(0)  # 将test_1 数据移除
            CaseAction.attrib_update(field_name, key, opts)

        with step('点击已有用例 示例用例1，查看用例类型及下拉列表'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            lib_values = [option['value'] for f in res.value('data.fields') if f['name'] == field_name for option in
                          f['options']]

            assert 'test_1' not in lib_values

        with step('进入用例属性配置 - 默认配置的编辑页，查看用例类型的属性默认值下拉列表'):
            res = CaseAction.case_field_config()
            case_values = [option['value'] for f in res.value('data.fields') if f['name'] == field_name for option in
                           f['options']]

            assert 'test_1' not in case_values

    @story('135674 编辑用例属性：用例类型添加选项值')
    def test_add_selected_value(self, _storage):
        """用例属性添加选项值"""

        with step('前置条件'):
            field_name = '示例属性值被选'
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
            items, key = CaseAction.attrib_add('option', field_name, opts)

            _storage |= {'filed_config_key': items.value('item.key'),
                         'filed_key': key}

            # 用例库下新增用例
            CaseAction.case_add(_storage['library_uuid'], field_name, 'test_1')

        with step('选项值中添加一个选项：test_3'):
            opts.append({"value": "test_3", "color": "#fff", "bg_color": "#f1b300"})  # 添加test_3
            CaseAction.attrib_update(field_name, key, opts)

        with step('点击已有用例 示例用例1，查看用例类型及下拉列表'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            lib_values = [option['value'] for f in res.value('data.fields') if f['name'] == field_name for option in
                          f['options']]

            assert 'test_3' in lib_values

        with step('进入用例属性配置 - 默认配置的编辑页，查看用例类型的属性默认值下拉列表'):
            res = CaseAction.case_field_config()
            case_values = [option['value'] for f in res.value('data.fields') if f['name'] == field_name for option in
                           f['options']]

            assert 'test_3' in case_values

    @story('135740 用例属性：编辑自定义单选菜单属性（属性名称）')
    def test_up_field_name(self, _storage):
        """变更属性名称"""

        with step('前置条件'):
            field_name = '修改示例属性名称'
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
            items, key = CaseAction.attrib_add('option', field_name, opts)

            _storage |= {'filed_config_key': items.value('item.key'),
                         'filed_key': key}

            # 用例库下新增用例
            CaseAction.case_add(_storage['library_uuid'], field_name, 'test_1')

        with step('在属性名称输入框中将名称清空，失焦'):
            up = CaseAction.attrib_update('', key, opts, code=400)

            up.check_response('errcode', 'InvalidParameter.Field.Name.Empty')

        with step('修改属性名称为：2单选菜单'):
            CaseAction.attrib_update('2单选菜单', key, opts)

        with step('进入用例库 a 的详情页，点击新建用例，查看右侧属性'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            names = [f['name'] for f in res.value('data.fields')]

            assert '2单选菜单' in names

        with step('进入用例属性配置 - 默认配置的编辑页，查看属性名称'):
            res = CaseAction.case_field_config()
            names = [f['name'] for f in res.value('data.fields')]

            assert '2单选菜单' in names

    @story('135757 用例属性：删除自定义用例属性（属性已被配置使用）')
    @story('135756 用例属性：删除自定义用例属性（属性未被配置使用）')
    def test_del_used_field_config(self, _storage):
        """删除已使用的测试用例属性配置"""
        with step('前置条件'):
            field_name = '示例单行文本属性'
            items, key = CaseAction.attrib_add('text', field_name)

            _storage |= {'filed_config_key': items.value('item.key'),
                         'filed_key': key}

        with step('点击属性后的删除按钮'):
            res = CaseAction.del_field_config(key, code=400)

            res.check_response('errcode', 'InUse.Field')

    @story('135710 用例属性配置详情页：编辑自定义属性的必填配置')
    def test_edit_field_config(self, _storage):
        with step('前置条件'):
            # 新建配置属性
            param = tc.add_filed_config()[0]
            add = self.call(prj.ItemsAdd, param)
            config_key, name = add.value('item.key'), add.value('item.name')

            # 将用例属性关联新建的配置属性中
            items, key = CaseAction.attrib_add('text', f'test编辑文本-{mocks.num()}', field_name=name)
            filed_config_key = items.value('item.key')

            _storage |= {'filed_config_key': filed_config_key,
                         'filed_key': key,
                         'config_key': config_key}

        with step('点击自定义属性的必填选项，设置为必填'):
            prm = tc.case_field_update()[0]
            prm.json = {"item": {"required": True}}
            prm.uri_args({'field_key': filed_config_key})
            up = self.call(case.CaseFieldUpdate, prm)

            up.check_response('item.required', True)

        with step('设置为非必填'):
            prm.json = {"item": {"required": False}}
            up = self.call(case.CaseFieldUpdate, prm)

            up.check_response('item.required', False)


@feature('配置中心-用例属性')
class TestCaseFieldPriority(Checker):

    @classmethod
    def update_testcase_field(cls, field_type, library_uuid, opt=None):
        """
        新增用例属性 并添加到用例属性配置中
        校验用例库中是否存在该新增属性
        用例属性配置中是否存在该属性
        删除新增数据
        :param field_type: 属性类型
        :param library_uuid: 用例库UUID
        :param opt: 选项值
        :return:
        """
        field_name = 'update-testcase-field' + mocks.num()
        new_field_name = 'new-testcase-field-test' + mocks.num()
        with step('前置条件：存在自定义xxx属性'):
            items, field_key = CaseAction.attrib_add(field_type, field_name, option=opt)
        with step('修改属性名称为'):
            if opt is not None:
                param = tc.query_global_fields()[0]
                res = go(project.ItemGraphql, param).value('data.fields')
                options = [f['options'] for f in res if f['key'] == field_key][0]
                for option in options:
                    del option['__typename']  # 删除不要的key
                CaseAction.attrib_update(new_field_name, field_key, opt=options)
            else:
                CaseAction.attrib_update(new_field_name, field_key)

        with step('进入用例库 a 的详情页，点击新建用例，查看右侧属性'):
            res = CaseAction.case_lib_field_config(library_uuid)
            names = [f['name'] for f in res.value('data.fields')]

            assert new_field_name in names
        with step('进入用例属性配置 - 默认配置的编辑页，查看属性名称'):
            res = CaseAction.case_field_config()
            names = [f['name'] for f in res.value('data.fields')]

            assert new_field_name in names

        with step('删除数据'):
            CaseAction.del_test_field(field_key=items.value('item.key'))
            CaseAction.del_test_field(field_key=field_key)

    @story('135679 用例属性 - 编辑用例属性：优先级添加选项值')
    def test_priority_add_value(self, _storage):
        with step('前置条件'):
            # 用例库中存在用例
            CaseAction.case_add(_storage['library_uuid'])

        with step('优先级属性的编辑，在选项值中添加一个选项：P5'):
            field_name = '优先级'
            priority_key = 'field-testcase-1..-priority'  # 优先级是默认属性，key是固定的，可以写死
            opts = [
                {
                    "value": "P0",
                    "color": "#fff",
                    "bg_color": "#e63422"
                },
                {
                    "value": "P1",
                    "color": "#ff6a39",
                    "bg_color": "#ffe9e2"
                },
                {
                    "value": "P2",
                    "color": "#307fe2",
                    "bg_color": "#e0ecfb"
                },
                {
                    "value": "P3",
                    "color": "#00b388",
                    "bg_color": "#d9f4ed"
                },
                {
                    "value": "P4",
                    "color": "#909090",
                    "bg_color": "#EFEFEF"
                },
                {
                    "value": "P5",
                    "color": "#fff",
                    "bg_color": "#aa8066"
                }
            ]
            res = CaseAction.attrib_update(field_name, priority_key, opts)

            assert 'P5' in [o['value'] for o in res.value('item.options')]

        with step('进入用例库 a 的详情页，点击新建用例，查看优先级下拉列表'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            values = [o['value'] for f in res.value('data.fields') if f['name'] == field_name for o in f['options']]

            assert 'P5' in values

        with step('进入用例属性配置 - 默认配置的编辑页，查看优先级的属性默认值下拉列表'):
            res = CaseAction.case_field_config()
            values = [o['value'] for f in res.value('data.fields') if f['name'] == field_name for o in f['options']]

            assert 'P5' in values

    @story('135677 编辑用例属性：优先级删除选项值（优先级选项未被选用）')
    def test_priority_del_unused_value(self, _storage):
        with step('选项值P5后点击删除按钮'):
            field_name = '优先级'
            priority_key = 'field-testcase-1..-priority'  # 优先级是默认属性，key是固定的，可以写死
            opts = [
                {
                    "value": "P0",
                    "color": "#fff",
                    "bg_color": "#e63422"
                },
                {
                    "value": "P1",
                    "color": "#ff6a39",
                    "bg_color": "#ffe9e2"
                },
                {
                    "value": "P2",
                    "color": "#307fe2",
                    "bg_color": "#e0ecfb"
                },
                {
                    "value": "P3",
                    "color": "#00b388",
                    "bg_color": "#d9f4ed"
                },
                {
                    "value": "P4",
                    "color": "#909090",
                    "bg_color": "#EFEFEF"
                }
            ]
            res = CaseAction.attrib_update(field_name, priority_key, opts)

            assert 'P5' not in [o['value'] for o in res.value('item.options')]

        with step('进入用例库 a 的详情页，点击新建用例，查看优先级下拉列表'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            values = [o['value'] for f in res.value('data.fields') if f['name'] == field_name for o in f['options']]

            assert 'P5' not in values

        with step('进入用例属性配置 - 默认配置的编辑页，查看优先级的属性默认值下拉列表'):
            res = CaseAction.case_field_config()
            values = [o['value'] for f in res.value('data.fields') if f['name'] == field_name for o in f['options']]

            assert 'P5' not in values

    @story('135678 编辑用例属性：优先级删除选项值（优先级选项已被选用）')
    def test_test_priority_del_used_value(self, _storage):
        with step('前提条件'):
            # 优先级属性新增选项P5
            field_name = '优先级'
            priority_key = 'field-testcase-1..-priority'  # 优先级是默认属性，key是固定的，可以写死
            opts = [
                {
                    "value": "P0",
                    "color": "#fff",
                    "bg_color": "#e63422"
                },
                {
                    "value": "P1",
                    "color": "#ff6a39",
                    "bg_color": "#ffe9e2"
                },
                {
                    "value": "P2",
                    "color": "#307fe2",
                    "bg_color": "#e0ecfb"
                },
                {
                    "value": "P3",
                    "color": "#00b388",
                    "bg_color": "#d9f4ed"
                },
                {
                    "value": "P4",
                    "color": "#909090",
                    "bg_color": "#EFEFEF"
                },
                {
                    "value": "P5",
                    "color": "#fff",
                    "bg_color": "#aa8066"
                }
            ]
            res = CaseAction.attrib_update(field_name, priority_key, opts)

            p5_uuid = [u['uuid'] for u in res.value('item.options') if u['value'] == 'P5'][0]

            assert 'P5' in [o['value'] for o in res.value('item.options')]

            # 用例库中新增用例用例，优先级选择P5
            CaseAction.case_add(_storage['library_uuid'], priority='P5')

        with step('选项值P5后点击删除按钮'):
            # 统计P5选项值被使用情况
            param = tc.used_count()[0]
            param.json_update('option_uuid', p5_uuid)
            res = self.call(case.UsedCount, param)
            res.check_response('used_count[1].value', 1)  # 校验P5被使用过一次

            opts.pop(5)
            res = CaseAction.attrib_update(field_name, priority_key, opts)

            assert 'P5' not in [o['value'] for o in res.value('item.options')]

        with step('进入用例属性配置 - 默认配置的编辑页，查看优先级的属性默认值下拉列表'):
            res = CaseAction.case_field_config()
            values = [o['value'] for f in res.value('data.fields') if f['name'] == field_name for o in f['options']]

            assert 'P5' not in values

    @story('T135682 TestCase 配置中心 - 用例属性 - 编辑用例属性：自定义单选菜单删除选项值（自定义单选菜单选项未被选用）')
    def test_self_defining_del_not_used_value(self, _storage):
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
                },
                {
                    "value": "test_3",
                    "color": "#fff",
                    "bg_color": "#00b388"
                }
            ]
            items, field_key = CaseAction.attrib_add('option', field_name, opts)

        with step('删除选项3'):
            param = tc.query_global_fields()[0]
            res = go(project.ItemGraphql, param).value('data.fields')
            options = [f['options'] for f in res if f['key'] == field_key][0]
            for option in options:
                del option['__typename']  # 删除不要的key
            new_option = options[0]['uuid']
            old_option = options[2]['uuid']
            options.pop()
            CaseAction.attrib_update(field_name, field_key, opt=options, new_option=new_option,
                                     old_option=old_option)
        with step('进入用例库 a 的详情页，点击新建用例，查看1单选菜单的下拉列表'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            options_values = [r['options'] for r in res.value('data.fields') if r['name'] == field_name][0]
            assert 'test_3' not in options_values
        with step('进入用例属性配置 - 默认配置的编辑页，查看1单选菜单的属性默认值下拉列表'):
            resp = CaseAction.case_field_config()
            options_values = [r['options'] for r in resp.value('data.fields') if r['name'] == field_name][0]
            assert 'test_3' not in options_values
        with step('删除数据'):
            CaseAction.del_test_field(field_key=items.value('item.key'))
            CaseAction.del_test_field(field_key=field_key)

    @story('T135687 TestCase 配置中心 - 用例属性 - 编辑用例属性：自定义多选菜单删除选项值（自定义多选菜单选项未被选用）')
    def test_multi_option_del_not_used_value(self, _storage):
        with step('前置条件：存在一个自定义属性多选菜单'):
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
                },
                {
                    "value": "test_3",
                    "color": "#fff",
                    "bg_color": "#00b388"
                }
            ]
            items, field_key = CaseAction.attrib_add('multi_option', field_name, opts)

        with step('删除选项3'):
            param = tc.query_global_fields()[0]
            res = go(project.ItemGraphql, param).value('data.fields')
            options = [f['options'] for f in res if f['key'] == field_key][0]
            for option in options:
                del option['__typename']  # 删除不要的key
            new_option = options[0]['uuid']
            old_option = options[2]['uuid']
            options.pop()
            CaseAction.attrib_update(field_name, field_key, opt=options, new_option=new_option,
                                     old_option=old_option)
        with step('进入用例库 a 的详情页，点击新建用例，查看1单选菜单的下拉列表'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            options_values = [r['options'] for r in res.value('data.fields') if r['name'] == field_name][0]
            assert 'test_3' not in options_values
        with step('进入用例属性配置 - 默认配置的编辑页，查看1单选菜单的属性默认值下拉列表'):
            resp = CaseAction.case_field_config()
            options_values = [r['options'] for r in resp.value('data.fields') if r['name'] == field_name][0]
            assert 'test_3' not in options_values
        with step('删除数据'):
            CaseAction.del_test_field(field_key=items.value('item.key'))
            CaseAction.del_test_field(field_key=field_key)

    @story('T135683 TestCase 配置中心 - 用例属性 - 编辑用例属性：自定义单选菜单删除选项值（自定义单选菜单选项已被选用）')
    def test_self_defining_del_used_value(self, _storage):
        with step('前置条件：存在一个自定义属性1'):
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
            # 设置默认值
            uuid = [f['uuid'] for f in items.value('item.options') if f['value'] == 'test_2'][0]
            CaseAction.update_config_default_values(field_key=items.value('item.key'), default_value_uuid=uuid)
        with step('删除选项2'):
            param = tc.query_global_fields()[0]
            res = go(project.ItemGraphql, param).value('data.fields')
            options = [f['options'] for f in res if f['key'] == field_key][0]
            for option in options:
                del option['__typename']  # 删除不要的key
            options.pop()
            CaseAction.attrib_update(field_name, field_key, opt=options, new_option=options[0]['uuid'],
                                     old_option=uuid)
        with step('进入用例库 a 的详情页，点击新建用例，查看1单选菜单的下拉列表'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            options_values = [r['options'] for r in res.value('data.fields') if r['name'] == field_name][0]
            default_value = [r['defaultValue'] for r in res.value('data.fields') if r['name'] == field_name][0]
            assert 'test_2' not in options_values
            # 默认值变为test_1
            assert default_value == options[0]['uuid']
        with step('进入用例属性配置 - 默认配置的编辑页，查看1单选菜单的属性默认值下拉列表'):
            resp = CaseAction.case_field_config()
            options_values = [r['options'] for r in resp.value('data.fields') if r['name'] == field_name][0]
            default_value = [r['defaultValue'] for r in resp.value('data.fields') if r['name'] == field_name][0]
            assert default_value == options[0]['uuid']
            assert 'test_2' not in options_values
        with step('删除数据'):
            CaseAction.del_test_field(field_key=items.value('item.key'))
            CaseAction.del_test_field(field_key=field_key)

    @story('T135688 TestCase 配置中心 - 用例属性 - 编辑用例属性：自定义多选菜单删除选项值（自定义多选菜单选项已被选用）')
    def test_multi_option_del_used_value(self, _storage):
        with step('前置条件：存在一个自定义多选菜单属性'):
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
            items, field_key = CaseAction.attrib_add('multi_option', field_name, opts)
            # 设置默认值
            uuid = [f['uuid'] for f in items.value('item.options') if f['value'] == 'test_2'][0]
            CaseAction.update_config_default_values(field_key=items.value('item.key'), default_value_uuid=[uuid])
        with step('删除选项2'):
            param = tc.query_global_fields()[0]
            res = go(project.ItemGraphql, param).value('data.fields')
            options = [f['options'] for f in res if f['key'] == field_key][0]
            for option in options:
                del option['__typename']  # 删除不要的key
            options.pop()
            CaseAction.attrib_update(field_name, field_key, opt=options, new_option=options[0]['uuid'],
                                     old_option=uuid)
        with step('进入用例库 a 的详情页，点击新建用例，查看1单选菜单的下拉列表'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            options_values = [r['options'] for r in res.value('data.fields') if r['name'] == field_name][0]
            default_value = [r['defaultValue'] for r in res.value('data.fields') if r['name'] == field_name][0]
            assert 'test_2' not in options_values
            # 默认值变为test_1
            assert default_value[0] == options[0]['uuid']
        with step('进入用例属性配置 - 默认配置的编辑页，查看1单选菜单的属性默认值下拉列表'):
            resp = CaseAction.case_field_config()
            options_values = [r['options'] for r in resp.value('data.fields') if r['name'] == field_name][0]
            default_value = [r['defaultValue'] for r in resp.value('data.fields') if r['name'] == field_name][0]
            assert default_value[0] == options[0]['uuid']
            assert 'test_2' not in options_values
        with step('删除数据'):
            CaseAction.del_test_field(field_key=items.value('item.key'))
            CaseAction.del_test_field(field_key=field_key)

    @story('T135684 TestCase 配置中心 - 用例属性 - 编辑用例属性：自定义单选菜单添加选项值')
    def test_add_case_field_value_opt(self, _storage):
        with step('前置条件：存在一个自定义属性1'):
            field_name = '自定义属性-' + mocks.num()
            opts = [
                {
                    "value": "test_1",
                    "color": "#fff",
                    "bg_color": "#307fe2"
                }
            ]
            items, field_key = CaseAction.attrib_add('option', field_name, opts)
        with step('打开1单选菜单属性的编辑弹窗，在选项值中添加一个选项：选项2'):
            opt = {"value": "test_2", "color": "#fff", "bg_color": "#307fe2"}
            param = tc.query_global_fields()[0]
            res = go(project.ItemGraphql, param).value('data.fields')
            options = [f['options'] for f in res if f['key'] == field_key][0]
            for option in options:
                del option['__typename']  # 删除不要的key
            options.append(opt)
            CaseAction.attrib_update(field_name, field_key, options)
        with step('进入用例库 a 的详情页，点击新建用例，查看1单选菜单的下拉列表'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            options_values = [r['options'] for r in res.value('data.fields') if r['name'] == field_name][0]
            values = [r['value'] for r in options_values]
            assert 'test_2' in values
        with step('进入用例属性配置 - 默认配置的编辑页，查看1单选菜单的属性默认值下拉列表'):
            resp = CaseAction.case_field_config()
            options_values = [r['options'] for r in resp.value('data.fields') if r['name'] == field_name][0]
            values = [r['value'] for r in options_values]
            assert 'test_2' in values
        with step('删除数据'):
            CaseAction.del_test_field(field_key=items.value('item.key'))
            CaseAction.del_test_field(field_key=field_key)

    @story('T135689 TestCase 配置中心 - 用例属性 - 编辑用例属性：自定义多选菜单添加选项值')
    def test_add_case_field_value_multi_option(self, _storage):
        with step('前置条件：存在一个自定义多选属性'):
            field_name = '自定义属性-' + mocks.num()
            opts = [
                {
                    "value": "test_1",
                    "color": "#fff",
                    "bg_color": "#307fe2"
                }
            ]
            items, field_key = CaseAction.attrib_add('multi_option', field_name, opts)
        with step('打开1单选菜单属性的编辑弹窗，在选项值中添加一个选项：选项2'):
            opt = {"value": "test_2", "color": "#fff", "bg_color": "#307fe2"}
            param = tc.query_global_fields()[0]
            res = go(project.ItemGraphql, param).value('data.fields')
            options = [f['options'] for f in res if f['key'] == field_key][0]
            for option in options:
                del option['__typename']  # 删除不要的key
            options.append(opt)
            CaseAction.attrib_update(field_name, field_key, options)
        with step('进入用例库 a 的详情页，点击新建用例，查看1单选菜单的下拉列表'):
            res = CaseAction.case_lib_field_config(_storage['library_uuid'])
            options_values = [r['options'] for r in res.value('data.fields') if r['name'] == field_name][0]
            values = [r['value'] for r in options_values]
            assert 'test_2' in values
        with step('进入用例属性配置 - 默认配置的编辑页，查看1单选菜单的属性默认值下拉列表'):
            resp = CaseAction.case_field_config()
            options_values = [r['options'] for r in resp.value('data.fields') if r['name'] == field_name][0]
            values = [r['value'] for r in options_values]
            assert 'test_2' in values
        with step('删除数据'):
            CaseAction.del_test_field(field_key=items.value('item.key'))
            CaseAction.del_test_field(field_key=field_key)

    @story('T135759 TestCase 配置中心 - 用例属性：新建单选菜单属性')
    def test_add_radio_menu_filed(self):
        with step('新建单选菜单属性'):
            options = [{"value": "11", "color": "#fff", "bg_color": "#307fe2"}]
            field_key = CaseAction.add_case_field(field_type='option', options=options)
        with step('查看任意用例属性配置详情页的添加用例属性弹窗'):
            CaseAction.query_case_global_field(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135758 TestCase 配置中心 - 用例属性：新建单行文本属性')
    def test_add_case_filed_text(self):
        with step('新建单行文本属性'):
            field_key = CaseAction.add_case_field(field_type='text')
        with step('查看任意用例属性配置详情页的添加用例属性弹窗'):
            CaseAction.query_case_global_field(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135760 TestCase 配置中心 - 用例属性：新建单选成员属性')
    def test_add_case_filed_single_member(self):
        with step('新建单选成员属性'):
            field_key = CaseAction.add_case_field(field_type='user')
        with step('查看任意用例属性配置详情页的添加用例属性弹窗'):
            CaseAction.query_case_global_field(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135761 TestCase 配置中心 - 用例属性：新建多行文本属性')
    def test_add_case_filed_multi_line_text(self):
        with step('新建多行文本属性'):
            field_key = CaseAction.add_case_field(field_type='multi_line_text')
        with step('查看任意用例属性配置详情页的添加用例属性弹窗'):
            CaseAction.query_case_global_field(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135762 TestCase 配置中心 - 用例属性：新建多选菜单属性')
    def test_add_case_field_multi_choice_menu(self):
        options = [
            {
                "value": "111",
                "color": "#fff",
                "bg_color": "#307fe2"
            }
        ]
        with step('新建多选菜单属性'):
            field_key = CaseAction.add_case_field(field_type='multi_option', options=options)
        with step('查看任意用例属性配置详情页的添加用例属性弹窗'):
            CaseAction.query_case_global_field(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135763 TestCase 配置中心 - 用例属性：新建多选成员属性')
    def test_add_case_filed_user_list(self):
        with step('新建多选成员属性'):
            field_key = CaseAction.add_case_field(field_type='user_list')
        with step('查看任意用例属性配置详情页的添加用例属性弹窗'):
            CaseAction.query_case_global_field(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135764 TestCase 配置中心 - 用例属性：新建浮点数属性')
    def test_add_case_filed_float(self):
        with step('新建浮点数属性'):
            field_key = CaseAction.add_case_field(field_type='float')
        with step('查看任意用例属性配置详情页的添加用例属性弹窗'):
            CaseAction.query_case_global_field(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135765 TestCase 配置中心 - 用例属性：新建日期属性')
    def test_add_case_filed_date(self):
        with step('新建日期属性'):
            field_key = CaseAction.add_case_field(field_type='date')
        with step('查看任意用例属性配置详情页的添加用例属性弹窗'):
            CaseAction.query_case_global_field(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135766 TestCase 配置中心 - 用例属性：新建时间属性')
    def test_add_case_filed_time(self):
        with step('新建时间属性'):
            field_key = CaseAction.add_case_field(field_type='time')
        with step('查看任意用例属性配置详情页的添加用例属性弹窗'):
            CaseAction.query_case_global_field(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135767 TestCase 配置中心 - 用例属性：新建整数属性')
    def test_add_case_filed_integer(self):
        with step('新建整数属性'):
            field_key = CaseAction.add_case_field(field_type='integer')
        with step('查看任意用例属性配置详情页的添加用例属性弹窗'):
            CaseAction.query_case_global_field(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135755 TestCase 配置中心 - 用例属性：列表检查')
    @story('T135749 TestCase 配置中心 - 用例属性：检查列表默认属性表现')
    def test_check_case_list(self):
        default_names = {'所属用例库', '创建时间', '前置条件', '用例名称', '用例ID', '优先级', '用例维护人', '所属模块', '备注', '用例类型'}
        param = tc.query_global_fields()[0]
        res = self.call(project.ItemGraphql, param).value('data.fields')
        names = [r['name'] for r in res]
        assert set(names) >= default_names

    @story('T135739 TestCase 配置中心 - 用例属性：编辑自定义单行文本属性')
    def test_update_case_field_text(self, _storage):
        self.update_testcase_field('text', _storage['library_uuid'])

    @story('T135741 TestCase 配置中心 - 用例属性：编辑自定义单选成员属性')
    def test_update_case_field_user(self, _storage):
        self.update_testcase_field('user', _storage['library_uuid'])

    @story('T135742 TestCase 配置中心 - 用例属性：编辑自定义多行文本属性')
    def test_update_case_field_multi_line_text(self, _storage):
        self.update_testcase_field('multi_line_text', _storage['library_uuid'])

    @story('T135743 TestCase 配置中心 - 用例属性：编辑自定义多选菜单属性（属性名称）')
    def test_update_case_field_multi_option(self, _storage):
        options = [{"value": "111", "color": "#fff", "bg_color": "#307fe2"}]
        self.update_testcase_field('multi_option', _storage['library_uuid'], opt=options)

    @story('T135744 TestCase 配置中心 - 用例属性：编辑自定义多选成员属性')
    def test_update_case_field_user_list(self, _storage):
        self.update_testcase_field('user_list', _storage['library_uuid'])

    @story('T135745 TestCase 配置中心 - 用例属性：编辑自定义浮点数属性')
    def test_update_case_field_float(self, _storage):
        self.update_testcase_field('float', _storage['library_uuid'])

    @story('T135746 TestCase 配置中心 - 用例属性：编辑自定义日期属性')
    def test_update_case_field_date(self, _storage):
        self.update_testcase_field('date', _storage['library_uuid'])

    @story('T135747 TestCase 配置中心 - 用例属性：编辑自定义时间属性')
    def test_update_case_field_time(self, _storage):
        self.update_testcase_field('time', _storage['library_uuid'])

    @story('T135748 TestCase 配置中心 - 用例属性：编辑自定义整数属性')
    def test_update_case_field_integer(self, _storage):
        self.update_testcase_field('integer', _storage['library_uuid'])

    @story('T135665 TestCase 配置中心 - 用例属性 - 编辑用例属性：检查优先级的默认选项值')
    def test_check_testcase_field_priority(self, _storage):
        default_values = {'P0', 'P1', 'P2', 'P3', 'P4'}
        with step('查看优先级的默认选项值'):
            param = testcase.query_global_fields()[0]
            res = go(project.ItemGraphql, param).value('data.fields')
            options = [r['options'] for r in res if r['name'] == '优先级'][0]
            values = [r['value'] for r in options]
            assert set(values) >= default_values
        with step('进入用例库 a 的详情页，点击新建用例，查看优先级下拉列表'):
            resp = CaseAction.case_lib_field_config(_storage['library_uuid']).value('data.fields')
            options = [r['options'] for r in resp if r['name'] == '优先级'][0]
            values = [r['value'] for r in options]
            assert set(values) >= default_values
        with step('进入用例属性配置 - 默认配置的编辑页，查看优先级的属性默认值下拉列表'):
            response = CaseAction.case_field_config().value('data.fields')
            options = [r['options'] for r in response if r['name'] == '优先级'][0]
            values = [r['value'] for r in options]
            assert set(values) >= default_values

    @story('T135664 TestCase 配置中心 - 用例属性 - 编辑用例属性：检查用例类型的默认选项值')
    def test_check_testcase_field_case_type(self, _storage):
        default_values = {'功能测试', '性能测试', '接口测试', '安装部署', '配置相关', '安全相关', '其他'}
        with step('查看用例类型的默认选项值'):
            param = testcase.query_global_fields()[0]
            res = go(project.ItemGraphql, param).value('data.fields')
            options = [r['options'] for r in res if r['name'] == '用例类型'][0]
            values = [r['value'] for r in options]
            assert set(values) >= default_values
        with step('进入用例库 a 的详情页，点击新建用例，查看用例类型下拉列表'):
            resp = CaseAction.case_lib_field_config(_storage['library_uuid']).value('data.fields')
            options = [r['options'] for r in resp if r['name'] == '用例类型'][0]
            values = [r['value'] for r in options]
            assert set(values) >= default_values
        with step('进入用例属性配置 - 默认配置的编辑页，查看用例类型的属性默认值下拉列表'):
            response = CaseAction.case_field_config().value('data.fields')
            options = [r['options'] for r in response if r['name'] == '用例类型'][0]
            values = [r['value'] for r in options]
            assert set(values) >= default_values


@feature('配置中心')
class TestCaseFiled(Checker):

    @story('T149510 配置中心-项目管理-工作项状态：检查工作项状态的系统默认值（开箱）')
    @parametrize('param', p.issue_task_status())
    def test_check_default_issue_status(self, param):
        """"""
        # 获取 task_status 数据， 检查结果即可
        resp = self.call(prj.TeamStampData, param)

        status = resp.value('task_status.task_statuses')
        actual_status = {s['name']: s['category'] for s in status}

        expect_status = {
            '未开始': '未开始',
            '实现中': '进行中',
            '已实现': '已完成',
            '关闭': '已完成',
            '回归不通过': '进行中',
            '回归通过': '已完成',
            '进行中': '进行中',
            '已完成': '已完成',
            '待处理': '未开始',
            '修复中': '进行中',
            '已修复': '进行中',
            '已验证': '已完成',
            '已拒绝': '已完成',
            '重新打开': '未开始'
        }

        s_mapper = {
            '未开始': 'to_do',
            '进行中': 'in_progress',
            '已完成': 'done',
        }

        for k, v in expect_status.items():
            assert k in actual_status, f'{k} 未找到！'
            assert s_mapper.get(v) == actual_status[k], f'{k} 的状态错误！'
