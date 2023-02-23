from falcons.helper import mocks
from falcons.ops import generate_param

from main.params.const import ACCOUNT


def version_add():
    """新增版本"""
    return generate_param({
        "version": {
            "release_time": None,
            "title": f'ProVersion-{mocks.ones_uuid()}',
            "assign": None,
            "product_uuids": []  # 用例中赋值，产品uuid
        }
    })


def version_relate_product():
    """产品版本关联产品"""
    return generate_param({
        "product_uuids": []  # 用例中赋值，产品uuid
    })


def version_relate_sprint():
    """版本关联迭代"""
    return generate_param({
        "sprint_uuid": ""  # 用例中赋值，产品uuid
    })


def add_member_permit(permit):
    """新增成员权限"""
    return generate_param({
        "permission_rule": {
            "context_type": "product",
            "context_param": {
                "product_uuid": ""  # 用例中赋值，产品uuid
            },
            "permission": permit,
            "user_domain_type": "single_user",
            "user_domain_param": ACCOUNT.user.owner_uuid
        }
    })


def add_product_module():
    """新增模块"""
    return generate_param({
        "item": {
            "name": f'ProModule-{mocks.ones_uuid()}',
            "description": "",
            "parent": None,
            "item_type": "product_module",
            "product": ""  # 用例中赋值，产品uuid
        }
    })


def up_product_module():
    """产品模块更新"""
    return generate_param({
        "item": {
            "name": f'UpModule-{mocks.ones_uuid()}',
            "description": "update_test/update_test"
        }
    })


def sort_product_module():
    """产品模块排序"""
    return generate_param({
        "item": {
            "sort": {
                "previous_uuid": "",  # 同级别的module_uuid
                "previous_relation": "brother",
                "parent_relation": ""
            }
        }
    })


def products_data():
    p = {
        "query": "\n    {\n      buckets(groupBy: $groupBy, orderBy: $orderBy) {\n        key\n        \n        products(filterGroup: $productsFilter, orderBy: $productsOrderBy) {\n          name\n          uuid\n          key\n          owner {\n            uuid\n            name\n            avatar\n          }\n\n          createTime\n          assign {\n            uuid\n            name\n            avatar\n          }\n          \n  productComponents {\n    uuid\n    name\n    parent{\n      uuid\n    }\n    key\n    type\n    contextType\n    contextParam1\n    contextParam2\n    position\n    templateUUID\n    urlSetting{\n      url\n    }\n    views{\n      key\n      uuid\n      name\n      builtIn\n    }\n  }\n\n          \n  taskCount\n  taskCountToDo\n  taskCountDone\n  taskCountInProgress\n\n          \n        }\n      }\n    }",
        "variables": {
            "orderBy": {},
            "groupBy": {
                "products": {}
            },
            "productsOrderBy": {
                "createTime": "DESC"
            },
            "productsFilter": []
        }
    }

    return generate_param(p)


def _delete():
    """相关删除操作"""
    return generate_param({})


def product_delete():
    """删除产品"""
    return generate_param({}, **{'product_uuid': ''})


# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*


def _search():
    """搜索，查询相关"""
    return generate_param({})


def version_update():
    """版本信息更新"""
    return generate_param({
        "version": {
            "release_time": mocks.now_timestamp(),
            "uuid": "",  # 用例中赋值，版本uuid
            "title": f"V-{mocks.ones_uuid()}",
            "desc": "",
            "assign": ACCOUNT.user.owner_uuid,
            "create_time": 1647414755,
            "category": "todo",  # 默认未开始状态
            "sprints": [],
            "product_uuids": []
        }
    })


# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*


def graphql_body(body):
    """工时日志操作传参"""

    return generate_param(body)


