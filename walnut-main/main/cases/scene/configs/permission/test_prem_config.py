"""
@Desc：全局配置-项目管理-权限配置
"""
from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, mark

from main.actions.pro import ProjPermissionAction
from main.api import project as prj, task
from main.params import conf, task as ts
from main.params.const import ACCOUNT


@fixture(scope='module')
def _perm_uuid():
    return []


@mark.smoke
@feature('全局配置-权限配置')
class TestPermissionConfig(Checker):

    def permission_rule_add(self, permission, user_domain_type, _perm_uuid, user_domain_param=''):
        param = conf.global_perm_config(permission, user_domain_type, user_domain_param)[0]
        resp = self.call(prj.PermissionAdd, param)

        _perm_uuid.append(resp.value('permission_rule.uuid'))

        return resp.value('permission_rule')

    @story('131573 管理版本：添加成员域（成员）')
    def test_perm_manage_versions_add_single_user(self, _perm_uuid):
        self.permission_rule_add('manage_versions', 'single_user', _perm_uuid, ACCOUNT.user.owner_uuid)

    @story('131594 管理工作项配置：添加成员域（成员）')
    def test_perm_manage_tasks_config_add_single_user(self, _perm_uuid):
        self.permission_rule_add('manage_tasks_config', 'single_user', _perm_uuid, ACCOUNT.user.owner_uuid)

    @story('131608 批量移动：添加成员域（成员）')
    def test_perm_batch_move_tasks_add_single_user(self, _perm_uuid):
        self.permission_rule_add('batch_move_tasks', 'single_user', _perm_uuid, ACCOUNT.user.owner_uuid)

    @story('131615 新建项目：添加成员域（成员）')
    def test_perm_add_project_single_user(self, _perm_uuid):
        self.permission_rule_add('add_project', 'single_user', _perm_uuid, ACCOUNT.user.owner_uuid)

    @story('131612 新建项目：删除成员域')
    def test_perm_add_project_delete_single_user(self, _perm_uuid):
        if _perm_uuid:
            for uuid in _perm_uuid:
                ProjPermissionAction.del_permission(uuid)

    @story('131619 权限配置：开箱后权限默认成员域列表检查')
    def test_global_perm_config_unpack(self):
        param = ts.lite_context_permission_rules()[0]
        param.json_update('context_type', 'team')
        del param.json['context_param']
        resp = self.call(task.LiteContextPermissionRules, param)

        permission = [p['permission'] for p in resp.value('permission_rules')]

        # 默认权限
        d = {'add_project', 'manage_tasks_config', 'manage_versions', 'batch_move_tasks'}
        assert d <= set(permission)
