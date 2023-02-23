"""
@File    ：relation.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/25
@Desc    ：
"""
from falcons.helper import mocks
from falcons.ops import generate_param

from main.params.const import ACCOUNT


def add_relation(r_type):
    """
    添加前置依赖/后置影响
    :return:
    """

    return generate_param(
        {
            'query': 'mutation ActivityRelationLink { \n    addActivityRelationLink (relation_type:'
                     '$relation_type chart_uuid: $chart_uuid source: $source target: $target) {\n'
                     '    key\n    } \n    }\n',
            'variables': {
                'relation_type': r_type,
                'chart_uuid': '',  # 项目计划甘特图的UUID
                'source': '',  # 起 工作项UUID
                'target': ''  # 止 工作项 UUID
            }
        }
    )


def update_gantt_data(**kwargs):
    """
    项目计划添加计划前置依赖/后置影响
    :return:
    """

    return generate_param({
        "query": 'mutation UpdateGanttData {\n          updateActivity (relation_type: $relation_type key: '
                 '$key id: $id target: $target source: $source) {\n            key\n          }\n        }\n      ',
        "variables": kwargs
        #     {
        #     "relation_type": r_type_mapper.get(r_type),
        #     "key": f"activity-{source}",
        #     "id": f"{source}-{target}-{r_type_mapper.get(r_type)}",
        #     "target": target,
        #     "source": source
        # }
    })


def del_relation():
    """
    删除依赖
    :return: 
    """

    return generate_param(
        {
            'query': 'mutation DeleteActivityRelationLink {\n        deleteActivityRelationLink(key: $key)'
                     '{key}\n      }\n    ',
            'variables': {
                # activity_relation_link-7CU6yrjuIN4NRnh9-7CU6yrjuLqRfkTbY-start_to_start-QjS6D1fQ
                'key': ''  # 依赖关系key
            }
        }
    )


def chart_uuid(project_uuid=''):
    """
    获取项目的甘特图UUID

    使用 ItemGraphql 接口

    :return:
    """
    p_uid = project_uuid if project_uuid else ACCOUNT.project_uuid

    return generate_param(
        {
            'query': 'query PPMProjectChartInfo {\n            activityCharts(\n              filter:{\n'
                     '                project_in:[\"%s\"]\n              }) {\n              '
                     'key\n              name\n              uuid\n              drafting\n              '
                     'personalConfig {\n                key\n                zooming\n'
                     '              }\n              config {\n                key\n                '
                     'settings\n              }\n            }\n          }\n' % p_uid
        }
    )


def query_relation_links(t_type):
    """
    查询前置/后置管理工作项等
    :return: 
    """

    t_mapper = {
        'pre': 'target',  # 前置使用target 查询
        'post': 'source'  # 后置使用source 查询
    }

    return generate_param(
        {
            'query': 'query ActivityRelationLinks {\n    activityRelationLinks(filter: $filter) '
                     '{\n      key\n      target {\n        uuid\n        name\n        canBrowse\n'
                     '        chart {\n          project {\n            uuid\n          }\n        }\n'
                     '      }\n      targetTask \n{\n  key\n  uuid\n  name\n  project {\n    uuid\n'
                     '    activityChart {\n      uuid\n    }\n  }\n  assign {\n    key\n    uuid\n'
                     '    name\n    avatar\n  }\n  status {\n    uuid\n    name\n    namePinyin\n'
                     '    category\n    builtIn\n    detailType\n  }\n  priority {\n    bgColor\n'
                     '    color\n    uuid\n    value\n    position\n  }\n  deadline\n  issueType {\n'
                     '    key\n    uuid\n    name\n    builtIn\n    detailType\n    namePinyin\n'
                     '    icon\n    subIssueType\n  }\n  subIssueType {\n    key\n    uuid\n'
                     '    value: uuid\n    name\n    label: name\n    builtIn\n    detailType\n'
                     '    namePinyin\n    icon\n  }\n  owner {\n    key\n    uuid\n    name\n'
                     '    avatar\n  }\n  importantField {\n    bgColor\n    color\n    fieldUUID\n'
                     '    name\n    value\n  }\n  canView(attachPermission:{\n    permissions:[\"view_tasks\"],\n'
                     '  })\n  canEdit(attachPermission:{\n    permissions:[\"update_tasks\"],\n  })\n}\n\n'
                     '      targetType\n      relationType\n      chartUUID\n    }\n  }\n',
            'variables': {
                'filter': {
                    t_mapper.get(t_type): {
                        'uuid_equal': ''  # 源工作项的UUID
                    }
                }
            }
        }
    )


