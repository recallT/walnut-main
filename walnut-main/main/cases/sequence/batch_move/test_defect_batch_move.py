import time

from falcons.check import Checker
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture, step

from main.actions.issue import IssueAction
from main.actions.task import TaskAction, team_stamp
from main.api import task, issue
from main.helper.extra import Extra
from main.params import task as t, issue as i


@fixture(scope='module', autouse=True)
def defect():
    # 新建两个测试项目，供缺陷批处理使用
    creator = Extra(ApiMeta)
    p_uuid_one = creator.new_project(f'缺陷批处理pro_one')
    time.sleep(10.5)
    p_uuid_two = creator.new_project(f'缺陷批处理pro_two')

    ise = TaskAction.new_issue_batch(10, issue_type_name='缺陷', proj_uuid=p_uuid_one)

    return {'task': ise[0], 'backup_task': ise[1], 'old_proj': p_uuid_one, 'new_proj': p_uuid_two}


@fixture(scope='module', autouse=True)
def del_defect(defect):
    """批量删除缺陷"""
    yield

    TaskAction.del_task_batch(defect['task'])

    # 清除项目数据
    time.sleep(1)
    creator = Extra(ApiMeta)
    creator.del_project(defect['old_proj'])
    creator.del_project(defect['new_proj'])


