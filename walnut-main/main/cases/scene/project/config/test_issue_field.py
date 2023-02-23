"""
@Desc：项目设置-工作项类型-工作项属性
"""
from falcons.check import Checker, go
from falcons.com.nick import feature, story, step, parametrize, fixture
from main.actions.task import TaskAction, proj_team_stamp
from main.api import project as prj
from main.api.const import field
from main.api.task import LiteContextPermissionRules
from main.params import conf, data, task
from main.params.const import ACCOUNT


@fixture(scope='module')
def _uuid_storage():
    """缓存属性uuid"""

    return []


@fixture(scope='module', autouse=True)
def clear_field(_uuid_storage):
    yield
    param = data.field_delete()[0]

    if _uuid_storage:
        for f in _uuid_storage:
            param.uri_args({'field_uuid': f})

            # 删除全局工作项属性
            go(prj.FieldDelete, param)


@feature('工作项类型-工作项属性')
class TestProjIssueField(Checker):

    @story('123419 系统属性：需求-设置默认值（负责人）')
    @story('123420 系统属性：子需求-设置默认值（负责人）')
    @parametrize('types', ('需求', '子需求'))
    def test_principal_default_value(self, types):
        with step('属性默认值选择：成员A'):
            issue_type_uuid = TaskAction.issue_type_uuid(types)[0]

            param = conf.proj_field_update()[0]
            param.json_update('field_config.default_value', ACCOUNT.user.owner_uuid)
            param.uri_args({"issue_uuid": issue_type_uuid})
            param.uri_args({"field_uuid": 'field004'})
            resp = self.call(prj.ProjectIssueFieldUpdate, param)

            resp.check_response('field_config.default_value', ACCOUNT.user.owner_uuid)

        with step('清除默认值'):
            param.json_update('field_config.default_value', None)
            self.call(prj.ProjectIssueFieldUpdate, param)

    @story('123620 需求-开启必填')
    @story('123638 子需求-开启必填')
    @parametrize('types', ('需求', '子需求'))
    def test_field_enable_require(self, types):
        issue_type_uuid = TaskAction.issue_type_uuid(types)[0]

        param = conf.proj_field_update()[0]
        param.json_update('field_config', {"required": True})
        param.uri_args({"issue_uuid": issue_type_uuid})
        param.uri_args({"field_uuid": 'field011'})  # field011 所属迭代
        resp = self.call(prj.ProjectIssueFieldUpdate, param)

        resp.check_response('field_config.required', True)

    @story('123606 需求-关闭必填')
    @story('123617 子需求-关闭必填')
    @parametrize('types', ('需求', '子需求'))
    def test_field_close_require(self, types):
        issue_type_uuid = TaskAction.issue_type_uuid(types)[0]

        param = conf.proj_field_update()[0]
        param.json_update('field_config', {"required": False})
        param.uri_args({"issue_uuid": issue_type_uuid})
        param.uri_args({"field_uuid": 'field011'})  # field011 所属迭代
        resp = self.call(prj.ProjectIssueFieldUpdate, param)

        resp.check_response('field_config.required', False)

    @story('123618 存在单选菜单类型的自定义工作项属性')
    def test_proj_issue_add_field(self, _uuid_storage):
        #
        param = conf.add_issue_type_field()[0]
        param.json_update('field.type', 1)
        param.json['field'] |= {'options': [
            {
                "value": "test_1",
                "background_color": "#307fe2",
                "color": "#fff"
            },
            {
                "value": "test_2",
                "background_color": "#00b388",
                "color": "#fff"
            }]}

        res = self.call(prj.FieldsAdd, param)

        field_uuid = res.value('field.uuid')
        _uuid_storage.append(field_uuid)

    @story('123829 需求-添加自定义工作项属性（设置必填）')
    @story('123830 子需求-添加自定义工作项属性（设置必填）')
    @parametrize('types', ('需求', '子需求'))
    def test_customize_field_enable_require(self, types, _uuid_storage):
        with step('工作项属性名称选择：a，开启必填'):
            prm = {"field_uuid": _uuid_storage[0], "required": True}
            TaskAction.task_add_field(prm, types)

    @story('123722 任务-属性列表检查')
    @story('123726 子任务-属性列表检查')
    @parametrize('types', ('任务', '子任务'))
    def test_check_issue_field_list(self, types):
        issue_type_uuid = TaskAction.issue_type_uuid(types)[0]

        no_set_default_names = ['关注者', '创建者', '优先级', '剩余工时', '工时进度']

        with step('查看不支持设置属性默认值的属性类型'):
            # 获取项目工作项属性all不支持设置默认属性值
            stamp_resp = proj_team_stamp({"field_config": 0})
            no_set_default = [required['field_uuid'] for required in stamp_resp['field_config']['field_configs'] if
                              required['can_modify_required'] == False and
                              required['issue_type_uuid'] == issue_type_uuid]

            for name in no_set_default_names:
                key = field.name_to_key(name)
                assert key in no_set_default

    @story('123699 需求-删除工作项属性')
    @story('123695 子需求-删除工作项属性')
    @parametrize('types', ('需求', '子需求'))
    def test_del_issue_field(self, types, _uuid_storage):
        with step('选择已添加的属性删除'):
            issue_type_uuid = TaskAction.issue_type_uuid(types)[0]

            param = data.field_delete()[0]
            param.uri_args({'field_uuid': _uuid_storage[0]})
            param.uri_args({'issue_uuid': issue_type_uuid})

            # 删除项目工作项属性
            self.call(prj.ProjectIssueFieldDelete, param)


