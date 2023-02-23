#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：auth.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/24 
@Desc    ：
"""
from falcons.helper import mocks
from falcons.ops import generate_param


def join_team():
    """加入团队"""
    return generate_param({
        "email": "normalxxx@ones.ai",
        "password": "word0pass",
        "name": "normal1",
        "invite_code": ""  # 邀请码 形如 85TwopquxUXxfGuyw5jLY1fiBkolG3zU
    })


def invitation(single=False):
    """邀请注册"""
    u = [{'email': f'{mocks.ones_uuid("mb_").lower()}@ones.ai'}] if single \
        else [{'email': f'{mocks.ones_uuid("mb_").lower()}@ones.ai'} for _ in range(2)]
    return generate_param({
        'invite_settings': u,
        'license_types': [7, 8, 4, 5, 1, 3, 2]
    })


def invitation_history():
    """邀请列表"""
    return generate_param({})


def permission_rules():
    """权限配置信息"""
    return generate_param({
        "context_type": "team",
        "context_param": None
    })
