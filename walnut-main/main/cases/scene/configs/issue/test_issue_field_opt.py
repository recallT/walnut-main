"""
@Desc：全局配置-工作项属性编辑
"""
import time

from falcons.check import Checker, go
from falcons.com.nick import feature, story, fixture, step, parametrize
from falcons.helper import mocks
from falcons.ops import generate_param

from main.actions.pro import PrjAction
from main.actions.task import TaskAction, team_stamp, global_issue_type
from main.api import project as prj, issue as i, project
from main.params import data, conf, issue, com
from main.params.const import ACCOUNT
from main.actions.issue import IssueAction as Ia


@fixture(scope='module')
def uuid_storage():
    """缓存属性uuid"""

    return []


@fixture(scope='module', autouse=True)
def clear_field(uuid_storage):
    yield
    issue_uuid = TaskAction.issue_type_uuid()[0]
    param = data.field_delete()[0]

    if uuid_storage:
        for f in uuid_storage:
            param.uri_args({'field_uuid': f})
            param.uri_args({'issue_uuid': issue_uuid})

            # 删除项目工作项属性
            try:
                go(prj.ProjectIssueFieldDelete, param)
            except AssertionError:
                pass

            # 删除全局工作项属性
            time.sleep(1)
            try:
                go(prj.FieldDelete, param)
            except AssertionError:
                time.sleep(1)
                go(prj.FieldDelete, param)


def field_param(field_type: int, u_storage, **kwargs):
    """属性类型参数"""

    param = conf.add_issue_type_field()[0]
    param.json_update('field.type', field_type)
    if kwargs:
        for key, value in kwargs.items():
            param.json['field'] |= {key: value}

    res = go(prj.FieldsAdd, param)
    res.check_response('field.built_in', False)

    u_storage.append(res.value('field.uuid'))

    return res.value('field.uuid'), param