def time_log_list():
    """工时日志列表信息"""
    p = {
        "query": '\n    query {\n    reportCategories(\n      filter: { project_equal: \"\" }\n      orderBy: '
                 '{\n        createTime: ASC\n        detailType: DESC\n        namePinyin: ASC\n      }\n    )'
                 '{\n      \n  uuid\n  name\n  key\n  detailType\n  canUpdate\n  canDelete\n\n    }\n\n    '
                 'teamReports(\n      \n      orderBy: {\n        updateTime: DESC\n        namePinyin: ASC\n      }'
                 '\n    ){\n      uuid\n      key\n      name\n      uuid\n      owner {\n        name\n        uuid'
                 '\n      }\n      \n      reportCategory {\n        uuid\n        name\n        key\n        '
                 'detailType\n      }\n      updateTime\n      reportType: detailType\n      config\n    }\n  }'
    }

    return generate_param(p)


def group_add():
    """新增分组"""
    p = {
        "query": '\n    mutation AddReportCategory {\n      addReportCategory (name: $name) '
                 '{\n        key\n      }\n    }\n  ',
        "variables": {
            "name": f"FZ-{mocks.ones_uuid()}"
        }
    }

    return p


def group_rename():
    """重命名分组"""
    p = {
        "query": '\n    mutation UpdateReportCategory {\n      updateReportCategory '
                 '(key: $key name: $name) {\n        key\n      }\n    }\n  ',
        "variables": {
            "key": '',  # 分组key，用例中赋值
            "name": f"Rename-{mocks.ones_uuid()}"
        }
    }

    return p


def group_report_delete(key=None):
    """删除分组和报表"""
    p = {
        "query": '\n    mutation DeleteReportCategory {\n      deleteReportCategory '
                 '(key: $key delete_reports: $delete_reports) {\n        key\n      }\n    }\n  ',
        "variables": {
            "key": key if key else "",  # 分组key，用例中赋值
            "delete_reports": True
        }
    }

    return p


def group_delete():
    """删除分组"""
    p = {
        "query": '\n    mutation DeleteReportCategory {\n      deleteReportCategory '
                 '(key: $key) {\n        key\n      }\n    }\n  ',
        "variables": {
            "key": ""  # 分组key，用例中赋值
        }
    }

    return p


def change_group():
    """更改所属分组"""
    p = {
        "query": "\n    mutation UpdateTeamReport {\n      updateTeamReport (key: $key report_category: "
                 "$report_category) {\n        key\n      }\n    }\n  ",
        "variables": {
            "key": "",  # 报表key，用例中赋值
            "report_category": ""  # 分组uuid，用例中赋值
        }
    }

    return generate_param(p)


def add_team_report(detail_type='manhour_log'):
    """
    新建报表
    :param
        detail_type  # 报表类型
            manhour_overview  # 工时总览
            manhour_log  # 工时日志
    """
    p = {
        "query": '\n    mutation AddTeamReport {\n      addTeamReport (name: $name config: '
                 '$config detail_type: $detail_type report_category: $report_category) '
                 '{\n        key\n      }\n    }\n  ',
        "variables": {
            "name": f"AddR-{mocks.ones_uuid()}",
            "config": '{\"filter\":null,\"include_subtasks\":true,\"dimensions\":[{\"aggregation\":'
                      '\"user\",\"order_by\":\"default\",\"order\":\"asc\",\"limit\":10,\"values\":'
                      '[],\"date_range_absolute\":[]}]}',
            "detail_type": detail_type,
            "report_category": ""  # 分组uuid，用例中赋值
        }
    }

    return generate_param(p)


def report_update(repost_key):
    """编辑报表"""
    p = {
        "query": '\n    mutation UpdateTeamReport {\n      updateTeamReport (key: $key config: $config) '
                 '{\n        key\n      }\n    }\n  ',
        "variables": {
            "key": repost_key,  # 报表key，用例中赋值
        }
    }

    return generate_param(p)


