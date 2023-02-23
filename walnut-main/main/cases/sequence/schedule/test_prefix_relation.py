"""
@File    ：test_prefix_relation.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/28
@Desc    ：工作项前置关联测试用例
"""
import time

from falcons.check import CheckerChain
from falcons.com.nick import feature, fixture, story, step

from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra
from main.actions.task import TaskAction


@fixture(scope='module')
def task():
    """自动创建6条任务 用于测试"""
    # 1.先添加一个【项目计划】 组件
    PrjAction.add_prj_plan_component()
    # 2. 创建测试任务
    tasks, backup_task_uuid = TaskAction.new_issue_batch(batch_no=8)

    if TaskAction.wait_to_done(backup_task_uuid):
        return tasks


@fixture(scope='module')
def relation_key():
    """前置依赖关系 key 缓存"""

    return []


@fixture(scope='module')
def del_plan_component():
    """移除项目组件"""
    yield

    PrjAction.remove_prj_plan_component()


@feature('任务管理')
class TestPrePostRelation(CheckerChain):
    """"""

    @story('152996 任务管理-前置依赖：添加前置依赖「开始-开始」')
    def test_add_prefix_sts(self, task):
        """"""

        rl_resp = Ra.add_relation('sts', task[1], task[0])
        rl_key = rl_resp.value('data.addActivityRelationLink.key')
        time.sleep(1)
        links = Ra.query_relation_links(task[0])
        pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]
        assert rl_key in pre_link_keys

    @story('153005 任务管理-前置依赖：添加前置依赖「开始-完成」')
    def test_add_prefix_ste(self, task):
        """"""

        rl_resp = Ra.add_relation('ste', task[2], task[0])
        rl_key = rl_resp.value('data.addActivityRelationLink.key')

        links = Ra.query_relation_links(task[0])
        pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

        assert rl_key in pre_link_keys

    @story('153006 任务管理-前置依赖：添加前置依赖「完成-开始」')
    def test_add_prefix_ets(self, task):
        """"""

        rl_resp = Ra.add_relation('ets', task[3], task[0])
        rl_key = rl_resp.value('data.addActivityRelationLink.key')

        links = Ra.query_relation_links(task[0])
        pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

        assert rl_key in pre_link_keys

    @story('153007 任务管理-前置依赖：添加前置依赖「完成-完成」')
    def test_add_prefix_ete(self, task):
        """"""

        rl_resp = Ra.add_relation('ete', task[4], task[0])
        rl_key = rl_resp.value('data.addActivityRelationLink.key')

        links = Ra.query_relation_links(task[0])
        pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

        assert rl_key in pre_link_keys

    # @mark.xfail(reason='与用例预期不符')
    # @story('155206 任务管理-前置依赖：选择的工作项没有设置计划开始日期和计划结束日期')
    # def test_add_prefix_empty_begin_end_date(self, task):
    #     """"""
    #     defeat_uuid = TaskAction.new_issue()[0]
    #
    #     # 将缺陷添加到任务列表中存起来
    #     task.append(defeat_uuid)
    #     TaskAction.update_task_info(defeat_uuid, {
    #         'field_uuid': "field027",  # 计划开始时间
    #         "type": 5,
    #         "value": None
    #     })
    #     TaskAction.update_task_info(defeat_uuid, {
    #         'field_uuid': "field028",  # 计划结束时间
    #         "type": 5,
    #         "value": None
    #     })
    #
    #     # 预期失败 实际成功
    #     rl_resp = Ra.add_relation('ete', defeat_uuid, task[0], 404)

    @story('153000 任务管理-前置依赖：选择的工作项未关联进当前项目的项目计划时，添加前置依赖')
    def test_add_prefix_not_in_plan_list(self, task):
        """"""
        # 添加一个测试计划
        activity_key = Ra.add_plans_or_milestones()
        # 将工作项添加到测试计划中
        Ra.external_activity(activity_key, *task[4:-2])

        with step('检查前置依赖弹出列表'):
            gantt_list = Ra.all_gantt_data()

            # 取出工作项UUID
            task_uuids = [gl['task']['uuid'] for gl in gantt_list if gl['ganttDataType'] == 'task']
            # 工作项都在列表中
            for t in task[4:-2]:
                assert t in task_uuids

        task_a, task_b = task[-1], task[-3]
        with step('添加前置依赖'):
            # 添加一天前置依赖 end_to_end
            rl_resp = Ra.add_relation('ete', task_b, task_a)
            rl_key = rl_resp.value('data.addActivityRelationLink.key')

        with step('查看动态'):
            # 检查任务动态
            resp = TaskAction.task_messages(task_a)
            # 拿到最新的第一条消息
            msg = resp.value('messages[0]')
            assert msg['ext']['dependency_type'] == 'pre'
            assert msg['ext']['relate_type'] == 'end_to_end'

        with step('查看任务B的后置影响列表以及动态'):
            relation_resp = Ra.query_relation_links(task_b, 'post')
            rel_links = [r['key'] for r in relation_resp.value('data.activityRelationLinks')]

            assert rl_key in rel_links

        with step('进入项目计划，查看任务A和任务B的连线情况'):
            gantt_list = Ra.all_gantt_data()
            # 取出工作项
            activity_tasks = [gl for gl in gantt_list if gl['ganttDataType'] == 'task']
            # 获取工作项b的连线数据, 获取其后置数据 有b-指向 a，取 b 的 target 数据
            t = [a['target'] for a in activity_tasks if a['task']['uuid'] == task_b][0]
            # 检查 b 没有后置连线
            assert not t

        with step('1、在计划B下关联工作项「任务A」2、查看任务A和任务B是否存在前后置连线'):
            # 将任务A加入项目计划中
            Ra.external_activity(activity_key, task_a)

            gantt_list = Ra.all_gantt_data()
            # 取出工作项
            activity_tasks = [gl for gl in gantt_list if gl['ganttDataType'] == 'task']
            # 获取工作项b的连线数据, 获取其后置数据 有b-指向a，取 b 的 target 数据
            t_b = [a['target'] for a in activity_tasks if a['task']['uuid'] == task_b][0]
            # 检查 b 有后置连线
            assert t_b

            t_a = [a['source'] for a in activity_tasks if a['task']['uuid'] == task_a][0]
            # 检查 a 有后置连线
            assert t_a

    @story('153154 任务管理-前置依赖：前置依赖弹窗中多个里程碑排序')
    def test_add_prefix_milestone_sorting(self, task):
        """"""

        with step('添加几个里程碑'):
            ms_keys = []
            for _ in range(3):
                k = Ra.add_plans_or_milestones('milestone')
                ms_keys.append(k)

        gantt_list = Ra.all_gantt_data()
        ms_keys.reverse()
        # 取出里程碑 ganttDataType == milestone

        milestone_key_list = [gl['key'] for gl in gantt_list if gl['ganttDataType'] == 'milestone']

        for i in range(3):  # 校验排序问题
            assert ms_keys[i] == milestone_key_list[i]

    @story('153153 任务管理-前置依赖：前置依赖弹窗中多个计划排序')
    def test_add_prefix_plan_sorting(self, task):
        """"""

        with step('添加几个测试计划'):
            plan_keys = []
            for _ in range(3):
                k = Ra.add_plans_or_milestones()
                plan_keys.append(k)

        gantt_list = Ra.all_gantt_data()
        plan_keys.reverse()
        # 取出测试计划 ganttDataType == ppm_task

        ppm_task_key = [gl['key'] for gl in gantt_list if gl['ganttDataType'] == 'ppm_task']

        for i in range(3):  # 校验排序问题
            assert plan_keys[i] == ppm_task_key[i]

    @story('153009 任务管理-前置依赖：进入添加前置依赖弹窗后，某个工作项被移出项目计划')
    def test_add_prefix_ete_issue_not_in_plan(self, task):
        """就是普通的直接添加关联即可"""

        rl_resp = Ra.add_relation('sts', task[-1], task[0])
        rl_key = rl_resp.value('data.addActivityRelationLink.key')
        time.sleep(1)
        links = Ra.query_relation_links(task[0])
        pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]
        assert rl_key in pre_link_keys
