# -*- coding: UTF-8 -*-
"""
@Author  ：zhangweiyu@ones.ai
@Date    ：2022/8/16
@Desc    ：项目-工作项权限-管理预估工时权限
"""
import time

from falcons.check import Checker, go
from falcons.com.nick import feature, step, fixture, mark, story
from falcons.com.ones import unify_login
from main.actions.member import MemberAction
from main.actions.pro import PrjAction, ProjPermissionAction
from main.actions.task import TaskAction
from main.api import task as tk, task as ta
from main.cases.scene.configs.issue import IssueConfig
from main.helper.extra import Extra
from falcons.com.meta import ApiMeta

from main.params import task
from . import add_permission, clear_permission, get_default_role, clear_issue_field_contraint


@fixture(scope='module', autouse=True)
def _data():
    with step('全局配置：工时模式切换为"简单模式"'):
        PrjAction.work_hour_configs_update('simple')
    with step('创建一个项目'):
        time.sleep(2)
        pid = PrjAction.new_project(index=3, name='项目-工作项权限-管理预估工时权限')
        it_uuid = TaskAction.issue_type_uuid('任务', project_uuid=pid)[0]
        s_it_uuid = TaskAction.issue_type_uuid('子任务', project_uuid=pid)[0]

    with step('项目-清空工作项的属性修改权限（维护：全局配置用例会影响）'):
        for i_name in ['任务', '子任务']:
            issue_uuid = TaskAction.issue_type_uuid(issue_types=i_name, uuid_type='uuid', project_uuid=pid)[0]
            issue_type_uuid = TaskAction.issue_type_uuid(issue_types=i_name, project_uuid=pid)[0]
            clear_issue_field_contraint(pid, issue_uuid, issue_type_uuid)
    with step('项目-添加自定义成员属性'):
        with step('全局-项目-添加工作项属性'):
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
    with step('创建成员A'):
        user_a = MemberAction.new_member()
        # 为用户A添加查看项目权限
        ProjPermissionAction.add_permission('single_user', permission="browse_project",
                                            user_domain_param=user_a.owner_uuid,
                                            project_uuid=pid)
        # 添加成员A为项目成员
        MemberAction.add_proj_member(user_a.owner_uuid, project_uuid=pid)
        # 修改成员A为项目负责人
        PrjAction.update_prj_assign(pid, user_a.owner_uuid)
    with step('新建1个任务'):
        more_fields = []
        for k in fid_map.keys():
            more_fields.append({
                "field_uuid": fid_map[k],
                "type": f_type_map[k],
                "value": [user_a.owner_uuid] if k.find('多') > -1 else user_a.owner_uuid
            })
        t_param = TaskAction.new_issue(proj_uuid=pid, param_only=True)
        t_param.json['tasks'][0]['field_values'] += more_fields
        res = go(tk.TaskAdd, t_param)
        tid = [r['uuid'] for r in res.json()['tasks']][0]
    with step('新建1个子任务'):
        s_t_param = TaskAction.new_issue(issue_type_name='子任务', param_only=True, parent_uuid=tid, proj_uuid=pid)
        s_t_param.json['tasks'][0]['field_values'] += more_fields
        res = go(tk.TaskAdd, s_t_param)
        s_tid = [r['uuid'] for r in res.json()['tasks']][0]
    data = {'pid': pid,
            'fid_map': fid_map,  # 自定义成员属性id的map表
            'a_uid': user_a.owner_uuid,  # 成员A的id
            'a_utoken': unify_login(user_a),  # 成员A的token
            'tid': tid,  # 任务id-管理员创建
            's_tid': s_tid,  # 子任务id-管理员创建
            'it_id': it_uuid,  # 任务-工作项类型id
            's_it_id': s_it_uuid  # 子任务-工作项类型id
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
def _a_sub_task(_data):
    # 用户A创建子任务
    for perm in ["create_tasks", "view_tasks", "be_assigned"]:
        add_permission(_data['pid'], _data['s_it_id'], perm, 'single_user', _data['a_uid'])
    with step('用户A新建1个子任务'):
        s_tid = TaskAction.new_issue(parent_uuid=_data['tid'],
                                     proj_uuid=_data['pid'],
                                     issue_type_name='子任务',
                                     owner_uuid=_data['a_uid'],
                                     field004=_data['a_uid'],
                                     watcher_uuid=_data['a_uid'],
                                     token=_data['a_utoken']
                                     )[0]
    return s_tid


label = ApiMeta.env.label

permission = 'manage_task_assess_manhour'


@mark.skipif(label == 'private' or label == 'dev', reason='环境跳过权限用例')
@feature('项目-工作项权限-管理预估工时权限')
class TestPrjTaskPermAssessHour(Checker):
    @classmethod
    def update_assess_hour(cls, tid, token=None, status_code=200):
        """更新预估工时"""
        param = task.assess_man_hour()[0]
        param.uri_args({'task_uuid': tid})
        cls.call(ta.TaskAssessManHourUpdate, param, status_code=status_code, token=token)

    @story('T133029 任务-工作项权限：管理预估工时权限（自定义单选成员属性）')
    def test_task_perm_custom_field_type_8(self, _data):
        with step('项目管理员清空任务的「管理预估工时」权限域'):
            clear_permission(permission, _data['pid'])
        with step('登陆成员A编辑任务A预估工时'):
            self.update_assess_hour(_data['tid'], token=_data['a_utoken'], status_code=403)
        with step('项目管理员添加任务的「管理预估工时」权限域为示例单选成员'):
            add_permission(_data['pid'], _data['it_id'], permission,
                           "custom_member_fields", _data['fid_map']['自定义单选成员'])
        with step('成员A编辑任务A的预估工时记录'):
            self.update_assess_hour(_data['tid'], token=_data['a_utoken'], status_code=200)

    @story('T133030 任务-工作项权限：管理预估工时权限（自定义多选成员属性）')
    def test_task_perm_custom_field_type_13(self, _data):
        with step('项目管理员清空任务的「管理预估工时」权限域'):
            clear_permission(permission, _data['pid'])
        with step('登陆成员A编辑任务A预估工时'):
            self.update_assess_hour(_data['tid'], token=_data['a_utoken'], status_code=403)
        with step('项目管理员添加任务的「管理预估工时」权限域为示例多选成员'):
            add_permission(_data['pid'], _data['it_id'], permission,
                           "custom_member_fields", _data['fid_map']['自定义多选成员'])
        with step('成员A编辑任务A的预估工时记录'):
            self.update_assess_hour(_data['tid'], token=_data['a_utoken'], status_code=200)

    @story('T142199 子任务-工作项权限：管理预估工时权限（自定义单选成员属性）')
    def test_sub_task_perm_custom_field_type_8(self, _data):
        with step('项目管理员清空子任务的「管理预估工时」权限域'):
            clear_permission(permission, _data['pid'], it_name='子任务')
        with step('登陆成员A编辑子任务A预估工时'):
            self.update_assess_hour(_data['s_tid'], token=_data['a_utoken'], status_code=403)
        with step('项目管理员添加子任务的「管理预估工时」权限域为示例单选成员'):
            add_permission(_data['pid'], _data['s_it_id'], permission,
                           "custom_member_fields", _data['fid_map']['自定义单选成员'])
        with step('成员A编辑任务A的预估工时记录'):
            self.update_assess_hour(_data['s_tid'], token=_data['a_utoken'], status_code=200)

    @story('T142200 子任务-工作项权限：管理预估工时权限（自定义多选成员属性）')
    def test_sub_task_perm_custom_field_type_13(self, _data):
        with step('项目管理员清空子任务的「管理预估工时」权限域'):
            clear_permission(permission, _data['pid'], it_name='子任务')
        with step('登陆成员A编辑子任务A预估工时'):
            self.update_assess_hour(_data['s_tid'], token=_data['a_utoken'], status_code=403)
        with step('项目管理员添加子任务的「管理预估工时」权限域为示例多选成员'):
            add_permission(_data['pid'], _data['s_it_id'], permission,
                           "custom_member_fields", _data['fid_map']['自定义多选成员'])
        with step('成员A编辑任务A的预估工时记录'):
            self.update_assess_hour(_data['s_tid'], token=_data['a_utoken'], status_code=200)

    @story('T142191 子任务-工作项权限：管理预估工时权限（部门）')
    def test_sub_task_perm_department(self, _data, _department):
        with step('项目管理员清空子任务的「管理预估工时」权限域'):
            clear_permission(permission, _data['pid'], it_name='子任务')
        with step('登陆成员A编辑子任务A预估工时'):
            self.update_assess_hour(_data['s_tid'], token=_data['a_utoken'], status_code=403)
        with step('项目管理员添加子任务的「管理预估工时」权限域为部门1'):
            add_permission(_data['pid'], _data['s_it_id'], permission,
                           "department", _department)
        with step('成员A编辑任务A的预估工时记录'):
            self.update_assess_hour(_data['s_tid'], token=_data['a_utoken'], status_code=200)

    @story('T142198 子任务-工作项权限：管理预估工时权限（用户组）')
    def test_sub_task_perm_group(self, _data, _group):
        with step('项目管理员清空子任务的「管理预估工时」权限域'):
            clear_permission(permission, _data['pid'], it_name='子任务')
        with step('登陆成员A编辑子任务A预估工时'):
            self.update_assess_hour(_data['s_tid'], token=_data['a_utoken'], status_code=403)
        with step('项目管理员添加子任务的「管理预估工时」权限域为用户组1'):
            add_permission(_data['pid'], _data['s_it_id'], permission,
                           "group", _group)
        with step('成员A编辑任务A的预估工时记录'):
            self.update_assess_hour(_data['s_tid'], token=_data['a_utoken'], status_code=200)

    @story('T142193 子任务-工作项权限：管理预估工时权限（工作项创建者）')
    def test_sub_task_t_creator(self, _data, _a_sub_task):
        with step('项目管理员清空子任务的「管理预估工时」权限域'):
            clear_permission(permission, _data['pid'], it_name='子任务')
        with step('登陆成员A编辑子任务A预估工时'):
            self.update_assess_hour(_a_sub_task, token=_data['a_utoken'], status_code=403)
        with step('项目管理员添加子任务的「管理预估工时」权限域为（工作项创建者）'):
            add_permission(_data['pid'], _data['s_it_id'], permission, "task_owner", "")
        with step('成员A编辑任务A的预估工时记录'):
            self.update_assess_hour(_a_sub_task, token=_data['a_utoken'], status_code=200)

    @story('T142194 子任务-工作项权限：管理预估工时权限（工作项负责人）')
    def test_sub_task_t_assigner(self, _data, _a_sub_task):
        with step('项目管理员清空子任务的「管理预估工时」权限域'):
            clear_permission(permission, _data['pid'], it_name='子任务')
        with step('登陆成员A编辑子任务A预估工时'):
            self.update_assess_hour(_a_sub_task, token=_data['a_utoken'], status_code=403)
        with step('项目管理员添加子任务的「管理预估工时」权限域为（工作项负责人）'):
            add_permission(_data['pid'], _data['s_it_id'], permission, "task_assign", "")
        with step('成员A编辑任务A的预估工时记录'):
            self.update_assess_hour(_a_sub_task, token=_data['a_utoken'], status_code=200)

    @story('T142195 子任务-工作项权限：管理预估工时权限（工作项关注者）')
    def test_sub_task_t_watcher(self, _data, _a_sub_task):
        with step('项目管理员清空子任务的「管理预估工时」权限域'):
            clear_permission(permission, _data['pid'], it_name='子任务')
        with step('登陆成员A编辑子任务A预估工时'):
            self.update_assess_hour(_a_sub_task, token=_data['a_utoken'], status_code=403)
        with step('项目管理员添加子任务的「管理预估工时」权限域为（工作项关注者）'):
            add_permission(_data['pid'], _data['s_it_id'], permission, "task_watchers", "")
        with step('成员A编辑任务A的预估工时记录'):
            self.update_assess_hour(_a_sub_task, token=_data['a_utoken'], status_code=200)

    @story('T142196 子任务-工作项权限：管理预估工时权限（项目负责人）')
    def test_sub_task_p_assign(self, _data, _a_sub_task):
        with step('项目管理员清空子任务的「管理预估工时」权限域'):
            clear_permission(permission, _data['pid'], it_name='子任务')
        with step('登陆成员A编辑子任务A预估工时'):
            self.update_assess_hour(_a_sub_task, token=_data['a_utoken'], status_code=403)
        with step('项目管理员添加子任务的「管理预估工时」权限域为（项目负责人）'):
            add_permission(_data['pid'], _data['s_it_id'], permission, "project_assign", "")
        with step('成员A编辑任务A的预估工时记录'):
            self.update_assess_hour(_a_sub_task, token=_data['a_utoken'], status_code=200)

    @story('T142197 子任务-工作项权限：管理预估工时权限（项目角色）')
    def test_sub_task_p_role(self, _data, _a_sub_task):
        with step('项目管理员清空子任务的「管理预估工时」权限域'):
            clear_permission(permission, _data['pid'], it_name='子任务')
        with step('登陆成员A编辑子任务A预估工时'):
            self.update_assess_hour(_a_sub_task, token=_data['a_utoken'], status_code=403)
        with step('项目管理员添加子任务的「管理预估工时」权限域为（项目角色-项目成员）'):
            role_id = get_default_role(_data['pid'])
            add_permission(_data['pid'], _data['s_it_id'], permission, "role", role_id)
        with step('成员A编辑任务A的预估工时记录'):
            self.update_assess_hour(_a_sub_task, token=_data['a_utoken'], status_code=200)
