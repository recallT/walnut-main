#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：conftest.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/11/25 
@Desc    ：
"""
import time

from falcons.com.meta import ApiMeta
from falcons.com.nick import fixture
from falcons.com.ui import UiDriver
from falcons.pages import ProjectPage

from main.actions.team import TeamAction


@fixture(scope='session')
def demo_driver():
    """"""
    u = ApiMeta.account.user
    driver = UiDriver(u)

    return driver


@fixture(autouse=True, scope='session')
def clean_stuff(demo_driver):
    """"""
    yield
    # Quit Browser
    print('Quit browser....')
    demo_driver.driver.quit()


@fixture(scope='class')
def project_page(demo_driver):
    prj = ProjectPage(demo_driver)
    print(f'Now UI project name is :[{prj.proj_name}]')
    team, num = TeamAction.team_info(ApiMeta.account.user.team_uuid)
    # jss = """
    #         elem = document.evaluate('//div[contains(@class, "team-list-wrapper")]/ul/li[%s]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue;
    #         elem.click();
    #        """ % (num)
    loc = '//span[text()="测试专用"]/..'
    _, is_exist = demo_driver.is_visibility(loc)
    if is_exist:
        prj.side_bar.action_click('//span[text()="测试专用"]/..')
        prj.driver.find_element(f'//div[contains(@class, "team-list-wrapper")]/ul/li[{num}]').click()
    return prj
