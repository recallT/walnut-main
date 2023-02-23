from falcons.check import go
from falcons.ops import generate_param

from main.api import task as ta, project, issue
from main.params import task, proj, conf
from main.params.const import ACCOUNT
from main.actions.issue import IssueAction as ia


def permission_rules(project_uuid=ACCOUNT.project_uuid):
    """获取项目权限规则信息"""
    param = task.lite_context_permission_rules()[0]
    param.json_update('context_param.project_uuid', project_uuid)
    param.json_update('context_type', 'project')

    resp = go(ta.LiteContextPermissionRules, param)

    return resp.json()


def get_start_step(project_uuid, issue_type_name):
    """步骤-开始任务"""
    param = generate_param({"transition": 0,
                            "issue_type_config": 0}, is_project=True)[0]
    param.uri_args({"project_uuid": project_uuid})
    res = go(project.ProjectStamp, param)
    issue_type_uuid = [i['issue_type_uuid'] for i in res.value('issue_type_config.issue_type_configs') if
                       i['name'] == issue_type_name][0]
    transitions = res.value('transition.transitions')
    start_step = [tr for tr in transitions if tr['name'] == '开始任务' and tr['issue_type_uuid'] == issue_type_uuid][0]
    return start_step


def trigger(task_uuid, transit_uuid, token=None, code=None):
    """触发任务步骤"""
    pam1 = proj.update_transit_status(transit_uuid)[0]
    pam1.uri_args({'tasks_uuid': task_uuid})
    res = go(project.UpdateTransitStatus, pam1, token=token, status_code=code if code else 200)
    return res


def get_permission_uuids(permission_type, project_uuid, it_name='任务'):
    """项目-某项工作项权限-id列表"""
    res = ia.get_pro_permission_rules(it_name, project_uuid=project_uuid)
    uuids = [r['uuid'] for r in res.value('permission_rules') if
             r['permission'] == permission_type]
    return uuids


def clear_permission(permission_type, project_uuid, it_name='任务'):
    """项目-清空某工作项权限"""
    perm_uuids = get_permission_uuids(permission_type, project_uuid, it_name)
    for i in perm_uuids:
        ia.del_issue_permission(i)


def add_permission(pid, it_id, permission, user_domain_type, user_domain_param):
    """添加工作项权限"""
    param = {
        "permission_rule": {
            "context_type": "issue_type",
            "context_param": {
                "project_uuid": pid,
                "issue_type_uuid": it_id
            },
            "permission": permission,
            "user_domain_type": user_domain_type,
            "user_domain_param": user_domain_param
        }
    }
    param = generate_param(param)[0]
    return go(project.PermissionAdd, param)


def get_default_role(project_uuid):
    """默认角色：项目成员"""
    param = generate_param({"role_config": 0}, is_project=True)[0]
    param.uri_args({"project_uuid": project_uuid})
    res1 = go(project.ProjectStamp, param, is_print=False)

    return res1.value('role_config.role_configs[0].role_uuid')  # 默认角色: 项目成员


def clear_issue_field_contraint(pid, issue_uuid, issue_type_uuid):
    """清空项目的属性修改权限"""
    # 获取工作项的属性修改权限列表
    param_g = proj.get_task_permission_list(issue_uuid)[0]
    r = go(project.ItemGraphql, param_g, is_print=False)
    f_contraints = [c['issueTypeScopeFieldConstraints'] for c in r.value('data.buckets')]
    # 清除工作项的属性修改权限
    if f_contraints:
        uuids = []
        for cs in f_contraints:
            uuids += [c['uuid'] for c in cs]
        param = conf.proj_constraints_del(uuids)[0]
        param.uri_args({'project_uuid': pid})
        param.uri_args({'issue_type_uuid': issue_type_uuid})
        go(issue.ProjConstraintsDelete, param, is_print=False)
