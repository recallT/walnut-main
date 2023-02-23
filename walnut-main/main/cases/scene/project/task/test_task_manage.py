"""
@File    ：test_task_manage.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/1
@Desc    ：任务管理场景测试用例
"""
from falcons.check import Checker
from falcons.com.nick import feature, story, parametrize, fixture, step
from falcons.helper import mocks

from main.actions.sprint import SprintAction
from main.actions.task import TaskAction
from main.api import task as api
from main.params import task as p
from main.params.const import ACCOUNT


@fixture(scope='module')
def task():
    """预先创建一条测试任务"""
    return TaskAction.new_issue()[0]


@fixture(scope='module')
def sprint():
    """预先创建迭代"""
    return SprintAction.sprint_add()


@fixture(scope='module', autouse=True)
def del_task(task):
    """删除测试任务"""
    yield
    TaskAction.del_task(task)


@feature('任务管理')
class TestTaskManage(Checker):
    """"""

    @story('134475 任务详情-属性：编辑「标题」')
    @parametrize('param', p.task_update_name())
    def test_edit_task_title(self, param, task):
        with step('成员A清空工作项标题'):
            param.json_update('tasks[0].uuid', task)
            param.json_update('tasks[0].name', '')
            param.json_update('tasks[0].summary', '')

            res = self.call(api.TaskUpdate3, param)
            res.check_response('bad_tasks[0].code', 400)
            res.check_response('bad_tasks[0].type', 'InvalidParameter')

        with step('成员A修改工作项标题为：示例任务'):
            param.json_update('tasks[0].name', '示例任务')
            param.json_update('tasks[0].summary', '示例任务')

            self.call(api.TaskUpdate3, param)

    @story('147779 任务详情-属性：编辑「标题」（输入长文本）')
    @parametrize('param', p.task_update_name())
    def test_long_task_name(self, param, task):
        """"""
        param.json_update('tasks[0].uuid', task)

        self.call(api.TaskUpdate3, param)

    @story('134476 任务详情-属性：编辑「负责人」')
    @parametrize('param', p.task_detail_edit())
    def test_edit_task_principal(self, param, task):
        param.json_update('tasks[0].uuid', task)
        param.json['tasks'][0] |= {'assign': ACCOUNT.user.owner_uuid}
        self.call(api.TaskUpdate3, param)

    @story('134478 任务详情-属性：编辑「所属迭代」（非必填）')
    @story('143372 任务详情-属性：编辑必填项「所属迭代」')
    @parametrize('param', p.task_detail_edit())
    def test_edit_task_sprint(self, param, task, sprint):
        with step('成员A修改「示例任务」的「所属迭代」为「示例迭代1」'):
            param.json_update('tasks[0].uuid', task)
            param.json['tasks'][0] |= {'field_values': [
                {
                    "field_uuid": "field011",
                    "type": 7,
                    "value": sprint
                }
            ]}
            self.call(api.TaskUpdate3, param)

        with step('点击「移出迭代」'):
            param.json['tasks'][0] |= {'field_values': [
                {
                    "field_uuid": "field011",
                    "type": 7,
                    "value": None
                }
            ]}
            self.call(api.TaskUpdate3, param)

    @story('134479 任务详情-属性：编辑「优先级」')
    @story('162195 任务详情-属性：关键属性「优先级」展示')
    @parametrize('param', p.task_detail_edit())
    def test_edit_task_priority(self, param, task):
        with step('修改优先级为 较高'):
            pri_uuid = TaskAction.task_field_value_uuid('优先级', '较高')

            param.json_update('tasks[0].uuid', task)
            param.json['tasks'][0] |= {"field_values": [
                {
                    "field_uuid": "field012",
                    "type": 1,
                    "value": pri_uuid
                }
            ]}
            self.call(api.TaskUpdate3, param)

    @story('143376 任务详情-属性：编辑非必填项发布日期')
    @parametrize('param', p.task_update())
    def test_edit_task_release_date(self, param, task):
        with step('存在任务A包含非必填属性-发布日期'):
            prm = {"field_uuid": "field036", "required": False}
            res = TaskAction.task_add_field(prm)

            res.check_response('field_config.field_uuid', 'field036')

        with step('修改发布日期'):
            param.json_update('tasks[0].uuid', task)
            param.json['tasks'][0] |= {"field_values": [
                {
                    "field_uuid": "field036",
                    "type": 5,
                    "value": mocks.day_timestamp()
                }
            ]}
            self.call(api.TaskUpdate3, param)

        with step('清空「任务A」的「发布日期」属性值'):
            param.json['tasks'][0] |= {"field_values": [
                {
                    "field_uuid": "field036",
                    "type": 5,
                    "value": None
                }
            ]}
            self.call(api.TaskUpdate3, param)

    @story('143366 任务详情-属性：编辑非必填截止日期')
    @story('143401 任务详情-属性：编辑非必填截止日期')
    @parametrize('param', p.task_update())
    def test_edit_task_deadline_date(self, param, task):
        param.json_update('tasks[0].uuid', task)
        param.json['tasks'][0] |= {"field_values": [
            {
                "field_uuid": "field013",
                "type": 5,
                "value": mocks.day_timestamp()
            }
        ]}
        self.call(api.TaskUpdate3, param)

    @story('148526 任务详情-属性：删除截止日期属性（截止日期已填）')
    @parametrize('param', p.task_update())
    def test_del_deadline_date(self, param, task):
        """"""
        param.json_update('tasks[0].uuid', task)
        param.json['tasks'][0] |= {"field_values": [
            {
                "field_uuid": "field013",
                "type": 5,
                "value": None
            }
        ]}
        self.call(api.TaskUpdate3, param)

        with step('查看任务详情'):
            resp = TaskAction.task_info(task)
            resp.check_response('deadline', None)

    @story('143375 任务详情-属性：编辑必填项是否线上缺陷')
    @parametrize('param', p.task_update())
    def test_edit_task_online_bug(self, param, task):
        """编辑是否线上缺陷"""

        with step('存在任务A包含必填属性-是否线上缺陷'):
            bug_uuid = TaskAction.task_field_value_uuid('是否线上缺陷', '否')

            prm = {"field_uuid": "field031", "required": False}
            res = TaskAction.task_add_field(prm)

            res.check_response('field_config.field_uuid', 'field031')

        with step('「是否线上缺陷」为「否」'):
            param.json_update('tasks[0].uuid', task)
            param.json['tasks'][0] |= {"field_values": [
                {
                    "field_uuid": "field031",
                    "type": 1,
                    "value": bug_uuid
                }
            ]}
            self.call(api.TaskUpdate3, param)

    @story('任务详情-属性：修改「负责人」为长名称负责人')
    def test_modify_long_name_assigner(self):
        """"""

    @story('134446 关注者：添加关注者')
    @story('134441 任务详情-关注者：点击关注')
    @parametrize('param', p.watchers_opt())
    def test_add_watchers(self, param, task):
        param.uri_args({'task_uuid': task})

        self.call(api.WatchersAdd, param)

    @story('134447 关注者：移除关注者')
    @story('134445 任务详情-关注者：点击取消关注')
    @parametrize('param', p.watchers_opt())
    def test_delete_watchers(self, param, task):
        param.uri_args({'task_uuid': task})

        self.call(api.WatchersDelete, param)
