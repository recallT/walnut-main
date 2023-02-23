"""
@File    ：test_group_proj_list
@Author  ：xiechunwei
@Date    ：2022/8/1 18:46
@Desc    ：项目列表-分组
"""


from falcons.com.nick import feature, story, parametrize, fixture, step
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


@feature('项目列表-分组')
class TestGroupProjList(Checker):

    @story('137995 按项目创建者分组')
    @story('137997 按项目名称分组')
    @story('137998 按项目状态分组')
    @story('137999 按状态类型分组')
    @story('138005 检查不同布局下的分组')
    @parametrize('param', graphql.proj_group())
    def test_proj_group(self, param):
        resp = self.call(proj.ItemGraphql, param)

        assert len(resp.value('data.buckets')) > 0

    @story('138000 按自定义单行文本分组')
    @story('138002 按自定义单选成员分组')
    @story('138001 按自定义单选菜单分组')
    @parametrize('types', ['text', 'user'])
    def test_proj_customize_field_group(self, types, _field_store):
        with step('前提条件：创建自定义项目属性'):
            parm = conf.add_field(types)[0]
            resp = self.call(proj.ItemsAdd, parm)

            aliases_uuid = resp.value('item.aliases[0]')
            aliases_key = resp.value('item.key')

            _field_store.append(aliases_key)

        with step('按自定义属性分组'):
            if types == 'user':
                param = graphql.proj_group({f"_{aliases_uuid}": '{\n      uuid\n      name\n    }\n '})
            else:
                param = graphql.proj_group({f"_{aliases_uuid}": ''})

            self.call(proj.ItemGraphql, param[0])

    @story('138004 点击关闭分组')
    def test_close_proj_group(self):
        param = graphql.proj_table_view()[0]
        resp = self.call(proj.ItemGraphql, param, is_print=False)

        key = [k['key'] for k in resp.value('data.buckets')]
        assert 'bucket.0.__all' in key