@feature('全局配置-工作项属性更新')
class TestIssueFieldUpdate(Checker):

    @story('131432 编辑出现时间时间点')
    def test_appear_time_field_up(self, uuid_storage):
        with step('前置条件'):
            # 存在出现时间类型的自定义工作项属性
            field_uuid, param = field_param(45, uuid_storage, appear_time_settings={
                "field_uuid": "field005",
                "method": "first_at",
                "field_option_uuid": "6tj7uFts"
            })

            # 项目A存在工作项使用了工作项属性
            prm = {"field_uuid": field_uuid, "required": False}
            TaskAction.task_add_field(prm)

        with step('修改时间点为：最后出现时间点'):
            param.json_update('field.appear_time_settings.method', 'last_at')
            param.uri_args({'field_uuid': field_uuid})
            self.call(prj.FieldUpdate, param)

        with step('进入项目A查看「工作项1」工作项属性A的值'):
            stamp = team_stamp({'field': 0})
            method = [f['appear_time_settings']['method'] for f in stamp['field']['fields'] if f['uuid'] == field_uuid]

            assert 'last_at' in method

    @story('131439 编辑单选菜单选项值排序')
    def test_single_choice_option_value_sort(self, uuid_storage):
        with step('前置条件'):
            # 存在单选菜单类型的自定义工作项属性
            field_uuid, param = field_param(1, uuid_storage, options=[
                {
                    "value": "test_1",
                    "background_color": "#307fe2",
                    "color": "#fff"
                },
                {
                    "value": "test_2",
                    "background_color": "#00b388",
                    "color": "#fff"
                }
            ])

            # 项目A存在工作项使用了工作项属性
            prm = {"field_uuid": field_uuid, "required": False}
            TaskAction.task_add_field(prm)

        with step('拖拽选项「1」至选项「2」后'):
            param.json_update('field.options', [{
                "value": "test_2",
                "background_color": "#00b388",
                "color": "#fff"
            }, {
                "value": "test_1",
                "background_color": "#307fe2",
                "color": "#fff"
            }])
            param.uri_args({'field_uuid': field_uuid})
            self.call(prj.FieldUpdate, param)

        with step('进入项目A查看「工作项1」工作项详情中属性A的选项值排序'):
            stamp = team_stamp({'field': 0})
            value = [v['value'] for f in stamp['field']['fields'] if f['uuid'] == field_uuid for v in f['options']][0]

            assert value == 'test_2'

    @story('131442 编辑多选菜单选项值排序')
    def test_multi_choice_option_value_sort(self, uuid_storage):
        with step('前置条件'):
            # 存在单选菜单类型的自定义工作项属性
            field_uuid, param = field_param(16, uuid_storage, options=[
                {
                    "value": "test_1",
                    "background_color": "#307fe2",
                    "color": "#fff"
                },
                {
                    "value": "test_2",
                    "background_color": "#00b388",
                    "color": "#fff"
                },
                {
                    "value": "test_3",
                    "background_color": "#f1b300",
                    "color": "#fff"
                }
            ])

            # 项目A存在工作项使用了工作项属性
            prm = {"field_uuid": field_uuid, "required": False}
            TaskAction.task_add_field(prm)

        with step('拖拽选项「1」至选项「3」后'):
            param.json_update('field.options', [
                {
                    "value": "test_3",
                    "background_color": "#f1b300",
                    "color": "#fff"
                },
                {
                    "value": "test_2",
                    "background_color": "#00b388",
                    "color": "#fff"
                },
                {
                    "value": "test_1",
                    "background_color": "#307fe2",
                    "color": "#fff"
                }
            ])
            param.uri_args({'field_uuid': field_uuid})
            self.call(prj.FieldUpdate, param)

        with step('进入项目A查看「工作项1」工作项详情中属性A的选项值排序'):
            stamp = team_stamp({'field': 0})
            value = [v['value'] for f in stamp['field']['fields'] if f['uuid'] == field_uuid for v in f['options']][0]

            assert value == 'test_3'

    @story('131443 编辑工作项属性的属性名称')
    def test_field_name_up(self, uuid_storage):
        with step('前置条件'):
            field_uuid, param = field_param(2, uuid_storage)

            # 项目A存在工作项使用了工作项属性
            prm = {"field_uuid": field_uuid, "required": False}
            TaskAction.task_add_field(prm)

        with step('编辑属性名称'):
            field_name = f'up_name_{mocks.num()}'
            param.json_update('field.name', field_name)
            param.uri_args({'field_uuid': field_uuid})
            self.call(prj.FieldUpdate, param)

        with step('点击「添加属性到工作项类型」，查看工作项自定义属性'):
            stamp = team_stamp({'field': 0})
            fields = [f['name'] for f in stamp['field']['fields'] if f['uuid'] == field_uuid]

            assert field_name in fields

    @story('131444 编辑间隔时间来源')
    def test_interval_time_up(self, uuid_storage):
        with step('前置条件'):
            # 存在间隔时间类型的自定义工作项属性
            field_uuid, param = field_param(4, uuid_storage, step_settings={
                "step_start": {
                    "field_type": 12,
                    "field_uuid": "field005",
                    "method": "first_at",
                    "field_option_uuid": "XqxRFzZN"
                },
                "step_end": {
                    "field_type": 12,
                    "field_uuid": "field005",
                    "method": "first_at",
                    "field_option_uuid": "Nox3euh7"
                }
            })

            # 项目A存在工作项使用了工作项属性
            prm = {"field_uuid": field_uuid, "required": False}
            TaskAction.task_add_field(prm)

        with step('修改时间点'):
            param.json_update('field.step_settings', {
                "step_start": {
                    "field_type": 12,
                    "field_uuid": "field005",
                    "method": "last_at",
                    "field_option_uuid": "6tj7uFts"
                },
                "step_end": {
                    "field_type": 12,
                    "field_uuid": "field005",
                    "method": "first_at",
                    "field_option_uuid": "Nox3euh7"
                }
            })
            param.uri_args({'field_uuid': field_uuid})
            self.call(prj.FieldUpdate, param)

    @story('131457 编辑属性选项停留次数单选属性')
    @story('131458 全局配置-工作项属性：编辑属性选项停留次数选项')
    def test_stay_frequent_single_choice_field_up(self, uuid_storage):
        with step('前置条件'):
            # 存在属性选项停留次数类型的自定义工作项属性
            field_uuid, param = field_param(41, uuid_storage, stay_settings={
                "field_type": 1,
                "field_uuid": "field012",
                "field_option_uuid": "Drzwx1Lz"
            })

            # 项目A存在工作项使用了工作项属性
            prm = {"field_uuid": field_uuid, "required": False}
            TaskAction.task_add_field(prm)

        with step('修改单选属性为：状态  修复中'):
            param.json_update('field.stay_settings', {
                "field_type": 12,
                "field_uuid": "field005",
                "field_option_uuid": "DhQ3oPq6"
            })
            param.uri_args({'field_uuid': field_uuid})
            self.call(prj.FieldUpdate, param)

        with step('修改选项为：解决者'):
            param.json_update('field.stay_settings', {
                "field_type": 8,
                "field_uuid": "field040",
                "field_option_uuid": ACCOUNT.user.owner_uuid
            })
            self.call(prj.FieldUpdate, param)

    @story('131459 编辑属性选项停留时间单选属性')
    def test_stay_times_single_choice_field_up(self, uuid_storage):
        with step('前置条件'):
            # 存在属性选项停留时间类型的自定义工作项属性
            field_uuid, param = field_param(42, uuid_storage, stay_settings={
                "field_type": 12,
                "field_uuid": "field005",
                "field_option_uuid": "XqxRFzZN"
            })

            # 项目A存在工作项使用了工作项属性
            prm = {"field_uuid": field_uuid, "required": False}
            TaskAction.task_add_field(prm)

        with step('修改单选属性为：状态  修复中'):
            param.json_update('field.stay_settings.field_option_uuid', 'DhQ3oPq6')
            param.uri_args({'field_uuid': field_uuid})
            self.call(prj.FieldUpdate, param)

        with step('修改选项为：解决者'):
            param.json_update('field.stay_settings', {
                "field_type": 8,
                "field_uuid": "field040",
                "field_option_uuid": ACCOUNT.user.owner_uuid
            })
            self.call(prj.FieldUpdate, param)

    @story('123833 工作项属性：添加工作项属性（设置必填）')
    def test_add_issue_field_and_enable_require(self, uuid_storage):
        # 获取全局工作项uuid
        issue_uuid = global_issue_type().get('uuid')

        with step('添加工作项属性，开启必填'):
            param = issue.add_issue_field()[0]
            param.json_update('field_config.field_uuid', uuid_storage[2])
            param.uri_args({'issue_uuid': issue_uuid})
            resp = self.call(i.IssueFieldAdd, param)

            field_uuids = [f['field_uuid'] for f in resp.value('default_configs.default_field_configs')]
            assert uuid_storage[2] in field_uuids

        with step('清除数据'):
            pr = issue.delete_issue()[0]
            pr.uri_args({'issue_uuid': issue_uuid})
            pr.uri_args({'field_uuid': uuid_storage[2]})
            self.call(i.IssueFieldDelete, pr)

    @story('T123708 工作项属性：删除工作项属性--子任务')
    @story('T123827 工作项属性：添加工作项属性（设置必填）单选菜单-子任务')
    def test_add_and_del_field(self):
        issue_type_uuid = TaskAction.issue_type_uuid('子任务')
        with step("添加工作项属性（设置必填）单选菜单"):
            options = {
                "value": mocks.num(),
                "background_color": "#307fe2",
                "color": "#fff"
            }
            param = conf.add_issue_type_field()[0]
            param.json_update('field.type', 1)
            param.json_update('field.options', [options])
            res = self.call(project.FieldsAdd, param)
            field_uuid = res.value('field.uuid')

            # 将新增属性添加到对应工作项
            prm = issue.add_issue_field()[0]
            prm.json_update('field_config.field_uuid', field_uuid)
            prm.json_update('field_config.required', True)
            prm.uri_args({'issue_uuid': issue_type_uuid[0]})

            self.call(i.IssueFieldAdd, prm)

        with step('删除工作项属性'):
            # 删除工作项内属性
            Ia.del_issue_field(issue_type_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T123623 工作项属性：开启必填--子任务')
    def test_update_field_required(self):
        issue_type_uuid = TaskAction.issue_type_uuid('子任务')
        with step("前置条件，新增一个工作项属性"):
            options = {
                "value": mocks.num(),
                "background_color": "#307fe2",
                "color": "#fff"
            }
            param = conf.add_issue_type_field()[0]
            param.json_update('field.type', 1)
            param.json_update('field.options', [options])
            res = self.call(project.FieldsAdd, param)
            field_uuid = res.value('field.uuid')

            # 将新增属性添加到对应工作项
            prm = issue.add_issue_field()[0]
            prm.json_update('field_config.field_uuid', field_uuid)
            prm.uri_args({'issue_uuid': issue_type_uuid[0]})

            self.call(i.IssueFieldAdd, prm)
        with step('工作项属性：开启必填'):
            prm.json_update('field_config.required', True)
            prm.uri_args({'field_uuid': field_uuid})
            self.call(i.IssueFieldUpdate, prm)

        with step('删除工作项属性'):
            # 删除工作项内属性
            Ia.del_issue_field(issue_type_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T44229 工作项属性-严重程度：编辑工作项属性')
    def test_33(self):
        # 获取严重程度选项信息
        with step('1.输入选项值：P5 2.点击「添加」按钮'):
            param = generate_param({
                "field": {
                    "name": "严重程度",
                    "type": 1,
                    "uuid": "field038",
                    "options": []
                }
            })[0]
            severity_options = PrjAction.get_severity_level()
            severity_options.append({"value": "p5", "background_color": "#9678d3", "color": "#fff"})
            param.json_update('field.options', severity_options)
            param.uri_args({'field_uuid': 'field038'})
            self.call(project.FieldUpdate, param)
        with step('还原数据'):
            # 删除列表最后一个元素
            severity_options.pop()
            self.call(project.FieldUpdate, param)



@feature('全局配置-工作项属性删除')
class TestIssueFieldDelete(Checker):

    @story('131338 删除工作项属性（已经被项目使用）')
    @parametrize('param', data.field_delete())
    def test_issue_field_used_del(self, param, uuid_storage):
        param.uri_args({'field_uuid': uuid_storage[0]})
        resp = self.call(prj.FieldDelete, param, status_code=801)

        resp.check_response('errcode', 'InUse.Field.UsedInFieldConfig')

    @story('131464 删除单选菜单选项值/131465 删除多选菜单选项值')
    @parametrize('type_index', (1, 16))
    def test_choice_option_value_del(self, type_index, uuid_storage):
        with step('前置条件'):
            # 存在单选菜单类型的自定义工作项属性
            field_uuid, param = field_param(type_index, uuid_storage, options=[
                {
                    "value": "test_1",
                    "background_color": "#307fe2",
                    "color": "#fff"
                },
                {
                    "value": "test_2",
                    "background_color": "#00b388",
                    "color": "#fff"
                },
                {
                    "value": "test_3",
                    "background_color": "#f1b300",
                    "color": "#fff"
                }
            ])

            # 项目A存在工作项使用了工作项属性
            prm = {"field_uuid": field_uuid, "required": False}
            TaskAction.task_add_field(prm)

            # 工作项属性选择的默认值1
            issue_uuid = TaskAction.issue_type_uuid()[0]

            stamp = team_stamp({'field': 0})
            value = [v['uuid'] for f in stamp['field']['fields'] if f['uuid'] == field_uuid for v in f['options']][0]

            time.sleep(1)
            parm = conf.proj_field_update()[0]
            parm.json_update('field_config.default_value', value)
            if type_index == 16:
                parm.json_update('field_config.default_value', [value])
            parm.uri_args({"issue_uuid": issue_uuid})
            parm.uri_args({"field_uuid": field_uuid})
            self.call(prj.ProjectIssueFieldUpdate, parm, status_code=[200, 403])

        with step('删除工作项属性的默认值1'):
            param.json_update('field.options', [{
                "value": "test_2",
                "background_color": "#00b388",
                "color": "#fff"
            }, {
                "value": "test_3",
                "background_color": "#f1b300",
                "color": "#fff"
            }])
            param.uri_args({'field_uuid': field_uuid})
            self.call(prj.FieldUpdate, param)

        with step('进入项目A查看「工作项1」工作项详情中属性A的选项值'):
            stamp = team_stamp({'field': 0})
            value = [v['value'] for f in stamp['field']['fields'] if f['uuid'] == field_uuid for v in f['options']]

            assert 'test_1' not in value

    @story('131339 删除已被「间隔次数」和「间隔时间」属性使用的日期类型工作项属性')
    def test_interval_date_used_del(self, uuid_storage):
        """删除间隔类型使用的日期选项"""
        field_param(5, uuid_storage)

    @story('131340 删除已被「间隔次数」和「间隔时间」属性使用的时间类型工作项属性')
    def test_interval_time_used_del(self, uuid_storage):
        """删除间隔类型使用的时间选项"""
        field_param(6, uuid_storage)

    @story('131341 删除已被「属性选项停留次数」和「属性选项停留时间」属性使用的单选菜单类型工作项属性')
    def test_stay_frequent_choice_used_del(self, uuid_storage):
        """删除停留次数类型已使用单选菜单的属性"""
        field_param(1, uuid_storage, options=[
            {
                "value": "test_1",
                "background_color": "#307fe2",
                "color": "#fff"
            },
            {
                "value": "test_2",
                "background_color": "#00b388",
                "color": "#fff"
            }
        ])

    @story('131342 删除已被「属性选项停留次数」和「属性选项停留时间」属性使用的单选成员类型工作项属性')
    def test_stay_frequent_member_used_del(self, uuid_storage):
        """删除停留次数类型已使用单选成员的属性"""
        field_param(8, uuid_storage)

    @story('131343 删除已被「属性选项停留次数」和「属性选项停留时间」属性使用的单选迭代类型工作项属性')
    def test_stay_frequent_sprint_used_del(self, uuid_storage):
        """删除停留次数类型已使用单选迭代的属性"""
        field_param(7, uuid_storage)

    @story('123627 工作项属性：开启必填')
    def test_issue_field_enable_require(self):
        with step('开启「所属迭代属性」必填'):
            stamp = team_stamp({'issue_type': 0})
            issue_uuid = [f['uuid'] for f in stamp['issue_type']['issue_types'] if f['name'] == '工单'][0]
            field_uuid = 'field011'  # field011 所属迭代属性uuid

            param = conf.update_issue_field(field_uuid)[0]
            param.json_update('field_config.required', True)
            param.uri_args({'issue_uuid': issue_uuid})
            param.uri_args({'field_uuid': field_uuid})

            resp = self.call(i.IssueFieldUpdate, param)
            field_config = [f['required'] for f in resp.value('default_configs.default_field_configs') if
                            f['field_uuid'] == field_uuid][0]

            assert True == field_config

        with step('还原为非必填'):
            param.json_update('field_config.required', False)
            self.call(i.IssueFieldUpdate, param)

    @story('123641 工作项属性：开箱后属性列表检查')
    def test_issue_field_list_check(self):
        key_set = None

        stamp = team_stamp({'issue_type': 0})
        for f in stamp['issue_type']['issue_types']:
            if f['name'] == '任务':
                key_set = set(f)

        assert 'name' in key_set
