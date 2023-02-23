import time

from falcons.check import Checker, go
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, fixture, story, step, mark
from main.actions.issue import IssueAction as iis
from main.actions.member import MemberAction
from main.actions.task import TaskAction
from main.actions.task import TaskAction as ta
from main.api import third, project, issue
from main.helper.extra import Extra
from main.params import data, conf, proj
from main.params.third import add_sub_department


@fixture(scope='module', autouse=True)
def permission_data1():
    # 创建一个单独项目
    time.sleep(2)
    creator = Extra(ApiMeta)
    p_id = creator.new_project(f'项目工作项权限test1')
    issue_type_uuid = TaskAction.issue_type_uuid('子任务', project_uuid=p_id)[0]
    # 获取系统中存在的一个成员uuid
    member_uuid = MemberAction.get_member_uuid()
    data = {'p_id': p_id, 'member_uuid': member_uuid, 'issue_type_uuid': issue_type_uuid}
    return data


@fixture()
def get_pro_permission(permission_data1):
    """每次都用重新查询一次权限数据"""
    resp = iis.get_pro_permission_rules('子任务', project_uuid=permission_data1['p_id'])
    return resp


@fixture(scope='module', autouse=True)
def _del_project(permission_data1):
    yield
    # 清除项目数据
    creator = Extra(ApiMeta)
    creator.del_project(permission_data1['p_id'])


label = ApiMeta.env.label


