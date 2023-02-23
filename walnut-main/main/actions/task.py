#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：task.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/7 
@Desc    ：一些常用接口的快捷调用方法
"""
import json
import time
from typing import Union

from falcons.check import go
from falcons.com.meta import OnesParams
from falcons.com.nick import step
from falcons.helper import mocks

from main.api import current as c, project
from main.api import issue as ise
from main.api import project as pj
from main.api import sprint as spt
from main.api import task as tk
from main.api.project import ItemGraphql, QueuesList
from main.helper.extra import retry
from main.params import com
from main.params import current as curr
from main.params import proj, task
from main.params import proj as p
from main.params.const import ACCOUNT
from main.params.task import plan_task_drag, queue_list


def team_stamp(param: dict, token: dict = None) -> dict:
    """
    调用全局team_stamp类型信息
    :param param: 查询数据 参数 如 `{'issue_type':0}`
    :param token: 可选
    :return:
    """

    prm = com.gen_stamp(param)
    res = go(pj.TeamStampData, prm, token, is_print=False)

    return res.json()


def proj_team_stamp(param: dict, token: dict = None):
    """
    项目team_stamp信息
    :param param: 查询数据 参数 如 `{'issue_type':0}`
    :param token:
    :return:
    """
    params = p.proj_stamp(param)[0]
    issue_resp = go(pj.ProjectStamp, params, token, is_print=False)

    return issue_resp.json()


def global_issue_type(issue_name='任务', token: dict = None) -> dict:
    """
    获取全局工作项类型信息

    :param token:
    :param issue_name
    :return:
    """

    param = com.issue_type()
    resp = go(ise.IssueTypes, param, token, is_print=False)
    issue_data = [r for r in resp.value('issue_types') if r['name'] == issue_name][0]

    return issue_data


class TaskAction:
    """任务用例各类"""

    @classmethod
    def task_stamp(cls, flush=False, token=None) -> dict:
        """获取工作项配置"""
        field_param = task.task_field(flush)[0]
        if not flush:
            return field_param
        else:
            stamp_resp = go(pj.TeamStampData, field_param, token)

            return stamp_resp.json()

    @classmethod
    def get_task_status_and_issue_uid(cls, target_type='任务', proj_uuid=ACCOUNT.project_uuid, token=None):
        """
        获取工作项类型的状态和工作项uuid
        :param token
        :param target_type 工作项类型
        :param proj_uuid  项目uuid
        """
        prm = p.proj_stamp()[0]
        prm.json = {"issue_type_config": 0, "task_status_config": 0}
        prm.uri_args({"project_uuid": proj_uuid})
        issue_resp = go(pj.ProjectStamp, prm, token, is_print=False).json()

        issue_type_uuid = [s['issue_type_uuid'] for s in issue_resp['issue_type_config']['issue_type_configs'] if
                           s['name'] == target_type][0]  # 获取任务工作项的属性uuid

        target_status = [n['status_uuid'] for n in issue_resp['task_status_config']['task_status_configs'] if
                         n['issue_type_uuid'] == issue_type_uuid][0]  # 获取工作项状态

        return target_status, issue_type_uuid

    @classmethod
    @retry
    def new_issue(cls, parent_uuid='',
                  issue_type_name='任务',
                  is_batch=False,
                  token=None,
                  proj_uuid=ACCOUNT.project_uuid,
                  param_only=False,
                  owner_uuid=None,
                  field004=None,
                  watcher_uuid=None) -> [list[str], OnesParams]:

        """
        创建工作项
        :param token:
        :param parent_uuid: 父工作项uuid
        :param issue_type_name: 任务，子任务，需求，子需求， 缺陷 五种
        :param is_batch: 是否批量添加任务 默认为否
        :param param_only: 是否返回请求参数 默认为否
        :param proj_uuid  所属工作项
        :param owner_uuid: 创建者
        :param field004: 负责人
        :param watcher_uuid: 关注者
        :return:
        """
        task_no = 6 if is_batch else 1
        add_p = task.task_add(task_no, proj_uuid,
                              owner_uuid=owner_uuid,
                              field004=field004,
                              watcher_uuid=watcher_uuid)[0]

        is_sub_issue = '子' in issue_type_name
        if is_sub_issue and not parent_uuid:
            raise ValueError(f'创建{issue_type_name}时 parent_uuid 不能为空！')

        with step('获取工作项属性数据'):

            j = cls.task_stamp(flush=True)
            field_conf_uid = [c['default_value'] for c in j['field_config']['field_configs'] if
                              c['field_uuid'] == 'field012'][0]  # 用默认值就好了
            issue_conf_uid = [c['issue_type_uuid'] for c in j['issue_type_config']['issue_type_configs'] if
                              c['name'] == issue_type_name]  # 获取任务工作项的属性uuid
            if not issue_conf_uid:
                raise ValueError(f'没查到 {issue_type_name} 的uuid')
            # update param value
            for idx in range(task_no):
                add_p.json['tasks'][idx]['field_values'][1] |= {'value': field_conf_uid}
                add_p.json['tasks'][idx] |= {'issue_type_uuid': issue_conf_uid[0]}
                if is_sub_issue:
                    add_p.json['tasks'][idx] |= {'sub_issue_type_uuid': issue_conf_uid[0]}
                if parent_uuid:
                    add_p.json['tasks'][idx]['parent_uuid'] = parent_uuid

        if param_only:
            return add_p
        else:
            with step('创建任务'):

                resp = go(tk.TaskAdd, add_p, token)
                task_uuid = [r['uuid'] for r in resp.json()['tasks']]

                if not task_uuid:
                    raise RuntimeError(f'创建任务失败！')
                return task_uuid

    @classmethod
    def new_issue_batch(cls, batch_no=6, issue_type_name='任务', proj_uuid=ACCOUNT.project_uuid, token=None) -> tuple:
        """
        批量创建工作项

        :param token:
        :param batch_no: 批量任务数
        :param issue_type_name: 任务，需求 缺陷 三种
        :param proj_uuid  所属的项目
        :return:
        """
        add_p = task.task_add(batch_no, proj_uuid)[0]

        with step('获取工作项属性数据'):
            j = cls.task_stamp(flush=True, token=token)
            field_conf_uid = [c['default_value'] for c in j['field_config']['field_configs'] if
                              c['field_uuid'] == 'field012'][0]  # 用默认值就好了
            issue_conf_uid = [c['issue_type_uuid'] for c in j['issue_type_config']['issue_type_configs'] if
                              c['name'] == issue_type_name]  # 获取任务工作项的属性uuid
            if not issue_conf_uid:
                raise ValueError(f'没查到 {issue_type_name} 的uuid')
            # update param value
            for idx in range(batch_no):
                add_p.json['tasks'][idx]['field_values'][1] |= {'value': field_conf_uid}
                add_p.json['tasks'][idx] |= {'issue_type_uuid': issue_conf_uid[0]}

        with step('批量创建任务'):
            task_uuids = [t['uuid'] for t in add_p.json['tasks']]
            resp = go(tk.TaskBatchAdd, add_p, token)
            backup_task_uuid = resp.value('uuid')  # 这里返回的是批量任务的UUID

            return task_uuids, backup_task_uuid

    @classmethod
    def wait_to_done(cls, batch_uuid, token=None, timeout=120):
        """
        等待后台批量任务执行完毕
        :param token:
        :param batch_uuid: 后台任务UUID
        :param timeout: 等待任务完成时间 默认120秒
        :return:
        """
        param = p.queues_list()[0]
        for _ in range(timeout):
            time.sleep(1)
            resp = go(pj.QueuesList, param, token)

            result = [u for u in resp.value('batch_tasks') if u['uuid'] == batch_uuid]

            if not result:
                continue
            if result[0]['job_status'] == 'done':
                return True
        else:
            raise RuntimeError('Waiting batch task status timeout....')

    @classmethod
    def del_task(cls, task_uuid, token=None, status_code=None):
        """删除任务"""
        del_p = task.task_delete()[0]
        del_p.uri_args({'task_uuid': task_uuid})
        return go(tk.TaskDelete, del_p, token, status_code=status_code if status_code else 200)

    @classmethod
    def del_task_batch(cls, task_uuids):
        """批量删除任务"""
        del_p = task.task_delete_batch()[0]
        del_p.json['tasks'] = task_uuids

        return go(tk.TaskBatchDelete, del_p)

    @classmethod
    def sprint_add(cls) -> str:
        """新增迭代"""
        spt_p = p.sprint_add()[0]
        resp = go(spt.SprintAdd, spt_p)
        return resp.json()['sprints'][0]['uuid']

    @classmethod
    def task_info(cls, task_uuid, token=None):
        """获取任务详情"""
        with step('获取任务详情'):
            info_p = task.task_info()[0]
            info_p.uri_args({'task_uuid': task_uuid})
            return go(tk.TaskInfo, info_p, token)

    @classmethod
    def task_copy(cls, task_uuid, target_type='缺陷', token=None):
        """复制任务"""
        status_uid, issue_uid = cls.get_task_status_and_issue_uid(target_type)

        with step(f'复制任务为{target_type}'):
            """"""
            cop = task.task_copy()[0]
            cop.json |= {'issue_type_uuid': issue_uid, 'status_uuid': status_uid}
            cop.uri_args({'task_uuid': task_uuid})

            return go(tk.TaskCopy, cop, token)

    @classmethod
    def task_copy_batch(cls, task_uuid: list, target_type='任务', token=None):
        """批量复制任务"""
        status_uid, issue_uid = cls.get_task_status_and_issue_uid(target_type)

        with step(f'复制任务为{target_type}'):
            tasks = []
            for u in task_uuid:
                param = {
                    "task_uuid": u,
                    "project_uuid": ACCOUNT.project_uuid,
                    "issue_type_uuid": issue_uid,
                    "status_uuid": status_uid
                }
                tasks.append(param)

            cop = task.task_batch_copy()[0]
            cop.json_update('tasks', tasks)

            return go(tk.TaskBatchCopy, cop, token)

    @classmethod
    def upload_file(cls, task_uuid, name='', token=None):
        """上传附件"""

        img_name = f"TestImg_{mocks.ones_uuid()}" if not name else name

        with step('上传文件-token'):
            token_p = task.upload_file(img_name)[0]
            token_p.json_update('ref_id', task_uuid)
            resp = go(tk.ResAttUpload, token_p, token)

            j = resp.json()
            token = j['token']
            url = j['upload_url']

            file_uuid = j['resource_uuid']

        with step('上传文件'):
            """"""
            box = tk.UpBox()
            box.call({'token': token, 'img_name': img_name}, url)

            box.is_response_code(200)

        return file_uuid

    @classmethod
    def task_messages(cls, task_uuid, token=None):
        """
        获取工作项动态
        :param token:
        :param task_uuid:
        :return:
        """

        m_param = task.task_messages()[0]
        m_param.uri_args({'task_uuid': task_uuid})
        return go(tk.TaskMessages, m_param, token)

    @classmethod
    def update_task_info(cls, task_uuid, info: dict, token=None):
        """
        更新任务信息
        :param task_uuid: 任务UUID
        :param info: 更新的信息字典
        如 info={
                "field_uuid": field_uuid,
                "type": 8,
                "value": user_a.owner_uuid
            }
        :param token:
        :return:
        """
        u_param = task.task_update()[0]
        u_param.json_update('tasks[0].uuid', task_uuid)
        u_param.json['tasks'][0]['field_values'].append(info)

        return go(tk.TaskUpdate3, u_param, token)

    @classmethod
    def issue_type_uuid(cls, issue_types='任务',
                        uuid_type='issue_type_uuid',
                        project_uuid=None,
                        token=None) -> list[str]:
        """
        获取工作项类型uuid
        :param token
        :param issue_types  # 工作项类型
        :param project_uuid
        :param uuid_type  # 返回的字段

        """
        uid = project_uuid if project_uuid else ACCOUNT.project_uuid
        prm = p.proj_stamp()[0]
        prm.json = {"issue_type_config": 0}
        prm.uri_args({'project_uuid': uid})
        issue_response = go(pj.ProjectStamp, prm, token, is_print=False)

        response = issue_response.value('issue_type_config.issue_type_configs')
        issue_uuid = [u[uuid_type] for u in response if u['name'] == issue_types]

        if not issue_uuid:
            raise ValueError(f'获取 {issue_types}: UUID 失败！')

        return issue_uuid

    @classmethod
    def task_status_uuid(cls, status: Union[str, list] = '未开始') -> Union[str, dict]:
        """
        获取工作项系统状态类型uuid
        :param status 工作项状态(如 任务-未开始/进行中，缺陷-未激活/确认)等
        """
        stamp = cls.task_stamp(flush=True)
        if type(status) == str:
            status_uuid = [s['uuid'] for s in stamp['task_status']['task_statuses'] if
                           s['name'] == status]
            if not status_uuid:
                raise ValueError(f'获取状态uuid 失败 {status}')

            return status_uuid[0]
        elif type(status) == list:
            status_uuids = [s for s in stamp['task_status']['task_statuses'] if
                            s['name'] in status]
            s_map = {}
            for s in status_uuids:
                s_map[s['name']] = s['uuid']
            return s_map

    @classmethod
    def task_field_value_uuid(cls, field_name, value, token=None) -> str:
        """
        获取工作项系统属性值uuid
        :param token
        :param field_name  属性名称 如：优先级/是否线上缺陷等
        :param value  属性的具体选项值
        """
        param = task.task_field(True)[0]
        param.json = {"field": 0}
        stamp_resp = go(pj.TeamStampData, param, token)

        pri_uuid = [u['uuid'] for n in stamp_resp.value('field.fields') if n['name'] == field_name
                    for u in n['options'] if u['value'] == value][0]

        return pri_uuid

    @classmethod
    def task_add_field(cls, field_config: dict, issue_types='任务', project_uuid=ACCOUNT.project_uuid, token=None):
        """工作项类型添加属性"""

        issue_uuid = cls.issue_type_uuid(issue_types)[0]

        param = task.task_add_field()[0]
        param.json_update('field_config', field_config)
        param.uri_args({'issue_uuid': issue_uuid})
        param.uri_args({'project_uuid': project_uuid})

        return go(pj.ProjectIssueFieldAdd, param, token)

    @classmethod
    def task_delete_field(cls, field_uuid, issue_types='任务', project_uuid=ACCOUNT.project_uuid, token=None):
        issue_uuid = cls.issue_type_uuid(issue_types)[0]

        param = com.generate_param({}, is_project=True)[0]
        param.uri_args({'issue_uuid': issue_uuid, })
        param.uri_args({'project_uuid': project_uuid})
        param.uri_args({'field_uuid': field_uuid})

        return go(pj.ProjectIssueFieldDelete, param, token)

    @classmethod
    def export_issue(cls, *must_value, token=None):
        """
        工作项的导出功能

        :param token:
        :param must_value:
        :return:
        """
        param = curr.export_task_job()[0]
        param.json_update('query.must', must_value)
        ex = go(c.ExportTaskJob, param, token)

        key = ex.json()['key']  # 获取下载task的key

        # 下载task
        prm = curr.dashboard_opt()[0]
        prm.uri_args({'key_id': key})
        go(c.DownloadExportTask, prm, token)

    @classmethod
    def plan_task_drag(cls, key, parent, after='', token=None):
        """
        项目计划中拖拽排序
        :param key: 拖拽的任务key
        :param parent: 父类
        :param after: xx任务uuid之前
        :param token:
        :return:
        """
        if 'activity-' not in key:
            key = 'activity-' + key

        param = plan_task_drag(key=key, parent=parent, after=after)[0]

        resp = go(ItemGraphql, param, token)
        resp.check_response('data.updateActivity.key', key)
        return resp

    @classmethod
    def transit_task_status(cls, transition_uuid, tasks_uuid, status_code=200, token=None):
        """
        更新工作项状态
        :param transition_uuid: 更新后状态的uuid
        :param tasks_uuid: 工作项uuid
        :param status_code: 返回预期状态码
        :param token:
        :return:
        """
        pam = proj.update_transit_status(transition_uuid)[0]
        pam.uri_args({'tasks_uuid': tasks_uuid})
        response = go(project.UpdateTransitStatus, pam, token, status_code=status_code)
        return response

    @classmethod
    def get_task_config(cls, token=None):
        """
        获取项目内工作项工作流
        :param token:
        :return:
        """
        param = task.task_config()[0]
        resp = go(project.ProjectStamp, param, token, is_print=False)
        return resp

    @classmethod
    def check_queue_list(cls, url: str, filename: str):
        """查看队列列表"""
        param = queue_list()[0]
        res = go(QueuesList, param).json()
        for t in res['batch_tasks']:
            t['extra'] = json.loads(t['extra'])
            if t['extra']['url'] == url and t['extra']['filename'] == filename:
                return t
