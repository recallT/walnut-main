"""
@File    ：sort_list
@Author  ：xiechunwei
@Date    ：2022/7/31 15:58
@Desc    ：项目列表-列表排序
"""

from falcons.com.nick import feature, story, parametrize, step, fixture
from main.api import project as proj
from main.params import graphql, conf
from falcons.check import Checker, go


@fixture(scope='module')
def _field_store():
    """
    主要是记录key 用于清理测试数据
    :return:
    """
    return []


@fixture(scope='module', autouse=True)
def delete_proj_field(_field_store):
    """删除项目属性"""

    yield

    if _field_store:
        p = conf.add_options()[0]

        for field in _field_store:
            p.uri_args({'item_key': field})
            go(proj.ItemDelete, p, with_json=False)


@feature('项目列表-排序')
class TestProjListSort(Checker):

    @story('23633 项目列表-排序正序倒序检查')
    @story('23627 项目列表-属性排序')
    @story('138226 项目列表排序：按成员数量排序')
    @story('138227 项目列表排序：按创建时间排序')
    @story('138228 项目列表排序：按迭代数量排序')
    @story('138229 项目列表排序：按工作项数量排序')
    @story('138230 项目列表排序：按工作项完成度排序')
    @story('138230 项目列表排序：按工作项完成度排序')
    @story('138231 项目列表排序：按计划结束日期排序')
    @story('138232 项目列表排序：按计划开始日期排序')
    @story('138233 项目列表排序：按进行中工作项数量排序')
    @story('138234 项目列表排序：按未开始工作项数量排序')
    @story('138235 项目列表排序：按项目创建者排序')
    @story('138236 项目列表排序：按项目负责人排序')
    @story('138237 项目列表排序：按项目名称排序')
    @story('138240 项目列表排序：按状态类型排序')
    @story('138239 项目列表排序：按已完成工作项数量排序')
    @parametrize('param', graphql.proj_sort())
    def test_proj_list_sort(self, param):

        self.call(proj.ItemGraphql, param)

    @story('138241 项目列表排序：按自定义单选菜单属性排序')
    def test_proj_list_radio_menu_sort(self, _field_store):
        with step('前提条件：创建 自定义菜单 项目属性'):
            parm = conf.add_options()[0]
            resp = self.call(proj.ItemsAdd, parm)

            aliases_uuid = resp.value('item.aliases[0]')
            aliases_key = resp.value('item.key')

            _field_store.append(aliases_key)

        with step('按自定义单选菜单属性排序'):
            param = graphql.proj_sort(aliases_uuid)

            self.call(proj.ItemGraphql, param[0])

    @story('138242 项目列表排序：按自定义单选成员属性排序')
    @story('138243 项目列表排序：按自定义浮点数属性排序')
    @story('138244 项目列表排序：按自定义日期属性排序')
    @story('138245 项目列表排序：按自定义时间属性排序')
    @story('138246 项目列表排序：按自定义整数属性排序')
    @story('138247 项目列表排序：检查检查不同布局下项目列表排序')
    @parametrize('types', ['user', 'float', 'date', 'time', 'integer'])
    def test_proj_list_customize_sort(self, types, _field_store):
        with step('前提条件：创建自定义项目属性'):
            parm = conf.add_field(types)[0]
            resp = self.call(proj.ItemsAdd, parm)

            aliases_uuid = resp.value('item.aliases[0]')
            aliases_key = resp.value('item.key')

            _field_store.append(aliases_key)

        with step('按自定义属性排序'):
            param = graphql.proj_sort(aliases_uuid)

            self.call(proj.ItemGraphql, param[0])