@mark.skipif(label == 'private' or label == 'dev', reason='环境跳过权限用例')
@feature('工作项权限-子任务')
class TestProjSubTaskPermission(Checker):
    @classmethod
    def get_issue_permission_uuid(cls, resp, permission_type):
        uuid_list = [r['uuid'] for r in resp.value('permission_rules') if
                     r['permission'] == permission_type]
        return uuid_list

    @story('T142064 子任务-工作项权限：编辑关注者权限（成员）')
    def test_issue_permission_update_task_watchers(self, get_pro_permission, permission_data1):
        permission = 'update_task_watchers'
        with step('项目管理员清空子任务的「编辑关注者」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A的关注者'):
            ...
            # todo:
        with step('项目管理员添加子任务的「编辑关注者」权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data1['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('T142103 子任务-工作项权限：编辑子任务权限（成员）')
    def test_issue_permission_update_tasks(self, get_pro_permission, permission_data1):
        permission = 'update_tasks'
        with step('项目管理员清空子任务的「编辑子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A的属性'):
            ...
            # todo:
        with step('项目管理员将子任务的「编辑子任务」权限域添加成员A'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data1['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('T142116 子任务-工作项权限：查看子任务权限（成员）')
    def test_issue_permission_view_tasks(self, get_pro_permission, permission_data1):
        permission = 'view_tasks'
        with step('项目管理员清空子任务的「查看子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A查看子任务A'):
            ...
            # todo:
        with step('项目管理员将子任务的「查看子任务」权限域添加成员A'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data1['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('T142129 子任务-工作项权限：成为负责人权限（成员）')
    def test_issue_permission_be_assigned(self, get_pro_permission, permission_data1):
        permission = 'be_assigned'
        with step('项目管理员清空子任务的「成为负责人」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A创建子任务的工作项'):
            ...
            # todo:
        with step('项目管理员添加子任务的「成为负责人」权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data1['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story("T142130 子任务-工作项权限：成为负责人权限（项目负责人）")
    def test_issue_permission_be_assigned_project_assign(self, get_pro_permission, permission_data1):
        permission = 'be_assigned'
        with step('项目管理员清空子任务的「成为负责人」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A创建子任务的工作项'):
            ...
            # todo:
        with step('项目管理员添加子任务的「成为负责人」权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': "",
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('T142137 子任务-工作项权限：创建子任务权限（成员）')
    def test_issue_permission_create_tasks(self, get_pro_permission, permission_data1):
        permission = 'create_tasks'
        with step('项目管理员清空子任务的「创建子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A创建子任务的工作项'):
            ...
            # todo:
        with step('项目管理员将子任务的「创建子任务」权限域添加为成员A'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data1['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('T142145 子任务-工作项权限：导出子任务列表权限（成员）')
    def test_issue_permission_export_tasks(self, get_pro_permission, permission_data1):
        permission = 'export_tasks'
        with step('项目管理员清空子任务的「导出子任务」列表权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A导出子任务下的工作项'):
            ...
            # todo:
        with step('项目管理员清空子任务的「导出子任务」列表权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data1['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story("T142146 子任务-工作项权限：导出子任务列表权限（项目负责人）")
    def test_issue_permission_export_tasks_project_assign(self, get_pro_permission, permission_data1):
        permission = 'export_tasks'
        with step('项目管理员清空子任务的「导出子任务」列表权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A导出子任务下的工作项'):
            ...
            # todo:
        with step('项目管理员清空子任务的「导出子任务」列表权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': "",
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('T142153 子任务-工作项权限：更新子任务状态权限（成员）')
    def test_issue_permission_transit_tasks_member(self, get_pro_permission, permission_data1):
        permission = 'transit_tasks'
        with step('项目管理员清空子任务的「更新子任务状态」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A更新子任务A的状态'):
            ...
            # todo:
        with step('项目管理员将子任务的「更新子任务状态」权限域添加成员A'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data1['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('T142154 子任务-工作项权限：更新子任务状态权限（工作项创建者）')
    def test_issue_permission_transit_task_assign(self, get_pro_permission, permission_data1):
        permission = 'transit_tasks'
        with step('项目管理员清空子任务的「更新子任务状态」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A更新子任务A的状态'):
            ...
            # todo:
        with step('项目管理员将子任务的「更新子任务状态」权限域添加工作项负责人'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_assign'}  # 工作项创建者
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('T142155 子任务-工作项权限：更新子任务状态权限（工作项负责人）')
    def test_issue_permission_transit_tasks_owner(self, get_pro_permission, permission_data1):
        permission = 'transit_tasks'
        with step('项目管理员清空子任务的「更新子任务状态」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A更新子任务A的状态'):
            ...
            # todo:
        with step('项目管理员将子任务的「更新子任务状态」权限域添加工作项创建者'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_owner'}  # 工作项负责人
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('T142157 子任务-工作项权限：更新子任务状态权限（项目负责人）')
    @story('142156 子任务-工作项权限：更新子任务状态权限（工作项关注者）')
    def test_issue_permission_transit_task_project_assign(self, get_pro_permission, permission_data1):
        permission = 'transit_tasks'
        with step('项目管理员清空子任务的「更新子任务状态」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A更新子任务A的状态'):
            ...
            # todo:
        with step('项目管理员将子任务的「更新子任务状态」权限域添加工作项关注者'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'project_assign'}  # 项目负责人
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('142158 子任务-工作项权限：更新子任务状态权限（项目角色）')
    def test_issue_permission_transit_task_role(self, get_pro_permission, permission_data1):
        permission = 'transit_tasks'
        # 新增角色
        role_uuid = MemberAction.add_member_role().value('role.uuid')
        with step('项目管理员清空子任务的「更新子任务状态」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A更新子任务A的状态'):
            ...
            # todo:
        with step('项目管理员将子任务的「更新子任务状态」权限域添加项目成员'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': role_uuid,
                          'user_domain_type': 'role'}  # 项目角色
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])
        with step('删除角色'):
            MemberAction.del_member_role(role_uuid)

    @story('T142152 子任务-工作项权限：更新子任务状态权限（部门）')
    def test_issue_permission_transit_tasks_department(self, get_pro_permission, permission_data1):
        permission = 'transit_tasks'
        with step('项目管理员清空子任务的「更新子任务状态」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A更新子任务A的状态'):
            ...
            # todo:
        with step('项目管理员将子任务的「更新子任务状态」权限域添加部门1'):
            # 新增部门
            param = add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)
            depart_uuid = resp.json()['add_department']['uuid']
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': depart_uuid,
                          'user_domain_type': 'department'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])
        with step('清除部门数据'):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story('T142159 子任务-工作项权限：更新子任务状态权限（用户组）')
    def test_issue_permission_transit_tasks_group(self, get_pro_permission, permission_data1):
        # 新增用户组
        param = data.user_group_add()[0]
        resp = self.call(project.UsesGroupAdd, param)
        group_uuid = resp.value('uuid')
        permission = 'transit_tasks'
        with step('项目管理员清空子任务的「更新子任务状态」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A更新子任务A的状态'):
            ...
            # todo:
        with step('项目管理员将子任务的「更新子任务状态」权限域添加用户组1'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': group_uuid,
                          'user_domain_type': 'group'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])
        with step('清除用户组数据'):
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param, with_json=False)

    @story('T142166 子任务-工作项权限：管理所有登记工时权限（成员）')
    def test_issue_permission_manage_task_record_manhours(self, get_pro_permission, permission_data1):
        permission = 'manage_task_record_manhours'
        with step('项目管理员清空子任务的「管理所有登记工时」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A下成员L的登记工时记录'):
            ...
            # todo:
        with step('项目管理员添加子任务的「管理所有登记工时」权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data1['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('T142170子任务-工作项权限：管理所有登记工时权限（项目负责人）')
    def test_issue_permission_manage_task_record_manhours_project_assign(self, get_pro_permission, permission_data1):
        permission = 'manage_task_record_manhours'
        with step('项目管理员清空子任务的「管理所有登记工时」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A下成员L的登记工时记录'):
            ...
            # todo:
        with step('项目管理员添加子任务的「管理所有登记工时」权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': "",
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('T142179 子任务-工作项权限：管理预估工时权限（成员）')
    @story('142192 子任务-工作项权限：管理预估工时权限（成员）')
    def test_issue_permission_manage_task_assess_manhour(self, get_pro_permission, permission_data1):
        permission = 'manage_task_assess_manhour'
        with step('项目管理员清空子任务的「管理预估工时」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A下成员L的预估工时记录'):
            ...
            # todo:
        with step('项目管理员添加子任务的「管理预估工时」权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data1['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('T142206 子任务-工作项权限：管理自己登记工时权限（成员）')
    def test_issue_permission_manage_task_assess_manhour(self, get_pro_permission, permission_data1):
        permission = 'manage_task_own_record_manhours'
        with step('项目管理员清空子任务的「管理自己登记工时」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A下A的登记工时记录'):
            ...
            # todo:
        with step('项目管理员添加子任务的「管理自己登记工时」权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data1['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('T142210 子任务-工作项权限：管理自己登记工时权限（项目负责人）')
    @story('T142223 子任务-工作项权限：管理自己预估工时权限（项目负责人）')
    def test_issue_permission_manage_task_assess_manhour_project_assign(self, get_pro_permission, permission_data1):
        permission = 'manage_task_own_record_manhours'
        with step('项目管理员清空子任务的「管理自己登记工时」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A下A的登记工时记录'):
            ...
            # todo:
        with step('项目管理员添加子任务的「管理自己登记工时」权限域为成员A'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': "",
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('T142232 子任务-工作项权限：删除子任务权限（成员）')
    def test_issue_permission_delete_tasks(self, get_pro_permission, permission_data1):
        permission = 'delete_tasks'
        with step('项目管理员清空子任务的「删除子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A删除子任务下的子任务A'):
            ...
            # todo:
        with step('项目管理员将子任务的「删除子任务」权限添加成员A'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': permission_data1['member_uuid'],
                          'user_domain_type': 'single_user'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story('T142077子任务-工作项权限：编辑计划开始日期、计划完成日期权限（成员）')
    def test_issue_permission_update_task_field_field027(self, permission_data1):
        issue_type_scope_uuid = ta.issue_type_uuid('子任务', uuid_type='uuid'
                                                   , project_uuid=permission_data1['p_id'])[0]
        param_g = proj.get_task_permission_list(issue_type_scope_uuid)[0]
        resp = self.call(project.ItemGraphql, param_g)
        constraint_uuids = [r['issueTypeScopeFieldConstraints'][0]['uuid'] for r in resp.value('data.buckets') if
                            r['fieldUUID'] == 'field027-field028']
        with step('项目管理员清空任务的「编辑计划开始日期、计划完成日期」权限域 '):
            if len(constraint_uuids) != 0:
                param = conf.proj_constraints_del(constraint_uuids)[0]
                param.uri_args(
                    {'issue_type_uuid': permission_data1['issue_type_uuid'], 'project_uuid': permission_data1['p_id']})
                resp_del = self.call(issue.ProjConstraintsDelete, param)
                resp_del.check_response('code', 200)
        with step('成员A点击编辑任务A的计划开始日期、计划完成日期属性'):
            ...
            # todo
        with step('项目管理员将任务的「编辑计划开始日期、计划完成日期」权限域添加成员A'):
            param = proj.add_task_permission(issue_type_scope_uuid, 'field027-field028')[0]
            param.json_update('items[0].user_domain_param', permission_data1['member_uuid'])
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

    @story('T142090 子任务-工作项权限：编辑截止日期权限（成员）')
    @story('132920 【x】任务-工作项权限：编辑截止日期权限（成员）')
    def test_issue_permission_update_task_field_field013(self, permission_data1):
        issue_type_scope_uuid = ta.issue_type_uuid('子任务', uuid_type='uuid'
                                                   , project_uuid=permission_data1['p_id'])[0]
        param_g = proj.get_task_permission_list(issue_type_scope_uuid)[0]
        resp = self.call(project.ItemGraphql, param_g)
        constraint_uuids = [r['issueTypeScopeFieldConstraints'][0]['uuid'] for r in resp.value('data.buckets') if
                            r['fieldUUID'] == 'field013']
        with step('项目管理员清空子任务的「编辑截止日期」权限域'):
            if len(constraint_uuids) != 0:
                param = conf.proj_constraints_del(constraint_uuids)[0]
                param.uri_args(
                    {'issue_type_uuid': permission_data1['issue_type_uuid'], 'project_uuid': permission_data1['p_id']})
                resp_del = self.call(issue.ProjConstraintsDelete, param)
                resp_del.check_response('code', 200)
        with step('成员A编辑子任务A的截止日期属性'):
            ...
            # todo
        with step('项目管理员添加子任务的「编辑截止日期」权限域为成员A'):
            param = proj.add_task_permission(issue_type_scope_uuid, 'field013')[0]
            param.json_update('items[0].user_domain_param', permission_data1['member_uuid'])
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

    @story("T142065 子任务-工作项权限：编辑关注者权限（工作项创建者）")
    def test_issue_permission_edit_task_item_creator(self, get_pro_permission, permission_data1):
        permission = 'update_task_watchers'
        with step('项目管理员清空子任务的「编辑关注者」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将子任务的「编辑关注者」权限域添加工作项创建者'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_owner'}  # 工作项创建者
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story("T142066 子任务-工作项权限：编辑关注者权限（工作项负责人）")
    def test_issue_permission_edit_task_item_assign(self, get_pro_permission, permission_data1):
        permission = 'update_task_watchers'
        with step('项目管理员清空子任务的「编辑关注者」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将子任务的「编辑关注者」权限域添加工作项负责人'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_assign'}  # 工作项负责人
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    @story("T142067 子任务-工作项权限：编辑关注者权限（工作项关注者）")
    def test_issue_permission_edit_task_item_foll(self, get_pro_permission, permission_data1):
        permission = 'update_task_watchers'
        with step('项目管理员清空子任务的「编辑关注者」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将子任务的「编辑关注者」权限域添加工作项关注者'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_watchers'}  # 工作项关注者
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])
        with step('项目管理员将子任务的「编辑关注者」权限域添加「项目负责人」'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'project_assign'}  # 项目负责人
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])

    # 2022/8/1
    @story("T142069 子任务-工作项权限：编辑关注者权限（项目角色）")
    @story("T142070 子任务-工作项权限：编辑关注者权限（用户组）")
    def test_issue_permission_edit_task_proj_role(self, get_pro_permission, permission_data1):
        permission = 'update_task_watchers'
        # 新增角色
        role_uuid = MemberAction.add_member_role().value('role.uuid')
        # 新增用户组
        param = data.user_group_add()[0]
        resp = self.call(project.UsesGroupAdd, param)
        group_uuid = resp.value('uuid')

        with step('项目管理员清空子任务的「编辑关注者」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑子任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将子任务的「编辑关注者」权限域添加「项目角色」'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': role_uuid,
                          'user_domain_type': 'role'}  # 项目角色
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])
        with step('项目管理员将子任务的「编辑关注者」权限域添加「用户组」'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': group_uuid,
                          'user_domain_type': 'group'}  # 用户组
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])
        with step('删除角色、用户组'):
            # 删除角色
            MemberAction.del_member_role(role_uuid)
            # 删除用户组
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param, with_json=False)

    @classmethod
    def del_update_task_field(cls, issue_type_uuid1, project_uuid, uuid):
        """对 任务工作项权限的 编辑计划开始日期、计划完成日期权限 的成员域进行清除操作"""
        issue_type_uuid = TaskAction.issue_type_uuid('子任务', uuid_type='uuid'
                                                     , project_uuid=project_uuid)[0]
        param_g = proj.get_task_permission_list(issue_type_uuid)[0]
        resp = go(project.ItemGraphql, param_g)

        constraint_uuids = [r['issueTypeScopeFieldConstraints'][0]['uuid'] for r in resp.value('data.buckets') if
                            r['fieldUUID'] == uuid]
        with step('项目管理员清空任务的「编辑计划开始日期、计划完成日期」权限域 '):
            if len(constraint_uuids) != 0:
                param = conf.proj_constraints_del(constraint_uuids)[0]
                param.uri_args(
                    {'issue_type_uuid': issue_type_uuid1, 'project_uuid': project_uuid})
                resp_del = go(issue.ProjConstraintsDelete, param)
                resp_del.check_response('code', 200)
        return issue_type_uuid

    @story("T142076 子任务-工作项权限：编辑计划开始日期、计划完成日期权限（部门）")
    @story("T142082 子任务-工作项权限：编辑计划开始日期、计划完成日期权限（项目角色）")
    @story("T142083 子任务-工作项权限：编辑计划开始日期、计划完成日期权限（用户组）")
    def test_sub_task_permission_update_task_field_field027_depart(self, get_pro_permission, permission_data1):
        issue_type_uuid1 = permission_data1['issue_type_uuid']
        project_uuid = permission_data1['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid, 'field027-field028')

        with step('成员A点击编辑任务A的计划开始日期、计划完成日期属性'):
            ...
            # todo
        with step('项目管理员将任务的「编辑计划开始日期、计划完成日期」权限域添加 「部门'):
            # 新增部门
            param1 = add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param1)
            depart_uuid = resp.json()['add_department']['uuid']

            param = proj.add_task_permission(issue_type_uuid, 'field027-field028')[0]
            param.json_update('items[0].user_domain_param', depart_uuid)
            param.json_update('items[0].user_domain_type', 'department')
            self.call(project.ItemBatchAdd, param)
        with step('项目管理员将任务的「编辑计划开始日期、计划完成日期」权限域添加 「项目角色」'):
            # 新增角色
            role_uuid = MemberAction.add_member_role().value('role.uuid')
            param.json_update('items[0].user_domain_param', role_uuid)
            param.json_update('items[0].user_domain_type', 'role')
            self.call(project.ItemBatchAdd, param)
        with step("权限域添加「用户组」 "):
            # 新增用户组
            param1 = data.user_group_add()[0]
            resp = self.call(project.UsesGroupAdd, param1)
            group_uuid = resp.value('uuid')
            param.json_update('items[0].user_domain_param', group_uuid)
            param.json_update('items[0].user_domain_type', 'group')
            self.call(project.ItemBatchAdd, param)
        print("")
        with step('清除部门、角色、用户组数据'):
            # 删除部门
            param1.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param1, with_json=False)
            # 删除项目角色
            MemberAction.del_member_role(role_uuid)
            # 删除用户组
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param, with_json=False)

    @story("T142078 子任务-工作项权限：编辑计划开始日期、计划完成日期权限（工作项创建者）")
    def test_sub_task_permission_update_task_field027_item_creator(self, get_pro_permission, permission_data1):
        issue_type_uuid1 = permission_data1['issue_type_uuid']
        project_uuid = permission_data1['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid, 'field027-field028')

        with step('成员A点击编辑子任务A的计划开始日期、计划完成日期属性'):
            ...
            # todo
        with step('项目管理员将子任务的「编辑计划开始日期、计划完成日期」权限域添加 「工作项创建者」'):
            param = proj.add_task_permission(issue_type_uuid, 'field027-field028')[0]
            param.json_update('items[0].user_domain_param', '')
            param.json_update('items[0].user_domain_type', 'task_owner')
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

    @story("T142079 子任务-工作项权限：编辑计划开始日期、计划完成日期权限（工作项负责人）")
    def test_sub_task_permission_update_task_field027_item_assign(self, get_pro_permission, permission_data1):
        issue_type_uuid1 = permission_data1['issue_type_uuid']
        project_uuid = permission_data1['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid, 'field027-field028')

        with step('成员A点击编辑子任务A的计划开始日期、计划完成日期属性'):
            ...
            # todo
        with step('项目管理员将子任务的「编辑计划开始日期、计划完成日期」权限域添加 「工作项负责人」'):
            param = proj.add_task_permission(issue_type_uuid, 'field027-field028')[0]
            param.json_update('items[0].user_domain_param', '')
            param.json_update('items[0].user_domain_type', 'task_assign')
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

    @story("T142080 子任务-工作项权限：编辑计划开始日期、计划完成日期权限（工作项关注者）")
    def test_sub_task_permission_update_task_field027_task_watchers(self, get_pro_permission, permission_data1):
        issue_type_uuid1 = permission_data1['issue_type_uuid']
        project_uuid = permission_data1['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid, 'field027-field028')

        with step('成员A点击编辑子任务A的计划开始日期、计划完成日期属性'):
            ...
            # todo
        with step('项目管理员将子任务的「编辑计划开始日期、计划完成日期」权限域添加 「工作项关注者」'):
            param = proj.add_task_permission(issue_type_uuid, 'field027-field028')[0]
            param.json_update('items[0].user_domain_param', '')
            param.json_update('items[0].user_domain_type', 'task_watchers')
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

    @story("T142081 子任务-工作项权限：编辑计划开始日期、计划完成日期权限（项目负责人）")
    def test_sub_task_permission_update_task_field027_project_assign(self, get_pro_permission, permission_data1):
        issue_type_uuid1 = permission_data1['issue_type_uuid']
        project_uuid = permission_data1['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid, 'field027-field028')

        with step('成员A点击编辑子任务A的计划开始日期、计划完成日期属性'):
            ...
            # todo
        with step('项目管理员将子任务的「编辑计划开始日期、计划完成日期」权限域添加 「项目负责人」'):
            param = proj.add_task_permission(issue_type_uuid, 'field027-field028')[0]
            param.json_update('items[0].user_domain_param', '')
            param.json_update('items[0].user_domain_type', 'project_assign')
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

    @story('T142138子任务-工作项权限：创建子任务权限（项目负责人）')
    def test_issue_permission_create_tasks_project_assign(self, get_pro_permission, permission_data1):
        permission = 'create_tasks'
        with step('项目管理员清空子任务的「创建子任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A创建子任务的工作项'):
            ...
            # todo:
        with step('项目管理员将子任务的「创建子任务」项目负责人'):
            param_dict = {'issue_type_uuid': permission_data1['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data1['p_id'])
