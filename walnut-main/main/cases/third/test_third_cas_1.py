import requests
from falcons.check import Checker
from falcons.com.nick import feature, story, parametrize, step

from main.api import third as api
from main.environ import ThirdPartyType as Tdt
from main.params import third as p
from main.params.third import CasAccount as Ca


@feature('CAS服务')
class TestCas(Checker):

    @story('149682 添加第三方集成：手动绑定CAS')
    def test_cas_manual_add(self):
        param = p.cas_add()[0]
        self.call(api.ThirdAddOrUpdate, param)

    @story('149789 启用CAS登录认证')
    @story('143794 CAS登录-单团队登录')
    @parametrize('param', p.third_update('login', Tdt.cas))
    def test_status_enable(self, param):
        with step('点击启用'):
            self.call(api.ThirdStatusUpdate, param)

    @story('149859 个人中心-绑定第三方账号：绑定CAS账号')
    def test_cas_bind(self):
        with step('获取cas登录链接'):
            param = p.cas_login_link()[0]
            u = self.call(api.SsoLoginUrl, param)
            url = u.json()['login_url']

        with step('cas登录'):
            execution = api.CasExecutionValue(url).get_value()
            if execution:
                data = {'execution': execution, '_eventId': 'submit', 'geolocation': ''}
                data |= Ca.a1[0]
                login = requests.post(url, data=data, verify=False)
                redirect_url = login.history[1].url  # 获取cas登录后重定向的url

        with step('绑定cas账号'):
            bind_p = p.third_user_bind(Tdt.cas)[0]
            auth_key = redirect_url.split('?')[-1].split('&')[0].split('=')[1]
            ticket = redirect_url.split('?')[-1].split('&')[-1].split('=')[1]
            auth_info = "{\"auth_key\":\"%s\",\"from\":\"\",\"type\":\"4\",\"ticket\":\"%s\"}" % (auth_key, ticket)

            bind_p.json['auth_info'] = auth_info

            self.call(api.ThirdUserBind, bind_p)

        with step('检查cas绑定结果'):
            bind_p = p.third_user_bindings()[0]
            resp = self.call(api.ThirdUserBindings, bind_p)

            # 检查cas 绑定id 为xz
            ldap_bind = [r for r in resp.json() if r['third_party_type'] == Tdt.cas][0]

            assert ldap_bind['third_party_id'] == data['username']
            assert ldap_bind['is_bind'] == True

    @story('149684 添加CAS：添加用户属性映射')
    def test_cas_job_add(self):
        param = p.cas_add()[0]
        param.json['mappings'].append({"system_property_key": "id_number", "third_party_property_key": "id_number"})

        with step('成员属性选择：工号'):
            self.call(api.ThirdAddOrUpdate, param)

    @story('149797 开启登陆即时创建用户（单团队)')  # Todo 接口问题需修复
    @parametrize('param', p.login_create_member(Tdt.cas))
    def test_login_and_bind_user(self, param):
        """"""
    #
    #     with step('启用登陆即创建用户 团队A'):
    #         update = self.call(api.ThirdLoginUpdate, param)
    #         update.check_response('type', 'OK')

    #  with step('通过cas登录成员A'):
    #      param = p.cas_login_link()[0]
    #      u = self.call(api.SsoLoginUrl, param)
    #      url = u.json()['login_url']
    #
    #      execution = api.CasExecutionValue(url).get_value()
    #      if execution:
    #          data = {'username': 'Xz', 'password': 'Aa123456', 'execution': execution,
    #                  '_eventId': 'submit', 'geolocation': ''}
    #          login = requests.post(url, data=data, verify=False)
    #          redirect_url = login.history[1].url  # 获取cas登录后重定向的url
    #
    #      bind_p = p.third_user_bind(Tdt.cas)[0]
    #      auth_key = redirect_url.split('?')[-1].split('&')[0].split('=')[1]
    #      ticket = redirect_url.split('?')[-1].split('&')[-1].split('=')[1]
    #      auth_info = "{\"auth_key\":\"%s\",\"from\":\"\",\"type\":\"4\",\"ticket\":\"%s\"}" % (auth_key, ticket)
    #
    #      bind_p.json['auth_info'] = auth_info
    #
    #      self.call(api.ThirdUserBind, bind_p)
    #
    # with step('检查成员A登录成功，并加入团队'):
    #     ...

    @story('149683 添加第三方集成：自动绑定「邮箱相同的系统账号」CAS')
    def test_cas_auto_add(self):
        param = p.cas_add()[0]

        with step('绑定方式选择：自动绑定「邮箱相同的系统账号」'):
            param.json['match_user_by'] = 1
            self.call(api.ThirdAddOrUpdate, param)

    @story('149791-禁用CAS登录认证')
    @parametrize('param', p.third_update('login', Tdt.cas, False))
    def test_status_enable(self, param):
        with step('点击禁用'):
            self.call(api.ThirdStatusUpdate, param)

    @story('149860 个人中心-绑定第三方账号：解除绑定CAS账号')
    @parametrize('param', p.third_user_unbind(Tdt.cas))
    def test_unbind_cas_in_personal_center(self, param):
        with step('解除绑定cas账号'):
            self.call(api.ThirdUserUnbind, param)

        with step('检查解除绑定结果'):
            unbind_p = p.third_user_bindings()[0]
            resp = self.call(api.ThirdUserBindings, unbind_p)
            # 检查cas 绑定信息为空
            ldap_bind = [r for r in resp.json() if r['third_party_type'] == Tdt.cas][0]
            assert not ldap_bind['third_party_id']

    @story('移除CAS集成')
    @parametrize('param', p.third_remove(Tdt.cas))
    def test_cas_remove(self, param):
        self.call(api.ThirdRemove, param)

        with step('进入「ONES团队」-成员管理-不存在成员B'):
            """"""
        with step('成员A登录系统，进入个人中心-第三方集成-不存在CAS'):
            """"""
            unbind_p = p.third_user_bindings()[0]
            resp = self.call(api.ThirdUserBindings, unbind_p)
            # 检查CAS 绑定信息为空
            ldap_bind = [r for r in resp.json() if r['third_party_type'] == Tdt.cas]
            assert not ldap_bind
