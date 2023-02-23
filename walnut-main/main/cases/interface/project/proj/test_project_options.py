#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_project_options.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/11/22 
@Desc    ：
"""
import time

from falcons.com.nick import parametrize, feature, fixture, story, mark

from main.api.project import MyProject, AddProject, DeleteProject
from main.params.proj import my_project_list, add_project


@fixture(scope='class')
def uuid_storage():
    """用于存储案例间共享的数据"""
    p = []
    return p


@feature('项目相关接口')
class TestProjects:
    @mark.smoke
    @story('添加项目')
    @parametrize('param', add_project())
    def test_add_project(self, param, uuid_storage):
        """添加项目"""

        add_p = AddProject()

        # 缓存项目uuid 用在下边的用例
        uuid_storage.append(param.json['project']['uuid'])

        # 添加测试用户token
        extra = param.extra

        # 调用接口1
        add_p.call(param.json, **extra)
        # 检查接口响应码
        add_p.is_response_code(200)

        # 检查测试响应数据
        add_p.check_response('project.status', 1)
        add_p.check_response('project.uuid', param.json['project']['uuid'])
        add_p.check_response('project.name', param.json['project']['name'])

    @story('添加项目')
    @parametrize('param', add_project())
    def test_add_project_empty_type(self, param, uuid_storage):
        """添加项目参数无效"""

        add_p = AddProject()
        # 缓存项目uuid 用在下边的用例
        uuid_storage.append(param.json['project']['uuid'])

        param.json['template_id'] = ''
        extra = param.extra
        # 调用接口1
        add_p.call(param.json, **extra)
        # 检查接口响应码
        add_p.is_response_code(200)

        # 检查测试响应数据
        add_p.check_response('project.type', 'agile')

    @story('添加项目-参数无效')
    @parametrize('param', add_project())
    def test_add_project_invalid_param_empty_name(self, param):
        """添加项目参数无效"""

        add_p = AddProject()

        param.json['project']['name'] = ''
        extra = param.extra
        # 调用接口1
        add_p.call(param.json, **extra)
        # 检查接口响应码
        add_p.is_response_code(801)

        # 检查测试响应数据
        add_p.check_response('errcode', 'InvalidParameter.Project.Name.Empty')

    @story('项目列表')
    @parametrize('param', my_project_list())
    def test_my_proj_list(self, param, uuid_storage):
        """我的项目列表"""
        my_proj = MyProject()

        extra = param.extra

        # 调用接口
        my_proj.call(**extra)
        # 检查接口响应码
        my_proj.is_response_code(200)
        # # 检查测试响应数据
        my_proj.check_response('projects[0].status', 1)

    @story('137402 项目操作：删除项目')
    @parametrize('param', my_project_list())
    def test_delete_project(self, param, uuid_storage):
        """删除项目"""
        del_proj = DeleteProject()
        extra = param.extra
        for uuid in uuid_storage:
            extra['uri_args'] |= {'project_uuid': uuid}

            del_proj.call(**extra)
            del_proj.is_response_code(200)
            time.sleep(0.2)
