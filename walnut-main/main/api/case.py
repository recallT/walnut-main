"""
@File    ：case.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/9
@Desc    ：
"""

from falcons.ops import ProjectOps


class BindCase(ProjectOps):
    """绑定案例"""
    uri = '/team/{team_uuid}/testcase/bind_case'
    name = '绑定案例'
    api_type = 'POST'


class UnBindCase(ProjectOps):
    """解绑案例"""
    uri = '/team/{team_uuid}/testcase/unbind_case'
    name = '解绑案例'
    api_type = 'POST'


class CopyCase(ProjectOps):
    """拷贝用例接口"""
    uri = '/team/{team_uuid}/testcase/library/{lib_uuid}/cases/copy'
    name = '拷贝用例'
    api_type = 'POST'


class AddCaseLibrary(ProjectOps):
    uri = '/team/{team_uuid}/testcase/libraries/add'
    name = '新建用例库'
    api_type = 'POST'


class UpdateLibraryConfig(ProjectOps):
    uri = '/team/{team_uuid}/testcase/library/{library_uuid}/update'
    name = '变更用例库名'
    api_type = 'POST'


class DeleteLibrary(ProjectOps):
    uri = '/team/{team_uuid}/testcase/library/{library_uuid}/delete'
    name = '删除用例库'
    api_type = 'POST'


class AddLibraryModule(ProjectOps):
    uri = '/team/{team_uuid}/testcase/library/{library_uuid}/modules/add'
    name = '添加用例库模块'
    api_type = 'POST'


class UpdateLibraryModule(ProjectOps):
    uri = '/team/{team_uuid}/testcase/library/{library_uuid}/modules/update'
    name = '修改模块名称'
    api_type = 'POST'


class DeleteLibraryModule(ProjectOps):
    uri = '/team/{team_uuid}/testcase/library/{library_uuid}/modules/delete'
    name = '删除模块'
    api_type = 'POST'


class ModulesSort(ProjectOps):
    uri = '/team/{team_uuid}/testcase/library/{library_uuid}/modules/sort'
    name = '模块排序'
    api_type = 'POST'


class MoveLibraryCase(ProjectOps):
    uri = '/team/{team_uuid}/testcase/library/{library_uuid}/cases/move'
    name = '移动用例库用用例'
    api_type = 'POST'


class DeleteLibraryCase(ProjectOps):
    uri = '/team/{team_uuid}/testcase/library/{library_uuid}/cases/delete'
    name = '删除用例库用例'
    api_type = 'POST'


class ExportLibraryCase(ProjectOps):
    uri = '/team/{team_uuid}/testcase/library/{library_uuid}/export'
    name = '导出用例库用例'
    api_type = 'POST'


class CaseLibraryPin(ProjectOps):
    uri = '/team/{team_uuid}/testcase/library/{library_uuid}/pin'
    name = '置顶用例库'
    api_type = 'POST'


class CaseLibraryUnPin(ProjectOps):
    uri = '/team/{team_uuid}/testcase/library/{library_uuid}/unpin'
    name = '取消置顶用例库'
    api_type = 'POST'


class CaseRelPlan(ProjectOps):
    uri = '/team/{team_uuid}/testcase/plan/{plan_uuid}/cases/add'
    name = '测试用例关联计划'
    api_type = 'POST'


class CaseAttachment(ProjectOps):
    uri = '/team/{team_uuid}/testcase/case/{case_uuid}/attachments'
    name = '用例详情附件'
    api_type = 'POST'


class AddCasePlan(ProjectOps):
    uri = '/team/{team_uuid}/testcase/plans/add'
    name = '新增测试计划'
    api_type = 'POST'


class UpdatePlanStatus(ProjectOps):
    uri = '/team/{team_uuid}/testcase/plan/{plan_uuid}/update_status'
    name = '流转测试计划状态'
    api_type = 'POST'


class DeletePlan(ProjectOps):
    uri = '/team/{team_uuid}/testcase/plan/{plan_uuid}/delete'
    name = '删除测试计划'
    api_type = 'POST'


class UpdatePlanInfo(ProjectOps):
    uri = '/team/{team_uuid}/testcase/plan/{plan_uuid}/update'
    name = '更新测试计划信息'
    api_type = 'POST'


class UpdatePlanCase(ProjectOps):
    uri = '/team/{team_uuid}/testcase/plan/{plan_uuid}/cases/update'
    name = '更新测试计划用例'
    api_type = 'POST'


class PlanExecutor(ProjectOps):
    uri = '/team/{team_uuid}/testcase/plan/{plan_uuid}/executors'
    name = '执行人'
    api_type = 'GET'


