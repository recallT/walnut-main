"""
@File    ：test_milestones.py
@Author  ：zhangyonghui
@Email   ：zhangyonghui@ones.ai
@Date    ：2022/5/26
@Desc    ：里程碑管理
"""
from falcons.check import Checker, go
from falcons.com.nick import fixture, feature, story, step, mark
from falcons.helper import mocks
from falcons.helper.mocks import timestamp_time
from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra
from main.api.project import UsesSearch
from main.params import proj
from falcons.com.meta import ApiMeta


@fixture(scope='module', autouse=True)
def add_plan_component():
    # 1.先添加一个【项目计划】 组件
    PrjAction.add_component('项目计划')
    yield
    PrjAction.remove_prj_component('项目计划')


@fixture()
def add_proj_milestone():
    """新增项目计划-里程碑"""
    milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
    return milestone_key


@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境不稳定跳过')
@feature('项目计划-里程碑管理')
class TestProjMilestones(Checker):

    @story('T130959 里程碑：新建里程碑')
    def test_proj_plan_add_milestones(self):
        Ra.add_plans_or_milestones(p_type='milestone')

    @story('T130954 里程碑：快速新建里程碑')
    def test_proj_plan_fast_add_milestones(self):
        Ra.add_plans_or_milestones(p_type='milestone')

    @story('T130951 里程碑：更新里程碑状态')
    def test_proj_plan_update_milestones_status(self, add_proj_milestone):
        with step('更新里程碑状态为已完成'):
            Ra.fast_update_proj_plan_info("progress", 10000000, add_proj_milestone)

    @story('T130953 里程碑：快速更新示例里程碑信息')
    def test_proj_plan_fast_update_milestones(self, add_proj_milestone):
        with step('修改标题为“示例里程碑A”'):
            Ra.fast_update_proj_plan_info("name", '示例里程碑A' + mocks.num(), add_proj_milestone)
        with step('移动鼠标点击编辑示例里程碑负责人由A到B'):
            su_param = proj.program_search_user()[0]
            resp_user_uuid = go(UsesSearch, su_param).value('users[0].uuid')
            Ra.fast_update_proj_plan_info("assign", resp_user_uuid, add_proj_milestone)
            # 查看里程碑详情，断言负责人字段
            resp = Ra.get_proj_plan_info(add_proj_milestone)
            resp.check_response('data.activity.assign.uuid', resp_user_uuid)
        with step('移动鼠标点击编辑完成日期xxx”'):
            Ra.fast_update_proj_milestone_info(add_proj_milestone, mocks.day_timestamp(1))
        with step('移动鼠标点击编辑状态由未开始变为已完成”'):
            Ra.fast_update_proj_plan_info("progress", 10000000, add_proj_milestone)

    @story('T130955 里程碑：删除里程碑')
    def test_proj_plan_del_milestones(self, add_proj_milestone):
        with step('创建里程碑A'):
            milestone_key = add_proj_milestone

        with step('点击删除里程碑按钮'):
            resp = Ra.del_plans_or_milestones(milestone_key)
            assert resp == milestone_key

    @story('T130957 里程碑：跳转详情')
    def test_proj_plan_milestones_info(self, add_proj_milestone):
        with step('鼠标移动至“里程碑”，点击跳转详情按钮'):
            info_resp = Ra.get_proj_plan_info(add_proj_milestone)
            info_resp.check_response('data.activity.key', add_proj_milestone)
            info_resp.check_response('data.activity.type', 'milestone')

    @story('T130958 里程碑：拖拽更新里程碑完成时间')
    def test_update_proj_plan_milestones_endtime(self, add_proj_milestone):
        with step('移动鼠标点击编辑完成日期xxx”'):
            end_time = mocks.day_timestamp(1)
            Ra.fast_update_proj_milestone_info(add_proj_milestone, end_time)
        with step('查看里程碑详情，验证完成时间'):
            info_resp = Ra.get_proj_plan_info(add_proj_milestone)
            resp_end_time = info_resp.value('data.activity.endTime')
            assert timestamp_time(resp_end_time) == timestamp_time(end_time)

    @story('T137932 项目计划甘特图：添加完成-开始关系（里程碑与计划）')
    def test_add_milestone_and_plan_relation(self, add_proj_milestone):
        with step('前置条件， 创建一个计划和里程碑'):
            plan_key = Ra.add_plans_or_milestones()
            milestone_key = add_proj_milestone
        with step('程碑A右侧与计划B左侧连接,建立完成-开始关系'):
            rl_resp = Ra.add_ppm_relation('ets', milestone_key, plan_key)
            resp_plan_start_time = Ra.get_proj_plan_info(plan_key).value('data.activity.startTime')
            resp_milestones_end_time = Ra.get_proj_plan_info(milestone_key).value('data.activity.endTime')
            # 里程碑的完成时间早于计划的开始时间
            assert timestamp_time(resp_milestones_end_time) < timestamp_time(resp_plan_start_time)
        with step('将里程碑A的完成时间拖拽到计划B开始时间之后'):
            end_time = mocks.day_timestamp(4)
            Ra.fast_update_proj_milestone_info(add_proj_milestone, end_time)
            resp_plan_start_time = Ra.get_proj_plan_info(plan_key).value('data.activity.startTime')
            resp_milestones_end_time = Ra.get_proj_plan_info(milestone_key).value('data.activity.endTime')
            # 自动更新计划的开始时间晚于里程碑的完成时间
            assert timestamp_time(resp_milestones_end_time) < timestamp_time(resp_plan_start_time)

    @story('T137936 项目计划甘特图：添加完成-完成关系（里程碑与里程碑）')
    def test_proj_plan_add_milestones_ete(self, add_proj_milestone):
        with step('前置条件 创建两个里程碑'):
            milestone_a_key = add_proj_milestone
            milestone_b_key = Ra.add_plans_or_milestones(p_type='milestone')
        with step('建立完成-完成的前后置关系'):
            rl_resp = Ra.add_ppm_relation('ete', milestone_a_key, milestone_b_key)
            resp_milestones_a_end_time = Ra.get_proj_plan_info(milestone_a_key).value(
                'data.activity.endTime')
            resp_milestones_b_end_time = Ra.get_proj_plan_info(milestone_b_key).value(
                'data.activity.endTime')
            assert timestamp_time(resp_milestones_a_end_time) == timestamp_time(resp_milestones_b_end_time)

        with step('将里程碑A的完成时间拖拽到里程碑B完成时间之后'):
            Ra.fast_update_proj_milestone_info(milestone_a_key, mocks.day_timestamp(5))
            resp_milestones_a_end_time = Ra.get_proj_plan_info(milestone_a_key).value(
                'data.activity.endTime')
            resp_milestones_b_end_time = Ra.get_proj_plan_info(milestone_b_key).value(
                'data.activity.endTime')
            # 修改里程碑A的完成时间，里程碑B的完成时间自动更新与A的完成时间相同
            assert timestamp_time(resp_milestones_a_end_time) == timestamp_time(resp_milestones_b_end_time)
