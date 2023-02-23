#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：wiki.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/11/18 
@Desc    ：
"""
from falcons.ops import WikiOps, ProjectOps


class Demo(WikiOps):
    """

    """
    uri = '/wiki/api/wiki/team/{team_uuid}/page/{page_uuid}?version='
    name = ''
    api_type = 'GET'


class WikiSpaces(WikiOps):
    uri = '/team/{team_uuid}/my_spaces'
    name = 'wiki my_spaces 页面组'
    api_type = 'GET'


class WikiPages(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/pages?status=1'
    name = 'wiki列表查询'
    api_type = 'GET'


class UnBindWiki(ProjectOps):
    uri = '/team/{team_uuid}/task/{task_uuid}/unbind_wiki_page'
    name = '解绑Wiki'
    api_type = 'POST'


class BindWiki(ProjectOps):
    uri = '/team/{team_uuid}/task/{task_uuid}/bind_wiki_page'
    name = '绑定Wiki'
    api_type = 'POST'


class AddWikiSpaces(WikiOps):
    uri = '/team/{team_uuid}/spaces/add'
    name = '新增wiki页面组'
    api_type = 'POST'


class DelWikiSpace(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/delete'
    name = '删除wiki页面组'
    api_type = 'POST'


class AddWikiPages(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/drafts/add'
    name = '新增wiki页面'
    api_type = 'POST'


class DeployWikiPages(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/draft/{uuid}/update'
    name = '发布wiki页面'
    api_type = "POST"


class DelWikiPages(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/page/{page_uuid}/delete'
    name = '删除wiki页面'
    api_type = 'POST'


class SpaceTemplates(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/templates/add'
    name = '新建wiki页面组模版'
    api_type = 'POST'


class SpaceOnlineTemplates(WikiOps):
    uri = '/team/{team_uuid}/online_templates/add'
    name = '新建wiki协同页面组模版'
    api_type = 'POST'


class PublishOnlineTemplate(WikiOps):
    uri = '/team/{team_uuid}/online_template/{online_templates_uuid}/publish'
    name = '更新协同wiki模版'
    api_type = 'POST'


class PagesHistory(WikiOps):
    uri = '/team/{team_uuid}/page/{page_uuid}/history'
    name = '查看页面历史版本'
    api_type = 'GET'


class TemplatesList(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/templates'
    name = '模版列表'
    api_type = 'GET'


class UpdateTemplate(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/template/{template_uuid}/update'
    name = '更新模版信息'
    api_type = 'POST'


class UpdateSpaceInfo(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/update'
    name = '更新wiki页面组信息'
    api_type = 'POST'


class GlobalTemplate(WikiOps):
    uri = '/team/{team_uuid}/templates/add'
    name = '添加到全局模版'
    api_type = 'POST'


class DelGlobalTemplate(WikiOps):
    uri = '/team/{team_uuid}/template/{global_uuid}/delete'
    name = '删除全局模版'
    api_type = 'POST'


class UpdateGlobalTemplate(WikiOps):
    uri = '/team/{team_uuid}/template/{global_uuid}/update'
    name = '更新编辑全局模版'
    api_type = 'POST'


class DeletedPages(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/deleted_pages'
    name = '查看回收站'
    api_type = 'GET'


class DeleteDPagesDelete(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/deleted_page/{page_uuid}/delete'
    name = '回收站彻底删除'
    api_type = 'POST'


class PagesRestore(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/deleted_page/{page_uuid}/restore'
    name = '回收站 放回原处'
    api_type = 'POST'


class DeletePagesAll(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/delete_all_pages'
    name = '清空回收站'
    api_type = 'POST'


class UpdateWikiPage(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/page/{page_uuid}/update'
    name = '更新WIKI页面'
    api_type = 'POST'


class WikiRevert(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/page/{page_uuid}/revert'
    name = '回滚版本'
    api_type = 'POST'


class TaskAddWikiPages(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/add_wiki_page'
    name = '任务内新增wiki'
    api_type = 'POST'


class TaskAddOnlineWikiPages(WikiOps):
    uri = '/team/{team_uuid}/online_pages/add'
    name = '任务内新增wiki协同页'
    api_type = 'POST'


class TaskWordImport(WikiOps):
    uri = '/team/{team_uuid}/word/import'
    name = '导入word文档'
    api_type = 'POST'


class WikiTeamSearch(WikiOps):
    """团队搜索"""
    uri = '/team/{team_uuid}/search'
    name = '团队搜索'
    api_type = 'GET'


class WikiNoticeConfig(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/notice_config'
    name = '获取wiki页面组通知配置'
    api_type = 'GET'


class UpdateWikiNoticeConfig(WikiOps):
    uri = '/team/{team_uuid}/space/{space_uuid}/notice_config/{notice_config_uuid}/update'
    name = '更新wiki页面组通知配置'
    api_type = 'POST'


class GlobalTemplateList(WikiOps):
    uri = '/team/{team_uuid}/templates'
    name = 'wiki全局模版列表'
    api_type = 'GET'
