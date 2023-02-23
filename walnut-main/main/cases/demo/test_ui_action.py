#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_ui_action.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/11/23 
@Desc    ：UI Automation Case Demo
"""
import time

from falcons.com.nick import story, fixture, feature
from falcons.com.ui import UiDriver
from falcons.pages import WikiPage, ProjectPage, ConfCenterPage

from main.params.const import ACCOUNT


@fixture(scope='session')
def demo_driver():
    u = ACCOUNT.user
    driver = UiDriver(u)

    return driver


@feature('UI 测试DEMO')
class TestUICase:
    """UI 测试DEMO"""

    @story('项目管理')
    def test_ui_home_page(self, demo_driver):
        prj = ProjectPage(demo_driver)

        prj.side_bar.nav_to('项目管理')
        prj.main_page.click_link('未开始')
        # time.sleep(1)
        prj.main_page.click_link('全部项目')
        # time.sleep(1)
        prj.enter_project('敏捷式项目1')
        time.sleep(1)
        prj.main_page.take_screenshot('save')
        prj.top_bar.click_link('迭代')
        time.sleep(0.5)
        prj.top_bar.click_link('迭代计划')

        # 录入页面内容
        prj.main_page.click_button('新建迭代')

        prj.main_page.input('迭代名称', '迭代一')
        # time.sleep(0.5)
        prj.main_page.search_input('所属项目', '敏捷式项目1')
        # time.sleep(0.5)
        prj.main_page.member_input('迭代负责人', 'test@ones.ai')
        # time.sleep(0.5)
        prj.main_page.dropdown('迭代周期', '3周')
        # time.sleep(0.5)
        prj.main_page.date_input('迭代开始日期', '2021-12-01')

        prj.main_page.take_screenshot('项目管理.png')
        prj.main_page.click_button('确定')
        # home.nav_to('知识库管理')
        # home.take_screenshot('知识库管理.png')
        # home.nav_to('测试管理')
        # home.take_screenshot('测试管理.png')

    @story('知识库管理')
    def test_wiki_add_new_page_group(self, demo_driver):
        wiki = WikiPage(demo_driver)
        wiki.side_bar.nav_to('知识库管理')

        wiki.main_page.click_button('新建页面组')

        wiki.main_page.assert_page_contains('页面组是否共享')

        wiki.main_page.input('页面组名称', 'My First Page Group')
        time.sleep(1)
        wiki.main_page.assert_value('页面组名称', 'My First Page Group')

        wiki.main_page.input('页面组描述', 'My First Page Group...', el_type='textarea')
        time.sleep(1)
        # wiki.main_page.assert_value('页面组名称', 'My First Page Group')
        # time.sleep(1)
        # wiki.main_page.take_screenshot('save.png')
        # wiki.main_page.assert_page_contains('页面组是否共享adf')

    @story('配置中心')
    def test_jenkins_config(self, demo_driver):
        """"""
        conf_center = ConfCenterPage(demo_driver)
        conf_center.main_page.driver.refresh()
        conf_center.side_bar.nav_to_setting()
        conf_center.main_page.config_side_bar('流水线管理配置')
        conf_center.main_page.click_link('关联 Jenkins 服务')
        conf_center.main_page.click_button('新建关联 Jenkins')
        conf_center.main_page.input('Jenkins URL', 'http://localhost:8080/jenkins')
        conf_center.main_page.take_screenshot('配置中心')
