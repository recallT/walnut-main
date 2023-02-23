#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_dashboard.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/8 
@Desc    ：项目设置-项目操作
"""
import json

from falcons.check import Checker
from falcons.com.nick import feature, story, mark, parametrize, step, fixture

from main.actions.task import TaskAction
from main.api import project as prj
from main.params import proj, conf


@fixture(scope='module')
def _proj_uuid():
    return []


@mark.smoke
@feature('项目设置-项目操作')
class TestProjOpt(Checker):
    @mark.smoke
    @story('137396 复制项目')
    @parametrize('param', proj.proj_copy())
    def test_copy_proj(self, param, _proj_uuid):
        with step('复制项目'):
            cpy = prj.CopyProject()
            # 调用接口
            cpy.call(param.json, **param.extra)
            # 检查接口响应码
            cpy.is_response_code(200)

        with step('检查copy项目结果'):
            if TaskAction.wait_to_done(cpy.value('uuid')):
                q = prj.QueuesList()
                q.call(**param.extra)
                q.is_response_code(200)
                # 去掉这个步骤，因为批处理消息包含了其他步骤的消息返回，这里校验无用
                # q.check_response('batch_tasks[0].job_type', 'copy_project')
                # q.check_response('batch_tasks[0].job_status', 'done')

            #  获取复制后项目的uuid 用于删除该项目
            with step('获取复制后新项目的UUID'):
                tasks = [t for t in q.json()['batch_tasks'] if t['job_type'] == 'copy_project']
                for t in tasks:
                    extra = json.loads(t['extra'])
                    if extra['project_name'].startswith('CopyPrj'):
                        _proj_uuid += t['successful_objects']

            with step('清除批处理消息'):
                dismiss_uuid = [u['uuid'] for u in q.json()['batch_tasks'] if u['job_status'] == 'done']

                hide = prj.HiddenProgress()

                hide.call({'uuids': dismiss_uuid}, **param.extra)
                hide.is_response_code(200)

    @story('137398 归档项目')
    @parametrize('param', proj.proj_archive())
    def test_archive_proj(self, param, _proj_uuid):
        with step('归档项目'):
            param.uri_args({'item_key': f'project-{_proj_uuid[0]}'})
            resp = self.call(prj.ItemUpdate, param)

            resp.check_response('item.is_archive', True)

        with step('进入项目管理-已归档tab'):
            s_param = conf.get_sys_status()[0]
            del s_param.json['view'][1]
            s_param.json['query']['must'] = [{"equal": {"item_type": "project"}}, {"equal": {"uuid": _proj_uuid[0]}}]

            resp = self.call(prj.TeamView, s_param)
            resp.check_response('items[0].is_archive', True)

    @story('137400 取消归档项目')
    @parametrize('param', proj.proj_archive())
    def test_cancel_archive_proj(self, param, _proj_uuid):
        with step('取消项目归档'):
            param.json_update('item.is_archive', False)
            param.uri_args({'item_key': f'project-{_proj_uuid[0]}'})
            resp = self.call(prj.ItemUpdate, param)

            resp.check_response('item.is_archive', False)

        with step('进入项目管理-已归档tab'):
            s_param = conf.get_sys_status()[0]
            del s_param.json['view'][1]
            s_param.json['query']['must'] = [{"equal": {"item_type": "project"}}, {"equal": {"uuid": _proj_uuid[0]}}]

            resp = self.call(prj.TeamView, s_param)
            resp.check_response('items[0].is_archive', False)

    @story('137877 删除项目')
    @parametrize('param', proj.proj_delete())
    def test_del_proj(self, param, _proj_uuid):
        with step('删除复制后的项目'):
            param.uri_args({'project_uuid': _proj_uuid[0]})
            self.call(prj.DeleteProject, param, with_json=False)
