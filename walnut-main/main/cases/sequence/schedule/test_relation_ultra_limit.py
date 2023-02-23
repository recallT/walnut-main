from falcons.com.nick import feature, story, fixture, step
from falcons.helper.functions import parallel_task

from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra
from main.actions.task import TaskAction


@fixture(scope='module', autouse=True)
def add_component():
    # 1.先添加一个【项目计划】 组件
    PrjAction.add_prj_plan_component()


@fixture(scope='class')
def external():
    # 创建项目计划
    plan_key = Ra.add_plans_or_milestones()
    p_key = plan_key.split('-')[1]

    # 创建测试任务
    tasks, backup_task_uuid = TaskAction.new_issue_batch(batch_no=101)
    if TaskAction.wait_to_done(backup_task_uuid):
        task = tasks

        # 关联任务
        Ra.external_activity(plan_key, *task)

        # 已有计划下添加里程碑
        milestone_key = Ra.add_plans_or_milestones(p_type='milestone', parent=p_key).split('-')[1]

        return {'plan_key': p_key, 'milestone_key': milestone_key, 'tasks': task}


def activity_link_add(task_uuid, target):
    re = Ra.add_relation('ets', source=task_uuid, target=target)
    rl_key = re.value('data.addActivityRelationLink.key')

    links = Ra.query_relation_links(target)
    post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

    assert rl_key in post_link_keys


@feature('任务管理-后置影响')
class TestPostRelation:

    @story('T155165 已添加100条后置影响的工作项添加后置影响')
    @story('154198 添加的工作项后置影响已超过100条')
    @story('155164 任务管理-后置影响：添加的工作项前置依赖已超过100条')
    def test_add_100_post_relation(self, external):
        ...  # 暂不验证大批量前后置影响用例，有需要时再放开

        # task = external['tasks']
        #
        # with step('新增100条后置影响'):
        #     task_params = []
        #     for t in task[1:]:
        #         task_params.append((task[0], t))
        #
        #     parallel_task(activity_link_add, *task_params)
        # with step('新增第101条后置影响'):
        #     re = Ra.add_relation('ete', source=task[0], target=external['milestone_key'], code=403)
        #     re.check_response('errcode', 'LimitExceeded', check_type='contains')


@feature('任务管理-前置影响')
class TestPrefixRelation:

    @story('已添加100条前置影响的工作项添加后置影响')
    @story('153003 任务管理-前置依赖：已添加100条前置依赖的工作项添加前置依赖')
    @story('155345 任务管理-前置依赖：已添加100条前置依赖的工作项，添加后置影响')
    def test_add_100_prefix_relation(self, external):
        ...  # 暂不验证大批量前后置影响用例，有需要时再放开

        # task = external['tasks']
        #
        # with step('新增100条前置置影响'):
        #     task_params = []
        #     for t in task[1:]:
        #         task_params.append((t, task[0]))
        #
        #     parallel_task(activity_link_add, *task_params)
        #
        # with step('新增第101条后置影响'):
        #     re = Ra.add_relation('ete', source=external['milestone_key'], target=task[0], code=403)
        #     re.check_response('errcode', 'LimitExceeded', check_type='contains')
        #
        # with step('T155164 添加的工作项前置依赖已超过100条'):
        #     re = Ra.add_relation('ets', source=task[1], target=task[0], code=403)
        #     re.check_response('errcode', 'LimitExceeded', check_type='contains')
