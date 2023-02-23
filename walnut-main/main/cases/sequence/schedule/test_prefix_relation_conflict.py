"""
@File    ：test_prefix_relation_conflict.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/30
@Desc    ：前置依赖冲突用例
"""
from falcons.com.nick import feature, fixture, story, step
from falcons.helper import functions as fc
from falcons.helper import mocks

from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra
from main.actions.task import TaskAction


@fixture(scope='module')
def prepare():
    """
    前置条件
    1、项目A中任务视图已开启「前置依赖」模块标签页，布局为「宽详情」
    2、用户A是项目A的管理员，拥有全部工作项的全部权限
    3、项目A项目计划中存在以下计划/里程碑/工作项
    计划A        开始时间-结束时间：2022年3月1日-2022年3月31日
      缺陷A      计划开始日期-计划结束日期：2022年3月5日-2022年3月6日
      用户故事A  计划开始日期-计划结束日期：2022年3月5日-2022年3月20日
    计划B          开始时间-结束时间：2022年3月01日-2022年3月31日
        任务B      计划开始日期-计划结束日期：2022年3月1日-2022年3月20日
        子任务B   计划开始日期-计划结束日期：2022年3月5日-2022年3月20日
    里程碑1     完成时间：2022年3月30日

    :return:
    """
    # 1.先添加一个【项目计划】 组件
    PrjAction.add_prj_plan_component()
    # 2. 创建测试任务
    tasks, backup_task_uuid = TaskAction.new_issue_batch()

    if TaskAction.wait_to_done(backup_task_uuid):
        # 3. 添加两个测试计划
        plan_a = Ra.add_plans_or_milestones()
        plan_b = Ra.add_plans_or_milestones()

        # 4. 添加任务到计划中
        Ra.external_activity(plan_a, *tasks[:3])
        Ra.external_activity(plan_b, *tasks[3:5])
        # 5. 创建里程碑1
        milestone = Ra.add_plans_or_milestones('milestone')
        p = {
            'tasks': tasks,
            'plan': [plan_a, plan_b],
            'milestone': milestone,
            'activity_keys': [],  # 用来缓存创建好的关联关系key
        }

        return p


@fixture(scope='module')
def clean_stuff():
    pass


