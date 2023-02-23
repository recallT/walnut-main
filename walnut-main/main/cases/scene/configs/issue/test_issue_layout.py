"""
@Desc：全局配置-工作项类型-属性与视图
"""
import operator

from falcons.check import Checker, go
from falcons.com.nick import feature, story, step, parametrize, fixture

from main.actions.task import TaskAction
from main.api import layout as lay, project
from main.params import conf, issue as ise
from . import IssueConfig


@fixture(scope='module')
def _layout_storage():
    return {
        'layout_uuid': [],
        'issue_type_uuid': []
    }


@fixture(scope='module', autouse=True)
def _init_data(_layout_storage):
    issue_type_uuid = IssueConfig.global_issue_type('用户故事')
    _layout_storage['issue_type_uuid'].append(issue_type_uuid)

    # 创建自定义标准工作项和子工作项
    issue_name, issue_uuid = IssueConfig.global_issue_add()
    _layout_storage['issue_type_uuid'].append(issue_uuid)
    sub_ise_name, sub_ise_uuid = IssueConfig.global_sub_issue_add()
    _layout_storage['issue_type_uuid'].append(sub_ise_uuid)

    yield
    if _layout_storage['layout_uuid']:
        p = conf.layout_delete()[0]
        p.uri_args({'layout_uuid': _layout_storage['layout_uuid'][0]})
        go(lay.LayoutDelete, p)

    # 删除创建的自定义工作项
    IssueConfig.global_issue_delete(issue_uuid)
    IssueConfig.global_issue_delete(sub_ise_uuid)


@feature('全局配置-属性与视图')
class TestGlobalIssueLayout(Checker):

    @story('135482 另存为全局视图配置')
    @parametrize('param', conf.layout_add())
    def test_global_issue_layout_save(self, param, _layout_storage):
        """全局配置-工作项视图另存为"""

        with step('另存为全局视图配置，视图配置名称输入'):
            del param.json['issue_type_uuid']
            param.uri_args({'issue_uuid': _layout_storage['issue_type_uuid'][0]})
            layout_resp = self.call(lay.GlobalLayoutCopy, param)

            _layout_storage['layout_uuid'].append(layout_resp.value('layout_uuid'))

    @story('135507 切换视图配置（本地->全局）')
    @parametrize('param', conf.switch_layout())
    def test_global_switch_local_to_global(self, param, _layout_storage):
        """全局配置-工作项视图切换 本地->全局"""

        with step('点击切换视图配置-全局视图配置，选择视图'):
            param.json_update('layout_uuid', _layout_storage['layout_uuid'][0])
            param.uri_args({'issue_uuid': _layout_storage['issue_type_uuid'][0]})
            resp = self.call(lay.GlobalSwitchLayout, param, is_print=False)

            resp.check_response('default_configs.layout_uuid', _layout_storage['layout_uuid'][0])

    @story('135537 切换视图配置（全局->本地）')
    @parametrize('param', conf.switch_layout())
    def test_global_switch_global_to_local(self, param, _layout_storage):
        """全局配置-工作项视图切换 全局->本地"""

        with step(f'点击切换视图配置-本地视图配置，选择视图'):
            param.uri_args({'issue_uuid': _layout_storage['issue_type_uuid'][0]})
            resp = self.call(lay.GlobalSwitchLayout, param)

            resp.check_response('default_configs.layout_uuid', "")

    @story('T135468 属性与视图：切换视图配置（本地->全局）-子任务')
    @story('T135530 属性与视图：切换视图配置（全局->本地）-子任务')
    @parametrize('param', conf.switch_layout())
    def test_global_sub_task_views_switch(self, param):
        issue_type_uuid = TaskAction.issue_type_uuid('子任务')[0]
        with step('切换视图配置（本地->全局'):
            # 查询子任务全局视图uuid
            parm = conf.layout_list()[0]
            res = self.call(project.ItemGraphql, parm)
            layout_uuid = [r['uuid'] for r in res.value('data.issueTypeLayouts') if
                           r['issueType']['uuid'] == issue_type_uuid][0]

            param.uri_args({'issue_uuid': issue_type_uuid})
            param.json_update('layout_uuid', layout_uuid)
            resp = self.call(lay.GlobalSwitchLayout, param, is_print=False)

            resp.check_response('default_configs.layout_uuid', layout_uuid)
        with step('切换视图配置（全局->本地'):
            param.json_update('layout_uuid', '')
            resp = self.call(lay.GlobalSwitchLayout, param, is_print=False)
            resp.check_response('default_configs.layout_uuid', "")


@feature('全局配置-工作项类型-属性与视图-模块标签页')
class TestGlobalModuleTab(Checker):

    @story('131036 模块标签页：关闭显示')
    @parametrize('param', ise.tab_config_update())
    def test_global_module_tab_close_display(self, param, _layout_storage):
        """全局配置-模块标签页关闭显示"""

        with step('关闭代码关联显示状态'):
            param.json_update('configs[8].is_show', False)
            param.uri_args({'issue_uuid': _layout_storage['issue_type_uuid'][0]})
            resp = self.call(lay.GlobalTabConfigUpdate, param)

            resp.check_response('configs[8].is_show', False)

    @story('131045 模块标签页：开启显示')
    @parametrize('param', ise.tab_config_update())
    def test_global_module_tab_open_display(self, param, _layout_storage):
        """全局配置-模块标签页开启显示"""

        with step('开启代码关联显示状态'):
            param.uri_args({'issue_uuid': _layout_storage['issue_type_uuid'][0]})
            resp = self.call(lay.GlobalTabConfigUpdate, param)

            resp.check_response('configs[8].is_show', True)

    @story('131067/131065 自定义标准工作项/自定义子工作项/模块标签页：模块标签页列表检查')
    @parametrize('type_num', (1, 2))
    def test_check_module_tab_list(self, type_num, _layout_storage):
        configs_list = [1, 2, 3, 4, 5, 6, 7, 8]

        with step(f'查看模块标签页列表'):
            param = ise.tab_config_update()[0]
            param.uri_args({'issue_uuid': _layout_storage['issue_type_uuid'][type_num]})
            resp = self.call(lay.GlobalIssueTabConfigs, param, with_json=False)

            configs = [c['type'] for c in resp.value('configs') if c['is_show'] == True]
            assert operator.le(configs_list, configs)  # 小于或等于返回True
