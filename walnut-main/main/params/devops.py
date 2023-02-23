#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：devops.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/23 
@Desc    ：
"""
from falcons.helper import mocks
from falcons.ops import generate_param

from main.params.const import ACCOUNT


def ci_list():
    """
    获取流水线列表
    搜索pipeline

    :return:
    """

    return generate_param({
        "query": 'query DEVOPSPIPELINES($filter:Filter, $orderBy:OrderBy){\n        '
                 'devopsPipelines(filter:$filter,orderBy:$orderBy){\n          isPin\n          '
                 'uuid\n          name\n          type\n          path\n          namePinyin\n          '
                 'children{\n            uuid\n            name\n          }\n        }\n    }',
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
    })


def component_stamp():
    """
    获取项目组件配置信息

    :return:
    """

    return generate_param({
        'component': mocks.now_timestamp()
    }, is_project=True)


def component_add():
    """
    添加项目组件信息

    :return:
    """

    return generate_param({
        'components': [
            {
                "uuid": mocks.ones_uuid(),
                "template_uuid": "com00030",
                "project_uuid": ACCOUNT.project_uuid,
                "parent_uuid": "",
                "name": "流水线",
                "name_pinyin": "liu2shui3xian4",
                "desc": "“流水线”组件展示了当前项目关联的流水线信息，以及流水线的最近情况。",
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


def component_update():
    """
    更新项目组件信息-关联流水线信息

    :return:
    """

    return generate_param({
        "uuid": '',  # assign in case
        "template_uuid": "com00030",
        "project_uuid": ACCOUNT.project_uuid,
        "parent_uuid": "",
        "name": "流水线",
        "name_pinyin": "liu2shui3xian4",
        "desc": "“流水线”组件展示了当前项目关联的流水线信息，以及流水线的最近情况。",
        "objects": [],
        "permissions": []
        # "permissions": [
        #     {
        #         "permission": "view_component",
        #         "user_domains": [
        #             {
        #                 "user_domain_type": "everyone",
        #                 "user_domain_param": ""
        #             },
        #             {
        #                 "user_domain_type": "project_administrators",
        #                 "user_domain_param": ""
        #             }
        #         ]
        #     }
        # ],
        # "type": 2,
        # "views": [],
        # "update": 1
    },
        is_project=True, **{'component_uuid': ''}
    )


def devops_add(ok=True):
    """
    添加 devops

    :return:
    """

    return generate_param({
        "item": {
            "item_type": "devops_ci_sync",
            "ci_server_url": "http://47.112.50.166:8081/",  # 这里只做测试关联用途
            "ci_server_type": "jenkins",
            "certification_type": "token",
            "account": "admin" if ok else 'zeno1',
            "certification": "8ofbKVSO7eAJ"
        }
    })


def devops_list():
    """
    devops list

    :return:
    """

    return generate_param({
        "query": 'query devopsCiSyncs($filter:Filter,$orderBy:OrderBy){\n  devopsCiSyncs(filter:$filter,orderBy:'
                 '$orderBy){\n        uuid\n        ciServerUrl\n        ciServerType\n        '
                 'certificationType\n        account\n        certification\n        createTime\n        '
                 'syncPipelineCount\n        pipelineCount\n        syncStatus\n    }}',
        "variables": {
            "filter": {},
            "orderBy": {}
        }
    })


def pipeline_list():
    """
    查询pipline 列表

    :return:
    """

    return generate_param({
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
    })


def pipeline_run_history(fi=False):
    """

    查询 pipline 构建历史
    :param: fi
    :return:
    """

    return generate_param({
        "query": 'query DEVOPSPIPELINERUNS($filter:Filter, $orderBy:OrderBy){\n        '
                 'devopsPipelineRuns(filter:$filter,orderBy:$orderBy){\n          '
                 'uuid\n          number\n          duration\n          startTime\n          '
                 'triggerType\n          triggerBy\n          status\n          repo\n          '
                 'branch\n          pipelineUUID\n        }\n    }',
        "variables": {
            "filter": {
                "pipelineUUID_in": [],  # assign in case
            },
            "orderBy": {
                "number": "DESC"
            }
        }
    })


def pipeline_pin():
    """
    pip or unpin
    :return:
    """
    return generate_param({}, **{'pipeline_uuid': ''})


def devops_delete():
    return generate_param({}, **{'pipeline_uuid': ''})


def devops_search():
    """"""
    ll = ci_list()
    for m in ll:
        m.json['variables']['filter'] |= {
            'name_match': '测试流水线'
        }

    return ll


def permission_add():
    """"""
    return generate_param({
        "permission_rule": {
            "context_type": "pipeline",
            "context_param": {
                "pipeline_uuid": "",  # assign in case
            },
            "permission": "browse_pipeline",
            "user_domain_type": "everyone",
            "user_domain_param": ""
        }
    })


def user_permission_add(perm_type):
    """
    项目添加单个成员权限
    perm_type: browse_project, manage_project, 等等
    :return:
    """
    return generate_param({
        "permission_rule": {
            "context_type": "project",
            "context_param": {
                "project_uuid": ACCOUNT.project_uuid
            },
            "permission": perm_type,
            "user_domain_type": "single_user",
            "user_domain_param": ""  # assign in case, user uuid
        }
    })


def permission_delete():
    """
    项目权限删除
    :return:
    """
    return generate_param()


def jenkins_add():
    """新建关联jenkins"""
    return generate_param({
        "item": {
            "item_type": "devops_ci_sync",
            "ci_server_url": "http://119.23.154.208:8080",
            "ci_server_type": "jenkins",
            "certification_type": "token",
            "account": "ones",
            "certification": "Ones1234"
        }
    })


def eval_permission(perm_type):
    """
    查看成员是否有项目对应权限

    perm_type: browse_project, manage_project, 等等
    """
    return generate_param({
        "rules": [
            {
                "context_type": "project",
                "context_param": {
                    "project_uuid": ACCOUNT.project_uuid
                },
                "permission": perm_type
            }
        ]
    })
