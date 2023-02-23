from falcons.com.meta import ApiMeta
from falcons.helper import mocks
from falcons.helper.mocks import ones_uuid
from falcons.ops import generate_param

"""honor_upload_tips插件接口参数"""

PLUGIN_ACCOUNT = ApiMeta.account


def get_upload_tips():
    """获取-上传文件提醒"""
    return generate_param()


def set_upload_tips():
    """设置-上传文件提醒"""
    return generate_param({

        "content": "test+123"
    })


def Permission_Number_Add():
    """添加可用成员-个人"""

    return generate_param(
        {
            "context_type": "plugin",
            "context_param": {
                "plugin_uuid": ''
            },
            "permission": '',
            "user_domain_type": "single_user",
            "user_domain_param": PLUGIN_ACCOUNT.user.owner_uuid,
            "permission_id": '',
            "teamUUID": PLUGIN_ACCOUNT.user.team_uuid,
            "team_uuid": PLUGIN_ACCOUNT.user.team_uuid
        }
    )


def Permission_Number_Delete():
    """删除可用成员-个人"""

    return generate_param(
        {
            "team_uuid": PLUGIN_ACCOUNT.user.team_uuid,
            "id": ''
        }
    )


def Permission_Number_Check():
    """可用成员校验"""

    return generate_param(
        {
            "organization_uuid": PLUGIN_ACCOUNT.user.org_uuid,
            "team_uuid": PLUGIN_ACCOUNT.user.team_uuid,
            "instance_id": '',
            "permission_field": "ones-global-modal-upload-X5Rv"
        }
    )


def Permission_Info_List():
    """可用成员配置列表"""

    return generate_param(
        {
            "organization_uuid": PLUGIN_ACCOUNT.user.org_uuid,
            "team_uuid": PLUGIN_ACCOUNT.user.team_uuid,
            "instance_uuid": ''
        }
    )


"""honor_banner插件接口参数"""


def get_banner_tips():
    """获取-上传文件提醒"""

    return generate_param()


def set_banner_tips():
    """设置-顶部banner提示语"""
    return generate_param({

        "content": "test+123"

    })


"""honor_workspace插件接口参数"""


def workspace_permission_number_add():
    """添加可用成员-个人"""
    return generate_param(
        {
            "context_type": "plugin",
            "context_param": {
                "plugin_uuid": '',
            },
            "permission": '',
            "user_domain_type": "single_user",
            "user_domain_param": PLUGIN_ACCOUNT.user.owner_uuid,
            "permission_id": '',
            "teamUUID": PLUGIN_ACCOUNT.user.team_uuid,
            "team_uuid": PLUGIN_ACCOUNT.user.team_uuid
        }
    )


def workspace_permission_number_delete():
    """删除可用成员-个人"""
    num = mocks.two_num()
    return generate_param(
        {
            "team_uuid": PLUGIN_ACCOUNT.user.team_uuid,
            "id": num
        }
    )


def workspace_permission_number_check():
    """隐藏工作台校验"""
    return generate_param(
        {
            "organization_uuid": PLUGIN_ACCOUNT.user.org_uuid,
            "team_uuid": PLUGIN_ACCOUNT.user.team_uuid,
            "instance_id": '',
            "permission_field": "workspace_view_permission"
        }
    )


def workspace_permission_info_list():
    """可用成员配置列表"""

    return generate_param(
        {
            "organization_uuid": PLUGIN_ACCOUNT.user.org_uuid,
            "team_uuid": PLUGIN_ACCOUNT.user.team_uuid,
            "instance_uuid": '',
        }
    )


"""------紫金工单门户-----"""


def get_component_list():
    return generate_param(
        {
            "org_configs": 0
        }
    )


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


