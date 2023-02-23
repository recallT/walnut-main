"""
@Desc: 项目设置-工作项类型-工作项工作流
"""
import time

from falcons.check import Checker
from falcons.com.nick import story, step, fixture, feature
from main.helper.extra import Extra
from falcons.com.meta import ApiMeta
from main.actions.task import TaskAction as Ta
from main.api.issue import StatusAdd, ProjWorkflowStatusAdd
from main.params import issue, conf


@fixture(scope='module', autouse=True)
def permission_data():
    # 创建一个单独项目
    time.sleep(2)
    creator = Extra(ApiMeta)
    p_id = creator.new_project(f'工作项工作流-测试')
    # 获取系统中存在的一个成员uuid
    return p_id


@fixture(scope='module', autouse=True)
def _del_project(permission_data):
    yield
    # 清除项目数据
    creator = Extra(ApiMeta)
    creator.del_project(permission_data)


@feature('项目设置-工作项-工作流')
class TestProjTaskWorkFlow(Checker):

    @story("T123167 工作项工作流：添加多个工作项状态--子任务")
    def test_proj_sub_task_workflow_add_status(self, permission_data):
        # 获取 子任务 工作项类型 的uuid
        type = '子任务'
        issue_type_uuid = Ta.issue_type_uuid(type, project_uuid=permission_data)[0]
        # 存在两个新建的工作项状态
        with step('前置条件'):
            # 存在两个工作项状态
            parm_1 = conf.status_add()[0]
            resp_1 = self.call(StatusAdd, parm_1)
            uuid_1 = resp_1.value('uuid')

            parm_2 = conf.status_add()[0]
            resp_2 = self.call(StatusAdd, parm_2)
            uuid_2 = resp_2.value('uuid')

            status_uuids = [uuid_1, uuid_2]

        with step("给子任务 添加两个工作流的状态"):
            for u in status_uuids:
                param = issue.issue_workflow_status_add()[0]
                param.json['task_status_configs'].append({"status_uuid": u, "default": False})
                param.uri_args({'issue_type_uuid': issue_type_uuid})
                param.uri_args({'project_uuid': permission_data})
                self.call(ProjWorkflowStatusAdd, param)

    @story("T123157 工作项工作流：添加多个工作项状态--任务")
    def test_proj_task_workflow_add_status(self, permission_data):
        # 获取 任务 工作项类型 的uuid
        type = '任务'
        issue_type_uuid = Ta.issue_type_uuid(type, project_uuid=permission_data)[0]
        # 存在两个新建的工作项状态
        with step('前置条件'):
            # 存在两个工作项状态
            parm_1 = conf.status_add()[0]
            resp_1 = self.call(StatusAdd, parm_1)
            uuid_1 = resp_1.value('uuid')

            parm_2 = conf.status_add()[0]
            resp_2 = self.call(StatusAdd, parm_2)
            uuid_2 = resp_2.value('uuid')

            status_uuids = [uuid_1, uuid_2]

        with step("给任务 添加两个工作流的状态"):
            for u in status_uuids:
                param = issue.issue_workflow_status_add()[0]
                param.json['task_status_configs'].append({"status_uuid": u, "default": False})
                param.uri_args({'issue_type_uuid': issue_type_uuid})
                param.uri_args({'project_uuid': permission_data})
                self.call(ProjWorkflowStatusAdd, param)
