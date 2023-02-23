"""
@Desc：各工作项类型通用快捷调用方法
"""
import time

from falcons.check import go
from falcons.ops import generate_param

from main.actions.task import TaskAction
from main.api import issue as iss, project
from main.api import task
from main.api.issue import GetNoticeRules, DelNoticeRules, CreateIssueType, DeleteIssueType
from main.params import task as t, issue, data, com, conf
from main.params.const import ACCOUNT
from main.params.task import lite_context_permission_rules


class IssueAction:

    @classmethod
    def process_detail_and_close(cls, uuid, success_count: int, errors_affect=None, token=None):
        """
        进度管理器详情和关闭操作
        :param token
        :param uuid  处理后的工作项uuid
        :param success_count  成功条数
        :param errors_affect 错误信息
        """

        if TaskAction.wait_to_done(uuid):

            # 点击进度管理器的查看详情
            param = t.queue_progress()[0]
            param.uri_args({'queue_uuid': uuid})
            res = go(task.QueueProgress, param, token)

            res.check_response('successful_count', success_count)
            if errors_affect:
                res.check_response('errors_affect_count', errors_affect)

            # 关闭执行结果弹框
            # prm = t.close_progress()[0]
            # prm.json['uuids'].append(uuid)
            # go(prj.HiddenProgress, prm, token)

    @classmethod
    def task_param(cls, old_issue_type,
                   new_issue_type,
                   old_proj=ACCOUNT.project_uuid,
                   new_proj=ACCOUNT.project_uuid,
                   ):
        """移动工作项参数"""

        old_status_uuid, old_issue_uuid = TaskAction.get_task_status_and_issue_uid(old_issue_type, old_proj)
        time.sleep(1)
        new_status_uuid, new_issue_uuid = TaskAction.get_task_status_and_issue_uid(new_issue_type, new_proj)

        old_data = [old_status_uuid, old_issue_uuid]
        new_data = [new_status_uuid, new_issue_uuid]

        return {'old': old_data, 'new': new_data}

    @classmethod
    def need_sub_task(cls, parent_uuid,
                      old_proj,
                      new_proj,
                      sub_issue_type='子任务',
                      old_issue_type='任务',
                      new_issue_type='需求',
                      ):
        """
        移动工作项参数-需要子工作项
        :param parent_uuid  父工作项uuid
        :param old_proj  原项目uuid
        :param new_proj  新项目uuid
        :param sub_issue_type  子工作项类型uuid
        :param old_issue_type  原工作项类型uuid
        :param new_issue_type  新工作项类型uuid
        """

        tp = cls.task_param(old_issue_type, new_issue_type, old_proj, new_proj)

        # 新建子任务
        time.sleep(1)
        sub_uuid = TaskAction.new_issue(parent_uuid, sub_issue_type, proj_uuid=old_proj)

        sub_status_uuid, sub_issue_uuid = TaskAction.get_task_status_and_issue_uid(sub_issue_type, old_proj)
        related = {"uuid": parent_uuid, "sub_uuids": sub_uuid}

        param = t.batch_move_task([parent_uuid], tp['old'], tp['new'], old_proj)[0]
        param.json_update('rules[0].target_project_uuid', new_proj)
        param.json['tasks_related'].append(related)
        param.json['rules'].append({
            "source_project_uuid": old_proj,
            "target_project_uuid": new_proj,
            "source_issue_type_uuid": tp['old'][1],
            "target_issue_type_uuid": tp['new'][1],
            "source_status_uuid": sub_status_uuid,
            "target_status_uuid": sub_status_uuid,
            "source_sub_issue_type_uuid": sub_issue_uuid,
            "target_sub_issue_type_uuid": sub_issue_uuid
        })

        return param

    @classmethod
    def get_issue_notice_rule(cls, issue_name='任务', token=None):
        """
        获取工作项的工作项提醒列表
        :param issue_name: 工作项名称
        :param token:
        :return: 请求接口结果
        """
        issue_type_uuid = TaskAction.issue_type_uuid(issue_name, token=token)[0]

        param = issue.notice_rules()[0]
        param.uri_args({'issue_type_uuid': issue_type_uuid})
        resp = go(GetNoticeRules, param, token)
        return resp

    @classmethod
    def del_notice_rule(cls, issue_type_uuid, notice_rule_uuid, token=None):
        """
        删除工作项提醒
        issue_type_uuid：工作项uuid
        notice_rule_uuid：工作项提醒uuid
        """
        param = issue.notice_rules()[0]
        param.uri_args({'issue_type_uuid': issue_type_uuid})
        param.uri_args({'notice_rule_uuid': notice_rule_uuid})
        resp = go(DelNoticeRules, param, token)
        resp.check_response('code', 200)

    @classmethod
    def get_notice_config(cls, issue_type_uuid):
        """
        获取工作项通知列表
        :param issue_type_uuid:
        :return: 请求接口返回结果
        """
        param = issue.notice_rules()[0]
        param.uri_args({'issue_type_uuid': issue_type_uuid})
        resp = go(iss.GetNoticeConfig, param)
        return resp

    @classmethod
    def del_issue_permission(cls, permission_rule_uuid):
        """
        删除工作项 权限域
        :param permission_rule_uuid: 权限域UUID
        :return: 请求结果
        """
        param = issue.notice_rules()[0]
        param.uri_args({'permission_rule_uuid': permission_rule_uuid})
        return go(iss.DelIssuePermission, param)

    @classmethod
    def add_issue_permission(cls, param_dict: dict, project_uuid=ACCOUNT.project_uuid):
        """
        新增工作项权限
        :param param_dict: 字典形式 ={
            issue_type_uuid 工作类型uuid
            permission：权限
            user_domain_param ：成员域参数
            user_domain_type：成员域类型
        }
        :param project_uuid: 项目UUID
        :return: 权限域UUID
        """
        param = issue.add_issue_permission()[0]
        param.json_update('permission_rule.permission', param_dict['permission'])
        param.json_update('permission_rule.user_domain_type', param_dict['user_domain_type'])
        param.json_update('permission_rule.user_domain_param', param_dict['user_domain_param'])
        param.json_update('permission_rule.context_param.issue_type_uuid', param_dict['issue_type_uuid'])
        param.json_update('permission_rule.context_param.project_uuid', project_uuid)
        resp = go(project.PermissionAdd, param)
        resp.check_response('permission_rule.permission', param_dict['permission'])
        return resp.value('permission_rule.uuid')

    @classmethod
    def get_pro_permission_rules(cls, issue_name, project_uuid=ACCOUNT.project_uuid):
        """
        获取项目内工作项权限
        :param issue_name:组件名称 需求 任务 子需求 子任务 缺陷 等
        :param project_uuid: 项目UUID
        :return:
        """
        issue_type_uuid = TaskAction.issue_type_uuid(issue_name, project_uuid=project_uuid)[0]
        param = lite_context_permission_rules()[0]
        param.json_update('context_type', 'issue_type')
        param.json_update('context_param.issue_type_uuid', issue_type_uuid)
        param.json_update('context_param.project_uuid', project_uuid)
        resp = go(task.LiteContextPermissionRules, param)
        return resp

    @classmethod
    def global_add_post_action(cls, post_function: list, issue_type_uuid, transition_uuid):
        """
        配置中心-新增工作项-工作流-后置动作
        :param post_function: 对应后置动作post_function参数
        :param issue_type_uuid: 工作项UUID
        :param transition_uuid: 工作项中工作流步骤UUID
        :return:
        """
        param = issue.global_post_action()[0]

        param.json_update('transition.post_function', post_function)
        param.uri_args(
            {'issue_type_uuid': issue_type_uuid,
             'transition_uuid': transition_uuid})
        resp = go(iss.GlobalPostActionUpdate, param)
        resp.check_response('uuid', issue_type_uuid)

    @classmethod
    def global_add_field(cls, field_type, issue_type: list):
        """
        新增工作项属性 并将新增属性添加到对应工作项
        :param field_type: 工作属性field_type
        :param issue_type: 工作项UUID
        :return:field_uuid
        """
        param = conf.add_issue_type_field()[0]
        param.json_update('field.type', field_type)
        res = go(project.FieldsAdd, param)
        field_uuid = res.value('field.uuid')

        param = issue.add_task_field([field_uuid], '')[0]
        param.json_update('project_issue_types', [])
        param.json_update('team_issue_types', issue_type)
        go(project.AddTaskField, param)
        return field_uuid

    @classmethod
    def add_field_into_issue(cls, field_type: list, issue_type: list):
        """
        将新增属性添加到对应工作项
        :param field_type: 工作属性field_type
        :param issue_type: 工作项UUID
        :return:
        """
        param = issue.add_task_field(field_type, '')[0]
        param.json_update('project_issue_types', [])
        param.json_update('team_issue_types', issue_type)
        go(project.AddTaskField, param)

    @classmethod
    def del_issue_field(cls, issue_type, field_uuid):
        """
        删除工作项属性-配置中心
        :param issue_type: 工作项uuid
        :param field_uuid: 工作项属性uuid
        :return: 无
        """
        pr = issue.delete_issue()[0]
        pr.uri_args({'issue_uuid': issue_type})
        pr.uri_args({'field_uuid': field_uuid})
        go(iss.IssueFieldDelete, pr)

    @classmethod
    def del_field(cls, field_uuid):
        """
        全局属性删除
        :param field_uuid:属性uuid
        :return:
        """
        p = data.field_delete()[0]
        p.uri_args({'field_uuid': field_uuid})
        go(project.FieldDelete, p)

    @classmethod
    def global_fields(self):
        '''
        全局-工作项属性列表
        :return:
        '''
        p = com.gen_stamp({'field': 0})
        r = go(project.TeamStampData, p)
        return r.value('field.fields')

    @classmethod
    def get_field(self, field_uuid=None, field_name=None, is_build_in=True):
        '''
        获取工作项属性信息
        :param field_uuid: 属性uuid
        :param field_name: 属性名称
        :param is_build_in: 是否系统内置属性
        :return:
        '''
        p = com.gen_stamp({'field': 0})
        r = go(project.TeamStampData, p)
        fields = r.value('field.fields')
        if field_uuid:
            return [f for f in fields if f['uuid'] == field_uuid and f['built_in'] == is_build_in][0]
        elif field_name:
            return [f for f in fields if f['name'] == field_name and f['built_in'] == is_build_in][0]


class IssueTypeAction:
    @classmethod
    def create_issue_type(cls, typ=1, icon=1):
        '''
        全局配置-添加工作项类型
        :param typ: 类型x（1：标准工作项，2：子工作项）
        :param icon: 图标 默认1：1～15）
        :return:
        '''
        param = issue.issue_type_create()[0]
        res = go(CreateIssueType, param)
        return res

    @classmethod
    def delete_issue_type(cls, issue_type_uuid):
        '''
        全局配置-删除工作项类型
        :param issue_type_uuid:
        :return:
        '''
        param = generate_param({})[0]
        param.uri_args({'issue_type_uuid': issue_type_uuid})
        res = go(DeleteIssueType, param)
        return res

    @classmethod
    def get_issue_types(cls):
        '''
        全局配置-获取所有工作项类型
        :return:
        '''
        ts_param = com.gen_stamp({"issue_type": 0})
        res = go(project.TeamStampData, ts_param).json()
        return res['issue_type']['issue_types']
