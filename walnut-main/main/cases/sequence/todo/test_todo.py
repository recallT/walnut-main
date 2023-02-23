"""
@File    ：test_todo.py
@Author  ：zhangyonghui
@Email   ：zhangyonghui@ones.ai
@Date    ：2022/6/09
@Desc    ：待办事项
"""
from falcons.check import Checker
from falcons.com.nick import story, fixture, step, feature
from falcons.ops import generate_param

from main.actions.pro import PrjAction
from main.actions.sprint import SprintAction
from main.actions.task import TaskAction
from main.api import sprint
from main.api.task import TaskUpdate3, TaskAdd
from main.params.proj import update_deploy_relation_field
from main.params.task import task_relation_sprint


@fixture(scope='module', autouse=True)
def add_deploy_component():
    PrjAction.add_component('发布')
    PrjAction.add_component('待办事项')

    yield
    PrjAction.remove_prj_component('发布')
    PrjAction.remove_prj_component('待办事项')


@fixture(scope='module', autouse=True)
def todo_prepare():
    # 初始化创建一个迭代 一个发布 两个工作项
    sprint_uuid = SprintAction.sprint_add()
    deploy_uuid = PrjAction.add_deploy_task()
    task_a = TaskAction.new_issue()[0]
    task_b = TaskAction.new_issue(issue_type_name='需求')[0]

    data = {'sprint_uuid': sprint_uuid, 'deploy_uuid': deploy_uuid,
            'task_a': task_a, 'task_b': task_b
            }
    return data


@feature('项目组件-待办事项')
class TestProjToDo(Checker):

    @story('T119226 待办事项：新建迭代')
    @story('T41855 待办事项-迭代信息：删除迭代')
    def test_todo_add_sprint(self):
        with step('在待办事项中新增迭代'):
            sprint_uuid = SprintAction.sprint_add()
        with step("待办事项-迭代信息：删除迭代"):
            param = generate_param({}, is_project=True)[0]
            param.uri_args({'sprint_uuid': sprint_uuid})
            self.call(sprint.SprintDelete, param)

    @story('T119227 待办事项：新建发布')
    def test_todo_add_deploy(self):
        with step('在待办事项中新增发布'):
            PrjAction.add_deploy_task()

    @story('T119228 待办事项：新建工作项')
    @story('T41841 待办事项-新建工作项：新建工作项')
    def test_todo_add_task(self, todo_prepare):
        with step('新增工作项'):
            TaskAction.new_issue(issue_type_name='需求')

        with step('点击迭代A下的「+新建工作项」'):
            field_value = {
                'field_uuid': 'field011',  # 迭代属性
                'type': 7,
                'value': todo_prepare['sprint_uuid']  # 迭代UUID
            }
            param = TaskAction.new_issue(issue_type_name='需求', param_only=True)
            # 添加关联迭代字段属性
            param.json['tasks'][0]['field_values'].append(field_value)

            resp = self.call(TaskAdd, param)
            resp.check_response('tasks[0].sprint_uuid', todo_prepare['sprint_uuid'])

    @story('T119558 迭代信息-迭代故事点规模统计：检查操作工作项后故事点规模统计情况')
    def test_todo_sprint_story_info(self, todo_prepare):
        with step('创建迭代故事点的工作项'):
            with step('前置条件，在迭代中创建工作项'):
                field_value = {
                    'field_uuid': 'field011',  # 迭代属性
                    'type': 7,
                    'value': todo_prepare['sprint_uuid']  # 迭代UUID
                }
                field_story_value = {
                    "field_uuid": "field032",  # 故事点字段
                    "type": 4,
                    "value": 500000  # 故事点值
                }
                param = TaskAction.new_issue(issue_type_name='需求', param_only=True)
                # 添加关联迭代和故事点字段属性
                param.json['tasks'][0]['field_values'].append(field_value)
                param.json['tasks'][0]['field_values'].append(field_story_value)

                self.call(TaskAdd, param)
        with step('查看迭代规模'):
            resp = SprintAction.todo_sprint_info()
            resp.check_response('data.sprints[0].adviceScale', 0)
            # 与故事点值一直
            # resp.check_response('data.sprints[0].scale', 5)

    @story('待办事项-规划工作项：将迭代内的工作项拖拽至待规划')
    def test_sprint_drag_task(self, todo_prepare):
        with step('前置条件，在迭代中创建工作项'):
            field_value = {
                'field_uuid': 'field011',  # 迭代属性
                'type': 7,
                'value': todo_prepare['sprint_uuid']  # 迭代UUID
            }
            param = TaskAction.new_issue(issue_type_name='需求', param_only=True)
            # 添加关联迭代字段属性
            param.json['tasks'][0]['field_values'].append(field_value)

            resp = self.call(TaskAdd, param)
            resp.check_response('tasks[0].sprint_uuid', todo_prepare['sprint_uuid'])
            task_uuid = resp.value('tasks[0].uuid')
        with step('将工作项从迭代拖拽到待规划'):
            param = task_relation_sprint(task_uuid, None)[0]
            self.call(TaskUpdate3, param)

    @story('T119191 待办事项-规划工作项至迭代：拖拽规划至迭代')
    def test_task_drag_to_sprint(self, todo_prepare):
        with step('拖拽规划至迭代'):
            # 使用预先创建的任务A 拖拽到迭代中
            param = task_relation_sprint(todo_prepare['task_a'], todo_prepare['sprint_uuid'])[0]
            self.call(TaskUpdate3, param)

    @story('T119192 待办事项-规划工作项至发布：拖拽规划至发布')
    def test_task_drag_to_deploy(self, todo_prepare):
        with step('拖拽规划至发布A'):
            pam = update_deploy_relation_field(todo_prepare['task_b'], [todo_prepare['deploy_uuid']])[0]
            self.call(TaskUpdate3, pam)

        with step('拖拽到无关联发布'):
            task = TaskAction.new_issue(issue_type_name='需求')[0]
            pam = update_deploy_relation_field(task, [])[0]
            self.call(TaskUpdate3, pam)

    @story('T119557 迭代信息-迭代故事点规模建议：检查操作迭代后建议规模数据情况')
    def test_todo_story_sprint_value(self):
        with step('进入待办事项页面查看建议规模数据'):
            resp = SprintAction.todo_sprint_info()
            # 检查当前规模字段
            resp.check_response('data.sprints[0].adviceScale', 0)

    @story('T119224 待办事项：检查数据待办事项数据来源')
    def test_check_todo_list(self):
        # 查询待办事项数据源
        SprintAction.todo_sprint_info()
