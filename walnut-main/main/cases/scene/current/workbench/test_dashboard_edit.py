from falcons.check import Checker, go
from falcons.com.nick import feature, story, parametrize, fixture, step, mark

from main.api import current as wb
from main.api import project as prj
from main.params import current
from main.params.const import ACCOUNT


# 仪表盘新增和清除
@fixture(scope='module', autouse=True)
def dashboard_add_and_del(dashboard_uuid):
    param = current.dashboard_add()[0]
    add = go(wb.DashboardAdd, param)

    d_uuid = add.json()['dashboard']['uuid']
    dashboard_uuid.append(d_uuid)

    yield
    prm = current.dashboard_opt()[0]
    prm.uri_args({'dashboard_uuid': d_uuid})
    go(wb.DashboardDelete, prm)


@fixture(scope='module')
def dashboard_uuid():
    p = []
    return p


@mark.smoke
@feature('编辑仪表盘')
class TestDashboardEdit(Checker):

    def dashboard_card_add(self, car_type, layout, config, d_uuid):
        param = current.card_add(car_type, layout, config)[0]
        param.json['card']['dashboard_uuid'] = d_uuid[0]
        param.json['card']['config'] = config
        param.uri_args({'dashboard_uuid': d_uuid[0]})

        add_p = self.call(prj.DashboardCardAdd, param)

        add_p.check_response('card.name', param.json['card']['name'])
        add_p.check_response('card.type', param.json['card']['type'])

    @story('T117583 添加公告卡片')
    def test_announcement_add(self, dashboard_uuid):
        with step('选择公告卡片'):
            car_type = 'announcement'
            layout = {'w': 9, 'h': 3, 'x': 0, 'y': 7}
            config = {'content': ""}
            self.dashboard_card_add(car_type, layout, config, dashboard_uuid)

    @story('T117583 添加公告卡片-名字超长-64位')
    def test_dashboard_add_name_too_long(self, dashboard_uuid):
        car_type = 'announcement'
        layout = {'w': 9, 'h': 3, 'x': 0, 'y': 7}
        config = {'content': ""}
        param = current.card_add(car_type, layout, config)[0]

        d_uuid = dashboard_uuid[0]
        param.json['card']['dashboard_uuid'] = d_uuid
        param.uri_args({'dashboard_uuid': d_uuid})
        param.json['card']['name'] = (param.json['card']['name'] * 5)[:65]
        add_p = self.call(prj.DashboardCardAdd, param, status_code=801)
        add_p.check_response('errcode', 'InvalidParameter.DashboardCard.Name.TooLong')

    @story('T117577 添加版本列表卡片（全部版本）')
    def test_version_all_add(self, dashboard_uuid):
        with step('选择版本列表：全部版本'):
            car_type = 'version_list'
            layout = {"w": 6, "h": 4, "x": 0, "y": 7}
            config = {"category": "all"}
            self.dashboard_card_add(car_type, layout, config, dashboard_uuid)

    @story('T117580 添加迭代概览卡片')
    @parametrize('times', ('start', 'finish'))
    def test_sprint_overview_add(self, times, dashboard_uuid):
        with step('选择项目：A,选择迭代：A'):
            car_type = 'sprint_overview'
            layout = {"w": 6, "h": 4, "x": 0, "y": 7}
            config = {
                "project_uuid": ACCOUNT.project_uuid,
                "sprint_uuid": f"$earliest_{times}_sprint_in_progress"  # 最早开始的进行中迭代/最早结束的进行中迭代
            }
            self.dashboard_card_add(car_type, layout, config, dashboard_uuid)

    @story('T117584 添加工作项列表卡片（全局筛选器）')
    @parametrize('filter', ('ft-t-001', 'ft-t-002'))  # 我负责的工作项/我关注的工作项
    def test_task_add(self, filter, dashboard_uuid):
        with step('选择筛选器位置：我的工作台-筛选器'):
            car_type = 'task_list'
            layout = {"w": 6, "h": 4, "x": 0, "y": 4}
            config = {"project_uuid": None, "filter_uuid": filter}
            self.dashboard_card_add(car_type, layout, config, dashboard_uuid)

    @story('T117589 添加数据报表卡片（工作项分布统计报表）')
    def test_data_report_add(self, dashboard_uuid):
        # 获取数据报表所有uuid
        prm = current.data_report_type()[0]
        q = self.call(prj.ItemGraphql, prm)
        data = q.json()['data']['projectReports']
        uuid = [u['uuid'] for u in data if u['name'] == '需求按时交付情况分布'][0]

        with step('选择项目：A,选择报表'):
            car_type = 'report'
            layout = {"w": 6, "h": 4, "x": 0, "y": 7}
            config = {"project_uuid": ACCOUNT.project_uuid, "report_uuid": uuid}
            self.dashboard_card_add(car_type, layout, config, dashboard_uuid)

    @story('T117597 添加数字指标卡片（全局筛选器）')
    @parametrize('filter', ('ft-t-001', 'ft-t-002'))  # 我负责的工作项/我关注的工作项
    def test_task_count_add(self, filter, dashboard_uuid):
        with step('选择筛选器位置,选择视图：A/B'):
            car_type = 'task_count'
            layout = {"w": 4, "h": 4, "x": 0, "y": 7}
            config = {"project_uuid": None, "filter_uuid": filter}
            self.dashboard_card_add(car_type, layout, config, dashboard_uuid)

    @story('T117599 添加项目表格卡片')
    @parametrize('status', ('in_progress', 'to_do'))  # 状态：进行中/未开始
    def test_project_add(self, status, dashboard_uuid):
        with step('T117599 选择项目状态:进行中/未完成'):
            car_type = 'project_list'
            layout = {"w": 6, "h": 4, "x": 4, "y": 7}
            config = {
                "status": status,
                "field_alias": [
                    {
                        "alias": "name",
                        "field_type": "text",
                        "built_in": True
                    },
                    {
                        "alias": "task_count_to_do",
                        "field_type": "integer",
                        "built_in": True
                    },
                    {
                        "alias": "task_count_in_progress",
                        "field_type": "integer",
                        "built_in": True
                    },
                    {
                        "alias": "task_count_done",
                        "field_type": "integer",
                        "built_in": True
                    }
                ]
            }
            self.dashboard_card_add(car_type, layout, config, dashboard_uuid)

    @story('T117603 添加自定义数据报表卡片')
    @story('117607 编辑仪表盘：添加自定义数据报表卡片（新增工作项趋势报表）')
    @parametrize('types', ('task_cumulative_trend', 'task_trend'))
    def test_customize_report_add_1(self, types, dashboard_uuid):
        with step('选择报表类型：工作项累计趋势报表/新增工作项趋势报表'):
            car_type = 'customize_report'
            layout = {"w": 6, "h": 4, "x": 0, "y": 7}
            config = {
                "dimensions": [
                    {
                        "field_uuid": "field009",
                        "date_interval": "1d",
                        "date_range": "30d",
                        "aggregation": "date_histogram"
                    }
                ],
                "type": types,
                "field_uuids": [],
                "filter": None
            }
            self.dashboard_card_add(car_type, layout, config, dashboard_uuid)

    @story('T117604 添加自定义数据报表卡片')
    @story('117605 编辑仪表盘：添加自定义数据报表卡片（工作项属性分布比较报表）')
    def test_customize_report_add_2(self, dashboard_uuid):
        with step('选择报表类型：工作项属性分布报表'):
            car_type = 'customize_report'
            layout = {"w": 6, "h": 4, "x": 0, "y": 11}
            config = {
                "dimensions": [
                    {
                        "field_uuid": "field004",
                        "order_by": "task_count",
                        "order": "desc",
                        "limit": 10,
                        "aggregation": "terms"
                    }
                ],
                "type": "field",
                "field_uuids": [],
                "filter": None
            }
            self.dashboard_card_add(car_type, layout, config, dashboard_uuid)

    @story('T117606 添加自定义数据报表卡片')
    def test_customize_report_add_3(self, dashboard_uuid):
        with step('选择报表类型：工作项属性分布趋势报表'):
            car_type = 'customize_report'
            layout = {"w": 6, "h": 4, "x": 6, "y": 11}
            config = {
                "dimensions": [
                    {
                        "field_uuid": "field009",
                        "date_interval": "1d",
                        "date_range": "7d",
                        "aggregation": "date_histogram"
                    },
                    {
                        "field_uuid": "field005",
                        "order_by": "task_count",
                        "order": "desc",
                        "limit": 10,
                        "aggregation": "terms"
                    }
                ],
                "type": "field_trend",
                "field_uuids": [],
                "filter": None
            }
            self.dashboard_card_add(car_type, layout, config, dashboard_uuid)

    @story('T117608 添加最近浏览的项目卡片')
    def test_recent_project_add(self, dashboard_uuid):
        car_type = 'recent_projects'
        layout = {"w": 12, "h": 3, "x": 0, "y": 7}
        config = {"content": ""}

        with step('卡片名称输入框清空'):
            prm = current.card_add(car_type, layout, config)[0]
            prm.json['card']['dashboard_uuid'] = dashboard_uuid[0]
            prm.json['card']['name'] = ''
            prm.uri_args({'dashboard_uuid': dashboard_uuid[0]})

            add = self.call(prj.DashboardCardAdd, prm, status_code=801)
            add.check_response('errcode', 'InvalidParameter.DashboardCard.Name.TooLong')

        with step('卡片名称输入超过64位字符'):
            prm.json['card']['name'] = '最近浏览的项目/' * 8 + '65'

            add = self.call(prj.DashboardCardAdd, prm, status_code=801)
            add.check_response('errcode', 'InvalidParameter.DashboardCard.Name.TooLong')

        with step('卡片名称正常输入'):
            self.dashboard_card_add(car_type, layout, config, dashboard_uuid)

    @story('T117609 添加最近浏览的页面组卡片')
    def test_recent_spaces_add(self, dashboard_uuid):
        with step('卡片名称正常输入'):
            car_type = 'recent_spaces'
            layout = {"w": 12, "h": 3, "x": 0, "y": 10}
            config = {"content": ""}
            self.dashboard_card_add(car_type, layout, config, dashboard_uuid)
