"""
@File    ：links.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/6/23
@Desc    ： UI 页面 url 路径配置
"""
from falcons.com.meta import ApiMeta
from falcons.com.ui import UiDriver

from main.actions.pro import PrjAction
from main.actions.task import TaskAction
from main.config import RunVars


class ConfigPrjUrlLinks:
    """项目管理页面URL路径"""
    ROLE_CONFIG = '/team/{team_uuid}/do_setting/role'  # 角色管理
    PROJECT_MANAGER = '/team/{team_uuid}/do_setting/project_manager'  # 项目管理
    PROJECT_FIELD = '/team/{team_uuid}/do_setting/project_field'  # 项目属性
    PROJECT_STATUS = '/team/{team_uuid}/do_setting/project_status'  # 项目状态
    ISSUE_TYPE = '/team/{team_uuid}/do_setting/issue_type'  # 工作项类型
    TASK_FIELD = '/team/{team_uuid}/do_setting/task_field'  # 工作项属性
    TASK_STATUS = '/team/{team_uuid}/do_setting/task_status'  # 工作项状态
    PRIORITY_CONFIG = '/team/{team_uuid}/do_setting/priority_config'  # 优先级
    TASK_RELATED_TYPE_CONFIG = '/team/{team_uuid}/do_setting/task_related_type_config'  # 关联关系类型
    FIELD_CONFIG = '/team/{team_uuid}/do_setting/field_config'  # 产品属性
    VIEW_SETTING = '/team/{team_uuid}/do_setting/view_setting'  # 视图配置
    PRODUCT_PERMISSION = '/team/{team_uuid}/do_setting/product_permission'  # 权限配置


class PrjSettingLinks:
    """项目配置-URL路径"""
    HOME_PAGE = '/team/{team_uuid}/project/{project_uuid}/setting/project'


class PrjSprintLinks:
    """项目迭代"""
    SETTING_PAGE = '/team/{team_uuid}/project/{project_uuid}/setting/sprint'
    STATUS_PAGE = '/team/{team_uuid}/project/{project_uuid}/setting/sprint/status'


class PrjReportLinks:
    """项目报表-URL路径"""
    _prefix = '/team/{team_uuid}/project/{project_uuid}/component/{component_uuid}'
    MINES = f'{_prefix}/report/project_report/report_library/category/create_by_me'
    ALL = f'{_prefix}/report/project_report/report_library/category/all_reports'


class PrjReportDefectLinks:
    """项目报表-缺陷报表"""
    '''/defect_created_solved_trend/edit/report_detail/Ep3TbGwK'''
    _prefix = '/team/{team_uuid}/project/{project_uuid}/component/{component_uuid}/' \
              'report/project_report/report_library/category/{category_uuid}' \
              '/report_type_group/report_type'
    CREATE_SOLVE_TREND = _prefix + '/defect_created_solved_trend/report_detail/{report_uuid}'
    EDIT_CREATE_SOLVE_TREND = _prefix + '/defect_created_solved_trend/edit/report_detail/{report_uuid}'
    DI_OWNER_COMPARE = _prefix + '/defect_di_value_distribution/report_detail/{report_uuid}'
    EDIT_DI_OWNER_COMPARE = _prefix + '/defect_di_value_distribution/edit/report_detail/{report_uuid}'
    DI_DAY_TREND = _prefix + '/defect_di_value_trend/report_detail/{report_uuid}'
    EDIT_DI_DAY_TREND = _prefix + '/defect_di_value_trend/edit/report_detail/{report_uuid}'


class PrjWorkflowLinks:
    """项目工作流-URL链接"""
    FLOW_SETTING = '/team/{team_uuid}/project/{project_uuid}/setting/template/{issue_type_uuid}/workflow'


def full_link(link: str, is_wiki=False):
    """
    生成页面访问的全路径URL
    :param link:
    :param is_wiki: 是否wiki页面 默认为False
    :return:
    """
    pre = f'{UiDriver.env.host}'
    sprint = UiDriver.env.sprint
    sprint_front = UiDriver.env.sprint_front
    __product = 'wiki' if is_wiki else 'project'

    if RunVars.is_dev_host(pre):
        # 前端
        if sprint_front:
            s = sprint_front
        else:
            s = 'master' if not sprint else f'{sprint}'

        pre = pre + f'/{__product}/{s}/#'
    else:
        pre = pre + f'/{__product}/#'

    pre = pre + link
    pre = pre.replace('{team_uuid}', ApiMeta.account.user.team_uuid)
    pre = pre.replace('{project_uuid}', UiDriver.env.project_uuid_ui)

    if link.find('/report/project_report') > -1:
        c = PrjAction.get_component('报表', project_uuid=UiDriver.env.project_uuid_ui)
        pre = pre.replace('{component_uuid}', c['uuid'])

    if link.find('setting/template') > -1 and link.find('workflow'):
        issue_type_uuid = TaskAction.issue_type_uuid(project_uuid=UiDriver.env.project_uuid_ui)[0]
        pre = pre.replace('{issue_type_uuid}', issue_type_uuid)

    return pre


res = PrjAction.get_reports_groups(project_uuid=UiDriver.env.project_uuid_ui)
groups = res['groups']
reports = res['reports']


def prj_report_link(link: str, category_name, report_name):
    _link = full_link(link)
    gg = [g['uuid'] for g in groups if g['name'] == category_name]
    rr = [r['uuid'] for r in reports if r['name'] == report_name]
    if not gg:
        raise ValueError('报表分组不存在')
    if not rr:
        raise ValueError('报表不存在')
    _link = _link.replace('{category_uuid}', gg[0])
    _link = _link.replace('{report_uuid}', rr[0])
    return _link
