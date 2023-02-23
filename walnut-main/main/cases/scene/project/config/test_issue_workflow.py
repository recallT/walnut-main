"""
@Desc：项目设置-工作项类型-工作项工作流
"""
from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, step, parametrize

from main.actions.task import proj_team_stamp, team_stamp, TaskAction
from main.api import issue
from main.params import issue as ise


@fixture(scope='module')
def status_storage():
    return {
        'issue_type_uuid': [],
        'status_uuid': []
    }


@feature('工作项类型-工作项工作流')
class TestIssueWorkflow(Checker):

    @story('123137/123139 任务/子任务-添加单个工作项状态')
    @parametrize('types', ('任务', '子任务'))
    def test_proj_workflow_add_one_issue_status(self, types, status_storage):
        with step('前置条件'):
            issue_type_uuid = TaskAction.issue_type_uuid(types)[0]

            # 获取工作项状态配置
            issue_resp = proj_team_stamp({"task_status_config": 0})

            status_uuid = [u['status_uuid'] for u in issue_resp['task_status_config']['task_status_configs'] if
                           u['position'] == 4 and u['default'] != True][0]

            status_storage['issue_type_uuid'].append(issue_type_uuid)
            status_storage['status_uuid'].append(status_uuid)

        with step('添加工作项状态，选择状态'):
            param = ise.issue_workflow_status_add()[0]
            param.json['task_status_configs'].append({"status_uuid": status_uuid, "default": False})
            param.uri_args({'issue_type_uuid': issue_type_uuid})
            resp = self.call(issue.ProjWorkflowStatusAdd, param)

            resp.check_response('task_status_configs[0].status_uuid', status_uuid)

    @story('123209/123224 任务/子任务-详情视图下移除状态（无相关联的步骤）')
    @parametrize('types_num', (0, 1))
    def test_del_no_relation_step(self, types_num, status_storage):
        with step('移除工作项状态弹窗，点击 移除'):
            param = ise.issue_workflow_status_delete()[0]

            if status_storage:
                param.uri_args({'issue_type_uuid': status_storage['issue_type_uuid'][types_num]})
                param.uri_args({'status_uuid': status_storage['status_uuid'][types_num]})
                self.call(issue.ProjWorkflowStatusDelete, param)

    @story('123259/123268 任务/子任务-新建步骤')
    @parametrize('types', ('任务', '子任务'))
    def test_proj_workflow_add_step(self, types):
        issue_type_uuid = TaskAction.issue_type_uuid(types)[0]

        stamp_resp = team_stamp({"issue_type": 0})

        status_uuid = [d['status_uuid'] for n in stamp_resp['issue_type']['issue_types'] if n['uuid'] ==
                       issue_type_uuid for d in n['default_configs']['default_task_status_configs']][1]

        with step('新建步骤，开始状态选择-目标状态选择'):
            param = ise.issue_workflow_transition_add()[0]
            param.json_update('transitions[0].issue_type_uuid', issue_type_uuid)
            param.json_update('transitions[0].start_status_uuid', status_uuid)
            param.json_update('transitions[0].end_status_uuid', status_uuid)
            param.uri_args({'issue_type_uuid': issue_type_uuid})

            resp = self.call(issue.ProjWorkflowTransitionAdd, param)
            resp.check_response('transitions[0].start_status_uuid', status_uuid, 'contains')

            step_uuid = resp.value('transitions[0].uuid')

        with step('清除数据'):
            param.uri_args({'transition_uuid': step_uuid})
            self.call(issue.ProjWorkflowTransitionDelete, param, with_json=False)
