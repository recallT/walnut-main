"""
@Desc    ：迭代相关快捷调用方法
"""
from falcons.check import go
from falcons.helper import mocks

from main.actions.pro import ProjPermissionAction
from main.api import project as pj
from main.api import sprint as spt
from main.api import task as ts
from main.params import com, issue, proj, task, data
from main.params.relation import todo_sprint_info
from main.params.const import ACCOUNT
from main.actions.task import TaskAction
from main.params.com import generate_param


def team_stamp(param: dict, token: dict = None):
    """
    调用TeamStamp接口

    :param param: 查询数据 参数 如 `{'issue_type':0}`
    :param token:
    :return:
    """

    prm = com.gen_stamp(param)

    return go(pj.TeamStampData, prm, token)


class SprintAction:
    """迭代用例各类"""

    @classmethod
    def sprint_add(cls, project_uuid=ACCOUNT.project_uuid, assign=None) -> str:
        """
        新增迭代
        :param assign: 迭代负责人
        :param project_uuid: 项目UUD
        :return:
        """
        spt_p = proj.sprint_add(assign)[0]
        spt_p.uri_args({"project_uuid": project_uuid})
        resp = go(spt.SprintAdd, spt_p)
        return resp.json()['sprints'][0]['uuid']

    @classmethod
    def sprint_status(cls, s_uuid, token=None) -> list:
        """
        迭代状态
        :param s_uuid  迭代uuid
        :param token
        return 状态类型的uuid['未开始', '进行中', '已完成']
        """
        data = {"sprint": 0}
        res = team_stamp(data, token)

        status_uuid = [s['status_uuid'] for u in res.json()['sprint']['sprints'] if u['uuid'] == s_uuid for s in
                       u['statuses']]

        return status_uuid

    @classmethod
    def todo_sprint_info(cls, token=None):
        """
        获取待办事项中迭代信息
        :param token:
        :return:
        """
        task_issues_uuid = TaskAction.issue_type_uuid('任务')[0]
        demand_issues_uuid = TaskAction.issue_type_uuid('需求')[0]

        param = todo_sprint_info([task_issues_uuid, demand_issues_uuid])[0]

        resp = go(pj.ItemGraphql, param, token)
        return resp

    @classmethod
    def new_sprint_issue(cls, sprint_uuid, project_uuid=ACCOUNT.project_uuid, issue_type_name: str = '任务', token=None):
        """创建工作项，并归属到迭代中"""
        # 添加任务
        # issue_type_name = issue_type_name if not issue_type_name else '任务'
        task_uuid = TaskAction.new_issue(proj_uuid=project_uuid, issue_type_name=issue_type_name)[0]
        # 规划任务到迭代
        parm = task.task_detail_edit()[0]
        parm.json['tasks'][0] = {
            "uuid": task_uuid,
            "sprint_uuid": sprint_uuid
        }
        go(ts.TaskUpdate3, parm)

    @classmethod
    def sprint_field_list(cls, field_uuid, default_value):
        # 获取迭代属性列表
        param = proj.sprint_search()[0]
        res = go(spt.ProSprintField, param)
        result = res.value("fields")
        value = [d['default_value'] for d in result if d['uuid'] == field_uuid]
        assert value[0] == default_value

    @classmethod
    def sprint_add_field(cls, field_type, project_uuid=ACCOUNT.project_uuid):
        # 添加新的迭代属性
        param = proj.sprint_field_add(field_type)[0]
        param.uri_args({'project_uuid': project_uuid})
        rest = go(spt.SprintFieldAdd, param)
        return rest

    @classmethod
    def sprint_del_field(cls, field_uuid):
        # 删除迭代属性
        param = data.field_delete()[0]
        param.uri_args({'field_uuid': field_uuid})
        go(spt.SprintFieldDelete, param)

    @classmethod
    def sprint_responsible_member(cls):
        """"新建迭代时，获取迭代负责人的成员列表"""
        key = 'be_assigned_to_sprint'
        param = proj.sprint_search_user(key)[0]
        response = go(pj.UsesSearch, param)
        user = response.value('users')
        return user

    @classmethod
    def update_sprint_status(cls, s_uuid, status='进行中', actual_start_time=None, actual_end_time=None, project_uuid=None,
                             token=None):
        '''
        修改迭代阶段
        :param project_uuid:
        :param s_uuid:
        :param status:
        :param actual_start_time:
        :param actual_end_time:
        :param token:
        :return:
        '''
        # 获取迭代阶段
        p = {"sprint": 0}
        res = team_stamp(p, token)
        ss = [s for s in res.value('sprint.sprints') if s['uuid'] == s_uuid]
        if ss:
            statues = ss[0]['statuses']
            cur_status = [s for s in statues if s['is_current_status']][0]
            next_statuses = [s for s in statues if s['name'] == status]
            if next_statuses:
                next_status = next_statuses[0]
                if next_status['category'] == 'done':
                    next_status['actual_end_time'] = actual_end_time if actual_end_time else mocks.now_timestamp()
                else:
                    next_status['actual_start_time'] = actual_start_time if actual_start_time else mocks.now_timestamp()
                cur_status['is_current_status'] = False
                next_status['is_current_status'] = True
                param = generate_param({'sprint_statuses': [cur_status, next_status]})[0]
                param.uri_args(
                    {'project_uuid': project_uuid if project_uuid else ACCOUNT.project_uuid, 'sprint_uuid': s_uuid})
                go(spt.SprintStatusUpdate, param)
            else:
                raise ValueError(f'迭代阶段不存在：{status}')
        else:
            raise ValueError(f'迭代{s_uuid}不存在')
