"""
@Desc：项目设置-任务-步骤-后置动作-发送通知（邮件）
@Author  ：zhangweiyu@ones.ai
"""
import time

from falcons.check import Checker
from falcons.com.env import User
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture, step, parametrize, mark
from falcons.com.ones import unify_login

from main.actions.member import MemberAction
from main.actions.pro import TeamPermissionAction, ProjPermissionAction, PrjAction
from main.actions.task import TaskAction
from main.api import project, third
from main.environ import DevEnvVars, Preview1EnvVars, Preview2EnvVars, Preview3EnvVars
from main.helper.email_helper import connection
from main.helper.extra import Extra
from main.params import data, third as t
from main.params.const import ACCOUNT
from main.cases.scene.project.config.workflow import update_post_action, trigger_and_check, get_start_step, \
    get_default_role, add_custom_field, \
    wait_email_receive

project_name = 'ApiTest-check'


@fixture(scope='module', autouse=True)
def add_project():
    # 创建一个单独项目
    time.sleep(2)
    creator = Extra(ApiMeta)
    project_uuid = creator.new_project(project_name)

    yield project_uuid
    # 清除项目数据
    creator.del_project(project_uuid)


@fixture(scope='module', autouse=True)
def user_a():
    '''用户A：dev环境使用真实邮箱'''
    custom_email = None
    if ApiMeta.env.host == DevEnvVars.host:
        custom_email = connection.mail_user  # T2075520629@163.com
    manager = MemberAction.new_member(custom_email=custom_email)  # 新建成员接口不稳定
    if not manager.token:
        manager.token = unify_login(manager)
    # A添加团队-项目管理权限：可创建项目
    TeamPermissionAction.add_permission(manager.owner_uuid, user_domain_type='single_user', permission='administer_do')

    yield manager

    MemberAction.del_member(manager.owner_uuid)


data_post_function = [
    {
        "send_email_notice": {
            "notice_types": ["email"],
            "user_domains": [],
            "field_uuids": []
        }
    }
]

ex = Extra(ApiMeta)

label = ApiMeta.env.label


