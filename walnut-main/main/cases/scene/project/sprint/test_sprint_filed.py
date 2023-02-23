"""
@File    ：test_sprint_filed
@Author  ：xiechunwei
@Date    ：2022/6/30 11:57
@Desc    ：项目设置-迭代配置-迭代属性
"""
from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, step, parametrize, mark
from falcons.helper import mocks

from main.actions.sprint import SprintAction
from main.api import sprint as sp
from main.params import proj, data
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
@feature('迭代属性')
class TestSprintFiledAdd(Checker):

    @story('119502 新建迭代属性（单行文本）')
    @story('119501 迭代配置-迭代属性：新建迭代属性弹窗按钮检查')
    def test_add_sprint_field_single_text(self, data_storage, sprint_init):
        with step('输入属性名称，选择（单行文本）'):
            field_name, field_uuid = SprintOpt.sprint_field_add('text', data_storage)

        with step('进入迭代概览页面，查看迭代属性'):
            SprintOpt.check_sprint_field(field_name, field_uuid)

        with step('迭代概览，点击（单行文本），输入框输入'):
            SprintOpt.set_field_value(sprint_init, field_uuid, 'test')

    @story('119504 新建迭代属性（单选成员）')
    def test_add_sprint_field_single_user(self, data_storage, sprint_init):
        with step('输入属性名称，选择（单选成员）'):
            field_name, field_uuid = SprintOpt.sprint_field_add('user', data_storage)

        with step('进入迭代概览页面，查看迭代属性'):
            SprintOpt.check_sprint_field(field_name, field_uuid)

        with step('迭代概览，点击（单选成员），选择成员'):
            SprintOpt.set_field_value(sprint_init, field_uuid, ACCOUNT.user.owner_uuid)

    @story('119505 新建迭代属性（多行文本）')
    def test_add_sprint_field_multi_text(self, data_storage, sprint_init):
        with step('输入属性名称，选择（多行文本）'):
            field_name, field_uuid = SprintOpt.sprint_field_add('multi_line_text', data_storage)

        with step('进入迭代概览页面，查看迭代属性'):
            SprintOpt.check_sprint_field(field_name, field_uuid)

        with step('迭代概览，点击（多行文本），输入框输入'):
            SprintOpt.set_field_value(sprint_init, field_uuid, 'test')

    @story('119506 新建迭代属性（浮点数）')
    def test_add_sprint_field_float(self, data_storage, sprint_init):
        with step('输入属性名称，选择（浮点数）'):
            field_name, field_uuid = SprintOpt.sprint_field_add('float', data_storage)

        with step('进入迭代概览页面，查看迭代属性'):
            SprintOpt.check_sprint_field(field_name, field_uuid)

        with step('迭代概览，点击（浮点数），输入框输入'):
            SprintOpt.set_field_value(sprint_init, field_uuid, '186000')

    @story('119507 新建迭代属性（日期）')
    def test_add_sprint_field_date(self, data_storage, sprint_init):
        with step('输入属性名称，选择（日期）'):
            field_name, field_uuid = SprintOpt.sprint_field_add('date', data_storage)

        with step('进入迭代概览页面，查看迭代属性'):
            SprintOpt.check_sprint_field(field_name, field_uuid)

        with step('迭代概览，点击（日期），输入框输入'):
            SprintOpt.set_field_value(sprint_init, field_uuid, mocks.now_timestamp())

    @story('119508 新建迭代属性（时间）')
    def test_add_sprint_field_time(self, data_storage, sprint_init):
        with step('输入属性名称，选择（时间）'):
            field_name, field_uuid = SprintOpt.sprint_field_add('time', data_storage)

        with step('进入迭代概览页面，查看迭代属性'):
            SprintOpt.check_sprint_field(field_name, field_uuid)

        with step('迭代概览，点击（时间），输入框输入'):
            SprintOpt.set_field_value(sprint_init, field_uuid, mocks.now_timestamp())

    @story('119509 新建迭代属性（整数）')
    def test_add_sprint_field_integer(self, data_storage, sprint_init):
        with step('输入属性名称，选择（整数）'):
            field_name, field_uuid = SprintOpt.sprint_field_add('integer', data_storage)

        with step('进入迭代概览页面，查看迭代属性'):
            SprintOpt.check_sprint_field(field_name, field_uuid)

        with step('迭代概览，点击（整数），输入框输入'):
            SprintOpt.set_field_value(sprint_init, field_uuid, '10000000')

    @story('44209 批量添加迭代属性选项值')
    @story('44210 批量添加迭代属性选项值')
    def test_add_sprint_field_batch_option(self, data_storage):
        with step('按钮右侧的下拉菜单「批量添加」'):
            op = {'options': [{"value": "test_1"}, {"value": "test_2"}, {"value": "test_3"}]}

        with step('输入属性名称，选择（单选菜单）'):
            field_name, field_uuid = SprintOpt.sprint_field_add('option', data_storage, op)

        with step('进入迭代概览页面，查看迭代属性'):
            SprintOpt.check_sprint_field(field_name, field_uuid)

    @story('119447 新建迭代属性：单选菜单的选项值数量校验')
    def test_add_sprint_field_option_number_check(self, data_storage):
        with step('添加1000个选项值'):
            op = {'options': [{"value": f"test_{i};", "background_color": "#307fe2", "color": "#fff"}
                              for i in range(1001)]}

            SprintOpt.sprint_field_add('option', data_storage, op)
            # 添加失败，保留输入框内容，在输入框下方提示“选项值数量超出限制”  前端做了控制，后端未做

    @story('119448 新建迭代属性：单选菜单选项值重名校验')
    def test_add_sprint_field_option_value_same_name(self, data_storage):
        with step('添加重名选项值'):
            op = {'options': [{"value": "test_1"}, {"value": "test_1"}]}

            SprintOpt.sprint_field_add('option', data_storage, op)
            # 编辑失败，toast提示“选项名称已存在，请重新输入”  前端做了控制，后端未做

    @story('119452 新建迭代属性：添加单选菜单选项值校验')
    def test_add_sprint_field_option_value_check(self, data_storage):
        with step('不输入选项值'):
            op = {'options': [{"value": ""}]}

            SprintOpt.sprint_field_add('option', data_storage, op, code=801)

    @story('119453 新建迭代属性：修改选项值排序')
    def test_add_sprint_field_option_value_sort(self, data_storage):
        with step('选择单选菜单，添加三个选项值'):
            op = {'options': [{"value": "test_1"}, {"value": "test_2"}, {"value": "test_3"}]}

            field_name, field_uuid = SprintOpt.sprint_field_add('option', data_storage, op)

        with step('长按拖拽「示例选项值1」至选项值列表最后'):
            op = [{"value": "test_2"}, {"value": "test_3"}, {"value": "test_1"}]

            param = proj.sprint_field_value_up(field_uuid, field_name, op)[0]
            param.uri_args({'field_uuid': field_uuid})
            self.call(sp.ProSprintFieldUpdate, param)

    @story('119446 新建迭代属性：编辑单选菜单选项值')
    def test_add_sprint_field_edit_option_value(self, data_storage):
        with step('选择单选菜单，添加两个个选项值'):
            op = {'options': [{"value": "test_1"}, {"value": "test_2"}]}

            field_name, field_uuid = SprintOpt.sprint_field_add('option', data_storage, op)

        with step('修改选项值名称'):
            op = [{"value": "示例test_1"}, {"value": "test_2"}]

            param = proj.sprint_field_value_up(field_uuid, field_name, op)[0]
            param.uri_args({'field_uuid': field_uuid})

            self.call(sp.ProSprintFieldUpdate, param)

    @story('119449 新建迭代属性：删除单选菜单选项值')
    def test_add_sprint_field_del_option_value(self, data_storage):
        with step('选择单选菜单，添加两个个选项值'):
            op = {'options': [{"value": "test_1"}, {"value": "test_2"}]}
            field_name, field_uuid = SprintOpt.sprint_field_add('option', data_storage, op)

        with step('删除选项值test_2'):
            op = [{"value": "test_1"}]

            param = proj.sprint_field_value_up(field_uuid, field_name, op)[0]
            param.uri_args({'field_uuid': field_uuid})
            self.call(sp.ProSprintFieldUpdate, param)

        with step('项目概览迭代属性，test_2选择值不存在'):
            param = proj.sprint_field_position()[0]
            resp = self.call(sp.ProSprintField, param, with_json=False)

            values = [v['value'] for f in resp.value('fields') if f['name'] == field_name for v in f['options']]

            assert 'test_2' not in values

    @story('119450 新建迭代属性：属性名称校验')
    def test_add_sprint_field_name_check(self):
        param = proj.sprint_field_add('text')[0]
        del param.json['field']['options']
        with step('不输入属性名称'):
            param.json['field']['name'] = ''
            self.call(sp.SprintFieldAdd, param, status_code=801)

        with step('输入超过16位'):
            param.json['field']['name'] = mocks.serial_no()[:16]
            # self.call(sp.SprintFieldAdd, param)  # 前端做了控制，后端未做

    @story('119451 新建迭代属性：属性名称重名校验')
    def test_add_sprint_field_name_same(self, data_storage):
        with step('输入属性名称，选择（单行文本）'):
            field_name, field_uuid = SprintOpt.sprint_field_add('text', data_storage)

        with step('再次输入添加该属性名称'):
            param = proj.sprint_field_add('text')[0]
            del param.json['field']['options']
            param.json['field']['name'] = field_name
            resp = self.call(sp.SprintFieldAdd, param, status_code=409)

            resp.check_response('reason', 'NameExists')


