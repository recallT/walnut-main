"""
@Desc：全局配置-视图配置-详情表单
"""
from falcons.check import Checker
from falcons.com.nick import feature, story, step, parametrize, mark

from main.actions.task import TaskAction
from main.api import project as prj, layout as lay
from main.params import conf


@mark.smoke
@feature('视图布局配置开箱')
class TestLayoutUnpack(Checker):

    def layout_detail(self, issue_type: str):
        """视图布局详情"""

        # 获取工作项uuid
        issue_uuid = TaskAction.issue_type_uuid(issue_type)[0]

        # 视图配置列表
        resp = self.call(prj.ItemGraphql, conf.layout_list()[0])

        layout_uuid = [d['uuid'] for d in resp.value('data.issueTypeLayouts') if
                       d['issueType']['uuid'] == issue_uuid and d['builtIn'] == True][0]

        # 视图草稿
        param = conf.layout_draft_get()[0]
        param.uri_args({'layout_uuid': layout_uuid})
        resp = self.call(lay.LayoutDraftGet, param)

        children = resp.value('data.view_block_root.children')[0]['children']

        # 关键属性
        task_fields = [field['uuid'] for c in children if c['type'] == 'task_fields' for field in
                       c['metadata']['fields']]

        # 快速操作
        quick_actions = [field['uuid'] for c in children if c['type'] == 'quick_actions' for field in
                         c['metadata']['actions']]

        return task_fields, quick_actions

    @story('149520 需求视图配置-编辑详情表单：检查开箱后工作项详情表单默认配置')
    @story('152183 子需求视图配置-编辑详情表单：检查开箱后工作项详情表单默认配置')
    @story('152184 任务视图配置-编辑详情表单：检查开箱后工作项详情表单默认配置')
    @story('152185 子任务视图配置-编辑详情表单：检查开箱后工作项详情表单默认配置')
    @story('152186 缺陷视图配置-编辑详情表单：检查开箱后工作项详情表单默认配置')
    @parametrize('types', ['需求', '缺陷', '任务', '子需求', '子任务'])
    def test_layout_unpack(self, types):
        task_fields, quick_actions = self.layout_detail(types)

        with step('查看关键属性'):
            assert ['field004', 'field005', 'field012', 'field011'] == task_fields

        with step('查看快捷操作'):
            assert 'quick001', 'quick002' in quick_actions

    @story('152317 需求视图配置-新建表单：检查新建表单展示详情')
    @story('152318 子需求视图配置-新建表单：检查新建表单展示详情')
    @story('152319 任务视图配置-新建表单：检查新建表单展示详情')
    @story('152320 子任务视图配置-新建表单：检查新建表单展示详情')
    @story('152321 缺陷视图配置-新建表单：检查新建表单展示详情')
    @parametrize('types', ['需求', '子需求', '任务', '子任务', '缺陷'])
    def test_check_add_form(self, types):
        task_fields, quick_actions = self.layout_detail(types)

        with step('查看表单详情'):
            assert ['field004', 'field005', 'field012', 'field011'] == task_fields
