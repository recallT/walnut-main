"""
@Desc：项目设置-任务-步骤-后置动作-发送通知（邮件）
@Author  ：zhangweiyu@ones.ai
"""
import time
from falcons.check import Checker
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture, step, parametrize, mark

from main.actions.member import MemberAction
from main.api import project, third
from main.params import data, third as t
from main.helper.extra import Extra
from main.cases.scene.project.config.workflow import get_start_step, update_post_action, get_default_role, \
    add_custom_field


@fixture(scope='module', autouse=True)
def add_project():
    # 创建一个单独项目
    time.sleep(2)
    creator = Extra(ApiMeta)
    project_uuid = creator.new_project(f'ApiTest-SubTask-SPA')
    return project_uuid


@fixture(scope='module', autouse=True)
def del_project(add_project):
    yield
    # 清除项目数据
    creator = Extra(ApiMeta)
    creator.del_project(add_project)


@fixture(scope='module')
def users():
    users = []
    count = 1
    for i in range(count):
        time.sleep(2)
        user = MemberAction.new_member()
        users.append(user)
    yield users
    for u in users:
        MemberAction.del_member(u.uuid)


label = ApiMeta.env.label


@mark.smoke
@mark.skipif(label == 'saas', reason='saas环境跳过发送通知')
@feature('项目设置--步骤-后置动作-发送通知-添加')
class TestPrjTaskPostActionNotice(Checker):

    @story('T129930 任务-后置动作：添加发送通知后置动作（部门）')
    @story('T129914 子任务-后置动作：添加发送通知后置动作（部门）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_department(self, add_project, typ):
        with step('添加发送通知后置动作（部门）'):
            # 新建部门
            param = t.add_sub_department()[0]
            resp = self.call(third.ADDSubDepartment, param)
            depart_uuid = resp.value('add_department.uuid')
            # 更新后置动作
            start_step = get_start_step(add_project, issue_type_name=typ)
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": [
                            "email"
                        ],
                        "user_domains": [
                            {
                                "user_domain_type": "department",  # department
                                "user_domain_param": depart_uuid  # 部门Id
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]
            add_res = update_post_action(start_step, post_function)
            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('清除部门数据'):
            param2 = t.del_department()[0]
            param2.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param2, with_json=False)
        with step('清除后置动作'):
            update_post_action(start_step, [])

    @story('T129959 任务-后置动作：添加发送通知后置动作（角色）')
    @story('T129974 子任务-后置动作：添加发送通知后置动作（角色）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_role(self, add_project, typ):
        with step('添加发送通知后置动作（角色）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": [
                            "email"
                        ],
                        "user_domains": [
                            {
                                "user_domain_type": "role",  # 角色 项目成员
                                "user_domain_param": get_default_role(add_project)  # 项目默认角色：项目成员
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]
            add_res = update_post_action(start_step, post_function)

            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('清除后置动作'):
            update_post_action(start_step, [])

    @story('T129980 任务-后置动作：添加发送通知后置动作（特殊角色：工作项创建者）')
    @story('T129991 子任务-后置动作：添加发送通知后置动作（特殊角色：工作项创建者）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_task_owner(self, add_project, typ):
        with step('添加发送通知后置动作（特殊角色：工作项创建者）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": [
                            "email"
                        ],
                        "user_domains": [
                            {
                                "user_domain_type": "task_owner",
                                "user_domain_param": ""
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]

            add_res = update_post_action(start_step, post_function)
            add_res.check_response('transition.uuid', start_step['uuid'])

        with step('清除后置动作'):
            update_post_action(start_step, [])

    @story('T130012 任务-后置动作：添加发送通知后置动作（特殊角色：工作项负责人）')
    @story('T130003 子任务-后置动作：添加发送通知后置动作（特殊角色：工作项负责人）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_task_assign(self, add_project, typ):
        with step('添加发送通知后置动作（特殊角色：工作项负责人）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": [
                            "email"
                        ],
                        "user_domains": [
                            {
                                "user_domain_type": "task_assign",
                                "user_domain_param": ""
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]
            add_res = update_post_action(start_step, post_function)
            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('清除后置动作'):
            update_post_action(start_step, [])

    @story('T130026 任务-后置动作：添加发送通知后置动作（特殊角色：工作项关注者）')
    @story('T130025 子任务-后置动作：添加发送通知后置动作（特殊角色：工作项关注者）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_task_watcher(self, add_project, typ):
        with step('添加发送通知后置动作（特殊角色：工作项关注者）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": [
                            "email"
                        ],
                        "user_domains": [
                            {
                                "user_domain_type": "task_watchers",
                                "user_domain_param": ""
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]
            add_res = update_post_action(start_step, post_function)

            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('清除后置动作'):
            update_post_action(start_step, [])

    @story('T130083 任务-后置动作：添加发送通知后置动作（特殊角色：项目负责人）')
    @story('T130082 子任务-后置动作：添加发送通知后置动作（特殊角色：项目负责人）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_project_assign(self, add_project, typ):
        with step('添加发送通知后置动作（特殊角色：项目负责人）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": [
                            "email"
                        ],
                        "user_domains": [
                            {
                                "user_domain_type": "project_assign",
                                "user_domain_param": ""
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]
            add_res = update_post_action(start_step, post_function)

            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('清除后置动作'):
            update_post_action(start_step, [])

    @story('T130097 任务-后置动作：添加发送通知后置动作（特殊角色：项目管理员）')
    @story('T130093 子任务-后置动作：添加发送通知后置动作（特殊角色：项目管理员）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_project_administrators(self, add_project, typ):
        with step('添加发送通知后置动作（特殊角色：项目管理员）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": [
                            "email"
                        ],
                        "user_domains": [
                            {
                                "user_domain_type": "project_administrators",
                                "user_domain_param": ""
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]
            add_res = update_post_action(start_step,
                                         post_function)

            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('清除后置动作'):
            update_post_action(start_step, [])

    @story('T130050 任务-后置动作：添加发送通知后置动作（特殊角色：所有人）')
    @story('T130055 子任务-后置动作：添加发送通知后置动作（特殊角色：所有人）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_everyone(self, add_project, typ):
        with step('添加发送通知后置动作（特殊角色：所有人）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": [
                            "email"
                        ],
                        "user_domains": [
                            {
                                "user_domain_type": "everyone",
                                "user_domain_param": ""
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]
            add_res = update_post_action(start_step, post_function)

            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('清除后置动作'):
            update_post_action(start_step, [])

    @story('T130118 任务-后置动作：添加发送通知后置动作（用户组）')
    @story('T130117 子任务-后置动作：添加发送通知后置动作（用户组）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_group(self, add_project, typ):
        with step('添加发送通知后置动作（用户组）'):
            # 新增用户组，同时添加成员
            param = data.user_group_add()[0]
            resp = self.call(project.UsesGroupAdd, param)
            group_uuid = resp.value('uuid')
            start_step = get_start_step(add_project, issue_type_name=typ)
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": [
                            "email"
                        ],
                        "user_domains": [
                            {
                                "user_domain_type": "group",
                                "user_domain_param": group_uuid
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]
            add_res = update_post_action(start_step, post_function)

            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('清除用户组数据'):
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param, with_json=False)
        with step('清除后置动作'):
            update_post_action(start_step, [])

    @story('T130149 任务-后置动作：添加发送通知后置动作（自定义单选成员属性）')
    @story('T130147 子任务-后置动作：添加发送通知后置动作（自定义单选成员属性）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_notice_custom_field8(self, add_project, typ):
        with step('前置操作: 任务-已添加自定义属性'):
            field_uuid = add_custom_field(field_type=8, project_uuid=add_project, issue_type_name=typ)
        with step('添加发送通知后置动作（自定义单选成员属性）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": [
                            "email"
                        ],
                        "user_domains": [],
                        "field_uuids": [field_uuid]
                    }
                }
            ]
            add_res = update_post_action(start_step, post_function)

            add_res.check_response('transition.uuid', start_step['uuid'])

        with step('清除后置动作'):
            update_post_action(start_step, [])
        # with step('清除工作项属性：自定义单选成员'):
        # delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T129940 子任务-后置动作：添加发送通知后置动作（成员）')
    def test_post_action_notice_user(self, add_project, users):
        with step('添加发送通知后置动作（成员）'):
            start_step = get_start_step(add_project, issue_type_name='子任务')
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": [
                            "email"
                        ],
                        "user_domains": [
                            {
                                "user_domain_type": "single_user",
                                "user_domain_param": users[0].uuid
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]
            add_res = update_post_action(start_step, post_function)

            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('清除后置动作'):
            update_post_action(start_step, [])
