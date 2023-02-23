#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_team.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/2 
@Desc    ：团队管理测试案例
"""
from falcons.com.nick import feature, story, parametrize
from falcons.helper.codes import get_member_uuid

from main.api.project import TeamInfo, TeamUpdate, DeleteMember
from main.params.data import team_updating, delete_member


@feature('团队管理接口')
class TestTeam:

    @story('T136046 团队配置-团队信息：修改团队名称')
    @parametrize('p', team_updating())
    def test_update_team_success(self, p):
        """更新团队信息"""

        team_update = TeamUpdate()
        # 调用接口
        team_update.call(p.json, **p.extra)
        # 检查接口响应码
        team_update.is_response_code(200)

    @story('获取团队信息')
    @parametrize('p', team_updating())
    def test_team_info_success(self, p):
        """获取团队信息"""

        team_info = TeamInfo()
        # 调用接口
        team_info.call(**p.extra)
        # 检查接口响应码
        team_info.is_response_code(200)

        team_info.check_response('uuid', p.extra['uri_args']['team_uuid'])


@feature('团队管理接口')
class TestDeleteMember:
    """"""

    @story('删除成员')
    @parametrize('param', delete_member())
    def test_delete_member(self, param):
        """"""
        uid = get_member_uuid()
        dm = DeleteMember()
        param.json['member'] = uid
        dm.call(param.json, **param.extra)

        dm.is_response_code(200)

        dm.check_response('fail_count', 0)

    @story('删除成员失败')
    @parametrize('param', delete_member())
    def test_delete_member_fail_member_uuid(self, param):
        """"""

        dm = DeleteMember()
        param.json['member'] = '999'  # member not exist
        dm.call(param.json, **param.extra)

        dm.is_response_code(400)

    @story('删除成员失败')
    @parametrize('param', delete_member())
    def test_delete_member_fail_empty_member_uuid(self, param):
        """"""

        dm = DeleteMember()
        param.json['member'] = ''  # empty member uuid
        dm.call(param.json, **param.extra)

        dm.is_response_code(400)
