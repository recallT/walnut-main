# -*- coding: UTF-8 -*-
"""
@File    ：test_task_perm_custom_field.py
@Author  ：zhangweiyu@ones.ai
@Date    ：2022/8/15
@Desc    ：项目-工作项权限-自定义成员属性
"""
import time

from falcons.check import Checker, go
from falcons.com.nick import feature, step, fixture, mark, story
from falcons.com.ones import unify_login
from falcons.ops import generate_param

from main.actions.issue import IssueAction as ia
from main.actions.member import MemberAction
from main.actions.pro import PrjAction, ProjPermissionAction
from main.actions.task import TaskAction
from main.api import task as tk, project, issue
from main.params import task as tp
from main.cases.scene.configs.issue import IssueConfig
from main.helper.extra import Extra
from falcons.com.meta import ApiMeta, OnesParams
from . import get_start_step, trigger


@fixture(scope='module', autouse=True)
def prepare():
    with step('创建一个单独项目'):
        time.sleep(2)
        pid = PrjAction.new_project(index=3, name='项目-工作项权限-自定义成员属性')
        issue_type_uuid = TaskAction.issue_type_uuid('任务', project_uuid=pid)[0]
        s_it_uuid = TaskAction.issue_type_uuid('子任务', project_uuid=pid)[0]
    with step('全局-项目-添加工作项属性'):
        f_type_map = {"自定义单选成员": 8, "自定义多选成员": 13}
        f_uuid_map = {}
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
            f_uuid_map[k] = field_uuid
    with step('创建成员A'):
        user_a = MemberAction.new_member()
        # 为用户A添加查看项目权限
        ProjPermissionAction.add_permission('single_user', permission="browse_project",
                                            user_domain_param=user_a.owner_uuid,
                                            project_uuid=pid)
    with step('新建2个任务'):
        more_fields = []
        for k in f_uuid_map.keys():
            more_fields.append({
                "field_uuid": f_uuid_map[k],
                "type": f_type_map[k],
                "value": [user_a.owner_uuid] if k.find('多') > -1 else user_a.owner_uuid
            })
        tasks = []
        for i in range(2):
            t_param: OnesParams = TaskAction.new_issue(proj_uuid=pid, param_only=True)
            t_param.json['tasks'][0]['field_values'] += more_fields
            res = go(tk.TaskAdd, t_param)
            task_uuid = [r['uuid'] for r in res.json()['tasks']][0]
            tasks.append(task_uuid)
    with step('新建2个子任务'):
        sub_tasks = []
        parent_tid = TaskAction.new_issue(proj_uuid=pid)[0]
        for i in range(2):
            t_param: OnesParams = TaskAction.new_issue(parent_uuid=parent_tid, proj_uuid=pid, param_only=True,
                                                       issue_type_name='子任务')
            t_param.json['tasks'][0]['field_values'] += more_fields
            res = go(tk.TaskAdd, t_param)
            s_tid = [r['uuid'] for r in res.json()['tasks']][0]
            sub_tasks.append(s_tid)
    data = {'pid': pid,
            'user_a': user_a,
            'uid': user_a.owner_uuid,
            'utoken': unify_login(user_a),
            'f_uuid_map': f_uuid_map,
            'tid': tasks[0],
            'tasks': tasks,
            'issue_type_uuid': issue_type_uuid,
            's_it_uuid': s_it_uuid,
            'sub_tasks': sub_tasks}
    yield data
    creator = Extra(ApiMeta)
    creator.del_project(pid)
    MemberAction.del_member(user_a.owner_uuid)


@fixture(scope='module')
def transition(prepare):
    # 获取步骤：开始任务
    start_step = get_start_step(prepare['pid'], '任务')
    param = generate_param({
        "transitions": [
            {
                "project_uuid": prepare['pid'],
                "issue_type_uuid": prepare['issue_type_uuid'],
                "start_status_uuid": start_step['end_status_uuid'],
                "end_status_uuid": start_step['start_status_uuid'],
                "name": "未开始"
            }
        ]
    })[0]
    param.uri_args({'project_uuid': prepare['pid'], 'issue_type_uuid': prepare['issue_type_uuid']})
    # 新建步骤：进行中->未开始, 和开始任务流向相反
    res = go(issue.ProjWorkflowTransitionAdd, param)
    # step1: 未开始->进行中
    # step2: 进行中->未开始
    return {'step1': start_step, 'step2': res.value('transitions[0]')}


