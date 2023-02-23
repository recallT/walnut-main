# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_wiki_space.py
@Author  ：zhangyonghui@ones.ai
@Date    ：2022/6/10 3:51 PM 
@Desc    ：ONES Wiki 页面组管理
"""
from falcons.check import Checker
from falcons.com.nick import feature, story, step, fixture
from falcons.helper import mocks
from falcons.ops import generate_param

from main.actions.wiki import WikiAction as wa
from main.api.wiki import DelGlobalTemplate, AddWikiPages, UpdateWikiPage, SpaceTemplates, PagesHistory, WikiRevert, \
    PublishOnlineTemplate
from main.params import wiki
from main.params.wiki import wiki_param


@fixture(scope='module', autouse=True)
def add_space():
    """新增WIKI页面组"""

    space_uuid = wa.add_wiki_space().value('uuid')
    return space_uuid


@fixture(scope='module', autouse=True)
def del_wiki(add_space):
    """删除WIKI页面组"""
    yield
    wa.del_wiki_space(add_space)


@feature('Wiki-页面组管理')
class TestWikiSpaces(Checker):

    @story('T24289 新建wiki页面组')
    def test_add_wiki_space(self):
        with step('新建页面组'):
            space_uuid = wa.add_wiki_space().value('uuid')

            # 清除数据
            wa.del_wiki_space(space_uuid)

    @story('T146584 新建模板：入口（只开启了「Wiki 协同页面」）」')
    def test_add_online_template_space(self, add_space):
        with step('点击按钮：新建Wiki 协同页面模板'):
            template_uuid = wa.add_online_template_space(add_space).value('uuid')

        with step('进入页面组模版列表页面'):
            resp_template = wa.template_list(add_space).value('templates')

        assert template_uuid in [uuid['uuid'] for uuid in resp_template]

    @story('T146588 编辑模板：编辑「Wiki 协同页面」')
    def test_update_online_template_space(self, add_space):
        with step('点击按钮：新建Wiki 协同页面模板'):
            template_uuid = wa.add_online_template_space(add_space).value('uuid')
        with step('更新模版'):
            param = generate_param({
                "title": "update_title" + mocks.num()
            })[0]
            param.uri_args({'online_templates_uuid': template_uuid})
            resp = self.call(PublishOnlineTemplate, param)
            resp.check_response('code', 200)

    @story('T24223 页面组-新建页面模版')
    def test_add_space_template(self, add_space):
        with step('进入页面组，新建页面模版'):
            template_uuid = wa.add_template_space(add_space).value('uuid')
        with step('进入页面组模版列表页面'):
            resp_template = wa.template_list(add_space).value('templates')

            assert template_uuid in [uuid['uuid'] for uuid in resp_template]

    @story('T24266 页面组-编辑页面组模版')
    def test_update_template(self, add_space):
        with step('前置条件，创建一个模版'):
            template_uuid = wa.add_template_space(add_space).value('uuid')
        with step('更新模版信息'):
            wa.update_template(add_space, template_uuid)

    @story('T24250 页面-页面组模版-设置全局模版')
    def test_set_global_template(self, add_space):
        with step('前置条件，创建一个模版'):
            template_uuid = wa.add_template_space(add_space).value('uuid')

        with step('设置为全局模版'):
            global_uuid = wa.add_global_template(template_id=template_uuid)

    @story('T24234 页面组模版管理：删除页面全局模版')
    def test_del_global_template(self, add_space):
        with step('前置条件，创建一个模版'):
            template_uuid = wa.add_template_space(add_space).value('uuid')

        with step('设置为全局模版'):
            global_uuid = wa.add_global_template(template_id=template_uuid)

        with step('删除全局模版'):
            param = wiki_param()[0]
            param.uri_args({'global_uuid': global_uuid})
            resp = self.call(DelGlobalTemplate, param)
            resp.check_response('code', 200)

    @story('T24242 页面组管理：查看页面组回收站')
    def test_check_space_recycle_bin(self, add_space):
        with step('查看页面组回收站'):
            wa.deleted_pages(add_space)

    @story('T24306 页面组管理：开启页面组共享')
    def test_add_space_open_share_pages(self):
        with step('新建页面组 开启页面组共享'):
            # is_open_share_page 是否开启共享
            space_uuid = wa.add_wiki_space(is_open_share_page=True).value('uuid')
            # 清除数据
            wa.del_wiki_space(space_uuid)

    @story('T24309 页面组管理：关闭页面组共享')
    def test_add_space_close_share_pages(self):
        with step('新建页面组 关闭页面组共享'):
            # is_open_share_page 是否开启共享
            space_uuid = wa.add_wiki_space(is_open_share_page=False).value('uuid')
            # 清除数据
            wa.del_wiki_space(space_uuid)

    @story('T24278 页面组管理：从回收站彻底删除无层级的页面（页面树-主页下页面）')
    def test_del_pages(self, add_space):
        with step('前置条件：删除一个页面'):
            resp_pages = wa.deploy_wiki_pages(add_space)
            pages_uuid = resp_pages.value('page_uuid')
            wa.del_wiki_pages(add_space, pages_uuid)
        with step('点击彻底删除'):
            wa.delete_pages_delete(add_space, pages_uuid)
            resp = wa.deleted_pages(add_space)
            uuid_list = [uuid['uuid'] for uuid in resp.value('pages')]
            assert pages_uuid not in uuid_list

    @story('T24268 页面组管理：从回收站恢复无层级的页面（页面树-主页下页面）')
    def test_pages_restore(self, add_space):
        with step('前置条件：删除一个页面'):
            resp_pages = wa.deploy_wiki_pages(add_space)
            pages_uuid = resp_pages.value('page_uuid')
            wa.del_wiki_pages(add_space, pages_uuid)
        with step('放回原处'):
            wa.delete_pages_restore(add_space, pages_uuid)
            resp = wa.deleted_pages(add_space)
            uuid_list = [uuid['uuid'] for uuid in resp.value('pages')]
            assert pages_uuid not in uuid_list

    @story('T24302 页面组管理：更新页面组描述')
    def test_update_space_desc(self, add_space):
        space_uuid = wa.add_wiki_space().value('uuid')
        with step('更新页面组描述'):
            param = {
                "title": "页面组" + mocks.num(),
                "description": "description-description",
                "is_open_share_page": False,
                "space_category_uuid": ""
            }
            wa.update_space(space_uuid, param)

            wa.del_wiki_space(space_uuid)

    @story('T24301 页面组管理：更新页面组名称')
    def test_update_space_name(self):
        space_uuid = wa.add_wiki_space().value('uuid')
        with step('更新页面组名称'):
            param = {
                "title": "update_页面组" + mocks.num(),
                "description": "",
                "is_open_share_page": False,
                "space_category_uuid": ""
            }
            wa.update_space(space_uuid, param)

            wa.del_wiki_space(space_uuid)

    @story('T24290 页面组管理：清空回收站')
    def test_empty_recycle_bin(self, add_space):
        with step('前置条件，删除一个页面'):
            resp_pages = wa.deploy_wiki_pages(add_space)
            pages_uuid = resp_pages.value('page_uuid')
            wa.del_wiki_pages(add_space, pages_uuid)
        with step('点击清空回收站按钮'):
            wa.delete_pages_all(add_space)
            resp = wa.deleted_pages(add_space)
            uuid_list = [uuid['uuid'] for uuid in resp.value('pages')]
            assert pages_uuid not in uuid_list

    @story('T151742 页面组权限-编辑内容：复制页面')
    def test_copy_space(self, add_space):
        resp_pages = wa.deploy_wiki_pages(add_space)
        pages_uuid = resp_pages.value('page_uuid')
        with step('点击复制页面'):
            param = wiki.copy_pages(pages_uuid, pages_uuid)[0]
            param.uri_args({'space_uuid': add_space})
            resp = self.call(AddWikiPages, param)
            resp.check_response('page_uuid', pages_uuid)

    @story('T151741 页面组权限-编辑内容：共享页面')
    def test_share_space(self):
        ...

    @story('T151741 页面组权限-编辑内容：移动页面')
    def test_move_space(self, add_space):
        with step('前置条件 新建一个页面组'):
            space_uuid = wa.add_wiki_space().value('uuid')
            resp_pages = wa.deploy_wiki_pages(add_space)
            pages_uuid = resp_pages.value('page_uuid')
            parent_uuid = wa.get_space_pages(space_uuid).value('pages[0].uuid')
        with step('移动页面'):
            param = wiki.move_wiki_page(space_uuid, parent_uuid)[0]
            param.uri_args({'space_uuid': add_space, 'page_uuid': pages_uuid})
            resp = self.call(UpdateWikiPage, param)
            resp.check_response('code', 200)
        # 清除新建页面组数据
        wa.del_wiki_space(space_uuid)

    @story('T151739 页面组权限-编辑内容：回滚到此版本')
    def test_revert_space(self, add_space):
        resp_pages = wa.deploy_wiki_pages(add_space)
        pages_uuid = resp_pages.value('page_uuid')
        # 更新一次wiki
        wa.update_wiki_pages(add_space, pages_uuid)
        with step('查看历史版本，回滚'):
            param = wiki.wiki_param()[0]
            param.uri_args({'page_uuid': pages_uuid})
            history_version = self.call(PagesHistory, param).value('history[1].version')
            # 回滚到第一个版本
            version_param = generate_param({'version': history_version})[0]
            version_param.uri_args({'space_uuid': add_space, 'page_uuid': pages_uuid})

            resp_revert = self.call(WikiRevert, version_param)
            resp_revert.check_response('code', 200)

    @story('T151727 页面组权限-编辑内容：编辑页面')
    def test_update_wiki_info(self, add_space):
        with step('A有权限编辑页面'):
            resp_pages = wa.deploy_wiki_pages(add_space)
            pages_uuid = resp_pages.value('page_uuid')
            # 更新wiki
            wa.update_wiki_pages(add_space, pages_uuid)
        with step('B 无权限更新'):  # todo
            pass

    @story('T151731 页面组权限-编辑内容：删除页面')
    def test_del_space_pages(self):
        with step('前置条件'):
            space_uuid = wa.add_wiki_space().value('uuid')
            resp_pages = wa.deploy_wiki_pages(space_uuid)
            pages_uuid = resp_pages.value('page_uuid')
        with step('删除页面'):
            wa.del_wiki_pages(space_uuid, pages_uuid)
            # 查看回收站
            resp = wa.deleted_pages(space_uuid)
            uuid_list = [uuid['uuid'] for uuid in resp.value('pages')]
            assert pages_uuid in uuid_list
            wa.del_wiki_space(space_uuid)

    @story('T151734页面组权限-编辑内容：添加到页面组模板')
    def test_add_spaces_templates(self, add_space):
        resp_pages = wa.deploy_wiki_pages(add_space)
        pages_uuid = resp_pages.value('page_uuid')
        with step('添加到页面组模板'):
            param = wiki.page_add_template(pages_uuid)[0]
            param.uri_args({'space_uuid': add_space})
            resp = self.call(SpaceTemplates, param)
            resp.check_response('space_uuid', add_space)

    @story('T24541 页面组权限-编辑内容：新建页面')
    def test_add_new_pages(self, add_space):
        resp_pages = wa.deploy_wiki_pages(add_space)
        with step('无新建权限用户新建'):
            # todo:
            pass

    @story('T151752 页面组权限-编辑内容：页面组模板')
    def test_update_spaces_templates(self):
        ...

    @story('T151746 页面组权限-管理页面组：回收站')
    def test_check_delete_pages(self, add_space):
        with step('查看页面组回收站'):
            wa.deleted_pages(add_space)
