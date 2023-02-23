from falcons.helper import mocks
from falcons.ops import generate_param

from main.params.const import ACCOUNT

"""我的工作台workbench"""


def dashboard_add():
    """新增仪表盘"""
    return generate_param({
        "dashboard": {
            "name": f"Add仪表盘-{mocks.num()}",
            "pinned": True,
            "shared": False,
            "shared_to": []
        }
    })


def dashboard_update():
    """更新仪表盘"""
    return generate_param({
        "dashboard": {
            "uuid": "",  # 仪表盘uuid 用例中赋值
            "name": f"Up仪表盘-{mocks.num()}",
            "pinned": True,
            "shared": False,
            "shared_to": []
        }
    })


def dashboard_opt():
    return generate_param({})


def dashboard_query(dashboard_uuid):
    """查询仪表盘"""
    p = {
        "query": '\n    query {\n      cards (\n        filter: {\n          objectId_equal: \"%s\"\n'
                 '          objectType_equal: \"dashboard\"\n          status_equal: \"normal\"\n        },\n'
                 '        orderBy: {  layoutY: ASC, layoutX: ASC }\n      ) {\n        key\n        uuid\n'
                 '        name\n        description\n        type\n        layoutX\n        layoutY\n'
                 '        layoutW\n        layoutH\n        config\n      }\n    }\n  ' % dashboard_uuid,
        "variables": {}
    }

    return generate_param(p)


def card_add(car_type: str, layout: dict, config: dict):
    """添加卡片"""
    name = car_type.split('_')[0]
    p = {
        'card': {
            'name': f'{name}-{mocks.two_num()}',
            'type': car_type,
            'layout': layout,
            'config': config,
            'dashboard_uuid': '',  # assign in case
        }
    }

    return generate_param(p)


def data_report_type():
    """仪表盘-数据报表类型"""

    p = {
        "query": "\n    query {\n    reportCategories(\n      filter: { project_equal: \"%s\", containerType_equal: 1 }\n      orderBy: {\n        createTime: ASC\n        detailType: DESC\n        namePinyin: ASC\n      }\n    ){\n      \n  uuid\n  name\n  key\n  detailType\n  canUpdate\n  canDelete\n\n    }\n\n    projectReports(\n      filter: { project_equal: \"%s\" }\n      orderBy: {\n        updateTime: DESC\n        namePinyin: ASC\n      }\n    ){\n      uuid\n      key\n      name\n      uuid\n      owner {\n        name\n        uuid\n      }\n      \n      project {\n        uuid\n      }\n    \n      reportCategory {\n        uuid\n        name\n        key\n        detailType\n      }\n      updateTime\n      reportType: detailType\n      config\n    }\n  }" % (
            ACCOUNT.project_uuid, ACCOUNT.project_uuid)
    }

    return generate_param(p)


def dashboard_config():
    """关闭/开启常用仪表盘"""

    return generate_param({
        "pinned": False,
        "default": False
    })


# ------------------------------------------------------------------------------------

"""工作台-筛选器"""


def export_task_job():
    """导出工作项"""
    p = {
        "name": f'{ACCOUNT.project_uuid}-任务-全部任务.csv',
        "sort": [
            {
                "field_values.field009": {
                    "order": "desc"
                }
            }
        ],
        "query": {
            "must": [
                {
                    "should": [
                        {
                            "must": [
                                {
                                    "in": {
                                        "field_values.field004": [
                                            "${currentUser}"
                                        ]
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "include_subtasks": True,
        "group_by": "",
        "field_uuids": [
            "field015",
            "field001",
            "field005",
            "field004",
            "field003",
            "field009",
            "field018",
            "field019",
            "field020",
            "field013",
            "field012"
        ]
    }
    return generate_param(p)


def filter_view_add():
    p = {
        "shared": False,
        "shared_to": [],
        "group_by": "",
        "layout": "narrow",
        "select_group_key": "",
        "is_fixed_quick_screening": False,
        "query": {
            "must": [
                {
                    "not_in": {
                        "uuid": [
                            None
                        ]
                    }
                }
            ]
        },
        "condition": {
            "lock_conditions": [],
            "condition_groups": [
                [
                    {
                        "field_uuid": "field001",
                        "operate": {
                            "operate_id": "match",
                            "predicate": "match",
                            "negative": False,
                            "label": "filter.addQueryContent.include",
                            "filter_query": "match"
                        },
                        "value": None
                    },
                    {
                        "field_uuid": "field007",
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
                        "field_uuid": "field017",
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
                        "field_uuid": "field004",
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
            ],
            "is_init": True
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
        "is_show_derive": False,
        "display_type": "sub_tree",
        "include_subtasks": True,
        "name": f"T视图-{mocks.ones_uuid().upper()}",
        "board_settings": None
    }
    return generate_param(p)


def filter_view_config():
    """筛选视图管理"""

    return generate_param({
        "configs": [
            {
                "view_uuid": "ft-t-001",
                "is_show": True
            },
            {
                "view_uuid": "ft-t-002",
                "is_show": True
            }
        ]
    })


def filter_view_config_list():
    """筛选视图列表"""

    return generate_param()


# ------------------------------------------------------------------------------------

def card_gql(dashboard_uuid):
    """查询仪表盘"""

    return generate_param({
        'query': '\n    query {\n      cards (\n        filter: {\n          objectId_equal: \"%s\"\n          '
                 'objectType_equal: \"dashboard\"\n          status_equal: \"normal\"\n        },\n        '
                 'orderBy: {  layoutY: ASC, layoutX: ASC }\n      ) {\n        key\n        uuid\n        '
                 'name\n        description\n        type\n        layoutX\n        layoutY\n        '
                 'layoutW\n        layoutH\n        config\n      }\n    }\n  ' % dashboard_uuid,
        'variables': {}
    })
