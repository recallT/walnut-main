import time

from falcons.check import CheckerChain
from falcons.com.nick import feature, story, fixture, step
from falcons.helper import mocks

from main.actions.issue import IssueAction
from main.actions.task import TaskAction
from main.api import project as prj, task
from main.params import proj as p, task as t
from main.params.const import ACCOUNT


@fixture(scope='module')
def tasks_storage():
    """缓存测试数据"""
    return {
        'task': [],  # 批量创建任务的UUID
        'backup_task': ''  # 后台任务的UUID
    }


@fixture(scope='module', autouse=True)
def del_task(tasks_storage):
    """批量删除任务"""
    yield

    if tasks_storage['task']:
        TaskAction.del_task_batch(tasks_storage['task'])


@feature('任务管理-任务详情')
class TestTaskBatchManage(CheckerChain):

    @story('任务管理-批量新建任务')
    @story('131403 批量新建工作项：批量录入标题后新建')
    def test_add_task_batch(self, tasks_storage):
        m = TaskAction.new_issue_batch(10)
        tasks_storage |= {'task': m[0], 'backup_task': m[1], }

    @story('130896 进度管理器：批量新建工作项成功')
    def test_process_info(self, tasks_storage):
        # 持续查询 后台进度状态
        param = p.queues_list()[0]
        for _ in range(10):
            time.sleep(1)
            self.call('查询后台任务进度', prj.QueuesList, param)

            result = [u for u in self.ins.value('batch_tasks') if u['uuid'] == tasks_storage['backup_task']]

            if result[0]['job_status'] == 'done':
                successful_objects = result[0]['successful_objects']
                # 检查一下任务UUID 都在成功对象里边
                assert not set(successful_objects).difference(set(tasks_storage['task']))
                break

    @story('133727 任务管理-批量复制工作项：批量复制单个工作项')
    def test_batch_copy(self, tasks_storage):
        res = TaskAction.task_copy_batch([tasks_storage['task'][0]])
        res.check_response('job_type', 'copy_tasks')

        copy_uuid = res.value('uuid')

        IssueAction.process_detail_and_close(copy_uuid, 1)

    @story('133728 任务管理-批量复制工作项：批量复制为其他工作项类型')
    def test_batch_copy_convert_type(self, tasks_storage):
        with step('目标工作项类型选择：任务->缺陷'):
            res = TaskAction.task_copy_batch(tasks_storage['task'][:3], '缺陷')
            res.check_response('job_type', 'copy_tasks')

            copy_uuid = res.value('uuid')

            IssueAction.process_detail_and_close(copy_uuid, 3)

    @story('133729 任务管理-批量复制工作项：批量复制为原工作项类型')
    def test_batch_copy_original_type(self, tasks_storage):
        with step('目标工作项类型选择：任务->任务'):
            res = TaskAction.task_copy_batch(tasks_storage['task'][:3])
            res.check_response('job_type', 'copy_tasks')

            copy_uuid = res.value('uuid')

            IssueAction.process_detail_and_close(copy_uuid, 3)

    @story('134284 任务管理：批量修改工作项属性（修改单个工作项属性值）')
    def test_batch_update_task_single_field(self, tasks_storage):
        """批量更新工作项单个字段"""

        with step('目标工作项属性选择：需求：-修改负责人'):
            param = t.field_value_update()[0]
            param.json_update('tasks[0].task_uuid', tasks_storage['task'][3])
            self.call('修改字段值', task.TasksUpdateField, param)

            up_uuid = self.ins.value('uuid')

            IssueAction.process_detail_and_close(up_uuid, 1)

    @story('134283 任务管理：批量修改工作项属性（批量修改多种工作项属性值）')
    def test_batch_update_task_many_field(self, tasks_storage):
        """批量更新工作项多个字段"""
        start = mocks.day_timestamp(1)
        end = mocks.day_timestamp()

        with step('目标工作项属性选择：需求：-修改负责人'):
            param = t.field_value_update()[0]
            tasks = []
            for u in tasks_storage['task'][:2]:
                prm = {
                    "task_uuid": u,
                    "field_values": [
                        {
                            "type": 8,
                            "field_uuid": "field004",  # 负责人
                            "value": ACCOUNT.user.owner_uuid
                        },
                        {
                            "type": 5,
                            "field_uuid": "field027",  # 计划开始时间
                            "value": start
                        },
                        {
                            "type": 5,
                            "field_uuid": "field028",  # 计划结束时间
                            "value": end
                        }
                    ]
                }
                tasks.append(prm)

            if tasks:
                param.json_update('tasks', tasks)
                self.call('修改多个字段值', task.TasksUpdateField, param)

                up_uuid = self.ins.value('uuid')

                IssueAction.process_detail_and_close(up_uuid, 2)

    @story('134271 任务管理：批量变更工作项类型')
    def test_batch_update_task_type(self, tasks_storage):
        uuids = tasks_storage['task'][4:6]  # 选择任务5、任务6

        with step('目标工作项类型选择：任务->缺陷/目标工作项状态选择：未开始->未激活'):
            task_param = IssueAction.task_param('任务', '缺陷')

            param = t.batch_update_issue_type(uuids, task_param['old'], task_param['new'])[0]
            self.call('批量变更类型', task.UpdateIssueType, param)

            up_uuid = self.ins.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(up_uuid, 2)

    @story('134291 任务管理：批量转为工作项（变更多个工作项类型）')
    @story('134322 任务管理：转为工作项')
    def test_sub_change_task(self, tasks_storage):
        """子工作项批量转工作项"""
        parent_uuid = tasks_storage['task'][7]  # 选择7

        with step('前置条件'):
            time.sleep(1)
            sub_uuid = TaskAction.new_issue(parent_uuid, '子任务')

            old_status_uuid, old_issue_uuid = TaskAction.get_task_status_and_issue_uid('子任务')
            new_status_uuid, new_issue_uuid = TaskAction.get_task_status_and_issue_uid('任务')

        with step('更多-批量转为工作项，目标工作项类型选择：子任务->任务'):
            param = t.batch_update_issue_type(sub_uuid, [old_status_uuid, old_issue_uuid],
                                              [new_status_uuid, new_issue_uuid])[0]
            param.json_update('action', 'sub_to_std_issue_type')

            self.call('批量转为工作项', task.UpdateIssueType, param)

            up_uuid = self.ins.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(up_uuid, 1)

    @story('134294 任务管理：批量转为子工作项（变更多个工作项）')
    @story('133606 任务管理-更多：转为子工作项')
    def test_task_change_sub(self, tasks_storage):
        """工作项批量转子工作项目"""
        parent_uuid = tasks_storage['task'][8]
        sub_uuid = tasks_storage['task'][9]

        old_status_uuid, old_issue_uuid = TaskAction.get_task_status_and_issue_uid('任务')
        new_status_uuid, new_issue_uuid = TaskAction.get_task_status_and_issue_uid('子任务')

        with step('更多-批量转为工作项，目标工作项类型选择：任务->子任务，选择父工作项'):
            param = t.batch_update_issue_type([sub_uuid], [old_status_uuid, old_issue_uuid],
                                              [new_status_uuid, new_issue_uuid])[0]
            param.json_update('action', 'std_to_sub_issue_type')
            param.json_update('tasks[0].parent_uuid', parent_uuid)

            self.call('批量转为工作项', task.UpdateIssueType, param)

            up_uuid = self.ins.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(up_uuid, 1)

    @story('134276 任务管理：批量删除工作项（删除单个工作项）')
    @story('134275 任务管理：批量删除工作项')
    def test_batch_del_single_task(self):
        uuid = TaskAction.new_issue()

        with step('勾选一个工作项删除'):
            res = TaskAction.del_task_batch(uuid)
            res.check_response('job_type', 'delete_tasks')

            del_uuid = res.value('uuid')

        with step('检查进度条'):
            IssueAction.process_detail_and_close(del_uuid, 1)