@mark.skipif(label == 'saas', reason='saas环境跳过发送通知')
@feature('项目设置-任务-步骤-后置动作-发送通知（邮件）')
class TestPrjTaskPostActionNotice(Checker):

    def is_env_preview(self):
        if ApiMeta.env.host in [Preview1EnvVars.host, Preview2EnvVars.host, Preview3EnvVars.host]:
            return True
        else:
            return False

    def proj_create_and_autherize(self, creator: User = None, manager: User = None, member: User = None):
        '''项目创建和授权'''
        c_token = None
        if creator.owner_uuid != ACCOUNT.user.owner_uuid:
            creator.token = unify_login(creator)
            c_token = creator.token
        owner_uuid = creator.owner_uuid if creator else None
        pid = PrjAction.new_project(index=1, name=project_name, owner_uuid=owner_uuid,
                                    token=c_token)
        # 授权管理员
        if manager:
            ProjPermissionAction.add_permission('single_user',
                                                permission="manage_project",
                                                user_domain_param=manager.owner_uuid,
                                                project_uuid=pid)
        # 添加项目成员
        if member:
            MemberAction.add_proj_member(member.owner_uuid, project_uuid=pid)

        return pid

    def _check_email(self, _email, pid, it_uuid, task_uuid, status='进行中', pname=project_name):
        if _email:
            content = _email['content']
            assert f'Test Admin 将属性「状态」修改为「{status}」' in content
            assert f'项目名称:' in content
            assert pname in content
            assert f'{ApiMeta.env.host}/project/#/team/{ACCOUNT.user.team_uuid}/project/{pid}/issue_type/{it_uuid}/task/{task_uuid}' in content
        else:
            assert False, '收件超时~'

    @mark.skip(reason='产品缺陷：工单号321188，需被通知的成员属于项目成员')
    @story('T129282 任务-后置动作：检查发送通知后置动作事件（部门）')
    @story('T129281 子任务-后置动作：检查发送通知后置动作事件（部门）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_department(self, add_project, user_a: User, typ):
        with step('添加发送通知后置动作（部门）'):
            # 新建部门
            param = t.add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)
            depart_uuid = resp.value('add_department.uuid')
            # 更新后置动作
            start_step = get_start_step(project_uuid=add_project, issue_type_name=typ)
            post_function = data_post_function
            post_function[0]['send_email_notice']['user_domains'] = [{
                "user_domain_type": "department",  # department
                "user_domain_param": depart_uuid  # 部门Id
            }]
            add_res = update_post_action(start_step, post_function)
            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('添加成员A到部门'):
            param1 = t.update_department()[0]
            param1.json['departments_to_join'].append(depart_uuid)
            param1.json['variables']['selectedUserUUIDs'].append(user_a.owner_uuid)
            param1.json['variables']['selectedDepartments'].append('department003')  # department003:未分配部门
            self.call(third.UpdateDepartment, param1)
        with step('触发后置动作'):
            task_uuid = trigger_and_check(start_step, issue_type_name=typ, is_check_field=False)
        if self.is_env_preview():
            with step('检查A的邮箱'):
                _email = wait_email_receive(receiver=user_a.email, task_uuid=task_uuid)
                self._check_email(_email, start_step['project_uuid'], start_step['issue_type_uuid'], task_uuid)
        with step('清除后置动作'):
            update_post_action(start_step, [])
        with step('清除部门数据'):
            param2 = t.del_department()[0]
            param2.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param2, with_json=False)

    @story('T129297 任务-后置动作：检查发送通知后置动作事件（角色）')
    @story('T129302 子任务-后置动作：检查发送通知后置动作事件（角色）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_role(self, add_project, user_a: User, typ):
        with step('添加项目成员A'):
            MemberAction.add_proj_member(user_a.owner_uuid, project_uuid=add_project)
        with step('添加发送通知后置动作（角色）'):
            start_step = get_start_step(project_uuid=add_project, issue_type_name=typ)
            post_function = data_post_function
            post_function[0]['send_email_notice']['user_domains'] = [
                {
                    "user_domain_type": "role",
                    "user_domain_param": get_default_role(add_project)  # 项目默认角色：项目成员
                }
            ]
            add_res = update_post_action(start_step, post_function)
            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('触发后置动作'):
            task_uuid = trigger_and_check(start_step, issue_type_name=typ, is_check_field=False)
        if self.is_env_preview():
            with step('检查A的邮箱'):
                _email = wait_email_receive(receiver=user_a.email, task_uuid=task_uuid)
                self._check_email(_email, start_step['project_uuid'], start_step['issue_type_uuid'], task_uuid)
        with step('清除后置动作'):
            update_post_action(start_step, [])
        with step('清除项目成员A'):
            MemberAction.del_proj_member([user_a.owner_uuid], project_uuid=add_project)

    @story('T129315 任务-后置动作：检查发送通知后置动作事件（特殊角色：工作项创建者）')
    @story('T129316 子任务-后置动作：检查发送通知后置动作事件（特殊角色：工作项创建者）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_task_owner(self, user_a: User, typ):
        with step('超管创建项目，并授权A为项目管理员和成员'):
            pid = self.proj_create_and_autherize(creator=ACCOUNT.user, manager=user_a, member=user_a)
        with step('超管：添加发送通知后置动作（特殊角色：工作项创建者）'):
            start_step = get_start_step(project_uuid=pid, issue_type_name=typ)
            post_function = data_post_function
            post_function[0]['send_email_notice']['user_domains'] = [
                {
                    "user_domain_type": "task_owner",
                    "user_domain_param": ""
                }
            ]
            add_res = update_post_action(start_step, post_function)
            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('A创建任务，超管触发步骤'):
            task_uuid = trigger_and_check(start_step, issue_type_name=typ, is_check_field=False,
                                          creator=user_a,
                                          operator=ACCOUNT.user)
        if self.is_env_preview():
            with step('检查A的邮箱'):
                _email = wait_email_receive(receiver=user_a.email, task_uuid=task_uuid)
                self._check_email(_email, start_step['project_uuid'], start_step['issue_type_uuid'], task_uuid)
        with step('超管：删除项目'):
            ex.del_project(pid)

    @story('T129325 任务-后置动作：检查发送通知后置动作事件（特殊角色：工作项负责人）')
    @story('T129327 子任务-后置动作：检查发送通知后置动作事件（特殊角色：工作项负责人）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_task_assign(self, add_project, user_a: User, typ):
        with step('添加项目成员A'):
            MemberAction.add_proj_member(user_a.owner_uuid, project_uuid=add_project)
        with step('添加发送通知后置动作（特殊角色：工作项负责人）'):
            start_step = get_start_step(project_uuid=add_project, issue_type_name=typ)
            post_function = data_post_function
            post_function[0]['send_email_notice']['user_domains'] = [
                {
                    "user_domain_type": "task_assign",
                    "user_domain_param": ""
                }
            ]
            add_res = update_post_action(start_step, post_function)
            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('超管创建和触发任务，任务负责人为A'):
            task_uuid = trigger_and_check(start_step, issue_type_name=typ,
                                          field004=user_a.owner_uuid,
                                          is_check_field=False)
        if self.is_env_preview():
            with step('检查A的邮箱'):
                _email = wait_email_receive(receiver=user_a.email, task_uuid=task_uuid)
                self._check_email(_email, start_step['project_uuid'], start_step['issue_type_uuid'], task_uuid)
        with step('清除后置动作'):
            update_post_action(start_step, [])
        with step('清除项目成员A'):
            MemberAction.del_proj_member([user_a.owner_uuid], project_uuid=add_project)

    @story('T129333 任务-后置动作：检查发送通知后置动作事件（特殊角色：工作项关注者）')
    @story('T129336 子任务-后置动作：检查发送通知后置动作事件（特殊角色：工作项关注者）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_task_watcher(self, add_project, user_a, typ):
        with step('添加项目成员A'):
            MemberAction.add_proj_member(user_a.owner_uuid, project_uuid=add_project)
        with step('添加发送通知后置动作（特殊角色：工作项关注者）'):
            start_step = get_start_step(project_uuid=add_project, issue_type_name=typ)
            post_function = data_post_function
            post_function[0]['send_email_notice']['user_domains'] = [
                {
                    "user_domain_type": "task_watchers",
                    "user_domain_param": ""
                }
            ]
            add_res = update_post_action(start_step, post_function)
            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('创建和触发任务，任务关注人为A'):
            task_uuid = trigger_and_check(start_step,
                                          issue_type_name=typ,
                                          watcher_uuid=user_a.owner_uuid,
                                          is_check_field=False)
        if self.is_env_preview():
            with step('检查A的邮箱'):
                _email = wait_email_receive(receiver=user_a.email, task_uuid=task_uuid)
                self._check_email(_email, start_step['project_uuid'], start_step['issue_type_uuid'], task_uuid)
        with step('清除后置动作'):
            update_post_action(start_step, [])
        with step('清除项目成员A'):
            MemberAction.del_proj_member([user_a.owner_uuid], project_uuid=add_project)

    @story('T129361 任务-后置动作：检查发送通知后置动作事件（特殊角色：项目负责人）')
    @story('T129359 子任务-后置动作：检查发送通知后置动作事件（特殊角色：项目负责人）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_project_assign(self, user_a, typ):
        with step('成员A：创建项目（默认项目负责人为创建人），并授权超管'):
            pid = self.proj_create_and_autherize(creator=user_a, manager=ACCOUNT.user, member=ACCOUNT.user)
        with step('超管：添加发送通知后置动作（特殊角色：项目负责人）'):
            start_step = get_start_step(project_uuid=pid, issue_type_name=typ)
            post_function = data_post_function
            post_function[0]['send_email_notice']['user_domains'] = [
                {
                    "user_domain_type": "project_assign",
                    "user_domain_param": ""
                }
            ]
            add_res = update_post_action(start_step, post_function)
            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('超管:创建并触发任务'):
            task_uuid = trigger_and_check(start_step, issue_type_name=typ, is_check_field=False)
        if self.is_env_preview():
            with step('检查A的邮箱'):
                _email = wait_email_receive(receiver=user_a.email, task_uuid=task_uuid)
                self._check_email(_email, start_step['project_uuid'], start_step['issue_type_uuid'], task_uuid)
        with step('超管：删除项目'):
            ex.del_project(pid)

    @story('T129363 任务-后置动作：检查发送通知后置动作事件（特殊角色：项目管理员）')
    @story('T129369 子任务-后置动作：检查发送通知后置动作事件（特殊角色：项目管理员）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_project_administrators(self, user_a, typ):
        with step('超管：创建项目，并授权A为项目管理员'):
            pid = self.proj_create_and_autherize(creator=ACCOUNT.user, manager=user_a)
        with step('超管：添加发送通知后置动作（特殊角色：项目管理员）'):
            start_step = get_start_step(project_uuid=pid, issue_type_name=typ)
            post_function = data_post_function
            post_function[0]['send_email_notice']['user_domains'] = [
                {
                    "user_domain_type": "project_administrators",
                    "user_domain_param": ""
                }
            ]
            add_res = update_post_action(start_step, post_function)

            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('超管: 创建任务并触发任务步骤'):
            task_uuid = trigger_and_check(start_step, issue_type_name=typ, is_check_field=False)
        with step('检查A的邮箱'):
            if self.is_env_preview():
                with step('检查A的邮箱'):
                    _email = wait_email_receive(receiver=user_a.email, task_uuid=task_uuid)
                    self._check_email(_email, start_step['project_uuid'], start_step['issue_type_uuid'], task_uuid)
        with step('超管：删除项目'):
            ex.del_project(pid)

    @mark.skip(reason='产品缺陷：工单号321188，需被通知的成员属于项目成员')
    @story('T129350 任务-后置动作：检查发送通知后置动作事件（特殊角色：所有人）')
    @story('T129346 子任务-后置动作：检查发送通知后置动作事件（特殊角色：所有人）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_everyone(self, add_project, user_a, typ):
        with step('添加发送通知后置动作（特殊角色：所有人）'):
            start_step = get_start_step(project_uuid=add_project, issue_type_name=typ)
            post_function = data_post_function
            post_function[0]['send_email_notice']['user_domains'] = [
                {
                    "user_domain_type": "everyone",
                    "user_domain_param": ""
                }
            ]
            add_res = update_post_action(start_step, post_function)
            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('超管：新建任务，并触发任务步骤'):
            task_uuid = trigger_and_check(start_step, issue_type_name=typ, is_check_field=False)
        with step('检查A的邮箱'):
            if self.is_env_preview():
                with step('检查A的邮箱'):
                    _email = wait_email_receive(receiver=user_a.email, task_uuid=task_uuid)
                    self._check_email(_email, start_step['project_uuid'], start_step['issue_type_uuid'], task_uuid)
        with step('清除后置动作'):
            update_post_action(start_step, [])

    @mark.skip(reason='产品缺陷：工单号321188，需被通知的成员属于项目成员')
    @story('T129374 任务-后置动作：检查发送通知后置动作事件（用户组）')
    @story('T129380 子任务-后置动作：检查发送通知后置动作事件（用户组）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_group(self, add_project, user_a, typ):
        with step('添加发送通知后置动作（用户组）, 用户组中添加成员A'):
            start_step = get_start_step(project_uuid=add_project, issue_type_name=typ)
            # 新增用户组，同时添加成员
            param = data.user_group_add()[0]
            param.json_update('members', [user_a.owner_uuid])
            resp = self.call(project.UsesGroupAdd, param)
            group_uuid = resp.value('uuid')
            post_function = data_post_function
            post_function[0]['send_email_notice']['user_domains'] = [
                {
                    "user_domain_type": "group",
                    "user_domain_param": group_uuid
                }
            ]
            add_res = update_post_action(start_step, post_function)
            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('超管：新建和触发任务'):
            task_uuid = trigger_and_check(start_step, issue_type_name=typ, is_check_field=False)
        with step('检查A的邮箱'):
            if self.is_env_preview():
                with step('检查A的邮箱'):
                    _email = wait_email_receive(receiver=user_a.email, task_uuid=task_uuid)
                    self._check_email(_email, start_step['project_uuid'], start_step['issue_type_uuid'], task_uuid)
        with step('清除用户组数据'):
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param, with_json=False)
        with step('清除后置动作'):
            update_post_action(start_step, [])

    @mark.skip(reason='产品缺陷：工单号321188，需被通知的成员属于项目成员')
    @story('T129393 任务-后置动作：检查发送通知后置动作事件（自定义单选成员属性）')
    @story('T129394 子任务-后置动作：检查发送通知后置动作事件（自定义单选成员属性）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_custom_field8(self, add_project, user_a, typ):
        with step('前置操作: 任务-已添加自定义属性'):
            field_uuid = add_custom_field(field_type=8, project_uuid=add_project, issue_type_name=typ)
        with step('添加发送通知后置动作（自定义单选成员属性）'):
            start_step = get_start_step(project_uuid=add_project, issue_type_name=typ)
            post_function = data_post_function
            post_function[0]['send_email_notice']['field_uuids'] = [field_uuid]
            add_res = update_post_action(start_step, post_function)
            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('新建任务，并更新自定义单选成员为A'):
            # 新建任务
            task_uuid = TaskAction.new_issue(proj_uuid=add_project)[0]
            if typ.startswith('子'):
                task_uuid = TaskAction.new_issue(proj_uuid=add_project,
                                                 parent_uuid=task_uuid,
                                                 issue_type_name=typ,
                                                 )[0]

            TaskAction.update_task_info(task_uuid, info={
                "field_uuid": field_uuid,
                "type": 8,
                "value": user_a.owner_uuid
            })
        with step('触发后置动作'):
            trigger_and_check(start_step, issue_type_name=typ, is_check_field=False)
        with step('检查A的邮箱'):
            if self.is_env_preview():
                with step('检查A的邮箱'):
                    _email = wait_email_receive(receiver=user_a.email, task_uuid=task_uuid)
                    self._check_email(_email, start_step['project_uuid'], start_step['issue_type_uuid'], task_uuid)
        with step('清除后置动作'):
            update_post_action(start_step, [])
        # with step('清除工作项属性：自定义单选成员'):
        # delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T129288 任务-后置动作：检查发送通知后置动作事件（成员）')
    def test_post_action_notice_user(self, add_project, user_a: User):
        typ = '任务'
        with step('添加项目成员A'):
            MemberAction.add_proj_member(user_a.owner_uuid, project_uuid=add_project)
        with step('添加发送通知后置动作（成员）'):
            start_step = get_start_step(project_uuid=add_project, issue_type_name=typ)
            post_function = data_post_function
            post_function[0]['send_email_notice']['user_domains'] = [
                {
                    "user_domain_type": "single_user",
                    "user_domain_param": user_a.owner_uuid  # 项目默认角色：项目成员
                }
            ]
            add_res = update_post_action(start_step, post_function)
            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('触发后置动作'):
            task_uuid = trigger_and_check(start_step, issue_type_name=typ, is_check_field=False)
        if self.is_env_preview():
            with step('检查A的邮箱'):
                _email = wait_email_receive(receiver=user_a.email, task_uuid=task_uuid)
                self._check_email(_email, start_step['project_uuid'], start_step['issue_type_uuid'], task_uuid)
        with step('清除后置动作'):
            update_post_action(start_step, [])
        with step('清除项目成员A'):
            MemberAction.del_proj_member([user_a.owner_uuid], project_uuid=add_project)
