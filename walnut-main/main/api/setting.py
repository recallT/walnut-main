# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：setting.py
@Author  ：zhangyonghui@ones.ai
@Date    ：7/19/22 3:39 PM 
@Desc    ：配置中心-设置类
"""
from falcons.ops import ProjectOps


class SidebarSetting(ProjectOps):
    uri = '/team/{team_uuid}/sidebar_setting/add_directory'
    name = '侧边栏菜单设置'
    api_type = 'POST'


class DelMenu(ProjectOps):
    uri = '/team/{team_uuid}/sidebar_setting/delete/{menu_uuid}'
    name = '删除自定义一级菜单'
    api_type = 'POST'


class SidebarSettingMenu(ProjectOps):
    uri = '/team/{team_uuid}/sidebar_setting/menus?categories=system,custom,other'
    name = '侧边栏菜单数据获取'
    api_type = 'GET'


class SidebarSettingUpdate(ProjectOps):
    uri = '/team/{team_uuid}/sidebar_setting/update'
    name = '菜单栏更新'
    api_type = 'POST'


class AddSidebarSetting(ProjectOps):
    uri = '/team/{team_uuid}/sidebar_setting/add'
    name = '新增自定义菜单'
    api_type = 'POST'


class GetSidebarMenus(ProjectOps):
    uri = '/team/{team_uuid}/sidebar_menus'
    name = '系统菜单列表'
    api_type = 'GET'


class WorkDaySetting(ProjectOps):
    uri = '/team/{team_uuid}/update_info'
    name = '工作日设置'
    api_type = 'POST'
