from falcons.check import Checker
from falcons.com.nick import feature, story, fixture, parametrize, step
from falcons.platform.delivers.deliver_plugin_lifecycle import *
from falcons.platform.env_init import *

from main.api import plugin as api
from main.params import plug as p


@fixture(scope='module', autouse=True)
def do_plugin():
    do_deliver_install("honor_banner.opk")
    do_deliver_enable("honor_banner.opk")
    print("插件安装启用成功！")
    # info = get_plugin_info("Honor_workspace.opk")
    yield
    do_deliver_disable("honor_banner.opk")
    do_deliver_uninstall("honor_banner.opk")
    print("插件卸载成功！")


@feature('顶部安全栏提示语-Banner')
class TestBannerTips(Checker):
    """"""

    @story('获取-顶部安全栏提示语')
    @parametrize('param', p.set_banner_tips())
    def test_set_banner_tips(self, param):
        """获取顶部安全栏提示语"""
        info = get_plugin_info("honor_banner.opk")
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': info[0]['instance_id']}
        header.update()
        with step('更新banner提示语内容'):
            resp = self.call(api.SetBannerTips, param, header)
            # ('data.content','test+123'-----plu 里修改了参数，这里也要对应修改)
            resp.check_response('data.content', 'test+123')
            # resp.check_response('data.content', param.json_value('content'))----动态获取就这样写
        with step('获取顶部安全栏提示语内容'):
            respget = self.call(api.GetBannerTips, param, header)
            # 校验已写死：'test+123'-----plu 里修改了参数，这里也要对应修改
            respget.check_response('data.content', 'test+123')
