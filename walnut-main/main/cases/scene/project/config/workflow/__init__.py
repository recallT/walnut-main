from falcons.com.env import User
from falcons.com.ones import unify_login
from falcons.ops import generate_param, ProjectOps, WikiOps
from falcons.com.nick import step
from falcons.check import go
from typing import Union
from main.api import project, issue
from main.params import issue as ise, proj, com, conf
from main.actions.task import TaskAction
from main.actions.issue import IssueAction
from main.cases.scene.configs.issue import IssueConfig
from main.helper.email_helper import EmailGateApi, EmailReader
import time

options = [
    {
        "value": "选项001",
        "background_color": "#307fe2",
        "color": "#fff"
    },
    {
        "value": "选项002",
        "background_color": "#00b388",
        "color": "#fff"
    }
]


def update_post_action(transition, post_function: [dict]) -> Union[ProjectOps, WikiOps]:
    '''
    更新后置动作
    :param project_uuid:
    :param issue_type_uuid:
    :param transition: 步骤
    :param post_function: 后置动作配置
    :return:
    '''
    param = ise.post_action()[0]
    param.json_update('transition.uuid', transition['uuid'])
    param.json_update('transition.issue_type_uuid', transition['issue_type_uuid'])
    param.json_update('transition.project_uuid', transition['project_uuid'])
    param.json_update('transition.post_function', post_function)
    param.uri_args({"project_uuid": transition['project_uuid'],
                    "issue_type_uuid": transition['issue_type_uuid'],
                    "transition_uuid": transition['uuid']})
    r = go(issue.PostActionUpdate, param)
    return r


def add_custom_field(field_type, project_uuid, issue_type_name='任务', **kwargs):
    '''添加自定义属性'''
    with step('全局-添加工作项属性'):
        field_uuid = IssueConfig.issue_field_add(field_type=field_type, **kwargs)
        add_field_config = {
            "field_uuid": field_uuid,
            "required": False
        }
    with step('项目-添加工作项属性'):
        TaskAction.task_add_field(add_field_config, issue_types=issue_type_name,
                                  project_uuid=project_uuid)
    return field_uuid


def delete_custom_field(field_uuid, project_uuid, issue_type_name='任务'):
    '''删除自定义属性'''
    with step('项目-删除工作项属性'):
        TaskAction.task_delete_field(field_uuid, issue_types=issue_type_name,
                                     project_uuid=project_uuid)
    with step('全局-删除工作项属性'):
        IssueAction.del_field(field_uuid)


def get_default_role(project_uuid):
    '''默认角色：项目成员'''
    param = generate_param({"role_config": 0}, is_project=True)[0]
    param.uri_args({"project_uuid": project_uuid})
    res1 = go(project.ProjectStamp, param)

    return res1.value('role_config.role_configs[0].role_uuid')  # 默认角色: 项目成员


def get_start_step(project_uuid, issue_type_name):
    '''步骤-开始任务'''
    param = generate_param({"transition": 0,
                            "issue_type_config": 0}, is_project=True)[0]
    param.uri_args({"project_uuid": project_uuid})
    res = go(project.ProjectStamp, param)
    issue_type_uuid = [i['issue_type_uuid'] for i in res.value('issue_type_config.issue_type_configs') if
                       i['name'] == issue_type_name][0]
    transitions = res.value('transition.transitions')
    start_step = [tr for tr in transitions if tr['name'] == '开始任务' and tr['issue_type_uuid'] == issue_type_uuid][0]
    return start_step


def get_finish_step(project_uuid, issue_type_name='任务'):
    '''步骤-完成任务'''
    param = generate_param({"transition": 0,
                            "issue_type_config": 0,
                            "task_status_config": 0}, is_project=True)[0]
    param.uri_args({"project_uuid": project_uuid})
    res1 = go(project.ProjectStamp, param, is_print=False)
    # issue_type_uuid
    issue_type_uuid = [i['issue_type_uuid'] for i in res1.value('issue_type_config.issue_type_configs') if
                       i['name'] == issue_type_name][0]

    transitions = res1.value('transition.transitions')
    # 任务状态
    task_status_config = [s for s in res1.value('task_status_config.task_status_configs') if
                          s['issue_type_uuid'] == issue_type_uuid]
    default_status = [s['status_uuid'] for s in task_status_config if s['default']][0]  # 新建任务时的默认状态

    # 步骤：完成任务, 开始状态为任务的初始状态：未完成
    finish_step = [tr for tr in transitions if tr['name'] == '完成任务'
                   and tr['issue_type_uuid'] == issue_type_uuid
                   and tr['start_status_uuid'] == default_status][0]
    return finish_step


def get_project_assign(project_uuid):
    '''项目负责人'''
    param = generate_param({"project": 0}, is_project=True)[0]
    param.uri_args({"project_uuid": project_uuid})
    res = go(project.ProjectStamp, param, is_print=False)
    return res.value('project.projects[0].assign')


def get_status_list(project_uuid, issue_type_name) -> dict:
    '''通过工作项名称获取工作项状态'''
    param = generate_param({"issue_type_config": 0,
                            "task_status_config": 0}, is_project=True)[0]
    param.uri_args({"project_uuid": project_uuid})
    r = go(project.ProjectStamp, param, is_print=False)
    issue_type_uuid = [i['issue_type_uuid'] for i in r.value('issue_type_config.issue_type_configs') if
                       i['name'] == issue_type_name][0]
    task_status_config = [s for s in r.value('task_status_config.task_status_configs') if
                          s['issue_type_uuid'] == issue_type_uuid]

    task_status = [s['status_uuid'] for s in task_status_config]
    t_param = generate_param({'task_status': 0})[0]
    t = go(project.TeamStampData, t_param, is_print=False)
    t_status = t.value('task_status.task_statuses')
    s_map = {}
    for s in t_status:
        if s['uuid'] in task_status:
            s_map[s['name']] = s['uuid']
    return s_map


