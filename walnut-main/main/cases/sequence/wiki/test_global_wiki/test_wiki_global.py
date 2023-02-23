# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_wiki_global.py
@Author  ：zhangyonghui@ones.ai
@Date    ：8/12/22 4:15 PM 
@Desc    ：WIKI 配置中心
"""
from falcons.check import Checker
from falcons.com.nick import feature, story, step
from falcons.helper import mocks
from falcons.ops import generate_param

from main.actions.wiki import WikiAction as wa
from main.api import wiki


@feature('WIKI 配置中心')
class TestGlobalWiki(Checker):

    @story('T24226 wiki配置中心-删除全局模板')
    @story('T24220 wiki配置中心-新建模板')
    @story('T24224 wiki配置中心-编辑全局模板')
    def test_wiki_global_template_action(self):
        with step('新建模板'):
            global_uuid = wa.add_global_wiki_template()
            # 列表存在新增模版
            template_list = wa.wiki_global_template_list().value('templates')
            template_uuids = [r['uuid'] for r in template_list]
            assert global_uuid in template_uuids

        with step('编辑模版'):
            wa.update_global_wiki_template(global_uuid=global_uuid)

        with step('点击模板删除按钮，点击删除模板'):
            wa.del_global_template(global_uuid=global_uuid)

            # 列表不存在新增模版
            template_list = wa.wiki_global_template_list().value('templates')
            template_uuids = [r['uuid'] for r in template_list]
            assert global_uuid not in template_uuids

    @story('T147318 新建模板-Wiki 协同页面：新建全局模板')
    @story('T146634 编辑全局模板：编辑「Wiki 协同页面」')
    @story('T146632 删除模板：删除「Wiki 协同页面」模板')
    def test_collaborate_wiki_global_template_action(self):
        with step('新建模板'):
            global_uuid = wa.add_collaborate_wiki_global_template()
            template_list = wa.wiki_global_template_list().value('templates')
            template_uuids = [r['uuid'] for r in template_list]
            assert global_uuid in template_uuids
        with step('编辑模版'):
            param = generate_param({
                "title": "update_title" + mocks.num()
            })[0]
            param.uri_args({'online_templates_uuid': global_uuid})
            resp = self.call(wiki.PublishOnlineTemplate, param)
            resp.check_response('code', 200)

        with step('点击模板删除按钮，点击删除模板'):
            wa.del_global_template(global_uuid=global_uuid)
            template_list = wa.wiki_global_template_list().value('templates')
            template_uuids = [r['uuid'] for r in template_list]
            assert global_uuid not in template_uuids
