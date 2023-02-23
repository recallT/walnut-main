import time

from falcons.check import Checker
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture, step

from main.actions.issue import IssueAction
from main.actions.task import TaskAction
from main.api import task
from main.helper.extra import Extra
from main.params import task as t


@fixture(scope='module')
def task_data():
    # 新建两个测试项目，供需求批处理使用
    creator = Extra(ApiMeta)
    old_proj = creator.new_project(f'任务batch_1pro_one')
    time.sleep(10.5)
    new_proj = creator.new_project(f'任务batch_1pro_two')

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
class TestTaskBatchMoveOne(Checker):

    @story('151804 任务管理-批量移动：批量移动父子工作项（仅修改目标项目）')
    def test_batch_move_task_up_prj(self, task_data):
        """批量移动工作项修改项目"""
        parent_uuid = task_data['task'][0]  # 选择任务0
        old_proj, new_proj = task_data['old_proj'], task_data['new_proj']

        with step('更改目标项目为：项目B'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, new_issue_type='任务')
            res = self.call(task.TaskBatchMove, param)

            mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 2)

    @story('151903 任务管理-批量移动：移动的目标项目被删除')
    def test_move_target_prj(self, task_data):
        """批量移动时移除项目目标"""
        uuid = task_data['task'][1]  # 选择任务1
        old_proj, new_proj = task_data['old_proj'], task_data['new_proj']

        task_param = IssueAction.task_param('任务', '需求', old_proj, new_proj)

        with step('任务-->修改目标项目为项目B，再删除项目B'):
            param = t.batch_move_task([uuid], task_param['old'], task_param['new'], old_proj)[0]
            param.json_update('rules[0].target_project_uuid', 'AV8G6Ypr3b95QkWk')  # 替换成不存在的项目uuid
            res = self.call(task.TaskBatchMove, param)

            mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0)

    @story('151930 任务管理-批量移动：进入批量移动页面，选择的工作项下新增了子工作项（选择的父下存在子工作项）')
    def test_batch_opt_add_sub_task(self, task_data):
        """批量移动操作时添加子工作项"""
        parent_uuid = task_data['task'][5]  # 选择任务5
        old_proj, new_proj = task_data['old_proj'], task_data['new_proj']

        with step('项目选择，目标工作项类型选择：任务->缺陷'):
            task_param = IssueAction.task_param('任务', '缺陷', old_proj, new_proj)
            param = t.batch_move_task([parent_uuid], task_param['old'], task_param['new'], old_proj)[0]

            with step('此时任务下新增了一个子工作项'):
                IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, new_issue_type='缺陷')

            res = self.call(task.TaskBatchMove, param)

            mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 0, {"Blocked.SubTask.Increased": 2})

    @story('134286 任务管理：批量移动工作项')
    @story('133601 任务管理-更多：移动工作项')
    def test_batch_move_task(self, task_data):
        uuids = task_data['task'][6:8]  # 选择任务6、任务7
        old_proj, new_proj = task_data['old_proj'], task_data['new_proj']

        task_param = IssueAction.task_param('任务', '缺陷', old_proj, new_proj)

        with step('项目选择，目标工作项类型选择：任务->缺陷'):
            param = t.batch_move_task(uuids, task_param['old'], task_param['new'], old_proj)[0]
            res = self.call(task.TaskBatchMove, param)

            mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 2)

    @story('134285 任务管理：批量移动存在子工作的工作项')
    @story('133600 任务管理-更多：移动存在子工作的工作项')
    def test_batch_move_sub_task(self, task_data):
        parent_uuid = task_data['task'][8]  # 选择任务8
        old_proj, new_proj = task_data['old_proj'], task_data['new_proj']

        with step('项目选择，目标工作项类型选择：任务->缺陷'):
            param = IssueAction.need_sub_task(parent_uuid, old_proj, new_proj, new_issue_type='缺陷')
            res = self.call(task.TaskBatchMove, param)

            mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 2)

    @story('134289 任务管理：批量移动工作项（无子工作项的单个工作项）')
    def test_batch_move_single_task(self, task_data):
        uuids = task_data['task'][9]  # 选择任务9
        old_proj, new_proj = task_data['old_proj'], task_data['new_proj']

        task_param = IssueAction.task_param('任务', '需求', old_proj, new_proj)

        with step('项目选择，目标工作项类型选择：任务->需求'):
            param = t.batch_move_task([uuids], task_param['old'], task_param['new'], old_proj)[0]
            res = self.call(task.TaskBatchMove, param)

            mv_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(mv_uuid, 1)
