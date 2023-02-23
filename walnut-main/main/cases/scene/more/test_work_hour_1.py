from falcons.check import Checker
from falcons.com.nick import feature, story, step, fixture

from main.actions.sprint import SprintAction
from main.api import project as api
from main.params import more


@fixture(scope='module')
def _storage():
    p = {}

    return p


# 初始化迭代
@fixture(scope='module', autouse=True)
def init_sprint(_storage):
    sprint_uuid = SprintAction.sprint_add()

    _storage |= {'sprint_uuid': sprint_uuid}


@feature('工时管理相关')
class TestWorkHourOne(Checker):

    def time_log_operate(self, body, token=None):
        """工时日志操作"""
        param = more.graphql_body(body)[0]
        q = self.call(api.ItemGraphql, param, token)

        return q.json()['data']

    @story('工时日志：列表信息')
    def test_list_info(self, _storage):
        param = more.time_log_list()[0]
        info = self.call(api.ItemGraphql, param)

        # 获取默认的分组'工时分析'key
        default_key = [r['key'] for r in info.json()['data']['reportCategories'] if r['name'] == '工时分析'][0]
        repost_info = [r for r in info.json()['data']['teamReports']]

        _storage |= {'default_key': default_key, 'repost_info': repost_info}

    @story('工时日志-分组：新建分组')
    def test_group_add(self, _storage):
        param = more.group_add()
        rp = self.time_log_operate(body=param)

        _storage |= {'group_key': rp['addReportCategory']['key']}

    @story('122337 工时日志-分组：重命名')
    def test_group_rename(self, _storage):
        param = more.group_rename()
        param['variables']['key'] = _storage['group_key']

        self.time_log_operate(body=param)

    def edit_report(self, repost_name, storage, token=None, **kwargs):
        """
        编辑各报表
        :param
            'repost_name'  # 对应修改的 报表名称
        """
        repost_key = [k['key'] for k in storage if k['name'] == repost_name][0]

        param = more.report_update(repost_key)[0]
        param.json['variables'] |= dict(**kwargs)
        q = self.call(api.ItemGraphql, param, token)

        key = q.json()['data']['updateTeamReport']['key']
        return repost_key, key

    @story('142467 部门工时日志报表：编辑分析维度（X轴）')
    def test_department_hour_log_edit_1(self, _storage):
        with step('分析维度（X轴）选择维度默认为：部门'):
            param = more.update_dimension('department')
            q_key, r_key = self.edit_report(repost_name='部门工时日志报表', storage=_storage['repost_info'],
                                            config=param)

            assert q_key == r_key

    @story('142465 部门工时日志报表：编辑分析维度（X轴）')
    def test_department_hour_log_edit_2(self, _storage):
        with step('分析维度（X轴）选择"所属迭代"'):
            param = more.update_dimension('sprint')
            q_key, r_key = self.edit_report(repost_name='部门工时日志报表', storage=_storage['repost_info'],
                                            config=param)

            assert q_key == r_key

    @story('142460 「部门工时日志报表」-编辑态-筛选：默认值')
    def test_department_hour_log_edit_default(self):
        """"""

    @story('142466 部门工时日志报表：编辑筛选')
    def test_department_hour_log_edit_3(self, _storage):
        with step('添加筛选条件为：所属迭代包含A、创建时间等于 今天'):
            param = more.update_filter(_storage['sprint_uuid'])
            q_key, r_key = self.edit_report(repost_name='部门工时日志报表', storage=_storage['repost_info'],
                                            config=param)

            assert q_key == r_key

    @story('T142472 部门工时日志报表：更改所属分组')
    def test_department_hour_log_edit_4(self, _storage):
        category = (_storage['default_key']).split('-')[1]
        repost_key = [k['key'] for k in _storage['repost_info'] if k['name'] == '部门工时日志报表'][0]

        with step('选择分组A'):
            param = more.change_group()[0]
            param.json['variables']['key'] = repost_key
            param.json['variables']['report_category'] = category
            q = self.call(api.ItemGraphql, param)

            q.check_response('data.updateTeamReport.key', repost_key)

    @story('142540 成员（登记人）-每天工时总览：编辑分析维度（X轴）')
    def test_register_every_day_1(self, _storage):
        with step('分析维度（X轴）选择"工作项负责人"'):
            param = more.register_every_1()
            q_key, r_key = self.edit_report(repost_name='成员 (登记人)-每天工时总览', config=param,
                                            storage=_storage['repost_info'])

            assert q_key == r_key

    @story('142541 成员（登记人）-每天工时总览：编辑分析维度（X轴）')
    def test_register_every_day_2(self, _storage):
        with step('分析维度（X轴）选择"周"；分析维度（Y轴）选择"状态"'):
            param = more.register_every_update('week', 'task_status')
            q_key, r_key = self.edit_report(repost_name='成员 (登记人)-每天工时总览', config=param,
                                            storage=_storage['repost_info'])

            assert q_key == r_key

    @story('142547 成员（登记人）-每天工时总览：编辑筛选')
    def test_register_every_day_3(self, _storage):
        with step('添加筛选条件为：所属迭代包含A、创建时间等于 今天'):
            param = more.register_every_3(_storage['sprint_uuid'])
            q_key, r_key = self.edit_report(repost_name='成员 (登记人)-每天工时总览', config=param,
                                            storage=_storage['repost_info'])

            assert q_key == r_key

    @story('142549 成员（登记人）-每天工时总览：分析维度（X轴）和（Y轴）默认值')
    def test_register_every_day_4(self, _storage):
        param = more.register_every_update('day', 'user')
        q_key, r_key = self.edit_report(repost_name='成员 (登记人)-每天工时总览', config=param,
                                        storage=_storage['repost_info'])

        assert q_key == r_key

    @story('142530 「成员（登记人）-每天工时总览」-编辑态-筛选：默认值')
    def test_register_every_day_6(self):
        """"""

    @story('142562 成员（登记人）-每天工时总览：更改所属分组')
    def test_register_every_day_5(self, _storage):
        category = (_storage['default_key']).split('-')[1]
        repost_key = [k['key'] for k in _storage['repost_info'] if k['name'] == '成员 (登记人)-每天工时总览'][0]

        with step('选择分组A'):
            param = more.change_group()[0]
            param.json['variables']['key'] = repost_key
            param.json['variables']['report_category'] = category
            q = self.call(api.ItemGraphql, param)

            q.check_response('data.updateTeamReport.key', repost_key)

    @story('142552 「成员（登记人）-每天工时总览」-编辑态：分析维度（Y轴）默认值')
    def test_register_every_day_7(self):
        """"""

    @story('122335 工时日志-分组：删除分组和报表')
    def test_group_report_delete(self):
        # 新建分组
        param = more.group_add()
        rp = self.time_log_operate(body=param)

        _key = rp['addReportCategory']['key']

        with step('点击删除分组和报表'):
            param = more.group_report_delete()
            param['variables']['key'] = _key

            self.time_log_operate(body=param)

    @story("T142452 「部门-项目工时总览」-更多：更改所属分组")
    def test_depart_proj_hour_overview_edit_group(self, _storage):
        with step("更改所属分组"):
            category = (_storage['group_key']).split('-')[1]
            repost_key = [k['key'] for k in _storage['repost_info'] if k['name'] == '部门-项目工时总览'][0]

            with step('选择分组A'):
                param = more.change_group()[0]
                param.json['variables']['key'] = repost_key
                param.json['variables']['report_category'] = category
                q = self.call(api.ItemGraphql, param)

                q.check_response('data.updateTeamReport.key', repost_key)

    @story('122332 工时日志-分组：删除分组')
    def test_group_delete(self, _storage):
        param = more.group_delete()
        param['variables']['key'] = _storage['group_key']

        self.time_log_operate(body=param)

    @story('142567 「成员（登记人）-每天工时总览」-更多：删除')
    def test_register_every_delete(self):
        """"""

    @story("T142443 「部门-项目工时总览」-编辑态：编辑分析指标（Y轴）")
    def test_depart_proj_hour_overview_edit_y(self, _storage):
        with step('分析维度（X轴）选择"周"；分析维度（Y轴）选择"状态"'):
            param = more.register_every_update('week', 'task_status')
            q_key, r_key = self.edit_report(repost_name='部门-项目工时总览', config=param,
                                            storage=_storage['repost_info'])

            assert q_key == r_key

    @story("T142442 「部门-项目工时总览」-编辑态：编辑分析维度（X轴）")
    def test_depart_proj_hour_overview_edit_x(self, _storage):
        with step('分析维度（X轴）选择"工作项负责人"'):
            param = more.register_every_1()
            q_key, r_key = self.edit_report(repost_name='部门-项目工时总览', config=param,
                                            storage=_storage['repost_info'])

            assert q_key == r_key

    @story("T142444 「部门-项目工时总览」-编辑态：编辑筛选")
    def test_depart_proj_hour_overview_edit_screen(self, _storage):
        with step('添加筛选条件为：所属迭代包含A、创建时间等于 今天'):
            param = more.register_every_3(_storage['sprint_uuid'])
            q_key, r_key = self.edit_report(repost_name='部门-项目工时总览', config=param,
                                            storage=_storage['repost_info'])

            assert q_key == r_key

    @story("T142466 「部门工时日志报表」-编辑态：编辑筛选")
    def test_depart_hour_log_edit_screen(self, _storage):
        with step('添加筛选条件为：所属迭代包含A、创建时间等于 今天'):
            param = more.register_every_3(_storage['sprint_uuid'])
            q_key, r_key = self.edit_report(repost_name='部门工时日志报表', config=param,
                                            storage=_storage['repost_info'])

            assert q_key == r_key
