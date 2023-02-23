from falcons.check import Checker, go
from falcons.com.nick import feature, story, parametrize, fixture, step, mark

from main.api import current as cur
from main.api import project as prj
from main.params import current, proj, data
from main.params.const import ACCOUNT


# 仪表盘新增和清除
@fixture(scope='module', autouse=True)
def dashboard_add_and_del(dashboard_uuid):
    # 创建共享type仪表盘
    param = current.dashboard_add()[0]
    param.json_update('dashboard.shared', True)
    shared_to = [{'user_domain_type': 'single_user', 'user_domain_param': ACCOUNT.user.owner_uuid}]
    param.json_update('dashboard.shared_to', shared_to)

    add = go(cur.DashboardAdd, param)

    new_uuid = add.json()['dashboard']['uuid']
    dashboard_uuid |= {'n_uuid': new_uuid}

    yield
    prm = current.dashboard_opt()[0]
    prm.uri_args({'dashboard_uuid': new_uuid})
    go(cur.DashboardDelete, prm)


@fixture(scope='module')
def dashboard_uuid():
    p = {}
    return p


@mark.smoke
@feature('个人中心-仪表盘')
class TestCenterDashboard(Checker):

    def get_dashboard_uuid(self):
        d = proj.dashboard_uuid()[0]
        stamp = self.call(prj.TeamStampData, d)

        d_uuid = stamp.json()['dashboard']['dashboards'][-1]['uuid']
        return d_uuid

    @story('121349 常用仪表盘：点击仪表盘')
    def test_click_dashboard(self, dashboard_uuid):
        d_uuid = self.get_dashboard_uuid()
        dashboard_uuid |= {'d_uuid': d_uuid}

        param = current.card_gql(d_uuid)[0]

        with step('点击仪表盘名称a'):
            self.call(prj.ItemGraphql, param)

    @story('121351 常用仪表盘：关闭常用仪表盘')
    @parametrize('param', current.dashboard_config())
    def test_close_commonly_dashboard(self, param, dashboard_uuid):
        with step('仪表盘a右侧点击✖️'):
            param.uri_args({'dashboard_uuid': dashboard_uuid['d_uuid']})

            res = self.call(cur.DashboardConfigure, param)
            res.check_response('dashboard.pinned', False)

        with step('仪表盘b右侧点击✖️'):
            param.uri_args({'dashboard_uuid': dashboard_uuid['n_uuid']})

            res = self.call(cur.DashboardConfigure, param)
            res.check_response('dashboard.pinned', False)

    @story('121390 我创建的：开启常用仪表盘')
    @parametrize('param', current.dashboard_config())
    def test_enable_commonly_dashboard(self, param, dashboard_uuid):
        with step('仪表盘a,开关打开'):
            param.json_update('pinned', True)
            param.uri_args({'dashboard_uuid': dashboard_uuid['d_uuid']})

            res = self.call(cur.DashboardConfigure, param)
            res.check_response('dashboard.pinned', True)

        with step('仪表盘b,开关打开'):
            param.uri_args({'dashboard_uuid': dashboard_uuid['n_uuid']})
            self.call(cur.DashboardConfigure, param)

    @story('121354 常用仪表盘：设为首页')
    @parametrize('param', current.dashboard_config())
    def test_set_home_page(self, param, dashboard_uuid):
        with step('点击仪表盘b右侧的设为首页'):
            param.json |= {"pinned": True, "default": True}
            param.uri_args({'dashboard_uuid': dashboard_uuid['n_uuid']})

            res = self.call(cur.DashboardConfigure, param)
            res.check_response('dashboard.default', True)

    @story('121394 删除私人仪表盘')
    def test_del_private_dashboard(self):
        """"""


@mark.smoke
@feature('个人中心-账户信息')
class TestAccountInfo(Checker):

    @story('121410 修改公司名称')
    @parametrize('param', data.update_user_info())
    def test_company_name_update(self, param):
        with step('公司名称输入：示例'):
            param.json_update('company', '示范TEST')
            self.call(prj.UsersUpdate, param)

    @story('121411 修改用户名')
    @parametrize('param', data.update_user_info())
    def test_user_name_update(self, param):
        me = prj.UsersMe()
        me.call()
        name = me.value('name')

        with step('用户名输入'):
            param.json_update('name', name)
            self.call(prj.UsersUpdate, param)

    @story('121412 修改职位')
    @parametrize('param', data.update_user_info())
    def test_title_update(self, param):
        with step('职位输入：CTO'):
            param.json_update('title', 'CTO')
            self.call(prj.UsersUpdate, param)
