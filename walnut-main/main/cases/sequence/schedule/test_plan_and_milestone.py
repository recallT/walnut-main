from falcons.check import CheckerChain, Checker
from falcons.com.nick import feature, story, fixture, step

from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra
from main.actions.task import TaskAction
from main.api import project as prj
from main.params import relation as rel


@fixture(scope='module')
def task():
    """自动创建6条任务 用于测试"""
    # 1.先添加一个【项目计划】 组件
    PrjAction.add_prj_plan_component()
    # 2. 创建测试任务
    tasks, backup_task_uuid = TaskAction.new_issue_batch()

    if TaskAction.wait_to_done(backup_task_uuid):
        return tasks


@fixture(scope='class', autouse=True)
def external(task, relation_key):
    # 创建4个项目计划
    activity_key = [Ra.add_plans_or_milestones() for k in range(4)]
    plan_key = [k.split('-')[1] for k in activity_key]
    # 关联任务
    Ra.external_activity(activity_key[0], task[0])
    # 已有计划下添加里程碑
    m_key = [Ra.add_plans_or_milestones(p_type='milestone', parent=i) for i in
             [plan_key[2], plan_key[3]]]
    milestone_key = [m.split('-')[1] for m in m_key]

    relation_key |= {
        'plan_key': plan_key, 'milestone_key': milestone_key,
        'la_key': activity_key, 'lm_key': m_key
    }  # 4个plan_key, 2个milestone_key


@fixture(scope='class')
def relation_key():
    """后置依赖关系key缓存"""

    return {}


@feature('计划信息管理-前置依赖')
class TestPlanInfoPrefix(CheckerChain):

    @story('T153129 添加前置依赖「完成-完成」')
    def test_plan_prefix_end_to_end(self, relation_key):
        la_key = relation_key['la_key']
        p_key = relation_key['plan_key']

        with step('选中计划「计划C」添加'):
            rl_resp = Ra.add_ppm_relation('ete', la_key[0], la_key[1])
            rl_key = rl_resp.value('data.updateActivity.key').split('-')[1]

            links = Ra.query_relation_links(p_key[1])
            pre_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in pre_link_keys

        with step('查看被关联计划C的后置影响列表以及动态'):
            links = Ra.query_relation_links(p_key[0], 'post')
            post_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in post_link_keys

    @story('T153130 添加前置依赖「完成-开始」')
    def test_plan_prefix_end_to_start(self, task, relation_key):
        p_key = relation_key['plan_key']

        with step('选中「任务A」添加'):
            rl_resp = Ra.add_relation('ets', p_key[1], task[0])
            rl_key = rl_resp.value('data.addActivityRelationLink.key')

            links = Ra.query_relation_links(task[0])
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

        with step('查看被关联的任务A后置影响列表以及动态'):
            links = Ra.query_relation_links(p_key[1], 'post')
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

    @story('T153131 添加前置依赖「开始-完成」')
    def test_plan_prefix_start_to_end(self, task, relation_key):
        p_key = relation_key['plan_key']

        with step('选中「任务B」添加'):
            rl_resp = Ra.add_relation('ste', p_key[1], task[1])
            rl_key = rl_resp.value('data.addActivityRelationLink.key')

            links = Ra.query_relation_links(task[1])
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

        with step('查看被关联的任务A后置影响列表以及动态'):
            links = Ra.query_relation_links(p_key[1], 'post')
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

    @story('T153132 添加前置依赖「开始-开始」')
    def test_plan_prefix_start_to_start(self, relation_key):
        la_key = relation_key['la_key']
        p_key = relation_key['plan_key']

        with step('选中计划「计划B」添加'):
            rl_resp = Ra.add_ppm_relation('sts', la_key[1], la_key[0])
            rl_key = rl_resp.value('data.updateActivity.key').split('-')[1]

            links = Ra.query_relation_links(p_key[0])
            pre_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in pre_link_keys

        with step('查看被关联计划C的后置影响列表以及动态'):
            links = Ra.query_relation_links(p_key[1], 'post')
            post_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in post_link_keys


@feature('计划信息管理-后置依赖')
class TestPlanInfoPost(CheckerChain):

    @story('T153137 添加后置依赖「完成-完成」')
    def test_plan_post_end_to_end(self, relation_key):
        la_key = relation_key['la_key']
        p_key = relation_key['plan_key']

        with step('选中计划「计划C」添加'):
            rl_resp = Ra.add_ppm_relation('ete', la_key[0], la_key[1])
            rl_key = rl_resp.value('data.updateActivity.key').split('-')[1]

            links = Ra.query_relation_links(p_key[0], 'post')
            post_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in post_link_keys

        with step('查看被关联计划C的前置影响列表以及动态'):
            links = Ra.query_relation_links(p_key[1])
            pre_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in pre_link_keys

    @story('T153134 添加后置依赖「完成-开始」')
    def test_plan_post_end_to_start(self, task, relation_key):
        p_key = relation_key['plan_key']

        with step('选中「任务A」添加'):
            rl_resp = Ra.add_relation('ets', p_key[0], task[1])
            rl_key = rl_resp.value('data.addActivityRelationLink.key')

            links = Ra.query_relation_links(p_key[0], 'post')
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

        with step('查看被关联的任务A前置影响列表以及动态'):
            links = Ra.query_relation_links(task[1])
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

    @story('T153136 添加后置依赖「开始-完成」')
    def test_plan_post_start_to_end(self, task, relation_key):
        p_key = relation_key['plan_key']
        m_key = relation_key['milestone_key']

        with step('选中「里程碑A」添加'):
            rl_resp = Ra.add_relation('ste', p_key[0], m_key[0])
            rl_key = rl_resp.value('data.addActivityRelationLink.key')

            links = Ra.query_relation_links(p_key[0], 'post')
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

        with step('查看被关联的任务A前置影响列表以及动态'):
            links = Ra.query_relation_links(m_key[0])
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

    @story('T153138 添加后置依赖「开始-开始」')
    def test_plan_post_start_to_start(self, relation_key):
        la_key = relation_key['la_key']
        p_key = relation_key['plan_key']

        with step('选中计划「计划C」添加'):
            rl_resp = Ra.add_ppm_relation('sts', la_key[0], la_key[1])
            rl_key = rl_resp.value('data.updateActivity.key').split('-')[1]

            links = Ra.query_relation_links(p_key[0], 'post')
            post_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in post_link_keys

        with step('查看被关联计划C的前置影响列表以及动态'):
            links = Ra.query_relation_links(p_key[1])
            pre_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in pre_link_keys


