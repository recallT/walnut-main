"""
@File    ：document
@Author  ：zhangyonghui
@Email   ：zhangyonghui@ones.ai
@Date    ：2022/5/31
@Desc    ：文档
"""

from falcons.check import Checker
from falcons.com.meta import ApiMeta
from falcons.com.nick import story, fixture, step, feature, mark

from main.actions.relation import RelationAction
from main.actions.wiki import WikiAction as wa
from main.api.wiki import WikiSpaces
from main.params.proj import proj_url


@fixture(scope='module', autouse=True)
def add_wiki():
    """新增WIKI页面组 wiki页面"""
    space_uuid = wa.add_wiki_space().value('uuid')
    resp_pages = wa.deploy_wiki_pages(space_uuid)
    pages_uuid = resp_pages.value('page_uuid')

    # 获取页面组下的所有页面uuid
    resp = wa.get_space_pages(space_uuid)
    uuid_list = []
    for uuid in resp.value('pages'):
        uuid_list.append(uuid['uuid'])
    data = {'space_uuid': space_uuid, 'page_uuid': pages_uuid, 'uuid_list': uuid_list}

    return data


@fixture(scope='module', autouse=True)
def del_wiki(add_wiki):
    """删除WIKI页面组"""
    yield
    wa.del_wiki_space(add_wiki['space_uuid'])


@mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过')
@feature('文档管理')
class TestProjDocument(Checker):

    @story('T143513 关联wiki-新建页面组：在关联wiki弹窗正确新建页面组')
    def test_add_new_space(self):
        with step('点击「新建页面组」'):
            space_uuid = wa.add_wiki_space().value('uuid')
        with step('页面组列表处选中新建的页面组'):
            param = proj_url()[0]
            resp_spaces = self.call(WikiSpaces, param).value('spaces')
            uuid_list = []
            for uuid in resp_spaces:
                uuid_list.append(uuid['uuid'])
            # 判断新增的页面组uuid 存在页面组列表中
            assert space_uuid in uuid_list
            wa.del_wiki_space(space_uuid)

    @story('T143515 关联wiki-关联页面组：关联页面组')
    def test_relation_document_wiki_pages(self, add_wiki):
        with step('关联页面组'):
            RelationAction.relation_document_wiki(bind=add_wiki['uuid_list'])
        with step('解除页面关联'):
            RelationAction.relation_document_wiki(unbind=add_wiki['uuid_list'])

    @story('T143519 关联wiki-选择页面：在关联wiki弹窗中选择关联页面')
    def test_relation_wiki_sub_page(self, add_wiki):
        with step('关联页面组的父节点'):
            # 勾选父节点 主页 该页面组所有的页面默认都被关联
            RelationAction.relation_document_wiki(bind=[add_wiki['uuid_list'][0]])
        with step('解除页面关联'):
            RelationAction.relation_document_wiki(unbind=[add_wiki['uuid_list'][0]])

    @story('T143522 关联wiki-支持关联预览：检查已选页面组预览')
    def test_wiki_space_view(self):
        with step('页面组预览'):
            # 查询所有页面组数据
            param = proj_url()[0]
            self.call(WikiSpaces, param).value('spaces')

    @story('T143521 关联wiki-自动同步子节点：文档组件自动同步已关联的页面下的子页面')
    def test_rel_wiki_auto_sync(self, add_wiki):
        with step('前置条件，文档组件已关联页面组A'):
            RelationAction.relation_document_wiki(bind=[add_wiki['uuid_list'][0]])
        with step('在页面组A下创建一个wiki页面'):
            resp_pages_uuid = wa.deploy_wiki_pages(add_wiki['space_uuid']).value('page_uuid')
        with step('查看文档同步情况'):
            resp = RelationAction.get_rel_wiki_info().value('spaces.%s.pages' % add_wiki['space_uuid'])
            uuid_list = []
            for uuid in resp:
                uuid_list.append(uuid['uuid'])
            assert resp_pages_uuid in uuid_list
            RelationAction.relation_document_wiki(unbind=[add_wiki['uuid_list'][0]])

    @story('T143517 文档-关联信息：检查关联页面信息')
    def test_check_document_rel_wiki_page_info(self, add_wiki):
        with step('前置条件，文档组件已关联页面组A'):
            RelationAction.relation_document_wiki(bind=[add_wiki['uuid_list'][0]])
        with step('查询文档关联wiki页面信息'):
            resp = RelationAction.get_rel_wiki_info().value('spaces.%s.pages' % add_wiki['space_uuid'])
            uuid_list = []
            for uuid in resp:
                uuid_list.append(uuid['uuid'])
            assert add_wiki['page_uuid'] in uuid_list
            RelationAction.relation_document_wiki(unbind=[add_wiki['uuid_list'][0]])

    @story('T143520 文档组件：移除关联页面组')
    def test_del_relation_wiki_space(self, add_wiki):
        with step('关联页面组'):
            RelationAction.relation_document_wiki(bind=add_wiki['uuid_list'])
        with step('解除页面关联'):
            RelationAction.relation_document_wiki(unbind=add_wiki['uuid_list'])

    @story('T143516 文档组件：在关联wiki弹窗搜索页面')
    def test_search_wiki_pages(self):
        param = proj_url()[0]
        resp_spaces = self.call(WikiSpaces, param).value('spaces')
        space_uuid = [sp['uuid'] for sp in resp_spaces if sp['title'] == '示例知识库']

        resp = wa.get_space_pages(space_uuid[0]).value('pages')
        title_list = [title['title'] for title in resp]
        with step('根据页面名称搜索页面'):
            assert '主页' in title_list
        with step('搜索不存在的页面'):
            assert 'xxxxxxxxx' not in title_list

    @story('T146659 新建页面：只开启「Wiki 页面」')
    def test_add_wiki_pages(self, add_wiki):
        with step('点击新建页面'):
            wa.deploy_wiki_pages(add_wiki['space_uuid'])

    @story('T146658 新建页面：只开启「Wiki 协同页面」')
    def test_add_online_wiki_pages(self):
        ...
