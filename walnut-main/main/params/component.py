#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：component.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/7
@Desc    ：项目设置-组件配置测试用例数据模块
"""
from falcons.helper import mocks
from falcons.ops import generate_param

from main.params.const import ACCOUNT


def comp_default_view():
    """组件默认视图"""
    return generate_param({}, **{'issue_uuid': ''})


def new_comp_view():
    """新建视图"""
    return generate_param(
        {
            'group_by': "",
            'layout': 'narrow',
            'select_group_key': "",
            'is_fixed_quick_screening': False,
            'query': {
                'must': [
                    {
                        'must': [
                            {
                                'in': {
                                    'field_values.field006': [
                                        ACCOUNT.project_uuid
                                    ]
                                }
                            },
                            {
                                'in': {
                                    'field_values.field007': [
                                        'N85Gzctn'
                                    ]
                                }
                            }
                        ]
                    }
                ]
            },
            'condition': {
                'lock_conditions': [
                    {
                        'field_uuid': 'field006',  # 项目
                        'operate': {
                            'operate_id': 'include',
                            'predicate': 'in',
                            'negative': False,
                            'label': 'filter.addQueryContent.include',
                            'filter_query': 'in'
                        },
                        'value': [
                            ACCOUNT.project_uuid,  # 项目UUID
                        ]
                    },
                    {
                        'field_uuid': 'field007',  # 工作项类型 为任务， 取项目的任务组件UUID，使用stamp 接口 查 issue_types 配置
                        'operate': {
                            'operate_id': 'include',
                            'predicate': 'in',
                            'negative': False,
                            'label': 'filter.addQueryContent.include',
                            'filter_query': 'in'
                        },
                        'value': [  # 工作项UUID
                            'N85Gzctn'
                        ]
                    }
                ],
                'condition_groups': [
                    [
                        {
                            'field_uuid': 'field001',
                            'operate': {
                                'operate_id': 'match',
                                'predicate': 'match',
                                'negative': False,
                                'label': 'filter.addQueryContent.include',
                                'filter_query': 'match'
                            },
                            'value': None
                        },
                        {
                            'field_uuid': 'field017',
                            'operate': {
                                'operate_id': 'include',
                                'predicate': 'in',
                                'negative': False,
                                'label': 'filter.addQueryContent.include',
                                'filter_query': 'in'
                            },
                            'value': None
                        },
                        {
                            'field_uuid': 'field012',
                            'operate': {
                                'operate_id': 'include',
                                'predicate': 'in',
                                'negative': False,
                                'label': 'filter.addQueryContent.include',
                                'filter_query': 'in'
                            },
                            'value': None
                        },
                        {
                            'field_uuid': 'field004',
                            'operate': {
                                'operate_id': 'include',
                                'predicate': 'in',
                                'negative': False,
                                'label': 'filter.addQueryContent.include',
                                'filter_query': 'in'
                            },
                            'value': None
                        }
                    ]
                ],
                'is_init': True
            },
            'sort': [
                {
                    'field_values.field009': {
                        'order': 'desc'
                    }
                }
            ],
            'is_fold_all_groups': False,
            'table_field_settings': [],
            'is_show_derive': False,
            'display_type': 'sub_tree',
            'include_subtasks': True,
            'name': f'View{mocks.ones_uuid()}',
            'board_settings': None
        }
    )

# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
