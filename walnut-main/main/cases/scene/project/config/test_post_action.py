# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_post_action.py
@Author  ：zhangyonghui@ones.ai
@Date    ：2022/6/21 3:38 PM 
@Desc    ：工作项-后置动作
"""

from falcons.check import go, Checker
from falcons.com.nick import story, fixture, step, feature, mark
from main.actions.prodcut import ProductAction
from main.actions.sprint import team_stamp
from main.actions.task import TaskAction
from main.api import project, third
from main.api.issue import PostActionUpdate
from main.params import data
from main.params import issue, proj
from main.params.third import add_sub_department
from falcons.com.meta import ApiMeta


@fixture(scope='module', autouse=True)
def issue_data():
    issue_type_uuid = TaskAction.issue_type_uuid()[0]
    resp = TaskAction.get_task_config()
    transition_uuid = [r['uuid'] for r in resp.value('transition.transitions') if
                       r['name'] == '开始任务' and r['issue_type_uuid'] == issue_type_uuid][0]

    da = {'issue_type_uuid': issue_type_uuid, 'transition_uuid': transition_uuid}
    return da


label = ApiMeta.env.label


@mark.skipif(label == 'private' or label == 'dev', reason='环境跳过权限用例')
@feature('项目设置-工作项-后置动作')
class TestPostAction(Checker):

    @story('T129937 后置动作：添加发送通知后置动作（成员）')
    def test_add_post_action_notice(self, issue_data):
        param = issue.post_action()[0]
        param.json_update('transition.uuid', issue_data['transition_uuid'])
        param.json_update('transition.issue_type_uuid', issue_data['issue_type_uuid'])
        # 查询系统内存在的member 成员uuid
        su_param = proj.program_search_user()[0]
        resp_user_uuid = go(project.UsesSearch, su_param).value('users[0].uuid')
        send_email_notice = {
            "send_email_notice": {
                "notice_types": [
                    'email',
                    'third_7'
                ],
                "user_domains": [
                    {
                        "user_domain_type": "single_user",
                        "user_domain_param": resp_user_uuid
                    }
                ],
                "field_uuids": [

                ]
            }
        }
        param.json_update('transition.post_function', [send_email_notice])
        param.uri_args(
            {'issue_type_uuid': issue_data['issue_type_uuid'], 'transition_uuid': issue_data['transition_uuid']})
        resp = self.call(PostActionUpdate, param)
        resp.check_response('transition.uuid', issue_data['transition_uuid'])

    @story('T129942 后置动作：添加发送通知后置动作（成员）-只发邮件')
    def test_add_post_action_notice_email(self, issue_data):
        param = issue.post_action()[0]
        param.json_update('transition.uuid', issue_data['transition_uuid'])
        param.json_update('transition.issue_type_uuid', issue_data['issue_type_uuid'])
        # 查询系统内存在的member 成员uuid
        su_param = proj.program_search_user()[0]
        resp_user_uuid = go(project.UsesSearch, su_param).value('users[0].uuid')
        send_email_notice = {
            "send_email_notice": {
                "notice_types": [
                    'email'
                ],
                "user_domains": [
                    {
                        "user_domain_type": "single_user",
                        "user_domain_param": resp_user_uuid
                    }
                ],
                "field_uuids": [

                ]
            }
        }
        param.json_update('transition.post_function', [send_email_notice])
        param.uri_args(
            {'issue_type_uuid': issue_data['issue_type_uuid'], 'transition_uuid': issue_data['transition_uuid']})
        resp = self.call(PostActionUpdate, param)
        resp.check_response('transition.uuid', issue_data['transition_uuid'])

    @story('T130210 后置动作：添加更新属性后置动作（所属产品）')
    def test_add_post_action_notice_field_product(self, issue_data):
        """创建一个产品"""
        product_uuid = ProductAction.product_add().value('item.uuid')
        with step('后置动作：添加更新属性后置动作（所属产品'):
            param = issue.post_action()[0]
            param.json_update('transition.uuid', issue_data['transition_uuid'])
            param.json_update('transition.issue_type_uuid', issue_data['issue_type_uuid'])
            post_function = [
                {
                    "update_field_value": {
                        "field_uuid": "field029",
                        "value": [
                            product_uuid
                        ],
                        "type": 44,
                        "value_type": 0
                    }
                }
            ]
            param.json_update('transition.post_function', post_function)
            param.uri_args(
                {'issue_type_uuid': issue_data['issue_type_uuid'], 'transition_uuid': issue_data['transition_uuid']})
            resp = self.call(PostActionUpdate, param)
            resp.check_response('transition.uuid', issue_data['transition_uuid'])
        with step('清除产品数据'):
            ProductAction.product_del('product-' + product_uuid)

    @story('T129975 后置动作：添加发送通知后置动作（角色）')
    def test_add_post_action_notice_role(self, issue_data):
        param = issue.post_action()[0]
        param.json_update('transition.uuid', issue_data['transition_uuid'])
        param.json_update('transition.issue_type_uuid', issue_data['issue_type_uuid'])
        post_function = [
            {
                "send_email_notice": {
                    "notice_types": ['email', 'third_7'],
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
        param.json_update('transition.post_function', post_function)
        param.uri_args(
            {'issue_type_uuid': issue_data['issue_type_uuid'], 'transition_uuid': issue_data['transition_uuid']})
        resp = self.call(PostActionUpdate, param)
        resp.check_response('transition.uuid', issue_data['transition_uuid'])

    @story('T130034 后置动作：添加发送通知后置动作（特殊角色：工作项关注者）')
    def test_add_post_action_notice_task_watchers(self, issue_data):
        param = issue.post_action()[0]
        param.json_update('transition.uuid', issue_data['transition_uuid'])
        param.json_update('transition.issue_type_uuid', issue_data['issue_type_uuid'])
        post_function = [
            {
                "send_email_notice": {
                    "notice_types": ['email', 'third_7'],
                    "user_domains": [
                        {
                            "user_domain_type": "task_watchers",  # 角色 task_watchers
                            "user_domain_param": ""
                        }
                    ],
                    "field_uuids": []
                }
            }
        ]
        param.json_update('transition.post_function', post_function)
        param.uri_args(
            {'issue_type_uuid': issue_data['issue_type_uuid'], 'transition_uuid': issue_data['transition_uuid']})
        resp = self.call(PostActionUpdate, param)
        resp.check_response('transition.uuid', issue_data['transition_uuid'])

    @story('129922 后置动作：添加发送通知后置动作（部门）')
    def test_add_post_action_notice_department(self, issue_data):
        # 新增部门
        param = add_sub_department()[0]
        resp = self.call(third.ADDSubDepartment, param)
        depart_uuid = resp.json()['add_department']['uuid']
        with step('添加发送通知后置动作（部门）'):
            param = issue.post_action()[0]
            param.json_update('transition.uuid', issue_data['transition_uuid'])
            param.json_update('transition.issue_type_uuid', issue_data['issue_type_uuid'])
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": ['email', 'third_7'],
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
            param.json_update('transition.post_function', post_function)
            param.uri_args(
                {'issue_type_uuid': issue_data['issue_type_uuid'], 'transition_uuid': issue_data['transition_uuid']})
            resp = self.call(PostActionUpdate, param)
            resp.check_response('transition.uuid', issue_data['transition_uuid'])
        with step('清除部门数据'):
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story('130128 后置动作：添加发送通知后置动作（用户组）')
    def test_add_post_action_notice_group(self, issue_data):
        # 新增用户组
        param = data.user_group_add()[0]
        resp = self.call(project.UsesGroupAdd, param)
        group_uuid = resp.value('uuid')
        with step('添加发送通知后置动作（用户组）'):
            param = issue.post_action()[0]
            param.json_update('transition.uuid', issue_data['transition_uuid'])
            param.json_update('transition.issue_type_uuid', issue_data['issue_type_uuid'])
            post_function = [
                {
                    "send_email_notice": {
                        "notice_types": ['email', 'third_7'],
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
                                    "name": resp.value('name'),
                                    "name_pinyin": resp.value('name_pinyin'),
                                    "desc": "",
                                    "create_time": 0,
                                    "members": []
                                },
                                "members": [],
                                "tag": "用户组",
                                "name": resp.value('name'),
                                "subText": "0人"
                            }
                        ]
                    }
                }
            ]
            param.json_update('transition.post_function', post_function)
            param.uri_args(
                {'issue_type_uuid': issue_data['issue_type_uuid'], 'transition_uuid': issue_data['transition_uuid']})
            resp = self.call(PostActionUpdate, param)
            resp.check_response('transition.uuid', issue_data['transition_uuid'])
        with step('清除用户组数据'):
            param.uri_args({'group_uuid': group_uuid})
            self.call(project.UsesGroupDelete, param, with_json=False)

    @story('T130621 后置动作：添加状态联动后置动作（父工作项）（后置动作验证：关联工作项）')
    def test_add_post_action_relation(self, issue_data):
        # 获取工作项状态UUId
        data = {
            "task_status": 0
        }
        resp = team_stamp(data)
        task_uuid = [r['uuid'] for r in resp.value('task_status.task_statuses') if r['name'] == '测试提交'][0]

        with step('添加状态联动后置动作（父工作项）（后置动作验证：关联工作项）'):
            param = issue.post_action()[0]
            param.json_update('transition.uuid', issue_data['transition_uuid'])
            param.json_update('transition.issue_type_uuid', issue_data['issue_type_uuid'])
            post_function = [
                {
                    "update_status": {
                        "target": "parent",
                        "target_range": {},
                        "target_status": task_uuid,
                        "validation_type": "none",
                        "validation_params": {
                            "params1": "",
                            "params2": ""
                        }}}]
            param.json_update('transition.post_function', post_function)
            param.uri_args(
                {'issue_type_uuid': issue_data['issue_type_uuid'], 'transition_uuid': issue_data['transition_uuid']})
            resp = self.call(PostActionUpdate, param)
            resp.check_response('transition.uuid', issue_data['transition_uuid'])