label = ApiMeta.env.label


@mark.skipif(label == 'private' or label == 'dev', reason='环境跳过权限用例')
@feature('项目-工作项权限-自定义成员属性')
class TestPrjTaskPermCustField(Checker):

    @classmethod
    def get_perm_uuids(cls, permission_type, project_uuid, it_name='任务'):
        res = ia.get_pro_permission_rules(it_name, project_uuid=project_uuid)
        uuids = [r['uuid'] for r in res.value('permission_rules') if
                 r['permission'] == permission_type]
        return uuids

    @classmethod
    def add_watcher(cls, tid, uid, token=None, code=None):
        param = tp.watchers_opt()[0]
        param.json_update('watchers', [uid])
        param.uri_args({'task_uuid': tid})
        res = cls.call(tk.WatchersAdd, param, token=token, status_code=code if code else 200)
        return res

    @classmethod
    def add_permission(cls, pid, iid, permission, fid):
        param = {
            "permission_rule": {
                "context_type": "issue_type",
                "context_param": {
                    "project_uuid": pid,
                    "issue_type_uuid": iid
                },
                "permission": permission,
                "user_domain_type": "custom_member_fields",
                "user_domain_param": fid
            }
        }
        param = generate_param(param)[0]
        return cls.call(project.PermissionAdd, param)

    @story('T132953 任务-工作项权限：查看任务权限（自定义单选成员属性）')
    def test_view_task_custom_field8(self, prepare):
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看任务」权限域'):
            perm_uuids = self.get_perm_uuids(permission, project_uuid=prepare['pid'])
            for i in perm_uuids:
                ia.del_issue_permission(i)
        with step('成员A查看任务A'):
            res = self.add_watcher(prepare['tid'], prepare['uid'], token=prepare['utoken'], code=403)
            res.check_response('errcode', 'PermissionDenied.ViewTasks')
        with step('项目管理员将任务的「查看任务」权限域添加示例单选成员'):
            self.add_permission(prepare['pid'], prepare['issue_type_uuid'], permission,
                                prepare['f_uuid_map']['自定义单选成员'])
        with step('成员A查看任务A'):
            self.add_watcher(prepare['tid'], prepare['uid'], token=prepare['utoken'])  # 编辑关注者权限默认是所有人

    @story('T132901 任务-工作项权限：编辑关注者权限（自定义单选成员属性）')
    def test_update_task_watcher_custom_field8(self, prepare):
        permission = 'update_task_watchers'
        with step('项目管理员清空任务的「编辑关注者」工作项状态权限域'):
            perm_uuids = self.get_perm_uuids(permission, project_uuid=prepare['pid'])
            for i in perm_uuids:
                ia.del_issue_permission(i)
        with step('成员A编辑任务A的关注者'):
            self.add_watcher(prepare['tid'], prepare['uid'], token=prepare['utoken'], code=403)
        with step('项目管理员添加任务的「编辑关注者」权限域为示例单选成员'):
            self.add_permission(prepare['pid'], prepare['issue_type_uuid'], permission,
                                prepare['f_uuid_map']['自定义单选成员'])
        with step('成员A再次编辑任务A的关注者'):
            self.add_watcher(prepare['tid'], prepare['uid'], token=prepare['utoken'], code=200)

    @story('T132954 任务-工作项权限：查看任务权限（自定义多选成员属性）')
    def test_view_task_custom_field13(self, prepare):
        permission = 'view_tasks'
        with step('项目管理员清空任务的「查看任务」权限域'):
            perm_uuids = self.get_perm_uuids(permission, project_uuid=prepare['pid'])
            for i in perm_uuids:
                ia.del_issue_permission(i)
        with step('成员A查看任务A'):
            res = self.add_watcher(prepare['tid'], prepare['uid'], token=prepare['utoken'], code=403)
            res.check_response('errcode', 'PermissionDenied.ViewTasks')
        with step('项目管理员将任务的「查看任务」权限域添加示例多选成员'):
            self.add_permission(prepare['pid'], prepare['issue_type_uuid'], permission,
                                prepare['f_uuid_map']['自定义多选成员'])
        with step('成员A查看任务A'):
            self.add_watcher(prepare['tid'], prepare['uid'], token=prepare['utoken'])  # 编辑关注者权限默认是所有人

    @story('T132902 任务-工作项权限：编辑关注者权限（自定义多选成员属性）')
    def test_update_task_watcher_custom_field13(self, prepare):
        permission = 'update_task_watchers'
        with step('项目管理员清空任务的「编辑关注者」工作项状态权限域'):
            perm_uuids = self.get_perm_uuids(permission, project_uuid=prepare['pid'])
            for i in perm_uuids:
                ia.del_issue_permission(i)
        with step('成员A编辑任务A的关注者'):
            self.add_watcher(prepare['tid'], prepare['uid'], token=prepare['utoken'], code=403)
        with step('项目管理员添加任务的「编辑关注者」权限域为示例多选成员'):
            self.add_permission(prepare['pid'], prepare['issue_type_uuid'], permission,
                                prepare['f_uuid_map']['自定义多选成员'])
        with step('成员A再次编辑任务A的关注者'):
            self.add_watcher(prepare['tid'], prepare['uid'], token=prepare['utoken'], code=200)

    @story('T132990 任务-工作项权限：更新任务状态权限（自定义单选成员属性）')
    def test_update_task_status_custom_field8(self, prepare, transition):
        permission = 'transit_tasks'
        with step('项目管理员清空任务的「更新任务状态」权限域'):
            perm_uuids = self.get_perm_uuids(permission, project_uuid=prepare['pid'])
            for i in perm_uuids:
                ia.del_issue_permission(i)
        with step('成员A更新任务A的状态'):
            trigger(prepare['tid'], transition['step1']['uuid'], token=prepare['utoken'], code=403)
        with step('项目管理员将任务的「更新任务状态」权限域添加示例单选成员'):
            self.add_permission(prepare['pid'], prepare['issue_type_uuid'], permission,
                                prepare['f_uuid_map']['自定义单选成员'])
        with step('成员A再次更新任务A的状态'):
            trigger(prepare['tid'], transition['step1']['uuid'], token=prepare['utoken'], code=200)
        with step('后置：重置任务状态-未开始'):
            trigger(prepare['tid'], transition['step2']['uuid'], token=prepare['utoken'])

    @story('T132991 任务-工作项权限：更新任务状态权限（自定义多选成员属性）')
    def test_update_task_status_custom_field13(self, prepare, transition):
        permission = 'transit_tasks'
        with step('项目管理员清空任务的「更新任务状态」权限域'):
            perm_uuids = self.get_perm_uuids(permission, project_uuid=prepare['pid'])
            for i in perm_uuids:
                ia.del_issue_permission(i)
        with step('成员A更新任务A的状态'):
            trigger(prepare['tid'], transition['step1']['uuid'], token=prepare['utoken'], code=403)
        with step('项目管理员将任务的「更新任务状态」权限域添加示例多选成员'):
            self.add_permission(prepare['pid'], prepare['issue_type_uuid'], permission,
                                prepare['f_uuid_map']['自定义多选成员'])
        with step('成员A再次更新任务A的状态'):
            trigger(prepare['tid'], transition['step1']['uuid'], token=prepare['utoken'], code=200)
        with step('后置：重置任务状态-未开始'):
            trigger(prepare['tid'], transition['step2']['uuid'], token=prepare['utoken'])

    @story('T133074 任务-工作项权限：删除任务权限（自定义单选成员属性）')
    def test_delete_task_custom_field8(self, prepare):
        permission = 'delete_tasks'
        with step('项目管理员清空任务的「删除任务」权限域'):
            perm_uuids = self.get_perm_uuids(permission, project_uuid=prepare['pid'])
            for i in perm_uuids:
                ia.del_issue_permission(i)
        with step('成员A删除任务'):
            TaskAction.del_task(prepare['tid'], token=prepare['utoken'], status_code='403')
        with step('项目管理员将任务的「删除任务」权限域添加示例单选成员'):
            self.add_permission(prepare['pid'], prepare['issue_type_uuid'], permission,
                                prepare['f_uuid_map']['自定义单选成员'])
        with step('成员A再次删除任务'):
            TaskAction.del_task(prepare['tid'], token=prepare['utoken'], status_code='200')

    @story('T133075 任务-工作项权限：删除任务权限（自定义多选成员属性）')
    def test_delete_task_custom_field13(self, prepare):
        permission = 'delete_tasks'
        with step('项目管理员清空任务的「删除任务」权限域'):
            perm_uuids = self.get_perm_uuids(permission, project_uuid=prepare['pid'])
            for i in perm_uuids:
                ia.del_issue_permission(i)
        with step('成员A删除任务'):
            TaskAction.del_task(prepare['tasks'][1], token=prepare['utoken'], status_code='403')
        with step('项目管理员将任务的「删除任务」权限域添加示例多选成员'):
            self.add_permission(prepare['pid'], prepare['issue_type_uuid'], permission,
                                prepare['f_uuid_map']['自定义多选成员'])
        with step('成员A再次删除任务'):
            TaskAction.del_task(prepare['tasks'][1], token=prepare['utoken'], status_code='200')

    @story('T142123 子任务-工作项权限：查看子任务权限（自定义单选成员属性')
    def test_view_sub_task_custom_field8(self, prepare):
        permission = 'view_tasks'
        with step('项目管理员清空子任务的「查看子任务」权限域'):
            perm_uuids = self.get_perm_uuids(permission, project_uuid=prepare['pid'], it_name='子任务')
            for i in perm_uuids:
                ia.del_issue_permission(i)
        with step('成员A查看子任务A'):
            res = self.add_watcher(prepare['sub_tasks'][0], prepare['uid'], token=prepare['utoken'], code=403)
            res.check_response('errcode', 'PermissionDenied.ViewTasks')
        with step('项目管理员将子任务的「查看子任务」权限域添加示例单选成员'):
            self.add_permission(prepare['pid'], prepare['s_it_uuid'], permission,
                                prepare['f_uuid_map']['自定义单选成员'])
        with step('成员A查看子任务A'):
            self.add_watcher(prepare['sub_tasks'][0], prepare['uid'], token=prepare['utoken'])  # 编辑关注者权限默认是所有人

    @story('T142071 子任务-工作项权限：编辑关注者权限（自定义单选成员属性）')
    def test_update_sub_task_watcher_custom_field8(self, prepare):
        permission = 'update_task_watchers'
        with step('项目管理员清空子任务的「编辑关注者」工作项状态权限域'):
            perm_uuids = self.get_perm_uuids(permission, project_uuid=prepare['pid'], it_name='子任务')
            for i in perm_uuids:
                ia.del_issue_permission(i)
        with step('成员A编辑子任务A的关注者'):
            self.add_watcher(prepare['sub_tasks'][0], prepare['uid'], token=prepare['utoken'], code=403)
        with step('项目管理员添加子任务的「编辑关注者」权限域为示例单选成员'):
            self.add_permission(prepare['pid'], prepare['s_it_uuid'], permission,
                                prepare['f_uuid_map']['自定义单选成员'])
        with step('成员A再次编辑子任务A的关注者'):
            self.add_watcher(prepare['sub_tasks'][0], prepare['uid'], token=prepare['utoken'], code=200)

    @story('T142124 子任务-工作项权限：查看子任务权限（自定义多选成员属性）')
    def test_view_sub_task_custom_field13(self, prepare):
        permission = 'view_tasks'
        with step('项目管理员清空子任务的「查看子任务」权限域'):
            perm_uuids = self.get_perm_uuids(permission, project_uuid=prepare['pid'], it_name='子任务')
            for i in perm_uuids:
                ia.del_issue_permission(i)
        with step('成员A查看子任务A'):
            res = self.add_watcher(prepare['sub_tasks'][0], prepare['uid'], token=prepare['utoken'], code=403)
            res.check_response('errcode', 'PermissionDenied.ViewTasks')
        with step('项目管理员将子任务的「查看子任务」权限域添加示例多选成员'):
            self.add_permission(prepare['pid'], prepare['s_it_uuid'], permission,
                                prepare['f_uuid_map']['自定义多选成员'])
        with step('成员A查看子任务A'):
            self.add_watcher(prepare['sub_tasks'][0], prepare['uid'], token=prepare['utoken'])  # 编辑关注者权限默认是所有人

    @story('T142072 子任务-工作项权限：编辑关注者权限（自定义多选成员属性）')
    def test_update_sub_task_watcher_custom_field13(self, prepare):
        permission = 'update_task_watchers'
        with step('项目管理员清空子任务的「编辑关注者」工作项状态权限域'):
            perm_uuids = self.get_perm_uuids(permission, project_uuid=prepare['pid'], it_name='子任务')
            for i in perm_uuids:
                ia.del_issue_permission(i)
        with step('成员A编辑子任务A的关注者'):
            self.add_watcher(prepare['sub_tasks'][0], prepare['uid'], token=prepare['utoken'], code=403)
        with step('项目管理员添加子任务的「编辑关注者」权限域为示例多选成员'):
            self.add_permission(prepare['pid'], prepare['s_it_uuid'], permission,
                                prepare['f_uuid_map']['自定义多选成员'])
        with step('成员A再次编辑子任务A的关注者'):
            self.add_watcher(prepare['sub_tasks'][0], prepare['uid'], token=prepare['utoken'], code=200)

    @story('T142239 子任务-工作项权限：删除子任务权限（自定义单选成员属性）')
    def test_delete_sub_task_custom_field8(self, prepare):
        permission = 'delete_tasks'
        with step('项目管理员清空任务的「删除子任务」权限域'):
            perm_uuids = self.get_perm_uuids(permission, project_uuid=prepare['pid'], it_name='子任务')
            for i in perm_uuids:
                ia.del_issue_permission(i)
        with step('成员A删除子任务'):
            TaskAction.del_task(prepare['sub_tasks'][0], token=prepare['utoken'], status_code='403')
        with step('项目管理员将任务的「删除子任务」权限域添加示例单选成员'):
            self.add_permission(prepare['pid'], prepare['s_it_uuid'], permission,
                                prepare['f_uuid_map']['自定义单选成员'])
        with step('成员A再次删除子任务'):
            TaskAction.del_task(prepare['sub_tasks'][0], token=prepare['utoken'], status_code='200')

    @story('T142240 子任务-工作项权限：删除子任务权限（自定义多选成员属性）')
    def test_delete_sub_task_custom_field13(self, prepare):
        permission = 'delete_tasks'
        with step('项目管理员清空任务的「删除子任务」权限域'):
            perm_uuids = self.get_perm_uuids(permission, project_uuid=prepare['pid'], it_name='子任务')
            for i in perm_uuids:
                ia.del_issue_permission(i)
        with step('成员A删除子任务'):
            TaskAction.del_task(prepare['sub_tasks'][1], token=prepare['utoken'], status_code='403')
        with step('项目管理员将子任务的「删除子任务」权限域添加示例多选成员'):
            self.add_permission(prepare['pid'], prepare['s_it_uuid'], permission,
                                prepare['f_uuid_map']['自定义多选成员'])
        with step('成员A再次删除子任务'):
            TaskAction.del_task(prepare['sub_tasks'][1], token=prepare['utoken'], status_code='200')
