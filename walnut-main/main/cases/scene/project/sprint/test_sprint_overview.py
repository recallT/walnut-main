"""
@Desc：迭代管理-迭代概览
"""
import time
from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, step, parametrize
from falcons.helper import mocks
from main.actions.sprint import SprintAction
from main.actions.task import TaskAction
from main.api import sprint, task as ts
from main.api.project import ProjectStamp
from main.api.sprint import SprintAdd, SprintUpdate
from main.params import proj, data, task
from main.params.const import ACCOUNT
from main.params.proj import sprint_goal, proj_stamp


@fixture(scope='module')
def sprint_init():
    sprint_uuid = SprintAction.sprint_add()

    status_uuid: list = SprintAction.sprint_status(sprint_uuid)  # 状态类型的uuid['未开始', '进行中', '已完成']

    return {'sp_uuid': sprint_uuid, 'st_uuid': status_uuid}


@fixture(scope='module')
def _uuid_data():
    """存放uuid"""
    return []


@feature('迭代管理-迭代组件')
class TestSprintComponent(Checker):

    def get_sprint_info(self, s_init):
        """获取迭代信息"""
        not_start, process, completed = s_init['st_uuid'][0], s_init['st_uuid'][1], s_init['st_uuid'][2]

        return not_start, process, completed

    @story('119293 迭代概览-当前阶段：当前阶段为已完成，更改迭代阶段（已完成 -> 进行中）')
    def test_up_sprint_stage_1(self, sprint_init):
        not_start, process, completed = self.get_sprint_info(sprint_init)

        with step('将迭代状态 未开始 变更成：已完成'):
            param = proj.sprint_status_up(['to_do', 'done'], [not_start, completed],
                                          sprint_init['sp_uuid'])[0]
            param.json_update('sprint_statuses[1].is_current_status', True)
            self.call(sprint.SprintStatusUpdate, param)

        with step('将迭代状态 已完成 变更成：进行中'):
            parm = proj.sprint_status_up(['done', 'in_progress'], [completed, process], sprint_init['sp_uuid'])[0]
            parm.json_update('sprint_statuses[1].is_current_status', True)
            self.call(sprint.SprintStatusUpdate, parm)

        with step('修改实际开始日期'):
            parm.json_update('sprint_statuses[1].actual_start_time', mocks.day_timestamp(0.5))
            self.call(sprint.SprintStatusUpdate, parm)

    @story('119287 迭代概览-当前阶段：当前阶段为进行中，更改迭代阶段（进行中 -> 未开始）')
    def test_up_sprint_stage_2(self, sprint_init):
        not_start, process, completed = self.get_sprint_info(sprint_init)

        with step('将迭代状态 进行中 变更成：未开始'):
            param = proj.sprint_status_up(['in_progress', 'to_do'], [process, not_start],
                                          sprint_init['sp_uuid'])[0]
            param.json_update('sprint_statuses[1].is_current_status', True)
            self.call(sprint.SprintStatusUpdate, param)

    @story('119292 迭代概览-当前阶段：当前阶段为未开始，更改迭代阶段（未开始 -> 已完成）')
    def test_up_sprint_stage_not_start_to_completed(self, sprint_init):
        not_start, process, completed = self.get_sprint_info(sprint_init)

        with step('将迭代状态 未开始 变更成：已完成'):
            param = proj.sprint_status_up(['to_do', 'done'], [not_start, completed],
                                          sprint_init['sp_uuid'])[0]
            param.json_update('sprint_statuses[1].is_current_status', True)
            self.call(sprint.SprintStatusUpdate, param)

    @story('119294 迭代概览-当前阶段：当前阶段为已完成，更改迭代阶段（已完成 -> 未开始）')
    def test_up_sprint_stage_completed_to_not_start(self, sprint_init):
        not_start, process, completed = self.get_sprint_info(sprint_init)

        with step('将迭代状态 已完成 变更成：未开始'):
            param = proj.sprint_status_up(['done', 'to_do'], [completed, not_start],
                                          sprint_init['sp_uuid'])[0]
            param.json_update('sprint_statuses[1].is_current_status', True)
            self.call(sprint.SprintStatusUpdate, param)

    @story('119290 迭代概览-当前阶段：当前阶段为进行中，更改迭代阶段（自定义阶段 <- 进行中）')
    def test_up_sprint_stage_customize_to_process(self, sprint_init):
        not_start, process, completed = self.get_sprint_info(sprint_init)

        with step('将迭代状态 自定义 变更成：进行中'):
            param = proj.sprint_status_up(['done', 'process'], [completed, process],
                                          sprint_init['sp_uuid'])[0]
            param.json_update('sprint_statuses[1].is_current_status', True)
            self.call(sprint.SprintStatusUpdate, param)

    @story('119289 迭代概览-当前阶段：当前阶段为进行中，更改迭代阶段（进行中 -> 自定义阶段）')
    def test_up_sprint_stage_process_to_customize(self, sprint_init):
        not_start, process, completed = self.get_sprint_info(sprint_init)

        with step('将迭代状态 进行中 变更成：自定义'):
            param = proj.sprint_status_up(['process', 'done'], [process, completed],
                                          sprint_init['sp_uuid'])[0]
            param.json_update('sprint_statuses[1].is_current_status', True)
            self.call(sprint.SprintStatusUpdate, param)

    @story('119288 迭代概览-当前阶段：当前阶段为进行中，更改迭代阶段（进行中 -> 已完成）')
    def test_up_sprint_stage_5(self, sprint_init):
        not_start, process, completed = self.get_sprint_info(sprint_init)

        with step('将迭代状态 进行中 变更成：未开始'):
            param = proj.sprint_status_up(['in_progress', 'done'], [process, completed],
                                          sprint_init['sp_uuid'])[0]
            param.json_update('sprint_statuses[1].is_current_status', True)
            self.call(sprint.SprintStatusUpdate, param)

    @story('119302 迭代概览-当前阶段：修改日期')
    @parametrize('param', proj.sprint_update())
    def test_up_date(self, param, sprint_init):
        with step('点击「未开始」计划开始日期, 选择日期'):
            param.json_update('sprints[0].uuid', sprint_init['sp_uuid'])
            self.call(sprint.SprintUpdate, param)

    @story('119326 迭代概览-迭代信息：变更迭代负责人')
    @parametrize('param', proj.sprint_update())
    def test_up_principal(self, param, sprint_init):
        param.json_update('sprints[0].uuid', sprint_init['sp_uuid'])
        param.json['sprints'][0] |= {"assign": ACCOUNT.user.owner_uuid}
        res = self.call(sprint.SprintUpdate, param)

        res.check_response('sprints[0].assign', ACCOUNT.user.owner_uuid)

    @story('119317 迭代概览-迭代属性：修改迭代属性（单选菜单）')
    @parametrize('param', proj.sprint_field_up())
    def test_up_sprint_field(self, param, sprint_init):
        with step('前置条件'):
            # 迭代属性列表已添加单选菜单类型属性
            prm = proj.sprint_field_add('option')[0]
            res = self.call(sprint.SprintFieldAdd, prm)

            field_uuid = res.value('field.uuid')
            opt_uuid = [v['uuid'] for v in res.value('field.options')]

        with step('属性值修改'):
            param.uri_args({'sprint_uuid': sprint_init['sp_uuid']})
            param.uri_args({'field_uuid': field_uuid})
            param.json_update('field_value.value', opt_uuid[0])

            self.call(sprint.SprintFieldUpdate, param)

        with step('清除创建的迭代属性数据'):
            pram = data.field_delete()[0]
            pram.uri_args({'field_uuid': field_uuid})
            self.call(sprint.SprintFieldDelete, pram)

    @story('119327 迭代概览-迭代信息：变更迭代计划周期')
    @parametrize('param', proj.sprint_update())
    def test_up_sprint_plan(self, param, sprint_init):
        start_time = mocks.day_timestamp(0.5)

        with step('迭代计划周期变更'):
            param.json_update('sprints[0].uuid', sprint_init['sp_uuid'])
            param.json_update('sprints[0].start_time', start_time)
            res = self.call(sprint.SprintUpdate, param)

            res.check_response('sprints[0].uuid', sprint_init['sp_uuid'])

    @story('119346 迭代概览-阶段描述：修改迭代阶段描述信息（未开始）')
    def test_up_sprint_describe(self, sprint_init):
        status_u = SprintAction.sprint_status(sprint_init['sp_uuid'])

        with step('点击「未开始」描述信息。输入：XXX'):
            param = proj.sprint_status_up(['to_do'], [status_u[0]], sprint_init['sp_uuid'])[0]
            param.json_update('sprint_statuses[0].desc_rich', '<p>未开始描述TEST</p>\n')
            self.call(sprint.SprintStatusUpdate, param)

    @story('119423 迭代列表：编辑迭代')
    @parametrize('param', proj.sprint_update())
    def test_sprint_list_up(self, param, sprint_init):
        p = [
            {
                "title": "update_sprint",
                "assign": ACCOUNT.user.owner_uuid,
                "start_time": mocks.day_timestamp(0.5),
                "end_time": mocks.day_timestamp(2),
                "period": "2w",
                "fields": [],
                "uuid": sprint_init['sp_uuid'],
                "statuses": []
            }
        ]
        param.json_update('sprints', p)
        param.uri_args({'sprint_uuid': sprint_init['sp_uuid']})

        res = self.call(sprint.SprintUpdate, param)

        res.check_response('sprints[0].project_uuid', ACCOUNT.project_uuid)

    @story('119350 迭代概览-燃尽图-工作项燃尽：查看燃尽图')
    @parametrize('param', proj.burn_down())
    def test_sprint_burn_down(self, param, sprint_init):
        """迭代燃尽图"""

        with step('前置条件'):
            task_uuid = TaskAction.new_issue()[0]

            # 工作项选择所属迭代
            parm = task.task_detail_edit()[0]
            parm.json_update('tasks[0].uuid', task_uuid)
            parm.json['tasks'][0] |= {'field_values': [
                {
                    "field_uuid": "field011",
                    "type": 7,
                    "value": sprint_init['sp_uuid']
                }
            ]}
            self.call(ts.TaskUpdate3, parm)

        with step('查看燃尽图基线和工作项数量曲线图'):
            time.sleep(4)
            param.uri_args({'sprint_uuid': sprint_init['sp_uuid']})
            self.call(sprint.BurnDown, param)

    @story('119983 迭代组件-所有工作项：规划单个工作项至迭代')
    @parametrize('param', task.task_detail_edit())
    def test_all_task_planning_sprint(self, param):
        """all工作项入口:单个工作项规划至迭代"""

        with step('前置条件'):
            t_uuid = TaskAction.new_issue()[0]  # 新建任务工作项
            s_uuid = SprintAction.sprint_add()  # 新建迭代

        with step('勾选示例需求-点击规划至迭代-选择迭代'):
            param.json_update('tasks', [{'uuid': t_uuid, 'sprint_uuid': s_uuid}])
            self.call(ts.TaskUpdate3, param)

        with step('查看示例任务的所属迭代属性值'):
            res = TaskAction.task_messages(t_uuid)

            res.check_response('messages[0].new_value', s_uuid)

    @story('120409 迭代组件-未规划工作项：规划单个工作项至迭代')
    @parametrize('param', task.task_detail_edit())
    def test_not_task_planning_sprint(self, param):
        """未规划工作入口:单个工作项规划至迭代"""

        with step('前置条件'):
            t_uuid = TaskAction.new_issue()[0]  # 新建任务工作项
            s_uuid = SprintAction.sprint_add()  # 新建迭代

        with step('勾选示例需求-点击规划至迭代-选择迭代'):
            param.json_update('tasks', [{'uuid': t_uuid, 'sprint_uuid': s_uuid}])
            self.call(ts.TaskUpdate3, param)

        with step('查看示例任务的所属迭代属性值'):
            res = TaskAction.task_messages(t_uuid)

            res.check_response('messages[0].new_value', s_uuid)

    @story("T23638 迭代计划管理-迭代计划组件：新建迭代")
    def test_sprint_add(self, _uuid_data):
        # 新建一个迭代，保存uuid
        response = SprintAction.sprint_add()
        _uuid_data.append(response)
        print("pass123", response)
        # 获取迭代列表
        param = proj_stamp()[0]
        param.uri_args({'project_uuid': ACCOUNT.project_uuid})
        res = self.call(ProjectStamp, param, is_print=False)
        result = res.value('sprint.sprints')
        sprint_uuid = [d['uuid'] for d in result]
        # 判断uuid是否在列表中
        assert _uuid_data[0] in sprint_uuid

    @story("T24254 迭代组件-迭代概览：编辑迭代描述")
    def test_sprint_dec(self, _uuid_data):
        with step("添加迭代描述"):
            uuid = _uuid_data[0]
            param = sprint_goal(uuid)[0]
            param.uri_args({'team_uuid': ACCOUNT.user.team_uuid, 'project_uuid': ACCOUNT.project_uuid})
            self.call(SprintAdd, param)

        with step("修改迭代描述"):
            param1 = sprint_goal(uuid)[0]
            param1.uri_args({'team_uuid': ACCOUNT.user.team_uuid, 'project_uuid': ACCOUNT.project_uuid})
            res = self.call(SprintUpdate, param1)
            param2 = param1.json['sprints']
            # 判断请求的goal(描述)与返回的goal是否一致
            res.check_response('sprints[0].goal', param2[0]['goal'])
