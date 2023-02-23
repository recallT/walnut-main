import requests
from falcons.check import Checker, go
from falcons.com.nick import feature, story, parametrize, step, fixture

from main.api import project as prj
from main.api import third as api
from main.environ import ThirdPartyType as Tdt
from main.params import auth, data as dta
from main.params import third as t
from main.params.third import CasAccount as Ca


@fixture(scope='module')
def _member():
    p = {}
    return p


# 初始化cas配置
@fixture(scope='module', autouse=True)
def cas_add():
    param = t.cas_add()[0]
    with step('开启自动绑定「邮箱」相同的系统帐号'):
        param.json['match_user_by'] |= 1
        go(api.ThirdAddOrUpdate, param)

    with step('开启登录认证'):
        param = t.third_update('login', Tdt.cas, True)[0]
        go(api.ThirdStatusUpdate, param)

    with step('开启登录时即创建成员'):
        param = t.login_create_member(Tdt.cas)[0]
        update = go(api.ThirdLoginUpdate, param)
        update.check_response('type', 'OK')


# 删除创建用户数据
@fixture(scope='module', autouse=True)
def del_ones_user(_member):
    yield

    # 测试完成，删除创建的成员数据
    if _member != {}:
        d = dta.delete_member()[0]
        d.json['member'] = _member['uuid']
        go(prj.DeleteMember, d)


@fixture(scope='module', autouse=True)
def cas_remove():
    yield
    param = t.third_remove(Tdt.cas)[0]
    go(api.ThirdRemove, param)


