# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：setting.py
@Author  ：zhangyonghui@ones.ai
@Date    ：7/19/22 3:42 PM 
@Desc    ：
"""
from falcons.helper import mocks
from falcons.ops import generate_param


def add_directory():
    """配置中心-系统偏好设置-新增侧边菜单"""
    return generate_param({
        "value": "api-test" + mocks.num(),
        "position": 12,
        "is_custom": False
    })


def get_menu():
    return generate_param({})


def sidebar_setting_update():
    """更新菜单信息"""
    return generate_param({
        "sidebar_menus": [
            {
                "uuid": "",
                "key": "project",
                "default_value": "ONES Project",
                "value": "项目管理",
                "element_show": True,
                "is_show": True,
                "is_can_update_text": True,
                "is_can_update_is_show": False,
                "position": 1,
                "category": "system",
                "parent_uuid": "",
                "is_directory": False,
                "ext": None,
                "user_domains": []
            }
        ]
    })


def add_self_menu():
    return generate_param({
        "key": "custom_link",
        "value": "自定义菜单" + mocks.num(),
        "ext": {
            "url": "https://ones.cn/"
        },
        "user_domains": [
            {
                "user_domain_param": "",
                "user_domain_type": "everyone"
            }
        ]
    })


def update_self_menu_info(uuid):
    return generate_param({
        "sidebar_menus": [
            {
                "key": "custom_link:" + uuid,
                "uuid": uuid,
                "default_value": "自定义链接",
                "value": "ddd",
                "element_show": True,
                "is_show": True,
                "is_can_update_text": True,
                "is_can_update_is_show": False,
                "position": 0,
                "category": "custom",
                "parent_uuid": "",
                "is_directory": False,
                "ext": {
                    "url": "https://ones.cn/"
                },
                "user_domains": [],
                "custom": True
            }
        ]
    })


def set_work_day():
    return generate_param({
        "workdays": [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat"
        ],
        "workhours": 900000,
        "workhours_unit": "day"
    })
