# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_step_sub_task_properties.py
@Author  ：zhangyonghui@ones.ai
@Date    ：2022/6/28 10:26 AM 
@Desc    ： 配置中心-工作项类型-子任务-工作流-步骤属性
"""

from falcons.check import Checker, go
from falcons.com.nick import story, fixture, step, feature, mark

from main.actions.task import TaskAction
from main.api import project as api, issue, project
from main.params import proj, task as t, conf, issue as i, data as d, com
from main.actions.issue import IssueAction as Ia
from main.params.issue import add_task_field


@fixture(scope='module', autouse=True)
def get_sub_task_uuid():
    issue_type_uuid = TaskAction.issue_type_uuid('子任务')
    return issue_type_uuid


@fixture(scope='module', autouse=True)
def _del(admin_token):
    """还原步骤属性"""
    yield
    data = [{"field_uuid": "tf-comment", "default_value": "", "required": False}]

    TestProStepProperties().add_global_step_properties('tf-comment', field=data)


@mark.smoke
@feature('配置中心-子任务工作流-步骤属性')
class TestProStepProperties(Checker):

    def add_global_step_properties(self, field_uuid, process_name='开始任务', **kwargs):
        """
        添加全局步骤属性
        :param process_name 添加步骤属性流转过程的名称
        :param field_uuid 添加属性的uuid
        """
        issue_type = TaskAction.issue_type_uuid(issue_types='子任务')[0]

        param = t.task_field(True)[0]
        param.json = {"issue_type": 0}
        stamp_resp = self.call(api.TeamStampData, param)

        process_uuid = [u['uuid'] for n in stamp_resp.value('issue_type.issue_types') if
                        n['uuid'] == issue_type for u in n['default_configs']['default_transitions'] if
                        u['name'] == process_name][0]

        prm = proj.global_step_properties_up(issue_type, process_uuid, field_uuid)[0]

        if kwargs:
            prm.json_update('transition.fields', kwargs['field'])

        res = self.call(api.GlobalStepPropertiesUpdate, prm)

        return res

    @story('117989 步骤属性：添加步骤属性（文件）-子任务')
    def test_global_step_file_add(self):
        self.add_global_step_properties('tf-resource')

    @story('T117879 步骤属性：添加步骤属性（登记工时）-子任务')
    def test_global_sub_task_step_register_hour_add(self):
        self.add_global_step_properties('tf-manhour')

    @story('T117939 步骤属性：添加步骤属性（进度）-子任务')
    def test_global_sub_task_step_schedule_add(self):
        self.add_global_step_properties('field033')

    @story('T117971 步骤属性：添加步骤属性（所属产品）-子任务')
    def test_global_sub_task_step_product_add(self):
        self.add_global_step_properties('field029')

    @story('T118010 步骤属性：添加步骤属性（预估工时）-子任务')
    def test_global_sub_task_step_estimate_hour_add(self):
        self.add_global_step_properties('field018')

    @story('T117906 步骤属性：添加步骤属性（故事点）-子任务')
    def test_global_sub_task_step_field032(self, get_sub_task_uuid):
        with step('将故事点添加到工作项中'):
            Ia.add_field_into_issue(field_type=['field032'], issue_type=get_sub_task_uuid)
        with step('添加步骤属性（故事点）'):
            self.add_global_step_properties('field032')
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_sub_task_uuid[0], 'field032')

    @story('T118072 步骤属性：添加步骤属性（自定义单选成员）-子任务')
    def test_global_sub_task_step_customize_add(self, get_sub_task_uuid):
        with step('前置条件'):
            field_uuid = Ia.global_add_field(field_type=8, issue_type=get_sub_task_uuid)
        with step('添加步骤属性选择（自定义单选成员）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_sub_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T117839 步骤属性：删除步骤属性-子任务')
    def test_global_step_delete(self):
        data = [{"field_uuid": "tf-comment", "default_value": "", "required": False}]

        self.add_global_step_properties('tf-comment', field=data)

    @story('T118038 步骤属性：添加步骤属性（自定义单选菜单）-子任务')
    def test_global_sub_task_step_customize_add1(self, get_sub_task_uuid):
        with step('前置条件'):
            # 新增工作项属性
            param = conf.add_issue_type_field()[0]
            param.json_update('field.type', 1)
            param.json_update('field.options', [{'value': "test", 'background_color': "#307fe2", 'color': "#fff"}])
            res = self.call(api.FieldsAdd, param)
            field_uuid = res.value('field.uuid')

            # 将新增属性添加到对应工作项
            Ia.add_field_into_issue(field_type=[field_uuid], issue_type=get_sub_task_uuid)

        with step('添加步骤属性选择（自定义单选成员）'):
            self.add_global_step_properties(field_uuid)

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_sub_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118038 步骤属性：添加步骤属性（自定义单选菜单）-子任务')
    def test_global_sub_task_step_customize_add1(self, get_sub_task_uuid):
        with step('前置条件'):
            # 新增工作项属性
            param = conf.add_issue_type_field()[0]
            param.json_update('field.type', 1)
            param.json_update('field.options', [{'value': "test", 'background_color': "#307fe2", 'color': "#fff"}])
            res = self.call(api.FieldsAdd, param)
            field_uuid = res.value('field.uuid')

            # 将新增属性添加到对应工作项
            Ia.add_field_into_issue(field_type=[field_uuid], issue_type=get_sub_task_uuid)
        with step('添加步骤属性选择（自定义单选成员）'):
            self.add_global_step_properties(field_uuid)

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_sub_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118122 步骤属性：添加步骤属性（自定义多选菜单））-子任务')
    def test_global_sub_task_step_check_menu_add(self, get_sub_task_uuid):
        with step('前置条件'):
            # 新增工作项属性 自定义多选菜单
            param = conf.add_issue_type_field()[0]
            param.json_update('field.type', 16)
            param.json_update('field.options', [{'value': "test", 'background_color': "#307fe2", 'color': "#fff"}])
            res = self.call(api.FieldsAdd, param)
            field_uuid = res.value('field.uuid')

            # 将新增属性添加到对应工作项
            Ia.add_field_into_issue(field_type=[field_uuid], issue_type=get_sub_task_uuid)

        with step('添加步骤属性选择（自定义单选成员）'):
            self.add_global_step_properties(field_uuid)

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_sub_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118095 步骤属性：添加步骤属性（自定义单选迭代）-子任务')
    def test_global_sub_task_step_radio_sprint(self, get_sub_task_uuid):
        with step('前置条件'):
            field_uuid = Ia.global_add_field(field_type=7, issue_type=get_sub_task_uuid)
        with step('添加步骤属性选择（自定义单选迭代）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_sub_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118112 步骤属性：添加步骤属性（自定义多行文本）-子任务')
    def test_global_sub_task_step_more_text(self, get_sub_task_uuid):
        with step('前置条件'):
            # 新增工作项属性 自定义多行文本
            param = conf.add_issue_type_field()[0]
            param.json_update('field.type', 15)
            param.json_update('field.options', [{'value': "test", 'background_color': "#307fe2", 'color': "#fff"}])
            res = self.call(api.FieldsAdd, param)
            field_uuid = res.value('field.uuid')

            # 将新增属性添加到对应工作项
            Ia.add_field_into_issue(field_type=[field_uuid], issue_type=get_sub_task_uuid)
        with step('添加步骤属性选择（自定义多行文本）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_sub_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118142 步骤属性：添加步骤属性（自定义多选成员）-子任务')
    def test_global_sub_task_step_check_member_add(self, get_sub_task_uuid):
        with step('前置条件'):
            # 新增工作项属性 自定义多选成员
            field_uuid = Ia.global_add_field(field_type=13, issue_type=get_sub_task_uuid)
        with step('添加步骤属性选择（自定义单选成员）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_sub_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T117932 步骤属性：添加步骤属性（关联 Wiki 页面）')
    def test_add_step_properties_wiki(self):
        self.add_global_step_properties('tf-wikipage')

    @story('T118020 步骤属性：添加步骤属性（自定义单行文本）')
    def test_add_step_properties_single_line(self, get_sub_task_uuid):
        with step('前置条件，添加自定义属性'):
            field_uuid = Ia.global_add_field(field_type=2, issue_type=get_sub_task_uuid)
        with step('添加步骤属性选择（自定义单行文本）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_sub_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118163 步骤属性：添加步骤属性（自定义多选项目）')
    def test_add_step_properties_more_choice_product(self, get_sub_task_uuid):
        with step('前置条件，添加自定义属性'):
            field_uuid = Ia.global_add_field(field_type=50, issue_type=get_sub_task_uuid)
        with step('添加步骤属性选择（自定义单行文本）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_sub_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118193 步骤属性：添加步骤属性（自定义浮点数）')
    def test_add_step_properties_floating_point_number(self, get_sub_task_uuid):
        with step('前置条件，添加自定义属性'):
            field_uuid = Ia.global_add_field(field_type=4, issue_type=get_sub_task_uuid)
        with step('添加步骤属性选择（自定义单行文本）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_sub_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118203 步骤属性：添加步骤属性（自定义日期）')
    def test_add_step_properties_date(self, get_sub_task_uuid):
        with step('前置条件，添加自定义属性'):
            field_uuid = Ia.global_add_field(field_type=5, issue_type=get_sub_task_uuid)
        with step('添加步骤属性选择（自定义单行文本）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_sub_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118226 步骤属性：添加步骤属性（自定义时间）')
    def test_add_step_properties_time(self, get_sub_task_uuid):
        with step('前置条件，添加自定义属性'):
            field_uuid = Ia.global_add_field(field_type=6, issue_type=get_sub_task_uuid)
        with step('添加步骤属性选择（自定义单行文本）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_sub_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118246 步骤属性：添加步骤属性（自定义整数）')
    def test_add_step_properties_integer(self, get_sub_task_uuid):
        with step('前置条件，添加自定义属性'):
            field_uuid = Ia.global_add_field(field_type=3, issue_type=get_sub_task_uuid)
        with step('添加步骤属性选择（自定义单行文本）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_sub_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T117758 步骤属性：编辑列表属性默认值及必填项')
    @story('T117787 步骤属性：检查添加步骤属性时设置属性默认值和必填项的表现')
    def test_add_step_properties_default_value(self):
        with step('前置条件，获取需要数据'):
            param = com.gen_stamp({"field": 0})
            fields = go(project.TeamStampData, param).value('field.fields')
            default_value = [f['options'][0]['uuid'] for f in fields if f['name'] == '优先级' and f['built_in']][0]

            field = [{
                "required": True,
                "field_uuid": "field012",
                "default_value": default_value
            },
                {
                    "field_uuid": "tf-comment",
                    "default_value": "",
                    "required": False
                }]
        with step('步骤属性：编辑列表属性默认值及必填项-优先级'):
            self.add_global_step_properties(field_uuid='field012', field=field)

    @story('T117812 步骤属性：列表排序')
    def test_sort_field_list(self):
        field = [{
            "required": True,
            "field_uuid": "field027",
            "default_value": None
        },
            {
                "required": True,
                "field_uuid": "field012",
                "default_value": None
            },
            {
                "field_uuid": "tf-comment",
                "default_value": "",
                "required": False
            }]
        self.add_global_step_properties(field_uuid='field012', field=field)

        with step('列表排序'):
            # 更换位置
            field[0], field[1] = field[1], field[0]
            self.add_global_step_properties(field_uuid='field012', field=field)
