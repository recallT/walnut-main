"""
@File    ：test_third_youdu.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/2/15
@Desc    ：有度三方集成用例
"""
from falcons.check import Checker
from falcons.com.nick import feature, step, parametrize

from main.api import third as api
from main.environ import ThirdPartyType as Tdt
from main.params import third as p


@feature('第三方账号-new')
class TestYouDu(Checker):
    """"""

    @step('148568 添加第三方集成（有度）')
    @parametrize('param', p.third_ydu_add())
    def test_you_du_add(self, param):
        """"""
        with step('添加三方集成（有度）'):
            self.call(api.ThirdAddOrUpdate, param)
        with step('查看第三方集成>有度页面'):
            list_p = p.third_list()[0]

            list_resp = self.call(api.ThirdList, list_p)
            _type = [j['third_party_type'] for j in list_resp.json()['results']]

            assert Tdt.you_du in _type

        with step('进入个人中心-第三方集成-出现有度绑定账号的数据列'):
            bind_p = p.third_user_bindings()[0]
            bind_resp = self.call(api.ThirdUserBindings, bind_p)
            ydu_type = [j['third_party_type'] for j in bind_resp.json()]

            assert Tdt.you_du in ydu_type

    @step('148604 个人中心：绑定有度账号')
    @parametrize('param', p.third_ydu_bind('zeno'))
    def test_you_du_bind_in_personal_center(self, param):
        """"""
        with step('绑定有度账号'):
            self.call(api.ThirdUserBind, param)

        with step('检查绑定结果'):
            bind_p = p.third_user_bindings()[0]
            bind_resp = self.call(api.ThirdUserBindings, bind_p)
            ydu_user = [j['third_party_id'] for j in bind_resp.json() if j['third_party_type'] == Tdt.you_du][0]
            assert ydu_user == 'zeno'

    @step('148632 检查是否收到工作项通知')
    @parametrize('param', p.third_user_unbind(Tdt.you_du))
    def test_you_du_check_notifications(self, param):
        """"""
        with step('成员B将工作项负责人变更为「成员A」'):
            ...

    @step('148605 个人中心：解绑有度账号')
    @parametrize('param', p.third_user_unbind(Tdt.you_du))
    def test_you_du_unbind_in_personal_center(self, param):
        """"""
        with step('解绑有度账号'):
            self.call(api.ThirdUserUnbind, param)

        with step('检查解绑结果'):
            bind_p = p.third_user_bindings()[0]
            bind_resp = self.call(api.ThirdUserBindings, bind_p)
            ydu_user = [j['third_party_id'] for j in bind_resp.json() if j['third_party_type'] == Tdt.you_du][0]

            assert not ydu_user  # 绑定用户为空

    @step('148599 有度详情页：移除集成')
    @parametrize('param', p.third_remove(Tdt.you_du))
    def test_you_du_remove(self, param):
        """"""
        self.call(api.ThirdRemove, param)

        with step('进入个人中心-第三方集成-出现有度绑定账号的数据列'):
            bind_p = p.third_user_bindings()[0]
            bind_resp = self.call(api.ThirdUserBindings, bind_p)
            ydu_type = [j['third_party_type'] for j in bind_resp.json()]

            assert Tdt.you_du not in ydu_type
