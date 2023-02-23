"""
@Desc：项目设置-迭代配置
"""
import random
import time

from falcons.check import Checker, go
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture, step, parametrize
from falcons.helper import mocks
from falcons.ops import generate_param

from main.actions.pro import PrjAction
from main.actions.sprint import SprintAction
from main.api import sprint as sp
from main.api.sprint import ProSprintFieldUpdate
from main.helper.extra import Extra
from main.params import proj, data
from . import SprintOpt


@fixture(scope='module')
def sprint_init():
    sprint_uuid = SprintAction.sprint_add()

    return sprint_uuid


@fixture(scope='module')
def data_storage():
    return {}


@fixture(scope='module')
def _project():
    # 创建一个单独项目
    time.sleep(2)
    pid = PrjAction.new_project(index=3, name='项目-迭代配置-迭代阶段')
    # 新建两个迭代阶段
    statuses = []
    for i in range(2):
        param = proj.sprint_status_opt()[0]
        param.uri_args({"project_uuid": pid})
        res = go(sp.SprintStatusAdd, param)
        statuses.append(res.value('status.uuid'))
    yield pid
    # 删除项目
    creator = Extra(ApiMeta)
    creator.del_project(pid)


@feature('项目设置-迭代配置')
class TestSprintConfig(Checker):

    @classmethod
    def get_sprint_statuses(cls, pid):
        l_param = generate_param()[0]
        l_param.uri_args({'project_uuid': pid})
        res = cls.call(sp.SprintStatuses, l_param)
        return res.value('statuses')

    @story('119435 迭代阶段：新建迭代阶段')
    @parametrize('param', proj.sprint_status_opt())
    def test_sprint_status_add(self, param, data_storage):
        with step('阶段名称输入：示例阶段'):
            resp = self.call(sp.SprintStatusAdd, param)

        data_storage |= {'status_uuid': resp.value('status.uuid')}

    @story('119431迭代阶段：编辑迭代阶段')
    @parametrize('param', proj.sprint_status_opt())
    def test_sprint_status_name_update(self, param, data_storage):
        with step('阶段名称修改为：update示例阶段'):
            param.uri_args({'status_uuid': data_storage['status_uuid']})
            self.call(sp.SprintStageUpdate, param)

    @story('119434 迭代阶段：删除已被使用的迭代阶段')
    @story('148525 迭代配置-迭代阶段：删除已被使用的迭代阶段')
    def test_del_inuse_sprint_status(self, sprint_init, data_storage):
        status_u = SprintAction.sprint_status(sprint_init)

        with step('前提条件'):
            # 存在迭代阶段已被使用
            param = proj.sprint_status_up(['to_do', 'in_progress'], [status_u[0], data_storage['status_uuid']],
                                          sprint_init)[0]
            param.json_update('sprint_statuses[1].is_current_status', True)
            self.call(sp.SprintStatusUpdate, param)

        with step('删除已使用的阶段'):
            param.uri_args({'status_uuid': data_storage['status_uuid']})
            resp = self.call(sp.SprintStatusDelete, param, status_code=801)
            resp.check_response('errcode', 'InUse.SprintStatus')

        with step('将迭代阶段还原回未开始'):
            param = proj.sprint_status_up(['in_progress', 'to_do'], [data_storage['status_uuid'], status_u[0]],
                                          sprint_init)[0]
            param.json_update('sprint_statuses[1].is_current_status', True)
            self.call(sp.SprintStatusUpdate, param)

    @story('148524 迭代阶段：删除未被使用的迭代阶段（优化提示文案）')
    @story('119433 删除未被使用的迭代阶段')
    @parametrize('param', proj.sprint_status_del())
    def test_del_unused_sprint_status(self, param, sprint_init, data_storage):
        with step('删除未使用的阶段'):
            param.uri_args({'status_uuid': data_storage['status_uuid']})
            self.call(sp.SprintStatusDelete, param)

        with step('阶段列表不包含「示例阶段」'):
            status_u = SprintAction.sprint_status(sprint_init)

            assert data_storage['status_uuid'] not in status_u

    @story('T119436 迭代配置-迭代阶段：修改迭代阶段排序（存在多个自定义迭代阶段）')
    def test_update_sort_sprint_status(self, _project):
        with step('初始迭代阶段顺序'):
            _statuses = [s['uuid'] for s in self.get_sprint_statuses(_project)]
        with step('修改迭代阶段顺序'):
            param = proj.sprint_status_opt()[0]
            param.json_update('status', {
                "uuid": _statuses[3],
                "next_uuid": _statuses[2]
            })
            param.uri_args({'project_uuid': _project, 'status_uuid': _statuses[3]})
            self.call(sp.SprintStageUpdate, param)
        with step('查看调序后的迭代阶段列表'):
            statuses = [s['uuid'] for s in self.get_sprint_statuses(_project)]
            assert statuses == _statuses[0:2] + [_statuses[3], _statuses[2]] + [_statuses[4]]

    @story('119503 迭代属性：新建迭代属性（单选菜单）')
    @parametrize('param', proj.sprint_field_add('option'))
    def test_add_sprint_field_radio_menu(self, param, data_storage):
        res = self.call(sp.SprintFieldAdd, param)

        data_storage |= {'field_uuid': res.value('field.uuid')}
        data_storage |= {'opt_uuid': [v['uuid'] for v in res.value('field.options')]}

    @story('119494 迭代属性：添加单选菜单的属性默认值')
    @parametrize('param', proj.sprint_field_up())
    def test_sprint_field_add_default(self, param, data_storage):
        with step('单选菜单属性默认值选择1'):
            param.json = proj.sprint_field_param(data_storage['opt_uuid'][0], data_storage['opt_uuid'][1])
            param.uri_args({'field_uuid': data_storage['field_uuid']})

            self.call(sp.ProSprintFieldUpdate, param)

        with step('查看新建迭代的示例单选菜单属性值'):
            resp = self.call(sp.ProSprintField, param, with_json=False)

            default_value = [v['default_value'] for v in resp.value('fields') if
                             v['uuid'] == data_storage['field_uuid']]

            assert data_storage['opt_uuid'][0] in default_value

    @story('119455 迭代属性：编辑迭代属性（单选菜单）')
    @parametrize('param', proj.sprint_field_up())
    def test_sprint_field_update(self, param, data_storage):
        with step('修改属性名称为：编辑单选菜单'):
            param.json = proj.sprint_field_param(data_storage['opt_uuid'][1], data_storage['opt_uuid'][0])
            param.uri_args({'field_uuid': data_storage['field_uuid']})
            self.call(sp.ProSprintFieldUpdate, param)

    @story('119513 迭代属性：修改迭代名称的属性默认值')
    @parametrize('param', proj.sprint_field_up())
    def test_sprint_name_default_update(self, param, data_storage):
        param.json = {
            "field": {
                "uuid": "sprint01",
                "name": "迭代名称",
                "type": "text",
                "default_value": "default",
                "default_value_type": "auto",
                "built_in": True
            }
        }
        param.uri_args({'field_uuid': 'sprint01'})
        self.call(sp.ProSprintFieldUpdate, param)

    @story('119514 迭代属性：修改迭代属性排序（存在多个迭代属性）')
    @parametrize('param', proj.sprint_field_position())
    def test_sprint_field_sort(self, param):
        resp = self.call(sp.ProSprintField, param, with_json=False, is_print=False)

        field_uuids = [f['uuid'] for f in resp.value('fields')]
        random.shuffle(field_uuids)  # 对列表进行随机排序

        param.json_update('field_uuids', field_uuids)
        self.call(sp.SprintFieldPosition, param)

    @story('119470 迭代属性：检查支持的迭代属性类型')
    @parametrize('param', proj.sprint_field_position())
    def test_check_sprint_field_type(self, param):
        self.call(sp.ProSprintField, param, with_json=False)

    @story('119480 迭代属性：删除迭代属性（单选菜单）')
    @parametrize('param', data.field_delete())
    def test_del_sprint_field(self, param, data_storage):
        param.uri_args({'field_uuid': data_storage['field_uuid']})
        self.call(sp.SprintFieldDelete, param)

    @story("T119498 迭代配置-迭代属性：添加日期的属性默认值")
    @story("T119484 迭代配置-迭代属性：删除迭代属性（日期）")
    def test_add_sprint_field_date(self):
        with step("新建一个迭代属性,日期类型"):
            response = SprintAction.sprint_add_field('date')
            field_uuid = response.value('field.uuid')
            field_name = response.value('field.name')
        with step("修改日期的默认属性"):
            default_value = mocks.date_string()
            SprintOpt.field_default_edit(field_name, field_uuid, 'date', default_value)
        with step("获取属性列表"):
            SprintAction.sprint_field_list(field_uuid, default_value)
        with step("删除 迭代属性"):
            SprintAction.sprint_del_field(field_uuid)

    @story("T119493 迭代配置-迭代属性：添加单行文本的属性默认值")
    def test_add_sprint_field_text(self):
        response = SprintAction.sprint_add_field('text')
        field_uuid = response.value('field.uuid')
        field_name = response.value('field.name')

        with step("添加单行文本的默认属性"):
            default_value = mocks.random_text(5)
            SprintOpt.field_default_edit(field_name, field_uuid, 'text', default_value)
        with step("获取属性列表"):
            SprintAction.sprint_field_list(field_uuid, default_value)
        with step("删除 迭代属性"):
            SprintAction.sprint_del_field(field_uuid)

    @story("T119497 迭代配置-迭代属性：添加浮点数的属性默认值")
    @story("T119483 迭代配置-迭代属性：删除迭代属性（浮点数）")
    def test_add_sprint_field_float(self):
        response = SprintAction.sprint_add_field('float')
        field_uuid = response.value('field.uuid')
        field_name = response.value('field.name')

        with step("添加浮点数的默认属性"):
            param1 = proj.sprint_field_up()[0]
            default_value = 9990000
            param1.json = {
                "field": {
                    "uuid": field_uuid,
                    "name": field_name,
                    "type": "float",
                    "default_value": default_value,
                    "default_value_type": "default",
                    "built_in": False,
                    "options": None,
                    "required": False,
                    "can_modify_required": True,
                    "value": 99.9
                }
            }

            param1.uri_args({"field_uuid": field_uuid})
            self.call(ProSprintFieldUpdate, param1)

        with step("获取属性列表"):
            SprintAction.sprint_field_list(field_uuid, default_value)
        with step("删除 迭代属性"):
            SprintAction.sprint_del_field(field_uuid)

    @story("T119500 迭代配置-迭代属性：添加整数的属性默认值")
    @story("T119486 迭代配置-迭代属性：删除迭代属性（整数）")
    def test_add_sprint_field_int(self):
        response = SprintAction.sprint_add_field('integer')
        field_uuid = response.value('field.uuid')
        field_name = response.value('field.name')

        with step("添加整数的默认属性"):
            param1 = proj.sprint_field_up()[0]
            default_value = 10000000
            param1.json = {
                "field": {
                    "uuid": field_uuid,
                    "name": field_name,
                    "type": "integer",
                    "default_value": default_value,
                    "default_value_type": "default",
                    "built_in": False,
                    "options": None,
                    "required": False,
                    "can_modify_required": True,
                    "value": 100
                }
            }

            param1.uri_args({"field_uuid": field_uuid})
            self.call(ProSprintFieldUpdate, param1)

        with step("获取属性的列表"):
            SprintAction.sprint_field_list(field_uuid, default_value)
        with step("删除 迭代属性"):
            SprintAction.sprint_del_field(field_uuid)

    @story("T119499 迭代配置-迭代属性：添加时间的属性默认值")
    @story("T119485 迭代配置-迭代属性：删除迭代属性（时间）")
    def test_add_sprint_field_date(self):
        with step("新建一个迭代属性,时间类型"):
            response = SprintAction.sprint_add_field('time')
            field_uuid = response.value('field.uuid')
            field_name = response.value('field.name')
        with step("修改时间的默认属性"):
            default_value = mocks.now_timestamp()
            SprintOpt.field_default_edit(field_name, field_uuid, 'time', default_value)
        with step("获取属性列表"):
            SprintAction.sprint_field_list(field_uuid, default_value)
        with step("删除 迭代属性"):
            SprintAction.sprint_del_field(field_uuid)

    @story("T119495 迭代配置-迭代属性：添加单选成员的属性默认值")
    @story("T119481 迭代配置-迭代属性：删除迭代属性（单选成员）")
    def test_sprint_field_menu_user(self):
        with step("新建一个迭代属性,单选成员类型"):
            response = SprintAction.sprint_add_field('user')
            field_uuid = response.value('field.uuid')
            field_name = response.value('field.name')
        with step("修改单选成员的默认属性"):
            default_value = mocks.ones_uuid()
            SprintOpt.field_default_edit(field_name, field_uuid, 'user', default_value)
        with step("获取属性列表"):
            SprintAction.sprint_field_list(field_uuid, default_value)
        with step("删除 迭代属性"):
            SprintAction.sprint_del_field(field_uuid)

    @story("T119496 迭代配置-迭代属性：添加多行文本的属性默认值")
    @story("T119482 迭代配置-迭代属性：删除迭代属性（多行文本）")
    def test_sprint_field_multiline_text(self):
        with step("新建一个迭代属性,多行文本类型"):
            response = SprintAction.sprint_add_field('multi_line_text')
            field_uuid = response.value('field.uuid')
            field_name = response.value('field.name')
            with step("添加多行文本的默认属性"):
                default_value = "你好\n" + mocks.random_text(5)
                SprintOpt.field_default_edit(field_name, field_uuid, 'multi_line_text', default_value)
            with step("获取属性列表"):
                SprintAction.sprint_field_list(field_uuid, default_value)
            with step("删除 迭代属性"):
                SprintAction.sprint_del_field(field_uuid)
