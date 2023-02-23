#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：issue.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/5 
@Desc    ：工作项测试用例数据模块
"""
from falcons.helper import mocks
from falcons.ops import generate_param

from main.params.const import ACCOUNT


def add_standard_issue():
    """添加标准工作项"""
    return generate_param({
        'issue_type': {
            'name': f'Std{mocks.serial_no()}'[:30],
            'icon': 3,
            'type': 0
        }
    })


def add_sub_issue():
    """添加子工作项"""
    return generate_param({
        'issue_type': {
            'name': f'子Sub{mocks.serial_no()}'[:30],
            'icon': 15,
            'type': 1
        }
    })


def show_issue_list():
    """显示工作项列表"""
    return generate_param({
        'issue_type': 0,
        # 'issue_type_config': 0
    })


def issue_check():
    """用于工作项检查"""
    return generate_param({
        'issue_type': 0,
        'field': 0
    })


def delete_issue():
    """删除工作项"""
    return generate_param({}, **{'issue_uuid': ''})


def copy_issue():
    """复制工作项"""
    return generate_param({
        "issue_type": {
            "name": f'CpyIssue{mocks.ones_uuid()}',
            "icon": 2,
            "type": 0
        },
        "copy_from": ''  # 原工作项UUID
    })


def add_project_issue():
    """添加工作项到项目"""
    return generate_param({
        'issue_type_uuids': [
            ''  # 工作项uuid
        ]
    }, is_project=True)


def delete_project_issue():
    """删除项目工作项"""
    return generate_param({}, is_project=True, **{'issue_uuid': ''})


def add_issue_field():
    """添加属性到工作项"""
    return generate_param({
        'field_config': {
            'field_uuid': '',  # 工作项属性UUID
            'required': False
        }
    })


def update_issue_field(issue_uuid, field_uuid, time):
    """更新工作项开始，结束时间字段"""
    return generate_param({"tasks": [
        {
            "uuid": issue_uuid,
            "field_values": [
                {
                    "field_uuid": field_uuid,
                    "type": 5,
                    "value": time
                }
            ],
            "only_edit_alone_permission_fields": True
        }
    ]})


def issue_field_config():
    """获取工作项属性配置"""
    return generate_param({}, **{'issue_uuid': ''})


def get_task_progress(task_uuid):
    return generate_param({
        "query": "\n    query TASK($key: Key) {\n      task(key: $key) {\n        \n    planStartDate\nplanEndDate\nprogress\n\n    subTaskCount\n  \n\n        issueType {\n          uuid\n        }\n        subIssueType {\n          uuid\n        }\n        project {\n          uuid\n        }\n        issueTypeScope {\n          uuid\n        }\n      }\n    }\n  ",
        "variables": {
            "key": "task-" + task_uuid
        }
    })


def copy_issue_type_config(issue_uuid: list):
    """从已有项目中复制工作项"""
    return generate_param({
        "copy_from": {
            ACCOUNT.project_uuid: issue_uuid  # 工作项类型uuid
        }
    })


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 工作项类型-属性与视图-模块标签页


def tab_config_update():
    """更新模块标签页"""
    p = {"configs": []}

    for num in range(1, 10):
        p['configs'].append(
            {
                "type": num,
                "is_show": True,
                "can_hide": True
            }
        )

    return generate_param(p)


def tab_config_update1():
    return generate_param({"configs": []})


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 工作项类型-工作项工作流


def issue_workflow_set_init():
    """工作项工作流设置初始状态"""
    return generate_param({
        "task_status_config": {
            "default": True
        }
    }, is_project=True)


def issue_workflow_status_add():
    """添加工作项工作流状态"""
    return generate_param({"task_status_configs": []}, is_project=True)


def issue_workflow_status_delete():
    """删除工作项工作流状态"""
    return generate_param({}, is_project=True)


def issue_workflow_transition_add():
    """添加工作项工作流步骤"""
    return generate_param({
        "transitions": [
            {
                "project_uuid": ACCOUNT.project_uuid,
                "issue_type_uuid": "JbqewS6U",
                "start_status_uuid": "LyKDyvu3",
                "end_status_uuid": "LyKDyvu3",
                "name": "进行中"
            }
        ]
    }, is_project=True)


def sort_issue_type(issue_type_uuids: list):
    """项目内工作项类型排序"""
    return generate_param({
        "issue_type_uuids": issue_type_uuids
    }, is_project=True)


def task_sort(positions: list):
    """工作项状态排序"""
    return generate_param({
        "positions": positions
    }, is_project=True)


def add_task_field(fields: list, issue_types: list):
    """添加属性到工作项类型"""
    return generate_param({
        "fields": fields,
        "global_view_config": [],
        "team_issue_types": [],
        "project_issue_types": [
            {
                "project_uuid": ACCOUNT.project_uuid,
                "issue_types": issue_types
            }
        ]
    })


def notice_rules():
    return generate_param({}, is_project=True)


def add_notice_rules():
    """新增，编辑工作项提醒"""
    return generate_param({
        "field_uuid": '',
        "action": '',
        "notice_time": '',
        "notice_types": [
            "notice_center"
        ],
        "notice_user_domains": '',
        "filter_condition": '',
        "condition": ''
    }, is_project=True)


def notice_config():
    """工作项通知参数"""
    return generate_param({
        "roles": [],
        "single_user_uuids": [],
        "role_uuids": [],
        "group_uuids": [],
        "department_uuids": [],
        "field_uuids": []
    })


def update_notice_center():
    """工作项通知 通知方式配置"""
    return generate_param({
        "notice_center": False,
        "effect_notice_center": False,
        "email": False,
        "effect_email": True,
        "wechat": False,
        "effect_wechat": False
    })


def field_sort():
    """关键属性排序"""
    return generate_param({
        "fields": [
            ''
        ]
    })


def post_action():
    """后置动作参数"""
    return generate_param({
        "transition": {
            "uuid": '',
            "issue_type_uuid": '',
            "project_uuid": ACCOUNT.project_uuid,
            "post_function": ''
        }
    }, is_project=True)


def global_post_action():
    """配置中心-后置动作参数"""
    return generate_param({
        "transition": {
            "post_function": [
                ''
            ]
        }
    })


def update_step_field(step_uuid: str, it_uuid: str, prj_uuid: str, fields: [dict]):
    """更新步骤属性"""
    return generate_param({
        "transition": {
            "uuid": step_uuid,
            "issue_type_uuid": it_uuid,
            "project_uuid": prj_uuid,
            "fields": fields
        }
    }, is_project=True)


def add_issue_permission():
    """add 工作项权限"""
    return generate_param({
        "permission_rule": {
            "context_type": "issue_type",
            "context_param": {
                "project_uuid": ACCOUNT.project_uuid,
                "issue_type_uuid": ''
            },
            "permission": '',
            "user_domain_type": '',
            "user_domain_param": ''
        }
    })


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 全局配置-工作项类型
def issue_type_create(typ=0, icon=3):
    """
    参数：全局配置-新建工作项类型
    :param typ: 0 标准工作项 1 子工作项
    :param icon: 1～15
    :return:
    """
    return generate_param({
        "issue_type": {
            "name": f'it-{mocks.ones_uuid()}',
            "icon": icon,
            "type": typ
        }
    })


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# 全局配置-工作项-优先级

def priori_update():
    """优先级变更"""

    return generate_param({'field': ''})
