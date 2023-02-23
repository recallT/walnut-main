"""
@Desc：全局配置-工作项类型-工作项权限
"""
from falcons.check import go
from falcons.com.nick import feature, story, fixture, step, parametrize

from main.actions.pro import PrjAction
from main.actions.task import team_stamp
from main.api import issue
from main.params import conf
from main.params.const import ACCOUNT
from main.params.issue import delete_issue
from . import IssueConfig


@fixture(scope='module')
def _storage():
    return {}


@fixture(scope='module', autouse=True)
def _init_data(_storage):
    # 创建全局工作项
    issue_name, issue_uuid = IssueConfig.global_issue_add()
    _storage |= {'issue_type_uuid': issue_uuid, 'issue_name': issue_name}

    sub_ise_name, sub_ise_uuid = IssueConfig.global_sub_issue_add()
    _storage |= {'sub_ise_type_uuid': sub_ise_uuid, 'sub_ise_name': sub_ise_name}

    # 新增单选成员属性
    field_uuid = IssueConfig.issue_field_add(8)
    _storage |= {'field_uuid': field_uuid}

    # 将新增属性添加到对应工作项
    IssueConfig.global_issue_add_field(field_uuid, issue_name)

    yield

    # 清除新增的工作项
    prm = delete_issue()[0]
    prm.uri_args({'issue_uuid': issue_uuid})
    go(issue.IssueDelete, prm)

    prm.uri_args({'issue_uuid': sub_ise_uuid})
    go(issue.IssueDelete, prm)


def issue_type(storage):
    return storage['issue_type_uuid']


