"""
@File    ：test_gantt_relation.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/31
@Desc    ：
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

        # 4. 添加任务到计划中 task 1- 3 == 计划A , task 4 5 == 计划B
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


@feature('任务管理-甘特视图')
class TestGanttRelation:

    @story('155021 项目计划-甘特视图-设置前后置依赖关系：连线出现前后置冲突（工作项-计划）')
    def test_conflict_issue_plans(self, prepare):
        """"""
        print(prepare)
        task = prepare['tasks']
        task_a, plan_b = task[2], prepare['plan'][1]
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

        self.check_activity(task_a, plan_b, 'task', 'parent_ppm_task')

    @story('155016 项目计划-甘特视图-设置前后置依赖关系：连线出现前后置冲突（计划-计划）')
    def test_conflict_plan_to_plan(self, prepare):
        """"""
        print(prepare)
        plan_a, plan_b = prepare['plan'][0], prepare['plan'][1]
        with step('plan_a , plan b 的起始时间设为冲突时间'):
            # b 的 开始时间比a 的晚

            Ra.update_plans_or_milestones(plan_a, **{
                'start_time': mocks.day_timestamp(1),
                'end_time': mocks.day_timestamp(3)
            })
            Ra.update_plans_or_milestones(plan_b, **{
                'start_time': mocks.day_timestamp(2),
                'end_time': mocks.day_timestamp(4)
            })

        self.add_pre_relation(plan_a, plan_b)

        self.check_activity(plan_a, plan_b, 'parent_ppm_task', 'parent_ppm_task', True)

        a, b = self.gen_ppm_info(plan_a, plan_b)
        assert a['planStartTime'] == b['planStartTime']

    @story('152992 项目计划-甘特视图-设置前后置依赖关系：有目标工作项的查看/编辑权限和周期属性编辑权限时连线')
    def test_gantt_task_task(self, prepare):
        task = prepare['tasks']
        task_a, task_b = task[1], task[2]
        with step('将task a, plan b 的起始时间设为冲突时间'):
            # 将task 1 2 的起始时间设为冲突时间
            # b 的 开始时间比a 的晚
            task_a_s_time = fc.plan_time('start', mocks.day_timestamp(1))
            task_a_e_time = fc.plan_time('end', mocks.day_timestamp(2))
            TaskAction.update_task_info(task_a, task_a_s_time)
            TaskAction.update_task_info(task_a, task_a_e_time)

            task_b_s_time = fc.plan_time('start', mocks.day_timestamp(2))
            task_b_e_time = fc.plan_time('end', mocks.day_timestamp(3))
            TaskAction.update_task_info(task_b, task_b_s_time)
            TaskAction.update_task_info(task_b, task_b_e_time)

        self.add_pre_relation(task_a, task_b)

        self.check_activity(task_a, task_b, 'task', 'task')

    @story('152979 项目计划-甘特视图-设置前后置依赖关系：正确前后置关系连线检查')
    def test_gantt_task_milestone(self, prepare):
        task = prepare['tasks']
        task_a, milestone = task[1], prepare['milestone']
        with step('正常时间'):
            # 正常时间
            task_a_s_time = fc.plan_time('start', mocks.day_timestamp(2))
            task_a_e_time = fc.plan_time('end', mocks.day_timestamp(3))
            TaskAction.update_task_info(task_a, task_a_s_time)
            TaskAction.update_task_info(task_a, task_a_e_time)

            Ra.update_plans_or_milestones(milestone, **{
                'start_time': mocks.day_timestamp(1),
                'end_time': mocks.day_timestamp(1)
            })

        self.add_pre_relation(task_a, milestone, prefix_type='milestone')

        self.check_activity(task_a, milestone, 'task', 'milestone', True)

    @story('154192 项目计划-甘特视图-设置前后置依赖关系：自己连自己错误提示')
    def test_gantt_me_to_me(self, prepare):
        task_a = prepare['tasks'][0]
        resp_400 = Ra.add_relation('ete', task_a, task_a, 400)
        resp_400.check_response('reason', 'SameNodeCorrupt')

    @story('152995 项目计划-甘特视图-拖拽移动节点：拖拽被关联方至前后置冲突（不涉及工作项）')
    def test_gantt_update_plan_start_time(self, prepare):
        """依赖 plan_to_plan 用例"""
        plan_a, plan_b = prepare['plan'][0], prepare['plan'][1]
        with step('plan_a , plan b 的起始时间设为冲突时间'):
            # b 的 开始时间比a 的晚

            resp_400 = Ra.update_plans_or_milestones(plan_a, status_code=400, **{
                'start_time': mocks.day_timestamp(-1),
            })

            resp_400.check_response('errcode', 'InvalidParameter.Activity.StartTime.OutOfRange')

    @story('154194 项目计划-甘特图：迭代中已添加前后置的工作项类型被移除')
    def test_remove_related_issue(self, prepare):
        with step('关联一个工作项 a b 完成-完成, 检查取消任务前的连线情况'):
            task_a, task_b = prepare['tasks'][3], prepare['tasks'][4]
            Ra.add_relation('ete', task_b, task_a)

            gantt_list_before = Ra.all_gantt_data()
        with step('移除工作项 b 并 检查工作项 a 的连线'):
            """"""
            # 删除 task_b
            task_info = [gt for gt in gantt_list_before if gt['ganttDataType'] == 'task']
            tobe_remove = [t['key'] for t in task_info if t['task']['uuid'] == task_b][0]

            Ra.del_plans_or_milestones(tobe_remove)

            # 查看task_a 的前置关系 source
            gantt_list_after = Ra.all_gantt_data()
            task_info = [gt for gt in gantt_list_after if gt['ganttDataType'] == 'task']
            source_a = [t['source'] for t in task_info if t['task']['uuid'] == task_a][0]

            assert not source_a

        with step('重新加入工作项b 并检查工作项 a 的连线'):
            """"""
            Ra.external_activity(prepare['plan'][0], task_b)
            # 查看task_a 的前置关系 source
            gantt_list_curr = Ra.all_gantt_data()
            task_info = [gt for gt in gantt_list_curr if gt['ganttDataType'] == 'task']
            source_a = [t['source'] for t in task_info if t['task']['uuid'] == task_a][0]

            assert source_a

    @classmethod
    def add_pre_relation(cls, me, prefix, rl_type='sts', prefix_type='task', token=None):
        with step('选择前置依赖关系为：开始-开始'):
            # task_a 前置关联 plan_b
            t = rl_type
            if prefix_type == 'milestone':
                t = 'ets'
            relation_resp = Ra.add_ppm_relation(t, prefix, me, token=token)
            rl_key = relation_resp.value('data.updateActivity.key')

            return rl_key

    @classmethod
    def gen_ppm_info(cls, me, prefix, token=None):
        """
        检查
        :param token:
        :param me: 当前工作项
        :param prefix: 前置对象

        :return:
        """

        # 检查 milestone 的关联结果
        gantt_list = Ra.all_gantt_data(token)

        me_info = get_item(gantt_list, me, 'parent_ppm_task')
        prefix_info = get_item(gantt_list, prefix, 'parent_ppm_task')

        return me_info, prefix_info

    @classmethod
    def check_activity(cls, me, prefix, me_type, prefix_type='task', ok=False, token=None):
        """
        检查
        :param token:
        :param me: 当前工作项
        :param prefix: 前置对象
        :param me_type: task, milestone, parent_ppm_task, ppm_task
        :param prefix_type: task, milestone, parent_ppm_task, ppm_task
        :param ok:
        :return:
        """

        # 检查 milestone 的关联结果
        gantt_list = Ra.all_gantt_data(token)

        # 取出任务计划
        with step(f'检查{prefix_type.upper()}连线情况'):
            # 获取工作项 milestone 的连线数据, 获取其后置数据 有b-指向 a，取 b 的 target 数据
            t = get_item(gantt_list, prefix, prefix_type)
            # 检查 b 有后置连线
            # if prefix_type == 'milestone':
            #     assert t['source']
            assert t['target']
        if not ok:
            with step('此节点存在前后置冲突'):
                # a 有前后置冲突警告 dependency
                # 获取工作项a的连线数据
                activity_a = get_item(gantt_list, me, me_type)
                assert 'dependency' in activity_a['reminders']


def get_item(gantt, key_or_uuid, ac_type) -> dict:
    # 取出任务计划
    activities = [gl for gl in gantt if gl['ganttDataType'] == ac_type]

    # 获取工作项 milestone 的连线数据, 获取其后置数据 有b-指向 a，取 b 的 target 数据
    if ac_type == 'task':
        m = [a for a in activities if a['task']['uuid'] == key_or_uuid][0]

    else:
        m = [a for a in activities if a['key'] == key_or_uuid][0]

    return m
