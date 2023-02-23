#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_clean_projects.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/16 
@Desc    ：
"""
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture

from main.actions.task import TaskAction
from main.helper.extra import Extra


@fixture(scope='session', autouse=True)
def clean_project():
    """"""
    yield
    print('Nothing todo...')


@feature('批量删除项目')
class TestBatchDelProject:
    @story('批量删除项目')
    def test_batch_delete_project(self, ignore_project):
        """"""
        init = Extra(ApiMeta)

        all_projects = init.fetch_all_projects()

        tobe_del = [a for a in all_projects if a not in ignore_project] if ignore_project else all_projects

        for u in tobe_del:
            init.del_project(u)


    # def test_demo(self):  新建任务
    #     # proj_uuid 项目ID，在URL链接中，处于project/项目id
    #     ise = TaskAction.new_issue_batch(batch_no=1100, proj_uuid='7tMnkPmXQkDGDIgD')
    def test_demo(self):
        init = Extra(ApiMeta)
        project_name = f'AAAA-app-test'
        p_uuid = init.new_project(project_name)