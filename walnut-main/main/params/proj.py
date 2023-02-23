#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：proj.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/3 
@Desc    ：
"""
from falcons.com.meta import OnesParams, UiMeta
from falcons.helper import mocks
from falcons.helper.mocks import ones_uuid
from falcons.ops import generate_param
from main.params.const import ACCOUNT


def copy_case():
    """案例拷贝参数"""
    p = OnesParams()
    p.json = {
        'target_library_uuid': 'PBZGkbSD',
        'target_module_uuid': '8mK8p83t',
        'case_uuids': [
            'WT1RDPrj',
            'SjfNsZAW']
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'lib_uuid': ''
            },
    }
    return p,


def add_project(name=None, owner_uuid=None):
    """添加项目-测试参数"""

    ags = (
        {'name': 'SamplePrj', 'temp_id': 'project-t2', },
        {'name': 'AgileProj', 'temp_id': 'project-t1', },
        {'name': '瀑布式项目', 'temp_id': 'project-t4', },
        {'name': '敏捷项目', 'temp_id': 'project-t5'}
    )

    owner_uuid = ACCOUNT.user.owner_uuid if not owner_uuid else owner_uuid

    args = [{
        'project': {
            'uuid': ones_uuid(owner_uuid),
            'owner': owner_uuid,
            'name': name if name else a['name'],
            'status': 1,
            'members': []
        },
        'template_id': a['temp_id'],
        'members': [
            owner_uuid
        ]
    } for a in ags]

    return generate_param(args)


def my_project_list():
    """项目列表-测试参数"""

    p = OnesParams()

    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }

    return p,


def dashboard_uuid():
    p = OnesParams()
    p.json = {
        'dashboard': 0
    }
    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid,
                })
    return p,


def proj_stamp(param: dict = None):
    """获取项目stamp 数据"""
    if param:
        p = param
    else:
        p = {
            "component": 0,
            "sprint": 0,
            "issue_type_config": 0,
            "field_config": 0,
            "task_status_config": 0,
            "transition": 0,
            "role_config": 0,
            "project": 0
        }

    return generate_param(p, is_project=True)


def component_template_stamp():
    """获取项目项目组件模版数据"""
    return generate_param({
        "component_template": 0,
    })


# ==========================================================================================

def proj_copy():
    """
    拷贝项目
    :return:
    """

    p = OnesParams()
    uid = ones_uuid()
    p.json = {
        'project_uuid': ACCOUNT.project_uuid,  # assign in case
        'project_name': f'CopyPrj{uid}',
        'issue_types': [],
        'options': [],
        'members': [
            ACCOUNT.user.owner_uuid
        ]
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }

    return p,


def proj_delete():
    """
    删除项目
    :return:
    """

    p = OnesParams()
    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid,
                'project_uuid': '',  # assign in case
                })

    return p,


def proj_archive():
    """归档项目"""
    return generate_param({
        "item": {
            "is_archive": True
        }
    })


def sprint_status():
    """迭代状态更新"""
    params = [
        {'name': '未开始-进行中', 'category': ('to_do', 'in_progress'), },
        {'name': '进行中-未开始', 'category': ('in_progress', 'to_do'), },
    ]
    status = []
    for param in params:
        name = param.pop('name')
        n = name.split('-')
        p = OnesParams()

        _now = mocks.now_timestamp()
        p.json = {
            'sprint_statuses': [
                {
                    'status_uuid': 'GvXmBfRG',  # update in case
                    'name': n[0],
                    'category': param['category'][0],
                    'plan_start_time': _now,
                    'plan_end_time': None,
                    'actual_start_time': _now,
                    'actual_end_time': None,
                    'is_current_status': False,
                    'desc_plain': "",
                    'desc_rich': ""
                },
                {
                    'status_uuid': 'AzHj4Jwm',  # update in case
                    'name': n[1],
                    'category': param['category'][1],
                    'plan_start_time': _now,
                    'plan_end_time': None,
                    'actual_start_time': _now,
                    'actual_end_time': None,
                    'is_current_status': True,
                    'desc_plain': "",
                    'desc_rich': ""
                }
            ]
        }
        p.uri_args({'team_uuid': ACCOUNT.user.team_uuid, 'project_uuid': ACCOUNT.project_uuid, 'sprint_uuid': ''})

        status.append([name, p])

    return status


def sprint_add(assign=None):
    """新增迭代"""
    p = OnesParams()

    p.json = {
        'sprints': [
            {
                'title': 'NewSprint' + mocks.num(),
                'assign': assign if assign else ACCOUNT.user.owner_uuid,
                'start_time': mocks.now_timestamp(),
                'end_time': mocks.day_timestamp(),  # 2 周后
                'period': '2w',
                'statuses': [],
                'fields': []
            }
        ]
    }
    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid, 'project_uuid': ACCOUNT.project_uuid})

    return p,


def sprint_delete():
    """删除迭代"""
    p = OnesParams()
    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid, 'project_uuid': ACCOUNT.project_uuid, 'sprint_uuid': ''})

    return p,


def sprint_goal(uuid):
    """迭代描述"""
    return generate_param({
        'sprints': [
            {
                "uuid": uuid,
                "goal": "迭代描述" + mocks.num(),
                "fields": [],
                "statuses": []
            }
        ]
    })


def ui_prj_name():
    """项目名称"""
    proj_name = (UiMeta.env.proj_name, '未开始', 'NoTestData')

    return proj_name


def add_program():
    """添加项目集"""
    p = OnesParams()
    p.json = {
        'item': {
            'item_type': 'program',
            'name': f'Auto项目集{mocks.ones_uuid()[:4]}',
            'related_type': 'none',
            "plan_start_time": None,
            "plan_end_time": None,
            'parent': "",
            'assign': ACCOUNT.user.member_uuid,  # 默负责人 是 团队管理员
        }
    }
    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid})

    return p,


def delete_program():
    """删除项目集"""
    p = OnesParams()

    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid, 'item_key': ''})

    return p,


def list_program():
    """项目集列表"""

    p = OnesParams()

    p.json = {
        'query': 'query PROGRAMS($filter: Filter, $orderBy: OrderBy) {\n    programs(filter: $filter, orderBy: '
                 '$orderBy) {\n      key\n      uuid\n      relatedType\n      parent\n      name\n      isPin\n      '
                 'project {\n        \n        uuid\n        name\n        status {\n          uuid\n          '
                 'name\n          category\n        }\n        isPin\n        statusCategory\n        '
                 'assign {\n          uuid\n          name\n          avatar\n        }\n        '
                 'planStartTime\n        planEndTime \n        sprintCount\n        taskCount\n        '
                 'taskCountDone\n        taskCountInProgress\n        taskCountToDo\n        '
                 'memberCount\n        progress\n      }\n    }\n  }',
        'variables': {
            'filter': {
                'ancestors_in': [  # 项目集UUID
                ]
            },
            'orderBy': {
                'isPin': 'DESC',
                'namePinyin': 'ASC'
            }
        }
    }

    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid})

    return p,


def list_program_role():
    """
    获取项目集成员role信息
    ItemGq
    :return:
    """

    p = OnesParams()

    p.json = {
        'query': 'query ROLES($filter: Filter, $orderBy: OrderBy) {\n    roles (filter: $filter, orderBy: '
                 '$orderBy) {\n      key\n      uuid\n      name\n      members {\n        uuid\n        '
                 'name\n        syncTypes\n        email\n        avatar\n      }\n    }\n  }',
        'variables': {
            'filter': {
                'context': {
                    'programUUID_equal': ''  # 项目集uuid
                }
            },
            'orderBy': {
                'namePinyin': 'ASC'
            }
        }
    }

    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid})

    return p,


def program_search_user(keyword='normal'):
    """搜索用户"""

    p = OnesParams()

    p.json = {
        'keyword': keyword,  # 按字符串 normal 搜索, 因为在添加团队时有部分用户名记录为了 normal1
        'status': [
            1
        ],
        'team_member_status': [
            1
        ],
        'search_cols': [
            'name',
            'email',
            'name_pinyin',
            'department_name',
            'group_name'
        ]
    }

    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid})

    return p,


def sprint_search_user(permission):
    return generate_param({
        "keyword": "",
        "status": [
            1
        ],
        "team_member_status": [
            1
        ],
        "permission_list": [
            {
                "context_type": "project",
                "context_param": {
                    "project_uuid": ACCOUNT.project_uuid
                },
                "permission": permission
            }
        ]
    })


def add_program_user():
    """添加项目成员"""

    p = OnesParams()

    p.json = {
        'item': {
            'members': []
        }
    }

    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid, 'item_key': ''})

    return p,


def program_list_project():
    """显示项目列表"""

    p = OnesParams()
    p.json = {
        'query': 'query PROJECTS($filter: Filter, $orderBy: OrderBy) {\n    projects(filter: $filter, orderBy: '
                 '$orderBy) {\n      \n      key\n      uuid\n      name\n      status {\n        uuid\n        '
                 'name\n        category\n      }\n      isPin\n      statusCategory\n      assign {\n        '
                 'uuid\n        name\n        avatar\n      }\n      planStartTime\n      planEndTime \n      '
                 'taskUpdateTime\n      sprintCount\n      taskCount\n      taskCountDone\n      '
                 'taskCountInProgress\n      taskCountToDo\n      memberCount\n    }\n  }',
        'variables': {
            'filter': {
                'visibleInPlan_equal': True
            },
            'orderBy': {
                'isPin': 'DESC',
                'namePinyin': 'ASC'
            }
        }
    }
    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid})

    return p,


def program_add_project():
    """
    项目集添加项目
    ItemAddBatch
    :return:
    """

    p = OnesParams()
    p.json = {
        'items': [
            {
                'item_type': 'program',
                'parent': '',  # 项目集UUID
                'related_type': 'project',
                'project': ''  # 项目UUID
            },

        ]
    }
    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid})

    return p,


def program_delete_project():
    """批量删除/删除项目"""
    p = OnesParams()
    p.json = {
        'keys': [  # 关联项目uuid
            'program-K5Hp5hM1'
        ]
    }
    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid})

    return p,


def proj_list_edit(key_name, value):
    """项目列表编辑"""

    return generate_param({
        "item": {
            key_name: value
        }
    })


# ==========================================================================================

def devops_add(ok=True):
    """
    添加 devops

    :return:
    """

    p = OnesParams()
    p.json = {
        "item": {
            "item_type": "devops_ci_sync",
            "ci_server_url": "http://119.23.154.208:8080/",
            "ci_server_type": "jenkins",
            "certification_type": "token",
            "account": "zeno" if ok else 'zeno1',
            "certification": "Imok-2023"
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }

    return p,


def devops_list():
    """
    devops list

    :return:
    """

    p = OnesParams()
    p.json = {
        "query": 'query devopsCiSyncs($filter:Filter,$orderBy:OrderBy){\n  devopsCiSyncs(filter:$filter,orderBy:'
                 '$orderBy){\n        uuid\n        ciServerUrl\n        ciServerType\n        '
                 'certificationType\n        account\n        certification\n        createTime\n        '
                 'syncPipelineCount\n        pipelineCount\n        syncStatus\n    }}',
        "variables": {
            "filter": {},
            "orderBy": {}
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }

    return p,


def pipeline_list():
    """
    查询pipline 列表

    :return:
    """

    p = OnesParams()
    p.json = {
        "query": 'query DEVOPSPIPELINES($filter:Filter, $orderBy:OrderBy){\n        '
                 'devopsPipelines(filter:$filter,orderBy:$orderBy){\n          uuid\n          '
                 'name\n          namePinyin\n          pipelineUrl\n          repo\n          '
                 'branch\n          lastRunStatus\n          lastRunUUID\n          createTime\n          '
                 'createBy\n          isPin\n          path\n          type\n          owner{\n              '
                 'name\n          }\n          lastPipelineRun{\n              uuid\n              '
                 'number\n              duration\n              startTime\n              triggerBy\n              '
                 'status\n          }\n          projects{\n            uuid,\n            name\n    }\n      '
                 'ciSync{\n            uuid\n            ciServerUrl\n          }\n          children{\n    '
                 'uuid\n            name\n            namePinyin\n            repo\n            branch\n    '
                 'lastRunStatus\n            createTime\n            createBy\n            isPin\n  '
                 'lastRunUUID\n            lastSuccessRunUUID\n            pipelineUrl\n            type\n  '
                 'ciSync{\n                uuid\n                ciServerUrl\n            }\n            '
                 'lastPipelineRun{\n                uuid\n                number\n                '
                 'duration\n                startTime\n                triggerBy\n                '
                 'status\n            }\n        }\n        }\n    }',
        "variables": {
            "filter": {
                "type_in": [
                    "pipeline",
                    "free_style",
                    "multi_branch_pipeline"
                ]
            },
            "orderBy": {
                "isPin": "DESC",
                "namePinyin": "ASC"
            }
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }

    return p,


def pipeline_run_history():
    """
    查询 pipline 构建历史

    :return:
    """

    p = OnesParams()
    p.json = {
        "query": 'query DEVOPSPIPELINERUNS($filter:Filter, $orderBy:OrderBy){\n        '
                 'devopsPipelineRuns(filter:$filter,orderBy:$orderBy){\n          '
                 'uuid\n          number\n          duration\n          startTime\n          '
                 'triggerType\n          triggerBy\n          status\n          repo\n          '
                 'branch\n          pipelineUUID\n        }\n    }',
        "variables": {
            "filter": {
                "pipelineUUID_in": [
                    "2bc4usnb"  # assign in case
                ]
            },
            "orderBy": {
                "number": "DESC"
            }
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }

    return p,


def pipeline_pin():
    """
    pip or unpin
    :return:
    """
    p = OnesParams()
    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid, 'pipeline_uuid': ''})
    return p,


def devops_delete():
    p = OnesParams()
    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid, 'pipeline_uuid': ''})
    return p,


# ==========================================================================================


def user_view():
    """用户视图列表"""
    p = OnesParams()
    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid, 'component_uuid': ''})
    return p,


def delete_view():
    """删除视图"""
    p = OnesParams()
    p.uri_args({'team_uuid': ACCOUNT.user.team_uuid, 'component_uuid': '', 'view_uuid': ''})
    return p,


def w_config_update(t_type):
    """
    系统配置-工时模式切换

    :param t_type: 'detailed' or 'simple'
    :return:
    """
    return generate_param({
        "configs": [
            {
                "type": "manhour_mode",
                "data": t_type
            }
        ]
    })


def queues_list():
    """后台任务进度查询"""
    return generate_param()


def add_prj_plan_component():
    """
    添加项目组件信息

    :return:
    """

    return generate_param({
        'components': [
            {
                "uuid": ones_uuid(),
                "template_uuid": "com00014",
                "project_uuid": ACCOUNT.project_uuid,
                "parent_uuid": "",
                "name": "项目计划",
                "name_pinyin": "xiang4mu4ji4hua4",
                "desc": "“项目计划”组件包含计划和里程碑，支持通过 WBS 拆解计划，支持对比项目计划的历史版本。",
                "permissions": [
                    {
                        "permission": "view_component",
                        "user_domains": [
                            {
                                "user_domain_type": "everyone",
                                "user_domain_param": ""
                            },
                            {
                                "user_domain_type": "project_administrators",
                                "user_domain_param": ""
                            }
                        ]
                    }
                ],
                "objects": [],
                "type": 2,
                "views": [],
                "update": 1
            },  # 需要补充原组件信息
        ],
    }, is_project=True)


def add_prj_component(component_template: dict):
    """
    添加项目组件信息
    ：param: settings 有些组件带有该参数
    :return:
    """
    c_param = {
        'uuid': mocks.ones_uuid(),
        'template_uuid': component_template['uuid'],
        'project_uuid': ACCOUNT.project_uuid,
        'parent_uuid': component_template.get('parent_uuid', ''),
        'name': component_template['name'],
        'name_pinyin': component_template['desc'],
        'desc': component_template['desc'],
        'permissions': component_template['permissions'],
        'objects': component_template['objects'],
        'type': component_template['type'],
        'views': component_template['default_views'],
        'update': 1,
        'settings': component_template['settings']
    }

    return generate_param({
        'components': [
            c_param,  # 需要补充原组件信息
        ],
    }, is_project=True)


def update_prj_component(component: dict):
    """参数-更新项目组件"""
    component['update'] = 1
    return generate_param({
        'components': [
            component
        ]
    }, is_project=True)


def remove_plan_component():
    """移除项目计划组件"""

    return generate_param({
        'components': []  # 这里是需要保留的所有组件UUID数据 形如 {'uuid': '' }
    }, is_project=True)


def issue_task_status():
    """工作项状态配置"""
    return generate_param({
        'task_status': 0,
    })


def pro_step_properties_up(issue_type, process_uuid, field_uuid):
    """
    更新步骤属性
    :param issue_type  工作项类型uuid
    :param process_uuid  添加步骤属性流转过程的uuid
    :param field_uuid  新添加的属性uuid
    """
    return generate_param({
        "transition": {
            "uuid": process_uuid,
            "issue_type_uuid": issue_type,
            "project_uuid": ACCOUNT.project_uuid,
            "fields": [
                {
                    "field_uuid": field_uuid,
                    "default_value": None,
                    "required": False
                },
                {
                    "field_uuid": "tf-comment",  # 默认步骤属性: 评论
                    "default_value": "",
                    "required": False
                }
            ]
        }
    }, is_project=True, issue_type_uuid=issue_type, process_uuid=process_uuid)


def global_step_properties_up(issue_type, process_uuid, field_uuid):
    """全局工作项步骤属性变更"""
    return generate_param({
        "transition": {
            "fields": [
                {
                    "field_uuid": field_uuid,
                    "default_value": None,
                    "required": False
                },
                {
                    "field_uuid": "tf-comment",
                    "default_value": "",
                    "required": False
                }
            ]
        }
    }, issue_type_uuid=issue_type, process_uuid=process_uuid)


# ==========================================================================================


def sprint_status_up(category: list, status_uuids: list, sprint_uuid):
    """
    更新迭代状态
    :param category 状态类别(to_do、in_progress、done)
    :param status_uuids  状态uuid
    :param sprint_uuid
    """
    params = {'to_do': '未开始',
              'in_progress': '进行中',
              'done': '已完成'}

    _now = mocks.now_timestamp()

    prm = {
        "sprint_statuses": []
    }

    for c, s in zip(category, status_uuids):
        p = {
            "status_uuid": s,
            "name": params.get(c),
            "category": c,
            "plan_start_time": _now,
            "plan_end_time": _now,
            "actual_start_time": _now,
            "actual_end_time": _now,
            "is_current_status": False,
            "desc_plain": "",
            "desc_rich": ""
        }
        prm.get('sprint_statuses').append(p)

    return generate_param(prm, is_project=True, sprint_uuid=sprint_uuid)


def sprint_status_opt():
    """迭代阶段操作"""
    return generate_param({
        "status": {
            "name": f"示例阶段-{mocks.num()}"
        }
    }, is_project=True)


def sprint_status_del():
    """迭代阶段删除"""
    return generate_param({}, is_project=True)


def sprint_update():
    """迭代更新"""

    return generate_param(
        {
            "sprints": [
                {
                    "uuid": "",  # sprint_uuid
                    "start_time": mocks.now_timestamp(),
                    "end_time": mocks.day_timestamp(1),
                    "fields": [],
                    "statuses": []
                }
            ]
        }, is_project=True)


def sprint_field_add(types):
    """迭代属性添加"""

    return generate_param({
        "field": {
            "name": f'{types}-{mocks.num()}',
            "type": types,
            "options": [
                {
                    "value": "test_1",
                    "background_color": "#307fe2",
                    "color": "#fff"
                },
                {
                    "value": "test_2",
                    "background_color": "#00b388",
                    "color": "#fff"
                }
            ]
        }
    }, is_project=True)


def sprint_field_up():
    """迭代属性变更"""

    return generate_param({
        "field_value": {
            "value": ""  # 用例中赋值
        }
    }, is_project=True)


def sprint_search():
    """迭代属性列表"""
    return generate_param({}, is_project=True)


def sprint_field_param(opt_uuid_1, opt_uuid_2):
    """迭代属性变更参数"""
    p = {
        "field": {
            "name": f"迭代属性-{mocks.num()}",
            "type": "option",
            "default_value": opt_uuid_1,
            "default_value_type": "default",
            "built_in": False,
            "options": [
                {
                    "uuid": opt_uuid_1,
                    "value": "test_1",
                    "selected": False
                },
                {
                    "uuid": opt_uuid_2,
                    "value": "test_2",
                    "selected": False
                }
            ],
            "required": False,
            "can_modify_required": True,
            "value": opt_uuid_1
        }
    }
    return p


def sprint_field_value_up(field_uuid, field_name, options: dict = None, types='option'):
    """迭代属性值更新"""
    p = {"field": {
        "uuid": field_uuid,
        "name": field_name,
        "type": types,
        "default_value": None,
        "default_value_type": "default",
        "built_in": False,
        "required": False,
        "can_modify_required": True,
        "options": options
    }}
    return generate_param(p, is_project=True)


def sprint_field_position():
    """迭代属性位置排序"""
    return generate_param({"field_uuids": ''}, is_project=True)


def sprint_plan_list(project_uuid=None):
    '''迭代计划列表'''
    p = {
        "query": "\n      query QuerySprints {\n        sprints(\n        filter: {\n          project_in: $projectUUIDList\n          \n        },\n        orderBy: $orderBy\n      ) {\n          uuid\n  name\n  assign { uuid\n name\n} \n      progress\n        }\n      }\n    ",
        "variables": {
            "projectUUIDList": [
                project_uuid if project_uuid else ACCOUNT.user.owner_uuid
            ],
            "orderBy": {
                "name": "ASC"
            },
            "sprintDepList": None
        }
    }
    return generate_param(p, is_project=True)


def burn_down():
    """燃尽图"""

    return generate_param(is_project=True)


# ==========================================================================================


def add_deliverables_component():
    """交付物组件"""
    return generate_param({'components': [
        {
            "uuid": ones_uuid(),
            "template_uuid": "com00019",
            "project_uuid": ACCOUNT.project_uuid,
            "parent_uuid": "",
            "name": "交付物",
            "name_pinyin": "jiao1fu4wu4",
            "desc": "“交付物”组件列出了项目所有的交付物和来源。",
            "permissions": [
                {
                    "permission": "view_component",
                    "user_domains": [
                        {
                            "user_domain_type": "everyone",
                            "user_domain_param": ""
                        },
                        {
                            "user_domain_type": "project_administrators",
                            "user_domain_param": ""
                        }
                    ]
                }
            ],
            "objects": [],
            "type": 2,
            "views": [],
            "update": 1
        }
    ]}, is_project=True)


def add_primary_navigation():
    """新增一级导航栏"""
    return generate_param({'components': [{
        "uuid": ones_uuid(),
        "template_uuid": "com00000",
        "project_uuid": ACCOUNT.project_uuid,
        "parent_uuid": "",
        "name": "一级导航",
        "name_pinyin": "yi1ji2dao3hang2",
        "desc": "“一级导航”组件是一个空文件夹，您可以自定义其名称及其所含二级导航组件。",
        "permissions": [
            {
                "permission": "view_component",
                "user_domains": [
                    {
                        "user_domain_type": "everyone",
                        "user_domain_param": ""
                    },
                    {
                        "user_domain_type": "project_administrators",
                        "user_domain_param": ""
                    }
                ]
            }
        ],
        "objects": [],
        "type": 1,
        "views": [],
        "update": 1
    }]}, is_project=True)


def add_customize_component():
    """自定义链接组件"""
    return generate_param({'components': [{
        "uuid": ones_uuid(),
        "template_uuid": "com00012",
        "project_uuid": ACCOUNT.project_uuid,
        "parent_uuid": "",
        "name": "自定义链接",
        "name_pinyin": "zi4ding4yi4lian4jie1",
        "desc": "“自定义链接”组件可以通过配置URL，点击后跳转到对应网页。",
        "permissions": [
            {
                "permission": "view_component",
                "user_domains": [
                    {
                        "user_domain_type": "everyone",
                        "user_domain_param": ""
                    },
                    {
                        "user_domain_type": "project_administrators",
                        "user_domain_param": ""
                    }
                ]
            }
        ],
        "objects": [],
        "type": 2,
        "views": [],
        "url_setting": {
            "url": "https://www.baidu.com"
        },
        "update": 1
    }]}, is_project=True)


def add_implement_component(view):
    """add执行组件参数"""
    return generate_param({
        'components': [{
            "uuid": ones_uuid(),
            "template_uuid": "com00015",
            "project_uuid": ACCOUNT.project_uuid,
            "parent_uuid": "",
            "name": "执行",
            "name_pinyin": "zhi2xing2",
            "desc": "“执行”组件列出了从项目计划拆解得到的所有计划。",
            "permissions": [
                {
                    "permission": "view_component",
                    "user_domains": [
                        {
                            "user_domain_type": "everyone",
                            "user_domain_param": ""
                        },
                        {
                            "user_domain_type": "project_administrators",
                            "user_domain_param": ""
                        }
                    ]
                }
            ],
            "objects": [],
            "type": 2,
            "views": view,
            "update": 1
        }]
    }, is_project=True)


def add_task_component():
    """添加任务组件"""
    return generate_param({'components': [{
        "uuid": ones_uuid(),
        "template_uuid": "com00003",
        "project_uuid": ACCOUNT.project_uuid,
        "parent_uuid": "",
        "name": "任务",
        "name_pinyin": "ren4wu4",
        "desc": "“任务”组件包含了详细的任务列表，同时包含关联工作项等针对性功能。",
        "permissions": [
            {
                "permission": "view_component",
                "user_domains": [
                    {
                        "user_domain_type": "everyone",
                        "user_domain_param": ""
                    },
                    {
                        "user_domain_type": "project_administrators",
                        "user_domain_param": ""
                    }
                ]
            }
        ],
        "objects": '',
        "type": 3,
        "views": '',
        "update": 1
    }]}, is_project=True)


def add_milestone_component():
    """
    添加项目内里程碑组件参数
    """
    return generate_param({
        'components': [
            {
                "uuid": ones_uuid(),
                "template_uuid": "com00018",
                "project_uuid": ACCOUNT.project_uuid,
                "parent_uuid": "",
                "name": "里程碑",
                "name_pinyin": "li3cheng2bei1",
                "desc": "“里程碑”组件包含里程碑时间轴和里程碑列表，支持增删改查里程碑、对比里程碑计划的历史版本。",
                "permissions": [
                    {
                        "permission": "view_component",
                        "user_domains": [
                            {
                                "user_domain_type": "everyone",
                                "user_domain_param": ""
                            },
                            {
                                "user_domain_type": "project_administrators",
                                "user_domain_param": ""
                            }
                        ]
                    }
                ],
                "objects": [],
                "type": 2,
                "views": [],
                "update": 1
            },
        ],
    }, is_project=True)


def get_deploy_info(tasks_uuid):
    """查询发布详情graphql"""
    return generate_param({
        "query": "\n    query TASK($key: Key) {\n      task(key: $key) {\n        \n  \n  publishContent {\n    uuid\n    name\n    summary: name\n    path\n    parent {\n      uuid\n    }\n    readable\n    deadline\n    estimatedHours\n    remainingManhour\n    \n  project {\n    uuid\n    name\n    isSample\n    isArchive\n  }\n\n    \n    priority {\n      bgColor\n      color\n      defaultSelected\n      position\n      uuid\n      value\n    }\n  \n    \n  issueType {\n    key\n    uuid\n    value: uuid\n    name\n    label: name\n    builtIn\n    detailType\n    namePinyin\n    icon\n    subIssueType\n  }\n\n    \n  subIssueType {\n    key\n    uuid\n    value: uuid\n    name\n    label: name\n    builtIn\n    detailType\n    namePinyin\n    icon\n    \n  }\n\n    \n  importantField {\n    bgColor\n    color\n    fieldUUID\n    name\n    value\n  }\n  importantFieldsOptions:importantField {\n    uuid:fieldUUID\n    label: value\n    background: bgColor\n    color\n    name\n  }\n\n    \n  status {\n    uuid\n    name\n    namePinyin\n    category\n    builtIn\n    detailType\n  }\n\n    \n    assign {\n      uuid\n      name\n      avatar\n    }\n  \n    \n    \n    sprint {\n      name\n      uuid\n      namePinyin\n    }\n  \n  }\n\n  \n  publishContentCount\n  publishContentDoneCount\n\n\n\n  publishContentCount\n  publishContentDoneCount\n\n        issueType {\n          uuid\n        }\n        subIssueType {\n          uuid\n        }\n        project {\n          uuid\n        }\n        issueTypeScope {\n          uuid\n        }\n      }\n    }\n  ",
        "variables": {
            "key": "task-" + tasks_uuid
        }
    }, is_project=True, tasks_uuid=tasks_uuid)


def get_task_info(tasks_uuid):
    return generate_param({
        "query": "\n    query TASK($key: Key) {\n      task(key: $key) {\n        \n    \n  \n  relatedTasks {\n    uuid\n    name\n    summary: name\n    path\n    parent {\n      uuid\n    }\n    readable\n    deadline\n    estimatedHours\n    remainingManhour\n    \n  project {\n    uuid\n    name\n    isSample\n    isArchive\n    activityChart {\n      uuid\n    }\n  }\n\n    \n    priority {\n      bgColor\n      color\n      defaultSelected\n      position\n      uuid\n      value\n    }\n  \n    \n  issueType {\n    key\n    uuid\n    value: uuid\n    name\n    label: name\n    builtIn\n    detailType\n    namePinyin\n    icon\n    subIssueType\n  }\n\n    \n  subIssueType {\n    key\n    uuid\n    value: uuid\n    name\n    label: name\n    builtIn\n    detailType\n    namePinyin\n    icon\n    \n  }\n\n    \n  importantField {\n    bgColor\n    color\n    fieldUUID\n    name\n    value\n  }\n  importantFieldsOptions:importantField {\n    uuid:fieldUUID\n    label: value\n    background: bgColor\n    color\n    name\n  }\n\n    \n  status {\n    uuid\n    name\n    namePinyin\n    category\n    builtIn\n    detailType\n  }\n\n    \n    assign {\n      uuid\n      name\n      avatar\n    }\n  \n    \n    \n  }\n\n  allRelatedTasks(stubTaskRelatedTasks: {}) {\n    uuid\n    name\n    \n  status {\n    uuid\n    name\n    namePinyin\n    category\n    builtIn\n    detailType\n  }\n\n  }\n  links {\n    taskUUID\n    taskLinkTypeUUID\n    linkDescType\n  }\n  \n  relatedTasksCount\n  allRelatedTasksCount: stubRelatedTasksCount\n\n\n  \n    \n  subTaskCount\n  subTaskDoneCount\n\n  \n    \n  sprint {\n    description\n    name\n    namePinyin\n    uuid\n  }\n\n  \n    \n  relatedWikiPages {\n    uuid\n    title\n    referenceType\n    ref_type: referenceType\n    errorMessage\n  }\n  relatedWikiPagesCount\n\n  \n\n    \n    assign {\n      key\n      uuid\n      name\n      avatar\n    }\n  \n\n  status {\n    uuid\n    name\n    namePinyin\n    category\n    builtIn\n    detailType\n  }\n\n\n    priority {\n      bgColor\n      color\n      uuid\n      value\n      position\n    }\n  \n\n    sprint {\n      key\n      uuid\n      value: uuid\n      name\n      label: name\n    }\n  \n\n    subTaskCount\n  \n\n  number\n\n\n\n    deadline\n\n    assign {\n      key\n      uuid\n      name\n      avatar\n    }\n  \n\n  status {\n    uuid\n    name\n    namePinyin\n    category\n    builtIn\n    detailType\n  }\n\n\n    priority {\n      bgColor\n      color\n      uuid\n      value\n      position\n    }\n  \n\n    sprint {\n      key\n      uuid\n      value: uuid\n      name\n      label: name\n    }\n  \n\n    publishVersion {\n      key\n      uuid\n      value: uuid\n      name\n      label: name\n      readable\n    }\n  \n\n    subTaskCount\n  \n\n    \n    project {\n      key\n      uuid\n      value: uuid\n      name\n      label: name\n    }\n  \n\n    \n  issueType {\n    key\n    uuid\n    value: uuid\n    name\n    label: name\n    builtIn\n    detailType\n    namePinyin\n    icon\n    subIssueType\n  }\n\n    \n  subIssueType {\n    key\n    uuid\n    value: uuid\n    name\n    label: name\n    builtIn\n    detailType\n    namePinyin\n    icon\n    \n  }\n\n  \n\n    \n  issueType {\n    key\n    uuid\n    value: uuid\n    name\n    label: name\n    builtIn\n    detailType\n    namePinyin\n    icon\n    subIssueType\n  }\n\n    \n  subIssueType {\n    key\n    uuid\n    value: uuid\n    name\n    label: name\n    builtIn\n    detailType\n    namePinyin\n    icon\n    \n  }\n\n  \n\n    owner {\n      key\n      uuid\n      name\n      avatar\n    }\n  \ncreateTime\nserverUpdateStamp\n\n    subTaskCount\n  \n\n\n\n\n    \n  relatedTasksCount\n  allRelatedTasksCount: stubRelatedTasksCount\n\n   relatedActivities {\n      uuid\n      name\n      projectUUID\n      project_uuid: projectUUID\n      relatedChild\n      related_child_uuid: relatedChild\n    }\n     relatedActivitiesCount\n  \nrelatedWikiPagesCount\nattachmentCount\npreDependencyCount\npostDependencyCount\n\n\n\n\n    key\n    uuid\n    name\n    summary: name\n    description\n    descriptionText\n    desc_rich: description\n    path\n    parent {\n      uuid\n      number\n      canView(attachPermission:{\n        permissions:[\"view_tasks\"],\n      })\n      parent {\n        uuid\n        number\n        canView(attachPermission:{\n          permissions:[\"view_tasks\"],\n        })\n        parent {\n          uuid\n          number\n          canView(attachPermission:{\n            permissions:[\"view_tasks\"],\n          })\n          parent {\n            uuid\n            number\n            canView(attachPermission:{\n              permissions:[\"view_tasks\"],\n            })\n            parent {\n              uuid\n              number\n              canView(attachPermission:{\n                permissions:[\"view_tasks\"],\n              })\n              parent {\n                uuid\n                number\n                canView(attachPermission:{\n                  permissions:[\"view_tasks\"],\n                })\n                parent {\n                  uuid\n                  number\n                  canView(attachPermission:{\n                    permissions:[\"view_tasks\"],\n                  })\n                  parent {\n                    uuid\n                    number\n                    canView(attachPermission:{\n                      permissions:[\"view_tasks\"],\n                    })\n                    parent {\n                      uuid\n                      number\n                      canView(attachPermission:{\n                        permissions:[\"view_tasks\"],\n                      })\n                      parent {\n                        uuid\n                        number\n                        canView(attachPermission:{\n                          permissions:[\"view_tasks\"],\n                        })\n                      }\n                    }\n                  }\n                }\n              }\n            }\n          }\n        }\n      }\n    }\n    \n  importantField {\n    bgColor\n    color\n    fieldUUID\n    name\n    value\n  }\n  importantFieldsOptions:importantField {\n    uuid:fieldUUID\n    label: value\n    background: bgColor\n    color\n    name\n  }\n\n    \n  issueType {\n    key\n    uuid\n    value: uuid\n    name\n    label: name\n    builtIn\n    detailType\n    namePinyin\n    icon\n    subIssueType\n  }\n\n    \n  subIssueType {\n    key\n    uuid\n    value: uuid\n    name\n    label: name\n    builtIn\n    detailType\n    namePinyin\n    icon\n    \n  }\n\n    \n  status {\n    uuid\n    name\n    namePinyin\n    category\n    builtIn\n    detailType\n  }\n\n    \n  project {\n    uuid\n    name\n    isSample\n    isArchive\n    activityChart {\n      uuid\n    }\n  }\n\n    \n    owner {\n      key\n      uuid\n      name\n      avatar\n    }\n  \n\n\n    assign {\n      key\n      uuid\n      name\n      avatar\n    }\n  \n\n\n    watchers {\n      key\n      uuid\n      name\n      avatar\n    }\n  \n\n\n    solver {\n      key\n      uuid\n      name\n      avatar\n    }\n  \n\n\n  \n        issueType {\n          uuid\n        }\n        subIssueType {\n          uuid\n        }\n        project {\n          uuid\n        }\n        issueTypeScope {\n          uuid\n        }\n      }\n    }\n  ",
        "variables": {
            "key": "task-" + tasks_uuid
        }
    }, is_project=True, tasks_uuid=tasks_uuid)


def get_sprint_related_ppm(sprint_uuid):
    return generate_param({
        "query": "\n      query SprintRelatedActivity {\n        sprints(\n          filter: $filter\n        ) {\n          activities {\n            key\n            uuid\n            name\n          }\n          parentActivities {\n            key\n            uuid\n            name\n          }\n        }\n      }\n    ",
        "variables": {
            "filter": {
                "uuid_in": [
                    sprint_uuid
                ]
            }
        }
    })


def get_isu_task_list(deploy_task_uuid):
    return generate_param({
        "query": "{\n  buckets(groupBy: {tasks: {}}, pagination: {limit: 50, after: \"\", preciseCount: true}) {\n    tasks(filterGroup: $filterGroup, orderBy: $orderBy, limit: 1000) {\n      name\n      key\n      uuid\n      number\n      status {\n        category\n        name\n        uuid\n      }\n      path\n      position\n      parent {\n        uuid\n      }\n      importantField {\n        name\n        value\n        color\n        bgColor\n        fieldUUID\n      }\n      estimatedHours\n      remainingManhour\n    }\n    key\n    pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n",
        "variables": {
            "groupBy": None,
            "orderBy": {
                "createTime": "DESC"
            },
            "filterGroup": [
                {
                    "project_in": [
                        ACCOUNT.project_uuid
                    ],
                    "publishVersion_notEqual": deploy_task_uuid,
                    "parent": {
                        "uuid_in": [
                            ""
                        ]
                    }
                }
            ],
            "bucketOrderBy": None,
            "search": {
                "keyword": "",
                "aliases": [
                    "name",
                    "number"
                ]
            }
        }
    })


def get_deploy_list_graphql(issueType_uuid):
    """关联发布 下拉列表"""
    return generate_param({
        "query": "{\n  buckets(groupBy: {tasks: {}}, pagination: {limit: 20, after: \"\", preciseCount: true}) {\n    tasks(filterGroup: $filterGroup, orderBy: $orderBy, limit: 1000) {\n      name\n      key\n      uuid\n      number\n      status {\n        category\n        name\n        uuid\n      }\n      path\n      position\n      parent {\n        uuid\n      }\n      importantField {\n        name\n        value\n        color\n        bgColor\n        fieldUUID\n      }\n      estimatedHours\n      remainingManhour\n    }\n    key\n    pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n",
        "variables": {
            "groupBy": None,
            "orderBy": {
                "createTime": "DESC"
            },
            "filterGroup": [
                {
                    "issueType_in": [
                        issueType_uuid
                    ],
                    "project_in": [
                        ACCOUNT.project_uuid
                    ],
                    "parent": {
                        "uuid_in": [
                            ""
                        ]
                    }
                }
            ],
            "bucketOrderBy": None,
            "search": {
                "keyword": "",
                "aliases": [
                    "title",
                    "number"
                ]
            }
        }
    })


def select_deploy_relation_info(keyword, issueType_uuid):
    """查看关联发布 查询keyword 关键字"""
    return generate_param({
        "query": "{\n  buckets(groupBy: {tasks: {}}, pagination: {limit: 20, after: \"\", preciseCount: true}) {\n    tasks(filterGroup: $filterGroup, orderBy: $orderBy, search: $search, limit: 1000) {\n      name\n      key\n      uuid\n      number\n      status {\n        category\n        name\n        uuid\n      }\n      path\n      position\n      parent {\n        uuid\n      }\n      importantField {\n        name\n        value\n        color\n        bgColor\n        fieldUUID\n      }\n      estimatedHours\n      remainingManhour\n    }\n    key\n    pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n",
        "variables": {
            "groupBy": None,
            "orderBy": {
                "createTime": "DESC"
            },
            "filterGroup": [
                {
                    "issueType_in": [
                        issueType_uuid
                    ],
                    "project_in": [
                        ACCOUNT.project_uuid
                    ],
                    "parent": {
                        "uuid_in": [
                            ""
                        ]
                    }
                }
            ],
            "bucketOrderBy": None,
            "search": {
                "keyword": keyword,
                "aliases": [
                    "title",
                    "number"
                ]
            }
        }
    })


def batch_set_publish_version(type, ise_uuid: list):
    """规划任务至发布"""
    return generate_param({
        type: ise_uuid

    }, is_project=True)


def update_deploy_relation_field(isu_uuid, deploy_task_uuid_list):
    """更新关联发布字段 请求param"""
    return generate_param({
        "tasks": [
            {
                "uuid": isu_uuid,
                "field_values": [
                    {
                        "field_uuid": "field037",
                        "type": 49,
                        "value": deploy_task_uuid_list
                    }
                ]
            }
        ]
    }, is_project=True)


def add_deploy_tasks(issue_type_uuid, value=mocks.now_timestamp()):
    """
    添加发布任务
    """
    return generate_param({
        "tasks": [
            {
                "uuid": f'{ACCOUNT.user.owner_uuid}{ones_uuid()}',
                "owner": ACCOUNT.user.owner_uuid,
                "assign": ACCOUNT.user.owner_uuid,
                "summary": "发布任务" + mocks.num(),
                "parent_uuid": "",
                "field_values": [
                    {
                        "field_uuid": "field004",
                        "type": 8,
                        "value": ACCOUNT.user.owner_uuid
                    },
                    {
                        "field_uuid": "field012",
                        "type": 1,
                        "value": None
                    },
                    {
                        "field_uuid": "field036",
                        "type": 5,
                        "value": value
                    },
                    {
                        "field_uuid": "field013",
                        "type": 5,
                        "value": None
                    },
                    {
                        "field_uuid": "field029",
                        "type": 44,
                        "value": []
                    },
                    {
                        "field_uuid": "field030",
                        "type": 46,
                        "value": None
                    },
                    {
                        "field_uuid": "field037",
                        "type": 49,
                        "value": None
                    },
                    {
                        "field_uuid": "field011",
                        "type": 7,
                        "value": None
                    },
                    {
                        "field_uuid": "field027",
                        "type": 5,
                        "value": None
                    },
                    {
                        "field_uuid": "field028",
                        "type": 5,
                        "value": None
                    },
                    {
                        "field_uuid": "field033",
                        "type": 4,
                        "value": None
                    }
                ],
                "project_uuid": ACCOUNT.project_uuid,
                "issue_type_uuid": issue_type_uuid,
                "watchers": [
                    ACCOUNT.user.owner_uuid
                ]
            }
        ]
    }, is_project=True)


def proj_url():
    return generate_param(is_project=True)


def update_deploy_status(transition_uuid, task_uuid, undone_tasks=[], undone_target_versions=[]):
    """更新发布任务状态为发布状态 """
    return generate_param({
        "transit": {
            "field_values": [
                {
                    "field_uuid": "field036",
                    "type": 5,
                    "value": mocks.now_timestamp()
                }
            ],
            "transition_uuid": transition_uuid
        },
        "undone_tasks": undone_tasks,
        "undone_target_versions": undone_target_versions
    }, is_project=True, tasks_uuid=task_uuid)


def update_transit_status(transition_uuid):
    """参数：修改任务状态"""
    return generate_param({
        "transition_uuid": transition_uuid
    }, is_project=True)


def relation_document_wiki(bind: list, unbind: list):
    """文档绑定/解绑wiki"""
    return generate_param({
        "bind": bind,
        "unbind": unbind
    }, is_project=True)


def add_task_permission(issue_type_scope_uuid, field_uuid):
    """添加工作项规则权限"""
    return generate_param({
        "items": [
            {
                "user_domain_type": "single_user",  # 个人
                "user_domain_param": ACCOUNT.user.owner_uuid,
                "item_type": "issue_type_scope_field_constraint",
                "issue_type_scope_uuid": issue_type_scope_uuid,
                "constraint": "update_task_field",
                "field_uuid": field_uuid
            }
        ]
    })


def get_task_permission_list(issue_type_scope_uuid):
    return generate_param({
        "query": "{\n      buckets(groupBy:{\n          issueTypeScopeFieldConstraints:{\n              fieldUUID:{}\n          }\n      }){\n          key\n          fieldUUID\n          issueTypeScopeFieldConstraints(\n            filter: {\n              issueTypeScopeUUID_equal: $issueTypeScopeUUID\n              status_equal: normal\n            }\n            orderBy:{\n              createTime: ASC\n            }\n          ){\n              uuid\n              userDomainType\n              userDomainParam\n              position\n          }\n      }\n  }",
        "variables": {
            "issueTypeScopeUUID": issue_type_scope_uuid
        }
    })


def get_all_project():
    """请求参数：获取所有项目"""
    return generate_param(
        {
            "project": 0,
            "all_project": 0
        }
    )


# -*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-
# 敏捷模版管理

def new_agile_kanban(project_uuid) -> dict:
    """新建看板模版"""
    # 关联：project stamp data：field_config、issue_type_config
    return {
        "uuid": mocks.ones_uuid(),
        "name": f"敏捷看板-测试",
        "lane_type": 1,
        "project_uuid": project_uuid,
        "issue_type_uuids": [
            "QZF1MhZ6",
            "EPc5caRX"
        ],
        "conditions": {
            "condition_groups": [
                [
                    {
                        "field_uuid": "field024",
                        "operate": {
                            "label": "filter.addQueryContent.include",
                            "operate_id": "include",
                            "predicate": "in",
                            "negative": False
                        },
                        "value": [
                            "Q24Fhx1C"
                        ],
                        "field_type": 11
                    }
                ]
            ]
        },
        "is_updated": False,
        "board_settings": [
            {
                "uuid": "3pg8dXTd",
                "name": "未开始",
                "status_uuids": [
                    "EF2TG5BS"
                ]
            },
            {
                "uuid": "AME2cVBN",
                "name": "进行中",
                "status_uuids": [
                    "LyKDyvu3"
                ]
            },
            {
                "uuid": "5iLCUfXn",
                "name": "已完成",
                "status_uuids": [
                    "A3WBi2WE"
                ]
            }
        ],
        "lane_sort": {
            "type": "status_category",
            "status_uuids": []
        }
    }


def new_kb_board_settings(status_uuids: [str]):
    return {
        "uuid": ones_uuid(),
        "name": f"board{ones_uuid()}",
        "status_uuids": status_uuids
    }


def param_kanban_filter(project_uuid, issue_type_uuids: [str], sprint_uuid):
    return generate_param({
        "query": "\n  {\n    tasks(\n      filterGroup: $filterGroup\n      orderBy: {\n          priority: {\n            position: ASC\n          }\n          createTime: DESC\n      }\n    ) {\n      issueType {\n        name\n        uuid\n      }\n      subIssueType {\n        name\n        uuid\n      }\n      subTasks {\n        uuid\n        status { uuid }\n      }\n      description\n      \n    uuid\n    name\n    number\n    estimatedHours\n    remainingManhour\n    priority{\n      bgColor\n      color\n      value\n      uuid\n    }\n    status {\n      uuid\n      name\n      category\n    }\n    manhours {\n      hours\n    }\n    serverUpdateStamp\n    parent { uuid }\n    assign {\n      email\n      name\n      uuid\n    }\n    owner {\n      email\n      name\n      uuid\n    }\n    project { uuid }\n\n    }\n  }\n  ",
        "variables": {
            "filterGroup": [
                {
                    "alternativeIssueType_in":
                        issue_type_uuids,
                    "project_in": [
                        project_uuid
                    ],
                    "sprint_in": [
                        sprint_uuid
                    ]
                }
            ]
        }
    })


# -*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-
# 项目设置
def issue_type_add(issue_type_uuid):
    """
    项目设置-添加工作项类型
    :param issue_type_uuid:
    :return:
    """
    return generate_param({
        "issue_type_uuids": [
            issue_type_uuid
        ]
    })


def proj_pin_or_unpin():
    """项目置顶和取消"""

    return generate_param({}, is_project=True)


def update_prj_assign(uid):
    """修改项目负责人"""
    return generate_param({
        "item": {
            "assign": uid
        }
    }, is_project=True)


def update_prj_status():
    """修改项目状态"""
    return generate_param({
        "item": {
            "status": "to_do"
        }
    }, is_project=True)
