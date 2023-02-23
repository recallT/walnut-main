"""
@File    ：test_proj_layout
@Author  ：xiechunwei
@Date    ：2022/8/2 18:29
@Desc    ：项目列表-布局/置顶
"""

from falcons.com.nick import feature, story, parametrize, step, fixture
from main.api import project as p
from main.params import graphql, conf, proj
from falcons.check import Checker, go
from falcons.helper import mocks
from main.params.const import ACCOUNT


@feature('项目列表-表格布局')
class TestProjTableLayout(Checker):

    def edit_table_layout(self, filed_type, value):
        param = proj.proj_list_edit(filed_type, value)[0]
        param.uri_args({'item_key': f'project-{ACCOUNT.project_uuid}'})
        resp = self.call(p.ItemUpdate, param)

        resp.check_response('item.item_type', 'project')

    @story('137967 表格即时编辑：编辑计划结束日期')
    def test_table_edit_plan_end_time(self):
        value = mocks.day_timestamp(week=3)

        self.edit_table_layout('plan_end_time', value)

    @story('137968 编辑计划开始日期')
    def test_table_edit_plan_start_time(self):
        value = mocks.now_timestamp()

        self.edit_table_layout('plan_start_time', value)

    @story('137969 编辑项目负责人')
    def test_table_edit_proj_assign(self):
        self.edit_table_layout('assign', ACCOUNT.user.owner_uuid)

    @story('137970 编辑项目名称')
    def test_table_edit_proj_name(self):
        uid = mocks.ones_uuid().capitalize()

        self.edit_table_layout('name', f'ApiTest{uid[:4]}')

    @story('137972 编辑自定义单行文本')
    @story('137973 编辑自定义单选菜单')
    @story('137974 编辑自定义单选成员')
    @story('137975 编辑自定义多行文本')
    @story('137976 编辑自定义多选菜单')
    @story('137977 编辑自定义多选成员')
    @story('137978 编辑自定义浮点数')
    @story('137979 编辑自定义日期')
    @story('137980 编辑自定义时间')
    @story('137981 编辑自定义整数')
    @parametrize('types', ['text', 'user', 'multi_line_text', 'user_list', 'float', 'date', 'time', 'integer'])
    def test_table_edit_customize_filed(self, types):
        with step('前提条件：创建自定义项目属性'):
            parm = conf.add_field(types)[0]
            resp = self.call(p.ItemsAdd, parm)

            aliases_key = resp.value('item.key')

        with step('编辑自定义属性'):
            ...

        with step('删除属性'):
            param = conf.add_options()[0]
            param.uri_args({'item_key': aliases_key})
            self.call(p.ItemDelete, param, with_json=False)

    @story('137983 项目列表-表格布局-选择表头显示内容弹框：保存表头显示内容修改值后操作恢复默认值')
    def test_table_restore_defaults(self):
        param = graphql.proj_table_view()[0]
        resp = self.call(p.ItemGraphql, param, is_print=False)

        key = [k['key'] for k in resp.value('data.buckets')]
        assert 'bucket.0.__all' in key


@feature('项目列表-置顶')
class TestProjPin(Checker):

    @story('23670 项目置顶')
    def test_proj_pin(self):
        param = proj.proj_pin_or_unpin()[0]
        self.call(p.PinProject, param)

    @story('138255 取消置顶')
    def test_proj_unpin(self):
        param = proj.proj_pin_or_unpin()[0]
        self.call(p.UnpinProject, param)

    @story('138253 检查不同布局下置顶项目')
    def test_different_layouts_pin_proj(self):
        with step('138253 布局选择：卡片'):
            param = graphql.proj_card_view()[0]
            self.call(p.ItemGraphql, param)

        with step('操作项目置顶'):
            """与23670一样"""