def report_rename():
    """报表重命名"""
    p = {
        "query": '\n    mutation UpdateTeamReport {\n      updateTeamReport (key: $key name: $name) '
                 '{\n        key\n      }\n    }\n  ',
        "variables": {
            "key": "",  # 报表key，用例中赋值
            "name": f"Rename-{mocks.ones_uuid()}"
        }
    }

    return generate_param(p)


def hour_log_export():
    """工时日志报表导出"""
    p = {
        "report_config": {
            "filter": None,
            "include_subtasks": True,
            "dimensions": [
                {
                    "aggregation": "user",
                    "order_by": "default",
                    "order": "asc",
                    "limit": 10,
                    "values": [],
                    "date_range_absolute": []
                }
            ]
        },
        "detail_type": "manhour_log",  # 默认工时日志
        "file_type": "csv",
        "report_uuid": ""  # 报表uuid，用例中赋值
    }

    return generate_param(p)


def report_delete():
    """删除团队报表"""
    p = {
        "query": '\n    mutation DeleteTeamReport {\n      deleteTeamReport (key: $key) '
                 '{\n        key\n      }\n    }\n  ',
        "variables": {
            "key": ""  # 报表key，用例中赋值
        }
    }

    return generate_param(p)


def update_dimension(variable):
    """更新报表维度"""
    p = '{\"dimensions\":[{\"aggregation\":\"%s\",\"manhour_aggregation\":\"department\",' \
        '\"order_by\":\"default\",\"manhour_order_by\":\"default\",\"order\":\"desc\",\"limit\":10,' \
        '\"values\":[],\"date_range_absolute\":[]}],\"filter\":null,\"include_subtasks\":true}' % variable

    return p


def update_filter(variable):
    """更新报表筛选"""
    p = '{\"dimensions\":[{\"aggregation\":\"department\",\"manhour_aggregation\":\"department\",' \
        '\"order_by\":\"default\",\"manhour_order_by\":\"default\",\"order\":\"desc\",\"limit\":10,' \
        '\"values\":[],\"date_range_absolute\":[]}],\"filter\":{\"must\":[{\"should\":[{\"must\":' \
        '[{\"in\":{\"field_values.field011\":[\"%s\"]}},{\"date_range\":' \
        '{\"field_values.field009\":{\"equal\":\"today\"}}}]}]}]},\"include_subtasks\":true}' % variable

    return p


def register_every_1():
    p = '{\"dimensions\":[{\"aggregation\":\"task_assign\",\"manhour_aggregation\":\"day\",\"order_by\"' \
        ':\"default\",\"manhour_order_by\":\"default\",\"order\":\"desc\",\"limit\":10,\"values\":[],' \
        '\"date_range_absolute\":[]},{\"aggregation\":\"user\",\"manhour_aggregation\":\"user\",' \
        '\"order_by\":\"record_manhour\",\"manhour_order_by\":\"record_manhour\",\"order\":\"desc\",' \
        '\"limit\":10}],\"filter\":null,\"include_subtasks\":true}'

    return p


def register_every_update(x_axis, y_axis):
    p = '{\"dimensions\":[{\"aggregation\":\"%s\",\"manhour_aggregation\":\"day\",' \
        '\"order_by\":\"default\",\"manhour_order_by\":\"default\",\"order\":\"desc\",' \
        '\"limit\":10,\"values\":[],\"date_range_absolute\":[]},{\"aggregation\":' \
        '\"%s\",\"manhour_aggregation\":\"user\",\"order_by\":\"record_manhour\",' \
        '\"manhour_order_by\":\"record_manhour\",\"order\":\"desc\",\"limit\":10,' \
        '\"values\":[],\"date_range_absolute\":[]}],\"filter\":null,\"include_subtasks\":true}' % (x_axis, y_axis)

    return p


