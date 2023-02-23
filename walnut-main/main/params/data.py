#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：data.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/11/19 
@Desc    ： 测试用例数据
"""
from falcons.com.meta import OnesParams
from falcons.helper import mocks
from falcons.ops import generate_param

from main.environ import FieldType
from main.params.const import ACCOUNT


def reset_passwd():
    """重置密码链接"""

    return generate_param({'email': ACCOUNT.user.email}, **{'member_uuid': ACCOUNT.user.member_uuid})


def team_updating(team_name=None):
    """更新团队信息"""
    return generate_param({
        'name': team_name if team_name else '00AutoT'  # 团队名称 这里固定名字 方便UI测试
    })


def workday_update(unit, workhours=8):
    """
    更新工时设置
    :param unit: 默认单位：天 'day',小时 'hour'
    :param workhours: 一天多少个小时 默认给8小时
    :return:
    """
    return generate_param({

        "workdays": [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri"
        ],
        "workhours": workhours * 10 ** 5,
        "workhours_unit": unit

    })


def delete_member():
    """"""
    return generate_param({
        'member': '',  # uuid assign in case
    })


def user_req_code():
    """获取用户验证码"""
    return generate_param({
        'email': f'{mocks.ones_uuid()}@ones.ai'
    })


def user_req_code_registered():
    """获取用户验证码"""
    return generate_param({
        'email': ACCOUNT.user.email
    })


def user_verify_passwd():
    """获取用户密码"""

    return generate_param({
        'password': ACCOUNT.user.passwd,
        'email': ACCOUNT.user.email,
    })


def user_req_code_invalid():
    """获取用户验证码"""

    return generate_param({
        'password': f'{mocks.ones_uuid().lower() * 4}'
    })


def update_user_info():
    """"""

    return generate_param({
        'name': 'Test Admin',
        'title': 'CTO',
        'company': f'Ones Brh {mocks.ones_uuid().upper()} L.T.D'
    })


def user_group_add():
    """添加用户组"""

    return generate_param({
        'name': f'abc-{mocks.num()}',
        'members': []
    })


def user_group_update():
    """更新用户组"""

    return generate_param({
        'uuid': '',  # Assign in case
        'name': 'New name Update',
        'members': []
    }, **{'group_uuid': ''})


def user_group_list():
    """获取用户组列表"""

    return generate_param({
        'name': 'abc',
        'members': []
    })


# ========================================================================================

def version_add():
    """版本添加"""
    return generate_param({
        'version': {
            'release_time': mocks.now_timestamp(),
            'title': f'V-{mocks.ones_uuid()}',
            'assign': None
        }
    })


def version_update():
    """版本更新"""

    return generate_param({
        'version': {
            'release_time': mocks.now_timestamp(),
            'title': 'V-X',
            'assign': None,
        }
    }, **{'version_uuid': ''})


# ========================================================================================

def product_add():
    """添加Item"""

    return generate_param({
        'item': {
            'assign': ACCOUNT.user.owner_uuid,
            'name': f'Pro - {mocks.ones_uuid()}',
            'item_type': 'product'
        }
    })


def product_update():
    """更新Item"""

    return generate_param({
        'item': {
            'name': f'Pro-New-{mocks.num()}',
        }
    }, **{'item_key': ''})


def item_delete():
    """删除Item"""

    return generate_param({}, **{'item_key': ''})


# ========================================================================================


def fields_add():
    """Fields Add"""

    field_types = [x for x in FieldType.__dict__ if not x.startswith('__')]
    fields = []

    option = ('option', 'multi_option')
    stays = ('stay_count', 'stay_times')

    for t in field_types:
        p = OnesParams()
        field = {
            'name': f'{t.capitalize()}{mocks.serial_no()}'[:30],
            'type': getattr(FieldType, t),
            'renderer': 1,
            'filter_option': 0,
            'search_option': 1
        }
        if t in option:
            field |= {
                'options': [
                    {
                        'value': 'option1',
                        'background_color': '#307fe2',
                        'color': '#fff'
                    },
                    {
                        'value': 'option2',
                        'background_color': '#00b388',
                        'color': '#fff'
                    }
                ],
            }
        if t in stays:
            field |= {
                'stay_settings': {
                    'field_type': 1,
                    'field_uuid': 'GSsZx4J2',
                    'field_option_uuid': '9XpFxDwp'
                },
            }

        if t == 'interval':
            field |= {
                "step_settings": {
                    "step_start": {
                        "field_type": 12,
                        "field_uuid": "field005",
                        "method": "first_at",
                        "field_option_uuid": "NCBNHCH3"
                    },
                    "step_end": {
                        "field_type": 12,
                        "field_uuid": "field005",
                        "method": "first_at",
                        "field_option_uuid": "NCBNHCH3"
                    }
                },
            }
        if t == 'appear_time':
            field |= {
                "appear_time_settings": {
                    "field_uuid": "field005",
                    "method": "first_at",
                    "field_option_uuid": "NCBNHCH3"
                },
            }
        p.json = {'field': field}

        p.uri_args({'team_uuid': ACCOUNT.user.team_uuid, })

        fields.append(p)

    return fields


def field_update():
    """Field update"""

    return generate_param({
        'field': {  # All field should be replaced in case.
            'name': 'Field-integer-0',
            'type': 3,
            'uuid': 'L222x9mn'
        }
    }, **{'field_uuid': '', })


def field_delete():
    """Field delete"""

    return generate_param(is_project=True)

# ========================================================================================
