# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_issue_post_action.py
@Author  ：zhangyonghui@ones.ai
@Date    ：7/25/22 3:44 PM 
@Desc    ：配置中心-工作项工作流-后置动作
"""
from falcons.check import Checker, go
from falcons.com.nick import feature, fixture, story, step, mark
from falcons.helper import mocks

from main.actions.issue import IssueAction as Ia
from main.actions.member import MemberAction
from main.actions.prodcut import ProductAction
from main.actions.sprint import team_stamp
from main.actions.task import TaskAction
from main.api.const.notice_type import SysNoticeType
from main.api.project import TeamStampData
from main.params import issue, data, conf
from main.api import third, project
from main.params.third import add_sub_department

notice_types = [
    SysNoticeType.EMAIL,
    SysNoticeType.THIRD_7
]


@fixture(scope='module', autouse=True)
def task_issue_data():
    issue_type_uuid = TaskAction.issue_type_uuid()[0]
    s_param = issue.show_issue_list()[0]
    resp = go(TeamStampData, s_param)
    transition_uuids = [r['default_configs']['default_transitions'] for r in resp.value('issue_type.issue_types')
                        if r['name'] == '任务'][0]
    transition_uuid = [r['uuid'] for r in transition_uuids if r['name'] == '开始任务'][0]
    da = {'issue_type_uuid': issue_type_uuid, 'transition_uuid': transition_uuid}
    return da


@fixture(scope='module', autouse=True)
def sub_task_issue_data():
    issue_type_uuid = TaskAction.issue_type_uuid(issue_types='子任务')[0]
    s_param = issue.show_issue_list()[0]
    resp = go(TeamStampData, s_param)
    transition_uuids = [r['default_configs']['default_transitions'] for r in resp.value('issue_type.issue_types')
                        if r['name'] == '子任务'][0]
    transition_uuid = [r['uuid'] for r in transition_uuids if r['name'] == '开始任务'][0]
    da = {'issue_type_uuid': issue_type_uuid, 'transition_uuid': transition_uuid}
    return da


@fixture(scope='module', autouse=True)
def create_product():
    """创建产品"""
    product_uuid = ProductAction.product_add().value('item.uuid')
    return product_uuid


@fixture(scope='module', autouse=True)
def clear_product(create_product, task_issue_data, sub_task_issue_data):
    yield
    """删除产品"""
    ProductAction.product_del('product-' + create_product)

    # 清除后置动作数据
    post_function = []

    Ia.global_add_post_action(post_function=post_function,
                              issue_type_uuid=task_issue_data['issue_type_uuid'],
                              transition_uuid=task_issue_data['transition_uuid'])

    Ia.global_add_post_action(post_function=post_function,
                              issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                              transition_uuid=sub_task_issue_data['transition_uuid'])


@mark.smoke
@feature('配置中心-工作项-后置动作')
class TestGlobalPostAction(Checker):

    @story('T130185 后置动作：添加更新属性后置动作（进度）-子任务')
    def test_sub_task_post_action_progress(self, sub_task_issue_data):
        with step('后置动作：添加更新属性后置动作（进度）'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": "field033",
                        "value": 5000000,  # 进度50%
                        "type": 4,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

    @story('T130179 后置动作：添加更新属性后置动作（进度）-任务')
    def test_task_post_action_progress(self, task_issue_data):
        with step('后置动作：添加更新属性后置动作（进度）'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": "field033",
                        "value": 5000000,  # 进度50%
                        "type": 4,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

    @story('T130214 后置动作：添加更新属性后置动作（所属产品）-任务')
    def test_task_add_post_action_notice_field_product(self, create_product, task_issue_data):
        with step('后置动作：添加更新属性后置动作（所属产品'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": "field029",
                        "value": [
                            create_product
                        ],
                        "type": 44,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

    @story('T130201 后置动作：添加更新属性后置动作（所属产品）-子任务')
    def test_sub_task_add_post_action_notice_field_product(self, create_product, sub_task_issue_data):
        with step('后置动作：添加更新属性后置动作（所属产品'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": "field029",
                        "value": [
                            create_product
                        ],
                        "type": 44,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

    @story('T130109 后置动作：添加发送通知后置动作（特殊角色：项目管理员）-子任务')
    def test_sub_task_post_action_project_administrators(self, sub_task_issue_data):
        with step('添加发送通知后置动作（特殊角色：项目管理员）'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
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
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

    @story('T130061 后置动作：添加发送通知后置动作（特殊角色：所有人）--任务')
    def test_task_post_action_everyone(self, task_issue_data):
        with step('添加发送通知后置动作（特殊角色：所有人）'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
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
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

    @story('T130062 后置动作：添加发送通知后置动作（特殊角色：所有人）--子任务')
    def test_sub_task_post_action_everyone(self, sub_task_issue_data):
        with step('后置动作：添加发送通知后置动作（特殊角色：所有人'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
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
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

    @story('T130075 后置动作：添加发送通知后置动作（特殊角色：项目负责人）--子任务')
    def test_sub_task_post_action_project_assign(self, sub_task_issue_data):
        with step('后置动作：添加发送通知后置动作（特殊角色：所有人'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
                        "user_domains": [
                            {
                                "user_domain_type": "project_assign",
                                "user_domain_param": ""
                            }
                        ],
                        "field_uuids": [],
                        "expandedDomainList": [
                            {
                                "user_domain_type": "project_assign",
                                "user_domain_param": "",
                                "type": "project_assign",
                                "members": [],
                                "tag": "特殊角色",
                                "name": "项目负责人",
                                "subText": None
                            }
                        ]
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

    @story('T130076 后置动作：添加发送通知后置动作（特殊角色：项目负责人）--任务')
    def test_task_post_action_project_assign(self, task_issue_data):
        with step('后置动作：添加发送通知后置动作（特殊角色：所有人'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
                        "user_domains": [
                            {
                                "user_domain_type": "project_assign",
                                "user_domain_param": ""
                            }
                        ],
                        "field_uuids": [],
                        "expandedDomainList": [
                            {
                                "user_domain_type": "project_assign",
                                "user_domain_param": "",
                                "type": "project_assign",
                                "members": [],
                                "tag": "特殊角色",
                                "name": "项目负责人",
                                "subText": None
                            }
                        ]
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

    @story('T129916 后置动作：添加发送通知后置动作（部门）')
    def test_global_add_post_action_notice_department(self, task_issue_data):
        # 新增部门
        param = add_sub_department()[0]
        resp = self.call(third.ADDSubDepartment, param)
        depart_uuid = resp.json()['add_department']['uuid']
        with step('添加发送通知后置动作（部门）'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
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
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])
        with step('清除部门数据'):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story('T129950 后置动作：添加发送通知后置动作（成员）')
    def test_global_add_post_action_notice_member(self, task_issue_data):
        with step('创建一个成员'):
            m = MemberAction.new_member()
        member_uuid = m.owner_uuid
        with step('添加发送通知后置动作（成员)'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
                        "user_domains": [
                            {
                                "user_domain_type": "single_user",
                                "user_domain_param": member_uuid
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])
        with step('删除成员'):
            MemberAction.del_member(member_uuid)

    @story('T129970 后置动作：添加发送通知后置动作（角色）')
    def test_global_add_post_action_notice_role(self, task_issue_data):
        with step('添加发送通知后置动作（成员)'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
                        "user_domains": [
                            {
                                "user_domain_type": "project_administrators",  # 角色 项目管理员
                                "user_domain_param": ""
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]

        Ia.global_add_post_action(post_function=post_function,
                                  issue_type_uuid=task_issue_data['issue_type_uuid'],
                                  transition_uuid=task_issue_data['transition_uuid'])

    @story('129996 后置动作：添加发送通知后置动作（特殊角色：工作项创建者）-子任务')
    def test_global_sub_task_add_post_action_notice_task_owner(self, sub_task_issue_data):
        with step('添加发送通知后置动作（成员)'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
                        "user_domains": [
                            {
                                "user_domain_type": "task_owner",  # 特殊角色：工作项创建者
                                "user_domain_param": ""
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]

        Ia.global_add_post_action(post_function=post_function,
                                  issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                  transition_uuid=sub_task_issue_data['transition_uuid'])

    @story('129979 后置动作：添加发送通知后置动作（特殊角色：工作项创建者）-任务')
    def test_global_task_add_post_action_notice_task_owner(self, task_issue_data):
        with step('添加发送通知后置动作（成员)'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
                        "user_domains": [
                            {
                                "user_domain_type": "task_owner",  # 特殊角色：工作项创建者
                                "user_domain_param": ""
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]

        Ia.global_add_post_action(post_function=post_function,
                                  issue_type_uuid=task_issue_data['issue_type_uuid'],
                                  transition_uuid=task_issue_data['transition_uuid'])

    @story('130001 后置动作：添加发送通知后置动作（特殊角色：工作项负责人）-任务')
    def test_global_task_add_post_action_notice_task_assign(self, task_issue_data):
        with step('添加发送通知后置动作（成员)'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
                        "user_domains": [
                            {
                                "user_domain_type": "task_assign",  # 特殊角色：工作项负责人
                                "user_domain_param": ""
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]

        Ia.global_add_post_action(post_function=post_function,
                                  issue_type_uuid=task_issue_data['issue_type_uuid'],
                                  transition_uuid=task_issue_data['transition_uuid'])

    @story('130015 后置动作：添加发送通知后置动作（特殊角色：工作项负责人）-子任务')
    def test_global_sub_task_add_post_action_notice_task_assign(self, sub_task_issue_data):
        with step('添加发送通知后置动作（成员)'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
                        "user_domains": [
                            {
                                "user_domain_type": "task_assign",  # 特殊角色：工作项负责人
                                "user_domain_param": ""
                            }
                        ],
                        "field_uuids": []
                    }
                }
            ]

            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

    @story('130030 后置动作：添加发送通知后置动作（特殊角色：工作项关注者）')
    def test_global_sub_task_add_post_action_notice_task_watchers(self, sub_task_issue_data):
        with step('添加发送通知后置动作（成员)'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
                        "user_domains": [
                            {
                                "user_domain_type": "task_watchers",
                                "user_domain_param": ""
                            }
                        ],
                        "field_uuids": [],
                        "expandedDomainList": [
                            {
                                "user_domain_type": "task_watchers",
                                "user_domain_param": "",
                                "type": "task_watchers",
                                "members": [],
                                "tag": "特殊角色",
                                "name": "工作项关注者",
                                "subText": None
                            }
                        ]
                    }
                }
            ]

        Ia.global_add_post_action(post_function=post_function,
                                  issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                  transition_uuid=sub_task_issue_data['transition_uuid'])

    @story('130092 后置动作：添加发送通知后置动作（特殊角色：项目管理员）')
    def test_global_sub_task_add_post_action_notice_project_administrators(self, sub_task_issue_data):
        with step('添加发送通知后置动作（成员)'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
                        "user_domains": [
                            {
                                "user_domain_type": "project_administrators",
                                "user_domain_param": ""
                            }
                        ],
                        "field_uuids": [],
                        "expandedDomainList": [
                            {
                                "user_domain_type": "project_administrators",
                                "user_domain_param": "",
                                "type": "project_administrators",
                                "members": [],
                                "tag": "特殊角色",
                                "name": "项目管理员",
                                "subText": None
                            }
                        ]
                    }
                }
            ]

        Ia.global_add_post_action(post_function=post_function,
                                  issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                  transition_uuid=sub_task_issue_data['transition_uuid'])

    @story('130114后置动作：添加发送通知后置动作（用户组）-子任务')
    def test_global_sub_task_add_post_action_notice_group(self, sub_task_issue_data):
        # 新增用户组
        param = data.user_group_add()[0]
        resp = go(project.UsesGroupAdd, param)
        name = resp.value('name')
        name_pinyin = resp.value('name_pinyin')
        group_uuid = resp.value('uuid')
        with step('添加发送通知后置动作（成员)'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
                        "user_domains": [
                            {
                                "user_domain_type": "group",
                                "user_domain_param": group_uuid
                            }
                        ],
                        "field_uuids": [],
                        "expandedDomainList": [
                            {
                                "user_domain_type": "group",
                                "user_domain_param": group_uuid,
                                "type": "group",
                                "group": {
                                    "uuid": group_uuid,
                                    "name": name,
                                    "name_pinyin": name_pinyin,
                                    "desc": "",
                                    "create_time": 0,
                                    "members": []
                                },
                                "members": [],
                                "tag": "用户组",
                                "name": name,
                                "subText": "0人"
                            }
                        ]
                    }
                }
            ]

        Ia.global_add_post_action(post_function=post_function,
                                  issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                  transition_uuid=sub_task_issue_data['transition_uuid'])


@feature('配置中心-工作项-后置动作更新属性')
class TestGlobalPostActionField(Checker):

    @story('T130277 后置动作：添加更新属性后置动作（自定义单选成员）-任务')
    @story('T130296 后置动作：添加更新属性后置动作（自定义单选成员）（从其他单选成员属性拷贝）-子任务')
    def test_sub_task_post_action_radio_member(self, sub_task_issue_data, task_issue_data):
        with step('前置条件'):
            field_uuid = Ia.global_add_field(field_type=8, issue_type=[sub_task_issue_data['issue_type_uuid'],
                                                                       task_issue_data['issue_type_uuid']])
        with step('添加更新属性后置动作（自定义单选成员）-子任务'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": field_uuid,
                        "value": None,
                        "type": 8,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

        with step('添加更新属性后置动作（自定义单选成员）-任务'):
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(sub_task_issue_data['issue_type_uuid'], field_uuid)
            Ia.del_issue_field(task_issue_data['issue_type_uuid'], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T130144 后置动作：添加发送通知后置动作（自定义单选成员属性）-任务')
    @story('T130150 后置动作：添加发送通知后置动作（自定义单选成员属性）-子任务')
    def test_sub_task_post_action_field(self, sub_task_issue_data, task_issue_data):
        with step('前置条件'):
            field_uuid = Ia.global_add_field(field_type=8, issue_type=[sub_task_issue_data['issue_type_uuid'],
                                                                       task_issue_data['issue_type_uuid']])
        with step('添加发送通知后置动作 （自定义单选成员属性）-子任务'):
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": notice_types,
                        "user_domains": [],
                        "field_uuids": [field_uuid]
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

        with step('添加发送通知后置动作 （自定义单选成员属性）-任务'):
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(sub_task_issue_data['issue_type_uuid'], field_uuid)
            Ia.del_issue_field(task_issue_data['issue_type_uuid'], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T130168 后置动作：添加更新属性后置动作（故事点）-子任务')
    def test_sub_task_post_action_story_field(self, sub_task_issue_data):
        # 将新增属性添加到对应工作项
        Ia.add_field_into_issue(field_type=['field032'], issue_type=[sub_task_issue_data['issue_type_uuid']])
        with step('添加更新属性后置动作（故事点）-子任务'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": "field032",
                        "value": 500000,
                        "type": 4,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(sub_task_issue_data['issue_type_uuid'], 'field032')

    @story('T130164 后置动作：添加更新属性后置动作（故事点）-任务')
    def test_task_post_action_story_field(self, task_issue_data):
        # 将新增属性添加到对应工作项
        Ia.add_field_into_issue(field_type=['field032'], issue_type=[task_issue_data['issue_type_uuid']])
        with step('添加更新属性后置动作（故事点）-任务'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": "field032",
                        "value": 500000,
                        "type": 4,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(task_issue_data['issue_type_uuid'], 'field032')

    @story('T130230 后置动作：添加更新属性后置动作（自定义单行文本-子任务）')
    @story('T130231 后置动作：添加更新属性后置动作（自定义单行文本-任务）')
    def test_task_post_action_single_line(self, sub_task_issue_data, task_issue_data):
        with step('前置条件'):
            field_uuid = Ia.global_add_field(field_type=2, issue_type=[sub_task_issue_data['issue_type_uuid'],
                                                                       task_issue_data['issue_type_uuid']])
        with step('添加更新属性后置动作（自定义单行文本-任务）'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": field_uuid,
                        "value": None,
                        "type": 2,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

        with step('添加更新属性后置动作（自定义单行文本-子任务）'):
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(sub_task_issue_data['issue_type_uuid'], field_uuid)
            Ia.del_issue_field(task_issue_data['issue_type_uuid'], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T130327 后置动作：添加更新属性后置动作（自定义单选迭代）-子任务）')
    @story('T130310 后置动作：添加更新属性后置动作（自定义单选迭代）-任务）')
    def test_task_post_action_single_line(self, sub_task_issue_data, task_issue_data):
        with step('前置条件'):
            field_uuid = Ia.global_add_field(field_type=7, issue_type=[sub_task_issue_data['issue_type_uuid'],
                                                                       task_issue_data['issue_type_uuid']])
        with step('添加更新属性后置动作（自定义单行文本-任务）'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": field_uuid,
                        "value": None,
                        "type": 2,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

        with step('添加更新属性后置动作（自定义单行文本-子任务）'):
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(sub_task_issue_data['issue_type_uuid'], field_uuid)
            Ia.del_issue_field(task_issue_data['issue_type_uuid'], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T130332 后置动作：添加更新属性后置动作（自定义多行文本）-子任务）')
    @story('T130330 后置动作：添加更新属性后置动作（自定义多行文本）-任务）')
    def test_task_post_action_more_line(self, sub_task_issue_data, task_issue_data):
        with step('前置条件'):
            field_uuid = Ia.global_add_field(field_type=15, issue_type=[sub_task_issue_data['issue_type_uuid'],
                                                                        task_issue_data['issue_type_uuid']])

        with step('添加更新属性后置动作（自定义多行文本-任务）'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": field_uuid,
                        "value": None,
                        "type": 2,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

        with step('添加更新属性后置动作（自定义多行文本-子任务）'):
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(sub_task_issue_data['issue_type_uuid'], field_uuid)
            Ia.del_issue_field(task_issue_data['issue_type_uuid'], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T130260 后置动作：添加更新属性后置动作（自定义单选菜单）')
    @story('T130248 后置动作：添加更新属性后置动作（自定义单选菜单）')
    def test_task_post_action_radio_menu(self, sub_task_issue_data, task_issue_data):
        with step('前置条件'):
            options = {
                "value": mocks.num(),
                "background_color": "#307fe2",
                "color": "#fff"
            }
            param = conf.add_issue_type_field()[0]
            param.json_update('field.type', 1)
            param.json_update('field.options', [options])
            res = self.call(project.FieldsAdd, param)
            field_uuid = res.value('field.uuid')

            # 将新增属性添加到对应工作项
            Ia.add_field_into_issue(field_type=[field_uuid], issue_type=[sub_task_issue_data['issue_type_uuid'],
                                                                         task_issue_data['issue_type_uuid']])

        with step('添加更新属性后置动作（自定义单选菜单）'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": field_uuid,
                        "value": None,
                        "type": 1,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

        with step('添加更新属性后置动作（自定义单选菜单）-子任务）'):
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(sub_task_issue_data['issue_type_uuid'], field_uuid)
            Ia.del_issue_field(task_issue_data['issue_type_uuid'], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T130357 后置动作：添加更新属性后置动作（自定义多选菜单）')
    @story('T130352 后置动作：添加更新属性后置动作（自定义多选菜单）')
    def test_task_post_action_more_choice_menu(self, sub_task_issue_data, task_issue_data):
        with step('前置条件'):
            options = {
                "value": mocks.num(),
                "background_color": "#307fe2",
                "color": "#fff"
            }
            param = conf.add_issue_type_field()[0]
            param.json_update('field.type', 16)
            param.json_update('field.options', [options])
            res = self.call(project.FieldsAdd, param)
            field_uuid = res.value('field.uuid')

            # 将新增属性添加到对应工作项
            Ia.add_field_into_issue(field_type=[field_uuid], issue_type=[sub_task_issue_data['issue_type_uuid'],
                                                                         task_issue_data['issue_type_uuid']])
        with step('添加更新属性后置动作（自定义多选菜单）-任务'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": field_uuid,
                        "value": None,
                        "type": 1,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

        with step('添加更新属性后置动作（自定义多选菜单）-子任务）'):
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(sub_task_issue_data['issue_type_uuid'], field_uuid)
            Ia.del_issue_field(task_issue_data['issue_type_uuid'], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T130375 后置动作：添加更新属性后置动作（自定义多选成员）')
    @story('T130381 后置动作：添加更新属性后置动作（自定义多选成员）')
    def test_task_post_action_more_choice_member(self, sub_task_issue_data, task_issue_data):
        with step('前置条件'):
            field_uuid = Ia.global_add_field(field_type=13, issue_type=[sub_task_issue_data['issue_type_uuid'],
                                                                        task_issue_data['issue_type_uuid']])
        with step('添加更新属性后置动作（自定义多选成员）-任务）'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": field_uuid,
                        "value": None,
                        "type": 2,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

        with step('添加更新属性后置动作（自定义多选成员）-子任务）'):
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(sub_task_issue_data['issue_type_uuid'], field_uuid)
            Ia.del_issue_field(task_issue_data['issue_type_uuid'], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T130403 后置动作：添加更新属性后置动作（自定义多选项目）')
    @story('T130414 后置动作：添加更新属性后置动作（自定义多选项目）')
    def test_task_post_action_more_choice_product(self, sub_task_issue_data, task_issue_data):
        with step('前置条件'):
            field_uuid = Ia.global_add_field(field_type=50, issue_type=[sub_task_issue_data['issue_type_uuid'],
                                                                        task_issue_data['issue_type_uuid']])
        with step('添加更新属性后置动作（自定义多选项目-任务）'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": field_uuid,
                        "value": None,
                        "type": 2,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

        with step('添加更新属性后置动作（自定义多选项目-子任务）'):
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(sub_task_issue_data['issue_type_uuid'], field_uuid)
            Ia.del_issue_field(task_issue_data['issue_type_uuid'], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T130435 后置动作：添加更新属性后置动作（自定义浮点数）')
    @story('T130426 后置动作：添加更新属性后置动作（自定义浮点数）')
    def test_task_post_action_floating_point_number(self, sub_task_issue_data, task_issue_data):
        with step('前置条件'):
            field_uuid = Ia.global_add_field(field_type=4, issue_type=[sub_task_issue_data['issue_type_uuid'],
                                                                       task_issue_data['issue_type_uuid']])
        with step('添加更新属性后置动作（自定义多选项目-任务）'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": field_uuid,
                        "value": None,
                        "type": 2,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

        with step('添加更新属性后置动作（自定义多选项目-子任务）'):
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(sub_task_issue_data['issue_type_uuid'], field_uuid)
            Ia.del_issue_field(task_issue_data['issue_type_uuid'], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T130477 后置动作：添加更新属性后置动作（自定义时间）')
    @story('T130475 后置动作：添加更新属性后置动作（自定义时间）')
    def test_task_post_action_time(self, sub_task_issue_data, task_issue_data):
        with step('前置条件'):
            field_uuid = Ia.global_add_field(field_type=6, issue_type=[sub_task_issue_data['issue_type_uuid'],
                                                                       task_issue_data['issue_type_uuid']])
        with step('添加更新属性后置动作（自定义时间）-任务）'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": field_uuid,
                        "value": None,
                        "type": 2,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

        with step('添加更新属性后置动作（自定义时间）-子任务）'):
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(sub_task_issue_data['issue_type_uuid'], field_uuid)
            Ia.del_issue_field(task_issue_data['issue_type_uuid'], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T130461 后置动作：添加更新属性后置动作（自定义日期）')
    @story('T130452 后置动作：添加更新属性后置动作（自定义日期）')
    def test_task_post_action_date(self, sub_task_issue_data, task_issue_data):
        with step('前置条件'):
            field_uuid = Ia.global_add_field(field_type=5, issue_type=[sub_task_issue_data['issue_type_uuid'],
                                                                       task_issue_data['issue_type_uuid']])

        with step('添加更新属性后置动作（自定义日期）-任务）'):
            param = issue.global_post_action()[0]
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": field_uuid,
                        "value": None,
                        "type": 2,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

        with step('添加更新属性后置动作（自定义日期）-子任务）'):
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(sub_task_issue_data['issue_type_uuid'], field_uuid)
            Ia.del_issue_field(task_issue_data['issue_type_uuid'], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T130488 后置动作：添加更新属性后置动作（自定义整数）')
    @story('T130487 后置动作：添加更新属性后置动作（自定义整数）')
    def test_task_post_action_integer(self, sub_task_issue_data, task_issue_data):
        with step('前置条件'):
            field_uuid = Ia.global_add_field(field_type=3, issue_type=[sub_task_issue_data['issue_type_uuid'],
                                                                       task_issue_data['issue_type_uuid']])
        with step('添加更新属性后置动作（自定义日期）-任务）'):
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": field_uuid,
                        "value": None,
                        "type": 2,
                        "value_type": 0
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

        with step('添加更新属性后置动作（自定义日期）-子任务）'):
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(sub_task_issue_data['issue_type_uuid'], field_uuid)
            Ia.del_issue_field(task_issue_data['issue_type_uuid'], field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)


@fixture(scope='module', autouse=True)
def get_status_uuid():
    # 获取工作项状态UUId
    data = {
        "task_status": 0
    }
    resp = team_stamp(data)
    task_uuid = [r['uuid'] for r in resp.value('task_status.task_statuses') if r['name'] == '测试提交'][0]
    return task_uuid


@feature('配置中心-工作项-后置动作-状态联动')
class TestPostActionStatus(Checker):

    @story('T130541 后置动作：添加状态联动后置动作（父工作项）（后置动作验证：无）')
    def test_add_sub_task_post_action_relation_none(self, sub_task_issue_data, get_status_uuid):
        with step('添加状态联动后置动作（父工作项）（后置动作验证：关联工作项）'):
            post_function = [
                {
                    "update_status": {
                        "target": "parent",
                        "target_range": {},
                        "target_status": get_status_uuid,
                        "validation_type": "none",
                        "validation_params": {
                            "params1": "",
                            "params2": ""
                        }
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

    @story('T130530 后置动作：添加状态联动后置动作（父工作项）（后置动作验证：无）')
    def test_add_post_action_relation_none(self, task_issue_data, get_status_uuid):
        with step('添加状态联动后置动作（父工作项）（后置动作验证：关联工作项）'):
            post_function = [
                {
                    "update_status": {
                        "target": "parent",
                        "target_range": {},
                        "target_status": get_status_uuid,
                        "validation_type": "none",
                        "validation_params": {
                            "params1": "",
                            "params2": ""
                        }
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

    @story('T130514 后置动作：添加状态联动后置动作（父工作项）（后置动作验证：关联工作项）')
    def test_add_post_action_relation_issue(self, sub_task_issue_data, get_status_uuid):
        with step('添加状态联动后置动作（父工作项）（后置动作验证：关联工作项）'):
            post_function = [
                {
                    "update_status": {
                        "target": "parent",
                        "target_range": {},
                        "target_status": get_status_uuid,
                        "validation_type": "related",
                        "validation_params": {
                            "param_1": "",
                            "param_2": ""
                        }
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

    @story('T130565 后置动作：添加状态联动后置动作（父工作项）（后置动作验证：子工作项）')
    def test_add_sub_task_post_action_relation_sub_issue(self, sub_task_issue_data, get_status_uuid):
        with step('添加状态联动后置动作（父工作项）（后置动作验证：子工作项）'):
            post_function = [
                {
                    "update_status": {
                        "target": "parent",
                        "target_range": {},
                        "target_status": get_status_uuid,
                        "validation_type": "parent",
                        "validation_params": {
                            "param_1": "",
                            "param_2": ""
                        }
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

    @story('T130561 后置动作：添加状态联动后置动作（父工作项）（后置动作验证：子工作项）')
    def test_add_task_post_action_relation_sub_issue(self, task_issue_data, get_status_uuid):
        with step('添加状态联动后置动作（父工作项）（后置动作验证：子工作项）'):
            post_function = [
                {
                    "update_status": {
                        "target": "parent",
                        "target_range": {},
                        "target_status": get_status_uuid,
                        "validation_type": "parent",
                        "validation_params": {
                            "param_1": "",
                            "param_2": ""
                        }
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

    @story('T130625 后置动作：添加状态联动后置动作（全部关联工作项）（后置动作验证：关联工作项）')
    def test_add_sub_task_post_action_relation_sub_issue1(self, sub_task_issue_data, get_status_uuid):
        with step('添加状态联动后置动作（父工作项）（后置动作验证：子工作项）'):
            post_function = [
                {
                    "update_status": {
                        "target": "related",
                        "target_range": {
                            "links": [],
                            "issue_types": [],
                            "statuses": []
                        },
                        "target_status": get_status_uuid,
                        "validation_type": "related",
                        "validation_params": {
                            "param_1": "",
                            "param_2": ""
                        }
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

    @story('T130654 后置动作：添加状态联动后置动作（全部关联工作项）（后置动作验证：无）')
    def test_add_task_post_action_all_relation_issue(self, task_issue_data, get_status_uuid):
        with step('添加状态联动后置动作（父工作项）（后置动作验证：子工作项）'):
            post_function = [
                {
                    "update_status": {
                        "target": "related",
                        "target_range": {
                            "links": [],
                            "issue_types": [],
                            "statuses": []
                        },
                        "target_status": get_status_uuid,
                        "validation_type": "none",
                        "validation_params": {
                            "params1": "",
                            "params2": ""
                        }
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=task_issue_data['issue_type_uuid'],
                                      transition_uuid=task_issue_data['transition_uuid'])

    @story('T130655 后置动作：添加状态联动后置动作（全部关联工作项）（后置动作验证：无）')
    def test_add_sub_task_post_action_all_relation_issue(self, sub_task_issue_data, get_status_uuid):
        with step('添加状态联动后置动作（父工作项）（后置动作验证：子工作项）'):
            post_function = [
                {
                    "update_status": {
                        "target": "related",
                        "target_range": {
                            "links": [],
                            "issue_types": [],
                            "statuses": []
                        },
                        "target_status": get_status_uuid,
                        "validation_type": "none",
                        "validation_params": {
                            "params1": "",
                            "params2": ""
                        }
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

    @story('T130681 后置动作：添加状态联动后置动作（全部关联工作项）（后置动作验证：子工作项）')
    def test_add_sub_task_post_action_all_relation_issue_sub_issue(self, sub_task_issue_data, get_status_uuid):
        with step('添加状态联动后置动作（全部关联工作项）（后置动作验证：子工作项）'):
            post_function = [
                {
                    "update_status": {
                        "target": "related",
                        "target_range": {
                            "links": [],
                            "issue_types": [],
                            "statuses": []
                        },
                        "target_status": get_status_uuid,
                        "validation_type": "parent",
                        "validation_params": {
                            "param_1": "",
                            "param_2": ""
                        }
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])

    @story('T130740 后置动作：添加状态联动后置动作（特定关联工作项）（后置动作验证：无）')
    def test_add_sub_task_post_action_all_relation_issue_none(self, sub_task_issue_data, get_status_uuid):
        with step('添加状态联动后置动作（全部关联工作项）（后置动作验证：子工作项）'):
            post_function = [
                {
                    "update_status": {
                        "target": "related",
                        "target_range": {
                            "links": [
                                {
                                    "desc_type": "link_out_desc",
                                    "uuid": "UUID0001"
                                }
                            ],
                            "issue_types": [
                                sub_task_issue_data['issue_type_uuid']
                            ],
                            "statuses": [
                                get_status_uuid
                            ]
                        },
                        "target_status": get_status_uuid,
                        "validation_type": "parent",
                        "validation_params": {
                            "param_1": "",
                            "param_2": ""
                        }
                    }
                }
            ]
            Ia.global_add_post_action(post_function=post_function,
                                      issue_type_uuid=sub_task_issue_data['issue_type_uuid'],
                                      transition_uuid=sub_task_issue_data['transition_uuid'])
