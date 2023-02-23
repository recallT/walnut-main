"""
@File    ：test_auto_schedule_1.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/28
@Desc    ：自动排期
"""

from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, step
from falcons.helper import mocks

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
            'activity_keys': [],  # 用来缓存创建好的关联关系key
        }

        return p


@feature('项目计划-自动排期')
class TestAutoSchedule(Checker):

    @story('T152787「开始-开始」存在前后置冲突时，点击自动排期')
    def test_auto_schedule_start_to_start(self, prepare):
        """
        计划1        开始时间-结束时间：2022年3月15日-2022年3月30日
            工作项A   计划开始日期-计划结束日期：2022年3月20日-2022年3月26日
            工作项B   计划开始日期-计划结束日期：2022年3月15日-2022年3月20日
        """
        t = prepare['tasks']

        # 更改任务1开始时间
        up_start = {
            "field_uuid": "field027",  # 计划开始时间
            "type": 5,
            "value": mocks.day_timestamp(1)
        }
        TaskAction.update_task_info(t[0], up_start)

        # 更改任务2结束时间
        up_end = {
            "field_uuid": "field028",  # 计划结束时间
            "type": 5,
            "value": mocks.day_timestamp(1)
        }
        TaskAction.update_task_info(t[1], up_end)

        # 工作项A和工作项B存前后置依赖关系：工作项A开始工作项B才能开始
        re = Ra.add_relation('sts', t[0], t[1])
        rl_key = re.value('data.addActivityRelationLink.key')

        with step('点击「自动排期」'):
            auto = Ra.auto_schedule()
            auto.check_response('success_count', 1)

        with step('检查工作项A和工作项B前后置关系'):
            links = Ra.query_relation_links(t[1])
            link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in link_keys

    @story('T152788「开始-完成」存在前后置冲突时，点击自动排期')
    def test_auto_schedule_start_to_end(self, prepare):
        """
        计划1       开始时间-结束时间：2022年3月1日-2022年3月30日
            工作项A   计划开始日期-计划结束日期：2022年3月5日-2022年3月10日
            工作项B   计划开始日期-计划结束日期：2022年3月15日-2022年3月20日
        """
        t = prepare['tasks']

        # 更改任务2计划开始时间和结束时间
        up_end = {
            "field_uuid": "field028",  # 计划结束时间
            "type": 5,
            "value": mocks.day_timestamp(2)
        }
        TaskAction.update_task_info(t[1], up_end)

        up_start = {
            "field_uuid": "field027",  # 计划开始时间
            "type": 5,
            "value": mocks.day_timestamp(1.5)
        }
        TaskAction.update_task_info(t[1], up_start)

        # 工作项A和工作项B存在冲突前后置依赖关系（开始-完成）：工作项B开始后，工作项A才能完成
        re = Ra.add_relation('ste', t[1], t[0])
        rl_key = re.value('data.addActivityRelationLink.key')

        with step('点击「自动排期」'):
            auto = Ra.auto_schedule()
            auto.check_response('success_count', 1)

        with step('检查工作项A和工作项B前后置关系'):
            links = Ra.query_relation_links(t[0])
            link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in link_keys

    @story('T152799「完成-开始」存在前后置冲突时，点击自动排期')
    def test_auto_schedule_end_to_start(self, prepare):
        """
        计划2        开始时间-结束时间：2022年3月15日-2022年3月30日
            工作项A   计划开始日期-计划结束日期：2022年3月15日-2022年3月20日
            里程碑A   完成日期：2022年3月20日
            工作项B   计划开始日期-计划结束日期：2022年3月18日-2022年3月24日
        """
        plan_b = prepare['plan'][1].split('-')[1]
        t = prepare['tasks'][4]

        # 计划2下新建里程碑A
        milestone_a = Ra.add_plans_or_milestones(p_type='milestone', parent=plan_b)
        m_a = milestone_a.split('-')[1]

        # 里程碑A和工作项B存前后置依赖关系（完成-开始）：里程碑A完成后，工作项B才能开始
        re = Ra.add_relation('ets', m_a, t)
        rl_key = re.value('data.addActivityRelationLink.key')

        with step('点击「自动排期」'):
            auto = Ra.auto_schedule()
            auto.check_response('success_count', 1)

        with step('检查里程碑A和工作项B前后置关系'):
            links = Ra.query_relation_links(t)
            link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in link_keys

    @story('T152809「完成-完成」存在前后置冲突时，点击自动排期')
    def test_auto_schedule_end_to_end(self, prepare):
        """
        计划1        开始时间-结束时间：2022年3月15日-2022年3月30日
            工作项A   计划开始日期-计划结束日期：2022年3月15日-2022年3月20日
            工作项B   计划开始日期-计划结束日期：2022年3月15日-2022年3月18日
        """
        t = prepare['tasks']

        # 更改任务2结束时间
        up_end = {
            "field_uuid": "field028",  # 计划结束时间
            "type": 5,
            "value": mocks.day_timestamp(0.5)
        }
        TaskAction.update_task_info(t[1], up_end)

        # 工作项A和工作项B存前后置依赖关系（完成-完成）：工作项A完成后，工作项B才能完成
        re = Ra.add_relation('ete', t[0], t[1])
        rl_key = re.value('data.addActivityRelationLink.key')

        with step('点击「自动排期」'):
            auto = Ra.auto_schedule()
            auto.check_response('success_count', 1)

        with step('检查工作项A和工作项B前后置关系'):
            links = Ra.query_relation_links(t[1])
            link_keys = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert rl_key in link_keys

    @story('T152865 存在多个前置条件时，点击自动排期')
    def test_auto_schedule_multiple_prefix(self, prepare):
        """
        计划1        开始时间-结束时间：2022年3月10日-2022年3月25日
        计划2        开始时间-结束时间：2022年3月1日-2022年3月30日
            工作项A   计划开始日期-计划结束日期：2022年3月5日-2022年3月10日
            工作项B   计划开始日期-计划结束日期：2022年3月3日-2022年3月15日
        """
        p = prepare['plan'][1].split('-')[1]
        t = prepare['tasks']

        # 更改任务A开始时间
        up_start = {
            "field_uuid": "field027",  # 计划开始时间
            "type": 5,
            "value": mocks.day_timestamp(1)
        }
        TaskAction.update_task_info(t[0], up_start)

        # 更改任务B开始时间
        up_start = {
            "field_uuid": "field027",  # 计划开始时间
            "type": 5,
            "value": mocks.day_timestamp(0.5)
        }
        TaskAction.update_task_info(t[1], up_start)

        # 工作项B存在两个前置关系，计划2完成后，工作项B才能开始，工作项A开始后，工作项B才能开始
        r1 = Ra.add_relation('sts', t[1], p)
        r1_key = r1.value('data.addActivityRelationLink.key')

        r2 = Ra.add_relation('sts', t[1], t[0])
        r2_key = r2.value('data.addActivityRelationLink.key')

        with step('点击「自动排期」'):
            auto = Ra.auto_schedule()
            auto.check_response('success_count', 1)

        with step('检查计划1和工作项B的前后置关系'):
            links = Ra.query_relation_links(t[1], r_type='post')
            r1_link = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert r1_key in r1_link

        with step('检查工作项A和工作项B的前后置关系'):
            assert r2_key in r1_link

    @story('T153952 存在多个后置条件时，点击自动排期')
    def test_auto_schedule_multiple_post(self, prepare):
        """
        计划1        开始时间-结束时间：2022年3月10日-2022年3月25日
        计划2        开始时间-结束时间：2022年3月1日-2022年3月30日
            工作项A   计划开始日期-计划结束日期：2022年3月5日-2022年3月10日
            工作项B   计划开始日期-计划结束日期：2022年3月3日-2022年3月15日
        """
        p = prepare['plan'][1].split('-')[1]
        t = prepare['tasks']

        # 更改任务A开始时间
        up_start = {
            "field_uuid": "field027",  # 计划开始时间
            "type": 5,
            "value": mocks.day_timestamp(1)
        }
        TaskAction.update_task_info(t[0], up_start)

        # 更改任务B开始时间
        up_start = {
            "field_uuid": "field027",  # 计划开始时间
            "type": 5,
            "value": mocks.day_timestamp(0.5)
        }
        TaskAction.update_task_info(t[1], up_start)

        # 工作项B存在两个前置关系，计划2完成后，工作项B才能开始，工作项A开始后，工作项B才能开始
        r1 = Ra.add_relation('sts', p, t[1])
        r1_key = r1.value('data.addActivityRelationLink.key')

        r2 = Ra.add_relation('sts', t[0], t[1])
        r2_key = r2.value('data.addActivityRelationLink.key')

        with step('点击「自动排期」'):
            auto = Ra.auto_schedule()
            auto.check_response('success_count', 1)

        with step('检查计划1和工作项B的前后置关系'):
            links = Ra.query_relation_links(t[1])
            r1_link = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert r1_key in r1_link

        with step('检查工作项A和工作项B的前后置关系'):
            assert r2_key in r1_link

    @story('T153953 存在无法自动解决的前后置冲突')
    def test_unable_auto_schedule(self, prepare):
        """
        计划1        开始时间-结束时间：2022年3月1日-2022年3月30日
            任务A   计划开始日期-计划结束日期：2022年3月5日-2022年3月15日
            任务B   计划开始日期-计划结束日期：2022年3月1日-2022年3月5日
        """
        t = prepare['tasks']

        # 更改任务A开始时间
        up_start = {
            "field_uuid": "field027",  # 计划开始时间
            "type": 5,
            "value": mocks.day_timestamp(0.3)
        }
        TaskAction.update_task_info(t[0], up_start)

        # 更改任务B结束时间
        up_end = {
            "field_uuid": "field028",  # 计划结束时间
            "type": 5,
            "value": mocks.day_timestamp(0.3)
        }
        TaskAction.update_task_info(t[1], up_end)

        # 任务A和任务B存在前后置依赖关系（完成-完成）：任务A完成后，任务B才能完成
        Ra.add_relation('ete', t[0], t[1])
        # r1_key = r1.value('data.addActivityRelationLink.key')

        # 任务B和任务A存在前后置依赖关系（开始-开始）：任务B开始后，任务A才能开始
        Ra.add_relation('sts', t[1], t[0])
        # r2_key = r2.value('data.addActivityRelationLink.key')

        # 任务A和任务B存在前后置依赖关系（开始-开始）：任务A开始后，任务B才能开始
        Ra.add_relation('sts', t[0], t[1])
        # r3_key = r3.value('data.addActivityRelationLink.key')

        with step('点击「自动排期」'):
            auto = Ra.auto_schedule()
            # 成功排期1条内容，排期失败1条内容
            auto.check_response('success_count', 1)
            auto.check_response('fialed_count', 1)

    @story('T154195 正常层级的工作项变为父子层级后点击自动排期')
    def test_auto_schedule_father_son_1(self, prepare):
        """
        计划1       开始时间-结束时间：2022年3月15日-2022年3月30日
            需求A   计划开始日期-计划结束日期：2022年3月15日-2022年3月20日
            需求B   计划开始日期-计划结束日期：2022年3月15日-2022年3月18日
        计划2
            任务A   计划开始日期-计划结束日期：2022年3月15日-2022年3月20日
            任务B   计划开始日期-计划结束日期：2022年3月10日-2022年3月20日
        """
        t = prepare['tasks']

        # 获取task[0]原时间戳
        task_info_0 = TaskAction.task_info(t[0])
        original_0 = [v['value'] for v in task_info_0.value('field_values') if
                      v['field_uuid'] == 'field027' or v['field_uuid'] == 'field028']  # 返回两个值，[0]开始时间，[1]结束时间

        # 更改需求B结束时间
        up_end = {
            "field_uuid": "field028",  # 计划结束时间
            "type": 5,
            "value": mocks.day_timestamp(0.5)
        }
        TaskAction.update_task_info(t[1], up_end)

        # 更改任务B开始时间
        up_start = {
            "field_uuid": 'field027',  # 计划开始时间
            "type": 5,
            "value": 1649119690
        }
        TaskAction.update_task_info(t[4], up_start)

        # 需求A和需求B存前后置冲突关系（完成-完成）：需求A完成后，需求B才能完成，当前前后置线条变红
        r1 = Ra.add_relation('ete', t[0], t[1])
        r1_key = r1.value('data.addActivityRelationLink.key')

        # 任务A和任务B存在前后置冲突关系（开始-开始）：任务A开始后，任务B才能开始，当前前后置连线变红
        r2 = Ra.add_relation('sts', t[3], t[4])
        r2_key = r2.value('data.addActivityRelationLink.key')

        # 获取task[1]原时间戳
        task_info_1 = TaskAction.task_info(t[1])
        original_1 = [v['value'] for v in task_info_1.value('field_values') if
                      v['field_uuid'] == 'field027' or v['field_uuid'] == 'field028']

        with step('用户A将任务B变为任务A的子工作项，点击「自动排期」'):
            Ra.change_issue_type(t[4], t[3])

            auto = Ra.auto_schedule()
            auto.check_response('success_count', 2)

        with step('检查需求A和需求B前后置关系'):
            links = Ra.query_relation_links(t[1])
            r1_link = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert r1_key in r1_link

            # 需求A计划开始-结束日期不变
            info_0 = TaskAction.task_info(t[0])
            new_0 = [v['value'] for v in info_0.value('field_values') if
                     v['field_uuid'] == 'field027' or v['field_uuid'] == 'field028']

            assert new_0 == original_0

            # 需求B的计划开始时间-计划结束时间变为：2022年3月17日-2022年3月20日
            info_1 = TaskAction.task_info(t[1])
            new_1 = [v['value'] for v in info_1.value('field_values') if
                     v['field_uuid'] == 'field027' or v['field_uuid'] == 'field028']

            assert new_1 > original_1

    @story('T155671 存在父子层级连线的工作项点击自动排期')
    def test_auto_schedule_father_son_2(self, prepare):
        """
        计划1       开始时间-结束时间：2022年3月15日-2022年3月30日
            需求A   计划开始日期-计划结束日期：2022年3月15日-2022年3月20日
            需求B   计划开始日期-计划结束日期：2022年3月15日-2022年3月18日
        计划2
            任务A   计划开始日期-计划结束日期：2022年3月15日-2022年3月20日
            任务B   计划开始日期-计划结束日期：2022年3月10日-2022年3月20日
        """
        t = prepare['tasks']
        p = prepare['plan'][1]

        # 获取task[0]原时间戳
        task_info_0 = TaskAction.task_info(t[0])
        original_0 = [v['value'] for v in task_info_0.value('field_values') if
                      v['field_uuid'] == 'field027' or v['field_uuid'] == 'field028']  # 返回两个值，[0]开始时间，[1]结束时间

        # 更改需求B结束时间
        up_end = {
            "field_uuid": "field028",  # 计划结束时间
            "type": 5,
            "value": mocks.day_timestamp(0.5)
        }
        TaskAction.update_task_info(t[1], up_end)

        # 更改任务B开始时间
        up_start = {
            "field_uuid": 'field027',  # 计划开始时间
            "type": 5,
            "value": 1649119690
        }
        TaskAction.update_task_info(t[4], up_start)

        # 需求A和需求B存前后置冲突关系（完成-完成）：需求A完成后，需求B才能完成，当前前后置线条变红
        r1 = Ra.add_relation('ete', t[0], t[1])
        r1_key = r1.value('data.addActivityRelationLink.key')

        # 计划2和任务B存在前后置冲突关系（开始-开始）：计划2开始后，任务B才能开始，当前前后置线条变红
        Ra.add_relation('sts', p, t[4])

        # 获取task[1]原时间戳
        task_info_1 = TaskAction.task_info(t[1])
        original_1 = [v['value'] for v in task_info_1.value('field_values') if
                      v['field_uuid'] == 'field027' or v['field_uuid'] == 'field028']

        with step('用户A将任务B变为任务A的子工作项，点击「自动排期」'):
            Ra.change_issue_type(t[4], t[3])

            auto = Ra.auto_schedule()
            auto.check_response('success_count', 2)

        with step('检查需求A和需求B前后置关系'):
            links = Ra.query_relation_links(t[1])
            r1_link = [k['key'] for k in links.value('data.activityRelationLinks')]

            assert r1_key in r1_link

            # 需求A计划开始-结束日期不变
            info_0 = TaskAction.task_info(t[0])
            new_0 = [v['value'] for v in info_0.value('field_values') if
                     v['field_uuid'] == 'field027' or v['field_uuid'] == 'field028']

            assert new_0 == original_0

            # 需求B的计划开始时间-计划结束时间变为：2022年3月17日-2022年3月20日
            info_1 = TaskAction.task_info(t[1])
            new_1 = [v['value'] for v in info_1.value('field_values') if
                     v['field_uuid'] == 'field027' or v['field_uuid'] == 'field028']

            assert new_1 > original_1
