from falcons.com.meta import OnesParams
from falcons.helper import mocks
from falcons.ops import generate_param

from main.params import report_html as rh
from main.params.const import ACCOUNT


def query_case_config_list():
    """用例属性配置列表"""
    p = OnesParams()
    p.json = {
        "operationName": "QUERY_TEST_CASE_FIELD_CONFIG_LIST",
        "query": 'query QUERY_TEST_CASE_FIELD_CONFIG_LIST {\n  testcaseFieldConfigs(orderBy: '
                 '{isDefault: DESC, createTime: ASC}) {\n    key\n    uuid\n    name\n    namePinyin\n    '
                 'isDefault\n    testcaseLibraries {\n      uuid\n      name\n      __typename\n    }\n    '
                 '__typename\n  }\n}\n'
    }
    p.extra = {
        "uri_args":
            {
                "team_uuid": ACCOUNT.user.team_uuid,
            },
    }
    return p,


def query_library_list():
    """用例库列表"""

    return generate_param({
        "query": 'query QUERY_LIBRARY_LIST{\n  testcaseLibraries(\n    orderBy:{\n      isPin:DESC\n      '
                 'namePinyin:ASC\n    }\n  ){\n    uuid,\n    name,\n    isPin,\n    isSample,\n    '
                 'testcaseCaseCount,\n    testcaseFieldConfig{\n      key,\n      uuid,\n      '
                 'name\n    }\n  }\n}',
        "variables": {}
    })


def query_library_detail():
    """用例库详情"""
    p = OnesParams()
    p.json = {
        "operationName": "QUERY_LIBRARY_DETAIL",
        "variables": {
            "libraryFilter": {
                "uuid_in": [
                    ''
                ]
            }
        },
        "query": 'query QUERY_LIBRARY_DETAIL {\n  testcaseLibraries(filter: $libraryFilter) {\n    '
                 'key\n    uuid\n    name\n    isPin\n    namePinyin\n    createTime\n    '
                 'members {\n      type\n      param\n      __typename\n    }\n    '
                 'testcaseCaseCount\n    testcaseFieldConfig {\n      key\n      uuid\n      '
                 'name\n      __typename\n    }\n    __typename\n  }\n}\n'
    }
    p.extra = {
        "uri_args":
            {
                "team_uuid": ACCOUNT.user.team_uuid,
            },
    }
    return p,