@mark.smoke
@feature('迭代属性-编辑迭代属性')
class TestSprintFiledEdit(Checker):

    @story('119454 编辑迭代属性（单行文本）')
    def test_edit_sprint_field_single_text(self, data_storage):
        SprintOpt.sprint_field_edit('text', data_storage['text'])

    @story('119456 编辑迭代属性（单选成员）')
    def test_edit_sprint_field_single_user(self, data_storage):
        SprintOpt.sprint_field_edit('user', data_storage['user'])

    @story('119457 编辑迭代属性（多行文本）')
    def test_edit_sprint_field_multi_text(self, data_storage):
        SprintOpt.sprint_field_edit('multi_line_text', data_storage['multi_line_text'])

    @story('119458 编辑迭代属性（浮点数）')
    def test_edit_sprint_field_float(self, data_storage):
        SprintOpt.sprint_field_edit('float', data_storage['float'])

    @story('119459 编辑迭代属性（日期）')
    def test_edit_sprint_field_date(self, data_storage):
        SprintOpt.sprint_field_edit('date', data_storage['date'])

    @story('119460 编辑迭代属性（时间）')
    def test_edit_sprint_field_time(self, data_storage):
        SprintOpt.sprint_field_edit('time', data_storage['time'])

    @story('119461 编辑迭代属性（整数）')
    def test_edit_sprint_field_integer(self, data_storage):
        SprintOpt.sprint_field_edit('integer', data_storage['integer'])

    @story('119442 编辑迭代属性：属性名称校验')
    def test_edit_sprint_field_name_check(self, data_storage):
        with step('不输入属性名称'):
            param = proj.sprint_field_value_up(data_storage['text'], '', None, 'text')[0]
            param.uri_args({'field_uuid': data_storage['text']})

            self.call(sp.ProSprintFieldUpdate, param, status_code=801)

        with step('输入超过16位'):
            param.json['field']['name'] = mocks.serial_no()[:16]
            # self.call(sp.SprintFieldAdd, param)  # 前端做了控制，后端未做

    @story('119439 编辑迭代属性：单选菜单选项值重名校验')
    def test_edit_sprint_field_option_value_same_name(self, data_storage):
        with step('前置条件'):
            # 存在单选菜单迭代属性
            opt = {'options': [{"value": "test_1"}, {'value': 'test_2'}]}
            field_name, field_uuid = SprintOpt.sprint_field_add('option', data_storage, opt)

        with step('添加重名选项值'):
            opt = [{"value": "test_1"}, {'value': 'test_2'}, {'value': 'test_2'}]

            SprintOpt.sprint_field_edit('option', field_uuid, opt)
            # 应该是编辑失败，toast提示“选项名称已存在，请重新输入”  只有前端做了控制，后端未做

    @story('119444 编辑迭代属性：添加单选菜单选项值')
    def test_edit_sprint_field_option_value_add(self, sprint_init):
        """"""

    @story('119438 编辑迭代属性：编辑单选菜单选项值')
    def test_edit_sprint_field_edit_option_value(self, data_storage):
        with step('选择单选菜单，添加两个个选项值'):
            opt = {'options': [{"value": "test_1"}, {"value": "test_2"}]}

            field_name, field_uuid = SprintOpt.sprint_field_add('option', data_storage, opt)

        with step('修改选项值名称'):
            opt = [{"value": "示例test_1"}, {"value": "示范test_2"}]

            SprintOpt.sprint_field_edit('option', field_uuid, opt)

    @story('119440 编辑迭代属性：删除单选菜单选项值')
    def test_edit_sprint_field_del_option_value(self, data_storage):
        with step('前置条件'):
            # 存在单选菜单迭代属性
            opt = {'options': [{"value": "test_1"}, {"value": "test_2"}]}
            field_name, field_uuid = SprintOpt.sprint_field_add('option', data_storage, opt)

        with step('删除选项值test_2'):
            op = [{"value": "test_1"}]
            SprintOpt.sprint_field_edit('option', field_uuid, op)

        with step('删除选项值test_1'):
            op = []
            SprintOpt.sprint_field_edit('option', field_uuid, op, 801)

    @story('119441 编辑迭代属性：设置单选菜单属性值过程中删除选项值')
    def test_set_process_del_option_value(self, data_storage, sprint_init):
        SprintOpt.set_field_value(sprint_init, data_storage['option'], 'SyKyQN4S', 801)

    @story('119443 编辑迭代属性：属性名称重名校验')
    def test_add_sprint_field_name_same(self, data_storage):
        with step('前置条件'):
            # 已存在示例属性 A
            a_name, a_uuid = SprintOpt.sprint_field_add('text', data_storage)
            # 已存在示例属性 B
            b_name, b_uuid = SprintOpt.sprint_field_add('text', data_storage)

        with step('将示例属性B 的名称改成示例A属性的名称'):
            param = proj.sprint_field_value_up(b_uuid, a_name, types='text')[0]
            param.uri_args({'field_uuid': b_uuid})
            resp = self.call(sp.ProSprintFieldUpdate, param, status_code=409)

            resp.check_response('reason', 'NameExists')

    # 迭代属性-删除迭代属性
    @parametrize('types', ['text', 'user', 'multi_line_text', 'float', 'date', 'time', 'integer'])
    @story('119479 迭代属性：删除迭代属性')
    @story('119481 迭代配置-迭代属性：删除迭代属性（单选成员）')
    @story('119483 迭代配置-迭代属性：删除迭代属性（浮点数）')
    @story('119484 迭代配置-迭代属性：删除迭代属性（日期）')
    @story('119485 迭代配置-迭代属性：删除迭代属性（时间）')
    @story('119486 迭代配置-迭代属性：删除迭代属性（整数）')
    @story('119487 删除未设置属性默认值的迭代属性')
    @story('119488 删除已设置属性默认值的迭代属性')
    @story('119489 删除已在迭代设置属性值的迭代属性')
    @story('119482 迭代配置-迭代属性：删除迭代属性（多行文本）')
    def test_del_sprint_field(self, types, data_storage):
        param = data.field_delete()[0]

        if data_storage:
            param.uri_args({'field_uuid': data_storage[types]})
            self.call(sp.SprintFieldDelete, param)

    @story('119491 迭代属性：设置属性值过程中删除迭代属性')
    def test_set_process_del_filed(self, data_storage, sprint_init):
        param = proj.sprint_field_up()[0]
        param.uri_args({'sprint_uuid': sprint_init})
        param.uri_args({'field_uuid': data_storage['text']})
        param.json_update('field_value.value', 'test_1')
        resp = self.call(sp.SprintFieldUpdate, param, status_code=630)

        resp.check_response('errcode', 'NotFound.SprintField')
