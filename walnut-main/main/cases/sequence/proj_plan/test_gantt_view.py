"""
@File    ：test_gantt_view.py
@Author  ：zhangyonghui
@Email   ：zhangyonghui@ones.ai
@Date    ：2022/5/30
@Desc    ：项目计划-甘特视图
"""
import json

from falcons.check import Checker, go
from falcons.com.nick import story, fixture, step, mark, feature
from falcons.ops import generate_param
from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra
from main.actions.sprint import SprintAction
from main.actions.task import TaskAction
from main.api.project import ItemGraphql, ExportProjectPlan
from main.params import relation
from main.params import relation as rel
from main.params.task import export_pro_plan
from falcons.com.meta import ApiMeta


@fixture(scope='module', autouse=True)
def add_plan_component():
    # 1.先添加一个【项目计划】 组件
    PrjAction.add_component('项目计划')
    yield
    PrjAction.remove_prj_component('项目计划')


@fixture(scope='module', autouse=True)
def add_plan_task_sprint():
    # 添加 计划组
    plan_a_uuid = Ra.add_plans_or_milestones().split('-')[1]

    rl_resp = go(ItemGraphql, relation.chart_uuid()[0])
    chart_uuid = rl_resp.value('data.activityCharts[0].uuid')

    prm = relation.add_parent_plan(plan_a_uuid)[0]
    prm.json_update('variables.chart_uuid', chart_uuid)

    sub_plan_uuid = go(ItemGraphql, prm).value('data.addActivity.uuid')
    # 添加计划关联迭代
    sprint_uuid = SprintAction.sprint_add()

    plan_b_uuid = Ra.add_plans_or_milestones().split('-')[1]
    # 迭代关联项目计划
    Ra.external_activity('activity-' + plan_b_uuid, sprint_uuid, ob_type='sprint')
    sprint_key = Ra.task_relation_plan_key(sprint_uuid)
    # 计划关联需求
    plan_c_uuid = Ra.add_plans_or_milestones().split('-')[1]
    ise_uuid = TaskAction.new_issue(issue_type_name='需求', is_batch=False)[0]

    Ra.external_activity('activity-' + plan_c_uuid, ise_uuid, ob_type='task')
    ise_key = Ra.task_relation_plan_key(ise_uuid)
    # 里程碑
    milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
    data = {'plan_a_uuid': plan_a_uuid, 'sub_plan_uuid': sub_plan_uuid, 'plan_b_uuid': plan_b_uuid,
            'sprint_key': sprint_key, 'plan_c_uuid': plan_c_uuid, 'ise_key': ise_key, 'milestone_key': milestone_key
            }
    return data


@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过')
@feature('项目计划-甘特视图')
class TestProGantt(Checker):

    @story('T121338 甘特图-迭代：拖拽排序')
    def test_gantt_drag_sprint(self, add_plan_task_sprint):
        data = add_plan_task_sprint
        with step('示例关联迭代拖拽入示例计划中'):
            TaskAction.plan_task_drag(key=data['sprint_key'], parent=data['plan_a_uuid'])

    @story('T121340 甘特图-工作项：拖拽排序')
    def test_gantt_drag_issue(self, add_plan_task_sprint):
        data = add_plan_task_sprint
        with step('示例需求拖拽入计划组子计划中'):
            TaskAction.plan_task_drag(key=data['ise_key'], parent=data['sub_plan_uuid'])

        with step('示例需求拖拽入计划组中'):
            TaskAction.plan_task_drag(key=data['ise_key'], parent=data['plan_a_uuid'])

    @story('T121343 甘特图-计划组：拖拽排序')
    def test_gantt_drag_plan_group(self, add_plan_task_sprint):
        data = add_plan_task_sprint
        with step('示例计划组1与示例计划组2同级上下拖拽'):
            TaskAction.plan_task_drag(key=data['plan_b_uuid'], parent='')

        with step('示例计划组1拖拽入其它示例计划组2'):
            TaskAction.plan_task_drag(key=data['plan_a_uuid'], parent=data['plan_b_uuid'])

        with step('示例计划组2拖拽入示例计划2'):
            plan_uuid = Ra.add_plans_or_milestones()
            TaskAction.plan_task_drag(key=plan_uuid, parent=data['plan_c_uuid'])

        with step('示例计划组1拖拽出其它示例计划组2'):
            TaskAction.plan_task_drag(key=data['plan_a_uuid'], parent='')

    @story('T121344 甘特图-计划：拖拽排序')
    def test_gantt_drag_plan(self, add_plan_task_sprint):
        data = add_plan_task_sprint
        with step('示例计划1与示例计划2同级上下拖拽'):
            TaskAction.plan_task_drag(key=data['plan_a_uuid'], parent='')
        with step('示例计划1拖拽入示例计划组中'):
            TaskAction.plan_task_drag(key=data['plan_b_uuid'], parent=data['plan_a_uuid'])

        with step('示例计划1拖拽出示例计划2'):
            TaskAction.plan_task_drag(key=data['plan_a_uuid'], parent='')

    @story('T121346 甘特图-里程碑：拖拽排序')
    def test_gantt_drag_milestone(self, add_plan_task_sprint):
        data = add_plan_task_sprint
        milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
        with step('示例里程碑1与示例里程碑2同级拖拽'):
            TaskAction.plan_task_drag(key=data['milestone_key'], parent='',
                                      after=milestone_key.split('-')[1])

        with step('示例里程碑1拖拽入示例计划'):
            TaskAction.plan_task_drag(key=data['milestone_key'], parent=data['plan_c_uuid'])

        with step('示例里程碑2拽入示例计划组'):
            TaskAction.plan_task_drag(key=milestone_key, parent=data['plan_a_uuid'])

        with step('示例里程碑2拖拽出示例计划组'):
            TaskAction.plan_task_drag(key=milestone_key, parent='')

    @story('T144848 导出历史快照：有项目计划管理权限成员导出项目计划')
    def test_gantt_export_snapshot(self):
        with step('创建快照'):
            p_key = Ra.add_activity_release()
            key = p_key.value('data.addActivityRelease.key').split('-')[1]
        with step('导出历史快照'):
            param = generate_param({
                "release_uuid": key
            }, is_project=True)[0]
            self.call(ExportProjectPlan, param)

    @story('T144597 导出项目计划：有项目计划管理权限成员导出项目计划')
    def test_gantt_export_proj_plan(self):
        with step('点击更多-导出项目计划'):
            # 获取chart_uuid issueType_in
            rl_resp = go(ItemGraphql, relation.chart_uuid()[0])
            chart_uuid = rl_resp.value('data.activityCharts[0].uuid')
            settings = rl_resp.value('data.activityCharts[0].config.settings')
            resp_json = json.loads(settings)
            issue_type_in = [uuid['uuid'] for uuid in resp_json['sprint_settings']]
            # 点击导出
            param = export_pro_plan(chart_uuid, issue_type_in)[0]
            self.call(ExportProjectPlan, param)

    @story('T130960 历史快照对比：对比快照下拉菜单')
    def test_gantt_snapshot_compare(self):
        with step('创建快照'):
            p_key = Ra.add_activity_release()
            key = p_key.value('data.addActivityRelease.key')

        with step('查看历史快照对比'):
            param = rel.gantt_history(key)[0]
            resp = self.call(ItemGraphql, param)
            resp.check_response('data.activityRelease.key', key)
