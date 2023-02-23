# -*- coding: UTF-8 -*-
"""
@Author  ：zhangweiyu@ones.ai
@Date    ：2022/8/18
@Desc    ：项目-工作项权限-管理自己预估工时权限
"""
import time

from falcons.check import Checker, go
from falcons.com.nick import feature, step, fixture, mark, story
from falcons.com.ones import unify_login
from main.actions.member import MemberAction
from main.actions.pro import PrjAction, ProjPermissionAction
from main.actions.task import TaskAction
from main.api import task as tk, project
from main.cases.scene.configs.issue import IssueConfig
from main.helper.extra import Extra
from falcons.com.meta import ApiMeta

from main.params import task
from . import add_permission, clear_permission, get_default_role, clear_issue_field_contraint


def add_manhour(tid, owner=None, token=None):
    param = task.add_man_hour_detail_estimated(tid=tid)[0]
    if owner:
        param.json_update('variables.owner', owner)
    res = go(project.ItemGraphql, param, token=token)
    return res.value('data.addManhour.key')


@fixture(scope='module', autouse=True)
def _data():
    with step('全局配置：工时模式切换为"汇总模式"'):
        PrjAction.work_hour_configs_update('detailed')
    with step('创建一个项目'):
        time.sleep(2)
        pid = PrjAction.new_project(index=3, name='项目-工作项权限-管理自己预估工时权限')
        it_uuid = TaskAction.issue_type_uuid('任务', project_uuid=pid)[0]
        s_it_uuid = TaskAction.issue_type_uuid('子任务', project_uuid=pid)[0]
    with step('项目-添加自定义成员属性'):
        f_type_map = {"自定义单选成员": 8, "自定义多选成员": 13}
        fid_map = {}
        for k in f_type_map.keys():
            field_type = f_type_map[k]
            with step('全局-添加工作项属性'):
                field_uuid = IssueConfig.issue_field_add(field_type=field_type)
                add_field_config = {
                    "field_uuid": field_uuid,
                    "required": False
                }
            with step('项目-添加工作项属性'):
                TaskAction.task_add_field(add_field_config, project_uuid=pid)
                TaskAction.task_add_field(add_field_config, project_uuid=pid, issue_types='子任务')
            fid_map[k] = field_uuid
    with step('项目-清空工作项的属性修改权限（维护：全局配置用例会影响）'):
        for i_name in ['任务', '子任务']:
            issue_uuid = TaskAction.issue_type_uuid(issue_types=i_name, uuid_type='uuid', project_uuid=pid)[0]
            issue_type_uuid = TaskAction.issue_type_uuid(issue_types=i_name, project_uuid=pid)[0]
            clear_issue_field_contraint(pid, issue_uuid, issue_type_uuid)
    with step('创建成员A，并授权（查看项目、项目成员、项目负责人）'):
        user_a = MemberAction.new_member()
        # 为用户A添加查看项目权限
        ProjPermissionAction.add_permission('single_user', permission="browse_project",
                                            user_domain_param=user_a.owner_uuid,
                                            project_uuid=pid)
        # 添加成员A为项目成员
        MemberAction.add_proj_member(user_a.owner_uuid, project_uuid=pid)
        # 修改成员A为项目负责人
        PrjAction.update_prj_assign(pid, user_a.owner_uuid)
    with step('清空任务、子任务的权限域：管理所有预估工时'):
        clear_permission('manage_task_assess_manhour', pid, it_name='任务')
        clear_permission('manage_task_assess_manhour', pid, it_name='子任务')
    more_fields = []
    for k in fid_map.keys():
        more_fields.append({
            "field_uuid": fid_map[k],
            "type": f_type_map[k],
            "value": [user_a.owner_uuid] if k.find('多') > -1 else user_a.owner_uuid
        })
    data = {'pid': pid,
            'fid_map': fid_map,  # 自定义成员属性id的map表
            'a_uid': user_a.owner_uuid,  # 成员A的id
            'a_utoken': unify_login(user_a),  # 成员A的token
            'it_id': it_uuid,  # 任务-工作项类型id
            's_it_id': s_it_uuid,  # 子任务-工作项类型id
            'more_fields': more_fields  # 任务属性-自定义成员属性
            }
    yield data
    creator = Extra(ApiMeta)
    creator.del_project(pid)
    MemberAction.del_member(user_a.owner_uuid)


