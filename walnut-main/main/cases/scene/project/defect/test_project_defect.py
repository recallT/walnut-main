"""
@File    ：test_project_defect.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/5/17
@Desc    ：
"""
from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, parametrize, step

from main.actions.task import TaskAction
from main.api import task as api
from main.params import task as p
from main.params.const import ACCOUNT


@fixture(scope='module')
def batch_defect():
    """批量创建缺陷，用于用例测试"""
    task_uuids, backup_task_uuid = TaskAction.new_issue_batch(issue_type_name='缺陷')

    if TaskAction.wait_to_done(backup_task_uuid):
        return task_uuids


@feature('缺陷管理')
class TestProjectsDefect(Checker):
    """"""

    @story('T43708 工作项详情：合并缺陷')
    @parametrize('param', p.merge_defect())
    def test_merge_defect(self, param, batch_defect):
        """"""
        # 1.合并缺陷
        # 2.查看任务消息 message 里边有合并记录
        with step('合并缺陷'):
            param.json_update('merge_uuid', batch_defect[1])
            param.uri_args({'task_uuid': batch_defect[0]})
            resp = self.call(api.TaskMergeDefect, param)
            resp.check_response('code', 200)

        with step(f'查看缺陷A（{batch_defect[0]}） 的动态消息'):
            resp = TaskAction.task_messages(batch_defect[0])
            messages = [r for r in resp.json()['messages'] if 'object_attr' in r]
            # 有合并动态
            self.check_key(messages, 'merge_defect', batch_defect[1])
            # 有关联动态
            self.check_related_key(messages, batch_defect[1])

        with step(f'查看缺陷B（{batch_defect[1]}） 的动态消息'):
            resp = TaskAction.task_messages(batch_defect[1])
            messages = [r for r in resp.json()['messages'] if 'object_attr' in r]
            # 有合并动态
            self.check_key(messages, 'merge_defect', batch_defect[0])
            # 有关联动态
            self.check_related_key(messages, batch_defect[0])

    @story('43696 工作项详情：缺陷转需求（新建团队）')
    @story('43697 工作项详情：缺陷转需求（已有团队）')
    def test_defect_to_demand(self, batch_defect):
        """"""
        # 1. 先转化成需求
        # 这里有一个关闭缺陷的接口请求，暂未实现，步骤2 不检查相关日志
        # 2. 检查缺陷消息日志， 有关联需求记录，有转换记录，--有解决方式更新记录(不检查，因为没调接口)--
        # 3. 查看需求日志, 有关联需求记录
        with step('缺陷转为需求'):
            param = TaskAction.new_issue(issue_type_name='需求', param_only=True)
            param.uri_args({'task_uuid': batch_defect[2]})
            demand_resp = self.call(api.TaskCreateDemand, param)
            demand_uuid = demand_resp.value('tasks[0].uuid')

        with step(f'查看缺陷（{batch_defect[2]}） 的动态消息'):
            resp = TaskAction.task_messages(batch_defect[2])
            messages = [r for r in resp.json()['messages'] if 'object_attr' in r]
            # 有转化动态
            self.check_key(messages, 'create_demand_by_bug', demand_uuid)
            # 有关联动态
            self.check_related_key(messages, demand_uuid)
        with step(f'查看需求（{demand_uuid}） 的动态消息'):
            resp = TaskAction.task_messages(demand_uuid)
            messages = [r for r in resp.json()['messages'] if 'object_attr' in r]
            # 有关联动态
            self.check_related_key(messages, batch_defect[2])

    @story('T147198 缺陷管理-导出工作项：当工时默认单位为小时 时，导出缺陷')
    def test_export_defect(self):
        data = {"must": [{"in": {"field_values.field006": [ACCOUNT.project_uuid]}}]}

        TaskAction.export_issue(data)

    @classmethod
    def check_key(cls, messages, key_name, expect_uuid):
        merge_resp = [r for r in messages if r['object_attr'] == key_name][0]
        assert merge_resp['ext']['uuid'] == expect_uuid

    @classmethod
    def check_related_key(cls, messages, expect_key):
        merge_resp = [r for r in messages if r['object_attr'] == 'related_task'][0]
        assert merge_resp['ext']['object_uuid'] == expect_key
