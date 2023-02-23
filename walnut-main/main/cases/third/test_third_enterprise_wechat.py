import re

import requests
from falcons.check import Checker
from falcons.com.nick import feature, story, parametrize, step

from main.api import third as api
from main.environ import ThirdPartyType as Tdt
from main.params import third as p


@feature('Wechat服务')
class TestEnterpriseWechat(Checker):

    @story('146715 添加企业微信')
    def test_wechat_add(self):
        param = p.wechat_add()[0]

        with step('填写：ID、AgentId、Secret，勾选匹配「邮箱」相同的系统账号'):
            self.call(api.ThirdAddOrUpdate, param)

    @story('个人中心-绑定第三方账号：绑定企业微信账号')  # TODO wechat登录授权认证未实现
    def test_cas_bind(self):
        with step('获取企微登录链接'):
            param = p.wechat_login_link()[0]
            u = self.call(api.SsoLoginUrl, param)
            url = u.json()['login_url']

        with step('企微登录'):
            key_html = requests.get(url, verify=False).text
            pattern = re.compile('key=.*?"')
            key = (re.findall(pattern, key_html))[0][4:-1]  # 获取登录key

            get_value_url = f'https://open.work.weixin.qq.com/wwopen/sso/confirm2?k={key}'
            r = requests.get(get_value_url, verify=False).text

    def test_update_direct_sync(self):
        """更新目录同步配置"""
        # 获取配置详情
        detail_p = p.third_detail(Tdt.wechat_app)[0]
        detail = self.call(api.ThirdDetail, detail_p)
        json_config = detail.json()['json_config']

        param = p.third_sync_update(Tdt.wechat_app)[0]
        param.json['json_config'] = json_config

        self.call(api.ThirdSyncUpdate, param)

    @story('企业微信开启用户目录同步')
    def test_enabled_user_sync(self):
        with step('勾选定时同步、事件消息同步,点击「启用」'):
            sync_p = p.third_update('sync', Tdt.wechat_app)[0]
            self.call(api.ThirdStatusUpdate, sync_p)

    @story('个人中心-绑定第三方账号：解除绑定企业微信账号')
    @parametrize('param', p.third_user_unbind(Tdt.wechat_app))
    def test_unbind_wechat_in_personal_center(self, param):
        with step('解除绑定wechat账号'):
            self.call(api.ThirdUserUnbind, param)

        with step('检查解除绑定结果'):
            unbind_p = p.third_user_bindings()[0]
            resp = self.call(api.ThirdUserBindings, unbind_p)
            # 检查wechat 绑定信息为空
            ldap_bind = [r for r in resp.json() if r['third_party_type'] == Tdt.wechat_app][0]
            assert not ldap_bind['third_party_id']

    @story('移除 企业微信 集成')
    @parametrize('param', p.third_remove(Tdt.wechat_app))
    def test_wechat_remove(self, param):
        self.call(api.ThirdRemove, param)