class ExportPlanCase(ProjectOps):
    uri = '/team/{team_uuid}/testcase/plan/{plan_uuid}/export'
    name = '导出测试计划用例'
    api_type = 'POST'


class ViewReport(ProjectOps):
    uri = '/team/{team_uuid}/testcase/report/{report_uuid}/view_report'
    name = '测试报告视图'
    api_type = 'GET'


class ExportReport(ProjectOps):
    uri = '/team/{team_uuid}/testcase/report/{report_uuid}/export_report'
    name = '导出测试报告'
    api_type = 'POST'


class UpdateReport(ProjectOps):
    uri = '/team/{team_uuid}/testcase/report/{report_uuid}/update_report'
    name = '变更测试报告'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

class CaseFilter(ProjectOps):
    uri = '/team/{team_uuid}/items/graphql?t=library-testcase-list-paged'
    name = '筛选器选项内容'
    api_type = 'POST'


class DeleteTestCaseFieldConfig(ProjectOps):
    uri = '/team/{team_uuid}/item/testcase_field_config-{config_uuid}/delete'
    name = '删除测试用例属性配置'
    api_type = 'POST'


class DeletePlanField(ProjectOps):
    uri = '/team/{team_uuid}/item/{key}/delete'
    name = '删除测试计划属性'
    api_type = 'POST'


class AttachmentDownload(ProjectOps):
    uri = '/team/{team_uuid}/res/attachment/{file_uuid}?action=download'
    name = '下载文件'
    api_type = 'GET'


class AttachmentBatchDownload(ProjectOps):
    uri = '/team/{team_uuid}/res/attachments/batch_download'
    name = '批量下载文件'
    api_type = 'POST'


class PreviewAttachment(ProjectOps):
    uri = '/team/{team_uuid}/res/attachment/{file_uuid}'
    name = '预览附件信息'
    api_type = 'POST'


class PreviewImgAttachment(ProjectOps):
    uri = '/team/{team_uuid}/res/attachment/{file_uuid}'
    name = '预览文件'
    api_type = 'GET'


class UpdateAttachment(ProjectOps):
    uri = '/team/{team_uuid}/res/attachment/update/{file_uuid}'
    name = '修改附件信息'
    api_type = 'POST'


class DeleteAttachment(ProjectOps):
    uri = '/team/{team_uuid}/res/attachments/delete'
    name = '删除详情附件'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

class PlanReportTemplateAdd(ProjectOps):
    uri = '/team/{team_uuid}/testcase/plan_report_tpls/add'
    name = '新建测试报告模版'
    api_type = 'POST'


class ReportTemplateInfo(ProjectOps):
    uri = '/team/{team_uuid}/testcase/plan_report_tpls'
    name = '测试报告模版信息'
    api_type = 'GET'


class ReportTemplateUpdate(ProjectOps):
    uri = '/team/{team_uuid}/testcase/plan_report_tpl/{template_uuid}/update'
    name = '更新测试报告模版'
    api_type = 'POST'


class ReportTemplateDelete(ProjectOps):
    uri = '/team/{team_uuid}/testcase/plan_report_tpl/{template_uuid}/delete'
    name = '删除测试报告模版'
    api_type = 'POST'


class FieldDelete(ProjectOps):
    uri = '/team/{team_uuid}/item/{field_key}/delete'
    name = '删除测试管理配置中某个属性'
    api_type = 'POST'


# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------

class CaseFieldUpdate(ProjectOps):
    uri = '/team/{team_uuid}/item/{field_key}/update'
    name = '配置中心-测试用例属性变更'
    api_type = 'POST'


class UsedCount(ProjectOps):
    uri = '/team/{team_uuid}/field_option/used_count'
    name = '属性字段正在被使用次数'
    api_type = 'POST'


class CaseFieldConfigCopy(ProjectOps):
    uri = '/team/{team_uuid}/testcase/field_config/copy'
    name = '复制用例属性配置'
    api_type = 'POST'


class AddTestCaseDefaultMemberPermission(ProjectOps):
    uri = '/team/{team_uuid}/related_project/{project_uuid}/default_members/add'
    name = '新增关联项目配置默认成员权限'
    api_type = 'POST'


class DelTestCaseDefaultMemberPermission(ProjectOps):
    uri = '/team/{team_uuid}/related_project/{project_uuid}/default_members/delete'
    name = '删除关联项目配置默认成员权限'
    api_type = 'POST'


class UpdateTestCaseConfig(ProjectOps):
    uri = '/team/{team_uuid}/related_project/{project_uuid}/config/update'
    name = '更新关联项目配置默认成员权限'
    api_type = 'POST'