@feature('全局配置-工作项权限')
class TestIssuePermission:

    @story('132891 编辑关注者权限')
    def test_edit_followers_perm(self, _storage):
        with step('点击添加项目成员、用户组A、部门A、项目负责人、成员A、示例单选成员、示例多选成员'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type(_storage), 'custom_member_fields',
                user_domain_param=_storage['field_uuid'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(issue_type(_storage), rule_uuid)

    @story('132930 编辑任务权限')
    def test_edit_task_perm(self, _storage):
        with step('添加成员'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type(_storage), 'custom_member_fields', 'update_tasks', _storage['field_uuid'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(issue_type(_storage), rule_uuid)

    @story('132943 查看任务权限')
    def test_check_task_perm(self, _storage):
        with step('添加成员'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type(_storage), 'custom_member_fields', 'view_tasks', _storage['field_uuid'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(issue_type(_storage), rule_uuid)

    @story('132956 成为负责人权限')
    def test_be_assigned_perm(self, _storage):
        with step('添加成员'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type(_storage), 'custom_member_fields', 'be_assigned', _storage['field_uuid'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(issue_type(_storage), rule_uuid)

    @story('132964 创建任务权限')
    def test_create_task_perm(self, _storage):
        with step('添加成员'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type(_storage), 'single_user', 'create_tasks', ACCOUNT.user.owner_uuid)

        with step('删除成员'):
            IssueConfig.issue_permission_del(issue_type(_storage), rule_uuid)

    @story('132972 导出任务列表权限')
    def test_export_task_list_perm(self, _storage):
        with step('添加成员'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type(_storage), 'single_user', 'export_tasks', ACCOUNT.user.owner_uuid)

        with step('删除成员'):
            IssueConfig.issue_permission_del(issue_type(_storage), rule_uuid)

    @story('132980 更新任务状态权限')
    def test_update_task_status_perm(self, _storage):
        with step('添加成员'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type(_storage), 'single_user', 'transit_tasks', ACCOUNT.user.owner_uuid)

        with step('删除成员'):
            IssueConfig.issue_permission_del(issue_type(_storage), rule_uuid)

    @story('132993 管理所有登记工时权限')
    def test_manage_task_record_manhours_perm(self, _storage):
        with step('添加成员'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type(_storage), 'custom_member_fields', 'manage_task_record_manhours',
                _storage['field_uuid'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(issue_type(_storage), rule_uuid)

    @story('133006 管理所有预估工时权限')
    @story('133009 任务-工作项权限：管理所有预估工时权限（成员）')
    def test_manage_task_all_assess_manhour_perm(self, _storage):
        with step('添加成员'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type(_storage), 'custom_member_fields', 'manage_task_assess_manhour',
                _storage['field_uuid'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(issue_type(_storage), rule_uuid)

    @story('133019 管理预估工时权限')  # 老用例，无此功能
    def test_manage_task_assess_manhour_perm(self):
        """"""

    @story('133033 管理自己的登记工时权限')
    def test_manage_task_own_record_manhours_perm(self, _storage):
        with step('添加成员'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type(_storage), 'custom_member_fields', 'manage_task_own_record_manhours',
                _storage['field_uuid'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(issue_type(_storage), rule_uuid)

    @story('133045 管理自己的预估工时权限')  # 老用例，无此功能
    def test_manage_task_own_assess_manhour_perm(self):
        """"""

    @story('132917/132904 编辑截止日期权限/编辑计划开始日期、计划完成日期权限')
    @parametrize('field', ['field013', 'field027-field028'])
    def test_edit_expiration_date(self, field, _storage):
        with step('添加成员'):
            param = conf.constraints(_storage['field_uuid'], field)[0]
            param.json_update('constraints[0].user_domain_type', 'custom_member_fields')
            param.uri_args({'issue_uuid': issue_type(_storage)})

            resp = go(issue.ConstraintsAdd, param)

            c_uuid = [c['uuid'] for c in resp.value('default_configs.default_constraints') if
                      c['field_uuid'] == field and c['user_domain_param'] == _storage['field_uuid']]

        with step('删除成员'):
            param = conf.constraints_del()[0]
            param.json_update('constraint_uuids', c_uuid)
            param.uri_args({'issue_uuid': issue_type(_storage)})
            go(issue.ConstraintsDelete, param)

    @story('133064 删除任务权限')
    def test_del_task_perm(self, _storage):
        with step('添加成员'):
            rule_uuid = IssueConfig.issue_permission_add(
                issue_type(_storage), 'custom_member_fields', 'update_tasks', _storage['field_uuid'])

        with step('删除成员'):
            IssueConfig.issue_permission_del(issue_type(_storage), rule_uuid)

    @story('133059/133062 任务-工作项权限：任务权限列表（汇总模式下）/简单模式下')
    @parametrize('configs', ['detailed', 'simple'])
    def test_check_different_mode_task_issue_perm(self, configs):
        """查看不同模式下任务-工作项权限"""

        with step('切换成汇总/简单模式'):
            PrjAction.work_hour_configs_update(configs)

        with step('工作项权限配置查看权限列表，默认按照一下顺序暂时'):
            stamp_resp = team_stamp({"issue_type": 0})
            default_perm = [p['permission'] for c in stamp_resp['issue_type']['issue_types'] if c['name'] == '任务'
                            for p in c['default_configs']['default_permission']]

            d_perm = []
            [d_perm.append(i) for i in default_perm if i not in d_perm]  # 去重

            assert d_permission == d_perm

    @story('142244/142245 子任务-工作项权限：子任务权限列表（汇总模式下）/简单模式下')
    @parametrize('configs', ['detailed', 'simple'])
    def test_check_different_mode_sub_task_issue_perm(self, configs):
        """查看不同模式下子任务-工作项权限"""

        with step('切换成汇总/简单模式'):
            PrjAction.work_hour_configs_update(configs)

        with step('工作项权限配置查看权限列表，默认按照一下顺序暂时'):
            stamp_resp = team_stamp({"issue_type": 0})
            default_perm = [p['permission'] for c in stamp_resp['issue_type']['issue_types'] if c['name'] == '子任务'
                            for p in c['default_configs']['default_permission']]

            d_perm = []
            [d_perm.append(i) for i in default_perm if i not in d_perm]  # 去重

            assert d_permission == d_perm

    @story('141625/141627 自定义标准工作项-工作项权限：自定义标准工作项权限列表（汇总模式下）/简单模式下')
    @parametrize('configs', ['detailed', 'simple'])
    def test_check_custom_mode_issue_perm(self, configs, _storage):
        """查看自定义不同模式下标准工作项-工作项权限"""
        type_name = _storage['issue_name']

        with step('切换成汇总/简单模式'):
            PrjAction.work_hour_configs_update(configs)

        with step('工作项权限配置查看权限列表，默认按照一下顺序暂时'):
            stamp_resp = team_stamp({"issue_type": 0})
            default_perm = [p['permission'] for c in stamp_resp['issue_type']['issue_types'] if c['name'] == type_name
                            for p in c['default_configs']['default_permission']]

            d_perm = []
            [d_perm.append(i) for i in default_perm if i not in d_perm]

            assert d_permission == d_perm

    @story('141662/141663 自定义标准子工作项-工作项权限：自定义标准子工作项权限列表（汇总模式下）/简单模式下')
    @parametrize('configs', ['detailed', 'simple'])
    def test_check_custom_mode_sub_task_issue_perm(self, configs, _storage):
        """查看自定义不同模式下子工作项-工作项权限"""
        type_name = _storage['sub_ise_name']

        with step('切换成汇总/简单模式'):
            PrjAction.work_hour_configs_update(configs)

        with step('工作项权限配置查看权限列表，默认按照一下顺序暂时'):
            stamp_resp = team_stamp({"issue_type": 0})
            default_perm = [p['permission'] for c in stamp_resp['issue_type']['issue_types'] if c['name'] == type_name
                            for p in c['default_configs']['default_permission']]

            d_perm = []
            [d_perm.append(i) for i in default_perm if i not in d_perm]

            assert d_permission == d_perm


d_permission = ['create_tasks', 'view_tasks', 'update_tasks', 'delete_tasks', 'transit_tasks', 'be_assigned',
                'export_tasks', 'update_task_watchers', 'manage_task_assess_manhour',
                'manage_task_record_manhours', 'manage_task_own_record_manhours',
                'manage_task_own_assess_manhour']
