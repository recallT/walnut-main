"""
@File    ：test_third_ldap.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/18
@Desc    ： 三方认证- LDAP 配置测试
"""
import json as jsn

from falcons.check import Checker, go
from falcons.com.env import User
from falcons.com.nick import feature, story, parametrize, step, fixture
from falcons.com.ones import api_login

from main.api import auth
from main.api import project as prj
from main.api import third as api
from main.environ import ThirdPartyType as Tdt
from main.params import third as p

"""
zeno_a 绑定三方
zeno_abc@ones.ai 已有账户

zeno_ee 同邮箱三方 密码 imok0000   切换测试环境后，需要先邀请激活这个用户 zeno_ee@ones.ai

zeno_c 存在未激活邮箱 绑定 ；有工号 c020beb36950416fb16a6dc5ea48255c001
zeno_d 三方无邮箱用户1 用来绑定新邮箱用户 zeno_new@ones.ai
zeno_f 三方无邮箱用户2
"""


@fixture(scope='module', autouse=True)
def invite_zeno_c():
    """邀请一个测试用户，未激活状态"""
    print('邀请 zeno_c@ones.ai，处于未激活状态')
    invite_p = p.invite_c()[0]
    try:
        go(prj.InvitationsAdd, invite_p)
    except Exception as e:
        go(prj.InvitationsAdd, invite_p)


@fixture(scope='module', autouse=True)
def remove_member():
    """测试完成后清理账号"""
    yield
    print('删除 LDAP 绑定用户...')
    email = (f'zeno_{c}@ones.ai' for c in ('a', 'b', 'c', 'd', 'e', 'f'))
    # names = (f'zeno_c',)
    all_p = p.all_member_graph()[0]
    resp = go(prj.ItemGraphql, all_p)

    users = resp.json()['data']['buckets'][0]['users']
    uuids = [u['uuid'] for u in users if u['email'] in email]
    del_p = p.batch_delete_member()[0]

    del_p.json['variables']['selectedUserUUIDs'] = uuids
    go(prj.DeleteMembersBatch, del_p)


