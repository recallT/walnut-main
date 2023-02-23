import time

from falcons.check import Checker
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture, step

from main.actions.issue import IssueAction
from main.actions.task import TaskAction, team_stamp
from main.api import task, issue
from main.helper.extra import Extra
from main.params import task as t, issue as i


@fixture(scope='module')
def task_data():
    # 新建两个测试项目，供需求批处理使用
    creator = Extra(ApiMeta)
    old_proj = creator.new_project(f'任务batch_2pro_one')
    time.sleep(10.5)
    new_proj = creator.new_project(f'任务batch_2pro_two')

    ise = TaskAction.new_issue_batch(10, proj_uuid=old_proj)

    return {'task': ise[0], 'backup_task': ise[1], 'old_proj': old_proj, 'new_proj': new_proj}


@fixture(scope='module', autouse=True)
def del_task(task_data):
    """批量删除任务"""
    yield
    TaskAction.del_task_batch(task_data['task'])

    # 清除项目数据
    time.sleep(1)
    creator = Extra(ApiMeta)
    creator.del_project(task_data['old_proj'])
    creator.del_project(task_data['new_proj'])


@feature('任务管理-批量移动')
class TestTaskBatchMoveTwo(Checker):

    @story('151907 任务管理-批量移动：选择移动的父工作项被删除')
    def test_del_parent_task(self, task_data):
        """批量移动时删除父工作项"""

        parent_uuid = task_data['task'][2]  # 选择任务2
        old_proj, new_proj = task_data['old_proj'], task_data['new_proj']

        with step('修改目标项目，修改目标工作项类型'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj)

            with step('删除项目下的任务'):
                TaskAction.del_task(parent_uuid)

                res = self.call(task.TaskBatchMove, param)

                mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"NotFound.BatchTask.Task": 2})

    @story('151909 任务管理-批量移动：目标父工作项类型被删除（父工作项下有子工作项）')
    def test_del_task_type(self, task_data):
        """批量移动时删除工作项类型"""

        parent_uuid = task_data['task'][3]  # 选择任务3
        old_proj, new_proj = task_data['old_proj'], task_data['new_proj']

        with step('修改目标项目，修改目标工作项类型为 需求'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj)

            with step('删除工作项类型「需求」'):
                # 获取工作项-需求 uuid
                issue_id = TaskAction.issue_type_uuid('需求')[0]

                # 删除
                pp = i.delete_project_issue()[0]
                pp.uri_args({'issue_uuid': issue_id, 'project_uuid': new_proj})
                self.call(issue.IssueProjectDelete, pp)

                # 批量移动
                res = self.call(task.TaskBatchMove, param)

                mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"NotFound.BatchTask.TargetIssueType": 2})

            # 添加已删除的工作项类型-需求
            p = i.add_project_issue()[0]
            p.json['issue_type_uuids'] = [issue_id]
            p.uri_args({'project_uuid': new_proj})
            self.call(issue.IssueProjectAdd, p)

    @story('151939 任务管理-批量移动：目标父工作项类型为自定义标准工作项')
    def test_target_task_customize(self, task_data):
        """目标工作项是自定义工作项"""
        uuid = task_data['task'][5]  # 选择任务5
        old_proj, new_proj = task_data['old_proj'], task_data['new_proj']

        with step('前置条件'):
            # 添加自定义工作项
            resp = team_stamp({"issue_type": 0})
            issue_uuid = [n['uuid'] for n in resp['issue_type']['issue_types'] if n['name'] == '任务自定义类型']

            if not issue_uuid:
                param = i.add_standard_issue()[0]
                param.json_update('issue_type.name', '任务自定义类型')
                param.uri_args({'project_uuid': new_proj})
                res = self.call(issue.IssuesAdd, param)
                issue_uuid = [res.value('uuid')]

            # 项目中添加自定义工作项
            p = i.add_project_issue()[0]
            p.json['issue_type_uuids'] = issue_uuid
            p.uri_args({'project_uuid': new_proj})
            self.call(issue.IssueProjectAdd, p)

        with step('修改目标项目为「项目B」，目标工作项类型为「自定义类型」'):
            tp = IssueAction.task_param('任务', '任务自定义类型', old_proj, new_proj)

            param = t.batch_move_task([uuid], tp['old'], tp['new'], old_proj)[0]
            param.json_update('rules[0].target_project_uuid', new_proj)
            res = self.call(task.TaskBatchMove, param)

            mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 1)

        with step('清除新增的数据'):
            iu = issue_uuid[0]

            # 删除自定义工作项
            TaskAction.del_task(uuid)
            # 删除项目中的自定义工作项类型
            pp = i.delete_project_issue()[0]
            pp.uri_args({'issue_uuid': iu, 'project_uuid': new_proj})
            self.call(issue.IssueProjectDelete, pp)
            # 删除配置中心的自定义工作项类型
            prm = i.delete_issue()[0]
            prm.uri_args({'issue_uuid': iu})
            self.call(issue.IssueDelete, prm)

    @story('151921 任务管理-批量移动：目标父工作项状态被删除（父工作项下有子工作项）')
    def test_del_target_parent_task_status(self, task_data):
        """批量移动时删除父工作项状态"""

        parent_uuid = task_data['task'][6]  # 选择任务6
        old_proj, new_proj = task_data['old_proj'], task_data['new_proj']

        with step('修改目标项目B，修改目标工作项状态为：已完成'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, new_issue_type='缺陷')

            with step('项目B下的工作项类型「任务」的状态「已完成」被删除'):
                param.json_update('rules[0].target_status_uuid', 'F8ruTEST')
                res = self.call(task.TaskBatchMove, param)

                mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"NotFound.BatchTask.TargetIssueStatus": 2})

    @story('151924 任务管理-批量移动：目标父工作项和子工作项状态被删除（部分子工作项状态被删除）')
    def test_del_task_status(self, task_data):
        """批量移动时删除工作项状态"""

        parent_uuid = task_data['task'][7]  # 选择任务7
        old_proj, new_proj = task_data['old_proj'], task_data['new_proj']

        with step('修改目标项目B，修改目标工作项状态为：已完成，子任务目标工作项状态为：进行中'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, new_issue_type='任务')

            with step('项目B下的工作项类型「任务」的状态「已完成」被删除，「子任务」的状态「进行中」被删除'):
                param.json_update('rules[0].target_status_uuid', 'F8ruTEST')
                param.json_update('rules[1].target_status_uuid', 'Q8ruTEST')
                res = self.call(task.TaskBatchMove, param)

                mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"NotFound.BatchTask.TargetIssueStatus": 2})

    @story('151927 任务管理-批量移动：目标子工作项状态被删除（子工作项下没有子工作项）')
    def test_del_sub_task_status(self, task_data):
        """批量移动时删除子工作项状态"""

        parent_uuid = task_data['task'][8]  # 选择任务8
        old_proj, new_proj = task_data['old_proj'], task_data['new_proj']

        with step('修改目标项目B，修改目标子工作项状态为：已完成'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj)

            with step('项目B下的工作项类型「子任务」的状态「已完成」被删除'):
                param.json_update('rules[1].target_status_uuid', 'F8ruTEST')
                res = self.call(task.TaskBatchMove, param)

                mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"NotFound.BatchTask.TargetIssueStatus": 2})

    @story('151911 任务管理-批量移动：目标父工作项和子工作项类型被删除（部分子工作项类型被删除）')
    def test_del_task_and_subtask_type(self, task_data):
        """批量移动时删除工作项和子工作项类型"""

        parent_uuid = task_data['task'][4]  # 选择任务4
        old_proj, new_proj = task_data['old_proj'], task_data['new_proj']

        with step('修改目标项目，修改目标工作项类型为 需求和子需求'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj)

            with step('删除工作项类型「需求」'):
                # 获取工作项-需求/子任务 uuid
                issue_id = TaskAction.issue_type_uuid('需求')[0]
                sub_issue_id = TaskAction.issue_type_uuid('子需求')[0]

                # 删除需求类型
                pp = i.delete_project_issue()[0]
                pp.uri_args({'issue_uuid': issue_id, 'project_uuid': new_proj})
                self.call(issue.IssueProjectDelete, pp)

                # 删除子需求的工作项
                sub_uuid = param.json_value('tasks_related[0].sub_uuids')[0]
                TaskAction.del_task(sub_uuid)
                # 删除子需求类型
                pp.uri_args({'issue_uuid': sub_issue_id, 'project_uuid': new_proj})
                self.call(issue.IssueProjectDelete, pp)

                # 批量移动
                res = self.call(task.TaskBatchMove, param)

                mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"NotFound.BatchTask.TargetIssueType": 2})

            # 添加已删除的工作项类型-需求
            p = i.add_project_issue()[0]
            p.json['issue_type_uuids'] = [issue_id]
            p.uri_args({'project_uuid': new_proj})
            self.call(issue.IssueProjectAdd, p)
            # 添加已删除的工作项类型-子需求
            p.json['issue_type_uuids'] = [sub_issue_id]
            self.call(issue.IssueProjectAdd, p)
