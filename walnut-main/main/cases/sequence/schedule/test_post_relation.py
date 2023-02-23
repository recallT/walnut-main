from falcons.check import CheckerChain
from falcons.com.nick import feature, story, fixture, step

from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra
from main.actions.task import TaskAction


@fixture(scope='module')
def task():
    """自动创建6条任务 用于测试"""
    # 1.先添加一个【项目计划】 组件
    PrjAction.add_prj_plan_component()
    # 2. 创建测试任务
    tasks, backup_task_uuid = TaskAction.new_issue_batch()

    if TaskAction.wait_to_done(backup_task_uuid):
        return tasks


@fixture(scope='module', autouse=True)
def external(task, post_key):
    # 创建项目计划A
    p_key = Ra.add_plans_or_milestones()
    plan_key = p_key.split('-')[1]
    # 创建项目计划B
    b_key = Ra.add_plans_or_milestones()
    plan_b = b_key.split('-')[1]

    # 关联任务
    Ra.external_activity(p_key, task[0])
    # 已有计划下添加里程碑
    m_key = Ra.add_plans_or_milestones(p_type='milestone', parent=plan_key)
    milestone_key = m_key.split('-')[1]

    post_key |= {'plan_key': plan_key, 'milestone_key': milestone_key, 'plan_b': plan_b}


@fixture(scope='module')
def post_key():
    """后置依赖关系key缓存"""

    return {}


@feature('任务管理-后置影响')
class TestPostRelation(CheckerChain):

    @story('T153048 添加后置影响「完成-完成」')
    def test_end_to_end_add(self, task, post_key):
        with step('选中「里程碑B」'):
            re = Ra.add_relation('ete', source=task[0], target=post_key['milestone_key'])
            rl_key = re.value('data.addActivityRelationLink.key')

            links = Ra.query_relation_links(post_key['milestone_key'])
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

    @story('T153053 添加后置影响「完成-开始」')
    def test_end_to_start_add(self, task):
        with step('选中「任务B」'):
            re = Ra.add_relation('ets', source=task[0], target=task[1])
            rl_key = re.value('data.addActivityRelationLink.key')

            links = Ra.query_relation_links(task[1])
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

        with step('查看动态'):
            # 检查任务动态
            resp = TaskAction.task_messages(task[0])
            msg = resp.value('messages[0]')
            assert msg['ext']['relate_type'] == 'end_to_start'

    @story('T153058 添加后置影响「开始-完成」')
    def test_start_to_end_add(self, task, post_key):
        with step('选中计划「计划B」'):
            re = Ra.add_relation('ste', source=task[0], target=post_key['plan_b'])
            rl_key = re.value('data.addActivityRelationLink.key')

            links = Ra.query_relation_links(post_key['plan_b'])
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

    @story('T153065 添加后置影响「开始-开始」')
    def test_start_to_start_add(self, task, post_key):
        with step('选中「任务C」'):
            re = Ra.add_relation('sts', source=task[0], target=task[2])
            rl_key = re.value('data.addActivityRelationLink.key')

            links = Ra.query_relation_links(task[2])
            post_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in post_link_keys

    @story('T153049 进入添加后置影响弹窗后，选择的里程碑被删除')
    def test_milestone_delete(self, task):
        re = Ra.add_relation(rl_type='ete', source=task[0], target='4mZxzgt2', code=404)
        re.check_response('errcode', 'NotFound.Activity')

    @story('T153050 进入添加后置影响弹窗后，选择的计划被删除')
    def test_plan_delete(self, task):
        re = Ra.add_relation(rl_type='sts', source=task[0], target='2P6gFjP2', code=404)
        re.check_response('errcode', 'NotFound.Activity')

    @story('T153063 进入添加后置影响弹窗后，某个工作项被移出项目计划')
    def test_work_delete(self, task):
        re = Ra.add_relation(rl_type='sts', source=task[0], target='7CU6yrjuPcTQ9tN2', code=404)
        re.check_response('errcode', 'NotFound.Task')

    @story('T153060 选择的工作项未关联进当前项目的项目计划时，添加后置影响')
    def test_task_no_associated(self, task, post_key):
        re = Ra.add_relation('ste', source=task[1], target=post_key['plan_key'], code=400)
        re.check_response('errcode', 'InvalidParameter.Activity.RelationType')

    @story('T153055 后置影响弹窗中不选择任何内容，点击「添加」')
    def test_no_choose_content(self, task):
        re = Ra.add_relation('ste', source=task[1], target='', code=400)
        re.check_response('errcode', 'ActivityRelation.target', check_type='contains')

    @story('T154103 添加后置影响弹窗-搜索')
    def test_search(self, task):
        re = Ra.all_gantt_data()

    @story('T153292 没有工作项计划开始日期、计划完成日期编辑权限时添加后置影响')
    def test_no_start_or_end_date(self, task, post_key):
        # 将task[1]的开始时间和结束时间置为空
        up_start = {
            "field_uuid": "field027",  # 计划开始时间
            "type": 5,
            "value": None
        }
        TaskAction.update_task_info(task[1], up_start)

        end_start = {
            "field_uuid": "field028",  # 计划开始时间
            "type": 5,
            "value": None
        }
        TaskAction.update_task_info(task[1], end_start)

        Ra.add_relation('ste', source=task[1], target=post_key['plan_b'])
