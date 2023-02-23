"""
@File    ：test_third_api_1.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/2/22
@Desc    ：三方集成API集成用例
"""
import time

from falcons.check import Checker
from falcons.com.nick import feature, step, parametrize, story

from main.api import third as api
from main.environ import ThirdPartyType as Tdt
from main.params import third as p


@feature('第三方账号-new')
class TestThirdApiOne(Checker):
    """"""

    @story('151142 添加第三方集成：自动绑定「邮箱相同的系统账号」（API 同步）')
    @parametrize('param', p.third_api_add())
    def test_api_add(self, param):
        """"""
        with step('添加第三方集成：自动绑定「邮箱相同的系统账号」（API 同步）'):
            self.call(api.ThirdAddOrUpdate, param)

        with step('查看第三方集成>API页面'):
            list_p = p.third_list()[0]
            list_resp = self.call(api.ThirdList, list_p)
            api_type = [j['third_party_type'] for j in list_resp.json()['results']]

            assert Tdt.api in api_type

        with step('进入个人中心-第三方集成-出现API绑定账号的数据列'):
            bind_p = p.third_user_bindings()[0]
            bind_resp = self.call(api.ThirdUserBindings, bind_p)
            api_type = [j['third_party_type'] for j in bind_resp.json()]

            assert Tdt.api in api_type

    @story('151186 API 同步详情页：开启用户目录同步')
    @parametrize('param', p.third_update('sync', Tdt.api))
    def test_api_enable_sync_user_dir(self, param):
        """"""
        with step('开启用户目录同步'):
            self.call(api.ThirdStatusUpdate, param)

    @story('151145 添加API 同步：添加用户属性映射')
    @parametrize('param', p.third_update_mapping_ldap(Tdt.api))
    def test_api_add_user_property_mapping(self, param):
        """"""

        # 1.获取配置详情
        with step('获取配置详情'):
            detail_p = p.third_detail(Tdt.api)[0]
            detail = self.call(api.ThirdDetail, detail_p)
            json_config = detail.json()['json_config']

            # 2. 获取字段映射配置
            mapping_list = self.call(api.ThirdMappingList, detail_p)
            mapping = [{
                'system_property_key': m['system_property_key'],
                'third_party_property_key': m['third_party_property_key'],
            } for m in mapping_list.json()]
            is_id_exists = [m for m in mapping if m['system_property_key'] == 'id_member']

        # 3.修改组织单元过滤规则
        with step('添加用户属性映射'):
            m = param.json['mappings']
            if not is_id_exists:
                m += mapping  # 将原映射配置添加
            else:
                param.json['mappings'] = mapping  # 如果添加了，保持原样

            param.json |= {'json_config': json_config, }
            self.call(api.ThirdAddOrUpdate, param)

    @story('151154 编辑基础信息：添加用户属性映射')
    @story('149708 编辑基础信息：添加用户属性映射')
    @parametrize('param', p.third_pull(Tdt.api))
    def test_api_edit_user_mapping(self, param):
        with step('更新用户工号信息'):
            """将用户的工号信息更新到api组织成员中"""
            p1 = p.fake_api_update()[0]
            self.call(api.FakeApiUpdate, p1, {})
        time.sleep(0.5)
        with step('api用户目录同步'):
            self.call(api.ThirdPull, param)

        with step('查看成员详情工号'):
            # todo 这里检查结果未完成 查看成员的工号信息
            bind_p = p.third_user_bindings()[0]
            self.call(api.ThirdUserBindings, bind_p)

    @story('151159 API 同步详情页：移除集成')
    @parametrize('param', p.third_remove(Tdt.api))
    def test_you_du_remove(self, param):
        self.call(api.ThirdRemove, param)

        with step('进入个人中心-第三方集成-出现API绑定账号的数据列'):
            bind_p = p.third_user_bindings()[0]
            bind_resp = self.call(api.ThirdUserBindings, bind_p)
            api_type = [j['third_party_type'] for j in bind_resp.json()]

            assert Tdt.you_du not in api_type
