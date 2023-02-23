# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_step_task_properties.py
@Author  ：zhangyonghui@ones.ai
@Date    ：8/2/22 10:30 AM 
@Desc    ：
"""
from falcons.check import Checker
from falcons.com.nick import story, fixture, step, feature

from main.actions.task import TaskAction
from main.api import project as api, issue, project
from main.params import proj, task as t, conf, issue as i, data as d
from main.actions.issue import IssueAction as Ia
from main.params.issue import add_task_field


@fixture(scope='module', autouse=True)
def get_task_uuid():
    issue_type_uuid = TaskAction.issue_type_uuid()
    return issue_type_uuid


@fixture(scope='module', autouse=True)
def _del(admin_token):
    """还原步骤属性"""
    yield
    data = [{"field_uuid": "tf-comment", "default_value": "", "required": False}]

    TestProStepProperties().add_global_step_properties('tf-comment', field=data)


@feature('配置中心-任务工作流-步骤属性')
class TestProStepProperties(Checker):

    def add_global_step_properties(self, field_uuid, process_name='开始任务', **kwargs):
        """
        添加全局步骤属性
        :param token
        :param process_name 添加步骤属性流转过程的名称
        :param field_uuid 添加属性的uuid
        """
        issue_type = TaskAction.issue_type_uuid()[0]

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

    @story('T117903 步骤属性：添加步骤属性（故事点)')
    def test_global_sub_task_step_field032(self, get_task_uuid):
        with step('将故事点添加到工作项中'):
            Ia.add_field_into_issue(field_type=['field032'], issue_type=get_task_uuid)
        with step('添加步骤属性（故事点）'):
            self.add_global_step_properties('field032')

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_task_uuid[0], 'field032')

    @story('T118026 步骤属性：添加步骤属性（自定义单行文本）')
    def test_add_step_properties_single_line(self, get_task_uuid):
        with step('前置条件，添加自定义属性'):
            field_uuid = Ia.global_add_field(field_type=2, issue_type=get_task_uuid)
        with step('添加步骤属性选择（自定义单行文本）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118173 步骤属性：添加步骤属性（自定义多选项目）')
    def test_add_step_properties_more_choice_product(self, get_task_uuid):
        with step('前置条件，添加自定义属性'):
            field_uuid = Ia.global_add_field(field_type=50, issue_type=get_task_uuid)
        with step('添加步骤属性选择（自定义单行文本）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118181 步骤属性：添加步骤属性（自定义浮点数）')
    def test_add_step_properties_floating_point_number(self, get_task_uuid):
        with step('前置条件，添加自定义属性'):
            field_uuid = Ia.global_add_field(field_type=4, issue_type=get_task_uuid)
        with step('添加步骤属性选择（自定义单行文本）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118209 步骤属性：添加步骤属性（自定义日期）')
    def test_add_step_properties_date(self, get_task_uuid):
        with step('前置条件，添加自定义属性'):
            field_uuid = Ia.global_add_field(field_type=5, issue_type=get_task_uuid)
        with step('添加步骤属性选择（自定义单行文本）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118233 步骤属性：添加步骤属性（自定义时间）')
    def test_add_step_properties_time(self, get_task_uuid):
        with step('前置条件，添加自定义属性'):
            field_uuid = Ia.global_add_field(field_type=6, issue_type=get_task_uuid)
        with step('添加步骤属性选择（自定义单行文本）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118247 步骤属性：添加步骤属性（自定义整数）')
    def test_add_step_properties_integer(self, get_task_uuid):
        with step('前置条件，添加自定义属性'):
            field_uuid = Ia.global_add_field(field_type=3, issue_type=get_task_uuid)
        with step('添加步骤属性选择（自定义单行文本）'):
            self.add_global_step_properties(field_uuid)
        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(get_task_uuid[0], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)