def get_default_status(project_uuid, issue_type_name):
    '''通过工作项名称获取默认状态'''
    param = generate_param({"issue_type_config": 0,
                            "task_status_config": 0}, is_project=True)[0]
    param.uri_args({"project_uuid": project_uuid})
    r = go(project.ProjectStamp, param, is_print=False)
    issue_type_uuid = [i['issue_type_uuid'] for i in r.value('issue_type_config.issue_type_configs') if
                       i['name'] == issue_type_name][0]
    task_status_config = [s for s in r.value('task_status_config.task_status_configs') if
                          s['issue_type_uuid'] == issue_type_uuid]

    default_status = [s['status_uuid'] for s in task_status_config if s['default']][0]

    return default_status


def get_issue_types(project_uuid):
    '''项目工作项类型uuid map'''
    '''项目配置'''
    param = generate_param({"issue_type_config": 0}, is_project=True)[0]
    param.uri_args({"project_uuid": project_uuid})
    res1 = go(project.ProjectStamp, param, is_print=False)
    # 工作项类型
    issue_types = {}
    for i in res1.value('issue_type_config.issue_type_configs'):
        issue_types[i['name']] = i['issue_type_uuid']

    return issue_types  # 工作类型列表


def trigger(task_uuid, transit_uuid, token=None):
    '''触发任务步骤'''
    pam1 = proj.update_transit_status(transit_uuid)[0]
    pam1.uri_args({'tasks_uuid': task_uuid})
    res = go(project.UpdateTransitStatus, pam1, token=token)
    return res


def check_field(task_uuid, field_uuid, field_expect_value):
    task_info = TaskAction.task_info(task_uuid)
    field = [f for f in task_info.json()['field_values'] if f['field_uuid'] == field_uuid][0]
    if isinstance(field['value'], list):
        field['value'].sort()
    if isinstance(field_expect_value, list):
        field_expect_value.sort()
    assert field['value'] == field_expect_value, '任务属性值不符合预期'


def trigger_and_check(transition, issue_type_name: str = '任务',
                      field_uuid='', field_expect_value='', is_check_field=True,
                      creator: Union[None, User] = None,
                      operator: Union[None, User] = None,
                      field004=None,
                      watcher_uuid=None):
    '''
    触发后置动作，检查属性值
    :param watcher_uuid: 任务关注者
    :param field004: 任务负责人
    :param owner_uuid: 任务创建者
    :param transition:
    :param issue_type_name:
    :param field_uuid:
    :param field_expect_value:
    :param is_check_field:
    :param creator: 任务创建者（默认为超管）
    :param operator: 任务触发者（默认为超管）
    :return:
    '''
    # c_token = None
    # 新建任务
    # if creator and :
    #     creator.token = unify_login(creator)
    c_token = creator.token if creator else None
    owner_uuid = creator.owner_uuid if creator else None
    task_uuid = TaskAction.new_issue(proj_uuid=transition['project_uuid'],
                                     token=c_token,
                                     owner_uuid=owner_uuid,
                                     field004=field004,
                                     watcher_uuid=watcher_uuid)[0]
    if issue_type_name.startswith('子'):
        task_uuid = TaskAction.new_issue(proj_uuid=transition['project_uuid'], parent_uuid=task_uuid,
                                         issue_type_name=issue_type_name,
                                         token=c_token,
                                         owner_uuid=owner_uuid,
                                         field004=field004,
                                         watcher_uuid=watcher_uuid
                                         )[0]
    op_token = None
    # 触发任务
    if operator and (not operator.token):
        operator.token = unify_login(operator)
        op_token = operator.token

    trigger(task_uuid, transition['uuid'], token=op_token)
    task_info = TaskAction.task_info(task_uuid)
    task_info.check_response('status_uuid', transition['end_status_uuid'])

    if is_check_field and not field_uuid and not field_expect_value:
        raise ValueError(f'需要检查属性时， field_uuid, field_expect_value不能为空！')
    # 是否检查属性
    if is_check_field:
        updated_field = [f for f in task_info.json()['field_values'] if f['field_uuid'] == field_uuid][0]
        if isinstance(updated_field['value'], list):
            updated_field['value'].sort()
        if isinstance(field_expect_value, list):
            field_expect_value.sort()
        assert updated_field['value'] == field_expect_value, '任务属性值不符合预期'
    return task_uuid


def relate_tasks(task1_uuid, task2_uuid):
    '''关联任务'''
    parm = conf.link_related_task(task2_uuid, 'UUID0001')[0]  # 关联类型为：关联
    parm.uri_args({'tasks_uuid': task1_uuid})
    res = go(project.LinkRelatedTask, parm)
    return res


def field_options(field_uuid):
    '''属性选项'''
    param = com.gen_stamp({"field": 0})
    res = go(project.TeamStampData, param).json()
    field = [f for f in res['field']['fields'] if f['uuid'] == field_uuid][0]
    return field['options']


def wait_email_receive(receiver, task_uuid):
    '''
    等待收邮件
    :param receiver: 收件人邮箱地址
    :param task_uuid:
    :return:
    '''
    task_info = TaskAction.task_info(task_uuid)
    for _ in range(10):
        time.sleep(1)
        _e = EmailGateApi().first_mail()
        if _e:
            _condition1 = f'Test Admin 编辑了「#{task_info.value("number")} {task_info.value("summary")}」' in _e['subject']
            _condition2 = _e['to'] == receiver
            if not _condition1 or not _condition2:
                continue
            else:
                return _e
        else:
            continue
