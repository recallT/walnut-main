"""
@File    ：test_plan.py
@Author  ：zhangyonghui
@Email   ：zhangyonghui@ones.ai
@Date    ：2022/5/20
@Desc    ：项目计划管理
"""

from falcons.check import Checker, go
from falcons.com.nick import fixture, feature, story, step, mark
from falcons.helper import mocks
from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra
from main.actions.sprint import SprintAction
from main.actions.task import TaskAction
from main.api.project import ItemGraphql, UsesSearch
from main.params import relation, proj
from falcons.com.meta import ApiMeta


@fixture(scope='module', autouse=True)
def add_plan_component():
    PrjAction.add_component('项目计划')
    yield
    PrjAction.remove_prj_component('项目计划')


@fixture()
def add_proj_plan():
    """新增项目计划-计划A"""
    plan = Ra.add_plans_or_milestones()
    return plan


@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过')
@feature('项目计划-计划管理')
class TestProjPlan(Checker):

    @story('T130825 计划：新建计划')
    def test_add_proj_plan_task1(self):
        Ra.add_plans_or_milestones()

    @story('T130819 计划：快速新建计划')
    def test_fast_add_proj_plan_task(self):
        Ra.add_plans_or_milestones()

    @story('T130820 计划：删除计划')
    def test_del_proj_plan_task(self, add_proj_plan):
        with step('创建计划A'):
            plan_uuid = add_proj_plan

        with step('点击删除计划按钮'):
            Ra.del_plans_or_milestones(plan_uuid)

    @story('T130827 计划：子层级新建')
    def test_add_proj_parent_plan_task(self, add_proj_plan):
        with step('前置条件'):
            # return 例如activity-4bigG2nb key 需要切割
            plan_key = add_proj_plan
            parent_uuid = plan_key.split('-')[1]
        with step('创建子计划'):
            rl_resp = go(ItemGraphql, relation.chart_uuid()[0])
            chart_uuid = rl_resp.value('data.activityCharts[0].uuid')

            prm = relation.add_parent_plan(parent_uuid)[0]
            prm.json_update('variables.chart_uuid', chart_uuid)

            add_resp = go(ItemGraphql, prm)
            add_resp.check_response('data.addActivity.parent', parent_uuid)

    @story('T130822 计划：跳转详情')
    def test_proj_plan_info(self, add_proj_plan):
        with step('鼠标移动至“示例计划”，点击跳转详情按钮'):
            info_resp = Ra.get_proj_plan_info(add_proj_plan)
            info_resp.check_response('data.activity.key', add_proj_plan)
            info_resp.check_response('data.activity.type', 'ppm_task')

    @story('T130818 计划：快速更新计划信息')
    def test_fast_update_proj_plan(self, add_proj_plan):
        with step('鼠标移动至“示例计划”点击快速编辑按钮，修改标题为“示例计划A”'):
            Ra.fast_update_proj_plan_info("name", '示例计划' + mocks.num(), add_proj_plan)
        with step(''):
            # 查询环境的member用户uuid
            su_param = proj.program_search_user()[0]
            resp_user_uuid = go(UsesSearch, su_param).value('users[0].uuid')
            Ra.fast_update_proj_plan_info("assign", resp_user_uuid, add_proj_plan)
            # 查看里程碑详情，断言负责人字段
            resp = Ra.get_proj_plan_info(add_proj_plan)
            resp.check_response('data.activity.assign.uuid', resp_user_uuid)
        with step('移动鼠标点击编辑开始日期xxx、完成日期xxx'):
            Ra.fast_update_proj_plan_info("start_time", mocks.day_timestamp(1), add_proj_plan)

        with step('移动鼠标点击编辑进度由0修改为50%'):
            Ra.fast_update_proj_plan_info("progress", 5000000, add_proj_plan)

    @story('T130775 计划-关联工作项：关联已有工作项')
    def test_proj_plan_relation_task(self, add_proj_plan):
        with step('前置条件'):
            ise = TaskAction.new_issue(issue_type_name='需求', is_batch=False)[0]

        with step('关联项目计划和需求工作项'):
            Ra.external_activity(add_proj_plan, ise, ob_type='task')
            issue_key = Ra.task_relation_plan_key(ise)
            response = Ra.connecred_task_and_sprint(issue_key)
            assert ise == response['task']['uuid']

    @story('T130777 计划-关联工作项：新建关联工作项')
    def test_proj_plan_relation_new_task(self, add_proj_plan):
        with step('新建关联工作项'):
            ise = TaskAction.new_issue(issue_type_name='任务', is_batch=False)[0]
        with step('关联项目计划和需求工作项'):
            Ra.external_activity(add_proj_plan, ise, ob_type='task')
            issue_key = Ra.task_relation_plan_key(ise)
            response = Ra.connecred_task_and_sprint(issue_key)
            assert ise == response['task']['uuid']

    @story('T130776 计划-关联工作项：取消关联工作项')
    def test_proj_plan_del_task(self, add_proj_plan):
        with step('新增关联工作项'):
            ise = TaskAction.new_issue(issue_type_name='任务', is_batch=False)[0]
            resp = Ra.external_activity(add_proj_plan, ise, ob_type='task')
            issue_key = Ra.task_relation_plan_key(ise)
        with step('确定移除关联'):
            resp_del = Ra.del_plans_or_milestones(issue_key)
            assert resp_del == issue_key

    @story('T130767 计划-关联迭代：取消关联迭代')
    def test_proj_plan_del_sprint(self, add_proj_plan):
        with step('前置条件，新增迭代，并进行关联'):
            sprint_uuid = SprintAction.sprint_add()
            resp = Ra.external_activity(add_proj_plan, sprint_uuid, ob_type='sprint')

        with step('确定移除关联'):
            issue_key = Ra.task_relation_plan_key(sprint_uuid)
            resp_del = Ra.del_plans_or_milestones(issue_key)
            assert resp_del == issue_key

    @story('T130764 计划-关联迭代：关联已有迭代')
    @story('130772 计划-关联迭代：新窗口打开')
    def test_proj_plan_relation_sprint(self, add_proj_plan):
        with step('前置条件，新增迭代'):
            sprint_uuid = SprintAction.sprint_add()

        with step('选择迭代x，点击确认'):
            Ra.external_activity(add_proj_plan, sprint_uuid, ob_type='sprint')
            issue_key = Ra.task_relation_plan_key(sprint_uuid)
            response = Ra.connecred_task_and_sprint(issue_key)
            assert sprint_uuid == response['sprint']['uuid']

    @story('T130823 计划：拖拽更新计划进度')
    def test_update_proj_plan_progress(self, add_proj_plan):
        with step('点击“示例计划”甘特图示，拖拽进度变更至50%'):
            Ra.fast_update_proj_plan_info("progress", 5000000, add_proj_plan)

    @story('T130824 计划：拖拽更新计划周期')
    def test_update_proj_plan_time(self, add_proj_plan):
        with step('点击“示例计划”甘特图示，拖拽周期至开始时间为xxxxx，鼠标失焦'):
            Ra.fast_update_proj_plan_info("start_time", mocks.day_timestamp(1), add_proj_plan)

        with step('点击“示例计划”甘特图示，拖拽周期至开始时间为xxxxx，鼠标失焦'):
            Ra.fast_update_proj_plan_info("end_time", mocks.day_timestamp(3), add_proj_plan)

    @story('T137930 项目计划甘特图：添加完成-开始关系（计划与计划）')
    def test_add_plan_and_plan_relation(self):
        with step('存在计划A与计划B，无任何前后置关系'):
            plan_a = Ra.add_plans_or_milestones()
            plan_b = Ra.add_plans_or_milestones()
        with step('建立完成-开始的前后置关系'):
            rl_resp = Ra.add_ppm_relation('ets', plan_a, plan_b)
            info_resp_a = Ra.get_proj_plan_info(plan_a).value('data.activity.endTime')
            info_resp_b = Ra.get_proj_plan_info(plan_b).value('data.activity.startTime')
            # 创建关系后，计划B的开始时间晚于计划A的结束时间
            assert info_resp_a <= info_resp_b

        with step('将计划A的完成时间拖拽到计划B开始时间之后'):
            end_time = mocks.day_timestamp(5)
            Ra.fast_update_proj_plan_info("end_time", end_time, plan_a)
            info_resp = Ra.get_proj_plan_info(plan_b)
            # 修改计划A的完成时间后，B计划的开始时间在A计划的完成时间后开始
            info_resp.check_response('data.activity.startTime', end_time, check_type='gt')

    @story('T137928 项目计划甘特图：添加开始-完成关系（计划与里程碑）')
    def test_add_plan_and_milestone_relation(self):
        with step('存在计划A与计划B，无任何前后置关系'):
            plan = Ra.add_plans_or_milestones()
            milestones = Ra.add_plans_or_milestones(p_type='milestone')
        with step('建立开始-完成的前后置关'):
            rl_resp = Ra.add_ppm_relation('ste', plan, milestones)
            resp_plan_endTime = Ra.get_proj_plan_info(plan).value('data.activity.endTime')
            resp_milestones_endTime = Ra.get_proj_plan_info(milestones).value('data.activity.endTime')
            assert resp_plan_endTime >= resp_milestones_endTime
        with step('将计划A的开始时间拖拽到里程碑B完成时间之后'):
            start_time = mocks.day_timestamp(5)
            end_time = mocks.day_timestamp(6)
            Ra.fast_update_proj_plan_info("end_time", end_time, plan)
            Ra.fast_update_proj_plan_info("start_time", start_time, plan)
            resp_milestones_endTime = Ra.get_proj_plan_info(milestones).value('data.activity.endTime')
            # 修改计划A的完成时间后，计划的开始时间与里程碑的完成时间日期相等
            assert mocks.timestamp_time(start_time) == mocks.timestamp_time(resp_milestones_endTime)

    @story("T137927 项目计划甘特图：添加开始-完成关系（计划与计划）")
    def test_proj_plan_add_plan_ste(self):
        with step("前置条件：创建两个计划"):
            plan_a_key = Ra.add_plans_or_milestones()
            plan_b_key = Ra.add_plans_or_milestones()
        with step("建立开始-完成的前后置关系"):
            Ra.add_ppm_relation('ste', plan_a_key, plan_b_key)
            resp_plan_a_end_time = Ra.get_proj_plan_info(plan_a_key).value('data.activity.endTime')
            resp_plan_b_end_time = Ra.get_proj_plan_info(plan_b_key).value('data.activity.endTime')
            assert mocks.timestamp_time(resp_plan_a_end_time) == mocks.timestamp_time(resp_plan_b_end_time)

        with step("将计划A的开始时间拖拽到计划B完成时间之后"):
            start_time = mocks.day_timestamp(5)
            end_time = mocks.day_timestamp(6)
            Ra.fast_update_proj_plan_info("end_time", end_time, plan_a_key)
            Ra.fast_update_proj_plan_info("start_time", start_time, plan_a_key)
            resp_plan_b_end_time = Ra.get_proj_plan_info(plan_b_key).value('data.activity.endTime')
            # 修改计划A的完成时间后，计划A的开始时间与计划B的完成时间日期相等
            assert  mocks.timestamp_time(start_time) == mocks.timestamp_time(resp_plan_b_end_time)

    @story("T137933 项目计划甘特图：添加完成-完成关系（计划与计划）")
    def test_proj_plan_add_plan_ete(self):
        with step("前置条件： 创建两个计划"):
            plan_a_key = Ra.add_plans_or_milestones()
            plan_b_key = Ra.add_plans_or_milestones()
        with step("建立完成-完成的前后置关系"):
            Ra.add_ppm_relation('ete', plan_a_key, plan_b_key)
            resp_plan_a_end_time = Ra.get_proj_plan_info(plan_a_key).value('data.activity.endTime')
            resp_plan_b_end_time = Ra.get_proj_plan_info(plan_b_key).value('data.activity.endTime')
            assert mocks.timestamp_time(resp_plan_a_end_time) == mocks.timestamp_time(resp_plan_b_end_time)

        with step("将计划A的完成时间拖拽到计划B完成时间之后"):
            end_time = mocks.day_timestamp(5)
            Ra.fast_update_proj_plan_info('end_time', end_time, plan_a_key)
            resp_plan_b_end_time = Ra.get_proj_plan_info(plan_b_key).value('data.activity.endTime')
            # 修改计划A的完成时间后，计划A的开始时间与计划B的完成时间日期相等
            assert  mocks.timestamp_time(end_time) == mocks.timestamp_time(resp_plan_b_end_time)

    @story("T137934 项目计划甘特图：添加完成-完成关系（计划与里程碑）")
    def test_proj_plan_add_plan_milestone_ete(self):
        with step('存在计划A与里程碑B，无任何前后置关系'):
            plan_a = Ra.add_plans_or_milestones()
            milestone_b = Ra.add_plans_or_milestones(p_type='milestone')
        with step('建立完成-完成的前后置关系'):
            Ra.add_ppm_relation('ete', plan_a, milestone_b)
            resp_plan_a_end_time = Ra.get_proj_plan_info(plan_a).value('data.activity.endTime')
            resp_milestone_b_end_time = Ra.get_proj_plan_info(milestone_b).value('data.activity.endTime')
            assert resp_plan_a_end_time >= resp_milestone_b_end_time
        with step("将计划A的完成时间拖拽到里程碑B完成时间之后"):
            end_time = mocks.day_timestamp(5)
            Ra.fast_update_proj_plan_info('end_time', end_time, plan_a)
            resp_milestones_a_end_time = Ra.get_proj_plan_info(milestone_b).value(
                'data.activity.endTime')
            resp_plan_b_end_time = Ra.get_proj_plan_info(plan_a).value(
                'data.activity.endTime')
            assert mocks.timestamp_time(resp_milestones_a_end_time) == mocks.timestamp_time(resp_plan_b_end_time)

    @story("T137924 项目计划甘特图：添加开始-开始关系（计划与计划）")
    def test_proj_plan_add_plan_sts(self):
        with step("前置条件：创建两个计划"):
            plan_a_key = Ra.add_plans_or_milestones()
            plan_b_key = Ra.add_plans_or_milestones()
        with step("建立开始-开始的前后置关系"):
            Ra.add_ppm_relation('sts', plan_a_key, plan_b_key)
            resp_plan_a_start_time = Ra.get_proj_plan_info(plan_a_key).value('data.activity.startTime')
            resp_plan_b_start_time = Ra.get_proj_plan_info(plan_b_key).value('data.activity.startTime')
            assert resp_plan_a_start_time == resp_plan_b_start_time
        with step("将计划A的开始时间拖拽到计划B开始时间之后"):
            start_time = mocks.day_timestamp(week=1)
            Ra.fast_update_proj_plan_info('start_time', start_time, plan_a_key)
            resp_plan_b_start_time = Ra.get_proj_plan_info(plan_b_key).value('data.activity.startTime')
            # 修改计划A的开始时间后，计划A的开始时间与计划B的开始时间日期相等
            assert mocks.timestamp_time(start_time) == mocks.timestamp_time(resp_plan_b_start_time)

