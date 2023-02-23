"""通用模块api"""

from falcons.ops import ProjectOps


class DashboardAdd(ProjectOps):
    uri = '/team/{team_uuid}/dashboards/add'
    name = '新增仪表盘'
    api_type = 'POST'


class DashboardUpdate(ProjectOps):
    uri = '/team/{team_uuid}/dashboard/{dashboard_uuid}/update'
    name = '更新仪表盘'
    api_type = 'POST'


class DashboardDelete(ProjectOps):
    uri = '/team/{team_uuid}/dashboard/{dashboard_uuid}/delete'
    name = '删除仪表盘'
    api_type = 'POST'


class DashboardConfigure(ProjectOps):
    uri = '/team/{team_uuid}/dashboard/{dashboard_uuid}/configure'
    name = '配置仪表盘'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------


class ExportTaskJob(ProjectOps):
    uri = '/team/{team_uuid}/filters/add_export_task_job'
    name = '导出工作项'
    api_type = 'POST'


class DownloadExportTask(ProjectOps):
    uri = '/team/{team_uuid}/filters/download_export_task?key={key_id}'
    name = '下载工作项'
    api_type = 'GET'


class FilterViewAdd(ProjectOps):
    uri = '/team/{team_uuid}/user_filter_views/add'
    name = '新增筛选视图'
    api_type = 'POST'


class FilterViewDelete(ProjectOps):
    uri = '/team/{team_uuid}/user_filter_view/{view_uuid}/delete'
    name = '删除筛选视图'
    api_type = 'POST'


class FilterViewConfig(ProjectOps):
    uri = '/team/{team_uuid}/user_filter_views/config/update'
    name = '管理筛选视图配置'
    api_type = 'POST'


class FilterViewConfigGet(ProjectOps):
    uri = '/team/{team_uuid}/user_filter_views/config'
    name = '筛选视图配置列表'
    api_type = 'GET'