def register_every_3(variable):
    p = '{\"dimensions\":[{\"aggregation\":\"week\",\"manhour_aggregation\":\"day\",' \
        '\"order_by\":\"default\",\"manhour_order_by\":\"default\",\"order\":\"desc\",' \
        '\"limit\":10,\"values\":[],\"date_range_absolute\":[]},{\"aggregation\":' \
        '\"task_status\",\"manhour_aggregation\":\"user\",\"order_by\":\"record_manhour\",' \
        '\"manhour_order_by\":\"record_manhour\",\"order\":\"desc\",\"limit\":10,\"values\":[],' \
        '\"date_range_absolute\":[]}],\"filter\":{\"must\":[{\"should\":[{\"must\":[{\"in\":' \
        '{\"field_values.field011\":[\"%s\"]}}]},{\"must\":[{\"date_range\":' \
        '{\"field_values.field009\":{\"equal\":\"today\"}}}]}]}]},\"include_subtasks\":true}' % variable

    return p


def register_every_day_export():
    """成员（登记人）-每天工时总览报表导出"""
    p = {
        "report_config": {
            "chart_style": "bar",
            "filter": None,
            "include_subtasks": True,
            "dimensions": [
                {
                    "aggregation": "task_assign",
                    "order_by": "default",
                    "order": "asc",
                    "limit": 10,
                    "values": [],
                    "date_range_absolute": []
                },
                {
                    "aggregation": "sprint",
                    "order_by": "default",
                    "order": "asc",
                    "limit": 10
                }
            ]
        },
        "detail_type": "manhour_overview",
        "file_type": "csv",
        "report_uuid": ""  # 报表uuid，用例中赋值
    }

    return generate_param(p)


# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
# 项目报表相关

def proj_reports(project_uuid=None):
    """项目报表列表"""
    project_uuid = project_uuid if project_uuid else ACCOUNT.project_uuid
    p = {
        "query": '\n    query {\n    projectReports(\n      filter: { project_equal: \"%s\" }\n      '
                 'orderBy: {\n        updateTime: DESC\n        namePinyin: ASC\n      }\n    ){\n      '
                 'uuid\n      key\n      name\n      uuid\n      owner {\n        name\n        uuid\n      }\n'
                 '      \n      project {\n        uuid\n      }\n    \n      reportCategory {\n        uuid\n'
                 '        name\n        key\n        detailType\n      }\n      updateTime\n      '
                 'reportType: detailType\n      config\n    }\n  }' % project_uuid
    }

    return generate_param(p)


def proj_report_categories(pid=None):
    """项目报表所有分组"""
    project_uuid = ACCOUNT.project_uuid if not pid else pid
    p = {
        "query": '\n    query {\n    reportCategories(\n      filter: { project_equal: \"%s\", '
                 'containerType_equal: 1 }\n      orderBy: {\n        createTime: ASC\n        '
                 'detailType: DESC\n        namePinyin: ASC\n      }\n    ){\n      \n  uuid\n  name\n  '
                 'key\n  detailType\n  canUpdate\n  canDelete\n createTime\n\n}}' % project_uuid
    }

    return generate_param(p)


def report_categories_update(key=None, name=None):
    return generate_param({
        "query": "\n    mutation UpdateReportCategory {\n      updateReportCategory (key: $key name: $name) {\n        key\n      }\n    }\n  ",
        "variables": {
            "key": key if key else mocks.name(),  # 分组key，用例中赋值
            "name": name if name else f"Rename-{mocks.ones_uuid()}"
        }
    })


def report_category_delete(key, is_report_delete=False):
    return generate_param({
        "query": "\n    mutation DeleteReportCategory {\n      deleteReportCategory (key: $key delete_reports: $delete_reports) {\n        key\n      }\n    }\n  ",
        "variables": {
            "key": key,
            "delete_reports": is_report_delete
        }
    })


