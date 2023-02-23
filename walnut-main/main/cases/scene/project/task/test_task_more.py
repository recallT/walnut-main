import time

from falcons.check import Checker
from falcons.com.nick import feature, story, step, fixture, mark

from main.actions.task import TaskAction
from main.api import current as c
from main.params import current
from main.params.const import ACCOUNT


@fixture(scope='module')
def _add_task():
    m = TaskAction.new_issue_batch()
    TaskAction.wait_to_done(m[1])
    return m[0]


@mark.smoke
@feature('任务管理-更多')
class TestTaskMore(Checker):

    def export(self, must, token=None):
        """
        导出
        :param token
        :param must
        """
        param = current.export_task_job()[0]
        param.json_update('name', f'{ACCOUNT.project_uuid}-任务-全部任务.csv')
        param.json_update('query.must', must)
        ex = self.call(c.ExportTaskJob, param, token)

        key = ex.json()['key']  # 获取下载task的key

        # 下载task
        prm = current.dashboard_opt()[0]
        prm.uri_args({'key_id': key})
        self.call(c.DownloadExportTask, prm, token)

    @story('134255 导出工作项（默认导出')
    def test_export_default_task_job(self):
        with step('属性默认勾选，点击确认'):
            data = [{"must": [{"in": {"field_values.field006": [ACCOUNT.project_uuid]}}]}]
            self.export(data)

    @story('134256 导出工作项（筛选之后导出工作项）')
    def test_export_filter_task_job(self):
        with step('筛选：状态类型  不包含  已完成, 点击导出'):
            data = [{"must": [{"in": {"field_values.field006": [ACCOUNT.project_uuid]}},
                              {"should": [{"must": [{"in": {"field_values.field017": ["to_do", "in_progress"]}}]}]}]}]
            self.export(data)

    @story('T133598 删除没有子工作项的标准工作项')
    def test_del_no_sub_task_of_task(self):
        """"""

    @story('T133599 删除没有子工作项的子工作项')
    def test_del_sub_task_of_sub_task(self, _add_task):
        parent_uuid = _add_task[0]
        sub_uuid = TaskAction.new_issue(parent_uuid, '子任务')[0]

        TaskAction.del_task(sub_uuid)

    @story('T133560 删除存在子工作的工作项')
    def test_del_exist_sub_task(self, _add_task):
        parent_uuid = _add_task[1]
        TaskAction.new_issue(parent_uuid, '子任务')

        TaskAction.del_task(parent_uuid)

    @story('T133612 任务管理-更多：子工作项批量新建多个子工作项')
    def test_batch_add_sub_task(self):
        task = TaskAction.new_issue()[0]
        with step('批量创建子工作项'):
            TaskAction.new_issue(parent_uuid=task, issue_type_name="子任务", is_batch=True)
            TaskAction.del_task(task).check_response('code', 200)
