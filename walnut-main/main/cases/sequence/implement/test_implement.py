"""
@File    ：implement
@Author  ：zhangyonghui
@Email   ：zhangyonghui@ones.ai
@Date    ：2022/6/02
@Desc    ：执行
"""
from falcons.check import Checker
from falcons.com.nick import story, feature, fixture, step, mark
from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra
from main.actions.sprint import SprintAction
from main.actions.task import TaskAction
from falcons.com.meta import ApiMeta


@fixture(scope='module', autouse=True)
def add_plan_component():
    # 1.先添加【执行】【项目计划】 组件
    # view = PrjAction.get_project_implement_view()
    # component_uuid1 = PrjAction.add_implement_component(view).value('components[0].uuid')
    # component_uuid2 = PrjAction.add_prj_plan_component().value('components[0].uuid')
    # yield
    # PrjAction.remove_prj_component_by_uuid(component_uuid1)
    # PrjAction.remove_prj_component_by_uuid(component_uuid2)

    PrjAction.add_component('项目计划')
    PrjAction.add_component('执行')
    yield
    PrjAction.remove_prj_component('项目计划')
    PrjAction.remove_prj_component('执行')


@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过')
@feature('项目-执行')
class TestProjImplement(Checker):

    @story('T130785 计划动态日志：新增关联迭代')
    def test_plan_relation_sprint_log(self):
        with step('前置条件，新增迭代,关联计划'):
            plan_key = Ra.add_plans_or_milestones()
            plan_uuid = Ra.get_proj_plan_info(plan_key).value(
                'data.activity.ppmTask.uuid')
            sprint_uuid = SprintAction.sprint_add()
            Ra.external_activity(plan_key, sprint_uuid, ob_type='sprint')
            issue_key = Ra.task_relation_plan_key(sprint_uuid)
            response = Ra.connecred_task_and_sprint(issue_key)
            assert sprint_uuid == response['sprint']['uuid']
        with step('计划动态查询'):
            response = Ra.get_plan_log_data(plan_uuid)
            response.check_response('data.commonMessages[0].action', 'add')
            # 1条动态，add
            assert len(response.value('data.commonMessages')) == 1

    @story('T130786 计划动态日志：新增关联工作项')
    def test_plan_relation_task_log(self):
        with step('前置条件'):
            ise = TaskAction.new_issue(issue_type_name='需求', is_batch=False)[0]
            plan_key = Ra.add_plans_or_milestones()
            plan_uuid = Ra.get_proj_plan_info(plan_key).value(
                'data.activity.ppmTask.uuid')
        with step('关联项目计划和需求工作项'):
            Ra.external_activity(plan_key, ise, ob_type='task')
            issue_key = Ra.task_relation_plan_key(ise)
            response = Ra.connecred_task_and_sprint(issue_key)
            assert ise == response['task']['uuid']
        with step('计划动态查询'):
            response = Ra.get_plan_log_data(plan_uuid)
            response.check_response('data.commonMessages[0].action', 'add')
            # 1条动态，add
            assert len(response.value('data.commonMessages')) == 1

    @story('T130784 计划动态日志：取消关联工作项')
    def test_del_plan_task_relation(self):
        with step('前置条件：新增项目计划组和工作项'):
            plan_key = Ra.add_plans_or_milestones()
            plan_uuid = Ra.get_proj_plan_info(plan_key).value(
                'data.activity.ppmTask.uuid')
            ise = TaskAction.new_issue(issue_type_name='需求', is_batch=False)[0]
            Ra.external_activity(plan_key, ise, ob_type='task')
        with step('计划组取消关联工作项'):
            issue_key = Ra.task_relation_plan_key(ise)
            resp_del = Ra.del_plans_or_milestones(issue_key)
            assert resp_del == issue_key
        with step('查询项目计划组的日志log data'):
            response = Ra.get_plan_log_data(plan_uuid)
            # 断言返回的动态数据有2条
            assert len(response.value('data.commonMessages')) == 2

    @story('T130783 计划动态日志：取消关联迭代')
    def test_del_plan_sprint_relation(self):
        with step('前置条件，新增迭代,关联计划'):
            plan_key = Ra.add_plans_or_milestones()
            plan_uuid = Ra.get_proj_plan_info(plan_key).value(
                'data.activity.ppmTask.uuid')
            sprint_uuid = SprintAction.sprint_add()
            Ra.external_activity(plan_key, sprint_uuid, ob_type='sprint')
        with step('解除关联关系'):
            issue_key = Ra.task_relation_plan_key(sprint_uuid)
            resp_del = Ra.del_plans_or_milestones(issue_key)
            assert resp_del == issue_key
        with step('查询项目计划组的日志log data'):
            response = Ra.get_plan_log_data(plan_uuid)
            # 断言返回的动态数据有2条
            assert len(response.value('data.commonMessages')) == 2

    @story('T130781 计划动态日志：计划评论')
    def test_plan_message(self):
        plan_key = Ra.add_plans_or_milestones()
        ppmTask_uuid = Ra.get_proj_plan_info(plan_key).value(
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

    @story('T130782 计划动态日志：进度变更')
    def test_plan_progress_log(self):
        plan_key = Ra.add_plans_or_milestones()
        plan_uuid = Ra.get_proj_plan_info(plan_key).value(
            'data.activity.ppmTask.uuid')
        Ra.fast_update_proj_plan_info("progress", 5000000, plan_key)
        with step('计划动态日志'):
            response = Ra.get_plan_log_data(plan_uuid)
            response.check_response('data.commonMessages[0].action', 'update')
            # 断言返回的动态数据有1条
            assert len(response.value('data.commonMessages')) == 1

    @story('T130788 计划详情-后置影响：开始-完成')
    def test_add_ste_relation(self):
        plan_a_key = Ra.add_plans_or_milestones()
        plan_b_key = Ra.add_plans_or_milestones()
        plan_uuid = Ra.get_proj_plan_info(plan_b_key).value(
            'data.activity.ppmTask.uuid')
        Ra.add_ppm_relation('ste', plan_b_key, plan_a_key)
        with step('查看动态'):
            response = Ra.get_plan_log_data(plan_uuid)
            # 断言返回的动态数据有一条，action 是add
            response.check_response('data.commonMessages[0].action', 'add')
            response.check_response('data.commonMessages[0].tag', 'dependency')
            assert len(response.value('data.commonMessages')) == 1

    @story('T130789 计划详情-后置影响：完成-开始')
    def test_add_ets_relation(self):
        plan_a_key = Ra.add_plans_or_milestones()
        plan_b_key = Ra.add_plans_or_milestones()
        plan_uuid = Ra.get_proj_plan_info(plan_b_key).value(
            'data.activity.ppmTask.uuid')
        Ra.add_ppm_relation('ets', plan_b_key, plan_a_key)
        with step('查看动态'):
            response = Ra.get_plan_log_data(plan_uuid)
            # 断言返回的动态数据有一条，action 是add
            response.check_response('data.commonMessages[0].action', 'add')
            response.check_response('data.commonMessages[0].tag', 'dependency')
            assert len(response.value('data.commonMessages')) == 1

    @story("T130787 计划详情-后置影响：开始-开始")
    def test_add_sts_relation(self):
        # 新建两条 计划
        plan_a_key = Ra.add_plans_or_milestones()
        plan_b_key = Ra.add_plans_or_milestones()
        #
        plan_uuid = Ra.get_proj_plan_info(plan_b_key).value(
            'data.activity.ppmTask.uuid')
        Ra.add_ppm_relation('sts', plan_b_key, plan_a_key)
        with step('查看动态'):
            response = Ra.get_plan_log_data(plan_uuid)
            # 断言返回的动态数据有一条，action 是add
            response.check_response('data.commonMessages[0].action', 'add')
            response.check_response('data.commonMessages[0].tag', 'dependency')
            assert len(response.value('data.commonMessages')) == 1

    @story("T130790 计划详情-后置影响：完成-完成")
    def test_add_ete_relation(self):
        # 新建两条 计划
        plan_a_key = Ra.add_plans_or_milestones()
        plan_b_key = Ra.add_plans_or_milestones()
        plan_uuid = Ra.get_proj_plan_info(plan_b_key).value(
            'data.activity.ppmTask.uuid')
        Ra.add_ppm_relation('ete', plan_b_key, plan_a_key)
        with step('查看动态'):
            response = Ra.get_plan_log_data(plan_uuid)
            # 断言返回的动态数据有一条，action 是add
            response.check_response('data.commonMessages[0].action', 'add')
            response.check_response('data.commonMessages[0].tag', 'dependency')
            assert len(response.value('data.commonMessages')) == 1

    @story("T130791 计划详情-前置依赖：开始-开始")
    def test_add_sts_pre_relation(self):
        # 新建两条 计划
        plan_a_key = Ra.add_plans_or_milestones()
        plan_b_key = Ra.add_plans_or_milestones()
        plan_uuid = Ra.get_proj_plan_info(plan_b_key).value(
            'data.activity.ppmTask.uuid')
        Ra.add_ppm_relation('sts', plan_b_key, plan_a_key)
        with step('查看动态'):
            response = Ra.get_plan_log_data(plan_uuid)
            # 断言返回的动态数据有一条，action 是add
            response.check_response('data.commonMessages[0].action', 'add')
            response.check_response('data.commonMessages[0].tag', 'dependency')
            assert len(response.value('data.commonMessages')) == 1

    @story("T130792 计划详情-前置依赖：开始-完成")
    def test_add_ste_pre_relation(self):
        # 新建两条 计划
        plan_a_key = Ra.add_plans_or_milestones()
        plan_b_key = Ra.add_plans_or_milestones()
        plan_uuid = Ra.get_proj_plan_info(plan_b_key).value(
            'data.activity.ppmTask.uuid')
        Ra.add_ppm_relation('ste', plan_b_key, plan_a_key)
        with step('查看动态'):
            response = Ra.get_plan_log_data(plan_uuid)
            # 断言返回的动态数据有一条，action 是add
            response.check_response('data.commonMessages[0].action', 'add')
            response.check_response('data.commonMessages[0].tag', 'dependency')
            assert len(response.value('data.commonMessages')) == 1

    @story("T130793 计划详情-前置依赖：完成-开始")
    def test_add_ets_pre_relation(self):
        # 新建两条 计划
        plan_a_key = Ra.add_plans_or_milestones()
        plan_b_key = Ra.add_plans_or_milestones()
        plan_uuid = Ra.get_proj_plan_info(plan_b_key).value(
            'data.activity.ppmTask.uuid')
        Ra.add_ppm_relation('ets', plan_b_key, plan_a_key)
        with step('查看动态'):
            response = Ra.get_plan_log_data(plan_uuid)
            # 断言返回的动态数据有一条，action 是add
            response.check_response('data.commonMessages[0].action', 'add')
            response.check_response('data.commonMessages[0].tag', 'dependency')
            assert len(response.value('data.commonMessages')) == 1

    @story("T130794 计划详情-前置依赖：完成-完成")
    def test_add_ete_pre_relation(self):
        # 新建两条 计划
        plan_a_key = Ra.add_plans_or_milestones()
        plan_b_key = Ra.add_plans_or_milestones()
        plan_uuid = Ra.get_proj_plan_info(plan_b_key).value(
            'data.activity.ppmTask.uuid')
        Ra.add_ppm_relation('ete', plan_b_key, plan_a_key)
        with step('查看动态'):
            response = Ra.get_plan_log_data(plan_uuid)
            # 断言返回的动态数据有一条，action 是add
            response.check_response('data.commonMessages[0].action', 'add')
            response.check_response('data.commonMessages[0].tag', 'dependency')
            assert len(response.value('data.commonMessages')) == 1