def auto_schedule():
    """自动排期接口参数"""
    return generate_param({}, **{'project_uuid': ACCOUNT.project_uuid, 'chart_uuid': ''})


def add_plans_or_milestones(p_type='ppm'):
    """创建项目计划/里程碑"""

    p_mapper = {
        'ppm': 'ppm_task',
        'milestone': 'milestone'
    }

    start_time = mocks.now_timestamp() if p_type == 'ppm' else mocks.day_timestamp(2)

    return generate_param(
        {
            "query": 'mutation AddGanttData {\n            addActivity (name: $name assign: '
                     '$assign chart_uuid: $chart_uuid type: $type progress: $progress start_time: '
                     '$start_time end_time: $end_time parent: $parent) '
                     '{\n              key\n            }\n          }\n        ',
            "variables": {
                "name": f"{p_mapper.get(p_type)}-{mocks.num()}",
                "assign": ACCOUNT.user.owner_uuid,
                "chart_uuid": '',  # 项目chart_uuid
                "type": p_mapper.get(p_type),
                "progress": 0,
                "start_time": start_time,
                "end_time": mocks.day_timestamp(4),
                "parent": ''
            }
        }
    )


def add_parent_plan(parent, after=''):
    return generate_param({
        "query": "\n          mutation AddGanttData {\n            addActivity (name: $name chart_uuid: $chart_uuid assign: $assign type: $type progress: $progress start_time: $start_time end_time: $end_time parent: $parent after: $after) {\n              \n        \nkey\nname\nganttDataType: type\nuuid\nnumber\nprogress\nparent\ncreateTime\nchartUUID\nplanStartTime: startTime\nplanEndTime: endTime\ncanBrowse\ncanModify\ncanModifyProgress\ncanModifyPlanTimes\ntarget {\n  relationType\n  target {\n    uuid\n  }\n}\nsource{\n  relationType\n  source {\n    uuid\n  }\n}\nposition\nassign {\n  uuid\n  name\n  avatar\n}\n\n        \n  \n  relatedTaskUUID\n  relatedTaskStatus{uuid name}\n  relatedTaskParent{uuid}\n  relatedTaskIssueType{icon uuid}\n  relatedTaskSubIssueType{icon uuid}\n  relatedProjectUUID\n\n  task {\n    uuid\n    parent {\n      uuid\n    }\n    issueType {\n      icon\n      uuid\n    }\n    subIssueType {\n      icon\n      uuid\n    }\n    status {\n      uuid\n      name\n    }\n    project {\n      uuid\n    }\n  }\n  sprint {\n    uuid\n  }\n  estimatedHours\n  totalManhour\n  remainingManhour\n  isVirtual\n\n      \n            }\n          }\n        ",
        "variables": {
            "name": "子项目计划" + mocks.num(),
            "chart_uuid": "",  # 项目chart_uuid,
            "assign": ACCOUNT.user.owner_uuid,
            "type": "ppm_task",
            "progress": 0,
            "start_time": mocks.now_timestamp(),
            "end_time": mocks.day_timestamp(1),
            "parent": parent,
            "after": after
        }
    })