def add_proj_report(detail_type, category="", pid=None, config=None):
    """
    新增项目报表
    :param config:
    :param detail_type  报表类型
    :param category  报表分组uuid
    :param pid:
    """
    project_uuid = pid if pid else ACCOUNT.project_uuid
    configs = {
        'manhour_overview': '{\"chart_style\":\"bar\",\"filter\":{\"must\":[{\"must\":[{\"in\":'
                            '{\"field_values.field006\":[\"%s\"]}}]}]},\"include_subtasks\"'
                            ':true,\"dimensions\":[{\"aggregation\":\"task_assign\",\"order_by\":\"default\",'
                            '\"order\":\"asc\",\"limit\":10,\"values\":[],\"date_range_absolute\":[]},'
                            '{\"aggregation\":\"sprint\",\"order_by\":\"default\",\"order\":\"asc\",'
                            '\"limit\":10}]}' % project_uuid,

        'task_distribution': '{\"chart_style\":\"bar\",\"filter\":{\"must\":[{\"must\":[{\"in\":'
                             '{\"field_values.field006\":[\"%s\"]}}]}]},\"include_subtasks\":'
                             'true,\"dimensions\":[{\"aggregation\":\"terms\",\"field_uuid\":\"field005\",'
                             '\"limit\":10,\"order_by\":\"default\",\"order\":\"asc\",\"values\":[]},'
                             '{\"aggregation\":\"terms\",\"field_uuid\":\"\",\"order_by\":\"\",\"order\":\"\",'
                             '\"values\":[],\"limit\":0}]}' % project_uuid,

        'task_trend': '{\"chart_style\":\"area_line\",\"filter\":{\"must\":[{\"must\":[{\"in\":{\"field_values.'
                      'field006\":[\"%s\"]}}]}]},\"include_subtasks\":true,\"dimensions\":'
                      '[{\"aggregation\":\"date_histogram\",\"field_uuid\":\"field009\",\"date_interval\":'
                      '\"1d\",\"date_range\":\"30d\",\"include_weekend\":true,\"is_accumulative\":false},'
                      '{\"aggregation\":\"terms\",\"field_uuid\":\"\",\"limit\":0,\"values\":[],\"order_by\":'
                      '\"\",\"order\":\"\"}]}' % project_uuid,

        'single_selection_stay_duration': '{\"filter\":{\"must\":[{\"must\":[{\"in\":{\"field_values.field006\":'
                                          '[\"%s\"]}}]},{\"not_in\":{\"field_values.field021\":'
                                          '[\"UtXV3JgY\",\"UgEqSuwk\"]}}]}]}]},\"include_subtasks\":true,'
                                          '\"dimensions\":[{\"aggregation\":\"terms\",\"field_uuid\":'
                                          '\"field004\",\"order_by\":\"default\",\"order\":\"asc\",\"values\"'
                                          ':[],\"limit\":0}]}' % project_uuid,

        'task_field_retention_duration': '{\"chart_style\":\"bar\",\"filter\":{\"must\":[{\"must\":[{\"in\":'
                                         '{\"field_values.field006\":[\"%s\"]}}]}]},'
                                         '\"include_subtasks\":true,\"dimensions\":[{\"aggregation\":'
                                         '\"date_histogram\",\"date_interval\":\"2d\"},{\"aggregation\":'
                                         '\"terms\",\"field_uuid\":\"field005\",\"limit\":10,\"order_by\":'
                                         '\"default\",\"order\":\"asc\",\"values\":[]}]}' % project_uuid,

        'defect_created_solved_trend': '{\"chart_style\":\"line\",\"filter\":{\"must\":[{\"must\":[{\"in\":'
                                       '{\"field_values.field006\":[\"%s\"]}}]},{\"should\":[{\"must\":'
                                       '[{\"in\":{\"field_values.field007\":[\"AswjTtzD\"]}},{\"not_in\":'
                                       '{\"field_values.field021\":[\"UtXV3JgY\",\"UgEqSuwk\"]}}]}]}]},'
                                       '\"include_subtasks\":true,\"dimensions\":[{\"aggregation\":\"date_histogram\",'
                                       '\"date_interval\":\"1d\",\"date_range\":\"30d\",\"include_weekend\":true,'
                                       '\"is_accumulative\":false},{\"config\":{\"show_created_amount\":true,'
                                       '\"show_solved_amount\":true}}]}' % project_uuid,

        'defect_detect_escape_rate': '{\"chart_style\":\"bar\",\"filter\":{\"must\":[{\"must\":[{\"in\":'
                                     '{\"field_values.field006\":[\"%s\"]}}]},{\"should\":[{\"must\":'
                                     '[{\"in\":{\"field_values.field007\":[\"AswjTtzD\"]}},{\"not_in\":'
                                     '{\"field_values.field021\":[\"UtXV3JgY\",\"UgEqSuwk\"]}}]}]}]},'
                                     '\"include_subtasks\":true,\"dimensions\":[{\"aggregation\":\"terms\",\"field_uuid\
                                     ":\"field011\",\"limit\":10,\"order_by\":\"default\",\"order\":\"asc\",\"values\":'
                                     '[]},\"show_detect_rate\":true,\"show_escape_rate\":true}}]}'
                                     % project_uuid,

        'defect_reopen_distribution': '{\"chart_style\":\"bar\",\"filter\":{\"must\":[{\"must\":[{\"in\":'
                                      '{\"field_values.field006\":[\"%s\"]}}]},{\"should\":[{\"must\":'
                                      '[{\"in\":{\"field_values.field007\":[\"AswjTtzD\"]}},{\"not_in\":'
                                      '{\"field_values.field021\":[\"UtXV3JgY\",\"UgEqSuwk\"]}}]}]}]},'
                                      '\"include_subtasks\":true}' % project_uuid,

        'demand_delivery_situation': '{\"chart_style\":\"bar\",\"filter\":{\"must\":[{\"must\":[{\"in\":'
                                     '{\"field_values.field006\":[\"%s\"]}}]},{\"should\":[{\"must\":'
                                     '[{\"in\":{\"field_values.field007\":[\"UPH6U8vW\"]}},{\"not_in\":{\"field_values.'
                                     'field021\":[\"UtXV3JgY\",\"UgEqSuwk\"]}}]}]}]},\"include_subtasks\":true,'
                                     '\"dimensions\":[{\"aggregation\":\"terms\",\"field_uuid\":\"field011\",'
                                     '\"order_by\":\"default\",\"order\":\"asc\",\"limit\":10},{\"config\":'
                                     '{\"plan_end_time_field\":\"field013\",\"show_demand_count\":true,'
                                     '\"show_punctuality_demand_count\":true}}]}' % project_uuid,

        'task_avg_survival_duration': '{\"chart_style\":\"bar\",\"filter\":{\"must\":[{\"must\":[{\"in\":'
                                      '{\"field_values.field006\":[\"%s\"]}}]},{\"should\":'
                                      '[{\"must\":[{\"in\":{\"field_values.field007\":[\"AswjTtzD\"]}},'
                                      '{\"not_in\":{\"field_values.field021\":[\"UtXV3JgY\",\"UgEqSuwk\"]}}]}]}]},'
                                      '\"include_subtasks\":true,\"dimensions\":[{\"aggregation\":\"terms\",'
                                      '\"field_uuid\":\"field011\",\"limit\":10,\"order_by\":\"default\",\"order\":'
                                      '\"asc\",\"values\":[]}]}' % project_uuid,

        'manhour_log': '{\"filter\":{\"must\":[{\"must\":[{\"in\":{\"field_values.field006\":[\"%s\"]'
                       '}}]}]},\"include_subtasks\":true,\"dimensions\":[{\"aggregation\":\"user\",\"order_by\":'
                       '\"default\",\"order\":\"asc\",\"limit\":10,\"values\":[],\"date_range_absolute\":[]}]}'
                       % project_uuid,
    }

    p = {
        "query": '\n    mutation AddProjectReport {\n      addProjectReport (name: $name config: $config '
                 'project: $project detail_type: $detail_type report_category: $report_category) {\n'
                 '        key\n      }\n    }\n  ',
        "variables": {
            "name": f"{detail_type}-{mocks.num()}",
            "config": config if config else configs.get(detail_type),
            "project": project_uuid,
            "detail_type": detail_type,
            "report_category": category
        }
    }

    return generate_param(p)


