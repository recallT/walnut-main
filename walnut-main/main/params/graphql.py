#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""

@File    ：graphql.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/07
@Desc    ： Item graphql 测试数据
"""

from falcons.com.meta import OnesParams
from falcons.ops import generate_param

from main.params.const import ACCOUNT


# ========================================================================================

def _gen_task_graphql(conditions: list):
    """任务筛选器"""
    params = []

    for x in conditions:
        p = OnesParams()
        p.json = {
            'query': "{\n  buckets(groupBy: {tasks: {}}, pagination: {limit: 0, after: \"\", preciseCount: true}) {\n    tasks(filterGroup: $filterGroup, orderBy: $orderBy, limit: 1000, includeAncestors: {pathField: \"path\"}, orderByPath: \"path\") {\n      uuid\n    }\n    key\n    pageInfo {\n      count\n      totalCount\n      startPos\n      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n",
            'variables': {
                'groupBy': None,
                'orderBy': {
                    'position': 'ASC',
                    'createTime': 'DESC'
                },
                'filterGroup': [
                    {
                        'project_in': [
                            f'{ACCOUNT.project_uuid}'
                        ],
                        'issueType_in': [
                            'NYhWwb3y'
                        ],
                    }.update(**x)  # update filter condition
                ],
                'bucketOrderBy': None,
                'search': {
                    'keyword': '',
                    'aliases': []
                }
            }
        }

        p.uri_args({'team_uuid': ACCOUNT.user.team_uuid})

        params.append(p)

    return params


def task_graphql_1():
    """任务筛选器"""

    f1 = filter_conditions()
    return _gen_task_graphql(f1)


def task_graphql_2():
    """任务筛选器"""

    f2 = time_range('createTime') + time_range('serverUpdateStamp')

    return _gen_task_graphql(f2)


def task_graphql_3():
    """任务筛选器"""

    f3 = plan_range('planStartDate') + time_range('planEdnDate')

    return _gen_task_graphql(f3)


def task_graphql_4():
    """任务筛选器"""

    f4 = deadline_range_filter()

    return _gen_task_graphql(f4)


def filter_conditions():
    f = {
        'name_match': '包含标题',
        'name_notMatch': '不包含标题',
        'name_equal': '等于标题',
        'name_notEqual': '不等于标题',
        'statusCategory_in': [
            'to_do'
        ],

        'statusCategory_notIn': [
            'to_do',
        ],
        'priority_in': [
            'Q2utpUFG',
            'NV7eh2Zb',

        ], 'priority_notIn': [
            'Q2utpUFG',
            'NV7eh2Zb',

        ],
        'assign_in': [
            '$currentUser'
        ],

        'owner_in': [
            '$currentUser'
        ],
        'owner_notIn': [
            '$currentUser'
        ],

        'watchers_notEqual': None,

        'watchers_in': [
            '$currentUser'
        ],
        'watchers_notIn': [
            '$currentUser'
        ],
        'number_equal': 32,

        'progress_equal': 5000000,

        'progress_between': {
            'gte': 5000000,
            'lte': 8000000
        },
        'status_in': [
            'WucaUF4x',
            'UEB21pxE',
            '4JUzbhj8',
            'PnQ7ehb1',

        ],

        'subIssueType_in': [
            'EVYVWxmD',

        ],
        'subIssueType_notIn': [
            'EVYVWxmD',

        ],
        # 关联工作项
        "relatedCount_equal": 0,
        "relatedCount_notEqual": 0,
    }

    return [{k: v} for k, v in f.items()]


def deadline_range_filter():
    k = 'deadline_range'
    drf = [
        {
            'equal': '2021-12-01'
        },
        {
            'equal': 'today'
        },
        {
            'equal': 'today+1d'
        },
        {
            'equal': 'today-1d'
        },
        {
            'equal': 'today-7d'
        },
    ]
    return [{k: d} for d in drf]


def plan_range(state):
    """
    
    :param state: planStartDate, planEdnDate
    :return: 
    """
    k = f'{state}_range'
    per = [
        {
            'equal': '2021-12-01'
        }, {
            'not_equal': '2021-12-01'
        },
        {
            'gte': '2021-12-01'
        },
        {
            'lte': '2021-12-01'
        },
        {
            'gte': '2021-12-01',
            'lte': '2021-12-31'
        },
        {
            'equal': 'today-7d'
        }, ]

    return [{k: p} for p in per]


def time_range(time_type):
    """
    
    :param time_type: createTime, serverUpdateStamp
    :return: 
    """
    k = f'{time_type}_range'
    per = [
        {
            'equal': '2021-12-01'
        },
        {
            'not_equal': '2021-12-01'
        },
        {
            'gte': '2021-12-01'
        },
        {
            'lte': '2021-12-01'
        },
        {
            'gte': '2021-12-01',
            'lte': '2021-12-31'
        }, ]

    return [{k: p} for p in per]


def issue_type_scope():
    """
    获取项目工作项的UUID，名称
    :return:
    """

    return generate_param({
        "query": '{\n  buckets(\n    groupBy: {\n      issueTypeScopes: {\n        '
                 'scopeType: {}\n      }\n    }\n  ){\n    scopeType\n    '
                 'issueTypeScopes(filter: $filter, orderBy: $orderBy){\n      '
                 '\n  uuid\n  name\n\n      \n    }\n  }\n}\n',
        "variables": {
            "filter": {
                "scope_in": [ACCOUNT.project_uuid],  # 默认当前项目
                "scopeType_in": [
                    1
                ]
            },
            "orderBy": {
                "namePinyin": "ASC",
                "scopeNamePinyin": "ASC"
            }
        }
    })


def project_graphql():
    """
    项目列表筛选
    :return:
    """
    params = (
        {
            'step_name': '根据「创建时间」筛选（等于）（准确日期）',
            "createTime_range": {
                "equal": "2021-12-14"
            }
        },
        {
            'step_name': '根据「项目负责人」筛选（包含）（成员）',
            "assign_in": [
                "$currentUser"
            ], },
        {
            'step_name': '根据「项目名称」筛选（包含）',
            "name_match": "Pro",
        },
        {
            'step_name': '根据「项目状态」筛选（包含）',
            "status_in": [
                "to_do"
            ]
        },

    )

    grah = []
    for param in params:
        name = param.pop('step_name')

        p = OnesParams()
        p.json = {
            "query": "{\n  buckets(groupBy: $groupBy, pagination: {limit: 50, after: \"\", preciseCount: true}) {\n    key\n    projects(limit: 1000, orderBy: $projectOrderBy, filterGroup: $projectFilterGroup) {\n      key\n      sprintCount\n      taskCount\n      taskCountDone\n      taskCountInProgress\n      taskCountToDo\n      memberCount\n      uuid\n      name\n      status {\n        uuid\n        name\n        category\n      }\n      isPin\n      isSample\n      isArchive\n      statusCategory\n      assign {\n        uuid\n        name\n        avatar\n      }\n      owner {\n        uuid\n        name\n        avatar\n      }\n      createTime\n      planStartTime\n      planEndTime\n      type\n    }\n    key\n    pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n",
            "variables": {
                "projectOrderBy": {
                    "isPin": "DESC",
                    "namePinyin": "ASC",
                    "createTime": "DESC"
                },
                "projectFilterGroup": [
                    {

                        "visibleInProject_equal": True,
                        "isArchive_equal": False,
                    }.update(**param)
                ],
                "groupBy": {
                    "projects": {}
                }
            }
        }
        p.uri_args({'team_uuid': ACCOUNT.user.team_uuid})

        grah.append([name, p])

    return grah


def proj_sort(customize_uuid=None):
    """
    项目列表排序
    :param customize_uuid  自定义属性uuid
    """

    types = {
        'memberCount': ['ASC', 'DESC'],
        'createTime': ['ASC', 'DESC'],
        'sprintCount': ['ASC', 'DESC'],
        'taskCount': ['ASC', 'DESC'],
        'doneTaskPercent': ['ASC', 'DESC'],
        'planEndTime': ['ASC', 'DESC'],
        'planStartTime': ['ASC', 'DESC'],
        'taskCountInProgress': ['ASC', 'DESC'],
        'taskCountToDo': ['ASC', 'DESC'],
        'owner': ['ASC', 'DESC'],
        'assign': ['ASC', 'DESC'],
        'namePinyin': ['ASC', 'DESC'],
        'statusCategory': ['ASC', 'DESC'],
        'taskCountDone': ['ASC', 'DESC'],

    }

    if customize_uuid:
        types.update({f"_{customize_uuid}": ['ASC', 'DESC']})

    params = []

    for key, value in types.items():
        for v in value:
            p = {
                "query": "{\n  buckets(groupBy: $groupBy, pagination: {limit: 50, after: \"\", preciseCount: true}) {\n    key\n    projects(limit: 1000, orderBy: $projectOrderBy, filterGroup: $projectFilterGroup) {\n      key\n      sprintCount\n      taskCount\n      taskCountDone\n      taskCountInProgress\n      taskCountToDo\n      memberCount\n      uuid\n      name\n      status {\n        uuid\n        name\n        category\n      }\n      isPin\n      isSample\n      isArchive\n      statusCategory\n      assign {\n        uuid\n        name\n        avatar\n      }\n      owner {\n        uuid\n        name\n        avatar\n      }\n      createTime\n      planStartTime\n      planEndTime\n      type\n    }\n    key\n    pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n",
                "variables": {
                    "projectOrderBy": {
                        "isPin": "DESC",
                        key: v,
                    },
                    "projectFilterGroup": [
                        {
                            "visibleInProject_equal": True,
                            "isArchive_equal": False
                        }
                    ],
                    "groupBy": {
                        "projects": {}
                    }
                }
            }

            params.append(generate_param(p)[0])

    return params


def proj_group(customize_param=None):
    """
    项目列表-按创建者分组
    :param customize_param  自定义属性参数
    """
    types = {'owner': '{\n      uuid\n      name\n    }\n',
             'status': '{\n      name\n      uuid\n      category\n    }\n',
             'name': '',
             'statusCategory': ''
             }

    if customize_param:
        types = customize_param

    params = []

    for key, value in types.items():
        p = {
            "query": "{\n  buckets(groupBy: $groupBy, pagination: {limit: 50, after: \"\", preciseCount: true}) {\n    key\n    %s %s    projects(limit: 1000, orderBy: $projectOrderBy, filterGroup: $projectFilterGroup) {\n      key\n      sprintCount\n      taskCount\n      taskCountDone\n      taskCountInProgress\n      taskCountToDo\n      memberCount\n      uuid\n      name\n      status {\n        uuid\n        name\n        category\n      }\n      isPin\n      isSample\n      isArchive\n      statusCategory\n      assign {\n        uuid\n        name\n        avatar\n      }\n      owner {\n        uuid\n        name\n        avatar\n      }\n      createTime\n      planStartTime\n      planEndTime\n      type\n    }\n    key\n    pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n" % (
                key, value),
            "variables": {
                "projectOrderBy": {
                    "isPin": "DESC",
                    "namePinyin": "ASC",
                    "createTime": "DESC"
                },
                "projectFilterGroup": [
                    {
                        "visibleInProject_equal": True,
                        "isArchive_equal": False
                    }
                ],
                "groupBy": {
                    "projects": {
                        f"{key}": {}
                    }
                },
                "orderBy": {
                    f"{key}": {
                        "namePinyin": "ASC"
                    }
                }
            }
        }
        params.append(generate_param(p)[0])

    return params


def proj_card_view():
    """项目列表卡片视图"""
    p = {
        "query": "{\n  buckets(groupBy: $groupBy, pagination: {limit: 50, after: \"\", preciseCount: true}) {\n    key\n    projects(limit: 1000, orderBy: $projectOrderBy, filterGroup: $projectFilterGroup) {\n      key\n      taskUpdateTime\n      uuid\n      name\n      status {\n        uuid\n        name\n        category\n      }\n      isPin\n      isSample\n      isArchive\n      statusCategory\n      assign {\n        uuid\n        name\n        avatar\n      }\n      owner {\n        uuid\n        name\n        avatar\n      }\n      createTime\n      planStartTime\n      planEndTime\n      type\n    }\n    key\n    pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n",
        "variables": {
            "projectOrderBy": {
                "isPin": "DESC",
                "namePinyin": "ASC",
                "createTime": "DESC"
            },
            "projectFilterGroup": [
                {
                    "visibleInProject_equal": True,
                    "isArchive_equal": False
                }
            ],
            "groupBy": {
                "projects": {}
            }
        }
    }

    return generate_param(p)


def proj_table_view():
    """项目列表表格视图"""
    p = {
        "query": "{\n  buckets(groupBy: $groupBy, pagination: {limit: 50, after: \"\", preciseCount: true}) {\n    key\n    projects(limit: 1000, orderBy: $projectOrderBy, filterGroup: $projectFilterGroup) {\n      key\n      sprintCount\n      taskCount\n      taskCountDone\n      taskCountInProgress\n      taskCountToDo\n      memberCount\n      uuid\n      name\n      status {\n        uuid\n        name\n        category\n      }\n      isPin\n      isSample\n      isArchive\n      statusCategory\n      assign {\n        uuid\n        name\n        avatar\n      }\n      owner {\n        uuid\n        name\n        avatar\n      }\n      createTime\n      planStartTime\n      planEndTime\n      type\n    }\n    key\n    pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n",
        "variables": {
            "projectOrderBy": {
                "isPin": "DESC",
                "namePinyin": "ASC",
                "createTime": "DESC"
            },
            "projectFilterGroup": [
                {
                    "visibleInProject_equal": True,
                    "isArchive_equal": False
                }
            ],
            "groupBy": {
                "projects": {}
            }
        }
    }

    return generate_param(p)

