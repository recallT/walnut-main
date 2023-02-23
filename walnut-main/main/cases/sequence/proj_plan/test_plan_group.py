"""
@File    ：test_plan.py
@Author  ：zhangyonghui
@Email   ：zhangyonghui@ones.ai
@Date    ：2022/5/20
@Desc    ：项目计划-计划组管理
"""
from falcons.check import Checker, go
from falcons.com.nick import fixture, feature, story, step, mark
from falcons.helper import mocks
from falcons.helper.mocks import timestamp_time
from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra
from main.actions.sprint import SprintAction
from main.actions.task import TaskAction
from main.api.project import ItemGraphql
from main.params import relation
from falcons.com.meta import ApiMeta


@fixture(scope='module', autouse=True)
def add_plan_component():
    # 1.先添加一个【项目计划】 组件
    PrjAction.add_component('项目计划')
    yield
    PrjAction.remove_prj_component('项目计划')


@fixture()
def add_proj_plan():
    """新增项目计划-计划A"""
    plan = Ra.add_plans_or_milestones()
    return plan


@fixture()
def add_proj_plan_group(add_proj_plan):
    """
    新增项目计划组
    """
    # return 例如activity-4bigG2nb key 需要切割
    plan_key = add_proj_plan
    parent_uuid = plan_key.split('-')[1]
    rl_resp = go(ItemGraphql, relation.chart_uuid()[0])
    chart_uuid = rl_resp.value('data.activityCharts[0].uuid')

    prm = relation.add_parent_plan(parent_uuid)[0]
    prm.json_update('variables.chart_uuid', chart_uuid)

    add_resp = go(ItemGraphql, prm)
    add_resp.check_response('data.addActivity.parent', parent_uuid)
    return add_resp


