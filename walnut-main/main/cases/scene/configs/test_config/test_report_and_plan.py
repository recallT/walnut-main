from falcons.check import Checker, go
from falcons.com.nick import feature, story, fixture, step, parametrize
from falcons.helper import mocks

from main.actions.case import CaseAction
from main.api import case
from main.api import project as prj
from main.params import testcase as tc


@fixture(scope='module')
def _storage():
    return {}


@fixture(scope='module')
def plan_del(_storage):
    yield
    # 清除数据
    prm = tc.up_plan_status()
    prm.uri_args({'plan_uuid': _storage['plan_uuid']})
    go(case.DeletePlan, prm)


@feature('配置中心-测试报告和计划')
class TestReportAndPlan(Checker):

    def plan_add(self, storage):
        res = CaseAction.test_phase()
        stage_uuid = [r['uuid'] for r in res]

        # 新增测试计划
        p = tc.add_case_plan()
        p.json_update('plan.plan_stage', stage_uuid[-1])  # 选择测试阶段test1
        add = go(case.AddCasePlan, p)

        storage |= {'plan_uuid': add.json()['plan']['uuid']}

    @story('128911 管理报告模版-新建模版')
    @parametrize('param', tc.plan_report_temple())
    def test_template_add(self, param):
        add = self.call(case.PlanReportTemplateAdd, param)
        add.check_response('type', 'OK')

    @story('128912 报告模版信息')
    @parametrize('param', tc.plan_report_temple())
    def test_template_info(self, param, _storage):
        info = self.call(case.ReportTemplateInfo, param, with_json=False)

        _storage |= {'temple_uuid': info.value('templates[0].uuid')}

    @story('128910 管理报告模版-编辑模版')
    @parametrize('param', tc.plan_report_temple())
    def test_template_update(self, param, _storage):
        data = '{\"components\":[\"1\",\"2\",\"3\",\"4\"],\"contentMap\":' \
               '{\"richTextComponentTitleSet\":{},\"richTextComponentContentSet\":{}}}'
        param.json_update('content', data)
        param.uri_args({'template_uuid': _storage['temple_uuid']})

        up = self.call(case.ReportTemplateUpdate, param)
        up.check_response('type', 'OK')

    @story('128913 删除报告模版')
    @parametrize('param', tc.plan_report_temple())
    def test_template_delete(self, param, _storage):
        param.uri_args({'template_uuid': _storage['temple_uuid']})

        up = self.call(case.ReportTemplateDelete, param, with_json=False)
        up.check_response('type', 'OK')

    @story('135654 测试计划属性：新建单选菜单属性')
    def test_plan_add_single_choice(self, _storage):
        param = tc.add_plan_field()
        param.json['variables'] |= {
            "field_type": "option",
            "name": "单选计划属性",
            "context": {
                "type": "team"
            },
            "options": [
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
            ],
            "pool": "testcase_plan"
        }

        add = self.call(prj.ItemGraphql, param)

        _storage |= {'field_key': add.json()['data']['addField']['key']}

    @story('135644 测试计划属性：编辑自定义属性')
    @parametrize('param', tc.update_plan_field())
    def test_plan_up_field(self, param, _storage):
        param.json_update('variables.key', _storage['field_key'])

        with step('在属性名称输入框中将 1自定义属性 清空'):
            name = ''
            param.json_update('variables.name', name)
            res = self.call(prj.ItemGraphql, param, status_code=400)
            res.check_response('errcode', 'InvalidParameter.Field.Name.Empty')

        with step('修改属性名称'):
            field_name = '更新自定义属性test'
            param.json_update('variables.name', field_name)
            self.call(prj.ItemGraphql, param)

        with step('进入测试计划 a 的测试计划设置 - 测试计划信息页查看属性名称'):
            prm = tc.query_plan_field()
            res = self.call(prj.ItemGraphql, prm)

            names = [f['name'] for f in res.value('data.fields')]
            assert field_name in names

    @story('135621 测试计划属性 - 编辑测试计划属性：测试阶段删除选项值')
    @parametrize('param', tc.update_plan_field())
    def test_delete_selected_value(self, param, _storage):
        """删除已被选的选项值"""

        with step('前置条件'):
            # 测试阶段的默认选项值包含: test1
            prm = tc.plan_filter_query()[0]
            res = self.call(prj.ItemGraphql, prm)

            test_key = [f['key'] for f in res.value('data.fields') if f['name'] == '测试阶段'][0]
            options = [f['options'] for f in res.value('data.fields') if f['name'] == '测试阶段'][0]
            for option in options:
                del option['__typename']  # 删除不要的key
            options.append({"value": "test1", "color": "#307fe2", "bg_color": "#e0ecfb"})  # 增加test1选项

            param.json_update('variables.key', test_key)
            param.json_update('variables.name', '测试阶段')
            param.json_update('variables.options', options)
            self.call(prj.ItemGraphql, param)

            # 已存在测试计划 a，且 a 的测试阶段 选择了 test1
            self.plan_add(_storage)

        with step('选项值 test1 后点击删除按钮'):
            del options[-1]
            param.json_update('variables.options', options)
            self.call(prj.ItemGraphql, param)

        with step('点击新建测试计划，查看测试阶段下拉列表'):
            res = CaseAction.test_phase()
            values = [r['value'] for r in res]

            assert 'test1' not in values

    @story('135623 测试计划属性 - 编辑测试计划属性：测试阶段添加选项值')
    @parametrize('param', tc.update_plan_field())
    def test_add_option_value(self, param, _storage):
        """添加选项值"""

        with step('在 测试阶段 选项值中添加一个选项：test1'):
            prm = tc.plan_filter_query()[0]
            res = self.call(prj.ItemGraphql, prm)

            test_key = [f['key'] for f in res.value('data.fields') if f['name'] == '测试阶段'][0]
            options = [f['options'] for f in res.value('data.fields') if f['name'] == '测试阶段'][0]
            for option in options:
                del option['__typename']  # 删除不要的key
            options.append({"value": "test1", "color": "#307fe2", "bg_color": "#e0ecfb"})  # 增加test1选项

            param.json_update('variables.key', test_key)
            param.json_update('variables.name', '测试阶段')
            param.json_update('variables.options', options)
            self.call(prj.ItemGraphql, param)

        with step('点击新建测试计划，查看测试阶段下拉列表'):
            res = CaseAction.test_phase()
            values = [r['value'] for r in res]

            assert 'test1' in values

        with step('清除添加的选项'):
            del options[-1]
            param.json_update('variables.options', options)
            self.call(prj.ItemGraphql, param)

    @story('135652 测试计划属性：删除自定义测试计划属性')
    @parametrize('param', tc.update_plan_field())
    def test_plan_delete_field(self, param, _storage):
        with step('点击 删除 按钮'):
            param.uri_args({'field_key': _storage['field_key']})
            self.call(case.FieldDelete, param)

    @story('T135653 TestCase 配置中心 - 测试计划属性：新建单行文本属性')
    def test_add_test_plan_field_single_text(self):
        with step('新建单行文本属性'):
            field_key = CaseAction.add_testplan_field(field_type='text')
        with step('进入测试计划 a 的测试计划设置 - 测试计划信息页查看属性'):
            CaseAction.testplan_set_info(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135655 TestCase 配置中心 - 测试计划属性：新建单选成员属性')
    def test_add_test_plan_field_single_member(self):
        with step('新建单选成员属性'):
            field_key = CaseAction.add_testplan_field(field_type='user')
        with step('进入测试计划 a 的测试计划设置 - 测试计划信息页查看属性'):
            CaseAction.testplan_set_info(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135656 TestCase 配置中心 - 测试计划属性：新建多行文本属性')
    def test_add_test_plan_field_more_text(self):
        with step('新建多行文本属性'):
            field_key = CaseAction.add_testplan_field(field_type='multi_line_text')
        with step('进入测试计划 a 的测试计划设置 - 测试计划信息页查看属性'):
            CaseAction.testplan_set_info(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135657 TestCase 配置中心 - 测试计划属性：新建多选菜单属性')
    def test_add_test_plan_field_multi_choice_menu(self):
        with step('新建多选菜单属性'):
            options = [
                {
                    "value": "111",
                    "color": "#fff",
                    "bg_color": "#307fe2"
                }
            ]
            field_key = CaseAction.add_testplan_field(field_type='multi_option', options=options)
        with step('进入测试计划 a 的测试计划设置 - 测试计划信息页查看属性'):
            CaseAction.testplan_set_info(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135658 TestCase 配置中心 - 测试计划属性：新建多选成员属性')
    def test_add_test_plan_field_more_member(self):
        with step('新建多选成员属性'):
            field_key = CaseAction.add_testplan_field(field_type='user_list')
        with step('进入测试计划 a 的测试计划设置 - 测试计划信息页查看属性'):
            CaseAction.testplan_set_info(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135659 TestCase 配置中心 - 测试计划属性：新建浮点数属性')
    def test_add_test_plan_field_float(self):
        with step('新建浮点数属性'):
            field_key = CaseAction.add_testplan_field(field_type='float')
        with step('进入测试计划 a 的测试计划设置 - 测试计划信息页查看属性'):
            CaseAction.testplan_set_info(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135660 TestCase 配置中心 - 测试计划属性：新建日期属性')
    def test_add_test_plan_field_date(self):
        with step('新建日期属性'):
            field_key = CaseAction.add_testplan_field(field_type='date')
        with step('进入测试计划 a 的测试计划设置 - 测试计划信息页查看属性'):
            CaseAction.testplan_set_info(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135661 TestCase 配置中心 - 测试计划属性：新建时间属性')
    def test_add_test_plan_field_time(self):
        with step('新建时间属性'):
            field_key = CaseAction.add_testplan_field(field_type='time')
        with step('进入测试计划 a 的测试计划设置 - 测试计划信息页查看属性'):
            CaseAction.testplan_set_info(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135662 TestCase 配置中心 - 测试计划属性：新建整数属性')
    def test_add_test_plan_field_integer(self):
        with step('新建时间属性'):
            field_key = CaseAction.add_testplan_field(field_type='integer')
        with step('进入测试计划 a 的测试计划设置 - 测试计划信息页查看属性'):
            CaseAction.testplan_set_info(field_key)
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135651 TestCase 配置中心 - 测试计划属性：列表检查')
    @story('T135645 TestCase 配置中心 - 测试计划属性：检查列表默认属性表现')
    def test_test_plan_list(self):
        default_value = {'测试计划名称', '测试计划状态', '测试计划负责人', '测试阶段', '关联项目', '关联迭代'}
        prm = tc.plan_filter_query()[0]
        res = self.call(prj.ItemGraphql, prm)
        values = [r['name'] for r in res.value('data.fields')]
        assert set(values) >= default_value

    @story('T135624 TestCase 配置中心 - 测试计划属性 - 编辑测试计划属性：检查测试阶段的默认选项值')
    def test_testplan_plan_stage(self):
        default_value = {'冒烟测试', '单元测试', '功能测试', '集成测试', '系统测试', '版本验证'}
        param = tc.query_case_phase()[0]
        res = go(prj.ItemGraphql, param)
        values = [r['value'] for r in res.value('data.fields[0].options')]
        assert set(values) >= default_value

    @story('T135628 TestCase 配置中心 - 测试计划属性 - 编辑测试计划属性：自定义单选菜单删除选项值')
    def test_update_test_plan_del_field_single_menu_option(self):
        with step('前置条件:已添加自定义单选菜单测试计划属性：1单选菜单'):
            options = [
                {
                    "value": "1",
                    "color": "#fff",
                    "bg_color": "#307fe2"
                },
                {
                    "value": "2",
                    "color": "#fff",
                    "bg_color": "#00b388"
                },
                {
                    "value": "3",
                    "color": "#fff",
                    "bg_color": "#f1b300"
                }
            ]
            field_key = CaseAction.add_testplan_field(field_type='option', options=options)
        # 查询属性信息
        with step('删除选项3'):
            prm = tc.query_plan_field()
            res = go(prj.ItemGraphql, prm)
            options = [f['options'] for f in res.value('data.fields') if f['key'] == field_key][0]
            for option in options:
                del option['__typename']  # 删除不要的key
            param = tc.update_plan_field()[0]
            param.json_update('variables.new_option', options[0]['uuid'])
            param.json_update('variables.old_option', options[2]['uuid'])
            # 删除值为3的选项
            options.pop()
            param.json_update('variables.key', field_key)
            param.json_update('variables.name', 'test-plan-field' + mocks.num())
            param.json_update('variables.options', options)
            self.call(prj.ItemGraphql, param)
        with step("进入测试计划 a 的测试计划设置 - 测试计划信息页查看 1单选菜单 属性值及下拉列表"):
            prm = tc.query_plan_field()
            res = go(prj.ItemGraphql, prm)
            new_options = [f['options'] for f in res.value('data.fields') if f['key'] == field_key][0]
            values = [r['value'] for r in new_options]
            # 选项3不在列表中
            assert '3' not in values
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)

    @story('T135630 TestCase 配置中心 - 测试计划属性 - 编辑测试计划属性：自定义单选菜单添加选项值')
    def test_update_test_plan_add_field_single_menu_option(self):
        with step('前置条件:已添加自定义单选菜单测试计划属性：1单选菜单'):
            options = [
                {
                    "value": "1",
                    "color": "#fff",
                    "bg_color": "#307fe2"
                }
            ]
            field_key = CaseAction.add_testplan_field(field_type='option', options=options)
        with step('新增选项值为2'):
            prm = tc.query_plan_field()
            res = go(prj.ItemGraphql, prm)
            options = [f['options'] for f in res.value('data.fields') if f['key'] == field_key][0]
            for option in options:
                del option['__typename']  # 删除不要的key
            options.append({"value": "2", "color": "#fff", "bg_color": "#307fe2"})
            param = tc.update_plan_field()[0]
            param.json_update('variables.key', field_key)
            param.json_update('variables.name', 'test-plan-field' + mocks.num())
            param.json_update('variables.options', options)
            self.call(prj.ItemGraphql, param)
        with step("进入测试计划 a 的测试计划设置 - 测试计划信息页查看 1单选菜单 属性值及下拉列表"):
            prm = tc.query_plan_field()
            res = go(prj.ItemGraphql, prm)
            new_options = [f['options'] for f in res.value('data.fields') if f['key'] == field_key][0]
            values = [r['value'] for r in new_options]
            assert '2' in values
        with step('删除数据'):
            CaseAction.del_test_field(field_key=field_key)
