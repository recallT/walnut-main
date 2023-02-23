from falcons.check import Checker, go
from falcons.com.nick import parametrize, feature, fixture, story, step

from main.api import more as m
from main.api import project as api
from main.params import more


@fixture(scope='module')
def _storage():
    p = {}

    return p


# 新建分组
@fixture(scope='module', autouse=True)
def group_add(_storage):
    p = more.group_add()
    param = more.graphql_body(p)[0]
    rp = go(api.ItemGraphql, param)

    group_key = rp.json()['data']['addReportCategory']['key']
    group_uuid = group_key.split('-')[1]

    _storage |= {'group_key': group_key, 'group_uuid': group_uuid}

    yield
    # 清除新建的分组和报表数据
    d = more.group_report_delete()
    d['variables']['key'] = group_key

    param = more.graphql_body(d)[0]
    go(api.ItemGraphql, param)


@feature('工时管理相关')
class TestWorkHourTwo(Checker):

    @story('138480 工时日志报表新建')
    @parametrize('types', ('manhour_log', 'manhour_overview'))
    def test_report_add(self, types, _storage):
        param = more.add_team_report(types)[0]
        param.json['variables']['report_category'] = _storage['group_uuid']
        q = self.call(api.ItemGraphql, param)

        report_key = q.json()['data']['addTeamReport']['key']
        report_uuid = report_key.split('-')[1]
        _storage |= {f'{types}_key': report_key, f'{types}_uuid': report_uuid}  # 存储新建的工时日志报表key和表报uuid

    @story('142475 工时日志报表-更多：重命名')
    @parametrize('param', more.report_rename())
    def test_hour_log_rename(self, param, _storage):
        with step('重命名'):
            param.json['variables']['key'] = _storage['manhour_log_key']
            q = self.call(api.ItemGraphql, param)

            q.check_response('data.updateTeamReport.key', _storage['manhour_log_key'])

    @story('142477 工时日志报表：导出报表')
    @parametrize('param', more.hour_log_export())
    def test_hour_log_export(self, param, _storage):
        with step('点击导出报表'):
            param.json['report_uuid'] = _storage['manhour_log_uuid']
            export = self.call(m.ReportExport, param)

            assert export.response.text.split('\n')[0] == '提交人,所属项目,工作项名称,状态,提交人,登记工时,开始时间,备注'

    @story('142478 工时日志报表：另存为')
    @parametrize('param', more.add_team_report())
    def test_hour_log_save(self, param, _storage):
        with step('调整报表名称'):
            param.json['variables']['name'] = '工时日志另存为-TEST'
            param.json['variables']['report_category'] = _storage['group_uuid']
            q = self.call(api.ItemGraphql, param)

            save_as = q.json()['data']['addTeamReport']['key']
            _storage |= {'as_key': save_as}  # 存储另存为报表的key

    @story('142474 工时日志报表-更多：删除')
    @parametrize('param', more.report_delete())
    def test_hour_log_delete(self, param, _storage):
        param.json['variables']['key'] = _storage['as_key']
        self.call(api.ItemGraphql, param)

    @story('142568 成员（登记人）-每天工时总览-更多：重命名')
    @parametrize('param', more.report_rename())
    def test_register_every_day_rename(self, param, _storage):
        with step('重命名'):
            param.json['variables']['key'] = _storage['manhour_overview_key']
            q = self.call(api.ItemGraphql, param)

            q.check_response('data.updateTeamReport.key', _storage['manhour_overview_key'])

    @story('142572 成员（登记人）-每天工时总览-更多：导出报表')
    @parametrize('param', more.register_every_day_export())
    def test_register_every_day_export(self, param, _storage):
        with step('点击导出报表'):
            param.json['report_uuid'] = _storage['manhour_overview_uuid']
            self.call(m.ReportExport, param)

            # assert '合计登记工时,合计预估工时' in export.response.text

    @story('142574 成员（登记人）-每天工时总览：另存为')
    @parametrize('param', more.add_team_report('manhour_overview'))
    def test_register_every_day_save(self, param, _storage):
        with step('调整报表名称'):
            param.json['variables']['name'] = '工时总览另存为-TEST'
            param.json['variables']['report_category'] = _storage['group_uuid']
            q = self.call(api.ItemGraphql, param)

            save_as = q.json()['data']['addTeamReport']['key']
            _storage |= {'overview_key': save_as}  # 存储另存为报表的key

    @story('142474 工时日志报表-更多：删除')
    @parametrize('param', more.report_delete())
    def test_register_every_day_delete(self, param, _storage):
        param.json['variables']['key'] = _storage['overview_key']
        self.call(api.ItemGraphql, param)

    @story("T142458 「部门-项目工时总览」：另存为")
    @parametrize('param', more.add_team_report('manhour_overview'))
    def test_depart_proj_hour_overview_save(self, param, _storage):
        with step("调整报表名称"):
            param.json['variables']['name'] = '部门-项目工时总览-TEST'
            param.json['variables']['report_category'] = _storage['group_uuid']
            resp = self.call(api.ItemGraphql, param)

            save_key = resp.json()['data']['addTeamReport']['key']
            _storage |= {'proj_hour_overview_key': save_key} # 存储报表另存为的key

    @story("T142455 「部门-项目工时总览」-更多：重命名")
    @parametrize('param', more.report_rename())
    def test_depart_proj_hour_overview_report_rename(self, param, _storage):
        with step("报表重命名"):
            param.json['variables']['key'] = _storage['proj_hour_overview_key']
            resp = self.call(api.ItemGraphql, param)

            resp.check_response('data.updateTeamReport.key', _storage['proj_hour_overview_key'])

    @story("T142457 「部门-项目工时总览」：导出报表")
    @parametrize('param', more.register_every_day_export())
    def test_register_every_day_export(self, param, _storage):
        with step('点击导出报表'):
            param.json['report_uuid'] = _storage['manhour_overview_uuid']
            self.call(m.ReportExport, param)

    @story("T142454 「部门-项目工时总览」-更多：删除")
    @parametrize('param', more.report_delete())
    def test_depart_proj_hour_overview_delete(self, param, _storage):
        param.json['variables']['key'] = _storage['proj_hour_overview_key']
        self.call(api.ItemGraphql, param)

    @story("T142697 「成员（登记人）-项目工时总览」：另存为")
    @parametrize('param', more.add_team_report('manhour_overview'))
    def test_register_proj_hour_overview(self, param, _storage):
        with step("调整报表名称"):
            param.json['variables']['name'] = '成员（登记人）-项目工时总览-TEST'
            param.json['variables']['report_category'] = _storage['group_uuid']
            resp = self.call(api.ItemGraphql, param)

            save_key = resp.json()['data']['addTeamReport']['key']
            _storage |= {'register_proj_hour_overview_key': save_key} # 存储报表另存为的key

    @story("T142694 「成员（登记人）-项目工时总览」-更多：重命名")
    @parametrize('param', more.report_rename())
    def test_register_proj_hour_overview_report_rename(self, param, _storage):
        with step("报表重命名"):
            param.json['variables']['key'] = _storage['register_proj_hour_overview_key']
            resp = self.call(api.ItemGraphql, param)

            resp.check_response('data.updateTeamReport.key', _storage['register_proj_hour_overview_key'])

    @story("T142794 「成员（负责人）-每天工时总览」：另存为")
    @parametrize('param', more.add_team_report('manhour_overview'))
    def test_charge_proj_hour_overview_save_as(self, param, _storage):
        with step("调整报表名称"):
            param.json['variables']['name'] = '成员（负责人）-每天工时总览-TEST'
            param.json['variables']['report_category'] = _storage['group_uuid']
            resp = self.call(api.ItemGraphql, param)

            save_key = resp.json()['data']['addTeamReport']['key']
            _storage |= {'charge_proj_hour_overview_key': save_key} # 存储报表另存为的key值