def add_prj_desk_component():
    """
    添加工单组件信息

    :return:
    """

    return generate_param({
        'components': [
            {
                "uuid": ones_uuid(),
                "template_uuid": "com00016",
                "project_uuid": PLUGIN_ACCOUNT.project_uuid,
                "parent_uuid": "",
                "name": "工单",
                "name_pinyin": "gong1dan1",
                "desc": "“工单”组件用于收集和管理工单，可以指派工单处理人，自定义工单状态流转。",
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


def update_form():
    return generate_param(
        {
            "components": [
                {
                    "uuid": "9aSsvYtI",
                    "template_uuid": "com00016",
                    "container_type": 1,
                    "container_uuid": "5oziwx7y2FkJnNO4",
                    "project_uuid": "5oziwx7y2FkJnNO4",
                    "parent_uuid": "",
                    "name": "工单",
                    "name_pinyin": "gong1dan1",
                    "desc": "“工单”组件用于收集和管理工单，可以指派工单处理人，自定义工单状态流转。",
                    "type": 3,
                    "objects": [
                        {
                            "type": 1001,
                            "uuid": "TwNJcYZr",
                            "issue_type_scope_uuid": None
                        }
                    ],
                    "create_time": 1655366439,
                    "views": [
                        {
                            "uuid": "2MVAku7K",
                            "team_uuid": "BvuRW246",
                            "project_uuid": "5oziwx7y2FkJnNO4",
                            "component_uuid": "9aSsvYtI",
                            "built_in": True,
                            "board_settings": None,
                            "condition": {
                                "lock_conditions": [
                                    {
                                        "field_uuid": "field006",
                                        "operate": {
                                            "label": "filter.addQueryContent.include",
                                            "operate_id": "include",
                                            "predicate": "in"
                                        },
                                        "value": [
                                            "5oziwx7y2FkJnNO4"
                                        ]
                                    },
                                    {
                                        "field_uuid": "field007",
                                        "operate": {
                                            "label": "filter.addQueryContent.include",
                                            "operate_id": "include",
                                            "predicate": "in"
                                        },
                                        "value": [
                                            "TwNJcYZr"
                                        ]
                                    }
                                ],
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
                                ],
                                "is_init": True
                            },
                            "display_type": "sub_tree",
                            "is_show_derive": False,
                            "shared": False,
                            "shared_to": None,
                            "group_by": "",
                            "layout": "narrow",
                            "select_group_key": "",
                            "is_fixed_quick_screening": False,
                            "query": {
                                "must": [
                                    {
                                        "must": [
                                            {
                                                "in": {
                                                    "field_values.field006": [
                                                        "5oziwx7y2FkJnNO4"
                                                    ]
                                                }
                                            },
                                            {
                                                "in": {
                                                    "field_values.field007": [
                                                        "TwNJcYZr"
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                ]
                            },
                            "sort": [
                                {
                                    "field_values.field009": {
                                        "order": "desc"
                                    }
                                }
                            ],
                            "is_fold_all_groups": False,
                            "table_field_settings": [],
                            "include_subtasks": True,
                            "name": "全部工单"
                        },
                        {
                            "uuid": "6HWcf2iZ",
                            "team_uuid": "BvuRW246",
                            "project_uuid": "5oziwx7y2FkJnNO4",
                            "component_uuid": "9aSsvYtI",
                            "built_in": True,
                            "board_settings": None,
                            "condition": {
                                "lock_conditions": [
                                    {
                                        "field_uuid": "field006",
                                        "operate": {
                                            "label": "filter.addQueryContent.include",
                                            "operate_id": "include",
                                            "predicate": "in"
                                        },
                                        "value": [
                                            "5oziwx7y2FkJnNO4"
                                        ]
                                    },
                                    {
                                        "field_uuid": "field007",
                                        "operate": {
                                            "label": "filter.addQueryContent.include",
                                            "operate_id": "include",
                                            "predicate": "in"
                                        },
                                        "value": [
                                            "TwNJcYZr"
                                        ]
                                    }
                                ],
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
                                            "field_uuid": "field017",
                                            "operate": {
                                                "label": "filter.addQueryContent.include",
                                                "operate_id": "include",
                                                "predicate": "in"
                                            },
                                            "value": [
                                                "to_do"
                                            ]
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
                                ],
                                "is_init": True
                            },
                            "display_type": "sub_tree",
                            "is_show_derive": False,
                            "shared": False,
                            "shared_to": None,
                            "group_by": "",
                            "layout": "narrow",
                            "select_group_key": "",
                            "is_fixed_quick_screening": False,
                            "query": {
                                "must": [
                                    {
                                        "must": [
                                            {
                                                "in": {
                                                    "field_values.field006": [
                                                        "5oziwx7y2FkJnNO4"
                                                    ]
                                                }
                                            },
                                            {
                                                "in": {
                                                    "field_values.field007": [
                                                        "TwNJcYZr"
                                                    ]
                                                }
                                            }
                                        ]
                                    },
                                    {
                                        "should": [
                                            {
                                                "must": [
                                                    {
                                                        "in": {
                                                            "field_values.field017": [
                                                                "to_do"
                                                            ]
                                                        }
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            "sort": [
                                {
                                    "field_values.field009": {
                                        "order": "desc"
                                    }
                                }
                            ],
                            "is_fold_all_groups": False,
                            "table_field_settings": [],
                            "include_subtasks": True,
                            "name": "未开始"
                        },
                        {
                            "uuid": "EEWBqtsX",
                            "team_uuid": "BvuRW246",
                            "project_uuid": "5oziwx7y2FkJnNO4",
                            "component_uuid": "9aSsvYtI",
                            "built_in": True,
                            "board_settings": None,
                            "condition": {
                                "lock_conditions": [
                                    {
                                        "field_uuid": "field006",
                                        "operate": {
                                            "label": "filter.addQueryContent.include",
                                            "operate_id": "include",
                                            "predicate": "in"
                                        },
                                        "value": [
                                            "5oziwx7y2FkJnNO4"
                                        ]
                                    },
                                    {
                                        "field_uuid": "field007",
                                        "operate": {
                                            "label": "filter.addQueryContent.include",
                                            "operate_id": "include",
                                            "predicate": "in"
                                        },
                                        "value": [
                                            "TwNJcYZr"
                                        ]
                                    }
                                ],
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
                                            "field_uuid": "field017",
                                            "operate": {
                                                "label": "filter.addQueryContent.include",
                                                "operate_id": "include",
                                                "predicate": "in"
                                            },
                                            "value": [
                                                "in_progress"
                                            ]
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
                                ],
                                "is_init": True
                            },
                            "display_type": "sub_tree",
                            "is_show_derive": False,
                            "shared": False,
                            "shared_to": None,
                            "group_by": "",
                            "layout": "narrow",
                            "select_group_key": "",
                            "is_fixed_quick_screening": False,
                            "query": {
                                "must": [
                                    {
                                        "must": [
                                            {
                                                "in": {
                                                    "field_values.field006": [
                                                        "5oziwx7y2FkJnNO4"
                                                    ]
                                                }
                                            },
                                            {
                                                "in": {
                                                    "field_values.field007": [
                                                        "TwNJcYZr"
                                                    ]
                                                }
                                            }
                                        ]
                                    },
                                    {
                                        "should": [
                                            {
                                                "must": [
                                                    {
                                                        "in": {
                                                            "field_values.field017": [
                                                                "in_progress"
                                                            ]
                                                        }
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            "sort": [
                                {
                                    "field_values.field009": {
                                        "order": "desc"
                                    }
                                }
                            ],
                            "is_fold_all_groups": False,
                            "table_field_settings": [],
                            "include_subtasks": True,
                            "name": "进行中"
                        },
                        {
                            "uuid": "1NGUXsZH",
                            "team_uuid": "BvuRW246",
                            "project_uuid": "5oziwx7y2FkJnNO4",
                            "component_uuid": "9aSsvYtI",
                            "built_in": True,
                            "board_settings": None,
                            "condition": {
                                "lock_conditions": [
                                    {
                                        "field_uuid": "field006",
                                        "operate": {
                                            "label": "filter.addQueryContent.include",
                                            "operate_id": "include",
                                            "predicate": "in"
                                        },
                                        "value": [
                                            "5oziwx7y2FkJnNO4"
                                        ]
                                    },
                                    {
                                        "field_uuid": "field007",
                                        "operate": {
                                            "label": "filter.addQueryContent.include",
                                            "operate_id": "include",
                                            "predicate": "in"
                                        },
                                        "value": [
                                            "TwNJcYZr"
                                        ]
                                    }
                                ],
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
                                            "field_uuid": "field017",
                                            "operate": {
                                                "label": "filter.addQueryContent.include",
                                                "operate_id": "include",
                                                "predicate": "in"
                                            },
                                            "value": [
                                                "done"
                                            ]
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
                                ],
                                "is_init": True
                            },
                            "display_type": "sub_tree",
                            "is_show_derive": False,
                            "shared": False,
                            "shared_to": None,
                            "group_by": "",
                            "layout": "narrow",
                            "select_group_key": "",
                            "is_fixed_quick_screening": False,
                            "query": {
                                "must": [
                                    {
                                        "must": [
                                            {
                                                "in": {
                                                    "field_values.field006": [
                                                        "5oziwx7y2FkJnNO4"
                                                    ]
                                                }
                                            },
                                            {
                                                "in": {
                                                    "field_values.field007": [
                                                        "TwNJcYZr"
                                                    ]
                                                }
                                            }
                                        ]
                                    },
                                    {
                                        "should": [
                                            {
                                                "must": [
                                                    {
                                                        "in": {
                                                            "field_values.field017": [
                                                                "done"
                                                            ]
                                                        }
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            "sort": [
                                {
                                    "field_values.field009": {
                                        "order": "desc"
                                    }
                                }
                            ],
                            "is_fold_all_groups": False,
                            "table_field_settings": [],
                            "include_subtasks": True,
                            "name": "已完成"
                        }
                    ],
                    "settings": {
                        "forms": [
                            {
                                "name": mocks.name(),
                                "notice": "感谢你能抽出几分钟时间将你的建议和问题告诉我们+1！",
                                "enable": True,
                                "file_enable": True,
                                "agent_user": "5oziwx7y",
                                "field_uuids": [
                                    "field016"
                                ],
                                "uuid": mocks.ones_uuid(),
                                "owner": "5oziwx7y",
                                "create_time": mocks.now_timestamp()
                            }
                        ]
                    },
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
                    "update": 1
                }
            ]
        }
    )


def graghql_project():
    return generate_param(
        {'query': '{\n      projectPeeps(filter: $filter)'
                  '\n        {\n            uuid\n            name\n        }\n      }',
         'variables': {
             'filter': {
                 'enableWorkOrderForm_equal': True
             }
         }

         }
    )


def plug_update_forms():
    return generate_param(
        {'type': 1, 'project': ['5oziwx7y2FkJnNO4']}
    )


# def plug_query_proj():
#     p = [{'type': i} for i in range(4)]
#     return generate_param(p)

def plug_query_proj():
    return generate_param(
        {'type': 1}
    )


# 更新公告
def update_announcement():
    return generate_param(
        {
            "content": mocks.random_text()
        }
    )
