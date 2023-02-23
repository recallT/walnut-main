from falcons.check import go

from main.api import wiki as wk
from main.api.project import ItemGraphql
from main.params import wiki


class WikiAction:
    """wiki 公共方法"""

    @classmethod
    def add_page_classification(cls, token=None):
        """
        新增页面组分类
        :param token:
        :return:
        """

        param = wiki.add_page_classification()[0]

        resp_uuid = go(ItemGraphql, param, token).value('data.addSpaceCategory.key').split('-')[2]
        return resp_uuid

    @classmethod
    def add_wiki_space(cls, is_open_share_page=False, token=None):
        """
        新增wiki页面组
        :param is_open_share_page: 是否打开共享页面组
        :param token:
        :return:
        """
        param = wiki.add_wiki_space(is_open_share_page)[0]
        resp = go(wk.AddWikiSpaces, param, token)
        space_uuid = resp.value('uuid')
        # 关闭页面组通知
        notice_config_uuid = cls.get_wiki_notice_config(space_uuid)
        cls.update_wiki_notice_config(methods=[], space_uuid=space_uuid, notice_config_uuid=notice_config_uuid)
        return resp

    @classmethod
    def del_wiki_space(cls, space_uuid, token=None):
        """
        删除wiki页面组
        :param space_uuid: 页面组UUId
        :param token:
        :return:
        """
        param = wiki.wiki_param()[0]
        param.uri_args({'space_uuid': space_uuid})
        resp = go(wk.DelWikiSpace, param, token)
        return resp

    @classmethod
    def add_wiki_pages(cls, space_uuid, token=None):
        """
        新增wiki页面
        :param space_uuid: 页面组UUId
        :param token:
        :return:
        """
        param = wiki.add_wiki_pages()[0]
        param.uri_args({'space_uuid': space_uuid})
        return go(wk.AddWikiPages, param, token)

    @classmethod
    def deploy_wiki_pages(cls, space_uuid, token=None):
        #
        """
        新增 wiki页面并发布
        :param space_uuid: 页面组UUId
        :param token:
        :return:
        """
        resp = cls.add_wiki_pages(space_uuid)
        pages_uuid = resp.value('page_uuid')
        uuid = resp.value('uuid')

        # 发布页面
        param = wiki.deploy_wiki_pages(space_uuid, pages_uuid, uuid)[0]
        param.uri_args({'space_uuid': space_uuid, 'uuid': uuid})
        return go(wk.DeployWikiPages, param, token)

    @classmethod
    def update_wiki_pages(cls, space_uuid, page_uuid, token=None):
        """
        更新wiki 页面
        :param space_uuid: 页面组UUID
        :param page_uuid: 页面UUID
        :param token:
        :return:
        """
        # add
        param = wiki.update_wiki_pages(page_uuid)[0]
        param.uri_args({'space_uuid': space_uuid})
        resp = go(wk.AddWikiPages, param, token)
        uuid = resp.value('uuid')

        # deploy 发布
        deploy_param = wiki.update_deploy_wiki_pages(space_uuid, page_uuid, uuid)[0]
        deploy_param.uri_args({'space_uuid': space_uuid, 'uuid': uuid})
        return go(wk.DeployWikiPages, deploy_param, token)

    @classmethod
    def del_wiki_pages(cls, space_uuid, pages_uid, token=None):
        """
        删除wiki页面
        :param space_uuid: 页面组uuid
        :param pages_uid: 页面uuid
        :param token:
        :return:
        """
        param = wiki.wiki_param()[0]
        param.uri_args({'space_uuid': space_uuid, 'page_uuid': pages_uid})
        return go(wk.DelWikiPages, param, token)

    @classmethod
    def get_space_pages(cls, space_uuid, token=None):
        """
        查询页面组下wiki页面数据
        :param space_uuid: 页面组UUID
        :param token:
        :return:
        """
        param = wiki.wiki_param()[0]
        param.uri_args({'space_uuid': space_uuid})
        return go(wk.WikiPages, param, token)

    @classmethod
    def add_template_space(cls, space_uuid, token=None):
        """
        添加wiki 页面 模版
        :param space_uuid: 页面组UUID
        :param token:
        :return:
        """
        param = wiki.add_template_space()[0]
        param.uri_args({'space_uuid': space_uuid})
        return go(wk.SpaceTemplates, param, token)

    @classmethod
    def add_online_template_space(cls, space_uuid, token=None):
        """
        添加wiki协同 页面 模版
        :param space_uuid: 页面组UUID
        :param token:
        :return:
        """
        param = wiki.add_joint_template_space(space_uuid)[0]
        return go(wk.SpaceOnlineTemplates, param, token)

    @classmethod
    def template_list(cls, space_uuid, token=None):
        """
        页面组 模版列表
        :param space_uuid: 页面组UUID
        :param token:
        :return:
        """
        param = wiki.wiki_param()[0]
        param.uri_args({'space_uuid': space_uuid})
        return go(wk.TemplatesList, param, token)

    @classmethod
    def update_space(cls, space_uuid, data: dict, token=None):
        """
        更新页面组信息
        :param space_uuid: 页面组UUID
        :param data: 请求参数字典
        data = {
                "title": "update_页面组" + mocks.num(),
                "description": "",
                "is_open_share_page": False,
                "space_category_uuid": ""
            }
        :param token:
        :return:
        """
        param = wiki.update_space_info(data['title'], data['description'], data['is_open_share_page'],
                                       data['space_category_uuid'])[0]
        param.uri_args({'space_uuid': space_uuid})
        resp = go(wk.UpdateSpaceInfo, param, token)
        resp.check_response('code', 200)

    @classmethod
    def update_template(cls, space_uuid, template_uuid, token=None):
        """
        更新页面组模版信息
        :param space_uuid: 页面组UUID
        :param template_uuid: 页面组模版UUID
        :param token:
        :return:
        """

        param = wiki.add_template_space()[0]
        param.uri_args({'space_uuid': space_uuid, 'template_uuid': template_uuid})
        resp = go(wk.UpdateTemplate, param, token)
        resp.check_response('code', 200)

    @classmethod
    def add_global_template(cls, template_id, token=None):
        """
        设置页面组为全局模版
        :param template_id: 模版id
        :param token:
        :return:
        """
        param = wiki.add_global_template(template_id=template_id)[0]
        global_uuid = go(wk.GlobalTemplate, param, token).value('uuid')
        return global_uuid

    @classmethod
    def deleted_pages(cls, space_uuid, token=None):
        """
        回收站列表
        :param space_uuid: 页面组UUID
        :param token:
        :return:
        """
        param = wiki.wiki_param()[0]
        param.uri_args({'space_uuid': space_uuid})
        return go(wk.DeletedPages, param, token)

    @classmethod
    def delete_pages_delete(cls, space_uuid, page_uuid, token=None):
        """
        回收站彻底删除
        :param space_uuid: 页面组uuid
        :param page_uuid: 页面uuid
        :param token:
        :return:
        """
        param = wiki.wiki_param()[0]

        param.uri_args({'space_uuid': space_uuid, 'page_uuid': page_uuid})
        return go(wk.DeleteDPagesDelete, param, token)

    @classmethod
    def delete_pages_restore(cls, space_uuid, page_uuid, token=None):
        """
        回收站放回原处
        :param space_uuid: 页面组uuid
        :param page_uuid: 页面uuid
        :param token:
        :return:
        """
        param = wiki.pages_restore()[0]
        param.uri_args({'space_uuid': space_uuid, 'page_uuid': page_uuid})
        resp = go(wk.PagesRestore, param, token)
        resp.check_response('code', 200)

    @classmethod
    def delete_pages_all(cls, space_uuid, token=None):
        """
        清空回收站
        :param space_uuid: 页面组uuid
        :param token:
        :return:
        """
        param = wiki.wiki_param()[0]
        param.uri_args({'space_uuid': space_uuid})
        resp = go(wk.DeletePagesAll, param, token)
        resp.check_response('code', 200)

    @classmethod
    def get_wiki_notice_config(cls, space_uuid):
        """
        获取页面组通知配置
        :param space_uuid:
        :return:notice_config_uuid
        """
        param = wiki.wiki_param()[0]
        param.uri_args({'space_uuid': space_uuid})
        resp = go(wk.WikiNoticeConfig, param)
        return resp.value('uuid')

    @classmethod
    def update_wiki_notice_config(cls, methods: list, space_uuid, notice_config_uuid):
        """
        更新页面组通知
        :param methods: 通知方式 [1,2]
        :param space_uuid: 页面组UUID
        :param notice_config_uuid: 通知配置UUID
        :return:
        """
        param = wiki.wiki_param()[0]
        param.json_update('methods', methods)
        param.uri_args({'space_uuid': space_uuid, 'notice_config_uuid': notice_config_uuid})
        go(wk.UpdateWikiNoticeConfig, param)

    @classmethod
    def add_global_wiki_template(cls):
        """
        WIKI配置中心-新建wiki页面模版
        :return:template_uuid
        """
        param = wiki.add_template_space()[0]
        template_uuid = go(wk.GlobalTemplate, param).value('uuid')
        return template_uuid

    @classmethod
    def update_global_wiki_template(cls, global_uuid):
        """
        WIKI配置中心-编辑wiki页面模版
        :param global_uuid: 全局模版UUID
        :return:
        """
        param = wiki.add_template_space()[0]
        param.uri_args({'global_uuid': global_uuid})
        resp = go(wk.UpdateGlobalTemplate, param)
        resp.check_response('code', 200)

    @classmethod
    def del_global_template(cls, global_uuid):
        """
        删除WIKI全局模版
        :param global_uuid: 全局模版UUID
        :return:
        """
        param = wiki.wiki_param()[0]
        param.uri_args({'global_uuid': global_uuid})
        resp = go(wk.DelGlobalTemplate, param)
        resp.check_response('code', 200)

    @classmethod
    def add_collaborate_wiki_global_template(cls):
        """
        WIKI配置中心-新建协同wiki页面模版
        :return:template_uuid
        """
        param = wiki.add_collaborate_wiki_global_template()[0]
        template_uuid = go(wk.SpaceOnlineTemplates, param).value('uuid')
        return template_uuid

    @classmethod
    def wiki_global_template_list(cls):
        """
        查询配置中心-wiki全局模版列表
        :return:
        """
        param = wiki.wiki_param()[0]
        resp = go(wk.GlobalTemplateList, param)
        return resp