@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过')
@feature('项目计划-计划管理')
class TestProjPlanGroup(Checker):

    @story('T130809 计划组：计划转变为计划组')
    def test_plan_change_plan_group(self, add_proj_plan_group):
        with step('新增计划组'):
            resp = add_proj_plan_group
            parent_uuid = resp.value('data.addActivity.parent')
            info_resp = Ra.get_proj_plan_info('activity-' + parent_uuid)
            # 校验类型为计划组ppm_task_group
            info_resp.check_response('data.activity.type', 'ppm_task_group')

    @story('T130810 计划组：计划组进度计算')
    def test_plan_group_schedule(self, add_proj_plan_group):
        with step('新建计划组 计划组下存在 A B两子计划'):
            parent_uuid = add_proj_plan_group.value('data.addActivity.parent')
            plan1_uuid = add_proj_plan_group.value('data.addActivity.uuid')
            prm = relation.add_parent_plan(parent_uuid, after=plan1_uuid)[0]
            rl_resp = go(ItemGraphql, relation.chart_uuid()[0])
            chart_uuid = rl_resp.value('data.activityCharts[0].uuid')
            prm.json_update('variables.chart_uuid', chart_uuid)
            add_resp = go(ItemGraphql, prm)
            add_resp.check_response('data.addActivity.parent', parent_uuid)
        with step('更新子计划A 计划B的进度'):
            Ra.fast_update_proj_plan_info("progress", 5000000, 'activity-' + plan1_uuid)

            # 检查计划组的进度情况
            info_resp = Ra.get_proj_plan_info('activity-' + parent_uuid)
            info_resp.check_response('data.activity.progress', 2500000)

    @story('T130811 计划组：计划组周期展示')
    def test_plan_group_cycle(self, add_proj_plan_group):
        parent_key = 'activity-' + add_proj_plan_group.value('data.addActivity.parent')
        plan1_key = 'activity-' + add_proj_plan_group.value('data.addActivity.uuid')
        with step('拖拽子计划的周期'):
            end_time = mocks.day_timestamp(2)
            Ra.fast_update_proj_plan_info("end_time", end_time, plan1_key)
            # 验证计划组的结束时间和子计划的结束时间一致即可
            resp = Ra.get_proj_plan_info(parent_key)
            resp_end_time = resp.value('data.activity.endTime')
            assert timestamp_time(end_time) == timestamp_time(resp_end_time)

    @story('T130813 计划组：快速更新计划组信息')
    def test_fast_update_plan_group_info(self, add_proj_plan_group):
        parent_key = 'activity-' + add_proj_plan_group.value('data.addActivity.parent')
        with step('鼠标移动至“示例计划组”点击快速编辑按钮，修改标题为“示例计划组A”'):
            Ra.fast_update_proj_plan_info("name", '示例计划' + mocks.num(), parent_key)

    @story('T130814 计划组：删除计划组')
    def test_del_plan_group(self, add_proj_plan_group):
        with step('创建计划组A'):
            plan_uuid = add_proj_plan_group.value('data.addActivity.parent')

        with step('点击删除计划按钮'):
            key = Ra.del_plans_or_milestones('activity-' + plan_uuid)
            assert plan_uuid in key

    @story('T130815 计划组：跳转详情')
    def test_plan_group_info(self, add_proj_plan_group):
        plan_uuid = add_proj_plan_group.value('data.addActivity.parent')
        info_resp = Ra.get_proj_plan_info('activity-' + plan_uuid)
        info_resp.check_response('data.activity.type', 'ppm_task_group')

    @story('T130816 计划组：子层级新建')
    def test_plan_group_add_plan(self, add_proj_plan_group):
        with step('新建计划组'):
            parent_uuid = add_proj_plan_group.value('data.addActivity.parent')
            plan1_uuid = add_proj_plan_group.value('data.addActivity.uuid')
        with step('在计划组子层级新建计划B'):
            prm = relation.add_parent_plan(parent_uuid, after=plan1_uuid)[0]
            rl_resp = go(ItemGraphql, relation.chart_uuid()[0])
            chart_uuid = rl_resp.value('data.activityCharts[0].uuid')
            prm.json_update('variables.chart_uuid', chart_uuid)

            add_resp = go(ItemGraphql, prm)
            add_resp.check_response('data.addActivity.parent', parent_uuid)

    @story('T130808 计划组动态日志：新增关联工作项')
    def test_plan_group_relation_task(self, add_proj_plan_group):
        with step('前置条件：新增项目计划组和工作项'):
            parent_uuid = add_proj_plan_group.value('data.addActivity.parent')
            ise = TaskAction.new_issue(issue_type_name='需求', is_batch=False)[0]
            ppmTask_uuid = Ra.get_proj_plan_info('activity-' + parent_uuid).value(
                'data.activity.ppmTask.uuid')

        with step('计划组关联工作项'):
            Ra.external_activity('activity-' + parent_uuid, ise, ob_type='task')
        with step('查询项目计划组的日志log data'):
            response = Ra.get_plan_log_data(ppmTask_uuid)
            # 断言返回的动态数据有一条，action 是add
            response.check_response('data.commonMessages[0].action', 'add')
            assert len(response.value('data.commonMessages')) == 1

    @story('T130807 计划组动态日志：新增关联迭代')
    def test_plan_group_relation_sprint(self, add_proj_plan_group):
        with step('前置条件：新增项目计划组和工作项'):
            parent_uuid = add_proj_plan_group.value('data.addActivity.parent')
            # 新增迭代工作项
            sprint_uuid = SprintAction.sprint_add()
            ppmTask_uuid = Ra.get_proj_plan_info('activity-' + parent_uuid).value(
                'data.activity.ppmTask.uuid')

        with step('计划组关联迭代'):
            Ra.external_activity('activity-' + parent_uuid, sprint_uuid, ob_type='sprint')
        with step('查询项目计划组的日志log data'):
            response = Ra.get_plan_log_data(ppmTask_uuid)
            # 断言返回的动态数据有一条，action 是add
            response.check_response('data.commonMessages[0].action', 'add')
            assert len(response.value('data.commonMessages')) == 1

    @story('T130806 计划组动态日志：取消关联工作项')
    def test_plan_group_del_task(self, add_proj_plan_group):
        with step('前置条件：新增项目计划组和工作项'):
            parent_uuid = add_proj_plan_group.value('data.addActivity.parent')
            ise = TaskAction.new_issue(issue_type_name='需求', is_batch=False)[0]
            ppmTask_uuid = Ra.get_proj_plan_info('activity-' + parent_uuid).value(
                'data.activity.ppmTask.uuid')
            Ra.external_activity('activity-' + parent_uuid, ise, ob_type='task')

        with step('计划组取消关联工作项'):
            issue_key = Ra.task_relation_plan_key(ise)
            resp_del = Ra.del_plans_or_milestones(issue_key)
            assert resp_del == issue_key
        with step('查询项目计划组的日志log data'):
            response = Ra.get_plan_log_data(ppmTask_uuid)
            # 断言返回的动态数据有2条
            assert len(response.value('data.commonMessages')) == 2

    @story('T130805 计划组动态日志：取消关联迭代')
    def test_plan_group_del_sprint(self, add_proj_plan_group):
        with step('前置条件：新增项目计划组和工作项'):
            parent_uuid = add_proj_plan_group.value('data.addActivity.parent')
            # 新增迭代工作项
            sprint_uuid = SprintAction.sprint_add()
            ppmTask_uuid = Ra.get_proj_plan_info('activity-' + parent_uuid).value(
                'data.activity.ppmTask.uuid')
            # 关联计划和迭代
            Ra.external_activity('activity-' + parent_uuid, sprint_uuid, ob_type='sprint')
        with step('解除关联'):
            issue_key = Ra.task_relation_plan_key(sprint_uuid)
            resp_del = Ra.del_plans_or_milestones(issue_key)
            assert resp_del == issue_key
        with step('查询项目计划组的日志log data'):
            response = Ra.get_plan_log_data(ppmTask_uuid)
            # 断言返回的动态数据有2条
            assert len(response.value('data.commonMessages')) == 2

    @story('T130803 计划组动态日志：计划评论')
    def test_plan_group_message_action(self, add_proj_plan_group):
        with step('前置条件，新增计划组'):
            parent_uuid = add_proj_plan_group.value('data.addActivity.parent')
            ppmTask_uuid = Ra.get_proj_plan_info('activity-' + parent_uuid).value(
                'data.activity.ppmTask.uuid')
        with step('计划组详情中，点击评论，发布计划组评论'):
            key = Ra.add_message(ppmTask_uuid, 'ppm_task')
        with step('点击评论下方的编辑按钮'):
            Ra.update_message(key)
        with step('点击评论下方的回复按钮，输入回复信息'):
            key_uuid = key.split('-')[1]
            Ra.reply_message(ppmTask_uuid, 'ppm_task', key_uuid)
        with step('点击评论下方的删除按钮'):
            Ra.del_message(key)

    @story('T130802 计划组动态日志：动态筛选')
    def test_plan_group_log(self, add_proj_plan_group):
        with step('前置条件'):
            parent_uuid = add_proj_plan_group.value('data.addActivity.parent')
            ise = TaskAction.new_issue(issue_type_name='需求', is_batch=False)[0]
            ppmTask_uuid = Ra.get_proj_plan_info('activity-' + parent_uuid).value(
                'data.activity.ppmTask.uuid')
            Ra.external_activity('activity-' + parent_uuid, ise, ob_type='task')
            # 发布评论
            Ra.add_message(ppmTask_uuid, 'ppm_task')
        with step('评论数据条数 1'):
            response = Ra.get_plan_log_data(ppmTask_uuid)
            assert len(response.value('data.commonMessages')) == 1
        with step('关联条数 1'):
            assert len(response.value('data.commonComments')) == 1