@feature('缺陷管理-批量移动')
class TestDefectBatchMove(Checker):
    """缺陷管理批量移动案例"""

    @story('152027 目标父工作项类型被删除（父工作项下有子工作项）')
    def test_defect_del_target_issue_type(self, defect):
        """批量移动时删除目标工作项类型"""

        parent_uuid = defect['task'][3]  # 选择缺陷4
        old_proj, new_proj = defect['old_proj'], defect['new_proj']

        with step('修改目标项目，修改目标工作项类型为 任务'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子需求', '缺陷', '任务')

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

    @story('152033 目标子工作项状态被删除（子工作项下没有子工作项）')
    def test_defect_del_sub_task_status(self, defect):
        """批量移动时删除子工作项状态"""

        parent_uuid = defect['task'][6]  # 选择缺陷7
        old_proj, new_proj = defect['old_proj'], defect['new_proj']

        with step('修改目标项目B，修改目标子工作项状态为：已完成'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子需求', '缺陷')

            with step('项目B下的工作项类型「子需求」的状态「已完成」被删除'):
                param.json_update('rules[1].target_status_uuid', 'F8ruTEST')
                res = self.call(task.TaskBatchMove, param)

                mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"NotFound.BatchTask.TargetIssueStatus": 2})

    @story('152035 目标父工作项状态被删除（父工作项下有子工作项）')
    def test_defect_del_target_parent_task_status(self, defect):
        """批量移动时删除父工作项状态"""

        parent_uuid = defect['task'][8]  # 选择缺陷9
        old_proj, new_proj = defect['old_proj'], defect['new_proj']

        with step('修改目标项目B，修改目标工作项状态为：未开始'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子需求', '缺陷', '任务')

            with step('项目B下的工作项类型「任务」的状态「未开始」被删除'):
                param.json_update('rules[0].target_status_uuid', 'F8ruTEST')
                res = self.call(task.TaskBatchMove, param)

                mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"NotFound.BatchTask.TargetIssueStatus": 2})

    @story('152037 批量移动父子工作项（仅修改目标项目）')
    def test_defect_move_up_prj(self, defect):
        """批量移动工作项修改项目"""

        parent_uuid = defect['task'][1]  # 选择缺陷2
        old_proj, new_proj = defect['old_proj'], defect['new_proj']

        with step('更改目标项目为：项目B'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子需求', '缺陷')
            res = self.call(task.TaskBatchMove, param)

            mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 2)

    @story('152040 目标父工作项和子工作项状态被删除（部分子工作项状态被删除）')
    def test_defect_del_task_status(self, defect):
        """批量移动时删除工作项状态"""

        parent_uuid = defect['task'][5]  # 选择缺陷6
        old_proj, new_proj = defect['old_proj'], defect['new_proj']

        with step('修改目标项目B，修改目标工作项状态为：已完成，子任务目标工作项状态为：进行中'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子需求', '缺陷')

            with step('项目B下的工作项类型「缺陷」的状态「已完成」被删除，「子需求」的状态「进行中」被删除'):
                param.json_update('rules[0].target_status_uuid', 'F8ruTEST')
                param.json_update('rules[1].target_status_uuid', 'Q8ruTEST')
                res = self.call(task.TaskBatchMove, param)

                mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"NotFound.BatchTask.TargetIssueStatus": 2})

    @story('152043 目标父工作项和子工作项类型被删除（部分子工作项类型被删除）')
    def test_defect_del_task_and_subtask_type(self, defect):
        """批量移动时删除工作项和子工作项类型"""

        parent_uuid = defect['task'][9]  # 选择缺陷10
        old_proj, new_proj = defect['old_proj'], defect['new_proj']

        with step('修改目标项目，修改目标工作项类型为 任务和子任务'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子任务', '缺陷', '任务')

            with step('项目B下的工作项类型「任务」和「子任务」被删除'):
                # 获取工作项-任务/子任务 uuid
                issue_id = TaskAction.issue_type_uuid('任务')[0]
                sub_issue_id = TaskAction.issue_type_uuid('子任务')[0]

                # 删除任务类型
                pp = i.delete_project_issue()[0]
                pp.uri_args({'issue_uuid': issue_id, 'project_uuid': new_proj})
                self.call(issue.IssueProjectDelete, pp)

                # 删除子任务的工作项
                sub_uuid = param.json_value('tasks_related[0].sub_uuids')[0]
                TaskAction.del_task(sub_uuid)
                # 删除子任务类型
                pp.uri_args({'issue_uuid': sub_issue_id, 'project_uuid': new_proj})
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
                # 添加已删除的工作项类型-子任务
                p.json['issue_type_uuids'] = [sub_issue_id]
                self.call(issue.IssueProjectAdd, p)

    @story('152047 移动的目标项目被删除')
    def test_defect_del_target_prj(self, defect):
        """批量移动时移除项目目标"""

        uuid = defect['task'][0]  # 选择缺陷1
        old_proj, new_proj = defect['old_proj'], defect['new_proj']

        task_param = IssueAction.task_param('缺陷', '任务', old_proj, new_proj)

        with step('需求-->修改目标项目为项目B，再删除项目B'):
            param = t.batch_move_task([uuid], task_param['old'], task_param['new'], old_proj)[0]
            param.json_update('rules[0].target_project_uuid', 'AV8G6Ypr3b95QkWk')  # 替换成不存在的项目uuid
            res = self.call(task.TaskBatchMove, param)

            mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0)

    @story('152050 进入批量移动页面，选择的工作项下新增了子工作项（选择的父下存在子工作项）')
    def test_defect_opt_add_sub_task(self, defect):
        """批量移动操作时添加子工作项"""

        parent_uuid = defect['task'][2]  # 选择缺陷3
        old_proj, new_proj = defect['old_proj'], defect['new_proj']

        with step('修改目标项目，修改目标工作项类型'):
            task_param = IssueAction.task_param('缺陷', '任务', old_proj, new_proj)
            param = t.batch_move_task([parent_uuid], task_param['old'], task_param['new'], old_proj)[0]

            with step('此时缺陷下新增了一个子工作项'):
                IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子需求', '缺陷')

            res = self.call(task.TaskBatchMove, param)

            mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"Blocked.SubTask.Increased": 2})

    @story('152057 选择移动的父工作项被删除')
    def test_defect_del_parent_task(self, defect):
        """批量移动时删除父工作项"""

        parent_uuid = defect['task'][4]  # 选择缺陷5
        old_proj, new_proj = defect['old_proj'], defect['new_proj']

        with step('修改目标项目，修改目标工作项类型'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, '子需求', '缺陷', '任务')

            with step('删除项目下的缺陷'):
                TaskAction.del_task(parent_uuid)

                res = self.call(task.TaskBatchMove, param)

                mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"NotFound.BatchTask.Task": 2})

    @story('152062 目标父工作项类型为自定义标准工作项')
    def test_defect_target_task_customize(self, defect):
        """目标工作项是自定义工作项"""

        uuid = defect['task'][7]  # 选择需求8
        old_proj, new_proj = defect['old_proj'], defect['new_proj']

        with step('前置条件'):
            # 添加自定义工作项
            resp = team_stamp({"issue_type": 0})
            issue_uuid = [n['uuid'] for n in resp['issue_type']['issue_types'] if n['name'] == '缺陷自定义类型']

            if not issue_uuid:
                param = i.add_standard_issue()[0]
                param.json_update('issue_type.name', '缺陷自定义类型')
                param.uri_args({'project_uuid': new_proj})
                res = self.call(issue.IssuesAdd, param)
                issue_uuid = [res.value('uuid')]

            # 项目中添加自定义工作项
            p = i.add_project_issue()[0]
            p.json['issue_type_uuids'] = issue_uuid
            p.uri_args({'project_uuid': new_proj})
            self.call(issue.IssueProjectAdd, p)

        with step('修改目标项目为「项目B」，目标工作项类型为「自定义类型」'):
            tp = IssueAction.task_param('缺陷', '缺陷自定义类型', old_proj, new_proj)

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