def update_gantt(**kwargs):
    """更新计划/里程碑数据"""
    if not kwargs:
        raise ValueError('没有更新测试数据！')

    mutation_keys = [f'{k}: ${k}' for k in kwargs.keys()]
    # key: $key start_time: $start_time end_time: $end_time)
    mutation_keys = ' '.join(mutation_keys)
    m = {
        "query": '\n        mutation UpdateGanttData {\n          updateActivity'
                 ' (%s)'
                 '{\n            key\n          }\n        }\n      ' % mutation_keys,
        "variables": kwargs
        # 需要更新的数据 形如 {
        #     "key": "activity-TTnbsmmd",
        #     "start_time": 1648699200,
        #     "end_time": 1648699200
        # }
    }
    return generate_param(m)


def proj_plan_info(plan_uuid):
    return generate_param({
        "query": "\n      query PPMActivityDetail {\n        activity(\n          key: \"%s\"\n        ) {\n          key\n          name\n          uuid\n          type\n          progress\n          createTime\n          updateTime\n          startTime\n          endTime\n          position\n          description\n          number\n          \n    ppmTask {\n      uuid\n    }\n    milestone {\n      uuid\n    }\n  \n\n          \n    milestone {\n      uuid\n    }\n    deliverable{\n      uuid\n      key\n      number\n      commitTime\n      name\n      type\n      committer{\n        name\n        uuid\n        avatar\n      }\n      content{\n        name\n        size\n        resource_uuid\n        page_uuid\n      }\n    }\n          \n          target {\n            relationType\n            target {\n              uuid\n            }\n          }\n          source{\n            relationType\n            source {\n              uuid\n            }\n          }\n          assign {\n            uuid\n            name\n            avatar\n          }\n          owner {\n            uuid\n            name\n            avatar\n          }\n        }\n      }\n    "
                 % plan_uuid})


def update_proj_plan_info(field_name, field_value, key):
    return generate_param({
        "query": "\n        mutation UpdateGanttData {\n          updateActivity (%s: $%s key: $key) {\n            key\n          }\n        }\n      " % (
            field_name, field_name),
        "variables": {
            field_name: field_value,
            "key": key
        }
    })


def update_snapshot_info(key, field_name, field_value):
    return generate_param({
        "query": "\n        mutation UpdateActivityRelease {\n          updateActivityRelease (key: $key %s: $%s) {\n            key\n          }\n        }\n      " % (
            field_name, field_name),
        "variables": {
            "key": key,
            field_name: field_value
        }
    })


def update_proj_milestone_info(key, time):
    return generate_param({
        "query": "\n        mutation UpdateGanttData {\n          updateActivity (key: $key start_time: $start_time end_time: $end_time) {\n            key\n          }\n        }\n      ",
        "variables": {
            "key": key,
            "start_time": time,
            "end_time": time
        }
    })


def add_proj_plan_message(query, variables):
    """项目计划 评论操作参数"""
    return generate_param({
        "query": query,
        "variables": variables
    })


def del_gantt(key):
    """删除计划/里程碑数据"""
    return generate_param(
        {
            "query": 'mutation DeleteGanttData {\n            deleteActivity(\n'
                     '              key: \"%s\"\n            ) {\n'
                     '              key\n            }\n          }\n' % key
        }
    )


def external_activity():
    """关联工作项/迭代 到测试计划"""
    return generate_param(
        {
            "chart_uuid": '',  # 项目chart_uuid
            "add": [
                # 需要关联的工作项/迭代数据 形如
                # {
                #     "object_id": "EqEHHMRu",
                #     "object_type": "sprint"
                # }
            ]
        },
        **{'activity_uuid': ''}, is_project=True
    )


