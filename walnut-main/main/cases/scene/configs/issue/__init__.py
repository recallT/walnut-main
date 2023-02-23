from falcons.check import go
from main.actions.task import team_stamp
from main.api import project as prj, issue
from main.params import conf, issue as ise, devops


class IssueConfig:

    @classmethod
    def global_issue_type(cls, issue_type, token=None):
        """获取全局工作项类型uuid"""

        resp = team_stamp({"issue_type": 0}, token)
        issue_uuid = [n['uuid'] for n in resp['issue_type']['issue_types'] if n['name'] == issue_type]

        return issue_uuid[0]

    @classmethod
    def issue_field_add(cls, field_type: int, token=None, **kwargs):
        """添加工作项属性"""

        param = conf.add_issue_type_field()[0]
        param.json_update('field.type', field_type)
        if kwargs:
            for key, value in kwargs.items():
                param.json['field'] |= {key: value}

        res = go(prj.FieldsAdd, param, token)
        res.check_response('field.built_in', False)

        return res.value('field.uuid')

    @classmethod
    def global_issue_add(cls, token=None):
        """添加全局标准工作项"""

        param = ise.add_standard_issue()[0]
        resp = go(issue.IssuesAdd, param, token)

        return resp.value('name'), resp.value('uuid')

    @classmethod
    def global_sub_issue_add(cls, token=None):
        """添加全局子工作项"""

        param = ise.add_sub_issue()[0]
        resp = go(issue.IssuesAdd, param, token)

        return resp.value('name'), resp.value('uuid')

    @classmethod
    def global_issue_delete(cls, issue_uuid, token=None):
        """删除全局工作项"""

        prm = ise.delete_issue()[0]
        prm.uri_args({'issue_uuid': issue_uuid})
        go(issue.IssueDelete, prm, token)

    @classmethod
    def global_issue_add_field(cls, field_uuid, issue_type='任务', token=None):
        """全局工作项添加属性"""

        issue_type_uuid = cls.global_issue_type(issue_type)

        prm = ise.add_issue_field()[0]
        prm.json_update('field_config.field_uuid', field_uuid)
        prm.uri_args({'issue_uuid': issue_type_uuid})

        return go(issue.IssueFieldAdd, prm, token)

    @classmethod
    def issue_permission_add(cls, issue_type,
                             user_domain_type,
                             permission="update_task_watchers",
                             user_domain_param="",
                             token=None):
        """
        添加全局工作项权限
        :param token
        :param issue_type
        :param user_domain_type
        :param permission
        :param user_domain_param
        :return rule_uuid
        """

        param = conf.global_issue_perm(user_domain_type, permission, user_domain_param)[0]
        param.uri_args({'issue_uuid': issue_type})
        resp = go(issue.PermissionRulesAdd, param, token)

        perm_uuid = [p['uuid'] for p in resp.value('default_configs.default_permission') if
                     p['permission'] == permission and p['user_domain_param'] == user_domain_param]

        return perm_uuid[0]

    @classmethod
    def issue_permission_del(cls, issue_type_uuid, rule_uuid, token=None):
        """删除全局工作项权限"""

        param = devops.permission_delete()[0]
        param.uri_args({'issue_uuid': issue_type_uuid})
        param.uri_args({'rule_uuid': rule_uuid})

        return go(issue.PermissionRulesDelete, param, token)
