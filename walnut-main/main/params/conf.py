#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：conf.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/4 
@Desc    ：项目配置/全局配置测试数据
"""
from falcons.helper import mocks
from falcons.ops import generate_param

from main.params.const import ACCOUNT


def add_options(op_type='option'):
    """
    新建项目属性
    :param op_type: option / multi_option
    :return:
    """
    return generate_param({
        'item': {
            'field_type': 'option',
            'name': op_type.upper() + mocks.random_string(4),
            'options': [
                {
                    'value': 'abc',
                    'background_color': '#307fe2',
                    'color': '#fff'
                },
                {
                    'value': 'def',
                    'background_color': '#00b388',
                    'color': '#fff'
                }
            ],
            'item_type': 'field',
            'pool': 'project',
            'context': {
                'type': 'team'
            }
        }
    })


def add_issue_type_field():
    """新建全局工作项属性"""
    return generate_param({
        "field": {
            "name": mocks.ones_uuid(),
            "type": 8,  # 具体类型，用例中赋值
            "renderer": 1,
            "filter_option": 0,
            "search_option": 1
        }
    })


def update_issue_field(field_uuid):
    """修改全局工作项属性配置"""
    return generate_param({
        "field_config": {
            "field_uuid": field_uuid,
            "required": False
        }
    })


def add_field(f_type: str):
    """
    生成测试数据

    类型	类型枚举值	值类型	说明
    option	1	string	选项，值是当前选中的选项 uuid
    text	2	string	文本
    integer	3	int	整数，值 = 实际数值 x 100000
    float	4	int	浮点数，值 = 向下取整(实际数值 x 100000)，小数点后有效位数 5 位
    date	5	int	日期，utc 时间戳，以秒为单位
    time	6	int	时间，utc 时间戳，以秒为单位
    milestone	7	string	里程碑，值是里程碑 uuid
    user	8	string	团队内成员，值是用户 uuid
    project	9	string	项目，值是项目 uuid
    task	10	string	工作项，值是工作项的uuid
    issue_type	11	string	issue_type，值issue_type的uuid
    task_status	12	string	工作项状态，值是工作项状态的uuid
    user_list	13	array	用户列表
    number	14	int	工作项编号
    multi_line_text	15	string	多行文本
    multi_option	16	array	多选，值 = 选中的选项uuid数组
    :param f_type:
    :return:
    """
    return generate_param({
        'item': {
            'field_type': f_type,
            'name': f'{f_type}-{mocks.ones_uuid()}'[-16:],  # 限制名字16个字符内
            'item_type': 'field',
            'pool': 'project',
            'context': {
                'type': 'team'
            }
        }
    })


def add_member():
    """添加成员"""
    return generate_param({})


def member_list():
    """成员列表"""
    return generate_param({}, is_project=True)


def update_proj_members(members: list):
    """项目内添加成员"""
    return generate_param({
        "members": members
    }, is_project=True)


def delete_project():
    return generate_param({})


def delete_field():
    return generate_param({}, is_project=True, **{'item_key': ''})


def add_field_to_project(proj_uuid=ACCOUNT.project_uuid):
    return generate_param({
        'item': {
            'aliases': [],  # 属性 的 aliases 值
            'item_type': 'field',
            'pool': 'project',
            'context': {
                'type': 'project',
                'project_uuid': proj_uuid,
            }
        }
    })


def proj_field_update():
    """项目属性默认值更新"""

    return generate_param({
        "field_config": {
            "default_value": "5BAjX4qP"  # 用例中赋值
        }
    }, is_project=True)


def update_prj_status():
    """"""
    return generate_param({
        'item': {
            'statuses': []  # 自行传入status数据
        }
    })


def get_sys_status():
    """获取全局配置-项目状态配置信息"""
    return generate_param({
        'query': {
            'must': [
                {
                    'equal': {
                        'item_type': 'field'
                    }
                },
                {
                    'in': {
                        'field_type': [
                            'status'
                        ]
                    }
                },
                {
                    'in': {
                        'pool': [
                            'project'
                        ]
                    }
                },
                {
                    'in': {
                        'context.type': [
                            'team'
                        ]
                    }
                }
            ]
        },
        'view': [
            '[default]',
            'used_in'
        ]
    })


def role_add():
    """
    添加角色
    :return:
    """
    return generate_param({
        'role': {
            'name': mocks.random_string(10)
        }

    })


def update_role():
    """更新角色名"""
    return generate_param({
        'role': {
            'uuid': '',  # 角色uuid
            'name': 'Now role one'
        }
    })


def project_roles_add():
    """添加角色到项目"""
    return generate_param({
        'role_uuids': [],  # 角色uuid
    }, is_project=True)


def project_roles_delete():
    """移除角色到项目"""
    return generate_param({}, is_project=True, **{'role_uuid': ''})


def role_configs():
    """"""

    return generate_param({
        'role': 0,
        'role_config': 0
    })


def role_delete():
    """"""
    return generate_param({})


# -*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-

def view_product():
    """查看产品配置"""
    return generate_param({
        'query': {
            'must': [
                {
                    'equal': {
                        'item_type': 'field'
                    }
                },
                {
                    'in': {
                        'pool': [
                            'product'
                        ]
                    }
                },
                {
                    'in': {
                        'context.type': [
                            'team'
                        ]
                    }
                }
            ]
        },
        'view': [
            '[default]'
        ]
    })


def add_product(p_type):
    """添加产品属性"""
    return generate_param({
        'item': {
            'field_type': p_type,
            'name': f'{p_type}{mocks.ones_uuid()}'.upper()[:16],
            'context': {
                'type': 'team'
            },
            'item_type': 'field',
            'pool': 'product'
        }
    })


def update_product():
    """更新产品属性名称"""
    return generate_param({
        'item': {
            'name': f'Prd{mocks.ones_uuid()}'.upper()
        }
    })


def delete_product_field():
    """删除产品属性配置"""
    return generate_param({})


def layout_list():
    """视图配置信息"""
    return generate_param({
        'query': '{\n    issueTypeLayouts(filter:$filter,orderBy:$orderBy) {\n      \n  key\n  '
                 'uuid\n  syncFormFromView\n  name\n  builtIn\n  haveDraft\n  issueType {\n    uuid\n    name\n  }'
                 '\n  issueTypeTemplate {\n    name\n    uuid\n  }\n  lastScopes {\n    uuid\n    name\n    scope\n    '
                 'scopeName\n    scopeType\n    issueType {\n      uuid\n      name\n    }\n  }\n\n    }\n  }',
        'variables': {
            'filter': {
                'issueTypeScopeUUID_equal': None
            },
            'orderBy': {
                'namePinyin': 'ASC'
            }
        }
    })


def layout_add():
    """新建视图工作项"""
    return generate_param({
        'name': f'Layout{mocks.ones_uuid()}',
        'issue_type_uuid': ''  # 工作项类型UUID
    })


def issue_type_stamp():
    """获取工作项类型配置"""
    return generate_param({
        'issue_type': 0,
        'issue_type_config': 0
    })


def layout_delete():
    """删除视图"""
    return generate_param({})


def switch_layout():
    """视图切换"""
    return generate_param({
        "layout_uuid": ""
    })


def layout_draft_get():
    """获取视图详情配置草稿"""
    return generate_param({})


def layout_draft_set():
    """保存视图详情配置草稿"""
    return generate_param({'data': {}})


def field_stamp():
    """获取属性配置"""
    return generate_param({
        'field': 0,
    })


# -*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-


def project_role_member():
    """获取项目成员列表"""
    return generate_param({}, is_project=True)


def stamps_role():
    """获取角色定义"""
    return generate_param({'role': 0})


def project_isu_template():
    """获取项目组件模板数据"""
    return generate_param({
        "team": 1652804780928255,
        "department": 1648118144144956,
        "group": 1648118144871625,
        "issue_type": 1652840528828114,
        "field": 1652804783170482,
        "task_status": 1648118142790953,
        "task_link_type": 1648118142272075,
        "role": 1652804789019025,
        "pipeline": 1652840529189082,
        "component_template": 1652840528820935,
        "project_template": 1497517064652901,
        "project": 1652840529189082
    })


# -*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-


def status_add(category='in_progress'):
    """添加全局工作项状态"""
    return generate_param({
        "task_status": {
            "name": f"in_progress_{mocks.num()}",
            "category": category
        }
    })


def status_delete():
    """删除全局工作项状态"""
    return generate_param()


def status_update(status_uuid):
    """更新全局工作项状态"""
    return generate_param({
        "task_status": {
            "name": f"up_status_name_{mocks.num()}",
            "category": "in_progress",
            "uuid": status_uuid
        }
    })


def issue_status_add(status_uuid):
    """全局工作项-工作流状态新增"""
    return generate_param({
        "task_status_configs": [
            {
                "status_uuid": status_uuid,
                "default": False
            }
        ]
    })


# -*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-
# 关联关系类型

def add_link_type(source, target, model=102):
    """
    新增关联关系
    :param source  发起关联方的工作项类型
    :param target  被关联方的工作项类型
    :param model  关联关系(102一对多、202多对多)
    """
    in_desc = f'InDesc-{mocks.ones_uuid()}'
    out_desc = f'OutDesc-{mocks.ones_uuid()}'

    p = {
        "query": '\n    mutation AddObjectLinkType {\n      addObjectLinkType (link_indesc: '
                 '$link_indesc link_outdesc: $link_outdesc name: $name source_condition: '
                 '$source_condition source_type: $source_type target_condition: $target_condition '
                 'target_type: $target_type link_in_desc: $link_in_desc link_out_desc: $link_out_desc '
                 'link_model: $link_model) {\n        key\n      }\n    }\n  ',
        "variables": {
            # "link_indesc": "",
            # "link_outdesc": "",
            "name": f"关联关系-{mocks.num()}",
            "source_condition": source,
            "source_type": "task",
            "target_condition": target,
            "target_type": "task",
            "link_in_desc": in_desc,
            "link_out_desc": out_desc,
            "link_model": model
        }
    }

    return generate_param(p)


def update_link_type(link_key, model):
    """更新关联关系"""

    in_desc = f'InDesc-{mocks.ones_uuid()}'
    out_desc = f'OutDesc-{mocks.ones_uuid()}'

    p = {
        "query": '\n    mutation UpdateObjectLinkType {\n      updateObjectLinkType (link_indesc: '
                 '$link_indesc link_outdesc: $link_outdesc name: $name source_condition: $source_condition '
                 'source_type: $source_type target_condition: $target_condition target_type: $target_type '
                 'built_in: $built_in create_time: $create_time key: $key link_in_desc: $link_in_desc '
                 'link_model: $link_model link_out_desc: $link_out_desc name_pinyin: $name_pinyin uuid:'
                 ' $uuid f_stamp: $f_stamp) {\n        key\n      }\n    }\n  ',
        "variables": {
            "name": f"Up关联关系-{mocks.num()}",
            "source_condition": "{}",
            "source_type": "task",
            "target_condition": "{}",
            "target_type": "task",
            "built_in": False,
            "key": link_key,
            "link_in_desc": in_desc,
            "link_model": model,
            "link_out_desc": out_desc,
        }
    }

    return generate_param(p)


def q_link_type():
    """查询关联关系"""
    p = {
        "query": 'query OBJECT_LINK_TYPES($filter: Filter, $orderBy: OrderBy) {\n    '
                 'objectLinkTypes (filter: $filter, orderBy: $orderBy) {\n      uuid\n      '
                 'name\n      namePinyin\n      builtIn\n      sourceType\n      sourceCondition\n      '
                 'linkOutDesc\n      linkOutDescPinyin\n      targetType\n      targetCondition\n'
                 '      linkInDesc\n      linkInDescPinyin\n      linkModel\n      key\n      \n    }\n  }',
        "variables": {
            "filter": {},
            "orderBy": {
                "createTime": "ASC"
            }
        }
    }

    return generate_param(p)


def q_relation_types():
    """查询关联关系列表-描述"""
    p = {
        "query": "query OBJECT_LINK_TYPES($filter: Filter, $orderBy: OrderBy) {\n    "
                 "objectLinkTypes (filter: $filter, orderBy: $orderBy) {\n      uuid\n      "
                 "name\n      builtIn\n      sourceType\n      sourceCondition\n      "
                 "linkOutDesc\n      linkOutDescPinyin\n      targetType\n      targetCondition\n"
                 "      linkInDesc\n      linkInDescPinyin\n      key\n    }\n  }",
        "variables": {
            "filter": {},
            "orderBy": {
                "namePinyin": "ASC"
            }
        }
    }
    return generate_param(p)


def delete_link_type(link_key):
    """删除关联关系"""
    p = {
        "query": '\n    mutation DeleteObjectLinkType {\n      deleteObjectLinkType (key: $key) '
                 '{\n        key\n      }\n    }\n  ',
        "variables": {
            "key": link_key
        }
    }
    return generate_param(p)


def link_related_task(task_uuid, link_uuid):
    """关联任务"""
    return generate_param({
        "task_uuids": [task_uuid],  # 工作项类型uuid
        "task_link_type_uuid": link_uuid,
        "link_desc_type": "link_in_desc"
    })


# -*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-
# 属性修改权限

def constraints(domain_uuid, field_uuid):
    """属性权限规则操作"""
    return generate_param({
        "constraints": [
            {
                "user_domain_type": "role",
                "user_domain_param": domain_uuid,
                "field_uuid": field_uuid
            }
        ]
    })


def constraints_del():
    """属性权限规则删除"""
    return generate_param({
        "constraint_uuids": [
            ""
        ]
    })


def proj_constraints_del(constraint_uuids: list):
    """属性权限规则删除"""
    return generate_param({
        "constraint_uuids": constraint_uuids
    }, is_project=True)


# -*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-
# 项目权限设置

def proj_permission(user_domain_type, permission, user_domain_param, project_uuid=ACCOUNT.project_uuid):
    """
    项目权限设置
    :param user_domain_type  成员域类型
    :param permission  权限类型
    :param user_domain_param  用户域参数
    """
    return generate_param({
        "permission_rule": {
            "context_type": "project",
            "context_param": {
                "project_uuid": project_uuid
            },
            "permission": permission,
            "user_domain_type": user_domain_type,
            "user_domain_param": user_domain_param
        }
    })


def team_permission(user_domain_param, user_domain_type=None, permission=None):
    '''
    团队权限设置
    :param user_domain_param:
    :param user_domain_type:
    :param permission:
    :return:
    '''
    return generate_param({
        "permission_rule": {
            "context_type": "team",
            "context_param": None,
            "permission": "administer_do" if not permission else permission,
            "user_domain_type": "single_user" if not user_domain_type else user_domain_type,
            "user_domain_param": user_domain_param
        }
    })


# -*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-
# 全局配置-工作项目权限

def global_issue_perm(user_domain_type, permission, user_domain_param):
    p = {
        "permission_rule": {
            "permission": permission,
            "user_domain_type": user_domain_type,
            "user_domain_param": user_domain_param
        }
    }
    return generate_param(p)


# -*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-
# 全局配置-项目管理-权限配置

def global_perm_config(permission, user_domain_type, user_domain_param):
    p = {
        "permission_rule": {
            "context_type": "team",
            "context_param": {
                "team_uuid": ACCOUNT.user.team_uuid
            },
            "permission": permission,
            "user_domain_type": user_domain_type,
            "user_domain_param": user_domain_param
        }
    }
    return generate_param(p)


def user_security_setting():
    """信息安全设置 邮箱可见性设置"""
    return generate_param({
        "settings": [
            {
                "name": "email_visible",
                "value": "private"
            }
        ]
    })
