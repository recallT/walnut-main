"""
@File    ：test_issue_role_config.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/3
@Desc    ：默认工作想类型权限配置
"""
from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, parametrize

from main.actions.task import TaskAction
from main.api import task as api
from main.params import task as p


@fixture(scope='module')
def issue_type():
    """工作项UUID"""
    j = TaskAction.task_stamp(flush=True)
    return j


def get_uuid(name, j):
    """"""
    configs = [m['issue_type_uuid'] for m in j['issue_type_config']['issue_type_configs'] if m['name'] == name]
    if not configs:
        raise RuntimeError(f'没查到 {name} 默认权限配置!')

    return configs[0]


@feature('开箱默认配置')
class TestIssuePermission(Checker):
    """"""

    @story('152176 工作项权限：检查项目下工作项权限的默认权限域（缺陷）')
    @parametrize('param', p.lite_context_permission_rules())
    def test_task_default_role_defense(self, param, issue_type):
        """"""

        self.check_default_conf(issue_type, param, '缺陷')

    @story('152171 工作项权限：检查项目下工作项权限的默认权限域（任务）')
    @parametrize('param', p.lite_context_permission_rules())
    def test_task_default_role_task(self, param, issue_type):
        """"""

        self.check_default_conf(issue_type, param, '任务')

    @story('152168 工作项权限：检查项目下工作项权限的默认权限域（需求）')
    @parametrize('param', p.lite_context_permission_rules())
    def test_task_default_role_demand(self, param, issue_type):
        """"""

        self.check_default_conf(issue_type, param, '需求')

    @story('152172 工作项权限：检查项目下工作项权限的默认权限域（子任务）')
    @parametrize('param', p.lite_context_permission_rules())
    def test_task_default_role_sub_task(self, param, issue_type):
        """"""
        self.check_default_conf(issue_type, param, '子任务')

    @story('152172 工作项权限：检查项目下工作项权限的默认权限域（子需求）')
    @parametrize('param', p.lite_context_permission_rules())
    def test_task_default_role_sub_demand(self, param, issue_type):
        """"""
        self.check_default_conf(issue_type, param, '子需求')

    def check_default_conf(self, issue_type, param, type_name):
        param.json['context_param']['issue_type_uuid'] = get_uuid(type_name, issue_type)
        self.call(api.LiteContextPermissionRules, param)
