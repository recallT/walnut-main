#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_devops.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/21 
@Desc    ： 流水线测试用例
"""
from falcons.com.nick import feature, story, mark, parametrize, fixture

from main.api import project as pjt
from main.params import devops


@fixture(scope='class')
def _storage():
    """
    Store devops list
    eg:
    {"create_time":1640229455,"item_type":"devops_ci_sync","key":"devops_ci_sync-7acx2jtw","uuid":"7acx2jtw"}
    :return:
    """
    p = []
    return p


@feature('配置中心')
class TestDevOps:

    @mark.smoke
    @mark.emphasis
    @story('关联Jenkins-新建关联成功')
    @parametrize('param', devops.devops_add())
    def test_devops_add(self, param, _storage):
        """添加jenkins"""
        cpy = pjt.DevopsAdd()
        # 调用接口
        cpy.call(param.json, **param.extra)
        # 检查接口响应码
        cpy.is_response_code(200)

        d = cpy.json()
        _storage.append(d['item'])

    @mark.emphasis
    @story('关联Jenkins-关联列表')
    @parametrize('param', devops.devops_list())
    def test_devops_list(self, param, _storage):
        """jenkins列表"""
        sync = pjt.DevopsSync()
        sync.call(param.json, **param.extra)
        sync.is_response_code(200)

    @mark.emphasis
    @story('关联Jenkins-编辑关联成功')
    @parametrize('param', devops.devops_add())
    def test_update_devops_ok(self, param, _storage):
        """更新jenkins"""
        updator = pjt.DevopsUpdate()

        param.uri_args({'devops_uuid': _storage[0]['uuid']})

        updator.call(param.json, **param.extra)
        updator.is_response_code(200)

    @story('23518 关联Jenkins-编辑关联失败')
    @parametrize('param', devops.devops_add(ok=False))
    def test_update_devops_fail(self, param, _storage):
        """更新jenkins"""
        updator = pjt.DevopsUpdate()

        param.uri_args({'devops_uuid': _storage[0]['uuid']})

        updator.call(param.json, **param.extra)
        updator.is_response_code(401)

    @mark.emphasis
    @story('23517 关联Jenkins-删除关联成功')
    @parametrize('param', devops.devops_delete())
    def test_devops_delete(self, param, _storage):
        """删除jenkins"""
        dev_delete = pjt.DevopsDelete()
        # param.uri_args({'devops_uuid': '7acx2jtw'})
        param.uri_args({'devops_uuid': _storage[0]['uuid']})
        dev_delete.call(**param.extra)
        dev_delete.is_response_code(200)
