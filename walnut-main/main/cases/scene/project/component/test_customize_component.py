# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_customize_component.py
@Author  ：zhangyonghui@ones.ai
@Date    ：2022/6/23 11:26 AM 
@Desc    ：
"""
from falcons.check import go, Checker
from falcons.com.nick import fixture, step, story, feature

from main.actions.pro import PrjAction
from main.api import project


@fixture(scope='module', autouse=True)
def add_customize_component():
    """新增自定义链接组件，并返回请求参数"""
    param, exist_components = PrjAction.add_customize_component(is_param=True)
    param.json['components'] += exist_components  # 添加上原有组件
    resp = go(project.ComponentsAdd, param)

    return param


@feature('组件-自定义链接组件')
class TestCustomizeComponent(Checker):

    @story('141701 自定义链接组件配置-基础设置：修改组件显示名称')
    def test_update_customize_link_component_name(self, add_customize_component):
        param = add_customize_component
        param.json_update('components[0].desc', '自定义链接组件描述修改哈哈哈哈哈哈哈')
        resp_desc = go(project.UpdateComponents, param)
        resp_desc.check_response('components[0].desc', '自定义链接组件描述修改哈哈哈哈哈哈哈')

    @story('T141700 自定义链接组件配置-基础设置：修改组件描述')
    def test_update_customize_link_component_desc(self, add_customize_component):
        param = add_customize_component
        param.json_update('components[0].name', '示例自定义链接组件')
        resp_desc = go(project.UpdateComponents, param)
        resp_desc.check_response('components[0].name', '示例自定义链接组件')
        with step('修改回原来的名称'):
            param.json_update('components[0].name', '自定义链接')
            resp_desc = go(project.UpdateComponents, param)
            resp_desc.check_response('components[0].name', '自定义链接')

    @story('T141695 自定义链接组件配置-基础设置：检查基础设置展示信息')
    def test_check_customize_link_component_info(self):
        ...

    @story('T141699 自定义链接组件配置-基础设置：通过按钮移除自定义链接组件')
    def test_del_customize_link_component(self):
        # PrjAction.add_customize_component()
        with step('自定义链接组件'):
            PrjAction.remove_prj_component('自定义链接')

    @story('T143655 添加自定义链接组件')
    @story('T138462 项目组件-导航自定义：拖拽移除「自定义链接」组件')
    @story('23282 添加自定义链接组件')
    @story('143657 移除已添加的组件')
    def test_add_customize_link_component(self):
        with step('添加自定义链接组件'):
            param, exist_components = PrjAction.add_customize_component(is_param=True)
            param.json['components'] += exist_components  # 添加上原有组件
            param.json_update('components[0].name', '链接组件')
            resp = go(project.ComponentsAdd, param)
        with step('项目组件-导航自定义：拖拽移除「自定义链接」组件'):
            PrjAction.remove_prj_component('链接组件')
