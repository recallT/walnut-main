"""honor_uploads_tips插件借口"""
from falcons.ops import ProjectOps


class GetUploadTips(ProjectOps):
    """获取-上传文件安全提示语"""
    uri = '/getUploadTips'
    name = '获取上传文件安全提示接口'
    api_type = 'GET'


class SetUploadTips(ProjectOps):
    """设置-上传文件安全提示语"""
    uri = '/setUploadTips'
    name = '设置上传文件安全提示接口'
    api_type = 'POST'


class PermissionNumberAdd(ProjectOps):
    """添加可用成员"""
    uri = '/team/{team_uuid}/plugin/permissionrule/add'
    name = '添加可用成员'
    api_type = 'POST'


class PermissionNumberDelete(ProjectOps):
    """删除可用成员"""
    uri = '/team/{team_uuid}/plugin/permissionrule/delete'
    name = '删除可用成员'
    api_type = 'POST'


class PermissionNumberCheck(ProjectOps):
    """获取提示语成员权限校验"""
    uri = '/team/{team_uuid}/plugin/permissionrule/check'
    name = '检查成员是否获取安全提示语'
    api_type = 'POST'


class PermissionInfoList(ProjectOps):
    """可用成员配置列表"""
    uri = '/team/{team_uuid}/plugin/permissioninfo/list'
    name = '可用成员配置列表'
    api_type = 'POST'


"""honor_banner插件接口"""


class SetBannerTips(ProjectOps):
    """设置-上传顶部安全栏提示语"""
    uri = '/setBanner'
    name = '上传顶部安全栏提示语'
    api_type = 'POST'


class GetBannerTips(ProjectOps):
    """获取-获取顶部安全栏提示语"""
    uri = '/getBanner'
    name = '获取顶部安全栏提示语'
    api_type = 'GET'


"""honor_workspace插件接口"""


class WorkspacePermissionInfoList(ProjectOps):
    """可用成员配置列表"""
    uri = '/team/{team_uuid}/plugin/permissioninfo/list'
    name = '可用成员配置列表'
    api_type = 'POST'


class WorkspacePermissionNumberAdd(ProjectOps):
    """添加可用成员"""
    uri = '/team/{team_uuid}/plugin/permissionrule/add'
    name = '添加可用成员'
    api_type = 'POST'


class WorkspacePermissionNumberDelete(ProjectOps):
    """删除可用成员"""
    uri = '/team/{team_uuid}/plugin/permissionrule/delete'
    name = '删除可用成员'
    api_type = 'POST'


class WorkspacePermissionNumberCheck(ProjectOps):
    """是否隐藏工作台权限校验"""
    uri = '/team/{team_uuid}/plugin/permissionrule/check'
    name = '是否隐藏工作台权限校验'
    api_type = 'POST'


"""------------------紫金插件相关接口-------------------------"""


class OrgStampsData(ProjectOps):
    uri = '/organization/{org_uuid}/stamps/data'
    name = '获取组织级别StampsData'
    api_type = 'POST'


class ComponentsAdd(ProjectOps):
    """项目添加组件"""
    uri = '/team/{team_uuid}/project/{project_uuid}/components/add'
    name = '项目添加组件'
    api_type = 'POST'


class UpdateForm(ProjectOps):
    uri = '/team/{team_uuid}/project/5oziwx7y2FkJnNO4/components/update'
    name = '新建表单'
    api_type = 'POST'


class ProjectStamp(ProjectOps):
    """项目标记数据"""
    uri = '/team/{team_uuid}/project/{project_uuid}/stamps/data'
    name = '项目标记数据'
    api_type = 'POST'


class AllProjects(ProjectOps):
    uri = '/team/{team_uuid}/items/graphql'
    name = '插件-关联项目-查询启用了表单的所有项目'
    api_type = 'POST'


class PlugQueryProj(ProjectOps):
    uri = '/associated/project/query'
    name = '插件-关联项目-查询关联项目'
    api_type = 'POST'


class PlugUpdateForms(ProjectOps):
    uri = '/associated/project/update'
    name = '插件-关联项目-更新关联项目'
    api_type = 'POST'


class QueryAnnouncement(ProjectOps):
    uri = '/announcement/query'
    name = '插件-查询公告'
    api_type = 'GET'


class UpdateAnnouncement(ProjectOps):
    uri = '/announcement/update'
    name = '插件-更新公告'
    api_type = 'POST'