def get_proj_report():
    """获取项目内存在的报表"""
    return generate_param({
        "query": 'query {\n    reportCategories(\n      filter: { project_equal: \"%s\", containerType_equal:'
                 ' 1 }\n      orderBy: {\n        createTime: ASC\n        detailType: DESC\n        '
                 'namePinyin: ASC\n      }\n    ){\n      \n  uuid\n  name\n  key\n  detailType\n  '
                 'canUpdate\n  canDelete\n\n    }\n\n    projectReports(\n      filter: '
                 '{ project_equal: \"%s\" }\n      orderBy: {\n        updateTime: DESC\n        '
                 'namePinyin: ASC\n      }\n    ){\n      uuid\n      key\n      name\n      uuid\n      '
                 'owner {\n        name\n        uuid\n      }\n      \n      project {\n        uuid\n      '
                 '}\n    \n      reportCategory {\n        uuid\n        name\n        key\n        '
                 'detailType\n      }\n      updateTime\n      reportType: detailType\n      config\n    }\n  '
                 '}' % (ACCOUNT.project_uuid, ACCOUNT.project_uuid)
    })


def export_proj_report(detail_type, report_uuid, dimensions=None, project_uuid=None):
    """导出项目内报表"""
    pid = project_uuid if project_uuid else ACCOUNT.project_uuid
    return generate_param({
        "report_config": {
            "dimensions": dimensions,
            "filter": {
                "must": [
                    {
                        "must": [
                            {
                                "in": {
                                    "field_values.field006": [
                                        pid
                                    ]
                                }
                            }
                        ]
                    }
                ]
            },
            "include_subtasks": True
        },
        "detail_type": detail_type,
        "file_type": "csv",
        "report_uuid": report_uuid
    }, is_project=True)