def gantt_list():
    """"""
    j = ACCOUNT.stamp_data

    issue_conf_uid = [c['issue_type_uuid'] for c in j['issue_type_config']['issue_type_configs'] if
                      c['name'] in ('需求', '任务')]

    return generate_param(
        {
            "query": '\n      query GanttData {\n        activities (orderBy: $orderBy filterGroup: $filterGroup)'
                     '{\n          \nkey\nname\nganttDataType: '
                     'type\nuuid\nnumber\nprogress\nparent\ncreateTime\nchartUUID\nplanStartTime:'
                     ' startTime\nplanEndTime: endTime\ncanBrowse\ncanModify\ncanModifyProgress\n'
                     'canModifyPlanTimes\ntarget {\n  relationType\n  target {\n    uuid\n  }\n}\n'
                     'source{\n  relationType\n  source {\n    uuid\n  }\n}\nposition\nassign {\n  uuid\n'
                     '  name\n  avatar\n}\npreDependencyCount\npostDependencyCount\n\n'
                     '          \n      \n          reminders\n          \n          \n        '
                     '\n      \n  task {\n    uuid\n    parent {\n      uuid\n    }\n    issueType {\n      '
                     'icon\n      uuid\n    }\n    subIssueType {\n      icon\n      uuid\n    '
                     '}\n    status {\n      uuid\n      name\n    }\n  }\n  sprint {\n    '
                     'uuid\n  }\n  estimatedHours\n  totalManhour\n  remainingManhour\n  isVirtual\n\n    '
                     '\n          ppmTask{\n            uuid\n          }\n          milestone{\n            uuid\n'
                     '          }\n          deliverable{\n            uuid\n            key\n'
                     '            number\n            commitTime\n            name\n            type\n'
                     '            committer{\n                name\n                uuid\n'
                     '                avatar\n            }\n            content{\n                name\n'
                     '                size\n                resource_uuid\n                page_uuid\n'
                     '            }\n          }\n        }\n      }\n    ',
            "variables": {
                "orderBy": {
                    "number": "desc",
                    "position": "ASC"
                },
                "filterGroup": [
                    {
                        "isVirtual_in": [
                            False
                        ],
                        "chartUUID_in": [
                            ''  # 项目的 chart_uuid
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
                            ''  # 项目的 chart_uuid
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
                            # 需求 和 任务 的 issue_type uuid 形如
                            # ["NAFqwKNf", "54NUEJzQ"]
                            "issueType_in": issue_conf_uid,

                        },
                        "chartUUID_in": [
                            ''  # 项目的 chart_uuid
                        ]
                    }
                ]
            }
        }
    )


def connecred_task_and_sprint(chart_uuid):
    return generate_param({
        "query": "\n    query ExternalActivities {\n      externalActivities: activities (\n        filter: {\n          chartUUID_in: [\"%s\"],\n          type_in: [\"parent_task\", \"task\", \"parent_sprint\", \"sprint\"],\n          isVirtual_in: [false]\n        }\n      ) {\n        key\n        type\n        task {\n          uuid\n        }\n        sprint {\n          uuid\n        }\n      }\n    }\n  " % chart_uuid,
        "variables": {}
    })