@fixture(scope='module')
def _department(_data):
    with step('创建部门B, 并添加成员A'):
        u_did = MemberAction.add_department()
        MemberAction.add_department_user(u_did, _data['a_uid'])
    yield u_did
    MemberAction.del_department(u_did)


@fixture(scope='module')
def _group(_data):
    with step('创建用户组C, 并添加成员A'):
        u_gid = MemberAction.add_user_group(members=[_data['a_uid']])
    yield u_gid
    MemberAction.del_user_group(u_gid)


@fixture(scope='module')
def _a_task(_data):
    with step('授权用户A创建任务'):
        for perm in ["create_tasks", "view_tasks", "be_assigned"]:
            add_permission(_data['pid'], _data['it_id'], perm, 'single_user', _data['a_uid'])
    with step('用户A-新建1个任务'):
        t_param = TaskAction.new_issue(proj_uuid=_data['pid'], param_only=True,
                                       owner_uuid=_data['a_uid'],
                                       field004=_data['a_uid'],
                                       watcher_uuid=_data['a_uid'])
        t_param.json['tasks'][0]['field_values'] += _data['more_fields']
        res = go(tk.TaskAdd, t_param, token=_data['a_utoken'])
        tid = [r['uuid'] for r in res.json()['tasks']][0]
    with step('成员A-新增1条预估工时'):
        t_h_key = add_manhour(tid, owner=_data['a_uid'])
    return {'tid': tid, 'h_key': t_h_key}


@fixture(scope='module')
def _a_sub_task(_data, _a_task):
    with step('授权用户A创建子任务'):
        for perm in ["create_tasks", "view_tasks", "be_assigned"]:
            add_permission(_data['pid'], _data['s_it_id'], perm, 'single_user', _data['a_uid'])
    with step('用户A-新建1个子任务'):
        s_t_param = TaskAction.new_issue(param_only=True,
                                         parent_uuid=_a_task['tid'],
                                         proj_uuid=_data['pid'],
                                         issue_type_name='子任务',
                                         owner_uuid=_data['a_uid'],
                                         field004=_data['a_uid'],
                                         watcher_uuid=_data['a_uid']
                                         )
        s_t_param.json['tasks'][0]['field_values'] += _data['more_fields']
        res = go(tk.TaskAdd, s_t_param, token=_data['a_utoken'])
        s_tid = [r['uuid'] for r in res.json()['tasks']][0]
    with step('成员A-新增一条工时记录'):
        s_t_h_key = add_manhour(s_tid, owner=_data['a_uid'])
    return {'tid': s_tid, 'h_key': s_t_h_key}


label = ApiMeta.env.label

permission = 'manage_task_own_assess_manhour'


