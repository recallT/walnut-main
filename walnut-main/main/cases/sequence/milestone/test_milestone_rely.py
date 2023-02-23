"""
@File    ：test_milestone_rely
@Author  ：zhangyonghui
@Email   ：zhangyonghui@ones.ai
@Date    ：2022/6/01
@Desc    ：里程碑-前后置依赖关系
"""
from falcons.check import Checker, go
from falcons.com.nick import story, step, fixture, feature

from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra
from main.api.project import ItemGraphql
from main.params import relation


@fixture(scope='module', autouse=True)
def add_plan_component():
    # 1.先添加一个【项目计划/里程碑】 组件
    PrjAction.add_prj_plan_component()
    PrjAction.add_component('里程碑')

    yield
    PrjAction.remove_prj_component('项目计划')
    PrjAction.remove_prj_component('里程碑')


@feature('项目-里程碑-前后置关系')
class TestMilestoneRely(Checker):

    @story('T149637 里程碑-后置依赖：（完成-开始）后置依赖删除')
    def test_del_post_milestone_ets_relation(self):
        with step('前置条件， 创建一个计划和里程碑'):
            plan_key = Ra.add_plans_or_milestones()
            milestone_key = Ra.add_plans_or_milestones(p_type="milestone")
            Ra.add_ppm_relation('ets', milestone_key, plan_key)
        with step('确认删除 完成-开始关系'):
            Ra.del_relation('ets', milestone_key, plan_key)

    @story('T149635 里程碑-后置依赖：（完成-开始）添加后置依赖，里程碑完成后，计划才能开始')
    def test_add_post_milestone_plan_ets_relation(self):
        plan_key = Ra.add_plans_or_milestones()
        milestone_key = Ra.add_plans_or_milestones(p_type="milestone")
        Ra.add_ppm_relation('ets', milestone_key, plan_key)

    @story('T149633 里程碑-后置依赖：（完成-完成）后置依赖删除')
    def test_del_post_milestone_ete_relation(self):
        with step('前置条件， 创建一个计划和里程碑'):
            plan_key = Ra.add_plans_or_milestones()
            milestone_key = Ra.add_plans_or_milestones(p_type="milestone")
            Ra.add_ppm_relation('ete', milestone_key, plan_key)
        with step('确认删除 完成-开始关系'):
            Ra.del_relation('ete', milestone_key, plan_key)

    @story('T149638 里程碑-后置依赖：（完成-完成）添加后置依赖，里程碑完成后，计划才能完成')
    def test_add_post_milestone_plan_ete_relation(self):
        plan_key = Ra.add_plans_or_milestones()
        milestone_key = Ra.add_plans_or_milestones(p_type="milestone")
        Ra.add_ppm_relation('ete', milestone_key, plan_key)

    @story('T149639 里程碑-后置依赖：（完成-完成）添加后置依赖，里程碑完成后，子计划才能完成')
    def test_add_post_milestone_sub_plan_ete_relation(self):
        with step('创建计划组B 里程碑A'):
            plan_key = Ra.add_plans_or_milestones()
            parent_uuid = plan_key.split('-')[1]
            rl_resp = go(ItemGraphql, relation.chart_uuid()[0])
            chart_uuid = rl_resp.value('data.activityCharts[0].uuid')

            prm = relation.add_parent_plan(parent_uuid)[0]
            prm.json_update('variables.chart_uuid', chart_uuid)

            add_resp = go(ItemGraphql, prm)
            add_resp.check_response('data.addActivity.parent', parent_uuid)
            milestone_key = Ra.add_plans_or_milestones(p_type="milestone")

        with step('添加 完成-完成）添加后置依赖'):
            plan_key = add_resp.value('data.addActivity.key')
            Ra.add_ppm_relation('ete', milestone_key, plan_key)

    @story('T149624 里程碑-前置依赖：（开始-完成）前置依赖删除')
    def test_del_pre_milestone_ste_relation(self):
        with step('前置条件， 创建一个计划和里程碑'):
            plan_key = Ra.add_plans_or_milestones()
            milestone_key = Ra.add_plans_or_milestones(p_type="milestone")
            Ra.add_ppm_relation('ste', plan_key, milestone_key)
        with step('确认删除 完成-开始关系'):
            Ra.del_relation('ste', plan_key, milestone_key)

    @story('T143551 里程碑-前置依赖：（开始-完成）添加前置依赖，计划开始后，里程碑才能完成')
    def test_add_pre_milestone_ste_relation(self):
        plan_key = Ra.add_plans_or_milestones()
        milestone_key = Ra.add_plans_or_milestones(p_type="milestone")
        milestone_uuid = Ra.get_proj_plan_info(milestone_key).value(
            'data.activity.milestone.uuid')
        Ra.add_ppm_relation('ste', plan_key, milestone_key)
        with step('查看动态'):
            response = Ra.get_plan_log_data(milestone_uuid)
            # 断言返回的动态数据有一条，action 是add
            response.check_response('data.commonMessages[0].action', 'add')
            response.check_response('data.commonMessages[0].tag', 'dependency')
            assert len(response.value('data.commonMessages')) == 1

    @story('T149627 里程碑-前置依赖：（完成-完成）前置依赖删除')
    def test_del_pre_milestone_ete_relation(self):
        with step('前置条件， 创建一个计划和里程碑'):
            plan_key = Ra.add_plans_or_milestones()
            milestone_key = Ra.add_plans_or_milestones(p_type="milestone")
            Ra.add_ppm_relation('ete', plan_key, milestone_key)
        with step('确认删除 完成-开始关系'):
            Ra.del_relation('ete', plan_key, milestone_key)

    @story('T143550 里程碑-前置依赖：（完成-完成）添加前置依赖，计划完成后，里程碑才能完成')
    def test_add_pre_milestone_ete_relation(self):
        plan_key = Ra.add_plans_or_milestones()
        milestone_key = Ra.add_plans_or_milestones(p_type="milestone")
        Ra.add_ppm_relation('ete', plan_key, milestone_key)

    @story('T149630 里程碑-前置依赖：（完成-完成）添加前置依赖，里程碑b完成后，里程碑a才能完成')
    def test_add_pre_milestones_ete_relation(self):
        milestone_a_key = Ra.add_plans_or_milestones(p_type="milestone")
        milestone_b_key = Ra.add_plans_or_milestones(p_type="milestone")
        Ra.add_ppm_relation('ete', milestone_a_key, milestone_b_key)
        milestone_uuid = Ra.get_proj_plan_info(milestone_a_key).value(
            'data.activity.milestone.uuid')
        with step('查看动态'):
            response = Ra.get_plan_log_data(milestone_uuid)
            # 断言返回的动态数据有一条，action 是add
            response.check_response('data.commonMessages[0].action', 'add')
            response.check_response('data.commonMessages[0].tag', 'dependency')
            assert len(response.value('data.commonMessages')) == 1

    @story('T149640 里程碑-后置依赖：（完成-完成）添加后置依赖，里程碑A完成后，里程碑B才能完成')
    def test_add_post_milestone_and_milestone_ete_relation(self):
        with step('前置条件， 里程碑A和里程碑B添加后置依赖关系'):
            milestone_a_key = Ra.add_plans_or_milestones(p_type="milestone")
            milestone_b_key = Ra.add_plans_or_milestones(p_type="milestone")
            Ra.add_ppm_relation('ete', milestone_a_key, milestone_b_key)

    @story('T149629 里程碑-前置依赖：（完成-完成）添加前置依赖，子计划完成后，里程碑才能完成')
    def test_add_pre_milestone_and_milestone_ete_relation(self):
        with step('创建计划组B 里程碑A'):
            plan_key = Ra.add_plans_or_milestones()
            parent_uuid = plan_key.split('-')[1]
            rl_resp = go(ItemGraphql, relation.chart_uuid()[0])
            chart_uuid = rl_resp.value('data.activityCharts[0].uuid')

            prm = relation.add_parent_plan(parent_uuid)[0]
            prm.json_update('variables.chart_uuid', chart_uuid)

            add_resp = go(ItemGraphql, prm)
            add_resp.check_response('data.addActivity.parent', parent_uuid)
            milestone_key = Ra.add_plans_or_milestones(p_type="milestone")

        with step('添加 完成-完成）添加前置依赖'):
            plan_key = add_resp.value('data.addActivity.key')
            Ra.add_ppm_relation('ete', plan_key, milestone_key)