@feature('工作项类型-工作项权限')
class TestProjIssuePermission(Checker):

    @classmethod
    def get_pro_permission_rules(cls, issue_name, token=None):
        issue_type_uuid = TaskAction.issue_type_uuid(issue_name)[0]
        param = task.lite_context_permission_rules()[0]
        param.json_update('context_type', 'issue_type')
        param.json_update('context_param.issue_type_uuid', issue_type_uuid)
        resp = go(LiteContextPermissionRules, param, token)
        return resp

    @classmethod
    def get_permission_list(cls, resp, permission):
        user_domain_type_list = [r['user_domain_type'] for r in resp.value('permission_rules') if
                                 r['permission'] == permission]
        return user_domain_type_list

    @story('T152171 工作项权限：检查项目下工作项权限的默认权限域（任务）')
    def test_issue_default_permission_task(self):
        # 获取项目权限规则
        default_role = {'project_administrators', 'role'}
        resp = self.get_pro_permission_rules('任务')

        with step('查看任务成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'view_tasks')
            assert default_role <= set(user_domain_type_list)

        with step('查看创建任务成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'create_tasks')
            assert default_role <= set(user_domain_type_list)

        with step('查看更新任务成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'update_tasks')

            assert default_role <= set(user_domain_type_list)

        with step('查看删除任务成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'delete_tasks')
            assert default_role <= set(user_domain_type_list)

        with step('查看编辑关注者成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'update_task_watchers')

            assert 'everyone' in user_domain_type_list

        with step('查看管理预估工时成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'manage_task_assess_manhour')

            assert default_role <= set(user_domain_type_list)

        with step('export_tasks'):
            user_domain_type_list = self.get_permission_list(resp, 'export_tasks')
            assert 'everyone' in user_domain_type_list

    @story('T152168 工作项权限：检查项目下工作项权限的默认权限域（需求）')
    def test_issue_default_permission_demand(self):
        # 获取项目权限规则
        resp = self.get_pro_permission_rules('需求')
        default_role = {'project_administrators', 'role'}
        with step('查看查看需求成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'view_tasks')
            assert default_role <= set(user_domain_type_list)

        with step('查看创建需求成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'create_tasks')

            assert default_role <= set(user_domain_type_list)

        with step('查看更新需求状态成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'update_tasks')

            assert default_role <= set(user_domain_type_list)

        with step('查看删除需求成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'delete_tasks')
            assert default_role <= set(user_domain_type_list)

        with step('查看管理自己的登记工时成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'manage_task_own_record_manhours')
            assert default_role <= set(user_domain_type_list)

        with step('查看管理所有登记工时成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'manage_task_record_manhours')
            assert 'project_administrators' in user_domain_type_list
        with step('export_tasks'):
            user_domain_type_list = self.get_permission_list(resp, 'export_tasks')
            assert 'everyone' in user_domain_type_list

    @story('T152172 工作项权限：检查项目下工作项权限的默认权限域（子任务）')
    def test_issue_default_permission_sub_task(self):
        # 获取项目权限规则
        resp = self.get_pro_permission_rules('子任务')
        default_role = {'project_administrators', 'role'}
        with step('查看子任务成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'view_tasks')
            assert default_role <= set(user_domain_type_list)

        with step('查看创建子任务成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'create_tasks')

            assert default_role <= set(user_domain_type_list)

        with step('查看更新子任务成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'update_tasks')

            assert default_role <= set(user_domain_type_list)

        with step('查看删除子任务成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'delete_tasks')

            assert default_role <= set(user_domain_type_list)

        with step('成为负责人'):
            user_domain_type_list = self.get_permission_list(resp, 'be_assigned')
            assert 'role' in user_domain_type_list

        with step('编辑关注者'):
            user_domain_type_list = self.get_permission_list(resp, 'update_task_watchers')
            assert 'everyone' in user_domain_type_list
        with step('子任务export_tasks'):
            user_domain_type_list = self.get_permission_list(resp, 'export_tasks')
            assert 'everyone' in user_domain_type_list

    @story('T152170 工作项权限：检查项目下工作项权限的默认权限域（子需求）')
    def test_issue_default_permission_sub_demand(self):
        # 获取项目权限规则
        default_role = {'project_administrators', 'role'}
        resp = self.get_pro_permission_rules('子需求')
        with step('查看子需求成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'view_tasks')

            assert default_role <= set(user_domain_type_list)

        with step('查看创建子需求成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'create_tasks')

            assert default_role <= set(user_domain_type_list)

        with step('查看更新子需求成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'update_tasks')

            assert default_role <= set(user_domain_type_list)

        with step('查看删除子需求成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'delete_tasks')

            assert default_role <= set(user_domain_type_list)

        with step('查看子需求编辑关注者成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'update_task_watchers')

            assert 'everyone' in user_domain_type_list

        with step('查看子需求管理预估工时成员域'):
            user_domain_type_list = self.get_permission_list(resp, 'manage_task_assess_manhour')

            assert default_role <= set(user_domain_type_list)
        with step('子需求export_tasks'):
            user_domain_type_list = self.get_permission_list(resp, 'export_tasks')
            assert 'everyone' in user_domain_type_list

    @story('T144506 工作项权限-工作项权限：页面信息检查')
    def test_check_permission_rules(self):
        """
        2.infobar文案下方按顺序展示以下权限点：
          创建工作项
          查看工作项
          编辑工作项
          删除工作项
          更新状态
          编辑关注者
          成为负责人
          导出工作项列表
          管理自己的登记工时
          管理所有登记工时
          管理自己的预估工时
          管理所有预估工时
        """
        permission_rules_list = ['export_tasks', 'manage_task_own_assess_manhour', 'manage_task_own_record_manhours',
                                 'manage_task_record_manhours', 'delete_tasks', 'manage_task_assess_manhour',
                                 'update_task_watchers', 'transit_tasks', 'update_tasks',
                                 'create_tasks']
        resp = self.get_pro_permission_rules('任务')
        resp_permission = [r['permission'] for r in resp.value('permission_rules')]
        # assert set(permission_rules_list) <= set(resp_permission)
