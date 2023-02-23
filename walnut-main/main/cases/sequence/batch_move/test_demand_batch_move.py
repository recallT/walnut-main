import time

from falcons.check import Checker
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture, step, mark

from main.actions.issue import IssueAction
from main.actions.task import TaskAction, team_stamp
from main.api import task, issue
from main.helper.extra import Extra
from main.params import task as t, issue as i


@fixture(scope='module', autouse=True)
def demand():
    # 新建两个测试项目，供需求批处理使用
    creator = Extra(ApiMeta)
    p_uuid_one = creator.new_project(f'需求批处理pro_one')
    time.sleep(10.5)
    p_uuid_two = creator.new_project(f'需求批处理pro_two')

    ise = TaskAction.new_issue_batch(10, issue_type_name='需求', proj_uuid=p_uuid_one)

    return {'task': ise[0], 'backup_task': ise[1], 'old_proj': p_uuid_one, 'new_proj': p_uuid_two}


@fixture(scope='module', autouse=True)
def del_demand(demand):
    """批量删除任务"""
    yield

    TaskAction.del_task_batch(demand['task'])

    # 清除项目数据
    time.sleep(1)
    creator = Extra(ApiMeta)
    creator.del_project(demand['old_proj'])
    creator.del_project(demand['new_proj'])


