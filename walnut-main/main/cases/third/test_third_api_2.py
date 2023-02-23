from falcons.check import Checker, go
from falcons.com.nick import feature, step, parametrize, fixture, story

from main.api import third as api
from main.environ import ThirdPartyType as Tdt
from main.params import third as p


# 重置api mock数据
@fixture(scope='module', autouse=True)
def api_reset():
    param = p.user_me()[0]
    go(api.FakeApiReset, param)


# 添加第三方api
@fixture(autouse=True)
def add_third_api():
    param = p.third_api_add()[0]
    go(api.ThirdAddOrUpdate, param)


# 移除api数据
@fixture(autouse=True)
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
    depart_uuids = [n['uuid'] for n in q.json()['data']['departments'] if n['name'] == 'API' or '企业微信' in n['name']]

    if len(depart_uuids) >= 1:
        data = p.user_me()[0]
        for i in depart_uuids:
            data.uri_args({'depart_uuid': i})
            go(api.DeleteDepartment, data)


@feature('第三方集成-API')
class TestThirdApiTwo(Checker):

    def enable_sync(self, token=None):
        """开启同步"""
        prm = p.third_update('sync', Tdt.api)[0]
        self.call(api.ThirdStatusUpdate, prm, token)

    def depart_member(self, token=None):
        # 查询部门信息
        param = p.org_department()[0]
        q = self.call(api.OrgDepartment, param, token)

        depart_uuid = [n['uuid'] for n in q.json()['data']['departments'] if n['name'] == 'API'][0]  # 获取API部门uuid
        uuids = [n['uuid'] for n in q.json()['data']['departments'] if n['sync_type'] == Tdt.api]  # 获取depart所有uuid

        # 查询部门成员
        prm = p.department_member()[0]
        prm.json['variables']['selectedDepartments'] = uuids
        prm.uri_args({'depart_uuid': depart_uuid})
        data = self.call(api.DepartmentMember, prm, token)

        return data.json()['data']['buckets'][0]

    @story('个人中心：检查绑定信息（移除集成后再添加集成）')
    @parametrize('param', p.third_api_add())
    def test_move_and_add(self, param):
        with step('开启用户目录同步'):
            self.enable_sync()

        with step('移除：API 同步'):
            prm = p.third_remove(Tdt.api)[0]
            self.call(api.ThirdRemove, prm)

        with step('重新添加API 同步'):
            self.call(api.ThirdAddOrUpdate, param)

            # 检查个人中心-API同步信息显示
            bind_p = p.third_user_bindings()[0]
            b = self.call(api.ThirdUserBindings, bind_p)
            assert b.json()[0]['is_bind'] == False

    @story('151151 添加第三方集成：请求接口 URL参数校验')
    @parametrize('param', p.third_api_add())
    def test_api_add(self, param):
        with step('不输入请求接口 URL'):
            param.json['json_config'] = "{\"user_id\":\"userid\",\"api_url\":\"\"}"
            self.call(api.ThirdAddOrUpdate, param, status_code=400)

        with step('输入错误的请求接口 URL'):
            param.json['json_config'] = "{\"user_id\":\"userid\",\"api_url\":\"http://119.23.154.208\"}"
            self.call(api.ThirdAddOrUpdate, param, status_code=400)

    @story('151144 重复添加API 同步集成')
    @parametrize('param', p.third_api_add())
    def test_api_repeat_add(self, param):
        with step('重复添加'):
            self.call(api.ThirdAddOrUpdate, param)  # 接口可重复添加，ui无法重复添加

    @story('151296 编辑基础信息：添加全部用户属性映射后，检查添加更多属性入口')
    @story('151155 编辑基础信息：添加全部用户属性映射后，检查添加更多属性入口')
    @story('149908 编辑基础信息：添加全部用户属性映射后，检查添加更多属性入口')
    @parametrize('param', p.third_api_add())
    def test_add_attribute(self, param):
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

    @story('添加API 同步：添加全部用户属性映射后，检查添加更多属性入口')
    @parametrize('param', p.third_api_add())
    def test_sync_add_attrib(self, param):
        with step('开启用户目录同步'):
            self.enable_sync()

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

    @story('151188 API开启用户目录同步（其他第三方集成已开启登录即时创建成员）')
    @parametrize('param', p.third_update('sync', Tdt.api))
    def test_api_sync_and_other_instant_login(self, param):
        with step('前置条件'):
            # 添加第三方集成 cas
            prm = p.cas_add()[0]
            self.call(api.ThirdAddOrUpdate, prm)
            # 启用cas登录认证
            prm = p.third_update('login', Tdt.cas)[0]
            self.call(api.ThirdStatusUpdate, prm)
            # 启用cas登录即时创建
            prm = p.login_create_member(Tdt.cas)[0]
            self.call(api.ThirdLoginUpdate, prm)

        with step('开启api用户目录同步'):
            r = self.call(api.ThirdStatusUpdate, param, status_code=403)
            r.check_response('third_party_type', Tdt.cas)

    @story('151187 API开启用户目录同步（其他第三方集成已开启用户目录同步）')
    @parametrize('param', p.third_update('sync', Tdt.api))
    def test_api_sync_and_other_enable_sync(self, param):
        with step('前置条件'):
            # 添加第三方集成 企微
            prm = p.wechat_add()[0]
            self.call(api.ThirdAddOrUpdate, prm)

            # 企微启动用户目录同步
            sync_p = p.third_update('sync', Tdt.wechat_app)[0]
            self.call(api.ThirdStatusUpdate, sync_p)

        with step('开启api用户目录同步'):
            r = self.call(api.ThirdStatusUpdate, param, status_code=403)
            r.check_response('third_party_type', Tdt.wechat_app)

    @story('151192 API 同步详情页：点击同步（第三方移除成员）')
    @parametrize('param', p.third_pull(Tdt.api))
    def test_move_user_and_sync(self, param):
        with step('前置条件'):
            # 开启api用户目录同步
            self.enable_sync()
            # 将api中成员A删除
            prm = p.fake_api_del()[0]
            self.call(api.FakeApiDelete, prm)

        with step('删除api成员后，点击同步'):
            self.call(api.ThirdPull, param)

        with step('进入成员管理, 成员列表无：成员A'):
            data = self.depart_member()
            uuids = [u['uuid'] for u in data['users']]
            assert 'wukong' not in uuids

    @story('开启用户目录同步（API 同步被移除）')
    @parametrize('param', p.third_update('sync', Tdt.api))
    def test_move_api_and_sync(self, param):
        with step('第三方集成「API 同步」被移除'):
            prm = p.third_remove(Tdt.api)[0]
            go(api.ThirdRemove, prm)

        with step('开启用户目录同步'):
            self.call(api.ThirdStatusUpdate, param, status_code=404)

    @story('T151193 点击同步（用户目录同步被关闭）')
    @parametrize('param', p.third_pull(Tdt.api))
    def test_close_sync_back_enable(self, param):
        with step('点击同步'):
            pull = self.call(api.ThirdPull, param, status_code=403)
            pull.check_response('errcode', 'AccessDenied.ThirdPartySetting.DisabledSync')

    @story('151199 点击同步（API中成员缺失邮箱信息）')
    @parametrize('param', p.third_pull(Tdt.api))
    def test_no_mail_sync(self, param):
        with step('开启用户目录同步，增加api无邮箱成员'):
            self.enable_sync()

            # 新增无邮箱成员
            prm = p.fake_api_members_add()[0]
            self.call(api.FakeApiAdd, prm)

        with step('点击同步'):
            self.call(api.ThirdPull, param)

        # with step('进入成员管理'):
        #     assert '成员列表无：成员状态：未激活  ToDo: 接口暂有问题，无邮箱的用户无法同步

    @story('151206 关闭用户目录同步')
    @parametrize('param', p.third_update('sync', Tdt.api))
    def test_close_sync(self, param):
        with step('前置条件'):
            # 开启用户目录同步
            self.call(api.ThirdStatusUpdate, param)

        with step('关闭同步'):
            prm = p.third_update('sync', Tdt.api, enable=False)[0]
            self.call(api.ThirdStatusUpdate, prm)

        with step('进入成员管理-成员A详情'):
            # 成员A无「API 标识」
            data = self.depart_member()
            sync_types = data['users'][0]['sync_types']
            assert sync_types == []
