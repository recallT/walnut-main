from falcons.com.nick import feature, story, fixture, step

from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra
from main.actions.task import TaskAction


@fixture(scope='module', autouse=True)
def add_plan_component():
    # 1.先添加一个【项目计划】 组件
    PrjAction.add_prj_plan_component()


@fixture()
def prepare():
    # 创建测试任务
    tasks, backup_task_uuid = TaskAction.new_issue_batch()

    if TaskAction.wait_to_done(backup_task_uuid):
        # 3. 添加两个测试计划
        plan_a = Ra.add_plans_or_milestones()
        plan_b = Ra.add_plans_or_milestones()

        # 4. 添加任务到计划中 task 1- 3 == 计划A , task 4 5 == 计划B
        Ra.external_activity(plan_a, *tasks[:3])
        Ra.external_activity(plan_b, *tasks[3:5])
        # 5. 创建里程碑1
        milestone = Ra.add_plans_or_milestones('milestone')

        p = {
            'tasks': tasks,
            'plan': [plan_a, plan_b],
            'milestone': milestone,
            'plan_uuid': [plan_a.split('-')[1], plan_b.split('-')[1]],
            'milestone_uuid': milestone.split('-')[1]
        }

        return p


@feature('项目计划-列表操作')
class TestPlanListOpt:

    @story('T155029 删除存在前后置依赖的计划（计划-计划）')
    def test_delete_plan_and_plan_relation(self, prepare):
        p = prepare['plan']
        p_uuid = prepare['plan_uuid']

        # 存在前后置依赖关系（开始-开始）：计划A开始后，计划B才能开始
        rl_resp = Ra.add_ppm_relation('ete', p[0], p[1])
        rl_key = rl_resp.value('data.updateActivity.key').split('-')[1]

        with step('查看计划A后置影响列表'):
            links = Ra.query_relation_links(p_uuid[0], 'post')
            post_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in post_link_keys

        with step('查看计划B前置依赖列表'):
            links = Ra.query_relation_links(p_uuid[1])
            pre_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in pre_link_keys

        with step('删除计划A'):
            del_key = Ra.del_plans_or_milestones(p[0])
            assert del_key == p[0]

        with step('查看计划B前置依赖列表'):
            links = Ra.query_relation_links(p_uuid[1])
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert pre_link_keys == []

    @story('T155030 删除存在前后置依赖的计划（计划-里程碑）')
    def test_delete_plan_and_milestone_relation(self, prepare):
        p = prepare['plan'][0]
        p_uuid = prepare['plan_uuid'][0]
        m = prepare['milestone']
        m_uuid = prepare['milestone_uuid']

        # 存在前后置依赖关系（完成-完成）：里程碑C完成后，计划A才能完成
        rl_resp = Ra.add_relation('ete', m, p)
        rl_key = rl_resp.value('data.addActivityRelationLink.key')

        with step('查看计划A前置依赖列表'):
            links = Ra.query_relation_links(p_uuid)
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

        with step('查看里程碑C后置影响列表'):
            links = Ra.query_relation_links(m_uuid, 'post')
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

        with step('删除计划A'):
            del_key = Ra.del_plans_or_milestones(p)
            assert del_key == p

        with step('查看里程碑C后置影响列表'):
            links = Ra.query_relation_links(m_uuid, 'post')
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert post_link_keys == []

    @story('T155031 删除存在前后置依赖的计划（计划-工作项）')
    def test_delete_plan_and_task_relation(self, prepare):
        p = prepare['plan'][0]
        p_uuid = prepare['plan_uuid'][0]
        t = prepare['tasks'][4]

        # 存在前后置依赖关系（开始-开始）：计划A开始后，任务B才能开始
        rl_resp = Ra.add_relation('sts', p, t)
        rl_key = rl_resp.value('data.addActivityRelationLink.key')

        with step('查看计划A后置影响列表'):
            links = Ra.query_relation_links(p_uuid, 'post')
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

        with step('查看任务B前置依赖列表'):
            links = Ra.query_relation_links(t)
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

        with step('删除计划A'):
            del_key = Ra.del_plans_or_milestones(p)
            assert del_key == p

        with step('查看任务B前置依赖列表'):
            links = Ra.query_relation_links(t)
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert pre_link_keys == []

    @story('T155044 删除存在前后置依赖的计划后，再次新建重名计划检查前后置关系')
    def test_rename_plan_relation(self, prepare):
        p = prepare['plan']
        p_uuid = prepare['plan_uuid']

        # 存在前后置依赖关系（开始-开始）：计划A开始后，计划B才能开始
        rl_resp = Ra.add_ppm_relation('ete', p[0], p[1])
        rl_key = rl_resp.value('data.updateActivity.key').split('-')[1]

        with step('查看计划A后置影响列表'):
            links = Ra.query_relation_links(p_uuid[0], 'post')
            post_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in post_link_keys

        with step('查看计划B前置依赖列表'):
            links = Ra.query_relation_links(p_uuid[1])
            pre_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in pre_link_keys

        with step('删除计划A'):
            del_key = Ra.del_plans_or_milestones(p[0])
            assert del_key == p[0]

        with step('查看计划B前置依赖列表'):
            links = Ra.query_relation_links(p_uuid[1])
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert pre_link_keys == []

    @story('T155032 移除存在前后置依赖的工作项（计划-工作项）')
    def test_move_plan_and_task_relation(self, prepare):
        p = prepare['plan'][0]
        p_uuid = prepare['plan_uuid'][0]
        t = prepare['tasks'][4]

        # 存在前后置依赖关系（开始-开始）：计划A开始后，任务B才能开始
        rl_resp = Ra.add_relation('sts', p, t)
        rl_key = rl_resp.value('data.addActivityRelationLink.key')

        with step('查看计划A后置影响列表'):
            links = Ra.query_relation_links(p_uuid, 'post')
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

        with step('查看任务B前置依赖列表'):
            links = Ra.query_relation_links(t)
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

        with step('移除任务B'):
            key = Ra.task_relation_plan_key(t)

            del_key = Ra.del_plans_or_milestones(key)
            assert key in del_key

        with step('查看计划A的后置影响列表'):
            links = Ra.query_relation_links(p_uuid, 'post')
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

        with step('查看任务B前置依赖列表'):
            links = Ra.query_relation_links(t)
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

        with step('计划B下再次关联「任务B」'):
            Ra.external_activity(p, t)

    @story('T155034 移除存在前后置依赖的工作项（工作项-里程碑）')
    def test_move_task_and_milestone_relation(self, prepare):
        p = prepare['plan']
        t = prepare['tasks'][4]
        m = prepare['milestone']
        m_uuid = prepare['milestone_uuid']

        # 存在前后置依赖关系（完成-完成）：里程碑C完成后，任务B才能完成
        rl_resp = Ra.add_relation('ete', m, t)
        rl_key = rl_resp.value('data.addActivityRelationLink.key')

        with step('查看任务B前置依赖列表'):
            links = Ra.query_relation_links(t)
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

        with step('查看里程碑C后置影响列表'):
            links = Ra.query_relation_links(m_uuid, 'post')
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

        with step('移除任务B'):
            key = Ra.task_relation_plan_key(t)

            del_key = Ra.del_plans_or_milestones(key)
            assert key in del_key

        with step('查看任务B前置依赖列表'):
            links = Ra.query_relation_links(t)
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

        with step('查看里程碑C后置影响列表'):
            links = Ra.query_relation_links(m_uuid, 'post')
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

        with step('再次添加任务B到计划B下'):
            Ra.external_activity(p[1], t)

    @story('T155040 移除存在前后置依赖的工作项（工作项-工作项）')
    def test_move_task_and_task_relation(self, prepare):
        t = prepare['tasks']
        p = prepare['plan']

        # 存在前后置依赖关系（开始-完成）：缺陷A开始后，任务B才能完成
        rl_resp = Ra.add_relation('ste', t[0], t[1])
        rl_key = rl_resp.value('data.addActivityRelationLink.key')

        with step('查看任务B前置依赖列表'):
            links = Ra.query_relation_links(t[1])
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

        with step('查看缺陷A后置影响列表'):
            links = Ra.query_relation_links(t[0], 'post')
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

        with step('移除任务B'):
            key = Ra.task_relation_plan_key(t[1])

            del_key = Ra.del_plans_or_milestones(key)
            assert key in del_key

        with step('查看任务B前置依赖列表'):
            links = Ra.query_relation_links(t[1])
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

        with step('查看缺陷A后置影响列表'):
            links = Ra.query_relation_links(t[0], 'post')
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

        with step('关联任务B到计划A下'):
            Ra.external_activity(p[0], t[1])
