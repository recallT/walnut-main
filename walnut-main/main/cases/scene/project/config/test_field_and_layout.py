"""
@Desc：项目设置-工作项类型-属性与视图
"""
import operator

from falcons.check import Checker, go
from falcons.com.nick import feature, story, step, parametrize, fixture

from main.actions.task import TaskAction
from main.api import project as prj, layout as lay, issue
from main.api.issue import IssueTabConfigs
from main.params import conf, graphql as gq, issue as ise


@fixture(scope='module')
def _layout_storage():
    return {
        'layout_uuid': [],
        'type_scope': []
    }


@fixture(scope='module', autouse=True)
def _clear_layout(_layout_storage):
    yield
    if _layout_storage['layout_uuid']:
        for uuid in _layout_storage['layout_uuid']:
            p = conf.layout_delete()[0]
            p.uri_args({'layout_uuid': uuid})
            go(lay.LayoutDelete, p)


def get_issue_type_scope(types):
    issue_type_uuid = TaskAction.issue_type_uuid(types)

    param = gq.issue_type_scope()[0]
    param.json['variables']['filter'] |= {'issueType': {'uuid_in': issue_type_uuid}}
    resp = go(prj.ItemGraphql, param)

    return resp.value('data.buckets[0].issueTypeScopes[0].uuid')


@feature('工作项类型-属性与视图')
class TestFieldAndLayout(Checker):

    @story('135476 任务-属性与视图：另存为全局视图配置')
    @story('135469 子任务-属性与视图：另存为全局视图配置')
    @story('T135468 属性与视图：另存为全局视图配置-子任务')
    @parametrize('types', ('任务', '子任务'))
    def test_task_layout_save(self, types, _layout_storage):
        with step('另存为全局视图配置，视图配置名称输入'):
            issue_type_scope = get_issue_type_scope(types)

            param = conf.layout_add()[0]
            del param.json['issue_type_uuid']
            param.uri_args({'issue_type_scope': issue_type_scope})
            layout_resp = self.call(lay.ProjLayoutCopy, param)

            _layout_storage['layout_uuid'].append(layout_resp.value('layout_uuid'))
            _layout_storage['type_scope'].append(issue_type_scope)

    @story('135522 任务-切换视图配置（本地->全局）')
    @story('135517 子任务-切换视图配置（本地->全局）')
    @parametrize('type_num', (0, 1))
    def test_layout_switch_local_to_global(self, type_num, _layout_storage):
        with step('点击切换视图配置-全局视图配置，选择视图'):
            param = conf.switch_layout()[0]

            if _layout_storage:
                param.json_update('layout_uuid', _layout_storage['layout_uuid'][type_num])
                param.uri_args({'issue_type_scope': _layout_storage['type_scope'][type_num]})
                self.call(lay.ProjSwitchLayout, param)

    @story('135534 任务-切换视图配置（全局->本地）')
    @story('135543 子任务-切换视图配置（全局->本地）')
    @parametrize('type_num', (0, 1))
    def test_layout_switch_global_to_local(self, type_num, _layout_storage):
        with step(f'点击切换视图配置-本地视图配置，选择视图'):
            param = conf.switch_layout()[0]

            if _layout_storage:
                param.uri_args({'issue_type_scope': _layout_storage['type_scope'][type_num]})
                self.call(lay.ProjSwitchLayout, param)


@feature('工作项类型-属性与视图-模块标签页')
class TestModuleTab(Checker):

    @story('131032 任务-模块标签页：关闭显示')
    @story('131037 子任务-模块标签页：关闭显示')
    @parametrize('type_num', (0, 1))
    def test_module_tab_close_display(self, type_num, _layout_storage):
        with step('关闭代码关联显示状态'):
            param = ise.tab_config_update()[0]

            if _layout_storage:
                param.json_update('configs[8].is_show', False)
                param.uri_args({'issue_type_scope': _layout_storage['type_scope'][type_num]})
                resp = self.call(issue.ProjTabConfigUpdate, param)

                resp.check_response('configs[8].is_show', False)

    @story('131056 任务-模块标签页：开启显示')
    @story('131052 任务-模块标签页：开启显示')
    @parametrize('type_num', (0, 1))
    def test_module_tab_open_display(self, type_num, _layout_storage):
        with step('开启代码关联显示状态'):
            param = ise.tab_config_update()[0]

            if _layout_storage:
                param.uri_args({'issue_type_scope': _layout_storage['type_scope'][type_num]})
                resp = self.call(issue.ProjTabConfigUpdate, param)

                resp.check_response('configs[8].is_show', True)

    def test_get_demand(self, _layout_storage):
        issue_type_scope = get_issue_type_scope('需求')
        _layout_storage['type_scope'].append(issue_type_scope)

    @story('131242 需求模块标签页：模块标签页列表检查')
    @story('131245 任务模块标签页：模块标签页列表检查')
    @story('131246 子任务模块标签页：模块标签页列表检查')
    @parametrize('type_num', (0, 1, 2))
    def test_check_module_tab_list(self, type_num, _layout_storage):
        configs_list = [1, 2, 3, 4, 5, 6, 7, 8]

        with step(f'查看模块标签页列表'):
            param = ise.tab_config_update()[0]

            if _layout_storage:
                param.uri_args({'issue_type_scope': _layout_storage['type_scope'][type_num]})
                resp = self.call(issue.IssueTabConfigs, param, with_json=False)

                configs = [c['type'] for c in resp.value('configs')]
                assert operator.le(configs_list, configs)  # 小于或等于返回True

    @story('T131254 模块标签页：排序')
    def test_sort_tab_config(self):
        issue_type_scope = TaskAction.issue_type_uuid(issue_types='任务', uuid_type='uuid')[0]
        param = ise.notice_rules()[0]
        param.uri_args({'issue_type_scope': issue_type_scope})
        configs_list = self.call(IssueTabConfigs, param).value('configs')

        with step('长按拖拽「关联内容」至「子工作项」前'):
            # 更换位置
            configs_list[2]['type'], configs_list[4]['type'] = configs_list[4]['type'], configs_list[2]['type']

            param_config = ise.tab_config_update1()[0]
            param_config.json_update('configs', configs_list)
            param_config.uri_args({'issue_type_scope': issue_type_scope})
            resp = self.call(issue.ProjTabConfigUpdate, param_config)
            resp.check_response('configs', configs_list)