@mark.skipif(label == 'private' or label == 'dev', reason='环境跳过权限用例')
@feature('项目-工作项权限-管理自己预估工时权限')
class TestPrjTaskPermOwnAssessHour(Checker):

    @classmethod
    def modify_manhour(cls, tid, t_h_key, owner, token=None, status_code=200):
        param = task.modify_man_hour()[0]
        param.json_update('variables.mode', 'detailed')
        param.json_update('variables.task', tid)
        param.json_update('variables.type', 'estimated')
        param.json_update('variables.key', t_h_key)
        param.json_update('variables.owner', owner)
        go(project.ItemGraphql, param, token=token, status_code=status_code)

    @story('T133048 任务-工作项权限：管理自己预估工时权限（部门）')
    def test_task_perm_department(self, _data, _department, _a_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'])
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['it_id'], permission,
                           "department", _department)
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T133049 任务-工作项权限：管理自己预估工时权限（成员）')
    def test_task_perm_member(self, _data, _a_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'])
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['it_id'], permission, "single_user", _data['a_uid'])
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T133055 任务-工作项权限：管理自己预估工时权限（用户组）')
    def test_task_perm_group(self, _data, _group, _a_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'])
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['it_id'], permission, "group", _group)
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T133050 任务-工作项权限：管理自己预估工时权限（工作项创建者）')
    def test_task_perm_t_creator(self, _data, _a_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'])
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['it_id'], permission, "task_owner", "")
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T133051 任务-工作项权限：管理自己预估工时权限（工作项负责人）')
    def test_task_perm_t_assigner(self, _data, _a_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'])
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['it_id'], permission, "task_assign", "")
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T133052 任务-工作项权限：管理自己预估工时权限（工作项关注者）')
    def test_task_perm_t_watcher(self, _data, _a_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'])
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['it_id'], permission, "task_watchers", "")
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T133053 任务-工作项权限：管理所自己预估工时权限（项目负责人）')
    def test_task_perm_p_assign(self, _data, _a_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'])
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['it_id'], permission, "project_assign", "")
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T133054 任务-工作项权限：管理自己预估工时权限（项目角色）')
    def test_task_perm_p_role(self, _data, _a_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'])
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时）'):
            role_id = get_default_role(_data['pid'])
            add_permission(_data['pid'], _data['it_id'], permission, "role", role_id)
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T133056 任务-工作项权限：管理自己预估工时权限（自定义单选成员属性）')
    def test_task_perm_custom_field_type_8(self, _data, _a_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'])
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['it_id'], permission, "custom_member_fields",
                           _data['fid_map']['自定义单选成员'])
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T133057 任务-工作项权限：管理自己预估工时权限（自定义多选成员属性）')
    def test_task_perm_custom_field_type_13(self, _data, _a_task):
        with step('清空限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'])
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['it_id'], permission, "custom_member_fields",
                           _data['fid_map']['自定义多选成员'])
            self.modify_manhour(_a_task['tid'], _a_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('子任务-工作项权限：管理自己预估工时权限（部门）')
    def test_sub_task_perm_department(self, _data, _department, _a_sub_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'], it_name='子任务')
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['s_it_id'], permission, "department", _department)
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T142219 子任务-工作项权限：管理自己预估工时权限（成员）')
    def test_sub_task_perm_member(self, _data, _department, _a_sub_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'], it_name='子任务')
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['s_it_id'], permission, "single_user", _data['a_uid'])
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T142225 子任务-工作项权限：管理自己预估工时权限（用户组）')
    def test_sub_task_perm_group(self, _data, _group, _a_sub_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'], it_name='子任务')
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['s_it_id'], permission, "group", _group)
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T142220 子任务-工作项权限：管理自己预估工时权限（工作项创建者）')
    def test_sub_task_t_creator(self, _data, _a_sub_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'], it_name='子任务')
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['s_it_id'], permission, "task_owner", "")
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T142221 子任务-工作项权限：管理自己预估工时权限（工作项负责人）')
    def test_sub_task_t_assigner(self, _data, _a_sub_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'], it_name='子任务')
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['s_it_id'], permission, "task_assign", "")
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T142222 子任务-工作项权限：管理自己预估工时权限（工作项关注者）')
    def test_sub_task_t_watcher(self, _data, _a_sub_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'], it_name='子任务')
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['s_it_id'], permission, "task_watchers", "")
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('子任务-工作项权限：管理自己预估工时权限（项目负责人）')
    def test_sub_task_p_assign(self, _data, _a_sub_task):
        with step('项目管理员清空子任务的「管理自己预估工时」权限域'):
            clear_permission(permission, _data['pid'], it_name='子任务')
        with step('登陆成员A编辑子任务A预估工时'):
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('项目管理员添加子任务的「管理自己预估工时」权限域为（项目负责人）'):
            add_permission(_data['pid'], _data['s_it_id'], permission, "project_assign", "")
        with step('成员A编辑子任务A的预估工时记录'):
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T142224 子任务-工作项权限：管理自己预估工时权限（项目角色）')
    def test_sub_task_p_role(self, _data, _a_sub_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'], it_name='子任务')
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            role_id = get_default_role(_data['pid'])
            add_permission(_data['pid'], _data['s_it_id'], permission, "role", role_id)
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T142226 子任务-工作项权限：管理自己预估工时权限（自定义单选成员属性')
    def test_sub_task_perm_custom_field_type_8(self, _data, _a_sub_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'], it_name='子任务')
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['s_it_id'], permission, "custom_member_fields",
                           _data['fid_map']['自定义单选成员'])
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)

    @story('T142227 子任务-工作项权限：管理自己预估工时权限（自定义多选成员属性）')
    def test_sub_task_perm_custom_field_type_13(self, _data, _a_sub_task):
        with step('清空权限域后，A编辑自己的预估工时'):
            clear_permission(permission, _data['pid'], it_name='子任务')
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=403)
        with step('添加权限域后，A编辑自己的预估工时'):
            add_permission(_data['pid'], _data['s_it_id'], permission, "custom_member_fields",
                           _data['fid_map']['自定义多选成员'])
            self.modify_manhour(_a_sub_task['tid'], _a_sub_task['h_key'], _data['a_uid'], token=_data['a_utoken'],
                                status_code=200)
