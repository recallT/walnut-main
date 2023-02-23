"""
@Desc：项目设置-任务-工作项工作流-步骤属性
@Author  ：zhangweiyu@ones.ai
"""
import time
from falcons.check import Checker, go
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture, step, parametrize

from main.actions.task import TaskAction
from main.api import project
from main.api.issue import PostActionUpdate
from main.helper.extra import Extra
from main.params import issue as ise
from main.params import com
from . import get_start_step, options, add_custom_field, delete_custom_field


@fixture(scope='module', autouse=True)
def add_project():
    # 创建一个单独项目
    time.sleep(2)
    creator = Extra(ApiMeta)
    project_uuid = creator.new_project(f'ApiTest-Task-SP')
    return project_uuid


@fixture(scope='module', autouse=True)
def del_project(add_project):
    yield
    # 清除项目数据
    creator = Extra(ApiMeta)
    creator.del_project(add_project)


@feature('项目设置-步骤-属性')
class TestPrjTaskStepProperties(Checker):
    def add_step_field(self, start_step, add_field: dict, is_edit=False) -> dict:
        '''步骤-开始任务-添加属性'''
        if not is_edit:
            start_step['fields'].append(add_field)
        else:
            # 如果是修改操作，先清除field，再添加修后的field
            old_fields = [f for f in start_step['fields'] if f['field_uuid'] != add_field['field_uuid']]
            start_step['fields'] = old_fields + [add_field]
        param = ise.update_step_field(start_step['uuid'],
                                      start_step['issue_type_uuid'],
                                      start_step['project_uuid'],
                                      start_step['fields'])[0]
        param.uri_args({"project_uuid": start_step['project_uuid'],
                        "issue_type_uuid": start_step['issue_type_uuid'],
                        "transition_uuid": start_step['uuid']})
        r = self.call(PostActionUpdate, param)
        fields = [f for f in r.json()['transition']['fields'] if f['field_uuid'] == add_field['field_uuid']]
        assert fields
        return fields[0]

    @story('T117900 任务-步骤属性：添加步骤属性（故事点）')
    @story('T117899 子任务-步骤属性：添加步骤属性（故事点）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_field032(self, add_project, typ):

        add_field_config = {
            "field_uuid": "field032",
            "default_value": None,
            "required": False
        }
        with step('前置处理：添加工作项属性-故事点'):
            TaskAction.task_add_field(add_field_config, issue_types=typ,
                                      project_uuid=add_project)
        with step('步骤"开始任务"-添加属性-故事点'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            f = self.add_step_field(start_step,
                                    add_field_config)
            assert not f['required']
            assert not f['default_value']
            assert f['type'] == 4
            assert f['can_delete']

    @story('T117942 任务-步骤属性：添加步骤属性（进度）')
    @story('T117941 子任务-步骤属性：添加步骤属性（进度）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_field033(self, add_project, typ):
        add_field_config = {
            "field_uuid": "field033",
            "default_value": None,
            "required": False
        }
        with step('前置处理：添加工作项属性-进度'):
            ...
        with step('步骤"开始任务"-添加属性-进度'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            f = self.add_step_field(start_step, add_field_config)
            assert not f['required']
            assert not f['default_value']
            assert f['type'] == 4
            assert f['can_delete']

    @story('T118001 任务-步骤属性：添加步骤属性（预估工时）')
    @story('T118003 子任务-步骤属性：添加步骤属性（预估工时）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_field018(self, add_project, typ):
        add_field_config = {
            "field_uuid": "field018",
            "default_value": None,
            "required": False
        }
        with step('前置处理：添加工作项属性-预估工时'):
            ...
        with step('步骤"开始任务"-添加属性-预估工时'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            f = self.add_step_field(start_step,
                                    add_field_config)
            assert not f['required']
            assert not f['default_value']
            assert f['type'] == 4
            assert f['can_delete']

    @story('T117960 任务-步骤属性：添加步骤属性（所属产品）')
    @story('T117957 子任务-步骤属性：添加步骤属性（所属产品）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_field029(self, add_project, typ):
        add_field_config = {
            "field_uuid": "field029",
            "default_value": None,
            "required": False
        }
        with step('前置处理：添加工作项属性-所属产品'):
            ...
        with step('步骤"开始任务"-添加属性-所属产品'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            f = self.add_step_field(start_step, add_field_config)
            assert not f['required']
            assert not f['default_value']
            assert f['type'] == 44
            assert f['can_delete']

    @story('T117981 任务-步骤属性：添加步骤属性（文件）')
    @story('T117976 子任务-步骤属性：添加步骤属性（文件）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_tfresource(self, add_project, typ):
        add_field_config = {
            "field_uuid": "tf-resource",
            "default_value": None,
            "required": False
        }
        with step('前置处理：添加工作项属性-文件'):
            ...
        with step('步骤"开始任务"-添加属性-文件'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            f = self.add_step_field(start_step, add_field_config)
            assert not f['required']
            assert not f['default_value']
            assert f['type'] == -1
            assert f['can_delete']
            assert f['can_set_required']
            assert not f['can_set_default_value']

    @story('T117929 任务-步骤属性：添加步骤属性（关联 Wiki 页面）')
    @story('T117921 子任务-步骤属性：添加步骤属性（关联 Wiki 页面）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_tfwikipage(self, add_project, typ):
        add_field_config = {
            "field_uuid": "tf-wikipage",
            "default_value": None,
            "required": False
        }
        with step('前置处理：添加工作项属性-关联 Wiki 页面'):
            ...
        with step('步骤"开始任务"-添加属性-关联 Wiki 页面'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            f = self.add_step_field(start_step, add_field_config)
            assert not f['required']
            assert not f['default_value']
            assert f['type'] == -1
            assert f['can_delete']
            assert f['can_set_required']
            assert not f['can_set_default_value']

    @story('T118039 任务-步骤属性：添加步骤属性（自定义单选菜单）')
    @story('T118050 子任务-步骤属性：添加步骤属性（自定义单选菜单）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_custom_field_type1(self, add_project, typ):
        with step('前置条件：已存在属性-自定义单选菜单'):
            field_uuid = add_custom_field(field_type=1, project_uuid=add_project, issue_type_name=typ, options=options)
        with step('步骤添加属性：自定义单选菜单'):
            field_config = {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False
            }
            start_step = get_start_step(add_project, issue_type_name=typ)
            f = self.add_step_field(start_step, field_config)
            assert f == {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False,
                "type": 1,
                "can_set_required": True,
                "can_delete": True,
                "can_set_default_value": True
            }
        # with step('后置处理：清除属性-自定义单选菜单'):
        #     delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T118032 任务-步骤属性：添加步骤属性（自定义单行文本）')
    @story('T118028 子任务-步骤属性：添加步骤属性（自定义单行文本）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_custom_field_type2(self, add_project, typ):
        with step('前置条件：已存在属性-自定义单行文本'):
            field_uuid = add_custom_field(field_type=2, project_uuid=add_project, issue_type_name=typ)
        with step('步骤添加属性：自定义单行文本'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_config = {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False
            }
            f = self.add_step_field(start_step, field_config)
            assert f == {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False,
                "type": 2,
                "can_set_required": True,
                "can_delete": True,
                "can_set_default_value": True
            }
        # with step('后置处理：清除属性-自定义单行文本'):
        #     delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T118251 任务-步骤属性：添加步骤属性（自定义整数）')
    @story('T118243 子任务-步骤属性：添加步骤属性（自定义整数）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_custom_field_type3(self, add_project, typ):
        with step('前置条件：已存在属性-自定义整数'):
            field_uuid = add_custom_field(field_type=3, project_uuid=add_project, issue_type_name=typ)
        with step('步骤添加属性：自定义整数'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_config = {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False
            }
            f = self.add_step_field(start_step,
                                    field_config)
            assert f == {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False,
                "type": 3,
                "can_set_required": True,
                "can_delete": True,
                "can_set_default_value": True
            }
        # with step('后置处理：清除属性-自定义整数'):
        #     delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T118182 任务-步骤属性：添加步骤属性（自定义浮点数）')
    @story('T118195 子任务-步骤属性：添加步骤属性（自定义浮点数）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_custom_field_type4(self, add_project, typ):
        with step('前置条件：已存在属性-自定义浮点数'):
            field_uuid = add_custom_field(field_type=4, project_uuid=add_project, issue_type_name=typ)
        with step('步骤添加属性：自定义浮点数'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_config = {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False
            }
            f = self.add_step_field(start_step,
                                    field_config)
            assert f == {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False,
                "type": 4,
                "can_set_required": True,
                "can_delete": True,
                "can_set_default_value": True
            }
        # with step('后置处理：清除属性-自定义浮点数'):
        #     delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T118200 任务-步骤属性：添加步骤属性（自定义日期）')
    @story('T118204 子任务-步骤属性：添加步骤属性（自定义日期）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_custom_field_type5(self, add_project, typ):
        with step('前置条件：已存在属性-自定义日期'):
            field_uuid = add_custom_field(field_type=5, project_uuid=add_project, issue_type_name=typ)
        with step('步骤添加属性：自定义日期'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_config = {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False
            }
            f = self.add_step_field(start_step,
                                    field_config)
            assert f == {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False,
                "type": 5,
                "can_set_required": True,
                "can_delete": True,
                "can_set_default_value": True
            }
        # with step('后置处理：清除属性-自定义日期'):
        #     delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T118227 任务-步骤属性：添加步骤属性（自定义时间）')
    @story('T118217 子任务-步骤属性：添加步骤属性（自定义时间）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_custom_field_type6(self, add_project, typ):
        with step('前置条件：已存在属性-自定义时间'):
            field_uuid = add_custom_field(field_type=6, project_uuid=add_project, issue_type_name=typ)
        with step('步骤添加属性：自定义时间'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_config = {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False
            }
            f = self.add_step_field(start_step,
                                    field_config)
            assert f == {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False,
                "type": 6,
                "can_set_required": True,
                "can_delete": True,
                "can_set_default_value": True
            }
        # with step('后置处理：清除属性-自定义时间'):
        #     delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T118084 任务-步骤属性：添加步骤属性（自定义单选迭代）')
    @story('T118078 子任务-步骤属性：添加步骤属性（自定义单选迭代）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_custom_field_type7(self, add_project, typ):
        with step('前置条件：已存在属性-自定义单选迭代'):
            field_uuid = add_custom_field(field_type=7, project_uuid=add_project, issue_type_name=typ)
        with step('步骤添加属性：自定义单选迭代'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_config = {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False
            }
            f = self.add_step_field(start_step,
                                    field_config)
            assert f == {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False,
                "type": 7,
                "can_set_required": True,
                "can_delete": True,
                "can_set_default_value": True
            }
        # with step('后置处理：清除属性-自定义单选迭代'):
        #     delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T118069 任务-步骤属性：添加步骤属性（自定义单选成员）')
    @story('T118068 子任务-步骤属性：添加步骤属性（自定义单选成员）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_custom_field_type8(self, add_project, typ):
        with step('前置条件：已存在属性-自定义单选成员'):
            field_uuid = add_custom_field(field_type=8, project_uuid=add_project, issue_type_name=typ)
        with step('步骤添加属性：自定义单选成员'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_config = {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False
            }
            f = self.add_step_field(start_step,
                                    field_config)
            assert f == {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False,
                "type": 8,
                "can_set_required": True,
                "can_delete": True,
                "can_set_default_value": True
            }
        # with step('后置处理：清除属性-自定义单选成员'):
        #     delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T118152 任务-步骤属性：添加步骤属性（自定义多选成员）')
    @story('T118138 子任务-步骤属性：添加步骤属性（自定义多选成员）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_custom_field_type13(self, add_project, typ):
        with step('前置条件：已存在属性-自定义多选成员'):
            field_uuid = add_custom_field(field_type=13, project_uuid=add_project, issue_type_name=typ, options=options)
        with step('步骤添加属性：自定义多选成员'):
            field_config = {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False
            }
            start_step = get_start_step(add_project, issue_type_name=typ)
            f = self.add_step_field(start_step,
                                    field_config)
            assert f == {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False,
                "type": 13,
                "can_set_required": True,
                "can_delete": True,
                "can_set_default_value": True
            }
        # with step('后置处理：清除属性-自定义多选成员'):
        #     delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T118111 任务-步骤属性：添加步骤属性（自定义多行文本）')
    @story('T118115 子任务-步骤属性：添加步骤属性（自定义多行文本）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_custom_field_type15(self, add_project, typ):
        with step('前置条件：已存在属性-自定义多行文本'):
            field_uuid = add_custom_field(field_type=15, project_uuid=add_project, issue_type_name=typ)
        with step('步骤添加属性：自定义多行文本'):
            field_config = {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False
            }
            start_step = get_start_step(add_project, issue_type_name=typ)
            f = self.add_step_field(start_step,
                                    field_config)
            assert f == {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False,
                "type": 15,
                "can_set_required": True,
                "can_delete": True,
                "can_set_default_value": True
            }
        # with step('后置处理：清除属性-自定义多行文本'):
        #     delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T118121 任务-步骤属性：添加步骤属性（自定义多选菜单）')
    @story('T118125 子任务-步骤属性：添加步骤属性（自定义多选菜单）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_custom_field_type16(self, add_project, typ):
        with step('前置条件：已存在属性-自定义多选菜单'):
            field_uuid = add_custom_field(field_type=16, project_uuid=add_project, issue_type_name=typ, options=options)
        with step('步骤添加属性：自定义多选菜单'):
            field_config = {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False
            }
            start_step = get_start_step(add_project, issue_type_name=typ)
            f = self.add_step_field(start_step, field_config)
            assert f == {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False,
                "type": 16,
                "can_set_required": True,
                "can_delete": True,
                "can_set_default_value": True
            }
        # with step('后置处理：清除属性-自定义多选菜单'):
        #     delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T118165 任务-步骤属性：添加步骤属性（自定义多选项目）')
    @story('T118169 子任务-步骤属性：添加步骤属性（自定义多选项目）')
    @parametrize('typ', ('任务', '子任务'))
    def test_add_step_property_custom_field_type50(self, add_project, typ):
        with step('前置条件：已存在属性-自定义多选项目'):
            field_uuid = add_custom_field(field_type=50, project_uuid=add_project, issue_type_name=typ, options=options)
        with step('步骤添加属性：自定义多选项目'):
            field_config = {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False
            }
            start_step = get_start_step(add_project, issue_type_name=typ)
            f = self.add_step_field(start_step, field_config)
            assert f == {
                "field_uuid": field_uuid,
                "default_value": None,
                "required": False,
                "type": 50,
                "can_set_required": True,
                "can_delete": True,
                "can_set_default_value": True
            }
        # with step('后置处理：清除属性-自定义多选项目'):
        #     delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T117755 任务-步骤属性：编辑列表属性默认值及必填项')
    @story('T117762 子任务-步骤属性：编辑列表属性默认值及必填项')
    @parametrize('typ', ('任务', '子任务'))
    def test_edit_step_property_field012(self, add_project, typ):
        with step('前置条件：步骤已添加属性"优先级"'):
            field_config = {
                "field_uuid": "field012",
                "default_value": None,
                "required": False
            }
            start_step = get_start_step(add_project, issue_type_name=typ)
            self.add_step_field(start_step, field_config)
        with step('编辑步骤属性"优先级"'):
            # 获取优先级其中一个选项：最高
            ts_param = com.gen_stamp({"field": 0})
            res = go(project.TeamStampData, ts_param).json()
            field012_options = [field for field in res['field']['fields'] if field['uuid'] == 'field012'][0]['options']
            edit_field_config = {
                "field_uuid": "field012",
                "default_value": field012_options[0]['uuid'],
                "required": True
            }
            f = self.add_step_field(start_step, edit_field_config, is_edit=True)
            assert f == {
                "field_uuid": "field012",
                "default_value": field012_options[0]['uuid'],
                "required": True,
                "type": 1,
                "can_set_required": True,
                "can_delete": True,
                "can_set_default_value": True
            }
