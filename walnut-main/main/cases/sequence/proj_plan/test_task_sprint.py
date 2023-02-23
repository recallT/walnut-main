from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, step, mark
from falcons.helper import mocks
from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra
from main.actions.sprint import SprintAction
from main.actions.task import TaskAction
from main.api.project import ItemGraphql
from main.api.task import TaskUpdate3
from main.params.issue import update_issue_field, get_task_progress
from main.params.proj import get_task_info, get_sprint_related_ppm
from falcons.com.meta import ApiMeta


@fixture(scope='module', autouse=True)
def add_plan_component():
    # 1.先添加一个【项目计划】 组件
    PrjAction.add_component('项目计划')
    yield
    PrjAction.remove_prj_component('项目计划')


@fixture(scope='module', autouse=True)
def add_plan_task_sprint():
    # 添加 计划 任务 迭代数据
    sprint_uuid = SprintAction.sprint_add()

    ise = TaskAction.new_issue(issue_type_name='需求', is_batch=False)[0]

    plan_key = Ra.add_plans_or_milestones()

    return sprint_uuid, ise, plan_key


@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过')
@feature('项目计划-关联工作项或迭代管理 ')
class TestProjPlanTaskSprint(Checker):

    @story('T128829 关联迭代：新窗口打开')
    def test_relation_sprint_new_window(self):
        with step('前置条件，存在关联迭代的示例计划'):
            sprint_uuid = SprintAction.sprint_add()
            plan_key = Ra.add_plans_or_milestones()
            # 迭代关联项目计划
            Ra.external_activity(plan_key, sprint_uuid, ob_type='sprint')
        with step('查看迭代1迭代详情页面'):
            param = get_sprint_related_ppm(sprint_uuid)[0]
            resp = self.call(ItemGraphql, param)
            # 检查迭代关联计划
            resp.check_response('data.sprints[0].parentActivities[0].key', plan_key)

    @story('T128824 T130763 关联迭代：关联迭代下在子层级新建工作项')
    def test_relation_sprint_add_new_task(self):
        with step('存在计划“示例计划”已关联迭代1'):
            sprint_uuid = SprintAction.sprint_add()
            plan_key = Ra.add_plans_or_milestones()
            Ra.external_activity(plan_key, sprint_uuid, ob_type='sprint')
            issue_key = Ra.task_relation_plan_key(sprint_uuid)

        with step('在子层级新建工作项'):  # TODO 未完车
            print('')

    @story('T128825 关联迭代：快速更新关联迭代信息')
    def test_fast_update_relation_sprint_info(self):
        with step('存在计划“示例计划”已关联迭代1'):
            sprint_uuid = SprintAction.sprint_add()
            plan_key = Ra.add_plans_or_milestones()
            Ra.external_activity(plan_key, sprint_uuid, ob_type='sprint')
            sprint_key = Ra.task_relation_plan_key(sprint_uuid)

        with step('修改标题为“示例迭代1”'):
            Ra.fast_update_proj_plan_info("name", '示例迭代A' + mocks.num(), sprint_key)

        with step('移动鼠标点击编辑开始时间，结束时间”'):
            Ra.fast_update_proj_plan_info("start_time", mocks.day_timestamp(1), sprint_key)
            Ra.fast_update_proj_plan_info("end_time", mocks.day_timestamp(3), sprint_key)

    @story('T128827 关联迭代：拖拽更新迭代周期')
    def test_update_relation_sprint_time(self):
        with step('存在计划“示例计划”已关联迭代'):
            sprint_uuid = SprintAction.sprint_add()
            plan_key = Ra.add_plans_or_milestones()
            Ra.external_activity(plan_key, sprint_uuid, ob_type='sprint')
            sprint_key = Ra.task_relation_plan_key(sprint_uuid)
        with step('移动拖拽 开始时间”'):
            Ra.fast_update_proj_plan_info("start_time", mocks.day_timestamp(1), sprint_key)
        with step('移动拖拽 结束时间”'):
            Ra.fast_update_proj_plan_info("end_time", mocks.day_timestamp(3), sprint_key)

    @story('T128830 关联迭代：新建关联迭代')
    def test_add_new_relation_sprint(self):
        with step('前置条件，新增迭代'):
            sprint_uuid = SprintAction.sprint_add()
            plan_key = Ra.add_plans_or_milestones()

        with step('选择迭代x，点击确认'):
            Ra.external_activity(plan_key, sprint_uuid, ob_type='sprint')
            issue_key = Ra.task_relation_plan_key(sprint_uuid)
            response = Ra.connecred_task_and_sprint(issue_key)
            assert sprint_uuid == response['sprint']['uuid']

    @story('T130765 计划-关联迭代：关联已有迭代')
    def test_plan_relation_sprint(self, add_plan_task_sprint):
        with step('前置条件'):
            sprint_uuid, ise, plan_key = add_plan_task_sprint
            plan_a_key = Ra.add_plans_or_milestones()
        with step('关联工作项获迭代'):
            Ra.external_activity(plan_a_key, sprint_uuid, ob_type='sprint')
            issue_key = Ra.task_relation_plan_key(sprint_uuid)
            response = Ra.connecred_task_and_sprint(issue_key)
            assert sprint_uuid == response['sprint']['uuid']

    @story('T130768 计划-关联迭代：取消关联迭代')
    def test_del_plan_relation_sprint(self, add_plan_task_sprint):
        sprint_uuid, ise, plan_key = add_plan_task_sprint
        Ra.external_activity(plan_key, sprint_uuid, ob_type='sprint')
        with step('点击「移除关联迭代」按钮'):
            issue_key = Ra.task_relation_plan_key(sprint_uuid)
            resp_del = Ra.del_plans_or_milestones(issue_key)
            assert resp_del == issue_key

    @story('T128831 关联工作项：查看详情')
    def test_get_relation_sprint_info(self, add_plan_task_sprint):
        with step('前置条件'):
            sprint_uuid, ise, plan_key = add_plan_task_sprint
            Ra.external_activity(plan_key, ise, ob_type='task')
        with step('点击查看详情'):
            param = get_task_info(ise)[0]
            resp = self.call(ItemGraphql, param)
            # 检查关联项uuid为计划uuid
            resp.check_response('data.task.relatedActivities[0].uuid', plan_key.split('-')[1])

    @story('T128832 关联工作项：关联工作项下在子层级新建工作项')
    def test_add_relation_task_new_task(self):
        parent_ise = TaskAction.new_issue(issue_type_name='任务', is_batch=False)[0]
        plan_key = Ra.add_plans_or_milestones()
        Ra.external_activity(plan_key, parent_ise, ob_type='task')
        issue_key = Ra.task_relation_plan_key(parent_ise)
        with step('输入工作项名称“工作1子需求”，点击新建'):
            TaskAction.new_issue(parent_uuid=parent_ise, issue_type_name='子任务', is_batch=False)[0]

    @story('T128833 关联工作项：快速更新关联工作项信息')
    def test_fast_update_relation_task_info(self):
        ise = TaskAction.new_issue(issue_type_name='任务', is_batch=False)[0]
        plan_key = Ra.add_plans_or_milestones()
        Ra.external_activity(plan_key, ise, ob_type='task')
        issue_key = Ra.task_relation_plan_key(ise)
        with step('修改标题为“示例迭代1”'):
            Ra.fast_update_proj_plan_info("name", '示例工作项A' + mocks.num(), issue_key)

        with step('移动鼠标点击编辑开始时间'):
            param = update_issue_field(ise, 'field027', mocks.day_timestamp(1))[0]
            resp_start = self.call(TaskUpdate3, param)
        with step('移动鼠标点击编辑结束时间'):
            param = update_issue_field(ise, 'field028', mocks.day_timestamp(2))[0]
            resp_end = self.call(TaskUpdate3, param)
        with step('移动鼠标点击编辑进度由0修改为50%'):
            Ra.fast_update_proj_plan_info("progress", 5000000, issue_key)

    @story('T128835 关联工作项：拖拽更新工作项进度')
    def test_update_relation_task_schedule(self):
        ise = TaskAction.new_issue(issue_type_name='任务', is_batch=False)[0]
        plan_key = Ra.add_plans_or_milestones()
        Ra.external_activity(plan_key, ise, ob_type='task')
        issue_key = Ra.task_relation_plan_key(ise)
        with step('移动鼠标点击编辑进度由0修改为50%'):
            Ra.fast_update_proj_plan_info("progress", 5000000, issue_key)
            param = get_task_progress(ise)[0]
            resp = self.call(ItemGraphql, param)
            resp.check_response('data.task.progress', 5000000)

    @story('T128836 关联工作项：拖拽更新工作项周期')
    def test_update_task_cycle(self):
        ise = TaskAction.new_issue(issue_type_name='需求', is_batch=False)[0]
        plan_key = Ra.add_plans_or_milestones()
        Ra.external_activity(plan_key, ise, ob_type='task')
        issue_key = Ra.task_relation_plan_key(ise)
        with step('移动拖拽 开始时间”'):
            start_time = mocks.day_timestamp(1)
            Ra.fast_update_proj_plan_info("start_time", start_time, issue_key)
        with step('移动拖拽 结束时间”'):
            end_time = mocks.day_timestamp(3)
            Ra.fast_update_proj_plan_info("end_time", end_time, issue_key)
        with step('查看工作项详情'):
            param = get_task_progress(ise)[0]
            resp = self.call(ItemGraphql, param)
            # 验证详情中的开始-结束时间和上面拖拽的时间一致
            assert mocks.timestamp_time(start_time) == mocks.timestamp_time(resp.value('data.task.planStartDate'))
            assert mocks.timestamp_time(end_time) == mocks.timestamp_time(resp.value('data.task.planEndDate'))

    @story('T130774 计划-关联迭代：新建关联迭代')
    def test_plan_relation_new_sprint(self):
        with step('前置条件，新增迭代'):
            sprint_uuid = SprintAction.sprint_add()
            plan_key = Ra.add_plans_or_milestones()

        with step('选择迭代x，点击确认'):
            Ra.external_activity(plan_key, sprint_uuid, ob_type='sprint')
            issue_key = Ra.task_relation_plan_key(sprint_uuid)
            response = Ra.connecred_task_and_sprint(issue_key)
            assert sprint_uuid == response['sprint']['uuid']

    @story('T130766 计划-关联迭代：快速更新关联迭代信息')
    def test_fast_update_relation_sprint_info(self):
        sprint_uuid = SprintAction.sprint_add()
        plan_key = Ra.add_plans_or_milestones()
        Ra.external_activity(plan_key, sprint_uuid, ob_type='sprint')
        sprint_key = Ra.task_relation_plan_key(sprint_uuid)

        with step('修改标题为“示例迭代1”'):
            Ra.fast_update_proj_plan_info("name", '示例迭代A' + mocks.num(), sprint_key)

        with step('移动鼠标点击编辑开始时间，结束时间”'):
            Ra.fast_update_proj_plan_info("start_time", mocks.day_timestamp(1), sprint_key)
            Ra.fast_update_proj_plan_info("end_time", mocks.day_timestamp(3), sprint_key)

    @story('T130770 计划-关联迭代：拖拽更新迭代周期')
    def test_update_sprint_cycle_info(self):
        with step('存在计划“示例计划”已关联迭代'):
            sprint_uuid = SprintAction.sprint_add()
            plan_key = Ra.add_plans_or_milestones()
            Ra.external_activity(plan_key, sprint_uuid, ob_type='sprint')
            sprint_key = Ra.task_relation_plan_key(sprint_uuid)
        with step('移动拖拽 开始时间”'):
            Ra.fast_update_proj_plan_info("start_time", mocks.day_timestamp(1), sprint_key)
        with step('移动拖拽 结束时间”'):
            Ra.fast_update_proj_plan_info("end_time", mocks.day_timestamp(3), sprint_key)
