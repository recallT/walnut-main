#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_pipeline.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/23 
@Desc    ：
"""
import time

from falcons.check import go
from falcons.com.nick import feature, story, mark, parametrize, fixture, step
from falcons.com.meta import ApiMeta
from main.api import project as pjt
from main.params import devops


# 初始化流水线Jenkins
@fixture(scope='module', autouse=True)
def add_devops_jenkins():
    prm = devops.pipeline_list()[0]
    re = go(pjt.ItemGraphql, prm)

    if not re.value('data.devopsPipelines'):
        p = devops.jenkins_add()[0]
        go(pjt.ItemsAdd, p)
        time.sleep(2)  # 等待 add_devops_jenkins添加完成


@fixture(scope='module')
def _storage():
    """"""
    p = []
    return p


@fixture(scope='module')
def _pip_storage():
    """"""
    p = []
    return p


label = ApiMeta.env.label


@mark.skipif(label == 'private' or label == 'dev', reason='环境跳过开箱用例')
class TestProjDevOps:
    @story('T23538 关联已有流水线')
    @story('23441 配置中心-关联 Jenkins-新建关联jenkins成功')
    @parametrize('param', devops.component_stamp())
    def test_relate_pipeline(self, param, _storage):
        """关联已有流水线"""
        with step(''):
            component_stamp = pjt.ProjectStamp()
            component_stamp.call(param.json, **param.extra)
            component_stamp.is_response_code(200)
            j = component_stamp.json()

            exist_components = [{'uuid': c['uuid'], 'template_uuid': c['template_uuid']}
                                for c in j['component']['components']]

            _storage.append(exist_components)

        # 暂无流水线组件
        with step('暂无流水线组件'):
            assert 'com00030' not in [e['template_uuid'] for e in exist_components]

    @story('新增已有流水线')
    @parametrize('param', devops.component_add())
    def test_add_pipeline(self, param, _storage):
        """关联已有流水线"""

        with step('添加流水线组件'):
            component_add = pjt.ComponentsAdd()
            pipe_data = param.json['components'][0]
            uuid = pipe_data['uuid']

            param.json['components'] += _storage[0]

            _storage.append(uuid)
            component_add.call(param.json, **param.extra)
            component_add.is_response_code(200)
            component_add.check_response('components[0].uuid', uuid)

        with step('获取流水线列表'):
            """"""
            gq_param = devops.ci_list()[0]
            gq = go(pjt.ItemGraphql, gq_param)

            # time.sleep(2)  等待 add_devops_jenkins添加完成
            pipelines = gq.value('data.devopsPipelines')

            if not pipelines:
                time.sleep(2)
                param = devops.ci_list()[0]
                res = go(pjt.ItemGraphql, param)
                pipelines = res.value('data.devopsPipelines')
            print(pipelines)

        with step('关联流水线'):
            """"""
            try:
                param_update = devops.component_update()[0]
                param_update.json['objects'].append({'uuid': pipelines[0]['uuid'], 'type': 1003})
                param_update.uri_args({'component_uuid': uuid})

                go(pjt.ComponentUpdate, param_update)

            except IndexError:
                print('Do nothing...')

    @story('T23541 搜索流水线')
    @parametrize('param', devops.devops_search())
    def test_search_pipeline(self, param):
        """"""
        p_search = pjt.ItemGraphql()
        p_search.call(param.json, **param.extra)
        p_search.is_response_code(200)

    @story('T23543 展示流水线最新信息')
    @parametrize('p', devops.pipeline_run_history())
    def test_show_pipeline_latest_info(self, p, _storage):
        """"""
        history = pjt.ItemGraphql()
        uid = _storage[1]
        p.json['variables']['filter']['pipelineUUID_in'].append(uid)

        history.call(p.json, **p.extra)
        history.is_response_code(200)
        # history.check_response()

    @story('T23520 取消关联流水线')
    @parametrize('p', devops.component_update())
    def test_cancel_relate_pipeline(self, p, _storage):
        """"""
        component_update = pjt.ComponentUpdate()
        uid = _storage[1]
        p.json['uuid'] = uid
        p.uri_args({'component_uuid': uid})
        component_update.call(p.json, **p.extra)
        component_update.is_response_code(200)

        component_update.check_response('uuid', uid)


@mark.skipif(label == 'private' or label == 'dev', reason='环境跳过开箱用例')
@feature('流水线管理')
class TestPipeline:
    """"""

    @story('T23534 pipeline首页-查看流水线权限')
    @story('T23521 pipeline首页-可视化流水线动态')
    @story('23525 pipeline首页-流水线自动同步成功')
    @story('23693 pipeline首页-详情页-正常查看可视化流水线动态')
    @parametrize('p', devops.pipeline_list())
    def test_show_pipeline(self, p, _pip_storage):
        """"""
        lis = pjt.ItemGraphql()
        time.sleep(1)
        lis.call(p.json, **p.extra)
        lis.is_response_code(200)
        j = lis.json()['data']['devopsPipelines'][0]
        _pip_storage.append(j['uuid'])

    @story('T23536 pipeline首页-设置流水线权限')
    @parametrize('p', devops.permission_add())
    def test_permission_pipeline(self, p, _pip_storage):
        """"""
        lis = pjt.PermissionAdd()
        p.json['permission_rule']['context_param'] |= {'pipeline_uuid': _pip_storage[0]}
        lis.call(p.json, **p.extra)

        lis.is_response_code([200, 409])
        if lis.response.status_code == 200:
            lis.check_response('permission_rule.user_domain_type', p.json['permission_rule']['user_domain_type'])
            lis.check_response('permission_rule.permission', p.json['permission_rule']['permission'])

    @story('T23526 pipeline首页-可以搜索出流水线内容')
    @parametrize('p', devops.devops_search())
    def test_search_pipeline(self, p):
        """"""
        lis = pjt.ItemGraphql()
        lis.call(p.json, **p.extra)
        lis.is_response_code(200)

    @story('T23529 pipeline首页-流水线详情-代码提交查看正常')
    @story('T23528 pipeline首页-运行历史-信息展示正常')
    @story('23784 项目-工作项-查看流水线构建信息')
    @story('23544 项目-流水线组件-最新信息跳转正常')
    @parametrize('p', devops.pipeline_run_history())
    def test_history_pipeline(self, p, _pip_storage):
        """"""
        lis = pjt.ItemGraphql()
        p.json['variables']['filter']['pipelineUUID_in'].append(_pip_storage[0])
        lis.call(p.json, **p.extra)
        lis.is_response_code(200)

    @story('T23522 pipeline首页-状态分组tab切换正常')
    @parametrize('p', devops.pipeline_list())
    def test_tab_search_pipeline(self, p, _pip_storage):
        """"""
        lis = pjt.ItemGraphql()

        # f |= {}
        lis.call(p.json, **p.extra)
        lis.is_response_code(200)

    @story('T23527 pipeline首页-置顶流水线功能正常')
    @parametrize('p', devops.pipeline_pin())
    def test_pin_pipeline(self, p, _pip_storage):
        """"""
        pin = pjt.PipePin()
        p.uri_args({'pipeline_uuid': _pip_storage[0]})
        pin.call(p.json, **p.extra)
        pin.is_response_code(200)

    @story('pipeline首页-取消置顶流水线功能正常')
    @parametrize('p', devops.pipeline_pin())
    def test_unpin_pipeline(self, p, _pip_storage):
        """"""
        pin = pjt.PipePin()
        p.uri_args({'pipeline_uuid': _pip_storage[0]})
        pin.call(p.json, **p.extra)
        pin.is_response_code(200)
