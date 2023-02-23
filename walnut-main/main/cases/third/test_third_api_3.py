from falcons.check import Checker, go
from falcons.com.nick import feature, step, parametrize, fixture, story

from main.api import project as prj
from main.api import third as api
from main.environ import ThirdPartyType as Tdt
from main.params import auth
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
    depart_uuids = [n['uuid'] for n in q.json()['data']['departments'] if n['name'] == 'API' or n['name'] == 'add_test'
                    or n['name'] == 'RenameApi']

    if len(depart_uuids) >= 1:
        data = p.user_me()[0]
        for i in depart_uuids:
            data.uri_args({'depart_uuid': i})
            go(api.DeleteDepartment, data)


@feature('第三方集成-API')
class TestThirdApiThree(Checker):

    def enable_sync(self, token=None):
        """开启同步"""
        prm = p.third_update('sync', Tdt.api)[0]
        self.call(api.ThirdStatusUpdate, prm, token)

    def depart_member(self, token=None):
        # 查询API部门信息
        param = p.org_department()[0]
        q = self.call(api.OrgDepartment, param, token)

        depart_uuid = [n['uuid'] for n in q.json()['data']['departments'] if n['name'] == 'API'][0]  # 获取API部门uuid
        uuids = [n['uuid'] for n in q.json()['data']['departments'] if n['sync_type'] == Tdt.api]  # 获取depart所有uuid

        # 查询API部门成员
        prm = p.department_member()[0]
        prm.json['variables']['selectedDepartments'] = uuids
        prm.uri_args({'depart_uuid': depart_uuid})
        data = self.call(api.DepartmentMember, prm, token)

        return data.json()['data']['buckets'][0]

    def unknown_depart(self, token=None):
        # 查询未分配部门信息
        param = p.org_department()[0]
        q = self.call(api.OrgDepartment, param, token)

        depart_uuid = [n['uuid'] for n in q.json()['data']['departments'] if n['name'] == '未分配部门']  # 获取API部门uuid

        # 查询未分配部门成员
        prm = p.department_member()[0]
        prm.json['variables']['selectedDepartments'] = depart_uuid
        data = self.call(api.DepartmentMember, prm, token)

        return data.json()['data']['buckets'][0]

    def depart_info(self, member_status='disable'):
        """
        :param token
        :param member_status: 成员状态 默认disable(禁用)/pending(未激活)
        """

        # 查询部门成员
        prm = p.department_info()[0]
        prm.json['variables']['memberStatus'] = [f'{member_status}']
        data = self.call(api.DisabledDepartment, prm)

        return data.json()['data']['buckets'][0]

    @story('151205 点击同步（API中成员邮箱未绑定ONES成员）')
    @parametrize('param', p.third_pull(Tdt.api))
    def test_no_mail_sync(self, param):
        self.enable_sync()

        with step('点击同步'):
            self.call(api.ThirdPull, param)

        with step('成员A详情'):
            data = self.depart_member()
            # 检查成员状态：正常
            status = data['users'][0]['team_member_status']
            assert status == 1

    @story('151207 点击同步（API中成员邮箱匹配已禁用的ONES成员）')
    def test_system_disabled_member_sync(self):
        with step('禁用ONES系统成员A'):
            data = self.unknown_depart()
            uuid = [u['uuid'] for u in data['users'] if u['name'] == '齐天大圣']

            # 禁用成员
            prm = p.disable_members()[0]
            prm.json['members'] = uuid
            self.call(prj.DisableMembers, prm)

            # 检查成员状态：禁用
            d = self.depart_info()
            status = [n['team_member_status'] for n in d['users'] if n['name'] == '齐天大圣'][0]  # 获取禁用测试用户的status
            assert status == 4

        with step('开启同步'):
            self.enable_sync()

            data = self.depart_member()
            # 检查成员状态：正常
            status = [n['team_member_status'] for n in data['users'] if n['name'] == '齐天大圣'][0]
            assert status == 1

    @story('151208 点击同步（API中成员邮箱匹配已删除的ONES成员）')
    def test_system_del_member_sync(self):
        with step('删除ONES系统成员A'):
            data = self.unknown_depart()
            uuid = [u['uuid'] for u in data['users'] if u['name'] == '齐天大圣'][0]

            # 删除成员
            prm = p.delete_member()[0]
            prm.json['member'] = uuid
            self.call(prj.DeleteMember, prm)

            # 检查成员状态：已被删除
            d = self.depart_info()
            names = [n['name'] for n in d['users']]
            assert '齐天大圣' not in names

        with step('开启同步'):
            self.enable_sync()

            data = self.depart_member()
            # 检查成员A存在且状态正常
            status = [n['team_member_status'] for n in data['users'] if n['name'] == '齐天大圣'][0]
            assert status == 1

    @story('151212 已开启用户目录同步，删除成员')
    def test_enable_sync_del_member(self):
        self.enable_sync()

        with step('删除成员'):
            # 获取未激活成员uuid
            data = self.depart_info(member_status='pending')
            uuids = [u['uuid'] for u in data['users'] if u['sync_types'] == [Tdt.api]]

            param = p.batch_delete_member()[0]
            param.json['variables']['selectedUserUUIDs'] = uuids
            d = self.call(prj.DeleteMembersBatch, param)
            # 校验无法删除开启同步的成员
            d.check_response('fail_count', len(uuids))

    @story('151213 已开启用户目录同步，批量删除成员')
    def test_enable_sync_system_unbound_member(self):
        with step('前置条件'):
            # 开启同步
            self.enable_sync()

            # 邀请新成员到团队
            param = auth.invitation()[0]
            self.call(prj.InvitationsAdd, param)

        with step('批量删除成员'):
            # 获取未激活成员uuid
            data = self.depart_info(member_status='pending')
            all_uuids = [u['uuid'] for u in data['users']]
            uuids = [u['uuid'] for u in data['users'] if u['sync_types'] == [Tdt.api]]

            param = p.batch_delete_member()[0]
            param.json['variables']['selectedUserUUIDs'] = all_uuids
            d = self.call(prj.DeleteMembersBatch, param)
            # 校验无法删除开启同步的成员
            d.check_response('fail_count', len(uuids))

    @story('151214 未开启用户目录同步，删除成员')
    def test_not_enable_sync_del_member(self):
        with step('勾选成员A，点击确认删除'):
            # 选择成员A
            data = self.unknown_depart()
            uuid = [u['uuid'] for u in data['users'] if u['name'] == '齐天大圣']

            # 删除成员
            prm = p.batch_delete_member()[0]
            prm.json['variables']['selectedUserUUIDs'] = uuid
            d = self.call(prj.DeleteMembersBatch, prm)
            d.check_response('success_count', len(uuid))

        with step('检查成员列表，无成员A'):
            data = self.unknown_depart()
            names = [u['name'] for u in data['users']]
            assert '齐天大圣' not in names

    @story('151215 已开启用户目录同步，禁用成员')
    @parametrize('param', p.batch_disabled_member())
    def test_enable_sync_disabled_member(self, param):
        self.enable_sync()

        with step('勾选成员，选择禁用'):
            # 选择成员A
            data = self.depart_member()
            uuid = [n['uuid'] for n in data['users'] if n['name'] == '齐天大圣']

            # # 获取departments所有uuid
            prm = p.org_department()[0]
            q = self.call(api.OrgDepartment, prm)
            departments = [n['uuid'] for n in q.json()['data']['departments'] if n['sync_type'] == Tdt.api]

        with step('点击确定'):
            param.json['variables']['selectedUserUUIDs'] = uuid
            param.json['variables']['selectedDepartments'] = departments
            d = self.call(prj.DisableMembers, param)
            # 检查禁用失败
            d.check_response('fail_count', len(uuid))

    @story('151216 未开启用户目录同步，禁用成员')
    @parametrize('param', p.batch_disabled_member())
    def test_not_enable_sync_disabled_member(self, param):
        with step('勾选成员，选择禁用'):
            # 选择成员A
            data = self.unknown_depart()
            uuid = [u['uuid'] for u in data['users'] if u['name'] == '齐天大圣']

            # 获取未分配部门department的uuid
            prm = p.org_department()[0]
            q = self.call(api.OrgDepartment, prm)
            department = [n['uuid'] for n in q.json()['data']['departments'] if n['name'] == '未分配部门']

        with step('点击确定'):
            param.json['variables']['selectedUserUUIDs'] = uuid
            param.json['variables']['selectedDepartments'] = department
            d = self.call(prj.DisableMembers, param)
            # 检查禁用成功
            d.check_response('success_count', len(uuid))

    @story('151218 已开启用户目录同步，将成员加入其他ONES部门')
    @parametrize('param', p.update_department())
    def test_enable_sync_move_member(self, param):
        self.enable_sync()

        with step('勾选成员A，加入部门'):
            data = self.depart_member()
            uuid = [n['uuid'] for n in data['users'] if n['name'] == '齐天大圣']

        with step('选择其他部门'):
            # 获取新增子部门所需的next_uuid
            prm = p.org_department()[0]
            q = self.call(api.OrgDepartment, prm)
            next_uuid = [n['uuid'] for n in q.json()['data']['departments'] if n['parent_uuid'] == ''][0]
            uuids = [n['uuid'] for n in q.json()['data']['departments'] if n['sync_type'] == Tdt.api]  # 获取depart所有uuid

            # 新增部门，获取部门uuid
            pr = p.add_sub_department()[0]
            pr.json['next_uuid'] = next_uuid
            r = self.call(api.ADDSubDepartment, pr)
            depart_uuid = r.json()['add_department']['uuid']

            # 成员A，加入部门
            param.json['departments_to_join'].append(depart_uuid)
            param.json['variables']['selectedUserUUIDs'] = uuid
            param.json['variables']['selectedDepartments'] = uuids
            ud = self.call(api.UpdateDepartment, param)
            ud.check_response('success_count', len(uuid))

    @story('151220 已开启用户目录同步，编辑第三方部门')
    @parametrize('param', p.rename_department())
    def test_enable_sync_edit_department(self, param):
        self.enable_sync()

        with step('编辑第三方部门'):
            # 查询API部门信息
            prm = p.org_department()[0]
            q = self.call(api.OrgDepartment, prm)
            depart_uuid = [n['uuid'] for n in q.json()['data']['departments'] if n['name'] == 'API'][0]

            param.json['uuid'] = depart_uuid
            param.uri_args({'depart_uuid': depart_uuid})
            # self.call(api.RenameDepartment, param)  # API部门前端无编辑入口，接口可进行重命名

    @story('151221 未开启用户目录同步，编辑第三方部门')
    @parametrize('param', p.rename_department())
    def test_not_enable_sync_edit_department(self, param):
        with step('前置条件'):
            # 开启同步
            self.enable_sync()
            # 关闭同步
            prm = p.third_update('sync', Tdt.api, enable=False)[0]
            self.call(api.ThirdStatusUpdate, prm)

        with step('编辑第三方部门'):
            # 查询API部门信息
            prm = p.org_department()[0]
            q = self.call(api.OrgDepartment, prm)
            depart_uuid = [n['uuid'] for n in q.json()['data']['departments'] if n['name'] == 'API'][0]

            # 第三方部门重命名
            param.json['uuid'] = depart_uuid
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(api.RenameDepartment, param)

    @story('151222 点击同步（API中调整组织架构）')
    @parametrize('param', p.third_pull(Tdt.api))
    def test_sync_api_adjustment_org(self, param):
        self.enable_sync()

        with step('调整api服务组织架构'):
            prm = p.fake_api_departments_add()[0]
            self.call(api.FakeApiAdd, prm)

        with step('点击同步'):
            self.call(api.ThirdPull, param)

        with step('校验同步过来组织架构和API调整的架构一致'):
            pr = p.org_department()[0]
            q = self.call(api.OrgDepartment, pr)
            name = [n['name'] for n in q.json()['data']['departments'] if n['name'] == '销售部'][0]

            assert prm.json['data'][0]['name'] == name