def export_gantt():
    """导出项目计划"""
    j = ACCOUNT.stamp_data

    issue_conf_uid = [c['issue_type_uuid'] for c in j['issue_type_config']['issue_type_configs'] if
                      c['name'] in ('需求', '任务')]

    return generate_param(
        {
            "gql":
                {
                    "query": '\n      query GanttData {\n        activities (orderBy: $orderBy filterGroup: $filterGroup)'
                             '{\n          \nkey\nname\nganttDataType: '
                             'type\nuuid\nnumber\nprogress\nparent\ncreateTime\nchartUUID\nplanStartTime:'
                             ' startTime\nplanEndTime: endTime\ncanBrowse\ncanModify\ncanModifyProgress\n'
                             'canModifyPlanTimes\ntarget {\n  relationType\n  target {\n    uuid\n  }\n}\n'
                             'source{\n  relationType\n  source {\n    uuid\n  }\n}\nposition\nassign {\n  uuid\n'
                             '  name\n  avatar\n}\npreDependencyCount\npostDependencyCount\n\n'
                             '          \n      \n          reminders\n          \n          \n        '
                             '\n      \n  task {\n    uuid\n    parent {\n      uuid\n    }\n    issueType {\n      '
                             'icon\n      uuid\n    }\n    subIssueType {\n      icon\n      uuid\n    '
                             '}\n    status {\n      uuid\n      name\n    }\n  }\n  sprint {\n    '
                             'uuid\n  }\n  estimatedHours\n  totalManhour\n  remainingManhour\n  isVirtual\n\n    '
                             '\n          ppmTask{\n            uuid\n          }\n          milestone{\n            uuid\n'
                             '          }\n          deliverable{\n            uuid\n            key\n'
                             '            number\n            commitTime\n            name\n            type\n'
                             '            committer{\n                name\n                uuid\n'
                             '                avatar\n            }\n            content{\n                name\n'
                             '                size\n                resource_uuid\n                page_uuid\n'
                             '            }\n          }\n        }\n      }\n    ',
                    "variables": {
                        "orderBy": {
                            "number": "desc",
                            "position": "ASC"
                        },
                        "filterGroup": [
                            {
                                "isVirtual_in": [
                                    False
                                ],
                                "chartUUID_in": [
                                    ''  # 项目的 chart_uuid
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
                                    ''  # 项目的 chart_uuid
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
                                    # 需求 和 任务 的 issue_type uuid 形如
                                    # ["NAFqwKNf", "54NUEJzQ"]
                                    "issueType_in": issue_conf_uid,

                                },
                                "chartUUID_in": [
                                    ''  # 项目的 chart_uuid
                                ]
                            }
                        ]
                    }
                }
        }, is_project=True
    )


def add_activity(is_base=True):
    """添加活动(创建快照等)
    is_base:是否设置为基线
    """

    return generate_param({
        "query": 'mutation AddActivityRelease {\n            addActivityRelease (project: '
                 '$project chart_uuid: $chart_uuid is_base: $is_base name: $name) {\n              '
                 'key\n            }\n          }\n      ',
        "variables": {
            "project": ACCOUNT.project_uuid,
            "chart_uuid": "",
            "is_base": is_base,
            "name": "KuaiZhaoTest"
        }
    })


def gantt_history(activity_key):
    """甘特图历史记录"""
    q = {
        "query": 'query GanttHistory {\n        activityRelease(\n          key: '
                 '\"%s\"\n        ) {\n          key\n          '
                 'data\n        }\n      }\n    ' % activity_key
    }

    return generate_param(q)


def todo_sprint_info(issue_uuid_list):
    """待办事项内 迭代信息"""
    return generate_param({
        "query": "\n{\n  sprints (\n    filterGroup: $filterSprintGroup\n  ) {\n      key\n      createTime\n      name\n      uuid\n      scale\n      adviceScale\n      project {\n        uuid\n      }\n      status {\n        category\n        name\n      }\n      startTime\n      endTime\n  }\n  buckets (\n    groupBy: {\n        tasks: {\n          sprint: {}\n        }\n    }\n    orderBy: {\n      sprint: {\n          createTime: DESC\n      }\n    }\n  ) {\n    key\n    tasks (\n      filterGroup: $filterTaskGroup\n      orderBy: $taskOrderBy\n    ) {\n        key\n        \n    uuid\n    name\n    number\n    priority{\n      bgColor\n      color\n      value\n      uuid\n    }\n    serverUpdateStamp\n    issueType{\n      uuid\n      name\n      icon\n    }\n    _field032\n    publishVersion{\n      uuid\n      name\n    }\n\n    }\n  }\n}",
        "variables": {
            "filterSprintGroup": [
                {
                    "project_in": [
                        ACCOUNT.project_uuid
                    ],
                    "status": {
                        "category_notEqual": "done"
                    }
                }
            ],
            "filterTaskGroup": [
                {
                    "alternativeIssueType_in": issue_uuid_list,
                    "project_in": [
                        ACCOUNT.project_uuid
                    ],
                    "status": {
                        "category_notEqual": "done"
                    },
                    "publishVersion_equal": None
                }
            ],
            "taskOrderBy": {
                "rank": "ASC",
                "createTime": "DESC"
            }
        }
    })
