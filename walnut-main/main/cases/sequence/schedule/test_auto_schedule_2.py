from falcons.com.nick import feature, story, fixture, step, parametrize

from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra


@fixture(scope='module', autouse=True)
def add_plan_component():
    # 1.先添加一个【项目计划】 组件
    PrjAction.add_prj_plan_component()


@fixture(scope='module')
def cache_key():
    return {}


@feature('项目计划-自动排期')
class TestAutoSchedule:
    """"""

    def external(self, cache_key):
        # 添加项目计划
        plan_key = Ra.add_plans_or_milestones()
        p_key = plan_key.split('-')[1]
        # 添加里程碑
        milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
        m_key = milestone_key.split('-')[1]

        cache_key |= {'plan_key': plan_key, 'milestone_key': milestone_key, 'p_key': p_key, 'm_key': m_key}

    @story('T152782 没有任何计划时，点击「自动排期」')
    def test_no_plans(self):
        auto = Ra.auto_schedule()
        auto.check_response('success_count', 0)

    @story('T152786 项目计划中没有前后置关系，点击「自动排期」')
    def test_no_prefix_and_post(self, cache_key):
        with step('前置条件'):
            self.external(cache_key)

        with step('点击「自动排期」'):
            auto = Ra.auto_schedule()
            auto.check_response('success_count', 0)

    @story('T152863 仅存在计划和里程碑且存在前后置关系，点击自动排期')
    def test_plan_and_milestone_link(self, cache_key):
        with step('前置条件'):
            self.external(cache_key)

            # 计划1和里程碑1存前后置依赖关系（完成-完成）：计划1完成后，里程碑1才能完成
            rl_resp = Ra.add_ppm_relation('ete', cache_key['plan_key'], cache_key['milestone_key'])
            rl_key = rl_resp.value('data.updateActivity.key').split('-')[1]

        with step('点击「自动排期」'):
            auto = Ra.auto_schedule()
            auto.check_response('success_count', 0)

        with step('检查计划1和里程碑1的前后置关系'):
            links = Ra.query_relation_links(cache_key['m_key'])
            link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in link_keys