def update_proj_report(key, name=None, group=None):
    """更新项目报告信息"""
    variables = {"key": key}
    if name:
        variables['name'] = name
    if group:
        variables['report_category'] = group
    return generate_param({
        "query": "mutation UpdateProjectReport {\n      updateProjectReport (key: $key %s %s) {\n        key\n      }\n    }" % (
            'name: $name' if name else '', 'report_category: $report_category' if group else ''),
        "variables": variables
    })


def report_add_dashboard_card(report_uuid, dashboard_uuid, report_name):
    """报告添加到仪表盘(仪表盘卡片)"""
    p = {
        "card": {
            "config": {
                "project_uuid": ACCOUNT.project_uuid,
                "report_uuid": report_uuid
            },
            "dashboard_uuid": dashboard_uuid,
            "name": report_name,
            "layout": {
                "w": 6,
                "h": 4,
                "x": 0,
                "y": 7
            },
            "type": "report"
        }
    }

    return generate_param(p)


def report_add_dashboard_proj_overview(report_uuid, component_id, report_name, project_uuid=None):
    """报告添加到仪表盘(项目概览)"""

    p = {
        "query": "\n    mutation AddCard {\n      addCard( name: $name\n        object_id: $object_id object_type: $object_type\n        layout_x: $layout_x\n        layout_y: $layout_y\n        layout_w: $layout_w\n        layout_h: $layout_h\n        config: $config\n        type: $type\n        description: $description\n        status: $status\n        \n        ) {\n        key\n      }\n    }\n  ",
        "variables": {
            "name": report_name,
            "description": "",
            "object_id": component_id,
            "object_type": "project_component",
            "layout_x": 6,
            "layout_y": 9,
            "layout_w": 6,
            "layout_h": 4,
            "config": "{\"project_uuid\":\"%s\",\"report_uuid\":\"%s\"}" % (
                project_uuid if project_uuid else ACCOUNT.project_uuid, report_uuid),
            "type": "report",
            "status": "normal"
        }
    }

    return generate_param(p)


