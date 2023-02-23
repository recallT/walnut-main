from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, parametrize, step
from falcons.platform.delivers.deliver_plugin_lifecycle import *
from falcons.platform.env_init import *

from main.api import plugin as api
from main.params import plug as p


@fixture(scope='module', autouse=True)
def do_plugin():
    do_deliver_install("Honor_workspace.opk")
    do_deliver_enable("Honor_workspace.opk")
    print("插件安装启用成功！")
    # info = get_plugin_info("Honor_workspace.opk")
    yield
    do_deliver_disable("Honor_workspace.opk")
    do_deliver_uninstall("Honor_workspace.opk")
    print("插件卸载成功！")


@fixture(scope='module')  # 缓存一个数据
def _member_id_():
    m = dict()

    return m


@feature("honor_workspace插件接口用例")
class TestHideWorkspace(Checker):

    @story("隐藏工作台权限校验")
    @parametrize('param', p.workspace_permission_number_check())
    def test_hide_check_F(self, param):
        info = get_plugin_info("Honor_workspace.opk")
        print(info)
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': 'built_in_apis',
                  'instance_id': info[0]['instance_id']}
        header.update()
        # param.json_update('', info[0]['instance_id'])
        with step('隐藏工作台'):
            resp = self.call(api.WorkspacePermissionNumberCheck, param, header)
            resp.check_response('data.is_permission', False)

    @story("获取可用成员配置列表")
    @parametrize('param', p.workspace_permission_info_list())
    def test_get_permission_info_list(self, param, _member_id_):
        info = get_plugin_info("Honor_workspace.opk")
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': 'built_in_apis',
                  'instance_id': info[0]['instance_id']}
        header.update()
        param.json_update('instance_uuid', info[0]['instance_id'])
        with step('获取可用成员配置列表'):
            resp = self.call(api.WorkspacePermissionInfoList, param, header)
            _member_id_ |= {'member_id': resp.value('data[0].permission_id')}

    @story("添加成员")
    @parametrize('param', p.workspace_permission_number_add())
    def test_add_person(self, param, _member_id_):
        info = get_plugin_info("Honor_workspace.opk")

        param.json_update('permission_id', _member_id_['member_id'])
        param.json_update('permission', _member_id_['member_id'])
        param.json_update('context_param.plugin_uuid', info[0]['instance_id'])
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': 'built_in_apis',
                  'instance_id': info[0]['instance_id']}
        header.update()
        with step('添加成员'):
            resp = self.call(api.WorkspacePermissionNumberAdd, param, header)
            _member_id_ |= {'id': resp.value('data.id')}

    @story("不隐藏我的工作台校验")
    @parametrize('param', p.workspace_permission_number_check())
    def test_hide_check_T(self, param):
        info = get_plugin_info("Honor_workspace.opk")
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': 'built_in_apis',
                  'instance_id': info[0]['instance_id']}
        header.update()
        param.json_update('', info[0]['instance_id'])
        with step('隐藏工作台'):
            resp = self.call(api.WorkspacePermissionNumberCheck, param, header)
            resp.check_response('data.is_permission', True)

    @story("删除成员")
    @parametrize('param', p.workspace_permission_number_delete())
    def test_del_person(self, param, _member_id_):
        info = get_plugin_info("Honor_workspace.opk")

        param.json_update('id', _member_id_['id'])
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': 'built_in_apis',
                  'instance_id': info[0]['instance_id']}
        header.update()
        with step('删除成员'):
            resp = self.call(api.WorkspacePermissionNumberDelete, param, header)
            resp.check_response('data', True)