@feature('CAS开启登录即创建用户')
class TestCasEnableLoginToCreateUser(Checker):

    def login_url(self, token=None):
        param = t.cas_login_link()[0]
        u = self.call(api.SsoLoginUrl, param, token)
        url = u.json()['login_url']
        return url

    def get_param(self, data: dict):
        url = self.login_url()
        execution = api.CasExecutionValue(url).get_value()  # 一个execution只能使用一次，不能重复使用
        if execution:
            header = {'Accept-Language': 'zh-CN,zh;q=0.9'}
            body = {'execution': execution, '_eventId': 'submit', 'geolocation': ''}
            body |= data
            login = requests.post(url, data=body, headers=header, verify=False)
            redirect_url = login.history[1].url  # 获取cas登录后重定向的url

            bind_p = t.third_user_bind(Tdt.cas)[0]
            auth_key = redirect_url.split('?')[-1].split('&')[0].split('=')[1]
            ticket = redirect_url.split('?')[-1].split('&')[-1].split('=')[1]
            auth_info = "{\"auth_key\":\"%s\",\"from\":\"\",\"type\":\"4\",\"ticket\":\"%s\"}" % (auth_key, ticket)

            bind_p.json['auth_info'] = auth_info

            return bind_p

    def user_add(self, _member, token=None):
        param = auth.invitation()[0]
        email = Ca.a1[1]['email']

        # 邀请成员到团队
        param.json['invite_settings'] = [{'email': email}]
        go(prj.InvitationsAdd, param, token)

        # 查询邀请列表
        h = auth.invitation_history()[0]
        ih = go(prj.InvitationsHistory, h, token)

        # 邀请码
        invite_code = [c['code'] for c in ih.json()['invitations'] if c['email'] == email]

        jt = auth.join_team()[0]
        jt.json |= {'email': email, "password": "qweqwe123", "name": email[:-9], 'invite_code': invite_code[0]}

        aj = go(prj.AuthInviteJoin, jt, token)

        # 获取新成员uuid 和密码
        _member |= {'uuid': aj.json()['user']['uuid'], 'password': jt.json['password']}

        # 禁用成员
        param = t.disable_members()[0]
        param.json['members'].append(_member['uuid'])
        go(prj.DisableMembers, param, token)

    @story('149790 CAS详情页：复制登录链接访问')
    def test_visit_login_link(self):
        with step('访问链接'):
            r = requests.get(url=self.login_url(), verify=False)
            assert r.status_code == 200
            assert 'LOGIN' in r.text

    @story('添加全部用户属性映射后，检查添加更多属性入口')
    @parametrize('param', t.cas_add())
    def test_add_more_attribute(self, param):

        with step('添加更多属性-工号'):
            param.json['mappings'].append({"system_property_key": "id_number",
                                           "third_party_property_key": "job_number"})
        with step('添加更多属性-公司'):
            param.json['mappings'].append({"system_property_key": "company",
                                           "third_party_property_key": "company"})
        with step('添加更多属性-职位'):
            param.json['mappings'].append({"system_property_key": "title",
                                           "third_party_property_key": "title"})
            self.call(api.ThirdAddOrUpdate, param)

        with step('用户属性映射列表删除：职位'):
            del_p = [d for d in param.json['mappings'] if d['system_property_key'] != 'title']
            param.json |= {'mappings': del_p}
            self.call(api.ThirdAddOrUpdate, param)

    @story('150097 已开启登录即时创建用户-自动绑定：CAS成员绑定已有系统账号（状态已禁用）')
    def test_match_disabled_member(self, _member):
        url = self.login_url()

        with step('ones禁用成员'):
            self.user_add(_member)

        with step('通过cas登录被禁用的成员'):
            data = Ca.a1[0]
            execution = api.CasExecutionValue(url).get_value()

            if execution:
                header = {'Accept-Language': 'zh-CN,zh;q=0.9'}
                data |= {'execution': execution, '_eventId': 'submit', 'geolocation': ''}
                login = requests.post(url, data=data, headers=header, verify=False)
                assert login.status_code == 200

    @story('150099 已开启登录即时创建用户-自动绑定：CAS成员绑定已有系统账号（状态未激活）')
    def test_bind_inactive_user(self):
        data = {'username': 'chunwei', 'password': 'Aa123456'}

        with step('通过CAS登录成员A'):
            # 绑定不成功
            param = self.get_param(data)
            r = self.call(api.SsoLogin, param, status_code=404)
            assert 'NotFound.ThirdPartyUser' in r.text()

        with step('进入个人中心-绑定第三方集成'):
            param = self.get_param(data)
            self.call(api.ThirdUserBind, param)

        with step('解除绑定cas账号'):
            q = t.third_user_unbind(Tdt.cas)[0]
            self.call(api.ThirdUserUnbind, q)

    @story('149927 已开启登录即时创建用户：CAS中成员缺失邮箱信息')
    def test_bind_user_without_mailbox(self):
        data = {'username': 'emailno', 'password': 'Aa123456'}

        with step('通过CAS登录成员A'):
            # 绑定不成功
            param = self.get_param(data)
            r = self.call(api.SsoLogin, param, status_code=404)
            assert 'NotFound.ThirdPartyUser' in r.text()

    @story('149885 已开启登录即时创建用户：CAS中成员邮箱在ONES中不存在')
    def test_user_email_no_ones(self):
        data = {'username': 'cas_ones_test_1', 'password': 'Aa123456'}

        with step('通过CAS登录成员A'):
            # 绑定不成功
            param = self.get_param(data)
            r = self.call(api.SsoLogin, param, status_code=404)
            assert 'NotFound.ThirdPartyUser' in r.text()

        with step('进入个人中心-绑定第三方集成'):
            param = self.get_param(data)
            self.call(api.ThirdUserBind, param)

        with step('解除绑定cas账号'):
            q = t.third_user_unbind(Tdt.cas)[0]
            self.call(api.ThirdUserUnbind, q)

    @story('150082 已开启登录即时创建用户-自动绑定：CAS成员绑定已有系统账号（状态正常）')
    def test_bind_normal_user(self):
        data = {'username': 'cas_ones_test_2', 'password': 'Aa123456'}

        with step('通过CAS登录成员A'):
            # 绑定不成功
            param = self.get_param(data)
            r = self.call(api.SsoLogin, param, status_code=404)
            assert 'NotFound.ThirdPartyUser' in r.text()

        with step('进入个人中心-绑定第三方集成'):
            param = self.get_param(data)
            self.call(api.ThirdUserBind, param)

        with step('解除绑定cas账号'):
            q = t.third_user_unbind(Tdt.cas)[0]
            self.call(api.ThirdUserUnbind, q)
