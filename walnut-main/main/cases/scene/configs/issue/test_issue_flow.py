"""
@Desc：全局配置-工作项类型-工作项工作流
"""
from falcons.check import Checker, go
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture, step, mark

from main.actions.task import team_stamp
from main.api import issue as i
from main.params import issue


@fixture(scope='module')
def init_data():
    data = {
        "issue_type": 0,
        "task_status": 0
    }
    return team_stamp(data)


@fixture(scope='module')
def issue_storage():
    return []


@fixture(scope='module', autouse=True)
def issue_opt(issue_storage):
    # 添加自定义标准工作项/子工作项
    params = [issue.add_standard_issue()[0], issue.add_sub_issue()[0]]

    issue_uuids = []

    for p in params:
        resp = go(i.IssuesAdd, p, is_print=False)

        issue_uuids.append(resp.value('uuid'))
        issue_storage.append(resp.value('name'))

    yield

    prm = issue.delete_issue()[0]
    for u in issue_uuids:
        prm.uri_args({'issue_uuid': u})
        go(i.IssueDelete, prm)


label = ApiMeta.env.label


@mark.skipif(label == 'private' or label == 'dev', reason='环境跳过开箱用例')
@feature('全局配置-工作项类型-工作项工作流')
class TestIssueFlow(Checker):

    def get_task_status(self, data, status_name):
        """获取工作项状态uuid"""
        param = [n['uuid'] for n in data['task_status']['task_statuses'] if n['name'] == status_name]

        if param:
            return param[0]

    def get_default_task_status(self, data, issue_type):
        param = [d['status_uuid'] for n in data['issue_type']['issue_types'] if n['name'] == issue_type for d in
                 n['default_configs']['default_task_status_configs']]

        return param

    def get_status_step(self, data, issue_type, step_name):
        param = [d for n in data['issue_type']['issue_types'] if n['name'] == issue_type for d in
                 n['default_configs']['default_transitions'] if d['name'] == step_name]

        if param:
            return param[0]
        else:
            return None

    @story('122990 工作项工作流默认状态及步骤检查（开箱）')
    @story('122993 工作项工作流默认状态及步骤检查（开箱）- 子检查项')
    def test_issue_sub_check_unpack(self, init_data):
        issue_type = '子检查项'

        # 获取工作项状态
        upcoming = self.get_task_status(init_data, '待办')
        finish = self.get_task_status(init_data, '完成')

        with step('查看页面已有默认状态'):
            params = self.get_default_task_status(init_data, issue_type)

            if params:
                assert upcoming in params  # 待办
                assert finish in params  # 完成

        with step('查看待办状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '完成')  # 待办状态的步骤：完成

            if params:
                assert params.get('start_status_uuid') == upcoming
                assert params.get('end_status_uuid') == finish

        with step('查看完成状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '待办')  # 完成状态的步骤：待办

            if params:
                assert params.get('start_status_uuid') == finish
                assert params.get('end_status_uuid') == upcoming

        with step('查看任何状态状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '任何状态')

            assert params is None

    @story('122992 工作项工作流默认状态及步骤检查（开箱）- 需求')
    def test_demand_unpack(self, init_data):
        issue_type = '需求'

        # 获取工作项状态
        not_start = self.get_task_status(init_data, '未开始')
        in_progress = self.get_task_status(init_data, '实现中')
        implement = self.get_task_status(init_data, '已实现')

        with step('查看页面已有默认状态'):
            params = self.get_default_task_status(init_data, issue_type)

            if params:
                assert not_start in params
                assert implement in params

        with step('查看未开始状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '实现中')  # 未开始状态的步骤：实现中

            if params:
                assert params.get('start_status_uuid') == not_start
                assert params.get('end_status_uuid') == in_progress

        with step('查看实现中状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '已实现')  # 实现中状态的步骤：已实现

            if params:
                assert params.get('start_status_uuid') == in_progress
                assert params.get('end_status_uuid') == implement

        with step('查看任何状态状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '任何状态')

            assert params is None

    @story('122991 工作项工作流默认状态及步骤检查（开箱）- 用户故事')
    def test_user_story_unpack(self, init_data):
        issue_type = '用户故事'

        # 获取工作项状态
        not_start = self.get_task_status(init_data, '未开始')
        in_progress = self.get_task_status(init_data, '进行中')
        complete = self.get_task_status(init_data, '已完成')

        with step('查看页面已有默认状态'):
            params = self.get_default_task_status(init_data, issue_type)

            if params:
                assert not_start in params
                assert in_progress in params
                assert complete in params

        with step('查看未开始状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '开始用户故事')  # 未开始状态的步骤：开始用户故事

            if params:
                assert params.get('start_status_uuid') == not_start
                assert params.get('end_status_uuid') == in_progress

        with step('查看进行中状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '完成用户故事')  # 进行中状态的步骤：完成用户故事

            if params:
                assert params.get('start_status_uuid') == in_progress
                assert params.get('end_status_uuid') == complete

        with step('查看已完成状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '进行中')  # 已完成状态的步骤：进行中

            if params:
                assert params.get('start_status_uuid') == complete
                assert params.get('end_status_uuid') == in_progress

        with step('查看任何状态状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '任何状态')

            assert params is None

    @story('122991 工作项工作流默认状态及步骤检查（开箱）- 任务')
    def test_task_unpack(self, init_data):
        issue_type = '任务'

        # 获取工作项状态
        not_start = self.get_task_status(init_data, '未开始')
        in_progress = self.get_task_status(init_data, '进行中')
        complete = self.get_task_status(init_data, '已完成')

        with step('查看页面已有默认状态'):
            params = self.get_default_task_status(init_data, issue_type)

            if params:
                assert not_start in params
                assert in_progress in params
                assert complete in params

        with step('查看未开始状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '开始任务')  # 未开始状态的步骤：开始任务

            if params:
                assert params.get('start_status_uuid') == not_start
                assert params.get('end_status_uuid') == in_progress

        with step('查看已完成状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '重启任务')  # 已完成状态的步骤：重启任务

            if params:
                assert params.get('start_status_uuid') == complete
                assert params.get('end_status_uuid') == not_start

        with step('查看任何状态状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '任何状态')

            assert params is None

    @story('122988 工作项工作流默认状态及步骤检查（开箱）- 子任务')
    def test_sub_task_unpack(self, init_data):
        issue_type = '子任务'

        # 获取工作项状态
        not_start = self.get_task_status(init_data, '未开始')
        in_progress = self.get_task_status(init_data, '进行中')
        complete = self.get_task_status(init_data, '已完成')

        with step('查看页面已有默认状态'):
            params = self.get_default_task_status(init_data, issue_type)

            if params:
                assert not_start in params
                assert in_progress in params
                assert complete in params

        with step('查看未开始状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '开始任务')  # 未开始状态的步骤：开始任务

            if params:
                assert params.get('start_status_uuid') == not_start
                assert params.get('end_status_uuid') == in_progress

        with step('查看已完成状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '重启任务')  # 已完成状态的步骤：重启任务

            if params:
                assert params.get('start_status_uuid') == complete
                assert params.get('end_status_uuid') == not_start

        with step('查看任何状态状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '任何状态')

            assert params is None

    @story('122987 工作项工作流默认状态及步骤检查（开箱）- 工单')
    def test_work_order_unpack(self, init_data):
        issue_type = '工单'

        # 获取工作项状态
        pending = self.get_task_status(init_data, '待处理')
        in_process = self.get_task_status(init_data, '处理中')
        resolve = self.get_task_status(init_data, '已解决')
        close_bill = self.get_task_status(init_data, '已关单')

        with step('查看页面已有默认状态'):
            params = self.get_default_task_status(init_data, issue_type)

            if params:
                assert pending in params
                assert in_process in params
                assert resolve in params

        with step('查看待处理状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '开始处理')  # 待处理状态的步骤：开始处理

            if params:
                assert params.get('start_status_uuid') == pending
                assert params.get('end_status_uuid') == in_process

        with step('查看处理中状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '确认解决')  # 处理中状态的步骤：确认解决

            if params:
                assert params.get('start_status_uuid') == in_process
                assert params.get('end_status_uuid') == resolve

            params = self.get_status_step(init_data, issue_type, '拒绝')  # 处理中状态的步骤：拒绝

            if params:
                assert params.get('start_status_uuid') == in_process
                assert params.get('end_status_uuid') == close_bill

        with step('查看已关单状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '已关单')

            assert params is None

    @story('122986 工作项工作流默认状态及步骤检查（开箱）- 缺陷')
    def test_defect_unpack(self, init_data):
        issue_type = '缺陷'

        # 获取工作项状态
        not_active = self.get_task_status(init_data, '未激活')
        reopen = self.get_task_status(init_data, '重新打开')
        fixed = self.get_task_status(init_data, '已修复')
        verified = self.get_task_status(init_data, '已验证')
        confirm = self.get_task_status(init_data, '已确认')

        with step('查看页面已有默认状态'):
            params = self.get_default_task_status(init_data, issue_type)

            if params:
                assert reopen in params
                assert fixed in params

        with step('查看重新打开状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '已验证')  # 重新打开状态的步骤：已验证

            if params:
                assert params.get('start_status_uuid') == reopen
                assert params.get('end_status_uuid') == verified

        with step('查看已确认状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '已修复')  # 已确认状态的步骤：已修复

            if params:
                assert params.get('start_status_uuid') == confirm
                assert params.get('end_status_uuid') == fixed

        with step('查看已修复状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '已解决')  # 已修复状态的步骤：已解决

            if params:
                assert params.get('start_status_uuid') == fixed
                assert params.get('end_status_uuid') == verified

    @story('122985 工作项工作流默认状态及步骤检查（开箱）- 子需求')
    def test_sub_demand_unpack(self, init_data):
        issue_type = '子需求'

        # 获取工作项状态
        not_active = self.get_task_status(init_data, '未激活')
        planned = self.get_task_status(init_data, '已计划')
        research = self.get_task_status(init_data, '研发中')
        testing = self.get_task_status(init_data, '测试中')

        with step('查看页面已有默认状态'):
            params = self.get_default_task_status(init_data, issue_type)

            if params:
                assert not_active in params
                assert planned in params
                assert research in params

        with step('查看未激活状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '已计划')  # 未激活状态的步骤：已计划

            if params:
                assert params.get('start_status_uuid') == not_active
                assert params.get('end_status_uuid') == planned

        with step('查看研发中状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '开始测试')  # 研发中状态的步骤：开始测试

            if params:
                assert params.get('start_status_uuid') == research
                assert params.get('end_status_uuid') == testing

    @story('122984 工作项工作流默认状态及步骤检查（开箱）- 自定义标准')
    def test_customize_unpack(self, init_data, issue_storage):
        issue_type = issue_storage[0]

        # 获取工作项状态
        not_start = self.get_task_status(init_data, '未开始')
        in_progress = self.get_task_status(init_data, '进行中')
        complete = self.get_task_status(init_data, '已完成')

        with step('查看页面已有默认状态'):
            params = self.get_default_task_status(init_data, issue_type)

            if params:
                assert not_start in params
                assert in_progress in params
                assert complete in params

        with step('查看未开始状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '进行中')  # 未开始状态的步骤：进行中

            if params:
                assert params.get('start_status_uuid') == not_start
                assert params.get('end_status_uuid') == in_progress

        with step('查看已完成状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '未开始')  # 已完成状态的步骤：未开始

            if params:
                assert params.get('start_status_uuid') == complete
                assert params.get('end_status_uuid') == not_start

    @story('122989 工作项工作流默认状态及步骤检查（开箱）- 自定义子工作项')
    def test_sub_customize_unpack(self, init_data, issue_storage):
        issue_type = issue_storage[1]

        # 获取工作项状态
        not_start = self.get_task_status(init_data, '未开始')
        in_progress = self.get_task_status(init_data, '进行中')
        complete = self.get_task_status(init_data, '已完成')

        with step('查看页面已有默认状态'):
            params = self.get_default_task_status(init_data, issue_type)

            if params:
                assert not_start in params
                assert in_progress in params
                assert complete in params

        with step('查看未开始状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '进行中')  # 未开始状态的步骤：进行中

            if params:
                assert params.get('start_status_uuid') == not_start
                assert params.get('end_status_uuid') == in_progress

        with step('查看已完成状态下的步骤'):
            params = self.get_status_step(init_data, issue_type, '未开始')  # 已完成状态的步骤：未开始

            if params:
                assert params.get('start_status_uuid') == complete
                assert params.get('end_status_uuid') == not_start

    @story('123128 设置初始状态')
    def test_set_init_state(self):
        """设置初始状态"""


