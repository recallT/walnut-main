from time import sleep

from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, parametrize, step
from falcons.platform.delivers.deliver_plugin_lifecycle import *
from falcons.platform.env_init import *

from main.api import plugin as api
from main.params import plug as p


@fixture(scope='module', autouse=True)
def do_plugin():
    do_deliver_install("Honor_upload_tips.opk")
    do_deliver_enable("Honor_upload_tips.opk")
    print("插件安装启用成功！")
    # info = get_plugin_info("Honor_workspace.opk")
    sleep(20)

    yield
    do_deliver_disable("Honor_upload_tips.opk")
    do_deliver_uninstall("Honor_upload_tips.opk")
    print("插件卸载成功！")


@fixture(scope='module')  # 缓存一个数据
def _member_id_():
    m = dict()

    return m


@feature('上传文件安全提示语')
class TestUploadTips(Checker):
    """"""

    @story('获取/设置/检查-上传文件安全提示语')
    @parametrize('param', p.set_upload_tips())
    def test_set_upload_tips(self, param):
        """上传文件安全提示语"""
        info = get_plugin_info("Honor_upload_tips.opk")
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': info[0]['instance_id']}
        header.update()
        with step('更新安全提示语内容'):
            resp = self.call(api.SetUploadTips, param, header)
            # ('data.content','test+123'-----plu 里修改了参数，这里也要对应修改)
            resp.check_response('data.content', 'test+123')
            # resp.check_response('data.content', param.json_value('content'))----动态获取就这样写
        with step('获取安全提示语内容'):
            resp_get = self.call(api.GetUploadTips, param, header)
            # 校验已写死：'test+123'-----plu 里修改了参数，这里也要对应修改
            resp_get.check_response('data.content', 'test+123')


class TestUploadTipsCheck(Checker):

    @story("获取安全提示语权限校验-无权限")
    @parametrize('param', p.Permission_Number_Check())
    def test_uploadtips_check_F(self, param):
        info = get_plugin_info("Honor_upload_tips.opk")
        print(info)
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': 'built_in_apis',
                  'instance_id': info[0]['instance_id']}
        header.update()
        # param.json_update('', info[0]['instance_id'])
        with step('无权限校验'):
            resp = self.call(api.PermissionNumberCheck, param, header)
            resp.check_response('data.is_permission', False)

    @story("获取可用成员配置列表")
    @parametrize('param', p.Permission_Info_List())
    def test_get_permission_info_list(self, param, _member_id_):
        info = get_plugin_info("Honor_upload_tips.opk")
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': 'built_in_apis',
                  'instance_id': info[0]['instance_id']}
        header.update()
        param.json_update('instance_uuid', info[0]['instance_id'])
        with step('获取可用成员配置列表'):
            resp = self.call(api.PermissionInfoList, param, header)
            _member_id_ |= {'permission_id': resp.value('data[0].permission_id')}

    @story("添加成员")
    @parametrize('param', p.Permission_Number_Add())
    def test_add_person(self, param, _member_id_):
        info = get_plugin_info("Honor_upload_tips.opk")

        param.json_update('permission_id', _member_id_['permission_id'])
        param.json_update('permission', _member_id_['permission_id'])
        param.json_update('context_param.plugin_uuid', info[0]['instance_id'])
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': 'built_in_apis',
                  'instance_id': info[0]['instance_id']}
        header.update()
        with step('添加成员'):
            resp = self.call(api.PermissionNumberAdd, param, header)
            _member_id_ |= {'id': resp.value('data.id')}

    @story("获取安全提示语权限校验-有权限")
    @parametrize('param', p.Permission_Number_Check())
    def test_uploadtips_check_T(self, param):
        info = get_plugin_info("Honor_upload_tips.opk")
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': 'built_in_apis',
                  'instance_id': info[0]['instance_id']}
        header.update()
        param.json_update('instance_id', info[0]['instance_id'])
        with step('有权限校验'):
            resp = self.call(api.PermissionNumberCheck, param, header)
            resp.check_response('data.is_permission', True)

    @story("删除成员")
    @parametrize('param', p.Permission_Number_Delete())
    def test_del_person(self, param, _member_id_):
        info = get_plugin_info("Honor_upload_tips.opk")

        param.json_update('id', _member_id_['id'])
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': 'built_in_apis',
                  'instance_id': info[0]['instance_id']}
        header.update()
        with step('删除成员'):
            resp = self.call(api.PermissionNumberDelete, param, header)
            resp.check_response('data', True)
