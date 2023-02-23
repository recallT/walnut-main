"""
@Desc：全局配置-工作项状态
"""
import time

from falcons.check import Checker, go
from falcons.com.nick import feature, story, fixture, step

from main.actions import sprint
from main.actions.task import team_stamp, global_issue_type, TaskAction
from main.api import issue as i, issue
from main.params import conf, task
from main.params.issue import issue_workflow_set_init


@fixture(scope='module')
def uuid_data():
    return []


@fixture(scope='module', autouse=True)
def clear_issue_status(uuid_data):
    yield

    if uuid_data:
        issue_uuid = global_issue_type().get('uuid')
        param = conf.status_delete()[0]

        for u in uuid_data:
            param.uri_args({'issue_uuid': issue_uuid})
            param.uri_args({'status_uuid': u})

            # 清除工作项工作流中被使用的工作项状态
            go(i.IssueStatusDelete, param)

            time.sleep(1)
            # 清除工作项状态
            try:
                go(i.StatusDelete, param)
            except AssertionError:
                print('InUse.TaskStatus.UsedInProject')


@feature('全局配置-工作项状态')
class TestIssueStatus(Checker):

    @story('131530 新建进行中类型的工作项状态')
    def test_in_progress_status_add(self, uuid_data):
        with step('新建工作项状态，类型选择：进行中'):
            param = conf.status_add()[0]
            resp = self.call(i.StatusAdd, param)

            status_name = resp.value('name')
            status_uuid = resp.value('uuid')

            uuid_data.append(status_uuid)

        with step('进入配置中心-项目管理配置-工作项属性。查看系统工作项属性'):
            stamp = team_stamp({'field': 0})
            names = [s['name'] for s in stamp['field']['fields'] if status_name in s['name']]

            assert f'{status_name}-停留次数' in names
            assert f'{status_name}-停留时间' in names

        with step('进入项目A-项目设置-工作项类型-任意工作项-工作项工作流页面，查看可选择的状态'):
            p_stamp = team_stamp({'task_status': 0})
            p_names = [s['name'] for s in p_stamp['task_status']['task_statuses']]

            assert status_name in p_names

    @story('131517 编辑未被使用的工作项状态名称')
    def test_unused_issue_status_name(self, uuid_data):
        with step('修改状态名称'):
            param = conf.status_update(uuid_data[0])[0]
            param.uri_args({'status_uuid': uuid_data[0]})

            resp = self.call(i.StatusUpdate, param)
            status_name = resp.value('name')

        with step('进入项目A-项目设置-工作项类型-任意工作项-工作项工作流页面，查看可选择的状态'):
            p_stamp = team_stamp({'task_status': 0})
            p_names = [s['name'] for s in p_stamp['task_status']['task_statuses']]

            assert status_name in p_names

    @story('131518 编辑未被使用的工作项状态状态类型')
    def test_unused_issue_status_type(self, uuid_data):
        with step('修改状态为：未开始'):
            param = conf.status_update(uuid_data[0])[0]
            param.json_update('task_status.category', 'to_do')
            param.uri_args({'status_uuid': uuid_data[0]})

            resp = self.call(i.StatusUpdate, param)
            resp.check_response('category', 'to_do')

    @story('131519 编辑已被使用的工作项状态名称')
    def test_used_issue_status_name(self, uuid_data):
        with step('前置条件'):
            issue_uuid = global_issue_type().get('uuid')

            # 存在工作项状态在配置中心-工作项类型中被使用
            param = conf.issue_status_add(uuid_data[0])[0]
            param.uri_args({'issue_uuid': issue_uuid})
            self.call(i.IssueStatusAdd, param)

        with step('修改已使用状态名称'):
            param = conf.status_update(uuid_data[0])[0]
            param.uri_args({'status_uuid': uuid_data[0]})

            resp = self.call(i.StatusUpdate, param)
            status_name = resp.value('name')

        with step('进入项目A-项目设置-工作项类型-任意工作项-工作项工作流页面，查看可选择的状态'):
            p_stamp = team_stamp({'task_status': 0})
            p_names = [s['name'] for s in p_stamp['task_status']['task_statuses']]

            assert status_name in p_names

    @story('131520 编辑已被使用的工作项状态状态类型')
    def test_used_issue_status_type(self, uuid_data):
        with step('修改已使用状态为：进行中'):
            param = conf.status_update(uuid_data[0])[0]
            param.uri_args({'status_uuid': uuid_data[0]})

            resp = self.call(i.StatusUpdate, param)
            resp.check_response('category', 'in_progress')

    @story('131527 删除未被使用的工作项状态')
    def test_unused_issue_status_delete(self):
        with step('新建工作项状态'):
            param = conf.status_add()[0]
            resp = self.call(i.StatusAdd, param)

            status_uuid = resp.value('uuid')

        with step('删除工作状态'):
            param = conf.status_delete()[0]
            param.uri_args({'status_uuid': status_uuid})
            self.call(i.StatusDelete, param)

        with step('进入项目A-项目设置-工作项类型-任意工作项-工作项工作流页面，查看可选择的状态'):
            s_stamp = team_stamp({'task_status': 0})
            s_uuid = [s['uuid'] for s in s_stamp['task_status']['task_statuses']]

            assert status_uuid not in s_uuid

    @story('131528 删除已被使用的工作项状态')
    def test_used_issue_status_delete(self, uuid_data):
        with step('删除工作状态'):
            time.sleep(1)
            param = conf.status_delete()[0]
            param.uri_args({'status_uuid': uuid_data[0]})
            resp = self.call(i.StatusDelete, param, status_code=400)

            resp.check_response('type', 'InUse')

    @story('123150 工作项工作流：添加单个工作项状态')
    def test_workflow_add_one_issue_status(self, uuid_data):
        with step('前置条件'):
            # 存在工作项状态
            param = conf.status_add()[0]
            resp = self.call(i.StatusAdd, param)

            status_uuid = resp.value('uuid')
            uuid_data.append(status_uuid)

        with step('工作流添加工作项状态'):
            issue_uuid = global_issue_type().get('uuid')

            param = conf.issue_status_add(status_uuid)[0]
            param.uri_args({'issue_uuid': issue_uuid})
            self.call(i.IssueStatusAdd, param)

    @story('123171 工作项工作流：添加多个工作项状态')
    def test_workflow_add_multi_issue_status(self, uuid_data):
        with step('前置条件'):
            # 存在两个工作项状态
            parm_1 = conf.status_add()[0]
            resp_1 = self.call(i.StatusAdd, parm_1)
            uuid_1 = resp_1.value('uuid')

            parm_2 = conf.status_add()[0]
            resp_2 = self.call(i.StatusAdd, parm_2)
            uuid_2 = resp_2.value('uuid')

            status_uuids = [uuid_1, uuid_2]
            uuid_data += status_uuids

        with step('工作流添加工作项状态'):
            issue_uuid = global_issue_type().get('uuid')

            for u in status_uuids:
                param = conf.issue_status_add(u)[0]
                param.uri_args({'issue_uuid': issue_uuid})
                self.call(i.IssueStatusAdd, param)

    @story('T123151 工作项工作流：添加单个工作项状态')
    @story('T123225 工作项工作流：详情视图下移除状态（无相关联的步骤）')
    def test_sub_task_add_and_del_status(self):
        # 获取状态UUID
        data = {
            "task_status": 0
        }
        resp = sprint.team_stamp(data)
        status_uuid = [r['uuid'] for r in resp.value('task_status.task_statuses') if r['name'] == '测试提交'][0]

        issue_uuid = TaskAction.issue_type_uuid('子任务')[0]
        with step('添加单个工作项状态'):
            param = conf.issue_status_add(status_uuid)[0]
            param.uri_args({'issue_uuid': issue_uuid})
            self.call(i.IssueStatusAdd, param)
        with step('详情视图下移除状态（无相关联的步骤'):
            param.uri_args({'status_uuid': status_uuid})
            go(i.IssueStatusDelete, param)

    @story('T123162 工作项工作流：添加多个工作项状态-子任务')
    def test_sub_task_workflow_add_multi_issue_status(self, uuid_data):
        with step('前置条件'):
            # 存在两个工作项状态
            parm_1 = conf.status_add()[0]
            resp_1 = self.call(i.StatusAdd, parm_1)
            uuid_1 = resp_1.value('uuid')

            parm_2 = conf.status_add()[0]
            resp_2 = self.call(i.StatusAdd, parm_2)
            uuid_2 = resp_2.value('uuid')

            status_uuids = [uuid_1, uuid_2]
            uuid_data += status_uuids

        with step('工作流添加工作项状态'):
            issue_uuid = TaskAction.issue_type_uuid('子任务')[0]

            for u in status_uuids:
                param = conf.issue_status_add(u)[0]
                param.uri_args({'issue_uuid': issue_uuid})
                self.call(i.IssueStatusAdd, param)

        with step('清除数据'):
            for u in status_uuids:
                param.uri_args({'status_uuid': u})
                go(i.IssueStatusDelete, param)

    @story('T123269 工作项工作流：新建步骤')
    def test_sub_task_workflow_add_step(self):
        data = {
            "transition": 0,
            "task_status_config": 0
        }
        resp = sprint.team_stamp(data)
        issue_type_uuid = TaskAction.issue_type_uuid('子任务')[0]
        start_status_uuid = \
            [f['status_uuid'] for f in resp.value('task_status_config.task_status_configs') if
             f['issue_type_uuid'] == issue_type_uuid and f['default'] == True][0]

        end_status_uuid = [f['status_uuid'] for f in resp.value('task_status_config.task_status_configs') if
                           f['issue_type_uuid'] == issue_type_uuid and f['default'] == False][0]
        with step('新建步骤'):
            param = task.issue_workflow_transition_add(issue_type_uuid, start_status_uuid, end_status_uuid)[0]
            param.json_update('transitions[0].project_uuid', '')
            param.json_update('transitions[0].name', 'test')
            param.uri_args({'issue_type': issue_type_uuid})
            resp = self.call(i.IssueStepAdd, param)

        with step('删除数据'):
            transition_uuid = [r['uuid'] for r in resp.value('default_configs.default_transitions') if
                               r['name'] == 'test'][0]
            param.uri_args({'transitions_uuid': transition_uuid})
            self.call(i.IssueStepDel, param)

    @story('T123125 工作项工作流：设置初始状态')
    def test_set_default_status(self):
        data = {
            "transition": 0,
            "task_status_config": 0
        }
        resp = sprint.team_stamp(data)
        issue_type_uuid = TaskAction.issue_type_uuid('子任务')[0]
        task_status = [f['status_uuid'] for f in resp.value('task_status_config.task_status_configs') if
                       f['issue_type_uuid'] == issue_type_uuid and f['default'] == True][0]

        with step('设置初始状态'):
            param = issue_workflow_set_init()[0]
            param.uri_args({'issue_type': issue_type_uuid, 'task_status': task_status})
            self.call(i.IssueStepUpdate, param).check_response('uuid', issue_type_uuid)