@feature('第三方账号-new')
class TestLDAP(Checker):
    """"""

    def ldap_login(self, user: str, code=200):
        """三方登陆步骤"""
        with step('调用LDAP exchange_token 接口'):
            a_login = p.ldap_exchange_token(user)[0]
            resp = self.call(api.LdapExchangeToken, a_login)
            auth_info = {'type': Tdt.ldap, 'token': resp.json()['token']}
        with step('调用三方集成统一登陆接口'):
            sso_login_p = p.sso_login(Tdt.ldap)[0]
            sso_login_p.json['auth_info'] = jsn.dumps(auth_info)
            resp = self.call(api.SsoLogin, sso_login_p, {}, status_code=code)

        return resp

    def update_group_dn(self, j_config: dict, token=None):
        """更新Group DN 配置"""
        # 1.获取配置详情
        detail_p = p.third_detail(Tdt.ldap)[0]
        detail = self.call(api.ThirdDetail, detail_p, token)
        json_config = detail.json()['json_config']

        j = jsn.loads(json_config)
        j |= j_config  # 添加GN配置

        # 2.更新Group DN
        param = p.third_sync_update(Tdt.ldap)[0]
        param.json['json_config'] = jsn.dumps(j, ensure_ascii=False)

        self.call(api.ThirdSyncUpdate, param, token)

    @story('添加LDAP')
    @parametrize('param', p.ldap_add())
    def test_ldap_add(self, param):
        """"""
        self.call(api.ThirdAddOrUpdate, param)

    @story('个人中心-绑定第三方账号：绑定LDAP账号')
    @parametrize('param', p.third_user_bind(Tdt.ldap))
    def test_bind_ldap_in_personal(self, param):
        """
    
        :return:
        """
        with step('Ldap 登陆'):
            # 将zeno_a 绑定到默认 admin 账户上
            zeno_a = p.ldap_exchange_token('zeno_a')[0]
            resp = self.call(api.LdapExchangeToken, zeno_a)

            ldap_token = resp.json()

            ldap_token |= {'type': Tdt.ldap}

            param.json['auth_info'] = jsn.dumps(ldap_token)

        with step('绑定LDAP账号'):
            self.call(api.ThirdUserBind, param)

        with step('检查绑定结果'):
            unbind_p = p.third_user_bindings()[0]
            resp = self.call(api.ThirdUserBindings, unbind_p)
            # 检查Ldap 绑定id 为zeno_a
            ldap_bind = [r for r in resp.json() if r['third_party_type'] == Tdt.ldap][0]

            assert ldap_bind['third_party_id'] == 'zeno_a'
            assert ldap_bind['is_bind']

    @story('147736 LDAP：复制登录链接访问')
    def test_copy_login_link(self):
        """登陆链接由前端拼接，接口验证能开启登陆认证即可"""
        pass

    # ----
    @story('147852 LDAP：开启用户目录同步情况下，删除LDAP成员')
    @parametrize('param', p.batch_delete_member())
    def test_sync_enabled_and_delete_user(self, param):
        """"""
        # 获取用户列表，提取ldap用户的uuid
        with step('获取用户列表'):
            all_p = p.all_member_graph(is_pending=True)[0]
            resp = go(prj.ItemGraphql, all_p)

            # 获取未被绑定的ldap用户UUID
            users = resp.json()['data']['buckets'][0]['users']
            uuids = {u['uuid']: u['directDepartments'][0]['name'] for u in users if u['directDepartments']}
            uuid = [k for k, v in uuids.items() if v == 'z1']
        with step('删除成员接口'):
            del_p = p.batch_delete_member()[0]
            del_p.json['variables']['selectedUserUUIDs'] = uuid
            del_resp = go(prj.DeleteMembersBatch, del_p)

        with step('检查成员，未被删除'):
            del_resp.check_response('fail_count', len(uuid))

    @story('147848 LDAP：未开启用户目录同步情况下，删除绑定了LDAP的成员')
    @parametrize('param', p.batch_delete_member())
    def test_disable_sync_and_unbind_user(self, param):
        """"""
        # 关闭用户目录同步
        with step('禁用用户目录同步'):
            sync_p = p.third_update('sync', Tdt.ldap, False)[0]
            self.call(api.ThirdStatusUpdate, sync_p)
        # 获取用户列表，提取ldap用户的uuid
        with step('获取用户列表'):
            all_p = p.all_member_graph(is_pending=True)[0]
            resp = go(prj.ItemGraphql, all_p)

            users = resp.json()['data']['buckets'][0]['users']
            uuids = [u['uuid'] for u in users if u['name']]
            del_p = p.batch_delete_member()[0]

        # 删除成员接口
        del_p.json['variables']['selectedUserUUIDs'] = uuids
        del_resp = go(prj.DeleteMembersBatch, del_p)

        # 检查成员，删除成功
        del_resp.check_response('success_count', len(uuids))

    @story('147713 LDAP禁用用户目录同步')
    @parametrize('param', p.third_update('sync', Tdt.ldap, False))
    def test_disable_sync_user_dir(self, param):
        """"""

        with step('点击「禁用」'):
            self.call(api.ThirdStatusUpdate, param)

    @story('147453 LDAP启用用户目录同步')
    @parametrize('param', p.third_update('sync', Tdt.ldap))
    def test_enable_sync_user_dir(self, param):
        """"""

        with step('点击「启用」'):
            self.call(api.ThirdStatusUpdate, param)

            # 上一个用户删除了用户，此处重新同步一下
            pull_p = p.third_pull(Tdt.ldap)[0]
            self.call(api.ThirdPull, pull_p)

    @story('147849 LDAP开启用户目录同步情况下，开启登录认证')
    @parametrize('param', p.third_update('login', Tdt.ldap))
    def test_enable_sync_user_dir_and_login(self, param):
        """
        1、有组织管理员权限
        2、已添加LDAP，开启用户目录同步和登录认证
        3、LDAP包含「部门1」下成员A（邮箱A），成员B（邮箱B），成员C（无邮箱），成员D（无邮箱）
        4、系统存在加入「ONES团队1」「ONES团队2」第三方账号正常状态的成员A和未激活的成员D
        5、进入组织管理-第三方集成
        ldap 中有 ones_a, ones_b, ones_c, ones_d, 四个成员 ones_d 无邮箱
        :param param:
    
        :return:
        """
        with step('LDAP开启用户目录同步'):
            """"""
            # 这里需要检查其他集成类型已经开启了登陆即创建成员开关
            # 如果有，需要先关闭
            step1_p = p.third_list()[0]
            third_list = self.call(api.ThirdList, step1_p)
            # 获取已开启用户目录同步的三方类型
            enabled = [r for r in third_list.json()['results'] if r['sync_enabled']]
            print(enabled)
            if enabled:
                tpt = enabled[0]['third_party_type']
                if tpt != Tdt.ldap:  # 先关闭其他三方目录同步
                    close_ = p.third_update('sync', tpt, False)
                    self.call(api.ThirdStatusUpdate, close_)

                    open_ = p.third_update('sync', Tdt.ldap)[0]
                    self.call(api.ThirdStatusUpdate, open_)
            else:
                open_ = p.third_update('sync', Tdt.ldap)[0]
                self.call(api.ThirdStatusUpdate, open_)

        with step('开启登录认证'):
            self.call(api.ThirdStatusUpdate, param)

        with step('成员登陆'):
            """TODO 使用每个成员登陆"""

            # self.call(api.LdapExchangeToken)

    @story('147813 LDAP登录绑定账号：开启用户目录同步，LDAP登录绑定新建系统账号')
    @parametrize('param', p.sso_verify_email('zeno_new'))
    def test_login_and_bind_new_account(self, param):
        """借 147849 为前提"""
        resp_403 = self.ldap_login('zeno_d', 403)

        # 拿到认证的auth_code 信息 用于绑定新的邮箱账号
        auth_code = resp_403.json()['auth_code']

        # 认证新的绑定邮箱
        param.json['auth_code'] = auth_code
        self.call(api.SsoVerifyEmail, param)
        # TODO 后边还有验证步骤，由于获取不了email_code 暂不实施
        #  这里表里 third_party_auth_info, 根据前面的auth_code 查

    @story('LDAP登录绑定账号：未被绑定的LDAP成员扫码登录')
    def test_no_email_user_login(self):
        """"""
        with step('使用未绑定邮箱的ldap账号登陆'):
            self.ldap_login('zeno_f', 403)

    @story('LDAP勾选匹配邮箱相同的系统账号，开启登录即时创建成员')
    @parametrize('param', p.ldap_exchange_token('zeno_ee'))
    def test_same_email_user_login(self, param):
        """"""
        # 这里是几类登陆用户同时验证，其他用例已经覆盖

    @story('147495 LDAP-添加LDAP：添加用户属性映射')
    @parametrize('param', p.third_update_mapping_ldap(Tdt.ldap))
    def test_add_user_property_mapping(self, param):
        """"""
        # 1.获取原来的配置详情
        with step('获取配置详情'):
            detail_p = p.third_detail(Tdt.ldap)[0]
            detail = self.call(api.ThirdDetail, detail_p)
            json_config = detail.json()['json_config']

            # 2. 获取字段映射配置
            mapping_list = self.call(api.ThirdMappingList, detail_p)
            mapping = [{
                'system_property_key': m['system_property_key'],
                'third_party_property_key': m['third_party_property_key'],
            } for m in mapping_list.json()]
            # 这里将 ldap的 email 改为 mail
            for m in mapping:
                if m['system_property_key'] == 'email':
                    m['third_party_property_key'] = 'mail'

            is_id_exists = [m for m in mapping if m['system_property_key'] == 'id_member']

        # 3.修改组织单元过滤规则
        with step('添加用户属性映射'):
            m = param.json['mappings']
            if not is_id_exists:
                m += mapping  # 将原映射配置添加
            else:
                print('已经添加工号映射。。。')
                param.json['mappings'] = mapping  # 如果添加了，保持原样

            param.json |= {'json_config': json_config, }
            self.call(api.ThirdAddOrUpdate, param)

    @story('147865 LDAP-编辑基本信息：添加用户属性映射')
    def test_edit_user_mapping(self):
        """依赖上条用例 test_add_user_property_mapping"""
        with step('同步用户信息'):
            pull_p = p.third_pull(Tdt.ldap)[0]
            self.call(api.ThirdPull, pull_p)

        def _check_id_number(name, id_number):
            with step('访问环境，点击LDAP，通过LDAP登录'):
                """"""
                resp = self.ldap_login(name)
                u = resp.json()['user']
                assert u['email'] == f'{name}@ones.ai'
            with step('使用系统token进入系统'):
                cc_token = {'Ones-User-Id': u['uuid'], 'Ones-Auth-token': u['token']}
                bind_p = p.third_user_bindings()[0]
                resp = self.call(api.ThirdUserBindings, bind_p, cc_token)
                ldap_bind = [r for r in resp.json() if r['third_party_type'] == Tdt.ldap][0]

                assert ldap_bind['third_party_id'] == name
            with step('有团队权限的成员进入成员管理页面，查看成员ID'):
                me_p = p.user_me()[0]
                me_resp = self.call(prj.UsersMe, me_p, cc_token)

                me_resp.check_response('id_number', id_number)

        #  zeno_c 登陆
        _check_id_number('zeno_c', 'c020beb36950416fb16a6dc5ea48255c')  # c 配置了工号
        #  zeno_a 登陆
        _check_id_number('zeno_a', '')

        with step('再次同步同步用户信息'):
            pull_p = p.third_pull(Tdt.ldap)[0]
            self.call(api.ThirdPull, pull_p)

    @story('LDAP登录绑定账号：开启用户目录同步，扫码绑定状态正常的系统账号')
    @parametrize('param', p.ldap_exchange_token('zeno_abc'))
    def test_bind_normal_user(self, param):
        """"""
        """借 147849 为前提"""
        resp_403 = self.ldap_login('zeno_d', 403)

        # 拿到认证的auth_code 信息 用于绑定新的邮箱账号
        auth_code = resp_403.json()['auth_code']

        # 认证新的绑定邮箱
        param.json['auth_code'] = auth_code
        self.call(api.SsoVerifyEmail, param)
        # TODO 后边还有验证步骤，由于获取不了email_code 暂不实施
        #  这里表里 third_party_auth_info, 根据前面的auth_code 查

    @story('LDAP登录绑定账号：开启登录即时创建成员，LDAP登录绑定状态正常的系统账号')
    @parametrize('param', p.ldap_exchange_token('zeno_b'))
    def test_enable_login_create_user_then_bind_normal_user(self, param):
        """和test_bind_normal_user 一样的步骤"""

    @story('147815 绑定相同邮箱的成员解除绑定LDAP后，再次用户目录同步，查看绑定信息')
    def test_same_mail_member(self):
        """依赖上一条用例 开启用户目录同步和登陆认证"""
        with step('同步LDAP'):
            """"""
            pull_p = p.third_pull(Tdt.ldap)[0]
            self.call(api.ThirdPull, pull_p)

        ee_p = p.third_user_bindings()[0]
        # 这里使用 zeno_ee 用户登陆， 邮箱与ldap zeno_ee 的邮箱相同
        ee_token = api_login(User('zeno_ee@ones.ai', 'imok0000'))

        with step('查看个人绑定信息'):
            """"""
            resp = self.call(api.ThirdUserBindings, ee_p, ee_token)
            ldap_bind = [r for r in resp.json() if r['third_party_type'] == Tdt.ldap][0]

            assert ldap_bind['third_party_id'] == 'zeno_ee', '相同邮箱用户未自动绑定 zeno_ee'

        with step('解除个人绑定'):
            """"""
            unbind_p = p.third_user_unbind(Tdt.ldap)[0]
            self.call(api.ThirdUserUnbind, unbind_p, ee_token)

        with step('查看解绑结果'):
            """"""
            resp = self.call(api.ThirdUserBindings, ee_p, ee_token)
            ldap_bind = [r for r in resp.json() if r['third_party_type'] == Tdt.ldap][0]

            assert ldap_bind['third_party_id'] == ''

    @story('147857 登录即时创建成员：匹配到未激活邮箱成员，检查LDAP成员通过LDAP登录')
    @parametrize('param', p.ldap_exchange_token('zeno_c'))
    def test_has_inactive_mail_member(self, param):
        """"""
        # 直接使用未激活邮箱的 zeno_c 登陆
        with step('访问环境，点击LDAP，通过LDAP登录'):
            """"""
            resp = self.ldap_login('zeno_c')
            u = resp.json()['user']
            assert u['email'] == 'zeno_c@ones.ai'

        with step('使用系统token进入系统'):
            cc_token = {'Ones-User-Id': u['uuid'], 'Ones-Auth-token': u['token']}
            bind_p = p.third_user_bindings()[0]
            resp = self.call(api.ThirdUserBindings, bind_p, cc_token)
            ldap_bind = [r for r in resp.json() if r['third_party_type'] == Tdt.ldap][0]

            assert ldap_bind['third_party_id'] == 'zeno_c'
        with step('有团队权限的成员进入成员管理页面，查看成员A'):
            me_p = p.user_me()[0]
            me_resp = self.call(prj.UsersMe, me_p, cc_token)

            me_resp.check_response('name', 'zeno_c')
            me_resp.check_response('email', 'zeno_c@ones.ai')

    @story('勾选匹配邮箱相同账号，开启用户目录同步（LDAP成员已加入团队），检查LDAP成员进入组织情况')
    @parametrize('param', p.all_member_graph())
    def test_same_mail_member_check_org(self, param):
        """
    
        :return:
        """
        # zeno_d 无邮箱 未激活，zeno_a 正常
        with step('进入「ONES团队」-成员管理页面-检查成员状态A B 激活 D为未激活'):
            """"""
            resp = self.call(prj.ItemGraphql, param)
            users = [r for r in resp.json()['data']['buckets'][0]['users']]

            user_a = [u for u in users if u['name'] == 'zeno_a'][0]
            user_d = [u for u in users if u['name'] == 'zeno_d'][0]

            assert user_a['team_member_status'] == 1
            assert user_d['team_member_status'] == 3

    @story('LDAP启用登录认证')
    @parametrize('param', p.third_update('login', Tdt.ldap))
    def test_enable_login(self, param):
        """"""
        with step('LDAP启用登录认证'):
            self.call(api.ThirdLoginUpdate, param)

        with step('出现LDAP/AD登录入口'):
            support_param = p.third_support_list()[0]
            login_types = self.call(auth.AuthLoginTypes, support_param)

            assert Tdt.ldap in login_types.json()['third_party_login_types']

    @story('LDAP禁用登录即时创建成员！')
    @parametrize('param', p.login_create_member(Tdt.ldap, False))
    def test_disable_login_create_user(self, param):
        """依赖上一条用例 test_enable_login"""

        with step('禁用登陆即创建成员'):
            update = self.call(api.ThirdLoginUpdate, param)
            update.check_response('type', 'OK')
        with step('成员A通过LDAP登录-成功'):
            self.ldap_login('zeno_a')
        with step('成员D通过LDAP登录-失败'):
            self.ldap_login('zeno_d', 403)

    @story('LDAP编辑登录即时创建成员')
    @parametrize('param', p.login_create_member(Tdt.ldap))
    def test_login_create_member(self, param):
        """"""
        with step('开启登陆即创建成员 团队A'):
            update = self.call(api.ThirdLoginUpdate, param)
            update.check_response('type', 'OK')
        with step('成员B通过LDAP登录'):
            # 校验成员能够登陆
            p1 = p.ldap_exchange_token('zeno_a')[0]
            resp = self.call(api.LdapExchangeToken, p1)
            # 成员拿到token成功

        with step('开启登陆即创建成员 团队B'):
            update = self.call(api.ThirdLoginUpdate, param)
            update.check_response('type', 'OK')

        # TODO 这里要解决 在LDAP自动添加成员的方法
        with step('成员C通过LDAP登录'):
            # 校验成员能够登陆
            p1 = p.ldap_exchange_token('zeno_c')[0]
            resp = self.call(api.LdapExchangeToken, p1)
            # 成员拿到token成功

    @story('147463 LDAP未开启用户目录同步，启用登录即时创建成员')
    @parametrize('param', p.login_create_member(Tdt.ldap))
    def test_disable_sync_use_enable_login_create(self, param):
        """"""

        # 1、有组织管理员权限
        # 2、已添加LDAP，未启用用户目录同步，已启用登录认证
        # 3、第三方集成中不存在其他第三方开启用户目录同步或登录即时创建成员
        # 4、进入组织管理-第三方集成-LDAP

        update = self.call(api.ThirdLoginUpdate, param)

    @story('147508 LDAP：开启Group同步')
    def test_enable_group(self):
        """"""
        # 1. 添加group dn 规则
        with step('开启Group 同步'):
            """"""
            j_config = {'domain_group_base': 'ou=z1,ou=zeno,dc=ldap,dc=example,dc=com'}
            self.update_group_dn(j_config)

        # 2. 同步
        with step('返回第三方集成>LDAP/AD，点击「同步」'):
            """"""
            pull_p = p.third_pull(Tdt.ldap)[0]
            self.call(api.ThirdPull, pull_p)
        # 3. 检查部门信息
        with step('进入组织管理-团队管理-「ONES团队」-编辑，查看部门'):
            """"""

    @story('LDAP-编辑同步配置：修改Group DN')
    def test_modify_group_dn(self):
        """"""
        j_config = {'domain_group_base': 'ou=z1,ou=zeno,dc=ldap,dc=example,dc=com'}
        self.update_group_dn(j_config)

    @story('LDAP禁用登录认证')
    @parametrize('param', p.third_update('login', Tdt.ldap, enable=False))
    def test_disable_use_login(self, param):
        """"""
        with step('LDAP禁用登录认证'):
            self.call(api.ThirdStatusUpdate, param)

        with step('无LDAP登录入口'):
            support_param = p.third_support_list()[0]
            login_types = self.call(auth.AuthLoginTypes, support_param)

            assert Tdt.ldap not in login_types.json()['third_party_login_types']

    @story('个人中心-绑定第三方账号：解除绑定LDAP账号')
    @parametrize('param', p.third_user_unbind(Tdt.ldap))
    def test_unbind_ldap_in_personal_center(self, param):
        """
    
        :return:
        """
        with step('解除绑定LDAP账号'):
            self.call(api.ThirdUserUnbind, param)

        with step('检查解除绑定结果'):
            unbind_p = p.third_user_bindings()[0]
            resp = self.call(api.ThirdUserBindings, unbind_p)
            # 检查Ldap 绑定信息为空
            ldap_bind = [r for r in resp.json() if r['third_party_type'] == Tdt.ldap][0]
            assert not ldap_bind['third_party_id']

    @story('147495 LDAP-编辑同步配置：修改组织单元过滤规则')
    @parametrize('param', p.third_add_or_update(Tdt.ldap))
    def test_modify_group_pattern(self, param):
        """"""
        # 1.获取配置详情
        with step('获取配置详情'):
            detail_p = p.third_detail(Tdt.ldap)[0]
            detail = self.call(api.ThirdDetail, detail_p)
            json_config = detail.json()['json_config']

            # 2. 获取字段映射配置
            mapping_list = self.call(api.ThirdMappingList, detail_p)
            mapping = [{
                'system_property_key': m['system_property_key'],
                'third_party_property_key': m['third_party_property_key'],
            } for m in mapping_list.json()]

        # 3.修改组织单元过滤规则
        with step('修改组织单元过滤规则'):
            j = jsn.loads(json_config)
            j |= {'user_filter': '(|(objectclass=organizationalUnit))'}  # 单元过滤规则

            param.json |= {'json_config': jsn.dumps(j, ensure_ascii=False),
                           'mappings': mapping,
                           }
            self.call(api.ThirdAddOrUpdate, param)

    @story('147470 用户目录同步的情况下，移除LDAP')
    @parametrize('param', p.third_remove(Tdt.ldap))
    def test_ldap_remove(self, param):
        """"""
        # # 这条用例看最后需不需要执行
        self.call(api.ThirdRemove, param)
        with step('进入「ONES团队」-成员管理-不存在成员B'):
            """"""
        with step('成员A登录系统，进入个人中心-第三方集成-不存在LDAP'):
            """"""
            unbind_p = p.third_user_bindings()[0]
            resp = self.call(api.ThirdUserBindings, unbind_p)
            # 检查Ldap 绑定信息为空
            ldap_bind = [r for r in resp.json() if r['third_party_type'] == Tdt.ldap]
            assert not ldap_bind