@mark.smoke
@feature('需求管理-批量移动')
class TestDemandBatchMove(Checker):
    """需求管理批量移动案例"""

    @story('151971 需求管理-批量移动：目标父工作项类型被删除（父工作项下有子工作项）')
    def test_demand_del_target_issue_type(self, demand):
        """批量移动时删除目标工作项类型"""

        parent_uuid = demand['task'][3]  # 选择需求4
        old_proj, new_proj = demand['old_proj'], demand['new_proj']

        with step('修改目标项目，修改目标工作项类型为 任务'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子需求', '需求', '任务')

            with step('删除工作项类型「任务」'):
                # 获取工作项-任务 uuid
                issue_id = TaskAction.issue_type_uuid()[0]

                # 删除
                pp = i.delete_project_issue()[0]
                pp.uri_args({'issue_uuid': issue_id, 'project_uuid': new_proj})
                self.call(issue.IssueProjectDelete, pp)

                # 批量移动
                res = self.call(task.TaskBatchMove, param)

                mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"NotFound.BatchTask.TargetIssueType": 2})

            # 添加已删除的工作项类型-任务
            p = i.add_project_issue()[0]
            p.json['issue_type_uuids'] = [issue_id]
            p.uri_args({'project_uuid': new_proj})
            self.call(issue.IssueProjectAdd, p)

    @story('151973 需求管理-批量移动：选择移动的父工作项被删除')
    def test_demand_del_parent_task(self, demand):
        """批量移动时删除父工作项"""

        parent_uuid = demand['task'][4]  # 选择需求5
        old_proj, new_proj = demand['old_proj'], demand['new_proj']

        with step('修改目标项目，修改目标工作项类型'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子需求', '需求', '任务')

            with step('删除项目下的需求'):
                TaskAction.del_task(parent_uuid)

                res = self.call(task.TaskBatchMove, param)

                mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"NotFound.BatchTask.Task": 2})

    @story('151980 需求管理-批量移动：目标父工作项和子工作项状态被删除（部分子工作项状态被删除）')
    def test_demand_del_task_status(self, demand):
        """批量移动时删除工作项状态"""

        parent_uuid = demand['task'][5]  # 选择需求6
        old_proj, new_proj = demand['old_proj'], demand['new_proj']

        with step('修改目标项目B，修改目标工作项状态为：已完成，子任务目标工作项状态为：进行中'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子需求', '需求')

            with step('项目B下的工作项类型「需求」的状态「已完成」被删除，「子需求」的状态「进行中」被删除'):
                param.json_update('rules[0].target_status_uuid', 'F8ruTEST')
                param.json_update('rules[1].target_status_uuid', 'Q8ruTEST')
                res = self.call(task.TaskBatchMove, param)

                mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"NotFound.BatchTask.TargetIssueStatus": 2})

    @story('151989 需求管理-批量移动：目标子工作项状态被删除（子工作项下没有子工作项）')
    def test_demand_del_sub_task_status(self, demand):
        """批量移动时删除子工作项状态"""

        parent_uuid = demand['task'][6]  # 选择需求7
        old_proj, new_proj = demand['old_proj'], demand['new_proj']

        with step('修改目标项目B，修改目标子工作项状态为：已完成'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子需求', '需求')

            with step('项目B下的工作项类型「子需求」的状态「已完成」被删除'):
                param.json_update('rules[1].target_status_uuid', 'F8ruTEST')
                res = self.call(task.TaskBatchMove, param)

                mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"NotFound.BatchTask.TargetIssueStatus": 2})

    @story('151990 需求管理-批量移动：进入批量移动页面，选择的工作项下新增了子工作项（选择的父下存在子工作项）')
    def test_demand_opt_add_sub_task(self, demand):
        """批量移动操作时添加子工作项"""

        parent_uuid = demand['task'][2]  # 选择需求3
        old_proj, new_proj = demand['old_proj'], demand['new_proj']

        with step('修改目标项目，修改目标工作项类型'):
            task_param = IssueAction.task_param('需求', '任务', old_proj, new_proj)
            param = t.batch_move_task([parent_uuid], task_param['old'], task_param['new'], old_proj)[0]

            with step('此时需求下新增了一个子工作项'):
                IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子需求', '需求')

            res = self.call(task.TaskBatchMove, param)

            mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"Blocked.SubTask.Increased": 2})

    @story('151997 需求管理-批量移动：批量移动父子工作项（仅修改目标项目）')
    def test_demand_move_up_prj(self, demand):
        """批量移动工作项修改项目"""

        parent_uuid = demand['task'][1]  # 选择需求2
        old_proj, new_proj = demand['old_proj'], demand['new_proj']

        with step('更改目标项目为：项目B'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子需求', '需求')
            res = self.call(task.TaskBatchMove, param)

            mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 2)

    @story('152004 需求管理-批量移动：移动的目标项目被删除')
    def test_demand_del_target_prj(self, demand):
        """批量移动时移除项目目标"""

        uuid = demand['task'][0]  # 选择需求1
        old_proj, new_proj = demand['old_proj'], demand['new_proj']

        task_param = IssueAction.task_param('需求', '任务', old_proj, new_proj)

        with step('需求-->修改目标项目为项目B，再删除项目B'):
            param = t.batch_move_task([uuid], task_param['old'], task_param['new'], old_proj)[0]
            param.json_update('rules[0].target_project_uuid', 'AV8G6Ypr3b95QkWk')  # 替换成不存在的项目uuid
            res = self.call(task.TaskBatchMove, param)

            mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0)

    @story('152010 需求管理-批量移动：目标父工作项类型为自定义标准工作项')
    def test_demand_target_task_customize(self, demand):
        """目标工作项是自定义工作项"""
        uuid = demand['task'][7]  # 选择需求8
        old_proj, new_proj = demand['old_proj'], demand['new_proj']

        with step('前置条件'):
            # 添加自定义工作项
            resp = team_stamp({"issue_type": 0})
            issue_uuid = [n['uuid'] for n in resp['issue_type']['issue_types'] if n['name'] == '需求自定义类型']

            if not issue_uuid:
                param = i.add_standard_issue()[0]
                param.json_update('issue_type.name', '需求自定义类型')
                param.uri_args({'project_uuid': new_proj})
                res = self.call(issue.IssuesAdd, param)
                issue_uuid = [res.value('uuid')]

            # 项目中添加自定义工作项
            p = i.add_project_issue()[0]
            p.json['issue_type_uuids'] = issue_uuid
            p.uri_args({'project_uuid': new_proj})
            self.call(issue.IssueProjectAdd, p)

        with step('修改目标项目为「项目B」，目标工作项类型为「自定义类型」'):
            tp = IssueAction.task_param('需求', '需求自定义类型', old_proj, new_proj)

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

    @story('152015 需求管理-批量移动：目标父工作项状态被删除（父工作项下有子工作项）')
    def test_demand_del_target_parent_task_status(self, demand):
        """批量移动时删除父工作项状态"""

        parent_uuid = demand['task'][8]  # 选择需求9
        old_proj, new_proj = demand['old_proj'], demand['new_proj']

        with step('修改目标项目B，修改目标工作项状态为：未开始'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子需求', '需求', '任务')

            with step('项目B下的工作项类型「需求」的状态「未开始」被删除'):
                param.json_update('rules[0].target_status_uuid', 'F8ruTEST')
                res = self.call(task.TaskBatchMove, param)

                mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"NotFound.BatchTask.TargetIssueStatus": 2})

    @story('152016 需求管理-批量移动：目标父工作项和子工作项类型被删除（部分子工作项类型被删除）')
    def test_demand_del_task_and_subtask_type(self, demand):
        """批量移动时删除工作项和子工作项类型"""

        parent_uuid = demand['task'][9]  # 选择需求10
        old_proj, new_proj = demand['old_proj'], demand['new_proj']

        with step('修改目标项目，修改目标工作项类型为 任务和子任务'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子任务', '需求', '任务')

            with step('项目B下的工作项类型「任务」和「子任务」被删除'):
                # 获取工作项-需求/子任务 uuid
                issue_id = TaskAction.issue_type_uuid('任务')[0]
                sub_issue_id = TaskAction.issue_type_uuid('子任务')[0]

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

    @story('152011 需求管理-批量移动：检查移动后保留的内容')
    def test_check_content_after_moved(self):
        pass

    @story('151983 需求管理-批量移动：没有父工作项下某个子工作项的查看权限时移动')
    def test_no_permission_of_sub_issue(self):
        pass