@feature('任务管理-前置依赖')
class TestPrefixRelationConflict:
    """"""

    @story('153089 任务管理-前置依赖：被关联方计划周期冲突（工作项-工作项')
    def test_conflict_sts_task(self, prepare):
        """"""
        task = prepare['tasks']
        task_a, task_b = task[0], task[1]
        with step('将task a b 的起始时间设为冲突时间'):
            # 将task 1 2 的起始时间设为冲突时间
            # b 的 开始时间比a 的晚
            task_a_s_time = fc.plan_time('start', mocks.day_timestamp(1))
            task_a_e_time = fc.plan_time('end', mocks.day_timestamp(2))

            task_b_s_time = fc.plan_time('start', mocks.day_timestamp(3))
            task_b_e_time = fc.plan_time('end', mocks.day_timestamp(4))

            TaskAction.update_task_info(task_a, task_a_s_time)
            TaskAction.update_task_info(task_a, task_a_e_time)

            TaskAction.update_task_info(task_b, task_b_e_time)
            TaskAction.update_task_info(task_b, task_b_s_time)

        rl_key = self.add_pre_relation(task_a, task_b)
        # 用于缓存关联关系
        prepare['activity_keys'].append(rl_key)

        self.check_activity(task_a, task_b, 'task')

    @story('155025 任务管理-前置依赖：被关联方计划周期冲突（工作项-计划）')
    def test_conflict_sts_task_plan(self, prepare):
        """"""
        task = prepare['tasks']
        task_a, plan_b = task[0], prepare['plan'][1]
        with step('将task a, plan b 的起始时间设为冲突时间'):
            # 将task 1 2 的起始时间设为冲突时间
            # b 的 开始时间比a 的晚
            task_a_s_time = fc.plan_time('start', mocks.day_timestamp(1))
            task_a_e_time = fc.plan_time('end', mocks.day_timestamp(2))

            TaskAction.update_task_info(task_a, task_a_s_time)
            TaskAction.update_task_info(task_a, task_a_e_time)
            plan_s_time = {
                'start_time': mocks.day_timestamp(2),
                'end_time': mocks.day_timestamp(3)
            }
            Ra.update_plans_or_milestones(plan_b, **plan_s_time)

        self.add_pre_relation(task_a, plan_b)

        self.check_activity(task_a, plan_b, 'parent_ppm_task')

    @classmethod
    def add_pre_relation(cls, me, prefix, prefix_type='task', token=None):
        with step('选择前置依赖关系为：开始-开始'):
            # task_a 前置关联 plan_b
            t = 'sts'
            if prefix_type == 'milestone':
                t = 'ets'
            relation_resp = Ra.add_relation(t, prefix, me)
            rl_key = relation_resp.value('data.addActivityRelationLink.key')
            # 检查task_a 的前置关联列表

            links = Ra.query_relation_links(me)
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

            return rl_key

    @story('155026 任务管理-前置依赖：被关联方计划周期冲突（工作项-里程碑）')
    def test_conflict_sts_task_milestone(self, prepare):
        """"""
        task_a, milestone = prepare['tasks'][0], prepare['milestone']
        with step('将task a, milestone 的起始时间设为冲突时间'):
            # 将task 1 2 的起始时间设为冲突时间
            # b 的 开始时间比a 的晚
            task_a_s_time = fc.plan_time('start', mocks.day_timestamp(1))
            task_a_e_time = fc.plan_time('end', mocks.day_timestamp(2))

            TaskAction.update_task_info(task_a, task_a_s_time)
            TaskAction.update_task_info(task_a, task_a_e_time)
            # milestone 的时间默认在4周后，这里不用更新
        self.add_pre_relation(task_a, milestone, prefix_type='milestone')

        self.check_activity(task_a, milestone, 'milestone')

    @classmethod
    def check_activity(cls, me, prefix, collect_type, token=None):
        """
        检查
        :param token:
        :param me: 当前工作项
        :param prefix: 前置对象
        :param collect_type: task, milestone, parent_ppm_task, ppm_task
        :return:
        """

        # 检查 milestone 的关联结果
        gantt_list = Ra.all_gantt_data(token)
        # 取出任务计划
        activities = [gl for gl in gantt_list if gl['ganttDataType'] == collect_type]
        with step(f'检查{collect_type.upper()}连线情况'):
            # 获取工作项 milestone 的连线数据, 获取其后置数据 有b-指向 a，取 b 的 target 数据
            if collect_type == 'task':
                t = [a for a in activities if a['task']['uuid'] == prefix][0]
            else:
                t = [a for a in activities if a['key'] == prefix][0]

            # 检查 b 有后置连线
            assert t['target']
        with step('此节点存在前后置冲突'):
            # a 有前后置冲突警告 dependency
            # 获取工作项a的连线数据
            activity_tasks = [gl for gl in gantt_list if gl['ganttDataType'] == 'task']
            activity_a = [a for a in activity_tasks if a['task']['uuid'] == me][0]

            assert 'dependency' in activity_a['reminders'], '没查到前后置冲突提示'

    @story('154196 任务管理-前置依赖：检查前置依赖弹窗父子层级添加依赖结果')
    def test_conflict_sts_task_with_child(self, prepare):
        # 给task_b 添加子任务 sub_task_b
        task_b = prepare['tasks'][1]
        sub_task_b = TaskAction.new_issue(parent_uuid=task_b, issue_type_name='子任务')[0]

        # 添加父子层级的关联
        with step('选择子任务B，点击「添加」'):
            resp = Ra.add_relation('ete', sub_task_b, task_b)
            rl_key = resp.value('data.addActivityRelationLink.key')

            links = Ra.query_relation_links(task_b)
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

    @story('155672 任务管理-前置依赖：检查前置依赖弹窗父子层级添加依赖结果（计划）')
    def test_conflict_sts_task_with_child_relation_plan(self, prepare):
        # 给task_b 添加子任务 sub_task_b
        task_b = prepare['tasks'][1]
        plan_b = prepare['plan'][1]
        TaskAction.new_issue(parent_uuid=task_b, issue_type_name='子任务')

        # 添加父子层级的关联
        with step('选择计划B，点击「添加」'):
            resp = Ra.add_relation('ete', plan_b, task_b)
            rl_key = resp.value('data.addActivityRelationLink.key')

            links = Ra.query_relation_links(task_b)
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

    @story('154197 任务管理-前置依赖：进入前置依赖弹窗后，选择的前置依赖工作项变为当前工作项的子工作项')
    def test_conflict_sts_update_task_to_child(self, prepare):
        # 给task_b 添加子任务 sub_task_b
        task_b = prepare['tasks'][2]
        sub_task_b = TaskAction.new_issue(parent_uuid=task_b, issue_type_name='子任务')[0]

        # 添加父子层级的关联
        with step('选择子任务B，点击「添加」'):
            resp = Ra.add_relation('ete', sub_task_b, task_b)
            rl_key = resp.value('data.addActivityRelationLink.key')

            links = Ra.query_relation_links(task_b)
            pre_link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in pre_link_keys

    @story('154104 任务管理-前置依赖：进入添加前置依赖弹窗后，当前工作被移出项目计划')
    def test_conflict_sts_update_plan_list(self, prepare):
        # 给task_b 添加移除测试计划A
        task_a, task_b = prepare['tasks'][0], prepare['tasks'][1]
        gantt_list = Ra.all_gantt_data()
        # 取出任务计划
        activities = [gl for gl in gantt_list if gl['ganttDataType'] == 'parent_task']
        task_b_key = [a['key'] for a in activities if a['task']['uuid'] == task_b][0]

        # 从计划中删除任务b
        Ra.del_plans_or_milestones(task_b_key)
        # 检查 a 的source
        gantt_list = Ra.all_gantt_data()

        # 再次取出任务计划
        activities = [gl for gl in gantt_list if gl['ganttDataType'] == 'task']
        task_a_info = [a['source'] for a in activities if a['task']['uuid'] == task_a][0]

        print(f'task_a_info: {task_a_info}')
        source_uuids = [t['source']['uuid'] for t in task_a_info]
        assert task_b not in source_uuids

    @story('153012 任务管理-前置依赖：进入添加前置依赖弹窗后，选择的计划被删除')
    def test_conflict_sts_plan_not_exists(self, prepare):

        """"""

        resp_404 = Ra.add_relation('sts', 'activity_notfound', prepare['tasks'][0], 404)
        resp_404.check_response('errcode', 'NotFound.Activity')

    @story('153013 任务管理-前置依赖：进入添加前置依赖弹窗后，选择的里程碑被删除')
    def test_conflict_sts_milestone_not_exists(self, prepare):

        """"""

        resp_404 = Ra.add_relation('ste', 'activity_notfound', prepare['tasks'][0], 404)
        resp_404.check_response('errcode', 'NotFound.Activity')
