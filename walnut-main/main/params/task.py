#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：task.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/9 
@Desc    ：
"""
import json

from falcons.helper import mocks
from falcons.helper.mocks import ones_uuid
from falcons.ops import generate_param

from main.params.const import ACCOUNT


def task_add(task_no=1, proj_uuid=ACCOUNT.project_uuid, owner_uuid=None, field004=None,
             watcher_uuid=None):
    """添加工作项"""
    tasks = []
    now = mocks.now_timestamp()
    day = mocks.day_timestamp()
    if not field004:
        field004 = owner_uuid if owner_uuid else ACCOUNT.user.owner_uuid
    for c in range(task_no):
        m = {
            'uuid': f'{owner_uuid if owner_uuid else ACCOUNT.user.owner_uuid}{ones_uuid()}',
            'owner': owner_uuid if owner_uuid else ACCOUNT.user.owner_uuid,
            'assign': owner_uuid if owner_uuid else ACCOUNT.user.owner_uuid,
            'summary': f'用于测试的工作项-{c + 1}',  # 标题
            'parent_uuid': '',
            'field_values': [
                {
                    'field_uuid': 'field004',
                    'type': 8,
                    'value': field004,
                },
                {
                    'field_uuid': 'field012',
                    'type': 1,
                    'value': ''  # 优先级UUID，在案例中赋值
                },
                {
                    'field_uuid': 'field027',  # 计划开始日期
                    'type': 5,
                    'value': now
                },
                {
                    'field_uuid': 'field028',  # 计划完成日期
                    'type': 5,
                    'value': mocks.day_timestamp(week=1)
                },
                {
                    'field_uuid': 'field013',  # 截止日期
                    'type': 5,
                    'value': day
                }
            ],
            'project_uuid': proj_uuid,
            'issue_type_uuid': '',  # 任务工作项/子工作项的UUID， 在案例中赋值
            'add_manhours': [],
            'watchers': [
                watcher_uuid if watcher_uuid else ACCOUNT.user.owner_uuid
            ]
        }
        tasks.append(m)

    return generate_param({
        'tasks': tasks
    })


def task_field(flush=False):
    """
    获取任务属性配置

    :param flush: 获取最新的 默认False
    :return:
    """
    if flush:

        return generate_param({
            'issue_type_config': 0,  # 类型配置
            'field_config': 0,  # 属性配置
            'task_status': 0,  # 状态UUID
            'issue_type': 0
        })
    else:
        return ACCOUNT.stamp_data, None


def task_update_name():
    """更新任务名"""
    name_129 = mocks.random_string(43) * 3
    return generate_param({
        'tasks': [
            {
                'uuid': '',  # 任务的uuid
                'name': name_129,
                'summary': name_129
            }
        ]
    })


def task_detail_edit():
    """编辑任务详情属性"""

    return generate_param({
        'tasks': [
            {
                'uuid': '',
            }
        ]
    })


def task_delete():
    """删除任务"""
    return generate_param({}, **{'task_uuid': ''})


def task_delete_batch():
    """批量删除任务"""
    return generate_param({'tasks': []  # 任务UUID
                           })


def task_info():
    """获取任务信息"""
    return generate_param({}, **{'task_uuid': ''})


def task_update_sprint():
    """任务关联迭代"""
    return generate_param({
        'tasks': [
            {
                'uuid': '',  # 任务UUID
                'field_values': [
                    {
                        'field_uuid': 'field011',  # 迭代属性
                        'type': 7,
                        'value': ''  # 迭代UUID
                    }
                ]
            }
        ]
    })


def task_relation_sprint(uuid, sprint_uuid):
    """待办事项，工作项拖拽到迭代中"""
    return generate_param({
        "tasks": [
            {
                "uuid": uuid,
                "sprint_uuid": sprint_uuid
            }
        ]
    })


def task_add_sub_issue():
    """创建子工作项"""
    return task_add()


def task_copy():
    """任务复制"""

    return generate_param({
        'project_uuid': ACCOUNT.project_uuid,
        'issue_type_uuid': '',  # 工作项类型UUID
        'status_uuid': '',  # 任务状态UUID
        'reserve_contents': [
            'cycle',
            'relatedTask',
            'testing',
            'relatedWiki',
            'attachment',
            'watcher',
            'subTask'
        ]
    }, **{'task_uuid': ''})


def task_batch_copy():
    """批量复制工作项"""

    return generate_param({
        'tasks': [],
        'reserve_contents': [
            'cycle',
            'relatedTask',
            'testing',
            'relatedWiki',
            'attachment',
            'watcher',
            'subTask'
        ]
    })


def lite_context_permission_rules():
    return generate_param({
        'context_type': 'issue_type',  # 类型
        'context_param': {
            'project_uuid': ACCOUNT.project_uuid,
            'issue_type_uuid': ''  # 工作项类型UUID
        }
    })


def add_man_hour(hour: int = 5, mode='simple'):
    """
    添加工时

    :param hour: 默认工时5小时
    :param mode: 添加模式，简单 'simple', 汇总 'detailed'
    :return:
    """
    return generate_param({
        'query': 'mutation AddManhour {\n      addManhour (mode: $mode owner: $owner '
                 'task: $task type: $type start_time: $start_time hours: $hours '
                 'description: $description) {\n        key\n      }\n    }\n  ',
        'variables': {
            'mode': mode,
            'owner': ACCOUNT.user.owner_uuid,
            'task': '',  # task uuid
            'type': 'recorded',
            'start_time': mocks.now_timestamp(),
            'hours': hour * 10000,
            'description': ""
        }
    })


def modify_man_hour():
    """修改工时"""
    return generate_param({
        'query': 'mutation UpdateManhour {\n      updateManhour (mode: $mode owner: $owner task: '
                 '$task type: $type start_time: $start_time hours: $hours description: $description '
                 'key: $key) {\n        key\n      }\n    }\n  ',
        'variables': {
            'mode': 'simple',
            'owner': ACCOUNT.user.owner_uuid,
            'task': '',  # task uuid
            'type': 'recorded',
            'start_time': mocks.now_timestamp(),
            'hours': 300000,
            'description': '',
            'key': ''  # 工时key
        }
    })


def fetch_man_hours():
    """获取任务工时信息"""
    return generate_param({
        'query': 'query FetchUserManhours {\n      manhours(\n        filter: $manhourFilter\n'
                 '       orderBy: $manhoursOrderBy\n      ) {\n        key\n        hours\n'
                 '        startTime\n        description\n        type\n      }\n    }\n  ',
        'variables': {
            'manhourFilter': {
                'task_in': [
                    ''  # 任务uuid
                ],
                'type_in': [
                    'recorded'
                ]
            },
            'manhoursOrderBy': {
                'startTime': 'DESC',
                'createTime': 'DESC'
            }
        }
    })


def delete_man_hour():
    """删除工时"""
    return generate_param({
        'query': 'mutation DeleteManhour {\n      deleteManhour (key: $key mode: $mode) {\n'
                 '        key\n      }\n    }\n  ',
        'variables': {
            'key': '',  # 工时key
            'mode': 'simple'
        }
    })


def task_messages():
    """获取任务消息"""
    return generate_param({})


def task_update():
    """更新工作项属性"""

    return generate_param(
        {
            'tasks': [
                {
                    'uuid': '',  # 任务UUID
                    'field_values': [
                        # 需要更新的数据
                        # {
                        #     'field_uuid': 'field027',
                        #     'type': 5,
                        #     'value': 1648569600
                        # }
                    ],
                    'only_edit_alone_permission_fields': True
                }
            ]
        }
    )


def update_issue_type(tasks: dict):
    """
    更新工作项类型
    :param tasks 传入参数类型形如
                        {
                        'task_uuid': '7CU6yrjuE1ezt5KV',
                        'old_issue_type_uuid': 'NAFqwKNf',
                        'new_issue_type_uuid': 'MmUVuCB4',
                        'status': {
                            'old_status_uuid': 'Nw2jjybX',
                            'new_status_uuid': 'Nw2jjybX'
                        },
                        'field_values': None,
                        'parent_uuid': '7CU6yrjuK5HauXE7'
                        }
    """

    return generate_param({
        'type': 'single',
        'action': 'std_to_sub_issue_type',
        'tasks': [tasks]

    })


def assess_man_hour():
    """添加或更新预估工时"""

    return generate_param({
        'value': 24 * 100000  # 默认24个小时
    })


def remaining_hour():
    """添加或更新剩余工时"""

    return generate_param({
        'value': 3 * 100000  # 默认3个小时
    })


def add_man_hour_detail_estimated(f_type='sum', tid=None):
    """
    汇总模式添加预估工时
    :param tid:
    :param f_type:  工时模式，sum 总计，avg 平均每天。
    :return:
    """
    return generate_param({
        'query': 'mutation AddManhour {\n      addManhour (mode: $mode task: $task owner: $owner type:'
                 '$type hours: $hours from: $from to: $to hours_format: $hours_format) '
                 '{\n        key\n      }\n    }\n  ',
        'variables': {
            'mode': 'detailed',
            'task': tid if tid else '',  # 任务UUID
            'owner': ACCOUNT.user.owner_uuid,
            'type': 'estimated',
            'hours': 30 * 100000,
            'from': mocks.now_timestamp(),
            'to': mocks.day_timestamp(1),
            'hours_format': f_type
        }
    })


def task_add_field():
    """工作项添加属性"""

    return generate_param({
        'field_config': {}  # 属性信息，用例中赋值
    }, is_project=True)


# -*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*-
# -*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*-

def message_add(multi=False):
    """添加评论"""
    c_uuid = mocks.ones_uuid()
    t_uuid = mocks.ones_uuid()

    t = f'Test comment  about {c_uuid} - {t_uuid}.'
    txt = '\n'.join((t for _ in range(5))) if multi else t

    return generate_param({
        'uuid': c_uuid,
        'text': txt
    })


def message_update():
    """更新评论"""
    return generate_param({
        'uuid': '',
        'text': f'Updated comment text.'
    })


def message_reply():
    """回复评论"""
    return generate_param({
        'uuid': mocks.ones_uuid(),
        'text': 'Replay A comment ....',
        'replied_message_uuid': ''  # 被回复的评论UUID
    })


def message_delete():
    """删除评论"""
    return generate_param({})


# -*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*-
# -*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*-


def upload_file(name):
    """上传文件"""
    return generate_param({
        'type': 'attachment',
        'name': name,
        'ref_id': '',  # 任务UUID
        'ref_type': 'task',
        'description': ''
    })


def queue_progress():
    """队列进度"""
    return generate_param({})


def queue_list():
    """队列列表"""
    return generate_param({})


def queue_extra(extra: dict):
    """队列文件"""
    return generate_param(
        {
            "extra": json.dumps(extra)
        })


def close_progress():
    """关闭队列"""
    return generate_param({
        'uuids': []
    })


def field_value_update():
    """更新工作项字段值"""
    return generate_param({
        'tasks': [
            {
                'task_uuid': '',  # 用例中赋值
                'field_values': [
                    {
                        'type': 8,
                        'field_uuid': 'field004',
                        'value': ACCOUNT.user.owner_uuid
                    }
                ]
            }
        ],
        'type': 'batch',
        'action': 'modify_field_values'
    })


def batch_update_issue_type(uuids: list, old_data: list, new_data: list):
    """
    批量更新工作项类型
    :param uuids 工作项uuid集
    :param old_data 原工作项数据(状态和类型的uuid)
    :param new_data 新工作项数据(状态和类型的uuid)
    """

    tasks = []
    for uuid in uuids:
        tasks.append({
            'task_uuid': uuid,
            'old_issue_type_uuid': old_data[1],
            'new_issue_type_uuid': new_data[1],
            'status': {
                'old_status_uuid': old_data[0],
                'new_status_uuid': new_data[0]
            },
            'field_values': None,
            'parent_uuid': None
        })

    if tasks:
        return generate_param({
            'type': 'batch',
            'action': 'modify_issue_type',
            'tasks': tasks
        })


def batch_move_task(uuids: list, source_data: list, target_data: list, proj_uuid=ACCOUNT.project_uuid):
    """
    批量移动工作项
    :param uuids 工作项uuid集
    :param source_data 原工作项数据(状态和类型的uuid)
    :param target_data 目标工作项数据(状态和类型的uuid)
    :param proj_uuid
    """

    return generate_param({
        'tasks': uuids,
        'rules': [
            {
                'source_project_uuid': proj_uuid,
                'target_project_uuid': proj_uuid,
                'source_issue_type_uuid': source_data[1],
                'target_issue_type_uuid': target_data[1],
                'source_status_uuid': source_data[0],
                'target_status_uuid': target_data[0],
                'source_sub_issue_type_uuid': "",
                'target_sub_issue_type_uuid': ""

            }
        ],
        'tasks_related': []
    })


def task_file_upload():
    """工作项文件上传"""

    return generate_param({
        'type': 'attachment',
        'name': f'test_img_{mocks.ones_uuid()}',
        'ref_id': "",  # uuid
        'ref_type': 'task',
        'description': None,
        'isWorkorder': False
    })


# -*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*-
# -*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*--*-*-*-

def watchers_opt():
    """关注者操作"""

    return generate_param({'watchers': [ACCOUNT.user.owner_uuid]})


def merge_defect():
    return generate_param({

        'merge_uuid': "",  # 被合并的缺陷UUID
        'merge_type': 'source'
    }, **{'task_uuid': ''}  # 源缺陷UUID
    )


def to_demand():
    """
    缺陷转需求
    这个接口依次调用新建工作项，关联工作项，更新工作项状态接口
    起始参数和同创建工作项方法一下
    :return:
    """
    return generate_param({

    })


def bind_case():
    """绑定测试案例"""

    return generate_param({
        'cases': [
            {
                'task_uuid': '',  # 任务UUID
                'case_uuids': []  # 测试案例的UUID列表
            }
        ]
    })


def bind_case_result(task_uuid, plan_uuid, case_uuids: list):
    """关联执行结果"""
    return generate_param({
        "cases": [
            {
                "task_uuid": task_uuid,
                "plan_uuid": plan_uuid,
                "case_uuids": case_uuids

            }
        ]
    })


def unbind_case_result(task_uuid, plan_uuid, case_uuid):
    """解除关联执行结果"""
    return generate_param({
        "case_uuid": case_uuid,
        "task_uuid": task_uuid,
        "plan_uuid": plan_uuid
    })


def unbind_case(case_uuid, task_uuid):
    """解绑测试用例"""
    return generate_param({
        "case_uuid": case_uuid,
        "task_uuid": task_uuid
    })


def bind_testcase_plan(task_uuid, plan_uuids: list):
    """任务绑定测试计划"""
    return generate_param({
        "task_uuid": task_uuid,
        "plan_uuids": plan_uuids
    })


def unbind_testcase_plan(task_uuid, plan_uuid):
    """解除绑定测试计划"""
    return generate_param({
        "task_uuid": task_uuid,
        "plan_uuid": plan_uuid
    }, task_uuid=task_uuid)


def bind_wiki_pages(uuid, spaceUUID, title):
    """task 绑定wiki页面"""
    return generate_param({
        "pages": [
            {
                "uuid": uuid,
                "spaceUUID": spaceUUID,
                "title": title
            }
        ]
    })


def unbind_wiki_pages(title, uuid):
    """task 解除绑定wiki页面"""

    return generate_param({
        "page": {
            "title": title,
            "uuid": uuid
        }
    })


# -*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*-
def query_file(text_match=None, order_by=None):
    """文件组件搜索框查询"""
    val = {
        'query': '\n    query ResourcePage {\n      buckets(\n        '
                 'pagination: $pagination,\n        groupBy: {\n          '
                 'taskAttachments: {}\n        },\n      ) {\n'
                 '        key\n        pageInfo {\n          count\n'
                 '          totalCount\n          startCursor\n          endCursor\n'
                 '          hasNextPage\n          unstable\n        }\n'
                 '        taskAttachments(\n          filter: $filter,\n'
                 '          orderBy: $orderBy\n        ) {\n          uuid\n'
                 '          name\n          size\n          referenceType\n'
                 '          referenceId\n          summary\n          owner {\n'
                 '            uuid\n            name\n            avatar\n          }\n'
                 '          hash\n          extId\n          description\n'
                 '          mime\n          imageWidth\n          imageHeight\n'
                 '          createTime\n          fileCategory\n        }\n      }\n    }\n  ',
        'variables': {
            'filter': {
                'referenceType_equal': 'task',
                'project_equal': ACCOUNT.project_uuid,
                'source_equal': 'page',
                'status_equal': 'normal',
            },
            'pagination': {
                'limit': 50,
                'after': ''
            },
            'orderBy': {
                'createTime': 'DESC'
            }
        }
    }
    if text_match:  # 添加要搜索的内容
        val['variables']['filter'] |= {'text_match': text_match}
    if order_by:
        val['variables']['orderBy'] = order_by

    return generate_param(val)


# -*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*-


def add_new_wiki_pages(parent_page_uuid):
    """
    在任务中新建wiki页面
    parent_page_uuid：父属页面uuid
    """
    return generate_param({
        "parent_page_uuid": parent_page_uuid,
        "title": f"关联task" + mocks.num(),
        "content": "content-content",
        "src_type": "template",
        "src_uuid": ""
    })


def add_new_online_wiki_pages(parent_uuid, space_uuid):
    """任务内新增wiki协同页面"""
    return generate_param({
        "parent_uuid": parent_uuid,
        "title": "wiki协同页面" + mocks.num(),
        "space_uuid": space_uuid
    })


def bind_new_wiki_pages(page_uuid, space_uuid, parent_uuid):
    """任务绑定新增的wiki文档"""
    return generate_param({
        "pages": [
            {
                "uuid": page_uuid,
                "team_uuid": ACCOUNT.user.owner_uuid,
                "space_uuid": space_uuid,
                "owner_uuid": ACCOUNT.user.owner_uuid,
                "title": "api页面" + mocks.num(),
                "parent_uuid": parent_uuid,
                "status": 1,
                "create_time": mocks.now_time(),
                "updated_time": mocks.now_time(),
                "OldParentUUID": "",
                "OldPreviousUUID": "",
                "EncryptStatus": 0,
                "ref_type": 1,
                "ref_uuid": "",
                "edit_users": ""
            }
        ]
    })


def task_upload_wiki(ref_id):
    """任务内上传wiki文件"""
    return generate_param({
        "type": "word",
        "name": "test.docx",
        "ref_id": ref_id,
        "ref_type": "space",
        "description": ""
    })


def word_import(ref_id, task_uuid):
    """导入word文档"""
    return generate_param({
        "type": "wiz",
        "ref_id": ref_id,
        "resource_uuids": [
            mocks.ones_uuid()
        ],
        "post_actions": [
            {
                "action": "bind_task",
                "args": {
                    "task_uuid": task_uuid
                }
            }
        ]
    })


def plan_task_drag(key, parent, after):
    """
    项目计划中，拖拽排序接口参数
    """
    return generate_param({
        "query": "\n        mutation UpdateGanttData {\n          updateActivity (key: $key parent: $parent after: $after) {\n            key\n          }\n        }\n      ",
        "variables": {
            "key": key,
            "parent": parent,
            "after": after
        }
    })


def export_pro_plan(chart_uuid, issue_type_list):
    """导出项目计划"""
    return generate_param({
        "chart_uuid": chart_uuid,
        "field_uuids": [
            "name",
            "type",
            "estimatedHours",
            "totalManhour",
            "remainingManhour",
            "progress",
            "assign",
            "startTime",
            "endTime",
            "status"
        ],
        "gql": {
            "query": "\n      query GanttData {\n        activities (orderBy: $orderBy filterGroup: $filterGroup) {\n          \nkey\nname\nganttDataType: type\nuuid\nnumber\nprogress\nparent\ncreateTime\nchartUUID\nplanStartTime: startTime\nplanEndTime: endTime\ncanBrowse\ncanModify\ncanModifyProgress\ncanModifyPlanTimes\ntarget {\n  relationType\n  target {\n    uuid\n  }\n}\nsource{\n  relationType\n  source {\n    uuid\n  }\n}\nposition\nassign {\n  uuid\n  name\n  avatar\n}\npreDependencyCount\npostDependencyCount\n\n          \n      \n        reminders\n        \n        \n      \n      \n        \n  \n  relatedTaskUUID\n  relatedTaskStatus{uuid name}\n  relatedTaskParent{uuid}\n  relatedTaskIssueType{icon uuid}\n  relatedTaskSubIssueType{icon uuid}\n  relatedProjectUUID\n\n  sprint {\n    uuid\n  }\n  estimatedHours\n  totalManhour\n  remainingManhour\n  isVirtual\n\n        \n      \n      \n          ppmTask{\n            uuid\n          }\n          milestone{\n            uuid\n          }\n          deliverable{\n            uuid\n            key\n            number\n            commitTime\n            name\n            type\n            committer{\n                name\n                uuid\n                avatar\n            }\n            content{\n                name\n                size\n                resource_uuid\n                page_uuid\n            }\n          }\n        }\n      }\n    ",
            "variables": {
                "orderBy": {
                    "position": "ASC"
                },
                "filterGroup": [
                    {
                        "isVirtual_in": [
                            False
                        ],
                        "chartUUID_in": [
                            chart_uuid
                        ]
                    },
                    {
                        "isVirtual_in": [
                            True
                        ],
                        "virtualType_in": [
                            "task"
                        ],
                        "chartUUID_in": [
                            chart_uuid
                        ]
                    },
                    {
                        "isVirtual_in": [
                            True
                        ],
                        "virtualType_in": [
                            "sprint"
                        ],
                        "task": {
                            "issueType_in": issue_type_list
                        },
                        "chartUUID_in": [
                            chart_uuid
                        ]
                    }
                ]
            }
        }
    }, is_project=True)


def task_config():
    """工作项工作流获取"""
    return generate_param({
        "transition": 0,
        "task_status_config": 0
    }, is_project=True)


def issue_workflow_transition_add(issue_type_uuid, start_status_uuid, end_status_uuid):
    """添加工作项工作流步骤"""
    return generate_param({
        "transitions": [
            {
                "project_uuid": ACCOUNT.project_uuid,
                "issue_type_uuid": issue_type_uuid,
                "start_status_uuid": start_status_uuid,
                "end_status_uuid": end_status_uuid,
                "name": "进行中"
            }
        ]
    }, is_project=True)


def download_file():
    """下载文件"""
    return generate_param({'action': 'download'})


def views_add():
    """工时日历 另存为"""
    return generate_param({
        "item": {
            "manhour_calendar_group": "",
            "name": "aaaa" + mocks.num(),
            "config": {
                "type": "workload",
                "dimensions": [
                    {
                        "field": "owner",
                        "order_by": {
                            "name_pinyin": "asc"
                        }
                    }
                ],
                "condition": {
                    "condition_groups": [
                        [
                            {
                                "field_uuid": "department",
                                "operate": {
                                    "operate_id": "include",
                                    "predicate": "in",
                                    "negative": False,
                                    "label": "filter.addQueryContent.include",
                                    "filter_query": "in"
                                },
                                "value": None
                            },
                            {
                                "field_uuid": "user",
                                "operate": {
                                    "operate_id": "include",
                                    "predicate": "in",
                                    "negative": False,
                                    "label": "filter.addQueryContent.include",
                                    "filter_query": "in"
                                },
                                "value": [
                                    "$currentUser"
                                ]
                            },
                            {
                                "field_uuid": "field006",
                                "operate": {
                                    "operate_id": "include",
                                    "predicate": "in",
                                    "negative": False,
                                    "label": "filter.addQueryContent.include",
                                    "filter_query": "in"
                                },
                                "value": None
                            },
                            {
                                "field_uuid": "user_group",
                                "operate": {
                                    "operate_id": "include",
                                    "predicate": "in",
                                    "negative": False,
                                    "label": "filter.addQueryContent.include",
                                    "filter_query": "in"
                                },
                                "value": None
                            }
                        ]
                    ]
                },
                "display": [
                    "estimated_hour"
                ],
                "based_on": "estimated_hours",
                "range": {
                    "quick": "this_week"
                }
            },
            "item_type": "manhour_calendar"
        }
    })


def items_add():
    """工时报表，另存为"""
    return generate_param({
        "item": {
            "manhour_calendar_group": "",
            "name": "1111" + mocks.num(),
            "config": {
                "type": "time_series",
                "dimensions": [
                    {
                        "field": "task",
                        "order_by": {
                            "create_time": "desc"
                        }
                    }
                ],
                "condition": {
                    "condition_groups": [
                        [
                            {
                                "field_uuid": "field001",
                                "operate": {
                                    "label": "filter.addQueryContent.include",
                                    "operate_id": "match",
                                    "predicate": "match"
                                },
                                "value": None
                            },
                            {
                                "field_uuid": "field007",
                                "operate": {
                                    "label": "filter.addQueryContent.include",
                                    "operate_id": "include",
                                    "predicate": "in"
                                },
                                "value": None
                            },
                            {
                                "field_uuid": "field017",
                                "operate": {
                                    "label": "filter.addQueryContent.include",
                                    "operate_id": "include",
                                    "predicate": "in"
                                },
                                "value": None
                            },
                            {
                                "field_uuid": "field012",
                                "operate": {
                                    "label": "filter.addQueryContent.include",
                                    "operate_id": "include",
                                    "predicate": "in"
                                },
                                "value": None
                            },
                            {
                                "field_uuid": "field004",
                                "operate": {
                                    "label": "filter.addQueryContent.include",
                                    "operate_id": "include",
                                    "predicate": "in"
                                },
                                "value": None
                            }
                        ]
                    ]
                },
                "display": [],
                "based_on": None,
                "range": {
                    "quick": "this_week"
                }
            },
            "fold": None,
            "item_type": "manhour_report"
        }
    })


def views_list():
    """获取视图列表"""
    return generate_param({
        "query":
            "query LIST_MANHOUR_REPORTS($filter: Filter, $orderBy: OrderBy,$groupBy: GroupBy, $groupsOrderBy: OrderBy)"
            " {\n  buckets(filter: $filter, orderBy: $orderBy, groupBy: $groupBy) {\n    key"
            "\n    manhourCalendarGroup "
            "{\n      uuid\n      name\n    }\n    manhourCalendars {\n      key\n      uuid\n      name\n      "
            "description\n      builtIn\n      config {\n        type\n        dimensions"
            "\n        range\n        condition"
            "\n        basedOn\n        display\n      }\n      createTime\n    }\n  }\n  "
            "manhourCalendarGroups(filter: $groupsFilter, orderBy: $groupsOrderBy) {\n    uuid\n    name\n  }\n}\n",
        "variables": {
            "groupBy": {
                "manhourCalendars": {
                    "manhourCalendarGroup": {}
                }
            },
            "orderBy": {
                "manhourCalendarGroup": {
                    "createTime": "ASC"
                }
            },
            "groupsOrderBy": {
                "createTime": "ASC"
            }
        }
    })


def item_list():
    """获取报表列表"""
    return generate_param({
        "query": "query LIST_MANHOUR_REPORTS($filter: Filter, $orderBy: OrderBy) {"
                 "\n  manhourReports(filter: $filter, orderBy: $orderBy) {\n    key"
                 "\n    uuid\n    name\n    description\n    builtIn\n    fold\n    config {"
                 "\n      type\n      dimensions\n      range\n      condition\n      basedOn"
                 "\n      display\n    }\n    createTime\n  }\n}\n",
        "variables": {
            "orderBy": {
                "createTime": "DESC"
            }
        }
    })


def save_view():
    """报表 另存为"""
    return generate_param({
        "query": "\n    mutation AddTeamReport {"
                 "\n      addTeamReport (name: $name config: $config detail_type: "
                 "$detail_type report_category: $report_category) {\n        key\n      }\n    }\n  ",
        "variables": {
            "name": "每周工时总览-111" + mocks.num(),
            "config": "{\"dimensions\":[{\"aggregation\":\"week\",\"manhour_aggregation\":"
                      "\"week\",\"order_by\":\"default\",\"manhour_order_by\":\"default\",\"order"
                      "\":\"desc\",\"limit\":10},{\"aggregation\":\"user\",\"manhour_aggregation\":"
                      "\"user\",\"order_by\":\"record_manhour\",\"manhour_order_by\":\"record_manhour\","
                      "\"order\":\"desc\",\"limit\":10}],\"filter\":null,\"include_subtasks\":true}",
            "detail_type": "manhour_overview",
            "report_category": "2orPCr68"
        }
    })


def view_list():
    """获取报表列表"""
    return generate_param({
        "query": "\n    query {\n    reportCategories("
                 "\n      filter: { project_equal: \"%s\" }\n      orderBy: {"
                 "\n        createTime: ASC\n        detailType: DESC\n        "
                 "namePinyin: ASC\n      }\n    ){\n      \n  uuid\n  name\n  key"
                 "\n  detailType\n  canUpdate\n  canDelete\n\n    }\n\n    teamReports("
                 "\n      \n      orderBy: {\n        updateTime: DESC\n        namePinyin: ASC"
                 "\n      }\n    ){\n      uuid\n      key\n      name\n      uuid\n      owner {"
                 "\n        name\n        uuid\n      }\n      \n      reportCategory {\n        uuid"
                 "\n        name\n        key\n        detailType\n      }\n      updateTime\n      "
                 "reportType: detailType\n      config\n    }\n  }" % ACCOUNT.project_uuid
    })


def report_category():
    """新建报表分组"""
    return generate_param({
        "query": "\n    mutation AddReportCategory {\n      "
                 "addReportCategory (name: $name) {\n        key\n      }\n    }\n  ",
        "variables": {
            "name": "分组A" + mocks.num()

        }
    })


def rename_category(key):
    """修改 报表 分组名称"""
    return generate_param({
        "query": "\n    mutation UpdateReportCategory {"
                 "\n      updateReportCategory (key: $key name: $name) {"
                 "\n        key\n      }\n    }\n  ",
        "variables": {
            "key": key,
            "name": "分组333" + mocks.num()
        }
    })


def rename_report(key):
    """报表 重命名"""
    return generate_param({
        "query": "\n    mutation UpdateTeamReport {\n      "
                 "updateTeamReport (key: $key name: $name) {\n        key\n      }\n    }\n  ",
        "variables": {
            "key": key,
            "name": "每周工时总览-222" + mocks.num()
        }
    })


def del_report(form_key):
    """删除报表"""
    return generate_param({
        "query": "\n    mutation DeleteTeamReport {\n      deleteTeamReport (key: $key) {"
                 "\n        key\n      }\n    }\n  ",
        "variables": {
            "key": form_key
        }
    })


def batch_dowload_file(file_uuids: [str], file_name: str):
    """批量下载文件"""
    return generate_param(
        {
            "resources": file_uuids,
            "file_name": file_name
        }
    )


def update_file(name, desc):
    """参数：更新文件信息"""
    return generate_param({
        "name": name,
        "description": desc
    })


def get_file_info():
    """参数：获取文件信息"""
    return generate_param({})
