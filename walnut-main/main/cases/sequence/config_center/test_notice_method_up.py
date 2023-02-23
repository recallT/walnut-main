"""
@File    ：test_notice_method_up
@Author  ：xiechunwei
@Date    ：2022/8/8 14:29
@Desc    ：配置中心-项目管理-工作项类型-工作项通知
"""

from falcons.check import Checker, go
from falcons.com.nick import story, step, mark, fixture
from main.actions.issue import IssueAction
from main.actions.task import TaskAction
from main.api import project
from main.api.issue import AddSubScription, DelSubScription, UpdateAllNoticeMethods
from main.params import issue, proj
from falcons.com.meta import ApiMeta

label = ApiMeta.env.label


@fixture(scope='module')
def issue_notice():
    task_issue_uuid = TaskAction.issue_type_uuid('任务')[0]
    sub_task_issue_uuid = TaskAction.issue_type_uuid('子任务')[0]

    yield {'task_uuid': task_issue_uuid, 'sub_task_uuid': sub_task_issue_uuid}

    param = issue.update_notice_center()[0]
    param.json_update('effect_notice_center', True)
    param.json_update('email', False)
    param.json_update('effect_wechat', True)

    # 关闭 任务 通知方式
    param.uri_args({'issue_type_uuid': task_issue_uuid})
    go(UpdateAllNoticeMethods, param)

    # 关闭 子任务 通知方式
    param.uri_args({'issue_type_uuid': sub_task_issue_uuid})
    go(UpdateAllNoticeMethods, param)


@mark.skipif(label == 'saas', reason='saas环境跳过工作项通知变更')
class TestNoticeMethodUp(Checker):

    @story('T128129 工作项通知：更改通知方式')
    def test_update_notice_type(self, issue_notice):
        with step('取消勾选：全选-通知中心'):
            param = issue.update_notice_center()[0]
            param.json_update('notice_center', True)
            param.json_update('effect_notice_center', True)
            param.uri_args({'issue_type_uuid': issue_notice['task_uuid']})
            resp = self.call(UpdateAllNoticeMethods, param)
            resp.check_response('code', 200)

        with step("勾选更改负责人通知方式：通知中心、邮件"):
            param.json_update('email', True)
            param.json_update('effect_email', True)
            resp = self.call(UpdateAllNoticeMethods, param)
            resp.check_response('code', 200)
        with step("勾选：全选-邮件"):
            param.json_update('wechat', True)
            param.json_update('effect_wechat', True)
            resp = self.call(UpdateAllNoticeMethods, param)
            resp.check_response('code', 200)

    @story('128127 工作项通知：更改通知方式--子任务')
    def test_sub_task_update_notice_type(self, issue_notice):
        with step('取消勾选：全选-通知中心'):
            param = issue.update_notice_center()[0]
            param.json_update('notice_center', True)
            param.json_update('effect_notice_center', True)
            param.uri_args({'issue_type_uuid': issue_notice['sub_task_uuid']})
            resp = self.call(UpdateAllNoticeMethods, param)
            resp.check_response('code', 200)

        with step("勾选更改负责人通知方式：通知中心、邮件"):
            param.json_update('email', True)
            param.json_update('effect_email', True)
            resp = self.call(UpdateAllNoticeMethods, param)
            resp.check_response('code', 200)
        with step("勾选：全选-邮件"):
            param.json_update('wechat', True)
            param.json_update('effect_wechat', True)
            resp = self.call(UpdateAllNoticeMethods, param)
            resp.check_response('code', 200)

    @story('T125587 工作项通知-创建任务：添加成员域')
    @story('T125589 工作项通知-创建任务：移除成员域')
    @story('144190 工作项通知-创建任务：移除成员域')
    def test_add_and_del_notice_config(self, issue_notice):
        with step('获取工作项通知配置'):
            resp_config = IssueAction.get_notice_config(issue_notice['task_uuid'])
            config_uuid = [r['uuid'] for r in resp_config.value('system_configs') if r['name'] == '创建任务'][0]
        with step('工作项通知-创建任务：添加成员域'):
            # 查询系统内存在的member 成员uuid
            su_param = proj.program_search_user()[0]
            resp_user_uuid = go(project.UsesSearch, su_param).value('users[0].uuid')

            param = issue.notice_config()[0]
            param.json_update('single_user_uuids', [resp_user_uuid])
            param.uri_args({'issue_type_uuid': issue_notice['task_uuid'], 'notice_config_uuid': config_uuid})
            resp_add = go(AddSubScription, param)
            resp_add.check_response('code', 200)
        with step('工作项通知-创建任务：移除成员域'):
            resp_del = go(DelSubScription, param)
            resp_del.check_response('code', 200)

    @story('T128205 工作项通知：通知事件的默认成员域及通知方式检查')
    def test_default_notice_config(self, issue_notice):
        with step('检查任务通知事件的默认成员域'):
            resp_config = IssueAction.get_notice_config(issue_notice['task_uuid'])
            config = [r for r in resp_config.value('system_configs') if r['name'] == '创建任务'][0]
            assert 'task_owner' in config['subscription']['roles']
            assert 'task_assign' in config['subscription']['roles']

    @story('T125647 工作项通知-创建子任务：添加成员域')
    @story('144208 工作项通知-创建任务：添加成员域')
    @story('T125648 工作项通知-创建子任务：移除成员域')
    def test_add_and_del_sub_task_notice_config(self, issue_notice):
        with step('获取工作项通知配置'):
            resp_config = IssueAction.get_notice_config(issue_notice['sub_task_uuid'])
            config_uuid = [r['uuid'] for r in resp_config.value('system_configs') if r['name'] == '创建任务'][0]
        with step('工作项通知-创建任务：添加成员域'):
            # 查询系统内存在的member 成员uuid
            su_param = proj.program_search_user()[0]
            resp_user_uuid = go(project.UsesSearch, su_param).value('users[0].uuid')

            param = issue.notice_config()[0]
            param.json_update('single_user_uuids', [resp_user_uuid])
            param.uri_args({'issue_type_uuid': issue_notice['sub_task_uuid'], 'notice_config_uuid': config_uuid})
            resp_add = go(AddSubScription, param)
            resp_add.check_response('code', 200)
        with step('工作项通知-创建任务：移除成员域'):
            resp_del = go(DelSubScription, param)
            resp_del.check_response('code', 200)
