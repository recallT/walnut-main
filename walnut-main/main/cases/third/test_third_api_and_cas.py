import requests
from falcons.check import Checker, go
from falcons.com.nick import feature, step, parametrize, fixture, story

from main.api import project as prj
from main.api import third as api
from main.environ import ThirdPartyType as Tdt
from main.params import auth
from main.params import third as p
from main.params.third import CasAccount as Ca


# 添加第三方api
@fixture(scope='module', autouse=True)
def add_third_api():
    param = p.third_api_add()[0]
    go(api.ThirdAddOrUpdate, param)


# 移除api数据
@fixture(scope='module', autouse=True)
def del_api():
    yield
    # 移除第三方集成api
    prm = p.third_support_list()[0]
    q = go(api.ThirdList, prm)
    ty = [t['third_party_type'] for t in q.json()['results']]
    for t in ty:
        param = p.third_remove(t)[0]
        go(api.ThirdRemove, param)

    # 移除api部门数据
    pm = p.org_department()[0]
    q = go(api.OrgDepartment, pm)
    depart_uuids = [n['uuid'] for n in q.json()['data']['departments'] if n['name'] == 'API' or n['name'] == 'add_test'
                    or n['name'] == 'RenameApi']

    if len(depart_uuids) >= 1:
        data = p.user_me()[0]
        for i in depart_uuids:
            data.uri_args({'depart_uuid': i})
            go(api.DeleteDepartment, data)


@feature('第三方集成api+cas')
class TestThirdApiAndCas(Checker):

    def api_sync(self, enable):
        """api同步"""
        prm = p.third_update('sync', Tdt.api, enable)[0]
        self.call(api.ThirdStatusUpdate, prm)

    def enable_cas_login(self):
        """启用cas登录认证"""
        param = p.third_update('login', Tdt.cas, True)[0]
        self.call(api.ThirdStatusUpdate, param)

    def user_add(self):
        # 查看系统中是否存在成员A
        prm = p.all_member()[0]
        am = self.call(api.AllMember, prm)
        users = am.json()['data']['buckets'][0]['users']
        user = [u for u in users if u['name'] == 'api_and_cas']

        if not user:
            param = auth.invitation()[0]
            email = Ca.a5[1]['email']
            passwd = Ca.a5[0]['password']

            # 邀请成员到团队
            param.json['invite_settings'] = [{'email': email}]
            go(prj.InvitationsAdd, param)

            # 查询邀请列表
            h = auth.invitation_history()[0]
            ih = go(prj.InvitationsHistory, h)

            # 邀请码
            invite_code = [c['code'] for c in ih.json()['invitations'] if c['email'] == email]

            jt = auth.join_team()[0]
            jt.json |= {'email': email, "password": passwd, "name": email[:-9], 'invite_code': invite_code[0]}

            aj = go(prj.AuthInviteJoin, jt)

            # 获取新成员uuid 和密码
            member = {'uuid': aj.json()['user']['uuid'], 'password': jt.json['password']}

    def cas_login_url(self):
        param = p.cas_login_link()[0]
        u = self.call(api.SsoLoginUrl, param)
        url = u.json()['login_url']
        return url

    def get_param(self, account: dict):
        url = self.cas_login_url()
        execution = api.CasExecutionValue(url).get_value()  # 一个execution只能使用一次，不能重复使用
        if execution:
            header = {'Accept-Language': 'zh-CN,zh;q=0.9'}
            body = {'execution': execution, '_eventId': 'submit', 'geolocation': ''}
            body |= account
            login = requests.post(url, data=body, headers=header, verify=False)
            try:
                redirect_url = login.history[1].url  # 获取cas登录后重定向的url

                bind_p = p.third_user_bind(Tdt.cas)[0]
                auth_key = redirect_url.split('?')[-1].split('&')[0].split('=')[1]
                ticket = redirect_url.split('?')[-1].split('&')[-1].split('=')[1]
                auth_info = "{\"auth_key\":\"%s\",\"from\":\"\",\"type\":\"4\",\"ticket\":\"%s\"}" % (auth_key, ticket)

                bind_p.json['auth_info'] = auth_info

                return bind_p
            except:
                return '认证失败'

    @story('150258 已开启API用户目录同步，添加CAS集成')
    @parametrize('param', p.cas_add())
    def test_enable_api_add_cas(self, param):

        with step('前置条件'):
            # 系统中需存在API和CAS共同成员A
            # self.user_add()

            # api服务创建共同成员
            prm = p.api_mocks_add_user()[0]
            self.call(api.FakeApiAdd, prm)

            # 开启api同步
            self.api_sync(True)

        with step('添加CAS集成'):
            # 绑定方式选择：自动绑定「唯一标识」相同的同步源账号
            param.json['match_user_by'] = 2
            self.call(api.ThirdAddOrUpdate, param)

        with step('开启cas登录认证'):
            self.enable_cas_login()

        with step('用户A通过cas登录'):
            account = Ca.a5[0]
            prm = self.get_param(account)
            r = self.call(api.SsoLogin, prm)
            r.check_response('user.status', 1)

        # with step('用户A个人中心-绑定第三方账号'):
        #     l_user = User(email=Ca.a5[1]['email'], passwd=Ca.a5[0]['password'])
        #     token = api_login(l_user)  # 获取用户A的token
        #
        #     prm = p.third_user_bindings()[0]
        #     r = self.call(api.ThirdUserBindings, prm, token)
        #
        #     ids = [i['third_party_id'] for i in r.json() if
        #            i['third_party_type'] == Tdt.cas or i['third_party_type'] == Tdt.api]
        #     assert ids[0] == ""
        #     assert ids[1] == ""

    @story('150264 关闭 API同步源，查看CAS的绑定方式')
    @story('150261 API+CAS：检查有同步源的情况下，编辑CAS集成（选择自动绑定「唯一标识」）')
    @parametrize('param', p.cas_add())
    def test_closure_api_checking_cas(self, param):

        with step('前置条件'):
            # 系统中需存在API和CAS共同成员A
            self.user_add()

            # 开启api同步
            self.api_sync(True)

            # 添加cas集成，绑定方式选择：自动绑定「唯一标识」相同的同步源账号
            param.json['match_user_by'] = 2
            self.call(api.ThirdAddOrUpdate, param)
            self.enable_cas_login()

        with step('关闭API同步源，查看cas账号绑定方式'):
            # 关闭同步
            self.api_sync(False)

            # 查看cas详情
            detail_p = p.third_detail(Tdt.cas)[0]
            detail = self.call(api.ThirdDetail, detail_p)

            detail.check_response('match_user_by', 0)  # 成员手动绑定

    @story('150504 同步源绑定已删除的系统账号，检查非同步源账号登录系统的表现')
    @parametrize('param', p.cas_add())
    def test_del_system_account(self, param):

        with step('前置条件'):
            # 系统中需存在API和CAS共同成员A
            self.user_add()

            # 开启api同步
            self.api_sync(True)

            # 添加cas集成，绑定方式选择：自动绑定「唯一标识」相同的同步源账号
            param.json['match_user_by'] = 2
            self.call(api.ThirdAddOrUpdate, param)
            self.enable_cas_login()

        with step('已删除的用户A通过cas登录'):
            account = {'username': 'test_api_cas', 'password': 'Aa123456'}
            prm = self.get_param(account)
            assert prm == '认证失败'
