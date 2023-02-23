#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：plan.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/24 
@Desc    ：测试计划用例
"""
from falcons.helper import mocks
from falcons.ops import generate_param

from main.params.const import ACCOUNT


def add_member():
    """权限配置里添加用户权限"""
    return generate_param({
        'permission_rule': {
            'context_type': 'team',
            'context_param': {
                'team_uuid': ACCOUNT.user.team_uuid
            },
            'permission': 'create_gantt_chart',  # 创建甘特图的权限
            'user_domain_type': 'single_user',
            'user_domain_param': ''  # 这是待赋权的成员uuid
        }
    })


def create_gantt():
    """新建甘特图"""
    return generate_param({
        'item': {
            'name': f'Gantt-{mocks.random_string(4)}',
            'shared': False,
            'item_type': 'gantt_chart',
            'shared_to': [],
            'import_config': {
                'projects': [
                    ACCOUNT.project_uuid
                ]
            },
            'sync_from_project': True,
            'sync_to_project': True
        }
    })


def update_gantt():
    """更新甘特图"""
    return generate_param({
        'item': {
            'uuid': '',  # 甘特图UUID
            'name': 'Gantt-ugSA-new',  # 甘特图新名称
            'shared': False,
            'item_type': 'gantt_chart',
            'shared_to': []
        }
    }, **{'item_key': ''})


# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*


def create_task():
    """新建甘特图-任务"""
    return generate_param({
        'item': {
            'name': f'Task-{mocks.random_string(4)}',
            'item_type': 'gantt_data',
            'gantt_data_type': 'task',
            'gantt_chart_uuid': '',  # 甘特图UUID
            'plan_start_time': mocks.now_timestamp(),
            'plan_end_time': mocks.day_timestamp(),
            'parent': '',
            'assign': None
        }
    })


def update_task():
    """更新甘特图-任务"""
    return generate_param({
        'item': {
            'uuid': '',  # 任务UUID
            'name': f'Task-new-{mocks.random_string(4)}',
            'item_type': 'gantt_data',
            'gantt_data_type': 'task',
            'gantt_chart_uuid': '',  # 甘特图UUID
            'plan_start_time': mocks.day_timestamp(1),
            'plan_end_time': mocks.day_timestamp(3),
            'assign': ACCOUNT.user.owner_uuid,
            'progress': 1000000  # 进度改为10%
        }
    })


def delete_item():
    """删除工作项"""
    return generate_param({})


def task_to_group():
    """
    任务改为分组 ItemUpdate
    :return: 
    """
    return generate_param({
        'item': {
            'gantt_data_type': 'group',
            'plan_start_time': 0,
            'plan_end_time': 0,
            'progress': 0
        }
    })


def task_to_milestone():
    """
    任务改为里程碑 ItemUpdate
    :return: 
    """
    return generate_param({
        'item': {
            'gantt_data_type': 'milestone',
            'plan_start_time': 14400,
            'plan_end_time': 14400
        }
    })


def group_to_task():
    """
    分组改为任务 ItemUpdate
    :return:
    """
    return generate_param({
        'item': {
            'gantt_data_type': 'task',
            'plan_start_time': mocks.now_timestamp(),
            'plan_end_time': mocks.day_timestamp()
        }
    })


def group_to_milestone():
    """
    分组改为里程碑 ItemUpdate
    :return:
    """
    return generate_param({
        'item': {
            'gantt_data_type': 'milestone',
            'plan_start_time': mocks.day_timestamp(1),
            'plan_end_time': mocks.day_timestamp(3)
        }
    })


def create_group():
    """里程碑-创建分组"""
    return generate_param({
        'item': {
            'name': f'Group-{mocks.random_string(4)}',
            'item_type': 'gantt_data',
            'gantt_data_type': 'group',
            'gantt_chart_uuid': '',  # 甘特图UUID
            'plan_start_time': 0,
            'plan_end_time': 0,
            'parent': '',
            'assign': None
        }
    })


def update_group():
    """更新分组信息"""
    return generate_param({
        'item': {
            'uuid': '',
            'name': 'new 分组',
            'item_type': 'gantt_data',
            'gantt_data_type': 'group',
            'gantt_chart_uuid': '',
            'plan_start_time': 0,
            'plan_end_time': 0
        }
    })


def create_milestone():
    """创建里程碑"""
    return generate_param({
        'item': {
            'name': f'MILESTONE-{mocks.random_string(4).upper()}',
            'item_type': 'gantt_data',
            'gantt_data_type': 'milestone',
            'gantt_chart_uuid': '',
            'progress': 0,
            'plan_start_time': mocks.now_timestamp(),
            'plan_end_time': mocks.now_timestamp(),
            'parent': '',
            'assign': ACCOUNT.user.owner_uuid
        }
    })


def update_milestone():
    """更新里程碑"""
    return generate_param({
        'item': {
            'uuid': '',  # 里程碑UUID
            'name': f'NewMS-{mocks.random_string(4).upper()}',
            'item_type': 'gantt_data',
            'gantt_data_type': 'milestone',
            'gantt_chart_uuid': '',  # 甘特图UUID
            'progress': 10000000,  # 改为已完成
            'plan_start_time': mocks.now_timestamp(),
            'plan_end_time': mocks.now_timestamp()
        }
    })


def milestone_to_task():
    """里程碑-》task"""
    return generate_param({
        'item': {
            'gantt_data_type': 'task',
            'plan_start_time': mocks.now_timestamp(),
            'plan_end_time': mocks.day_timestamp()
        }
    })


def share_gantt():
    """共享甘特图"""
    return generate_param({
        'item': {
            'uuid': '',  # 甘特图UUID
            'name': 'SharedGantt',  # 改个名字
            'shared': True,
            'item_type': 'gantt_chart',
            'shared_to': [
                {
                    'user_domain_type': 'everyone',
                    'user_domain_param': ''
                }
            ]
        }
    })


def private_gantt():
    return generate_param({
        'item': {
            'uuid': '',  # 甘特图UUID
            'name': 'PrivateGantt',
            'shared': False,
            'item_type': 'gantt_chart',
            'shared_to': []
        }
    })


def gantt_sync_to_proj():
    """"""
    return generate_param({
        "action": "to_project",
        "uuids": [  # 需要同步的任务UUID

        ]
    })


def gantt_close_sync(stp=False, sfp=True):
    """关闭同步功能"""
    return generate_param({
        "item": {
            "uuid": '',  # 甘特图UUID
            "item_type": "gantt_chart",
            "sync_from_project": sfp,
            "sync_to_project": stp
        }
    })


# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
##项目计划

def get_plan_log_data(plan_uuid):
    """项目计划动态log data"""
    return generate_param({
        "query": "\n    query COMMONMESSAGES($filter: Filter) {\n      commonMessages(\n        filter: {\n          objectId_in: [\"%s\"]\n      }) {\n        key\n        uuid\n        operator\n        objectId\n        createTime\n        objectType\n        action\n        tag\n        ext\n      }\n      commonComments(\n        filter: {\n          objectId_in: [\"%s\"]\n      }) {\n        key\n        uuid\n        referenceId\n        fromUser {\n          uuid\n        }\n        toUser {\n          uuid\n        }\n        message\n        objectType\n        objectId\n        createTime\n        updateTime\n        status\n      }\n    }\n  "
                 % (plan_uuid, plan_uuid),
        "variables": {}
    })


def get_plan_chart_uuid(project_uuid=''):
    """查询项目计划的chart_uuid"""
    p_uid = project_uuid if project_uuid else ACCOUNT.project_uuid
    return generate_param({
        "query": "\n          query PPMProjectChartInfo {\n            activityCharts(\n              filter:{\n                project_in:[\"% p_uid\"]\n              }) {\n              key\n              name\n              uuid\n              drafting\n              personalConfig {\n                key\n                zooming\n                personalFields {\n                  fieldUUID\n                  sort\n                }\n              }\n              config {\n                key\n                settings\n              }\n            }\n          }\n        "
                 % p_uid})


# --------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
## 项目内--里程碑组件


def add_deliverables(milestone_uuid, up_type, after=''):
    """
    新增交付物参数
    milestone_uuid：
    up_type：交付物类型
    after：前面的交付物id
    """
    return generate_param({
        "query": "\n        mutation AddDeliverable {\n          addDeliverable (project: $project name: $name type: $type after: $after milestone: $milestone) {\n            key\n          }\n        }\n      ",
        "variables": {
            "project": ACCOUNT.project_uuid,
            "name": "交付物" + mocks.num(),
            "type": up_type,
            "after": after,
            "milestone": milestone_uuid
        }
    })


def del_deliverables(key):
    """删除交付物"""
    return generate_param({
        "query": "\n        mutation DeleteDeliverable {\n          deleteDeliverable (key: $key) {\n            key\n          }\n        }\n      ",
        "variables": {
            "key": key
        }
    })


def submit_deliverables(key, content):
    """提交交付物 link wiki类型"""
    return generate_param({
        "query": "\n        mutation UpdateDeliverable {\n          updateDeliverable (key: $key content: $content) {\n            key\n          }\n        }\n      ",
        "variables": {
            "key": key,
            "content": content
        }
    })


def submit_deliverables_type(key, type):
    """更新交付物 link/wiki类型"""
    return generate_param({
        "query": "\n        mutation UpdateDeliverable {\n          updateDeliverable (key: $key type: $type) {\n            key\n          }\n        }\n      ",
        "variables": {
            "key": key,
            "type": type
        }
    })


def upload_deliverable_file(ref_id):
    """里程碑交付物 文件类型上传"""
    return generate_param({
        "type": "attachment",
        "name": "test_img_" + mocks.ones_uuid() + ".jpg",
        "ref_id": ref_id,
        "ref_type": "deliverable",
        "description": None
    })


def deliverable_list():
    """交付物组件列表"""
    return generate_param({
        "query": "\n    query DELIVERABLES($orderBy: OrderBy) {\n      deliverables (\n        orderBy: $orderBy,\n        filter: {\n          project_equal: \"%s\"\n        }\n      ) {\n        uuid\n        key\n        number\n        commitTime\n        name\n        type\n        milestone {\n          uuid\n          name\n          activityUUID\n        }\n        sourceType\n        committer{\n          name\n          uuid\n          avatar\n        }\n        content{\n          name\n          size\n          resource_uuid\n          page_uuid\n        }\n      }\n    }\n  " % ACCOUNT.project_uuid,
        "variables": {
            "orderBy": {
                "namePinyin": "ASC"
            }
        }
    })
