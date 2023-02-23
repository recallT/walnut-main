#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：task.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/9 
@Desc    ：工作项接口定义
"""
from falcons.helper import mocks
from falcons.ops import ProjectOps
from requests_toolbelt import MultipartEncoder

from main.config import RunVars


class TaskAdd(ProjectOps):
    """添加工作项"""
    uri = '/team/{team_uuid}/tasks/add2'
    name = '添加工作项'
    api_type = 'POST'


class TaskBatchAdd(ProjectOps):
    """批量添加工作项"""
    uri = '/team/{team_uuid}/tasks/batch_add'
    name = '批量添加工作项'
    api_type = 'POST'


class TaskBatchDelete(ProjectOps):
    """批量删除工作项"""
    uri = '/team/{team_uuid}/tasks/batch/delete'
    name = '批量删除工作项'
    api_type = 'POST'


class TaskBatchMove(ProjectOps):
    """批量移动工作项"""
    uri = '/team/{team_uuid}/tasks/batch/move'
    name = '批量移动工作项'
    api_type = 'POST'


class TaskUpdate(ProjectOps):
    """更新工作项"""
    uri = '/team/{team_uuid}/task/{task_uuid}/update2'
    name = '更新工作项'
    api_type = 'POST'


class TaskUpdate3(ProjectOps):
    """更新工作项3"""
    uri = '/team/{team_uuid}/tasks/update3'
    name = '更新工作项3'
    api_type = 'POST'


class UpdateIssueType(ProjectOps):
    """"""
    uri = '/team/{team_uuid}/tasks/update_issuetype'
    name = '更新工作项类型'
    api_type = 'POST'


class TaskDelete(ProjectOps):
    """删除工作项"""
    uri = '/team/{team_uuid}/task/{task_uuid}/delete'
    name = '删除工作项'
    api_type = 'POST'


class TasksInfo(ProjectOps):
    """根据 UUID 批量获取工作项详情"""
    uri = '/team/{team_uuid}/tasks/info'
    name = '根据 UUID 批量获取工作项详情'
    api_type = 'POST'


class TaskInfo(ProjectOps):
    """根据 UUID 或者序号获取工作项详情"""
    uri = '/team/{team_uuid}/task/{task_uuid}/info'
    name = '获取工作项详情'
    api_type = 'GET'


class TaskCopy(ProjectOps):
    """复制工作项"""
    uri = '/team/{team_uuid}/task/{task_uuid}/copy'
    name = '复制工作项'
    api_type = 'POST'


class TaskBatchCopy(ProjectOps):
    """批量复制工作项"""
    uri = '/team/{team_uuid}/tasks/copy'
    name = '批量复制工作项'
    api_type = 'POST'


class TasksUpdateField(ProjectOps):
    """批量更新工作项属性"""
    uri = '/team/{team_uuid}/tasks/update_field_values'
    name = '批量更新工作项属性'
    api_type = 'POST'


class TaskStats(ProjectOps):
    """获取工作项统计数据接口"""
    uri = '/team/{team_uuid}/task_stats'
    name = '获取工作项统计数据'
    api_type = 'GET'


class TaskMessages(ProjectOps):
    """工作项动态"""
    uri = '/team/{team_uuid}/task/{task_uuid}/messages'
    name = '工作项动态'
    api_type = 'GET'


class TaskSendMessage(ProjectOps):
    """添加评论"""
    uri = '/team/{team_uuid}/task/{task_uuid}/send_message'
    name = '添加评论'
    api_type = 'POST'


class TaskMessageUpdate(ProjectOps):
    """工作项评论更新"""
    uri = '/team/{team_uuid}/task/{task_uuid}//message/{message_uuid}/update_discussion'
    name = '工作项评论更新'
    api_type = 'POST'


class TaskMessageDelete(ProjectOps):
    """工作项评论删除"""
    uri = '/team/{team_uuid}/task/{task_uuid}/message/{message_uuid}/delete'
    name = '工作项评论删除'
    api_type = 'POST'


class TaskAssessManHourUpdate(ProjectOps):
    """预估工时更新"""
    uri = '/team/{team_uuid}/task/{task_uuid}/assess_manhour/update'
    name = '预估工时更新'
    api_type = 'POST'


class TaskRemainingHourUpdate(ProjectOps):
    """剩余工时更新"""
    uri = '/team/{team_uuid}/task/{task_uuid}/remaining_hour/update'
    name = '剩余工时更新'
    api_type = 'POST'


class ResAttUpload(ProjectOps):
    """上传附件"""
    uri = '/team/{team_uuid}/res/attachments/upload'
    name = '上传附件'
    api_type = 'POST'


class LiteContextPermissionRules(ProjectOps):
    """显示工作项权限"""
    uri = '/team/{team_uuid}/lite_context_permission_rules'
    name = '显示工作项权限'
    api_type = 'POST'


class ChartAutoSchedule(ProjectOps):
    """自动排期"""
    uri = '/team/{team_uuid}/project/{project_uuid}/activity_chart/{chart_uuid}/auto_shedule'
    name = '自动排期'
    api_type = 'POST'


class QueueProgress(ProjectOps):
    """队列进度"""
    uri = '/team/{team_uuid}/queue/{queue_uuid}/progress'
    name = '队列进度'
    api_type = 'GET'


class QueueExtra(ProjectOps):
    uri = '/team/{team_uuid}/queue/{queue_uuid}/extra'
    name = '队列文件下载'
    api_type = 'POST'


class WatchersAdd(ProjectOps):
    """添加关注者"""
    uri = '/team/{team_uuid}/task/{task_uuid}/watchers/add'
    name = '添加关注者'
    api_type = 'POST'


class WatchersDelete(ProjectOps):
    """删除关注者"""
    uri = '/team/{team_uuid}/task/{task_uuid}/watchers/delete'
    name = '删除关注者'
    api_type = 'POST'


# -*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*-
# -*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*-

class TaskMergeDefect(ProjectOps):
    """工作项合并缺陷"""
    uri = '/team/{team_uuid}/task/{task_uuid}/merge_defect'
    name = '工作项合并缺陷'
    api_type = 'POST'


class TaskCreateDemand(ProjectOps):
    """工作项创建需求"""
    uri = '/team/{team_uuid}/task/{task_uuid}/create_demand'
    name = '工作项创建需求'
    api_type = 'POST'


# -*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*-
# -*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*-

class UpBox(ProjectOps):
    """上传附件UpBox"""

    uri = 'https://up.qbox.me'
    name = '上传附件'
    api_type = 'FORM-DATA'

    def _parse_uri(self, **kwargs):
        """"""
        return self.uri

    def call(self, json=None, url=None, **kwargs):
        """
        :param url:
        :param json:
        :param kwargs:
        :return:
        """

        print(f'Call at：{mocks.now_time()}')
        print(f'API name：[{self.name}] Type: [{self.api_type}]')
        print(f'Request Url: [{url}]')

        img = json.pop('img_name')

        print(f'Request data: {json}')

        mocks.create_new_image(RunVars.tmp_files, img)

        file = {
            'token': json['token'],
            'file': (f'{img}.png', open(f'{RunVars.tmp_files}/{img}.png', 'rb'), 'image/png'),

        }

        # gen multi data
        multi_data = MultipartEncoder(file, boundary='----WebKitFormBoundaryjQNEjXOM9W9Xq8Al')

        headers = {'Content-Type': multi_data.content_type}
        self.response = self.session.post(url, data=multi_data, headers=headers)

        print(f'Respones: {self.response.text}')


# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# 任务-测试情况

class TaskRelTestPlan(ProjectOps):
    uri = '/team/{team_uuid}/task/{task_uuid}/bind_testcase_plan'
    name = '任务关联测试计划'
    api_type = 'POST'


class TaskDelRelTestPlan(ProjectOps):
    uri = '/team/{team_uuid}/task/{task_uuid}/unbind_testcase_plan'
    name = '移除任务关联测试计划'
    api_type = 'POST'
