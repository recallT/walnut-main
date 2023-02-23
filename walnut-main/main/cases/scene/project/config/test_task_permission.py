"""
@Desc: 项目设置-任务-工作项权限
"""
import time
from falcons.com.nick import feature, fixture, mark, story, step

from main.actions.pro import ProjPermissionAction
from main.helper.extra import Extra
from main.actions.task import TaskAction
from falcons.com.meta import ApiMeta
from main.actions.member import MemberAction
from main.actions.issue import IssueAction as iis
from falcons.check import Checker, go
from main.params import data, proj, conf
from main.api import project, third, issue
from main.params.third import add_sub_department


@fixture(scope='module', autouse=True)
def permission_data():
    # 创建一个单独项目
    time.sleep(2)
    creator = Extra(ApiMeta)
    p_id = creator.new_project(f'任务工作项权限-测试')
    issue_type_uuid = TaskAction.issue_type_uuid('任务', project_uuid=p_id)[0]
    # 获取系统中存在的一个成员uuid
    member_uuid = MemberAction.get_member_uuid()
    data = {'p_id': p_id, 'member_uuid': member_uuid, 'issue_type_uuid': issue_type_uuid}
    return data


@fixture(scope='module', autouse=True)
def _del_project(permission_data):
    yield
    # 清除项目数据
    creator = Extra(ApiMeta)
    creator.del_project(permission_data['p_id'])


@fixture()
def get_pro_permission(permission_data):
    resp = iis.get_pro_permission_rules('任务', project_uuid=permission_data['p_id'])
    return resp


label = ApiMeta.env.label