@feature('里程碑管理-前置依赖')
class TestMilestonePrefix(CheckerChain):

    @story('T153139 里程碑添加前置依赖「完成-完成」')
    def test_milestone_prefix_end_to_end(self, task, relation_key):
        m_key = relation_key['milestone_key']

        with step('选中「任务A」添加'):
            rl_resp = Ra.add_relation('ete', task[0], m_key[0])
            rl_key = rl_resp.value('data.addActivityRelationLink.key').split('-')[1]

            links = Ra.query_relation_links(m_key[0])
            pre_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in pre_link_keys

        with step('查看被关任务A的后置影响列表以及动态'):
            links = Ra.query_relation_links(task[0], 'post')
            post_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in post_link_keys

    @story('T153143 里程碑添加前置依赖「开始-完成」')
    def test_milestone_prefix_start_to_end(self, relation_key):
        lm_key = relation_key['lm_key']
        m_key = relation_key['milestone_key']
        la_key = relation_key['la_key']
        p_key = relation_key['plan_key']

        with step('选中「计划B」添加'):
            rl_resp = Ra.add_ppm_relation('ste', la_key[1], lm_key[1])
            rl_key = rl_resp.value('data.updateActivity.key').split('-')[1]

            links = Ra.query_relation_links(m_key[1])
            pre_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in pre_link_keys

        with step('查看被关联的计划B后置影响列表以及动态'):
            links = Ra.query_relation_links(p_key[1], 'post')
            post_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert f'activity_relation_link-{rl_key}' in post_link_keys


@feature('里程碑管理-后置依赖')
class TestMilestonePost(CheckerChain):

    @story('T153145 里程碑添加后置依赖「完成-开始」')
    def test_milestone_post_end_to_start(self, task, relation_key):
        p_key = relation_key['plan_key']
        m_key = relation_key['milestone_key']

        with step('选中「计划C」添加'):
            rl_resp = Ra.add_relation('ets', m_key[0], p_key[1])
            rl_key = rl_resp.value('data.addActivityRelationLink.key')

            links = Ra.query_relation_links(m_key[0], 'post')
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

        with step('查看被关联的计划C前置影响列表以及动态'):
            links = Ra.query_relation_links(p_key[1])
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

    @story('T153147 里程碑添加后置依赖「完成-完成」')
    def test_plan_post_end_to_end(self, task, relation_key):
        m_key = relation_key['milestone_key']

        with step('选中[任务B]添加'):
            rl_resp = Ra.add_relation('ete', m_key[0], task[1])
            rl_key = rl_resp.value('data.addActivityRelationLink.key')

            links = Ra.query_relation_links(m_key[0], 'post')
            post_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert rl_key in post_link_keys

        with step('查看被关联任务B的前置影响列表以及动态'):
            links = Ra.query_relation_links(task[1])
            pre_link_keys = str([k['key'] for k in links.value('data.activityRelationLinks')])

            assert rl_key in pre_link_keys


@feature('前后置影响其他操作')
class TestMoreOpt(Checker):

    @story('T154193 查看历史快照：工作项存在前后置连线时创建快照对比')
    def test_snapshot(self, task):
        with step('工作项A和工作项B存前后置依赖关系（完成-完成）'):
            re = Ra.add_relation('ete', source=task[0], target=task[1])
            rl_key = re.value('data.addActivityRelationLink.key')

            links = Ra.query_relation_links(task[1])
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

        with step('创建快照'):
            p_key = Ra.add_activity_release()
            key = p_key.value('data.addActivityRelease.key')

        with step('查看历史快照'):
            param = rel.gantt_history(key)[0]
            q = self.call(prj.ItemGraphql, param)
            data = q.value('data.activityRelease.key')
            assert data == key

    @story('T144676 导出项目计划：导出存在多个前后置依赖数据的项目计划')
    def test_export_project_plan_1(self, task, relation_key):
        la_key = relation_key['la_key']
        p_key = relation_key['plan_key']
        m_key = relation_key['milestone_key']

        with step('添加：前置依赖'):
            Ra.add_ppm_relation('sts', la_key[1], la_key[0])
            Ra.add_relation('ets', p_key[1], task[0])

        with step('添加：后置依赖'):
            Ra.add_relation('ste', p_key[0], m_key[0])
            Ra.add_ppm_relation('ete', la_key[0], la_key[1])

        with step('项目计划点击更多-导出项目计划'):
            Ra.export_project_plan()

    @story('T154199 导出项目计划：导出存在前后置依赖的工作项的项目计划')
    def test_export_project_plan_2(self, task, relation_key):
        with step('存在依赖关系'):
            Ra.add_relation('sts', task[0], task[1])
            Ra.add_relation('ste', task[0], task[1])
            Ra.add_relation('ets', task[0], task[1])

        with step('项目计划点击更多-导出项目计划'):
            Ra.export_project_plan()