def prj_overview_dashboard(overview_cid):
    """
    查看仪表盘-项目概览
    :param overview_cid: 项目概览组件uuid
    :return:
    """
    p = {
        "query": "\n    query {\n      cards (\n        filter: {\n          objectId_equal: \"%s\"\n          objectType_equal: \"project_component\"\n          status_equal: \"normal\"\n        },\n        orderBy: {  layoutY: ASC, layoutX: ASC }\n      ) {\n        key\n        uuid\n        name\n        description\n        type\n        layoutX\n        layoutY\n        layoutW\n        layoutH\n        config\n      }\n    }\n  " %
                 (overview_cid),
        "variables": {}
    }
    return generate_param(p)


def proj_report_add_group(pid=None):
    """项目报表新建分组"""
    p = {
        "query": 'mutation AddReportCategory {\n      addReportCategory (project: $project name: $name) '
                 '{\n        key\n      }\n    }\n  ',
        "variables": {
            "project": ACCOUNT.project_uuid if not pid else pid,
            "name": f"分组-{mocks.ones_uuid()}"
        }
    }

    return generate_param(p)


def report_update_group(key, group_uuid):
    """报表变更分组"""
    p = {
        "query": 'mutation UpdateProjectReport {\n      updateProjectReport (key: $key report_category: '
                 '$report_category) {\n        key\n      }\n    }\n  ',
        "variables": {
            "key": key,
            "report_category": group_uuid
        }
    }

    return generate_param(p)


def reports_and_groups(pid=None):
    '''
    参数：报表分组列表+报表列表
    :return:
    '''
    project_uuid = pid if pid else ACCOUNT.project_uuid
    return generate_param({
        "query": "\n    query {\n    reportCategories(\n    "
                 "  filter: { project_equal: \"%s\", containerType_equal: 1 }\n"
                 "      orderBy: {\n        createTime: ASC\n        detailType: DESC\n"
                 "        namePinyin: ASC\n      }\n    ){\n      \n  uuid\n  name\n  key\n "
                 " detailType\n  canUpdate\n  canDelete\n\n    }\n\n    projectReports(\n"
                 "      filter: { project_equal: \"%s\" }\n      orderBy: {\n"
                 "        updateTime: DESC\n        namePinyin: ASC\n      }\n    ){\n"
                 "      uuid\n      key\n      name\n      uuid\n      owner {\n "
                 "       name\n        uuid\n      }\n      \n      project {\n "
                 "       uuid\n      }\n    \n      reportCategory {\n        uuid\n  "
                 "      name\n        key\n        detailType\n      }\n      updateTime\n "
                 "     reportType: detailType\n      config\n    }\n  }" % (project_uuid, project_uuid)
    })


def proj_report_delete(key):
    """删除项目报表"""

    p = {
        "query": 'mutation DeleteProjectReport {\n      deleteProjectReport (key: $key) '
                 '{\n        key\n      }\n    }\n ',
        "variables": {
            "key": key
        }
    }

    return generate_param(p)


def issue_type_scope_equal(scope_uuid, end_status_uuid):
    p = {
        "query": "\n    query {\n      transitions(\n        filter: {\n          issueTypeScope_equal: \"%s\"\n          endStatus_equal: \"%s\"\n        }\n      ){\n        name\n        startStatus{\n            uuid\n            name\n        }\n      }\n    }\n  " % (
            scope_uuid, end_status_uuid)
    }
    return generate_param(p)


def report_datasets(detail_type):
    """报表数据集"""

    return generate_param({'detail_type': detail_type}, is_project=True)
