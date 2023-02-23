"""
@Desc：全局配置-工作项属性新增
"""
from falcons.check import Checker, go
from falcons.com.nick import feature, story, fixture, step, parametrize
from main.actions import task
from main.api import project as prj
from main.params import conf
from main.params import data


@fixture(scope='module')
def field_storage():
    return []


def field_param(field_type: int, _storage, **kwargs):
    """属性类型参数"""

    param = conf.add_issue_type_field()[0]
    param.json_update('field.type', field_type)
    if kwargs:
        for key, value in kwargs.items():
            param.json['field'] |= {key: value}

    res = go(prj.FieldsAdd, param)
    res.check_response('field.built_in', False)

    _storage.append(res.value('field.uuid'))

    return res.value('field.uuid')


@feature('全局配置-工作项属性')
class TestIssueFieldAdd(Checker):

    @story('131484 新建出现时间类型的工作项属性（来源：状态类型（进行中）时间点：最后出现时间点')
    def test_appear_time_and_last_field_add(self, field_storage):
        """新增出现时间-最后出现时间属性"""
        field_param(45, field_storage, appear_time_settings={
            "field_uuid": "field005",
            "method": "last_at",
            "field_option_uuid": "6tj7uFts"
        })

    @story('131485 新建出现时间类型的工作项属性（来源：状态类型（进行中）时间点：最早出现时间点）')
    def test_appear_time_and_first_field_add(self, field_storage):
        """新增出现时间-最早出现时间属性"""
        field_param(45, field_storage, appear_time_settings={
            "field_uuid": "field005",
            "method": "first_at",
            "field_option_uuid": "6tj7uFts"
        })

    @story('131490 新建出现时间类型的工作项属性（来源：状态（实现中），时间点：最后出现时间点）')
    def test_appear_time_implement_last_field_add(self, field_storage):
        """新增出现时间-实现中-最后出现时间属性"""
        field_param(45, field_storage, appear_time_settings={
            "field_uuid": "field005",
            "method": "last_at",
            "field_option_uuid": "2C4dTo7S"
        })

    @story('131491 新建出现时间类型的工作项属性（来源：状态（实现中），时间点：最早出现时间点）')
    def test_appear_time_implement_first_field_add(self, field_storage):
        """新增出现时间-实现中-最早出现时间属性"""
        field_param(45, field_storage, appear_time_settings={
            "field_uuid": "field005",
            "method": "first_at",
            "field_option_uuid": "6tj7uFts"
        })

    @story('131493 新建单选菜单类型的工作项属性')
    def test_single_choice_field_add(self, field_storage):
        """新增单选菜单属性"""
        field_param(1, field_storage, options=[
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

    @story('131497 新建多选菜单类型的工作项属性')
    def test_multi_choice_field_add(self, field_storage):
        """新增多选菜单属性"""

        with step('点击「新建工作项属性」'):
            field_uuid = field_param(16, field_storage, options=[
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

        with step('点击「添加属性到工作项类型」，查看工作项自定义属性'):
            stamp = task.team_stamp({'field': 0})
            fields = [f['uuid'] for f in stamp['field']['fields'] if f['built_in'] == False]

            assert field_uuid in fields

        with step('进入项目A-项目配置-工作项类型-工作项类型X-属性与视图， 点击「添加工作项属性」'):
            '同上'

        with step('进入我的工作台-筛选器'):
            '同上'

        with step('进入我的工作台-筛选器-更多-导出工作项'):
            '同上'

    @story('131494 新建单选成员类型的工作项属性')
    def test_single_member_field_add(self, field_storage):
        """新增单选成员属性"""
        field_param(8, field_storage)

    @story('131498 新建多选成员类型的工作项属性')
    def test_multi_member_field_add(self, field_storage):
        """新增多选成员属性"""
        field_param(13, field_storage)

    @story('131495 新建单选迭代类型的工作项属性')
    def test_single_sprint_field_add(self, field_storage):
        """新增单选迭代属性"""
        field_param(7, field_storage)

    @story('131492 新建单行文本类型的工作项属性')
    def test_single_text_field_add(self, field_storage):
        """新增单行文本属性"""

        with step('点击「新建工作项属性」'):
            field_uuid = field_param(2, field_storage)

        with step('点击「添加属性到工作项类型」，查看工作项自定义属性'):
            stamp = task.team_stamp({'field': 0})
            fields = [f['uuid'] for f in stamp['field']['fields'] if f['built_in'] == False]

            assert field_uuid in fields

        with step('进入项目A-项目配置-工作项类型-工作项类型X-属性与视图， 点击「添加工作项属性」'):
            '同上'

        with step('进入我的工作台-筛选器'):
            '同上'

        with step('进入我的工作台-筛选器-更多-导出工作项'):
            '同上'

    @story('131496 新建多行文本类型的工作项属性')
    def test_multi_text_field_add(self, field_storage):
        """新增多行文本属性"""
        field_param(15, field_storage)

    @story('131499 新建多选项目类型的工作项属性')
    def test_multi_proj_field_add(self, field_storage):
        """新增多选项目属性"""
        field_param(50, field_storage)

    @story('131500 新建浮点数类型的工作项属性')
    def test_float_field_add(self, field_storage):
        """新增浮点数类型属性"""
        field_param(4, field_storage)

    @story('131502 新建间隔时间类型的工作项属性（来源：状态-日期与时间，时间点：最早出现时间）')
    def test_interval_time_and_early_field_add(self, field_storage):
        """新增间隔时间-最早出现时间属性"""
        field_param(40, field_storage, step_settings={
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

    @story('131505 新建间隔时间类型的工作项属性（来源：状态类型-日期与时间，时间点：最后出现时间）')
    def test_interval_time_and_last_field_add(self, field_storage):
        """新增间隔时间-最后出现时间属性"""
        field_param(4, field_storage, step_settings={
            "step_start": {
                "field_type": 12,
                "field_uuid": "field005",
                "method": "last_at",
                "field_option_uuid": "XqxRFzZN"
            },
            "step_end": {
                "field_type": 12,
                "field_uuid": "field005",
                "method": "last_at",
                "field_option_uuid": "Nox3euh7"
            }
        })

    @story('131507 新建日期类型的工作项属性')
    def test_date_field_add(self, field_storage):
        """新增日期类型属性"""
        field_param(5, field_storage)

    @story('131508 新建时间类型的工作项属性')
    def test_time_field_add(self, field_storage):
        """新增时间类型属性"""
        field_param(6, field_storage)

    @story('131509 新建属性选项停留次数类型的工作项属性（单选属性选择「单选菜单」类型）')
    def test_stay_times_field_add(self, field_storage):
        """新增停留次数类型属性"""
        field_param(41, field_storage, stay_settings={
            "field_type": 1,
            "field_uuid": "field012",
            "field_option_uuid": "Drzwx1Lz"
        })

    @story('131515 新建整数类型的工作项属性')
    def test_int_field_add(self, field_storage):
        """新增整数类型属性"""
        field_param(3, field_storage)

    @story('删除配置中心-工作项属性')
    @story('T131337 配置中心-工作项属性：删除工作项属性（没有被项目使用）')
    @parametrize('param', data.field_delete())
    def test_config_field_delete(self, param, field_storage):
        # stamp = task.team_stamp({'field': 0})
        # fields = [f['uuid'] for f in stamp['field']['fields'] if f['built_in'] == False]

        if field_storage:
            for f in field_storage:
                param.uri_args({'field_uuid': f})
                self.call(prj.FieldDelete, param, status_code=[200, 801])
