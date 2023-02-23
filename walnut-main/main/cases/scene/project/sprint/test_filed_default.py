"""
@File    ：test_filed_default
@Author  ：xiechunwei
@Date    ：2022/7/14 15:35
@Desc    ：项目设置-迭代配置-迭代属性，默认值操作
"""
from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, step, parametrize, mark
from falcons.helper import mocks

from main.actions.sprint import SprintAction
from main.api import sprint as sp
from main.params import proj
from main.params.const import ACCOUNT
from . import SprintOpt


@fixture(scope='module')
def sprint_init():
    sprint_uuid = SprintAction.sprint_add()

    return sprint_uuid


@fixture(scope='module')
def data_storage():
    return {}


@mark.smoke
@feature('迭代配置-迭代属性')
class TestFiledUpdateDefault(Checker):

    @story('T119515 修改迭代属性排序（只有一个迭代属性）')
    def test_up_one_sprint_filed_sort(self):
        with step('长按「迭代名称」拖拽至任意位置'):
            param = proj.sprint_field_position()[0]
            param.json_update('field_uuids', ['sprint01'])

            self.call(sp.SprintFieldPosition, param)

    @story('T119510 修改单行文本的属性默认值')
    @story('T119516 修改多行文本的属性默认值')
    @parametrize('types', ['text', 'multi_line_text'])
    def test_up_text_default(self, types, data_storage):
        with step('存在示例单行文本；默认值为：示例默认值'):
            field_name, field_uuid = SprintOpt.sprint_field_add(types, data_storage)

        with step('修改属性默认值'):
            up_value = f'up-{types}-{mocks.ones_uuid()}'
            SprintOpt.field_default_edit(field_name, field_uuid, types, up_value)

        with step('查看新建迭代的属性默认值'):
            SprintOpt.check_sprint_field(field_name, field_uuid, 'default_value', up_value)

    @story('T119511 修改单选菜单的属性默认值')
    def test_up_option_default(self, ):
        with step('存在单选菜单属性'):
            param = proj.sprint_field_add('option')[0]
            resp = self.call(sp.SprintFieldAdd, param)

            field_uuid, field_name = resp.value('field.uuid'), resp.value('field.name')
            field_opt = resp.value('field.options')
            opt_uuid = [o['uuid'] for o in resp.value('field.options')]

        with step('修改属性默认值'):
            SprintOpt.field_default_edit(field_name, field_uuid, 'option', opt_uuid[1], field_opt)

        with step('查看新建迭代的属性默认值'):
            SprintOpt.check_sprint_field(field_name, field_uuid, 'default_value', opt_uuid[1])

    @story('T119512 修改单选成员的属性默认值')
    def test_up_single_user_default(self, data_storage):
        with step('存在单选成员属性'):
            field_name, field_uuid = SprintOpt.sprint_field_add('user', data_storage)

        with step('修改属性默认值'):
            up_value = ACCOUNT.user.owner_uuid
            SprintOpt.field_default_edit(field_name, field_uuid, 'user', up_value)

        with step('查看新建迭代的属性默认值'):
            SprintOpt.check_sprint_field(field_name, field_uuid, 'default_value', up_value)

    @story('T119517 修改浮点数的属性默认值')
    def test_up_float_default(self, data_storage):
        with step('存在浮点数属性'):
            field_name, field_uuid = SprintOpt.sprint_field_add('float', data_storage)

        with step('修改属性默认值'):
            up_value = 166000
            SprintOpt.field_default_edit(field_name, field_uuid, 'float', up_value)

        with step('查看新建迭代的属性默认值'):
            SprintOpt.check_sprint_field(field_name, field_uuid, 'default_value', up_value)

    @story('T119518 修改日期的属性默认值')
    @story('T119519 修改时间的属性默认值')
    @parametrize('types', ['date', 'time'])
    def test_up_date_and_time_default(self, types, data_storage):
        with step('存在属性'):
            field_name, field_uuid = SprintOpt.sprint_field_add(types, data_storage)

        with step('修改属性默认值'):
            up_value = mocks.now_timestamp()
            SprintOpt.field_default_edit(field_name, field_uuid, types, up_value)

        with step('查看新建迭代的属性默认值'):
            SprintOpt.check_sprint_field(field_name, field_uuid, 'default_value', up_value)

    @story('T119520 修改整数的属性默认值')
    def test_up_integer_default(self, data_storage):
        with step('存在整数属性'):
            field_name, field_uuid = SprintOpt.sprint_field_add('integer', data_storage)

        with step('修改属性默认值'):
            up_value = 200000
            SprintOpt.field_default_edit(field_name, field_uuid, 'integer', up_value)

        with step('查看新建迭代的属性默认值'):
            SprintOpt.check_sprint_field(field_name, field_uuid, 'default_value', up_value)


@mark.smoke
@feature('迭代配置-迭代属性')
class TestFiledClearDefault(Checker):

    @story('T119471 清空单行文本的属性默认值')
    @story('T119473 清空单选成员的属性默认值')
    @story('T119474 清空多行文本的属性默认值')
    @story('T119475 清空浮点数的属性默认值')
    @story('T119476 清空日期的属性默认值')
    @story('T119477 清空时间的属性默认值')
    @story('T119478 清空整数的属性默认值')
    @parametrize('types', ['text', 'multi_line_text', 'user', 'float', 'date', 'time', 'integer'])
    def test_clear_sprint_filed_default(self, types, data_storage):
        with step('属性默认值输入框的「清空」'):
            SprintOpt.field_default_edit(data_storage[f'{types}-name'], data_storage[types], types, None)

        with step('查看新建迭代的属性默认值'):
            SprintOpt.check_sprint_field(data_storage[f'{types}-name'], data_storage[types])

    @story('T119472 清空单选菜单的属性默认值')
    def test_clear_option_default(self):
        with step('存在单选菜单属性'):
            param = proj.sprint_field_add('option')[0]
            resp = self.call(sp.SprintFieldAdd, param)

            field_uuid, field_name = resp.value('field.uuid'), resp.value('field.name')
            field_opt = resp.value('field.options')
            opt_uuid = [o['uuid'] for o in resp.value('field.options')]

        with step('修改属性默认值'):
            SprintOpt.field_default_edit(field_name, field_uuid, 'option', opt_uuid[1], field_opt)

        with step('再「清空」默认值'):
            SprintOpt.field_default_edit(field_name, field_uuid, 'option', None, field_opt)