@mark.skipif(label == 'private' or label == 'dev', reason='环境跳过权限用例')
@feature('工作项权限-任务')
class TestTaskPermission(Checker):
    @classmethod
    def get_issue_permission_uuid(cls, resp, permission_type):
        """获取权限成员域的列表"""
        uuid_list = [r['uuid'] for r in resp.value('permission_rules') if
                     r['permission'] == permission_type]
        return uuid_list

    @classmethod
    def del_update_task_field(cls, issue_type_uuid1, project_uuid, uuid):
        """对 任务工作项权限的 编辑计划开始日期、计划完成日期权限 的成员域进行清除操作"""
        issue_type_uuid = TaskAction.issue_type_uuid('任务', uuid_type='uuid'
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

    @story("T132950 任务-工作项权限：查看任务权限（项目负责人）")
    def test_issue_permission_view_task_project_leader(self, get_pro_permission, permission_data):
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('项目管理员将任务的「查看任务」权限域添加为「项目负责人」'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T132947 任务-工作项权限：查看任务权限（工作项创建者）")
    def test_issue_permission_view_task_item_creator(self, get_pro_permission, permission_data):
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('项目管理员将任务的「查看任务」权限域添加为「工作项创建者」'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_owner'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T132949 任务-工作项权限：查看任务权限（工作项关注者）")
    def test_issue_permission_view_task_task_watchers(self, get_pro_permission, permission_data):
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('项目管理员将任务的「查看任务」权限域添加为「工作项关注者」'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_watchers'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T132945 任务-工作项权限：查看任务权限（部门）")
    def test_issue_permission_view_task_department(self, get_pro_permission, permission_data):
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('成员A查看任务A的属性-无法查看'):
            ...
            # todo:
        with step('项目管理员将任务的「查看任务」权限域添加部门1'):
            # 新增部门
            param = add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)
            depart_uuid = resp.json()['add_department']['uuid']
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': depart_uuid,
                          'user_domain_type': 'department'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('清除部门数据'):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story("T132952 任务-工作项权限：查看任务权限（用户组）")
    def test_issue_permission_view_group(self, get_pro_permission, permission_data):
        # 新增用户组
        param = data.user_group_add()[0]
        resp = self.call(project.UsesGroupAdd, param)
        group_uuid = resp.value('uuid')
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('成员A查看任务A'):
            ...
            # todo:
        with step('项目管理员将任务的「查看任务」权限域添加用户组1'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': group_uuid,
                          'user_domain_type': 'group'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('清除用户组数据'):
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param, with_json=False)

    @story("T132951 任务-工作项权限：查看任务权限（项目角色）")
    def test_issue_permission_view_project_role(self, get_pro_permission,permission_data):
        # 新建 项目角色
        role_uuid = MemberAction.add_member_role().value('role.uuid')
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('成员A查看任务A'):
            ...
            # todo:
        with step('项目管理员将任务的「查看任务」权限域添加「项目角色」'):
            # 获取系统中存在的一个成员uuid
            member_uuid = MemberAction.get_member_uuid()
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': role_uuid,
                          'user_domain_type': 'role'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('删除角色'):
            MemberAction.del_member_role(role_uuid)

    @story("T132960 任务-工作项权限：成为负责人权限（项目负责人）")
    def test_issue_permission_be_assigned_project_leader(self, get_pro_permission, permission_data):
        permission = 'be_assigned'
        with step('项目管理员清空任务的「成为负责人」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('成员A创建任务的工作项'):
            ...
            # todo:
        with step('项目管理员添加任务的「成为负责人」权限域为项目负责人'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T132961 任务-工作项权限：成为负责人权限（项目角色）")
    def test_issue_permission_be_assigned_project_role(self, get_pro_permission, permission_data):
        # 新建 项目角色
        role_uuid = MemberAction.add_member_role().value('role.uuid')
        permission = 'be_assigned'

        with step("先删除成员域的列表"):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])

        with step('成员A创建任务的工作项'):
            ...
            # todo:
        with step('项目管理员将任务的「成为负责人」权限域添加项目角色'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': role_uuid,
                          'user_domain_type': 'role'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('删除角色'):
            MemberAction.del_member_role(role_uuid)

    @story("T132958 任务-工作项权限：成为负责人权限（部门）")
    def test_issue_permission_be_assigned_department(self, get_pro_permission, permission_data):
        permission = 'be_assigned'
        with step('项目管理员清空任务的「成为负责人」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('成员A创建任务的工作项'):
            ...
            # todo:
        with step('项目管理员将任务的「成为负责人」权限域添加部门1'):
            # 新增部门
            param = add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)
            depart_uuid = resp.json()['add_department']['uuid']
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': depart_uuid,
                          'user_domain_type': 'department'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('清除部门数据'):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story("T132962 任务-工作项权限：成为负责人权限（用户组）")
    def test_issue_permission_be_assigned_group(self, get_pro_permission, permission_data):
        # 新增用户组
        param = data.user_group_add()[0]
        resp = self.call(project.UsesGroupAdd, param)
        group_uuid = resp.value('uuid')
        permission = 'be_assigned'
        with step('项目管理员清空任务的「成为负责人」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('成员A创建任务的工作项'):
            ...
            # todo:
        with step('项目管理员将任务的「成为负责人」权限域添加用户组1'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': group_uuid,
                          'user_domain_type': 'group'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('清除用户组数据'):
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param, with_json=False)

    @story("T132987 任务-工作项权限：更新任务状态权限（项目负责人）")
    def test_issue_permission_update_tasks_project_leader(self, get_pro_permission, permission_data):
        permission = 'transit_tasks'
        with step('项目管理员清空任务的「更新任务」列表权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('成员A更新任务A的状态'):
            ...
            # todo:
        with step('项目管理员将任务的「更新任务」列表权限域为「项目负责人」'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param':'',
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T133000 任务-工作项权限：管理所有登记工时权限（项目负责人）")
    def test_issue_permission_manage_hour_project_leader(self, get_pro_permission, permission_data):
        permission = 'manage_task_record_manhours'

        with step("先删除成员域的列表"):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])

        with step('成员A编辑任务A下成员L的登记工时记录'):
            ...
            # todo:
        with step('项目管理员将任务的「管理所有登记工时」列表权限域为「项目负责人」'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T132966 任务-工作项权限：创建任务权限（部门）")
    def test_issue_permission_create_tasks_department(self, get_pro_permission, permission_data):
        permission = 'create_tasks'
        with step('项目管理员清空任务的「创建任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('成员A创建任务的工作项'):
            ...
            # todo:
        with step('项目管理员将任务的「创建任务」权限域添加为项目负责人'):
            # 新增部门：
            param = add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)
            depart_uuid = resp.json()['add_department']['uuid']
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': depart_uuid,
                          'user_domain_type': 'department'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('清除部门数据'):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story("T132968 任务-工作项权限：创建任务权限（项目负责人）")
    def test_issue_permission_create_tasks_project_leader(self, get_pro_permission, permission_data):
        permission = 'create_tasks'
        with step('项目管理员清空任务的「创建任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('成员A创建任务的工作项'):
            ...
            # todo:
        with step('项目管理员将任务的「创建任务」权限域添加为项目负责人'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T132969 任务-工作项权限：创建任务权限（项目角色）")
    def test_issue_permission_create_tasks_project_role(self, get_pro_permission, permission_data):
        # 新建 项目角色
        role_uuid = MemberAction.add_member_role().value('role.uuid')
        permission = 'create_tasks'
        with step('项目管理员清空任务的「创建任务」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('成员A创建任务的工作项'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑任务」权限域添加工作项负责人'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': role_uuid,
                          'user_domain_type': 'role'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

        with step('删除角色'):
            MemberAction.del_member_role(role_uuid)

    @story("T132970 任务-工作项权限：创建任务权限（用户组）")
    def test_issue_permission_create_tasks_group(self, get_pro_permission, permission_data):
        # 新增用户组
        param = data.user_group_add()[0]
        resp = self.call(project.UsesGroupAdd, param)
        group_uuid = resp.value('uuid')
        permission = 'create_tasks'
        with step('项目管理员清空任务的「创建任务权限」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('成员A创建任务的工作项'):
            ...
            # todo:
        with step('项目管理员将任务的「创建任务权限」权限域添加用户组1'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': group_uuid,
                          'user_domain_type': 'group'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('清除用户组数据'):
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param, with_json=False)

    @story("T132974 任务-工作项权限：导出任务列表权限（部门）")
    def test_issue_permission_export_tasks_department(self, get_pro_permission, permission_data):
        permission = 'export_tasks'
        with step('项目管理员清空任务的「导出任务列表」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('成员A导出任务下的工作项'):
            ...
            # todo:
        with step('项目管理员将任务的「导出任务列表」权限域添加部门1'):
            # 新增部门
            param = add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)
            depart_uuid = resp.json()['add_department']['uuid']
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': depart_uuid,
                          'user_domain_type': 'department'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('清除部门数据'):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story("T132976 任务-工作项权限：导出任务列表权限（项目负责人）")
    def test_issue_permission_export_tasks_project_leader(self, get_pro_permission, permission_data):
        permission = 'export_tasks'
        with step("先删除成员域的列表"):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])

        with step('成员A导出任务下的工作项'):
            ...
            # todo:
        with step('项目管理员清空任务的「导出任务」列表权限域为「项目负责人」'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T132977 任务-工作项权限：导出任务列表权限（项目角色）")
    def test_issue_permission_export_tasks_project_role(self, get_pro_permission, permission_data):
        # 新建 项目角色
        role_uuid = MemberAction.add_member_role().value('role.uuid')
        permission = 'export_tasks'
        with step("先删除成员域的列表"):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])

        with step('成员A导出任务下的工作项'):
            ...
            # todo:
        with step('项目管理员将任务的「导出任务列表」权限域添加项目角色'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': role_uuid,
                          'user_domain_type': 'role'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('删除角色'):
            MemberAction.del_member_role(role_uuid)

    @story("T132978 任务-工作项权限：导出任务列表权限（用户组）")
    def test_issue_permission_export_tasks_group(self, get_pro_permission, permission_data):
        # 新增用户组
        param = data.user_group_add()[0]
        resp = self.call(project.UsesGroupAdd, param)
        group_uuid = resp.value('uuid')
        permission = 'export_tasks'

        with step("先删除成员域的列表"):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            for i in range(len(uuid_list)):
                ProjPermissionAction.del_permission(uuid_list[i])
        with step('成员A导出任务下的工作项'):
            ...
            # todo:
        with step('项目管理员将任务的「导出任务列表」权限域添加用户组1'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': group_uuid,
                          'user_domain_type': 'group'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('清除用户组数据'):
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param, with_json=False)

# 2022/7/27

    @story("T132893 任务-工作项权限：编辑关注者权限（部门）")
    def test_issue_permission_edit_followers_department(self, get_pro_permission, permission_data):
        permission = 'update_task_watchers'
        with step('项目管理员清空任务的「编辑关注者」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑关注者」权限域添加部门1'):
            # 新增部门
            param = add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)
            depart_uuid = resp.json()['add_department']['uuid']
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': depart_uuid,
                          'user_domain_type': 'department'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('清除部门数据'):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story("T132895 任务-工作项权限：编辑关注者权限（工作项创建者）")
    def test_issue_permission_edit_followers_item_creator(self, get_pro_permission, permission_data):
        permission = 'update_task_watchers'
        with step('项目管理员清空任务的「编辑关注者」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('项目管理员将任务的「编辑关注者」权限域添加为「工作项创建者」'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_owner'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T132896 任务-工作项权限：编辑关注者权限（工作项负责人）")
    def test_issue_permission_edit_followers_item_leader(self, get_pro_permission, permission_data):
        permission = 'update_task_watchers'
        with step('项目管理员清空任务的「编辑关注者」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('项目管理员将任务的「编辑关注者」权限域添加为「工作项负责人」'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T132897 任务-工作项权限：编辑关注者权限（工作项关注者）")
    def test_issue_permission_edit_followers_task_watchers(self, get_pro_permission, permission_data):
        permission = 'update_task_watchers'
        with step('项目管理员清空任务的「编辑关注者」权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('项目管理员将任务的「编辑关注者」权限域添加为「工作项关注者」'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'task_watchers'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T132898 任务-工作项权限：编辑关注者权限（项目负责人）")
    def test_issue_permission_edit_followers_project_leader(self, get_pro_permission, permission_data):
        permission = 'update_task_watchers'
        with step('项目管理员清空任务的「编辑关注者」列表权限域'):
            resp = get_pro_permission
            uuid_list = self.get_issue_permission_uuid(resp, permission)
            if len(uuid_list) != 0:
                iis.del_issue_permission(uuid_list[0])
        with step('成员A导出任务下的工作项'):
            ...
            # todo:
        with step('项目管理员清空任务的「编辑关注者」列表权限域为「项目负责人」'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': '',
                          'user_domain_type': 'project_assign'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])

    @story("T132899 任务-工作项权限：编辑关注者权限（项目角色）")
    def test_issue_permission_edit_followers_project_role(self, get_pro_permission, permission_data):
        # 新建 项目角色
        role_uuid = MemberAction.add_member_role().value('role.uuid')
        permission = 'update_task_watchers'

        with step("先删除成员域的列表"):
            rule_uuid = [p['uuid'] for p in get_pro_permission.json()['permission_rules'] if
                         p['permission'] == 'be_assigned']

            for i in range(len(rule_uuid)):
                ProjPermissionAction.del_permission(rule_uuid[i])

        with step('成员A编辑任务A的关注者'):
            ...
            # todo:
        with step('项目管理员将任务的「编辑关注者」权限域添加「项目角色」'):
            param_dict = {'issue_type_uuid': permission_data['issue_type_uuid'], 'permission': permission,
                          'user_domain_param': role_uuid,
                          'user_domain_type': 'role'}
            iis.add_issue_permission(param_dict, project_uuid=permission_data['p_id'])
        with step('删除角色'):
            MemberAction.del_member_role(role_uuid)

    @story("T132906 任务-工作项权限：编辑计划开始日期、计划完成日期权限（部门）")
    def test_issue_permission_update_task_field_field027_field028(self, permission_data):
        issue_type_uuid1 = permission_data['issue_type_uuid']
        project_uuid = permission_data['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid,'field027-field028')

        with step('成员A点击编辑任务A的计划开始日期、计划完成日期属性'):
            ...
            # todo
        with step('项目管理员将任务的「编辑计划开始日期、计划完成日期」权限域添加成员A'):
            # 新增部门
            param1 = add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param1)
            depart_uuid = resp.json()['add_department']['uuid']

            param = proj.add_task_permission(issue_type_uuid, 'field027-field028')[0]
            param.json_update('items[0].user_domain_param', depart_uuid)
            param.json_update('items[0].user_domain_type', 'department')
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)
        with step('清除部门数据'):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story("T132908 任务-工作项权限：编辑计划开始日期、计划完成日期权限（工作项创建者）")
    def test_issue_permission_update_task_field_project_creator(self, permission_data):
        issue_type_uuid1 = permission_data['issue_type_uuid']
        project_uuid = permission_data['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid,'field027-field028')

        with step('成员A点击编辑任务A的计划开始日期、计划完成日期属性'):
            ...
            # todo
        with step('项目管理员将任务的「编辑计划开始日期、计划完成日期」权限域添加 「工作项创建者」'):
            param = proj.add_task_permission(issue_type_uuid, 'field027-field028')[0]
            param.json_update('items[0].user_domain_param', '')
            param.json_update('items[0].user_domain_type', 'task_owner')
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

    @story("T132909 任务-工作项权限：编辑计划开始日期、计划完成日期权限（工作项负责人）")
    @story("T132910 任务-工作项权限：编辑计划开始日期、计划完成日期权限（工作项关注者）")
    @story("T132911 任务-工作项权限：编辑计划开始日期、计划完成日期权限（项目负责人）")
    def test_issue_permission_update_task_field_item_leader(self, permission_data):
        issue_type_uuid1 = permission_data['issue_type_uuid']
        project_uuid = permission_data['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid, 'field027-field028')

        with step('成员A点击编辑任务A的计划开始日期、计划完成日期属性'):
            ...
            # todo
        with step('项目管理员将任务的「编辑计划开始日期、计划完成日期」权限域添加 工作项负责人'):
            param = proj.add_task_permission(issue_type_uuid, 'field027-field028')[0]
            param.json_update('items[0].user_domain_param','')
            param.json_update('items[0].user_domain_type', 'task_assign')
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

        with step("权限域 添加 工作项关注者"):
            param.json_update('items[0].user_domain_type', 'task_watchers')
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

        with step("权限域 添加 项目负责人"):
            param.json_update('items[0].user_domain_type', 'project_assign')
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)

    @story("T132912 任务-工作项权限：编辑计划开始日期、计划完成日期权限（项目角色）")
    def test_issue_permission_update_task_field_project_role(self, permission_data):
        # 获取任务工作项类型的uuid
        issue_type_uuid1 = permission_data['issue_type_uuid']
        # 获取项目创建后的uuid
        project_uuid = permission_data['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid,'field027-field028')

        with step('成员A点击编辑任务A的计划开始日期、计划完成日期属性'):
            ...
            # todo
        with step('项目管理员将任务的「编辑计划开始日期、计划完成日期」权限域添加 「项目角色」'):
            # 新增角色
            role_uuid = MemberAction.add_member_role().value('role.uuid')

            param = proj.add_task_permission(issue_type_uuid, 'field027-field028')[0]
            param.json_update('items[0].user_domain_param', role_uuid)
            param.json_update('items[0].user_domain_type', 'role')
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)
        with step('删除角色'):
            MemberAction.del_member_role(role_uuid)

    @story("T132913 任务-工作项权限：编辑计划开始日期、计划完成日期权限（用户组）")
    def test_issue_permission_update_task_field_group(self, permission_data):
        issue_type_uuid1 = permission_data['issue_type_uuid']
        project_uuid = permission_data['p_id']
        issue_type_uuid = self.del_update_task_field(issue_type_uuid1, project_uuid,'field027-field028')
        with step('成员A点击编辑任务A的计划开始日期、计划完成日期属性'):
            ...
            # todo
        with step('项目管理员将任务的「编辑计划开始日期、计划完成日期」权限域添加 「用户组」'):
            # 新增用户组
            param = data.user_group_add()[0]
            resp = self.call(project.UsesGroupAdd, param)
            group_uuid = resp.value('uuid')

            param = proj.add_task_permission(issue_type_uuid, 'field027-field028')[0]
            param.json_update('items[0].user_domain_param', group_uuid)
            param.json_update('items[0].user_domain_type', 'group')
            resp = self.call(project.ItemBatchAdd, param)
            resp.check_response('code', 200)
        with step('清除用户组数据'):
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param, with_json=False)