def add_case_library():
    """新增用例库"""
    p = OnesParams()
    p.json = {
        "library": {
            "name": f"test新建用例库{mocks.num()}",
            "members": [
                {
                    "user_domain_type": "testcase_administrators",
                    "user_domain_param": ""
                },
                {
                    "user_domain_type": "single_user",
                    "user_domain_param": ACCOUNT.user.owner_uuid
                }
            ],
            "field_config_uuid": ''
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p,


def case_field_config_list():
    """
    案例属性配置列表， ItemGraphql 接口参数
    :return:
    """
    return generate_param({
        "operationName": "QUERY_TEST_CASE_FIELD_CONFIG_LIST",
        "variables": {},
        "query": 'query QUERY_TEST_CASE_FIELD_CONFIG_LIST {\n  testcaseFieldConfigs(orderBy: '
                 '{isDefault: DESC, createTime: ASC}) {\n    key\n    uuid\n    name\n    namePinyin\n    '
                 'isDefault\n    testcaseLibraries {\n      uuid\n      name\n      __typename\n    '
                 '}\n    __typename\n  }\n}\n'
    })


def query_config_fields_list():
    """查询配置属性列表"""
    return generate_param({
        'query': 'query QUERY_CONFIG_FIELDS_LIST{\n  fields(\n  filter:$fieldFilter,\n  '
                 'orderBy:$orderBy\n ){\n   aliases,\n   name,\n   uuid,\n   namePinyin,\n   '
                 'fieldType,\n   defaultValue,\n   createTime,\n   hidden,\n   required,\n   '
                 'canUpdate,\n   builtIn,\n   allowEmpty,\n   options {\n     uuid,\n     '
                 'value,\n     color,\n     bgColor\n   },\n}\n}',
        'variables': {
            'fieldFilter': {
                'hidden_in': [
                    False
                ],
                'pool_in': [
                    'testcase'
                ],
                'context': {
                    'type_in': [
                        'testcase_field_config'
                    ],
                    'fieldConfigUUID_in': [
                        ''  # 属性配置 UUID
                    ]
                }
            },
            'orderBy': {
                'builtIn': 'DESC',
                'namePinyin': 'ASC'
            }
        }
    })


def library_add():
    """新建用例库"""

    return generate_param({
        "library": {
            "name": f'TestLib{mocks.ones_uuid()}',
            "members": [
                {
                    "user_domain_type": "testcase_administrators",
                    "user_domain_param": ""
                },
                {
                    "user_domain_type": "single_user",
                    "user_domain_param": ACCOUNT.user.team_uuid,
                }
            ],
            "field_config_uuid": ''  # 案例属性配置 UUID
        }
    })


def library_delete():
    """删除用例库"""
    return generate_param({})


def case_add():
    """添加案例"""
    return generate_param({
        'item': {
            'name': f'Test Case {mocks.ones_uuid().capitalize()}',
            'assign': ACCOUNT.user.owner_uuid,
            'priority': '',  # 案例优先级uuid
            'type': '',  # 案例类型 uuid
            'module_uuid': '',  # 模块UUID
            'condition': '',
            'library_uuid': '',  # 用例库 uuid
            'desc': '',
            'steps': [],
            'related_wiki_page': [],
            'testcase_case_steps': [],
            'item_type': 'testcase_case',
            'testcase_library': '',  # 案例库uuid
            'testcase_module': ''  # 案例所属模块uuid
        }
    })


def update_library_config():
    """更新用例库配置"""
    p = OnesParams()
    p.json = {
        "library": {
            "name": 'update用例库名',
            "members": [
                {
                    "user_domain_type": "testcase_administrators",
                    "user_domain_param": ""
                },
                {
                    "user_domain_type": "single_user",
                    "user_domain_param": ACCOUNT.user.owner_uuid
                }
            ],
            "field_config_uuid": '',
            "uuid": ''
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'library_uuid': ''
            },
    }
    return p,


def query_library_cast_list():
    """查询用例库的用例列表"""
    p = OnesParams()
    p.json = {
        "query": 'query PAGED_LIBRARY_TESTCASE_LIST($libraryFilter: Filter, $testCaseFilter: Filter,'
                 ' $orderByFilter: Filter) {\n  buckets(groupBy: {testcaseCases: {}}, '
                 'pagination: {limit: 50, after: \"\", preciseCount: false}) {\n    '
                 'testcaseCases(filterGroup: $testCaseFilter, orderBy: $orderByFilter, limit: 10000) {\n'
                 '      uuid\n      name\n      key\n      number\n      priority {\n        uuid\n        value\n'
                 '      }\n      type {\n        uuid\n        value\n      }\n    }\n    key\n    pageInfo {\n'
                 '      count\n      preciseCount\n      totalCount\n      startPos\n      startCursor\n'
                 '      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n'
                 '  testcaseLibraries(filter: $libraryFilter) {\n    key\n    name\n    uuid\n    '
                 'testcaseCaseCount\n    testcaseFieldConfig {\n      key\n      uuid\n      name\n    }\n  }\n}\n',
        "variables": {
            "testCaseFilter": [
                {
                    "testcaseLibrary_in": [
                        ""
                    ]
                }
            ],
            "libraryFilter": {
                "uuid_in": [
                    ""
                ]
            },
            "moduleFilter": {
                "uuid_in": [
                    "all"
                ]
            },
            "orderByFilter": {
                "namePinyin": "DESC"
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


def query_library_case_edit():
    """用例库配置"""

    return generate_param({
        "query": 'query QUERY_LIBRARY_TESTCASE_EDIT(\n  $fieldFilter:Filter,\n  $moduleFilter: Filter,\n  '
                 '$orderBy:Filter\n  ){\n  fields(\n  filter:$fieldFilter,\n  orderBy:$orderBy\n ){\n   '
                 'aliases,\n   name,\n   uuid,\n   namePinyin,\n   fieldType,\n   key,\n   defaultValue,\n   '
                 'createTime,\n   hidden,\n   required,\n   canUpdate,\n   builtIn,\n   allowEmpty,\n   '
                 'options {\n     uuid,\n     value,\n     color,\n     bgColor\n   },\n}\n  \n  testcaseModules(\n    '
                 'filter:$moduleFilter,\n    groupBy:{\n      testcaseLibrary:{}\n    },\n    orderBy: {\n      '
                 'isDefault: ASC,\n      position: ASC\n    }\n  ){\n    uuid,\n    name,\n    path,\n    '
                 'createTime,\n    isDefault,\n    position,\n    key,\n    testcaseCaseCount,\n    '
                 'testcaseLibrary{\n      key,\n      uuid,\n      name,\n      testcaseCaseCount,\n    },\n    '
                 'parent{\n      uuid,\n      name,\n      path,\n      createTime,\n      isDefault,\n      '
                 'position,\n      key\n    }\n  }\n}',
        "variables": {
            "fieldFilter": {
                "hidden_in": [
                    'false'
                ],
                "pool_in": [
                    "testcase"
                ],
                "context": {
                    "type_in": [
                        "testcase_field_config"
                    ],
                    "fieldConfigUUID_in": [
                        ""
                    ]
                }
            },
            "moduleFilter": {
                "testcaseLibrary_in": [
                    ""
                ]
            },
            "orderBy": {
                "namePinyin": "ASC"
            }
        }
    })


def add_library_module():
    """添加模块"""
    p = OnesParams()
    p.json = {
        "module": {
            "name": f"test添加模块{mocks.num()}",
            "parent_uuid": ""
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'library_uuid': ''
            },
    }
    return p,


def query_modules_library():
    """查找用例库里的所有模块"""
    p = OnesParams()
    p.json = {
        "query": 'query QUERY_MODULES_IN_LIBRARY($moduleFilter:Filter){\n  testcaseModules(\n    '
                 'filter:$moduleFilter,\n    groupBy:{\n      testcaseLibrary:{}\n    },\n    orderBy: {\n      '
                 'isDefault: ASC,\n      position: ASC\n    }\n  ){\n    uuid,\n    name,\n    path,\n    '
                 'createTime,\n    isDefault,\n    position,\n    key,\n    testcaseCaseCount,\n    '
                 'testcaseLibrary{\n      key,\n      uuid,\n      name,\n      testcaseCaseCount,\n    '
                 '},\n    parent{\n      uuid,\n      name,\n      path,\n      createTime,\n      isDefault,\n      '
                 'position,\n      key\n    }\n  }\n}',
        "variables": {
            "moduleFilter": {
                "testcaseLibrary_in": [
                    ''
                ]
            }
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'library_uuid': ''
            },
    }
    return p,


def update_library_module():
    """修改模块"""
    p = OnesParams()
    p.json = {
        "module": {
            "name": "test重命名模块",
            "uuid": ''
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'library_uuid': ''
            },
    }
    return p,


def delete_library_module():
    """删除模块"""
    p = OnesParams()
    p.json = {
        "module": ''
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'library_uuid': ''
            },
    }
    return p,


def modules_sort():
    """模块排序"""
    p = OnesParams()
    p.json = {
        "module_uuid": "",
        "previous_uuid": "",
        "previous_relation": ""
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'library_uuid': ''
            },
    }
    return p,


def add_case():
    """用例库中新增用例"""

    return generate_param({
        "item": {
            "name": '',
            "assign": ACCOUNT.user.owner_uuid,
            "priority": '',
            "type": '',
            "module_uuid": '',
            "condition": "前置条件1；\n前置条件2；\n前置条件3；",
            "library_uuid": '',
            "desc": "",
            "steps": [
                {
                    "id": 1,
                    "desc": "步骤1",
                    "result": "预期结果1"
                },
                {
                    "id": 2,
                    "desc": "步骤2",
                    "result": "预期结果2"
                }
            ],
            "related_wiki_page": [],
            "testcase_case_steps": [
                {
                    "id": 1,
                    "desc": "步骤1",
                    "result": "预期结果1"
                },
                {
                    "id": 2,
                    "desc": "步骤2",
                    "result": "预期结果2"
                }
            ],
            "item_type": "testcase_case",
            "testcase_library": '',
            "testcase_module": ''
        }
    })


def move_case():
    """移动用例库用例"""
    p = OnesParams()
    p.json = {
        "target_library_uuid": "RCdZuUf1",
        "target_module_uuid": "Aju2sAE6",
        "case_uuids": [
            "T72kGN7j"
        ]
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'library_uuid': ''
            },
    }
    return p,


def delete_case():
    """删除用例库用例"""
    p = OnesParams()
    p.json = {
        "case_uuids": ['PT4B9dUN', 'BPTfikwz']
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'library_uuid': '5iu8pBes'
            },
    }
    return p,


def export_case():
    """导出用例库用例"""
    p = OnesParams()
    p.json = {
        "library_uuid": '',
        "case_uuids": ''
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'library_uuid': ''
            },
    }
    return p,


