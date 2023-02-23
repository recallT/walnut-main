from falcons.check import Checker
from falcons.com.nick import feature, story, parametrize, fixture, step, mark

from main.api import current as wb
from main.api import project as prj
from main.params import proj, current


@fixture(scope='class')
def dashboard_uuid():
    p = {}
    return p


@mark.smoke
@feature('仪表盘')
class TestDashboard(Checker):

    @story('T136271 我的工作台-顶栏-新建：新建仪表盘')
    @story('121362 个人中心-仪表盘-常用仪表盘：新建仪表盘（设为常用仪表盘，私人）')
    @parametrize('param', current.dashboard_add())
    def test_dashboard_add(self, param, dashboard_uuid):
        # get dashboard uuid
        d = proj.dashboard_uuid()[0]
        stamp = self.call(prj.TeamStampData, d)

        d_uuid = stamp.json()['dashboard']['dashboards'][-1]['uuid']
        dashboard_uuid |= {'d_uuid': d_uuid}

        with step('仪表盘名称输入'):
            a = self.call(wb.DashboardAdd, param)
            a.check_response('dashboard.pinned', param.json['dashboard']['pinned'])

            new_uuid = a.json()['dashboard']['uuid']
            dashboard_uuid |= {'new_uuid': new_uuid}

        with step('仪表盘名称为空'):
            prm = current.dashboard_add()[0]
            prm.json_update('dashboard.name', "")

            add = self.call(wb.DashboardAdd, prm, status_code=801)
            add.check_response('errcode', 'InvalidParameter.Dashboard.Name.TooLong')

        with step('进入个人中心-仪表盘-我创建的'):
            # get dashboard uuid
            d = proj.dashboard_uuid()[0]
            self.call(prj.TeamStampData, d)

    @story('T121421 更多-配置仪表盘：修改仪表盘名称')
    @parametrize('param', current.dashboard_update())
    def test_dashboard_up_name(self, param, dashboard_uuid):
        param.json['dashboard']['uuid'] = dashboard_uuid['new_uuid']
        param.uri_args({'dashboard_uuid': dashboard_uuid['new_uuid']})
        up = self.call(wb.DashboardUpdate, param)

        up.check_response('dashboard.name', param.json['dashboard']['name'])

    @story('T118994 常用仪表盘：点击仪表盘')
    def test_dashboard_query(self, dashboard_uuid):
        param = current.dashboard_query(dashboard_uuid['d_uuid'])[0]
        q = self.call(prj.ItemGraphql, param)

        names = [n['name'] for n in q.json()['data']['cards']]
        assert '我负责的工作项' in names

    @story('T140253 仪表盘：非全屏模式下，切换仪表盘')
    def test_drop_dashboard_toggle(self, dashboard_uuid):
        """下拉仪表盘列表，切换"""

        with step('切换仪表盘B'):
            param = current.dashboard_query(dashboard_uuid['new_uuid'])[0]
            q = self.call(prj.ItemGraphql, param)
            q.check_response('data.cards', [])

        with step('切换仪表盘A'):
            param = current.dashboard_query(dashboard_uuid['d_uuid'])[0]
            self.call(prj.ItemGraphql, param)
            assert q.json()['data']['cards'] is not None

    @story('T121424 更多：删除仪表盘')
    @parametrize('param', current.dashboard_opt())
    def test_dashboard_delete(self, param, dashboard_uuid):
        param.uri_args({'dashboard_uuid': dashboard_uuid['new_uuid']})
        self.call(wb.DashboardDelete, param)
