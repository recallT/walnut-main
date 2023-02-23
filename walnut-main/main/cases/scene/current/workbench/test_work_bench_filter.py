from falcons.check import Checker
from falcons.com.nick import feature, story, parametrize, fixture, step, mark

from main.api import current as wb
from main.params import current
from main.params.const import ACCOUNT


@fixture(scope='module')
def view_uuid():
    p = []
    return p


@mark.smoke
@feature('工作台-筛选器')
class TestWorkBenchFilter(Checker):

    @story('T136905 导出工作项（默认导出）')
    @parametrize('param', current.export_task_job())
    def test_export_task_job(self, param):
        with step('属性默认勾选，点击确认'):
            ex = self.call(wb.ExportTaskJob, param)

            key = ex.json()['key']  # 获取下载task的key

            # 下载task
            prm = current.dashboard_opt()[0]
            prm.uri_args({'key_id': key})
            self.call(wb.DownloadExportTask, prm)

    @story('T136875 视图管理：新建视图（私人）')
    @parametrize('param', current.filter_view_add())
    def test_filter_view_private_add(self, param, view_uuid):
        add = self.call(wb.FilterViewAdd, param)
        add.check_response('view.name', param.json['name'])

        private_uuid = add.json()['view']['uuid']
        view_uuid.append(private_uuid)

    @story('T136872 视图管理：新建视图（共享）')
    @parametrize('param', current.filter_view_add())
    def test_filter_view_shared_add(self, param, view_uuid):
        param.json['shared'] = True
        param.json['shared_to'].append(
            {"user_domain_type": "single_user", "user_domain_param": ACCOUNT.user.owner_uuid})

        add = self.call(wb.FilterViewAdd, param)
        add.check_response('view.name', param.json['name'])

        shared_uuid = add.json()['view']['uuid']
        view_uuid.append(shared_uuid)

    @story('视图管理：显示和隐藏视图')
    @parametrize('param', current.filter_view_config())
    def test_show_or_hied_view(self, param, view_uuid):
        show = {'view_uuid': view_uuid[0], 'is_show': True}  # 显示视图
        hied = {'view_uuid': view_uuid[1], 'is_show': False}  # 隐藏视图

        param.json['configs'].append(show)
        param.json['configs'].append(hied)
        self.call(wb.FilterViewConfig, param)

    @story('视图管理：删除已创建的视图')
    def test_filter_view_delete(self, view_uuid):
        param = current.dashboard_opt()[0]

        if view_uuid:
            for uuid in view_uuid:
                param.uri_args({'view_uuid': uuid})
                self.call(wb.FilterViewDelete, param)