def add_filed_config():
    """新增用例属性配置"""

    return generate_param({
        "item": {
            "name": f"test配置属性{mocks.num()}",
            "item_type": "testcase_field_config"
        }
    })


def pin_library():
    """置顶用例"""
    p = OnesParams()
    p.uri_args({
        'team_uuid': ACCOUNT.user.team_uuid,
        'library_uuid': ''})
    return p,


# ==========================================================================================


def add_attrib(field_type, pool='testcase'):
    """
    添加属性
    :param field_type  属性类型
    :param pool  testcase/testcase_plan

    """

    return generate_param({
        "item": {
            "field_type": field_type,
            "name": '',
            "context": {
                "type": "team"
            },
            "item_type": "field",
            "pool": pool
        }
    })


def add_case_attrib_config():
    """添加用例属性配置"""
    p = OnesParams()
    p.json = {
        "item": {
            "aliases": [
                ''
            ],
            "item_type": "field",
            "pool": "testcase",
            "context": {
                "type": "testcase_field_config",
                "field_config_uuid": ''
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


def del_field_config():
    """删除用例属性配置"""
    p = OnesParams()
    p.uri_args({
        'team_uuid': ACCOUNT.user.team_uuid,
        'config_uuid': ''})
    return p,


def query_filter_fields(config_uuid):
    """
    用例属性筛选
    :param config_uuid  用例属性配置-默认配置的uuid
    """

    return generate_param({
        "operationName": "FILTER_FIELDS_QUERY",
        "variables": {
            "fieldFilter": {
                "hidden_in": [
                    False
                ],
                "pool_in": [
                    "testcase"
                ],
                "context": {
                    "type_in": [
                        "testcase_field_config"
                    ],
                    "fieldConfigUUID_in": [config_uuid]
                }
            },
            "configFilter": {
                "uuid_in": [config_uuid]
            },
            "orderBy": {
                "builtIn": "DESC",
                "createTime": "ASC"
            }
        },
        "query": 'query FILTER_FIELDS_QUERY {\n  fields(filter: $fieldFilter, orderBy: $orderBy) {\n    aliases\n    '
                 'name\n    uuid\n    namePinyin\n    fieldType\n    key\n    defaultValue\n    createTime\n    '
                 'hidden\n    required\n    canUpdate\n    builtIn\n    allowEmpty\n    options {\n      uuid\n      '
                 'value\n      color\n      bgColor\n      __typename\n    }\n    __typename\n  }\n  '
                 'testcaseFieldConfigs(filter: $configFilter, orderBy: {namePinyin: ASC}) {\n    key\n    uuid\n    '
                 'name\n    namePinyin\n    __typename\n  }\n}\n'
    })


def query_global_fields():
    """用例属性全局字段"""
    p = OnesParams()
    p.json = {
        "operationName": "GLOBAL_FIELDS_QUERY",
        "variables": {},
        "query": 'query GLOBAL_FIELDS_QUERY {\n  fields(filter: {hidden_in: [false], pool_in: '
                 '[\"testcase\"], context: {type_in: [\"team\"]}}, orderBy: '
                 '{builtIn: DESC, createTime: ASC}) {\n    aliases\n    pool\n    name\n    uuid\n    '
                 'namePinyin\n    fieldType\n    key\n    defaultValue\n    createTime\n    hidden\n    '
                 'required\n    canUpdate\n    builtIn\n    allowEmpty\n    options {\n      uuid\n      '
                 'value\n      color\n      bgColor\n      __typename\n    }\n    '
                 'testcaseFieldConfigs(filter: $configFilter, orderBy: {namePinyin: ASC}) '
                 '{\n      key\n      uuid\n      name\n      namePinyin\n      __typename\n    }\n    '
                 '__typename\n  }\n}\n'
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p,


def case_rel_plan():
    """测试用例关联测试计划"""
    p = OnesParams()
    p.json = {
        "case_uuids": [
            ''
        ]
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'plan_uuid': ''
            },
    }
    return p,


def attachments_opt():
    """附件操作"""
    p = OnesParams()
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p


def case_attachment():
    """测试用例附件"""
    p = OnesParams()
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p,


def del_attachment(uuid):
    """删除附件文件"""
    p = OnesParams()
    p.json = [uuid]
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p,


# ==========================================================================================


def query_case_phase():
    """测试阶段"""
    p = OnesParams()
    p.json = {
        "operationName": "PLAN_SETTINGS_SYSTEM_FIELDS_QUERY",
        "variables": {
            "orderBy": {
                "builtIn": "DESC",
                "createTime": "ASC"
            },
            "filter": {
                "builtIn_equal": True,
                "pool_equal": "testcase_plan",
                "aliases_in": [
                    "plan_stage"
                ],
                "context": {
                    "type_equal": "team"
                },
                "hidden_equal": False
            }
        },
        "query": 'query PLAN_SETTINGS_SYSTEM_FIELDS_QUERY {\n  fields(filter: $filter, '
                 'orderBy: {builtIn: DESC, createTime: ASC}) {\n    aliases\n    pool\n    '
                 'name\n    uuid\n    namePinyin\n    fieldType\n    key\n    defaultValue\n    '
                 'createTime\n    hidden\n    required\n    canUpdate\n    builtIn\n    statuses '
                 '{\n      name\n      category\n      uuid\n      __typename\n    }\n    '
                 'allowEmpty\n    options {\n      uuid\n      value\n      color\n      bgColor\n      '
                 '__typename\n    }\n    __typename\n  }\n}\n'
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p,


def add_case_plan():
    """新增测试计划"""
    p = OnesParams()
    p.json = {
        "plan": {
            "name": f"test测试计划{mocks.num()}",
            "assigns": [
                ACCOUNT.user.owner_uuid
            ],
            "members": [
                {
                    "user_domain_type": "testcase_administrators",
                    "user_domain_param": ""
                },
                {
                    "user_domain_type": "testcase_plan_assign",
                    "user_domain_param": ""
                },
                {
                    "user_domain_type": "single_user",
                    "user_domain_param": ACCOUNT.user.owner_uuid
                }
            ],
            "related_project_uuid": None,
            "plan_stage": '',  # 需更新的参数--测试阶段
            "related_sprint_uuid": None,
            "related_issue_type_uuid": None,
            "check_points": []
        },
        "is_update_default_config": True
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p


def query_plan_list():
    """测试计划列表"""
    p = OnesParams()
    p.json = {
        "query": '\n    query QUERY_TESTPLAN_LIST {\n      buckets (\n        pagination: $pagination,\n        '
                 'groupBy: {\n          testcasePlans: {}\n        }\n      ) {\n        pageInfo {\n          '
                 'count\n          totalCount\n          startPos\n          startCursor\n          '
                 'endPos\n          endCursor\n          hasNextPage\n        }\n        '
                 'testcasePlans(\n          filter: $filter\n          orderBy:{\n            '
                 'status: {\n              category: ASC,\n            },\n            '
                 'namePinyin: ASC,\n          }\n          limit: 1000\n        ){\n          '
                 'key,\n          uuid,\n          owner{\n            uuid,\n            '
                 'name\n          },\n          planReports {\n            uuid\n            '
                 'name\n          },\n          name,\n          namePinyin,\n          '
                 'createTime,\n          status{\n            name\n            uuid\n            '
                 'category\n          }\n          members {\n            type,\n            '
                 'param\n          },\n          planStage {\n            value\n          }\n          '
                 'relatedProject{\n            key,\n            uuid,\n            namePinyin,\n          },'
                 '\n          relatedSprint{\n            key,\n            uuid,\n            namePinyin,'
                 '\n          },\n          relatedIssueType{\n            key,\n            uuid,\n            '
                 'name,\n            namePinyin\n          },\n          todoCaseCount,\n          '
                 'passedCaseCount,\n          blockedCaseCount,\n          skippedCaseCount,\n          '
                 'failedCaseCount,\n          assigns {\n            uuid,\n            name\n          '
                 '}\n          checkPoints\n          isSample\n          \n          \n        }\n      }\n    }\n',
        "variables": {
            "pagination": {
                "limit": 50,
                "after": ""
            },
            "filter": {}
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p


def query_plan_status():
    """测试计划状态"""
    p = OnesParams()
    p.json = {
        "query": '\n    query QUERY_STATUS {\n      fields(\n        filter: {\n            '
                 'pool_in: [\"testcase_plan\"]\n            aliases_in: [\"status\"]\n        }\n      )'
                 '{\n        name\n        aliases\n        statuses{\n          uuid\n          name\n          '
                 'category\n        }\n      }\n    }\n  ',
        "variables": {}
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p


def up_plan_status():
    """流转测试计划状态"""
    p = OnesParams()
    p.json = {
        "status": ''
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'plan_uuid': ''
            },
    }
    return p


def query_plan_detail():
    """测试计划详情"""
    p = OnesParams()
    p.json = {
        "query": 'query QUERY_TEST_PLAN {\n  \n  testcasePlans(\n    filter: $planFilter,\n  ){\n    key,'
                 '\n    uuid,\n    owner{\n      uuid,\n      name\n    },\n    name,\n    namePinyin,'
                 '\n    planStage {\n      value\n      uuid\n    },\n    createTime,\n    status {\n      '
                 'name\n      uuid\n      category\n    }\n    members {\n      type,\n      param\n    },'
                 '\n    relatedProject{\n      key,\n      uuid,\n      name,\n      namePinyin,\n    },'
                 '\n    relatedSprint{\n      key,\n      uuid,\n      name\n      namePinyin,\n    },\n    '
                 'relatedIssueType{\n      key,\n      uuid,\n      name,\n      namePinyin,\n      detailType\n'
                 '    },\n    assigns {\n      uuid,\n      name\n    }\n    todoCaseCount,\n    '
                 'passedCaseCount,\n    blockedCaseCount,\n    skippedCaseCount,\n    failedCaseCount,'
                 '\n    planReports {\n      uuid\n      name\n    },\n    checkPoints\n    '
                 'issueTracingConfig{\n      uuid\n      columnConfig\n      showIssueTrack\n    },\n    \n  }\n}',
        "variables": {
            "planFilter": {
                "uuid_in": [
                    ''
                ]
            }
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p


def add_plan_field():
    """增加测试计划属性"""
    p = OnesParams()
    p.json = {
        "query": "\n        mutation ADD_FIELD {\n          addField (field_type: $field_type name: "
                 "$name context: $context options: $options pool: $pool) {\n            key\n          }"
                 "\n        }\n      ",
        "variables": {
            "field_type": "",
            "name": "",
            "context": {
                "type": "team"
            },
            "pool": "testcase_plan"
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p


def update_plan_field():
    """更新测试计划属性"""
    return generate_param({
        "query": 'mutation UPDATE_FIELD {\n          updateField (key: $key name: $name options: '
                 '$options pool: $pool context: $context) {\n            key\n          }\n        }\n      ',
        "variables": {
            "key": "",  # 对应的属性key
            "name": "",
            "options": [
                {
                    "value": "test1",
                    "color": "#fff",
                    "bg_color": "#307fe2"
                },
                {
                    "value": "test2",
                    "color": "#fff",
                    "bg_color": "#00b388"
                }
            ],
            "pool": "testcase_plan",
            "context": {
                "type": "team"
            }
        }
    })


def query_plan_field():
    """查询测试计划配置属性"""
    p = OnesParams()
    p.json = {
        "operationName": "PLAN_SETTINGS_FIELDS_QUERY",
        "variables": {
            "orderBy": {
                "builtIn": "DESC",
                "createTime": "ASC"
            },
            "filter": {
                "builtIn_equal": False,
                "pool_equal": "testcase_plan",
                "context": {
                    "type_equal": "team"
                },
                "hidden_equal": False
            }
        },
        "query": 'query PLAN_SETTINGS_FIELDS_QUERY {\n  fields(filter: $filter, orderBy: '
                 '{builtIn: DESC, createTime: ASC}) {\n    aliases\n    pool\n    name\n    uuid\n    '
                 'namePinyin\n    fieldType\n    key\n    defaultValue\n    createTime\n    hidden\n    '
                 'required\n    canUpdate\n    builtIn\n    allowEmpty\n    options {\n      uuid\n      '
                 'value\n      color\n      bgColor\n      __typename\n    }\n    __typename\n  }\n}\n'
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p


def up_plan_info():
    """更新测试计划信息"""
    p = OnesParams()
    p.json = {
        "plan": {
            "uuid": '',
            "related_project_uuid": None,
            "related_sprint_uuid": None,
            "related_issue_type_uuid": None,
            "name": '',
            "assigns": [
                ACCOUNT.user.owner_uuid
            ],
            "members": [
                {
                    "user_domain_type": "testcase_administrators",
                    "user_domain_param": ""
                },
                {
                    "user_domain_type": "testcase_plan_assign",
                    "user_domain_param": ""
                }
            ],
            "issue_tracing_config": '',
            "field_values": [
            ]
        },
        "is_update_default_config": False
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'plan_uuid': ''
            },
    }
    return p


def del_plan_field():
    """删除测试计划属性"""
    p = OnesParams()
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'key': ''
            },
    }
    return p


def query_test_case():
    """测试计划中查询测试用例"""
    p = OnesParams()
    p.json = {
        "query": "{\n  testcaseCases(\n    filterGroup: $testCaseFilter,\n    orderBy: $orderByFilter\n    "
                 "limit: 1000\n  ){\n    uuid\n  }\n}",
        "variables": {
            "testCaseFilter": '',
            "orderByFilter": {
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
    return p


def plan_filter_query():
    """配置中心-测试计划属性查询"""

    return generate_param({
        "operationName": "PLAN_FIELDS_QUERY",
        "variables": {},
        "query": 'query PLAN_FIELDS_QUERY {\n  fields(filter: {hidden_equal: false, pool_equal:'
                 ' \"testcase_plan\", context: {type_equal: \"team\"}}, orderBy: {builtIn: DESC,'
                 ' createTime: ASC}) {\n    aliases\n    pool\n    name\n    uuid\n    namePinyin\n'
                 '    fieldType\n    key\n    defaultValue\n    createTime\n    hidden\n    required\n'
                 '    canUpdate\n    builtIn\n    allowEmpty\n    options {\n      uuid\n      value\n'
                 '      color\n      bgColor\n      __typename\n    }\n    __typename\n  }\n}\n'
    })


def rel_case_filter():
    """测试计划关联用例筛选"""
    p = OnesParams()
    p.json = {
        "query": "{\n    buckets (\n      pagination: $pagination,\n      groupBy: {\n        testcaseCases:"
                 "{}\n      }\n    ){\n      \n  pageInfo {\n    count\n    totalCount\n    startPos\n    "
                 "startCursor\n    endPos\n    endCursor\n    hasNextPage\n  }\n\n      \n  testcaseCases(\n    "
                 "filterGroup: $testCaseFilter,\n    orderBy: $orderByFilter,\n  ){\n    uuid\n    name\n    "
                 "key\n  }\n\n    }\n  }",
        "variables": {
            "testCaseFilter": '',
            "orderByFilter": {
                "namePinyin": "ASC"
            },
            "pagination": {
                "limit": 50,
                "after": ""
            }
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p


def plan_global_field():
    """测试计划全局筛选属性"""
    p = OnesParams()
    p.json = {
        "query": 'query GLOBAL_FIELDS_QUERY{\n  fields(\n  filter:{\n    hidden_in:[false],\n    '
                 'pool_in:[\"testcase\"],\n    context:{\n      type_in:[\"team\"]\n    },\n  },\n  '
                 'orderBy:{\n    builtIn:DESC,\n    createTime: ASC\n  } \n){\n  aliases,\n  pool,\n  name,'
                 '\n  uuid,\n  namePinyin,\n  fieldType,\n  key,\n  defaultValue,\n  createTime,\n  hidden,\n  '
                 'required,\n  canUpdate,\n  builtIn,\n  allowEmpty,\n  options{\n    uuid,\n    value,\n    '
                 'color,\n    bgColor\n  },\n  testcaseFieldConfigs(\n  filter:$configFilter,\n  orderBy:{\n    '
                 'namePinyin :ASC\n  }\n){\n  key,\n  uuid,\n  name,\n  namePinyin\n}\n}\n}',
        "variables": {}
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p


def query_case_detail():
    """查询测试用例详情"""

    return generate_param({
        "query": 'query QUERY_TESTCASES_DETAIL(\n    $testCaseFilter:Filter,\n    $stepFilter:Filter\n    )'
                 '{\n    testcaseCases(\n    filter:$testCaseFilter\n  ){\n    uuid\n    name\n    key\n    '
                 'condition\n    desc\n    assign {\n      uuid\n      name\n    }\n    createTime\n    '
                 'testcaseLibrary{\n      uuid,\n    }\n    testcaseModule{\n      uuid,\n    }\n    number\n    '
                 'path\n    priority{\n      uuid,\n      value,\n    },\n    type{\n      uuid,\n      value,\n'
                 '    }\n    relatedWikiPage\n    \n  }\n  testcaseCaseSteps(\n  filter:$stepFilter,\n  orderBy:'
                 '{\n    index:ASC\n  }\n){\n  key,\n  uuid,\n  testcaseCase{\n    uuid,\n  },\n  desc,\n  result,'
                 '\n  index\n}\n  }',
        "variables": {
            "testCaseFilter": {
                "uuid_in": [
                    ''
                ]
            },
            "stepFilter": {
                "testcaseCase_in": [
                    ''
                ]
            }
        }
    })


def update_case_pri():
    """更新测试用例优先级"""
    p = OnesParams()
    p.json = {
        "query": "\n        mutation UPDATE_TEST_CASE {\n          updateTestcaseCase (key: $key priority: "
                 "$priority item_type: $item_type) {\n            key\n          }\n        }\n      ",
        "variables": {
            "key": '',
            "item_type": "testcase_case"
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p


def update_case_title():
    """更新测试用例标题"""
    p = OnesParams()
    p.json = {
        "query": "\n        mutation UPDATE_TEST_CASE {\n          updateTestcaseCase (key: $key name: "
                 "$name item_type: $item_type) {\n            key\n          }\n        }\n      ",
        "variables": {
            "key": '',
            "name": "update标题",
            "item_type": "testcase_case"
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p


def update_case_assign():
    """更新测试用例维护人"""
    p = OnesParams()
    p.json = {
        "query": "\n        mutation UPDATE_TEST_CASE {\n          updateTestcaseCase (key: $key assign: "
                 "$assign item_type: $item_type) {\n            key\n          }\n        }\n      ",
        "variables": {
            "key": '',
            "assign": ACCOUNT.user.owner_uuid,
            "item_type": "testcase_case"
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p


def update_plan_case():
    """更新测试计划用例"""
    p = OnesParams()
    p.json = {
        "cases": [
            {
                "uuid": '',
                "executor": ACCOUNT.user.owner_uuid
            }
        ],
        "is_batch": True
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'plan_uuid': ''
            },
    }
    return p


def export_plan_case():
    """导出测试计划用例"""
    p = OnesParams()
    p.json = {
        "plan_uuid": '',
        "case_uuids": ''
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
                'plan_uuid': ''
            },
    }
    return p


def search_plan_case():
    """搜索测试计划详情用例"""
    p = OnesParams()
    p.json = {
        "query": 'query TESTCASE_PLAN_CASE_LIST_UUIDS($testCaseFilter: Filter, $planFilter: Filter, '
                 '$moduleFilter: Filter, $orderByFilter: Filter) {\n  buckets(groupBy: {testcasePlanCases: {}},'
                 ' pagination: {limit: 10000, after: \"\", preciseCount: false}) {\n    key\n    '
                 'testcasePlanCases(filterGroup: $testCaseFilter, orderBy: $orderByFilter, search: $search) {\n'
                 '      testcaseCase {\n        uuid\n      }\n    }\n    key\n    pageInfo {\n      count\n      '
                 'preciseCount\n      totalCount\n      startPos\n      startCursor\n      endPos\n      '
                 'endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n',
        "variables": {
            "search": {
                "keyword": ''
            },
            "testCaseFilter": [
                {
                    "testcasePlan_in": [
                        ''
                    ],
                    "testcaseCase": {}
                }
            ],
            "planFilter": {
                "uuid_in": []
            },
            "orderByFilter": {
                "testcaseCase": {
                    "namePinyin": "ASC"
                }
            }
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p


def plan_case_mod():
    """测试计划用例模块"""

    return generate_param({
        "operationName": None,
        "variables": {
            "planFilter": {
                "uuid_equal": ''
            }
        },
        "query": '{\n  testcasePlans(filter: $planFilter) {\n    testcaseModules {\n      uuid\n      name\n      '
                 'position\n      key\n      isDefault\n      testcaseLibrary {\n        key\n        uuid\n        '
                 'name\n        __typename\n      }\n      parent {\n        uuid\n        name\n        '
                 'position\n        key\n        __typename\n      }\n      __typename\n    }\n    '
                 '__typename\n  }\n}\n'
    })


def plan_case_list():
    """测试计划用例列表"""
    p = OnesParams()
    p.json = {
        "query": 'query PAGED_TESTCASE_PLAN_CASE_LIST($testCaseFilter: Filter, $planFilter: Filter, $moduleFilter:'
                 ' Filter, $orderByFilter: Filter) {\n  buckets(groupBy: {testcasePlanCases: {}}, pagination:'
                 ' {limit: 50, after: \"\", preciseCount: false}) {\n    key\n    testcasePlanCases(filterGroup:'
                 ' $testCaseFilter, orderBy: $orderByFilter, limit: 10000) {\n      inCaseUUID\n      '
                 'testcaseCase {\n        uuid\n        name\n        namePinyin\n        key\n        '
                 'condition\n        createTime\n        desc\n        number\n        path\n        assign '
                 '{\n          uuid\n          name\n        }\n        testcaseLibrary {\n          uuid\n'
                 '          testcaseFieldConfig {\n            uuid\n            name\n          }\n        }\n'
                 '        testcaseModule {\n          uuid\n          path\n        }\n        priority {\n'
                 '          uuid\n        }\n        type {\n          uuid\n        }\n        relatedWikiPage\n'
                 '      }\n      key\n      note\n      result\n      executor {\n        uuid\n        name\n'
                 '      }\n    }\n    key\n    pageInfo {\n      count\n      preciseCount\n      totalCount\n'
                 '      startPos\n      startCursor\n      endPos\n      endCursor\n      hasNextPage\n'
                 '      unstable\n    }\n  }\n  testcasePlans(filter: $planFilter) {\n    key\n    uuid\n'
                 '    owner {\n      uuid\n      name\n    }\n    name\n    namePinyin\n    createTime\n'
                 '    status {\n      name\n      uuid\n      category\n    }\n    members {\n      type\n'
                 '      param\n    }\n    planStage {\n      value\n    }\n    relatedProject {\n      key\n'
                 '      uuid\n      name\n      namePinyin\n    }\n    relatedSprint {\n      key\n      uuid\n'
                 '      name\n      namePinyin\n    }\n    relatedIssueType {\n      key\n      uuid\n      name\n'
                 '      namePinyin\n      detailType\n    }\n    assigns {\n      uuid\n      name\n    }\n'
                 '    todoCaseCount\n    passedCaseCount\n    blockedCaseCount\n    skippedCaseCount\n'
                 '    failedCaseCount\n    planReports {\n      uuid\n      name\n    }\n    checkPoints\n  }\n'
                 '  fields(filter: {hidden_in: [false], pool_in: [\"testcase\"], context: {type_in: [\"team\"]}},'
                 ' orderBy: {builtIn: DESC, createTime: ASC}) {\n    aliases\n    pool\n    name\n    uuid\n'
                 '    namePinyin\n    fieldType\n    key\n    defaultValue\n    createTime\n    hidden\n'
                 '    required\n    canUpdate\n    builtIn\n    allowEmpty\n    options {\n      uuid\n'
                 '      value\n      color\n      bgColor\n    }\n    testcaseFieldConfigs(filter: $configFilter,'
                 ' orderBy: {namePinyin: ASC}) {\n      key\n      uuid\n      name\n      namePinyin\n    }\n'
                 '  }\n}\n',
        "variables": {
            "testCaseFilter": [
                {
                    "testcasePlan_in": [],
                    "testcaseCase": {
                        "path_match": ''
                    }
                }
            ],
            "planFilter": {
                "uuid_in": []
            },
            "orderByFilter": {
                "testcaseCase": {
                    "namePinyin": "ASC"
                }
            }
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p


def query_plan_case_detail():
    p = OnesParams()
    p.json = {
        "query": 'query QUERY_PLAN_TESTCASE_DETAIL($testCaseFilter:Filter,$libraryStepFilter:Filter,'
                 '$planStepFilter:Filter,$lastCaseFilter:Filter){\n    testcasePlanCases(filter:$testCaseFilter)'
                 '{\n      inCaseUUID,\n      testcaseCase{\n        uuid, name, key, condition, createTime, desc,'
                 ' number, path,\n        assign{\n          uuid\n          name\n        },\n        '
                 'testcaseLibrary{\n          uuid,\n        },\n        testcaseModule{\n          uuid,'
                 '\n        },\n        priority{\n          uuid,\n          value,\n        },\n        '
                 'type{\n          uuid,\n          value,\n        }\n        pathModules{\n          '
                 'name\n        }\n        relatedWikiPage}\n      relatedTasks{\n    '
                 'uuid,\n    name,\n    namePinyin,\n    number,\n    status{\n      name\n      namePinyin\n    },'
                 '\n    issueType{\n      icon,\n      name,\n      uuid\n    },\n    subIssueType{\n      icon,'
                 '\n      name,\n      uuid\n    }\n    project{\n      uuid,\n      name,\n    },\n    sprint{\n'
                 '      uuid,\n      name,\n    }\n    statusCategory\n}\n      key,\nnote,\nresult,\nexecutor{\n'
                 '  uuid,\n  name,\n}\n      testcasePlan{\n  checkPoints\n  owner{\n    uuid,\n    name\n  },\n'
                 '  name, key, uuid,\n  status {\n    name\n    uuid\n    category\n  }\n  planStage {\n    value\n'
                 '  }\n  relatedProject{\n    key,\n    uuid,\n    name,\n  },\n  relatedSprint{\n    key,\n    uuid,'
                 '\n    name\n  },\n  relatedIssueType{\n    key,\n    uuid,\n    name,\n    namePinyin\n  },\n}\n'
                 '    }\n    testcaseCaseSteps(\n  filter:$libraryStepFilter,\n  orderBy:{\n    index:ASC\n  }\n){\n'
                 '  key,\n  uuid,\n  testcaseCase{\n    uuid,\n  },\n  desc,\n  result,\n  index\n}\n'
                 '    testcasePlanCaseSteps(filter:$planStepFilter){\n  key, stepResult, actualResult,\n'
                 '  testcasePlan{\n    key,\n    uuid,\n  },\n  testcaseCase{\n    key,\n    uuid,\n  },\n'
                 '  testcaseCaseStep{\n    key,\n    uuid,\n    desc,\n    result\n  }\n}\n'
                 '    testcaseCases(filter:$lastCaseFilter){\n  key,\n  uuid,\n  name,\n}\n  }',
        "variables": {
            "testCaseFilter": {
                "testcaseCase_in": [
                    ''
                ],
                "testcasePlan_in": [
                    ''
                ]
            },
            "libraryStepFilter": {
                "testcaseCase_in": [
                    ''
                ]
            },
            "planStepFilter": {
                "testcaseCase_in": [
                    ''
                ],
                "testcasePlan_in": [
                    ''
                ]
            },
            "lastCaseFilter": {
                "uuid_in": [
                    None
                ]
            }
        }
    }
    p.extra = {
        'uri_args':
            {
                'team_uuid': ACCOUNT.user.team_uuid,
            },
    }
    return p


# ==========================================================================================


def add_test_report():
    """新建测试报告"""
    return generate_param({
        "query": '\n        mutation ADD_TEST_REPORT {\n          addTestcaseReport '
                 '(name: $name description: $description testcase_plans: $testcase_plans) '
                 '{\n            key\n          }\n        }\n      ',
        "variables": {
            "name": '',
            "description": "{\"components\":[\"1\",\"2\",\"3\",\"4\",\"5\"],\"contentMap\":"
                           "{\"richTextComponentTitleSet\":{},\"richTextComponentContentSet\":{}}}",
            "testcase_plans": [
                ''
            ]
        }
    })


def del_test_report():
    """删除测试报告"""
    return generate_param({
        "query": '\n        mutation DELETE_TEST_REPORT {\n          deleteTestcaseReport (key: $key) '
                 '{\n            key\n          }\n        }\n      ',
        "variables": {
            "key": ''
        }
    })


def export_report():
    """导出测试报告"""
    return generate_param({
        'html': rh.html
    })


def up_report():
    """变更测试报告"""
    return generate_param({
        "uuid": '',
        'title': 'test修改测试报告',
        "start_time": 0,
        "end_time": 0,
        "summary": '{\"components\":[\"1\",\"2\",\"3\",\"4\",\"5\"],\"contentMap\":{\"richTextComponentTitleSet\":{},'
                   '\"richTextComponentContentSet\":{}}}'
    })


def up_del_module():
    """删除测试报告组件"""
    data = ['[\"1\",\"2\",\"3\",\"4\"]', '[\"1\",\"2\",\"3\",\"5\"]', '[\"1\",\"2\",\"4\",\"5\"]',
            '[\"1\",\"3\",\"4\",\"5\"]', '[\"2\",\"3\",\"4\",\"5\"]']  # 删除关联缺陷列表组件\测试用例所属模块分布\缺陷优先级分布\测试用例结果分布\概览
    report = []

    for i in data:
        p = generate_param({
            "uuid": '',
            'title': '删除测试报告组件',
            "start_time": 0,
            "end_time": 0,
            "summary": '{"components":%s,\"contentMap\":{\"richTextComponentTitleSet\":{},'
                       '\"richTextComponentContentSet\":{}}}' % i
        })

        report.append(p[0])

    return report


def report_list():
    """测试报告列表"""
    return generate_param({
        "query": 'query QUERY_TESTPLAN_LIST {\n  buckets(groupBy: {testcaseReports: {}}, pagination: '
                 '{limit: 50, after: \"\", preciseCount: false}) {\n    pageInfo {\n      count\n      '
                 'totalCount\n      startPos\n      startCursor\n      endPos\n      endCursor\n      '
                 'hasNextPage\n    }\n    testcaseReports(filter: $filter, orderBy: $orderBy, limit: 1000) '
                 '{\n      key\n      uuid\n      name\n      createTime\n      owner {\n        name\n        '
                 'uuid\n        avatar\n      }\n      testcasePlans {\n        name\n        uuid\n        '
                 'canBrowse\n        relatedProject {\n          uuid\n          name\n        }\n        '
                 'relatedSprint {\n          uuid\n          name\n        }\n      }\n    }\n    key\n    '
                 'pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n      '
                 'startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n',
        "variables": {
            "orderBy": {}
        }
    })


# ==========================================================================================

def overview_lib_list():
    """概览-用例库列表"""

    return generate_param({
        "query": '\n    query QUERY_LIBRARY_LIST {\n      buckets (\n        pagination: $pagination,'
                 '\n        groupBy: {\n          testcaseLibraries: {}\n        }\n      ) {\n        '
                 'pageInfo {\n          count\n          totalCount\n          startPos\n          '
                 'startCursor\n          endPos\n          endCursor\n          hasNextPage\n        '
                 '}\n        testcaseLibraries(\n          orderBy: {\n            isPin:DESC\n'
                 '            namePinyin:ASC\n          }\n          limit: 1000\n        ){\n'
                 '          uuid,\n          name,\n          isPin,\n          isSample,\n'
                 '          testcaseCaseCount,\n          testcaseFieldConfig{\n            key,\n'
                 '            uuid,\n            name\n          }\n        }\n      }\n    }\n  ',
        "variables": {
            "endCursor": "",
            "pagination": {
                "limit": 50
            }
        }
    })


# ==========================================================================================

def plan_report_temple():
    """测试计划报告模块"""

    return generate_param({
        "name": f"报告模板-{mocks.two_num()}",
        "content": "{\"components\":[\"1\",\"2\",\"3\",\"4\",\"5\"],\"contentMap\":{\"richTextComponentTitleSet\":{},\"richTextComponentContentSet\":{}}}"
    })


def case_field_update():
    """更新测试用例属性"""
    p = {}

    return generate_param(p)


def field_delete():
    """删除属性字段"""

    return generate_param()


def used_count():
    """测试用例属性正在被使用次数"""
    return generate_param({
        "context_type": "testcase_case",
        "field_alias": "priority",  # 属性uuid
        "option_uuid": ""  # 选项值uuid
    })


def field_copy():
    """复制属性配置"""

    return generate_param({
        "name": f"copy属性{mocks.num()}",
        "source_field_config": ""  # 被复制的uuid
    })


def query_libray_modules():
    """查询关联用例库"""
    return generate_param({
        "operationName": "SIMPLE_QUERY_LIBRARY_MODULES",
        "variables": {
            "moduleFilter": None
        },
        "query": "query SIMPLE_QUERY_LIBRARY_MODULES($moduleFilter: Filter) {\n  testcaseLibraries(orderBy: {namePinyin: ASC}) {\n    key\n    uuid\n    name\n    __typename\n  }\n  testcaseModules(filter: $moduleFilter, groupBy: {testcaseLibrary: {}}, orderBy: {isDefault: ASC, position: ASC}) {\n    uuid\n    name\n    path\n    createTime\n    isDefault\n    position\n    key\n    testcaseLibrary {\n      key\n      uuid\n      name\n      __typename\n    }\n    parent {\n      uuid\n      name\n      path\n      createTime\n      isDefault\n      position\n      key\n      __typename\n    }\n    __typename\n  }\n}\n"
    })


def query_testplan_list():
    """查询测试计划列表"""
    return generate_param({
        "operationName": "QUERY_TESTPLAN_LIST",
        "variables": {},
        "query": "query QUERY_TESTPLAN_LIST {\n  testcasePlans(filter: $planFilter, orderBy: {namePinyin: ASC}) {\n    key\n    uuid\n    owner {\n      uuid\n      name\n      __typename\n    }\n    planReports {\n      uuid\n      name\n      __typename\n    }\n    name\n    namePinyin\n    createTime\n    status {\n      name\n      uuid\n      category\n      __typename\n    }\n    members {\n      type\n      param\n      __typename\n    }\n    planStage {\n      value\n      __typename\n    }\n    relatedProject {\n      key\n      uuid\n      namePinyin\n      __typename\n    }\n    relatedSprint {\n      key\n      uuid\n      namePinyin\n      __typename\n    }\n    relatedIssueType {\n      key\n      uuid\n      name\n      namePinyin\n      __typename\n    }\n    todoCaseCount\n    passedCaseCount\n    blockedCaseCount\n    skippedCaseCount\n    failedCaseCount\n    assigns {\n      uuid\n      name\n      __typename\n    }\n    checkPoints\n    isSample\n    issueTracingConfig {\n      uuid\n      columnConfig\n      showIssueTrack\n      __typename\n    }\n    __typename\n  }\n}\n"
    })


def testcase_permission():
    """
    测试管理-权限配置-新增权限
    :return:
    """
    return generate_param({
        "permission_rule": {
            "context_type": "testcase",
            "context_param": None,
            "permission": "",
            "user_domain_type": "",
            "user_domain_param": ""
        }
    })


def add_testcase_default_member_permission():
    """
    配置中心-测试管理配置-关联项目配置-默认成员权限add
    :return:
    """
    return generate_param({
        "user_domain_type": "single_user",
        "user_domain_param": ""
    }, is_project=True)


def del_testcase_default_member_permission():
    """
    配置中心-测试管理配置-关联项目配置-默认成员权限delete
    :return:
    """
    return generate_param({
        "user_domain_type": "single_user",
        "user_domain_param": "",
        "type": "single_user",
        "user": {},
        "members": "",
        "tag": "成员",
        "name": "mb_2crqssnx",
        "subText": "mb_2crqssnx@ones.ai"
    }, is_project=True)


def update_testcase_related_project():
    """
    配置中心-测试管理配置-关联项目配置-「需求跟踪」组件 启用/不启用
    :return:
    """
    return generate_param({
        "issue_type_uuid": "",
        "show_issue_track": False
    }, is_project=True)


def testcase_result_field_set():
    """
    配置中心-测试管理配置-关联项目配置-执行结果属性配置
    :return:
    """
    check_points = []
    p = {
        "check_points": check_points,
        "issue_type_uuid": ""
    }

    result = ['passed', 'failed', 'blocked', 'skipped']
    check_point_type = ['note', 'file']
    for r in check_point_type:
        for f in result:
            check_points.append({"case_result": f, "check_point": r, "is_must": False})

    return generate_param(p, is_project=True)
