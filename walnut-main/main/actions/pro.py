"""
@File    ：pro.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/16
@Desc    ：项目接口相关操作
"""
import json
from falcons.check import go
from falcons.ops import generate_param

from main.actions.task import TaskAction
from main.api import project as api
from main.api.task import TaskAdd
from main.helper.extra import retry
from main.params import proj, conf, devops, more, com
from main.params.const import ACCOUNT


class PrjAction:
    """项目接口相关操作"""

    @classmethod
    @retry
    def new_project(cls, index=0, name=None, owner_uuid=None, token=None) -> str:
        """创建项目"""
        p = proj.add_project(name=name, owner_uuid=owner_uuid)[index]
        res = go(api.AddProject, p, token=token)

        return res.value('project.uuid')

    @classmethod
    def work_hour_configs_update(cls, t, token=None):
        """
        工时模式切换
        :param token:
        :param t: 模式
        :return:
        """
        p = proj.w_config_update(t)[0]

        go(api.TeamConfigsUpdate, p, token=token)

    @classmethod
    def project_stamp_data(cls, project_uuid=ACCOUNT.project_uuid, token=None):
        """项目配置数据"""
        param = proj.proj_stamp()[0]
        param.uri_args({'project_uuid': project_uuid})
        res = go(api.ProjectStamp, param, token, is_print=False)
        return res

    @classmethod
    def add_prj_plan_component(cls, token=None):
        """添加项目计划组件"""

        component_stamp = go(api.ProjectStamp, proj.proj_stamp()[0], token, is_print=False)
        j = component_stamp.json()

        exist_components = [{'uuid': c['uuid'], 'template_uuid': c['template_uuid']}
                            for c in j['component']['components']]

        com00014_ = [e for e in exist_components if e['template_uuid'] == 'com00014']
        if not com00014_:
            params = proj.add_prj_plan_component()[0]
            params.json['components'] += exist_components  # 添加上原有组件
            return go(api.ComponentsAdd, params, token)

        return None

    @classmethod
    def add_component(cls, component_name: str, project_uuid: str = None, token=None, repeat=False, parent_uuid=''):
        """
        添加组件到项目中, 组件的默认配置
        :param token:
        :param component_name: 组件中文名称 如 项目计划、文件 等等 参考项目配置-项目组件侧边栏系统组件列表
        :param project_uuid: 项目名称
        :param repeat：是否添加重复组件
        :param parent_uuid：一级导航的uuid
        :return:
        """
        # 获取组件模版信息
        comp_template = go(api.TeamStampData, proj.component_template_stamp()[0], token)
        template_json = comp_template.value('component_template.templates')

        template_mapper = {t['name']: t['uuid'] for t in template_json}

        pid = project_uuid if project_uuid else ACCOUNT.project_uuid
        # 获取已有的组件UUID
        param_cp = proj.proj_stamp()[0]
        param_cp.uri_args({'project_uuid': pid})

        component_stamp = go(api.ProjectStamp, param_cp, token, is_print=False)
        components = component_stamp.value('component.components')

        exist_components = [{'uuid': c['uuid'], 'template_uuid': c['template_uuid']}
                            for c in components]
        is_exist = [e for e in exist_components if e['template_uuid'] == template_mapper[component_name]]

        if not is_exist or repeat:
            c_template = [t for t in template_json if t['name'] == component_name][0]
            params = proj.add_prj_component(c_template)[0]

            # 这里可以指定到项目
            params.json_update('components[0].project_uuid', pid)
            params.json_update('components[0].parent_uuid', parent_uuid)  # 添加上 一级导航的uuid
            params.uri_args({'project_uuid': pid})
            params.json['components'] += exist_components  # 添加上原有组件

            return go(api.ComponentsAdd, params, token, is_print=False)

    @classmethod
    def get_component(cls, component_name: str, project_uuid: str = None, token=None):
        '''
        获取组件信息
        :param component_name:
        :param project_uuid:
        :param token:
        :return:
        '''
        param = com.generate_param({
            "component": 0
        }, is_project=True)[0]
        if project_uuid:
            param.uri_args({'project_uuid': project_uuid})
        res = go(api.ProjectStamp, param, is_print=False, token=token)
        components = res.value('component.components')
        cc = [c for c in components if c['name'] == component_name]
        if cc:
            return cc[0]
        else:
            raise ValueError(f'组件不存在, project_uuid:{project_uuid}, component_name:{component_name}')

    @classmethod
    def remove_prj_component(cls, component_name: str, project_uuid=None, token=None):
        """
        移除项目组件
        :param token:
        :param component_name: 组件名称
        :param project_uuid:  项目名称
        :return:
        """

        pid = project_uuid if project_uuid else ACCOUNT.project_uuid

        component_stamp = cls.project_stamp_data(project_uuid=pid)
        components = component_stamp.value('component.components')

        # 获取组件UUID
        keeping = [{'uuid': c['uuid']} for c in components if c['name'] != component_name]

        # 获取需要移除的组件UUID
        removing = [c['uuid'] for c in components if c['name'] == component_name]

        if removing:
            params = proj.remove_plan_component()[0]

            params.json['components'] += keeping  # 保留其他组件
            params.uri_args({'comp_uuid': removing[0]})
            params.uri_args({'project_uuid': pid})

            return go(api.ComponentDelete, params, token)

    @classmethod
    def remove_prj_component_by_uuid(cls, component_uuid: str, project_uuid=None, token=None):
        """
        通过uuid移除项目组件
        :param token:
        :param component_uuid: 组件uuid
        :param project_uuid:  项目uuid
        :return:
        """

        pid = project_uuid if project_uuid else ACCOUNT.project_uuid

        component_stamp = cls.project_stamp_data(project_uuid=pid)
        components = component_stamp.value('component.components')

        # 获取组件UUID
        keeping = [{'uuid': c['uuid']} for c in components if c['uuid'] != component_uuid]

        params = proj.remove_plan_component()[0]

        params.json['components'] += keeping  # 保留其他组件
        params.uri_args({'comp_uuid': component_uuid})
        params.uri_args({'project_uuid': pid})

        return go(api.ComponentDelete, params, token)

    @classmethod
    def remove_prj_plan_component(cls, token=None):
        """
        移除项目计划组件
        避免 清理测试数据时项 Item 删除失败，需要先移除项目计划组件
        :param token:
        :return:
        """

        component_stamp = go(api.ProjectStamp, proj.proj_stamp()[0], token, is_print=False)
        j = component_stamp.json()

        # 获取所有组件UUID，template_uuid
        exist_components = {c['uuid']: c['template_uuid']
                            for c in j['component']['components']}

        # 项目计划UUID
        plan_uuid = [u for u, t in exist_components.items() if t == 'com00014']
        keeping = []
        for k, v in exist_components.items():
            if v != 'com00014':
                keeping.append({'uuid': k})
        params = proj.remove_plan_component()[0]
        params.json['components'] += keeping  # 保留组件
        params.uri_args({'comp_uuid': plan_uuid})
        return go(api.ComponentDelete, params, token)

    @classmethod
    def add_task_component(cls, is_param=False, project_uuid=ACCOUNT.project_uuid, token=None):
        view, objects, isu_type_uuid = PrjAction.get_project_isu_list(template_name='任务')

        component_stamp = cls.project_stamp_data(project_uuid=project_uuid)
        exist_components = [{'uuid': c['uuid'], 'template_uuid': c['template_uuid']}
                            for c in component_stamp.value('component.components')]

        params = proj.add_task_component()[0]
        params.uri_args({'project_uuid': project_uuid})
        params.json_update('components[0].project_uuid', project_uuid)
        params.json_update('components[0].views', view)
        params.json_update('components[0].objects', objects)
        if is_param:
            return params
        params.json['components'] += exist_components  # 添加上原有组件
        return go(api.ComponentsAdd, params, token)

    @classmethod
    def add_customize_component(cls, is_param=False, token=None, project_uuid=ACCOUNT.project_uuid):
        """
        新增自定义链接组件
        is_param：是否只返回参数
        """
        # component_stamp = go(api.ProjectStamp, proj.proj_stamp()[0], token)
        component_stamp = cls.project_stamp_data(project_uuid=project_uuid)
        exist_components = [{'uuid': c['uuid'], 'template_uuid': c['template_uuid']}
                            for c in component_stamp.value('component.components')]

        params = proj.add_customize_component()[0]
        if is_param:
            return params, exist_components
        params.json['components'] += exist_components  # 添加上原有组件
        return go(api.ComponentsAdd, params, token)

    @classmethod
    def get_project_isu_list(cls, template_name='发布', token=None):
        """
        项目-获取组件的配置（视图、objects、工作项uuid）
        :param template_name: 组件名称 发布 任务  需求 缺陷等
        :param token:
        :return:
        """
        template_obj = go(api.TeamStampData, conf.project_isu_template()[0], token)
        template_json = template_obj.json()

        # 定义先
        view, objects, issue_type_uuid = '', '', ''
        for obj in template_json['component_template']['templates']:
            if obj['name'] == template_name:
                view = obj['default_views']
                objects = obj['objects']

        for issue_type in template_json['issue_type']['issue_types']:
            if issue_type['name'] == template_name:
                issue_type_uuid = issue_type['uuid']

        return view, objects, issue_type_uuid

    @classmethod
    def add_deploy_task(cls, token=None):
        """
        添加发布任务
        :param token:
        :return: 发布任务UUID
        """
        isu_type_uuid = TaskAction.issue_type_uuid(issue_types='发布')[0]
        param = proj.add_deploy_tasks(isu_type_uuid)[0]
        t = TaskAdd(token)
        # 调用接口
        t.call(param.json, **param.extra)
        # 检查接口响应码
        t.check_response('tasks[0].status', 1)
        return t.json()['tasks'][0]['uuid']

    @classmethod
    def get_task_transitions(cls, task_uuid, token=None):
        """
        获取task的流转UUID
        :param task_uuid: 工作项uuid 任务uuid
        :param token:
        :return: 接口结果resp
        """
        param = proj.proj_url()[0]
        param.uri_args({'tasks_uuid': task_uuid})
        resp = go(api.GetDeployStatus, param, token)
        return resp

    @classmethod
    def del_isu_task(cls, tasks_uuid, token=None):
        """
        "删除项目内各个组件的工作项：需求 子需求 任务 子任务等
        :param tasks_uuid: 对应任务UUID
        :param token:
        :return:接口结果
        """
        param = proj.proj_url()[0]
        param.uri_args({'tasks_uuid': tasks_uuid})
        resp = go(api.DeleteIsuTask, param, token)
        resp.check_response('code', 200)
        return resp

    @classmethod
    def get_deploy_relation_list(cls, keyword, issue_type_uuid, token=None):
        """
        关联发布下拉列表查询
        :param keyword: 查询关键字
        :param issue_type_uuid: 工作项UUID 如：任务 需求 发布 子任务等工作项UUID
        :param token:
        :return:resp
        """
        pam = proj.select_deploy_relation_info(keyword, issue_type_uuid)[0]
        resp = go(api.ItemGraphql, pam, token)
        return resp

    @classmethod
    def delete_project(cls, p_uuid):
        """
        删除测试项目
        :param p_uuid: 项目UUID
        :return:
        """
        del_param = proj.proj_delete()[0]
        del_param.uri_args({'project_uuid': p_uuid})
        return go(api.DeleteProject, del_param)

    @classmethod
    def get_all_projects(cls, token=None):
        p = com.gen_stamp({
            "all_project": 0
        })

        res = go(api.TeamStampData, p, is_print=False, token=token)
        return res.value('all_project.projects')

    @classmethod
    def proj_report_list(cls, report_type_name, report_name, token=None):
        """
        获取项目内报告列表
        report_type_name：报告分类名称：需求分析，缺陷分析，任务分析，工时分析，发布分析
        report_name：分组下的报告名称
        """
        parm = more.get_proj_report()[0]
        resp = go(api.ItemGraphql, parm, token)
        resp_report = [report for report in resp.value('data.projectReports') if
                       report['reportCategory']['name'] == report_type_name and report['name'] == report_name][0]
        report_uuid = resp_report['uuid']
        report_type = resp_report['reportType']
        dimensions = json.loads(resp_report['config'])['dimensions']
        return report_uuid, report_type, dimensions

    @classmethod
    def add_report_group(cls, project_uuid=ACCOUNT.project_uuid):
        """
        添加报表分组
        :return:
        """
        param = more.proj_report_add_group(project_uuid)[0]
        res = go(api.ItemGraphql, param)
        return res.value('data.addReportCategory.key')

    @classmethod
    def get_report_groups(cls, project_uuid=None):
        """获取报表分组列表"""
        list_param = more.proj_report_categories(project_uuid)[0]
        list_res = go(api.ItemGraphql, list_param)
        groups = list_res.value('data.reportCategories')
        return groups

    @classmethod
    def add_report(cls, group_key: str, typ: str = None, project_uuid=ACCOUNT.project_uuid):
        """
        添加报表
        :param project_uuid:
        :param group_key:
        :param typ: 报表类型，在param：more.add_proj_report中获取
        :return:
        """
        group_uuid = group_key.split('report_category-')[1]
        typ = typ if typ else 'task_distribution'
        add_report_param = more.add_proj_report(typ, category=group_uuid, pid=project_uuid)[0]
        res = go(api.ItemGraphql, add_report_param)
        return res.value('data.addProjectReport.key')

    @classmethod
    def get_reports_groups(cls, project_uuid=ACCOUNT.project_uuid):
        """
        获取报表分组列表和报表列表
        :return:
        """
        param = more.reports_and_groups(project_uuid)[0]
        res = go(api.ItemGraphql, param)
        return {
            'reports': res.value('data.projectReports'),
            'groups': res.value('data.reportCategories')
        }

    @classmethod
    def get_severity_level(cls, token=None):
        """
        配置中心-严重程度等级（系统）
        :param token:
        :return:
        """
        param = com.gen_stamp({"field": 0})
        fields = go(api.TeamStampData, param).json()['field']['fields']
        field_severity = [f for f in fields if f['name'] == '严重程度' and f['built_in']]
        severity_options = field_severity[0]['options']
        return severity_options

    @classmethod
    def update_prj_assign(cls, pid, uid, token=None):
        """修改项目负责人"""
        param = proj.update_prj_assign(uid)[0]
        param.uri_args({'project_uuid': pid})
        return go(api.UpdateProject, param, token=token)


class ProjPermissionAction:

    @classmethod
    def add_permission(cls, user_domain_type, permission="browse_project", user_domain_param="", token=None,
                       project_uuid=ACCOUNT.project_uuid):
        """添加权限"""

        param = conf.proj_permission(user_domain_type, permission, user_domain_param)[0]
        param.json_update('permission_rule.context_param.project_uuid', project_uuid)
        resp = go(api.PermissionAdd, param, token)

        resp.check_response('permission_rule.user_domain_type', user_domain_type)

        rule_uuid = resp.value('permission_rule.uuid')

        return rule_uuid

    @classmethod
    def del_permission(cls, rule_uuid, token=None):
        """删除权限"""

        param = devops.permission_delete()[0]
        param.uri_args({'rule_uuid': rule_uuid})

        return go(api.PermissionDelete, param, token)


class TeamPermissionAction:
    @classmethod
    def add_permission(cls, user_domain_param, user_domain_type=None, permission=None, token=None):
        """
        添加团队权限
        :param user_domain_param:
        :param user_domain_type:
        :param permission:
        :param token:
        :return:
        """
        param = conf.team_permission(user_domain_param, user_domain_type, permission)[0]
        r = go(api.PermissionAdd, param, token)
        r.check_response('permission_rule.user_domain_type', user_domain_type)
        return r.value('permission_rule.uuid')


class AgileKanbanAction:
    """敏捷看板管理"""

    def _get_component(cls, project_uuid):
        """
        获取项目组件
        """
        _component_stamp = PrjAction.project_stamp_data(project_uuid)
        return _component_stamp.value('component.components')

    @classmethod
    def _get_sprint_component(cls, project_uuid):
        """
        获取项目的迭代组件配置
        """
        component_stamp = PrjAction.project_stamp_data(project_uuid=project_uuid)
        components = component_stamp.value('component.components')
        _sprint_component = [c for c in components if c['template_uuid'] == 'com00007'][0]
        return _sprint_component, components

    @classmethod
    def get_kb_setting_by_id(cls, uuid, project_uuid=ACCOUNT.project_uuid) -> (dict, dict, [dict]):
        """查看看板配置信息"""
        s_component, components = cls._get_sprint_component(project_uuid)
        kanban_settings = s_component['kanban_settings']
        if kanban_settings:
            return [kb for kb in kanban_settings if kb['uuid'] == uuid][0], s_component, components

    @classmethod
    def get_ituuid_by_itname(cls, names: [str], it_configs: [dict]) -> [str]:
        """根据issue类型名称获取issue类型的uuid"""
        val = []
        for n in names:
            for i in it_configs:
                if i['name'] == n:
                    val.append(i['issue_type_uuid'])
                    break
        return val

    @classmethod
    def _config_lane_condition(cls, field_name, operate, field_value, it_configs):
        """泳道条件配置-单条：根据文字描述转换，和UI文字一致"""
        _operate_map = {
            "包含": {
                "label": "filter.addQueryContent.include",
                "operate_id": "include",
                "predicate": "in",
                "negative": False
            },
            "不包含": {
                "label": "filter.addQueryContent.exclude",
                "operate_id": "exclude",
                "negative": True,
                "predicate": "in"
            },
            "为空": {
                "label": "filter.addQueryContent.is",
                "operate_id": "equalEmpty",
                "predicate": "empty"
            },
            "不为空": {
                "label": "filter.addQueryContent.unEqualEmpty",
                "operate_id": "unEqualEmpty",
                "negative": True,
                "predicate": "empty"
            },
        }
        val = None
        if field_name != '工作项类型':
            pass
        else:
            val = cls.get_ituuid_by_itname(field_value, it_configs)

        _field_map = {
            "工作项类型": {
                "field_uuid": "field024",
                "field_type": 11  # 属性类型为issue_type
            }
        }

        return {
            "field_uuid": _field_map[field_name]["field_uuid"],
            "operate": _operate_map[operate],
            "value": val,
            "field_type": _field_map[field_name]["field_type"]
        }

    @classmethod
    def _add_default_board(cls, issue_names: [str], it_configs, ts_configs) -> [dict]:
        """模版：默认看板栏配置"""
        ituuids = cls.get_ituuid_by_itname(issue_names, it_configs)
        # print('task id: ', ituuids)
        status_uuids = [ts['status_uuid'] for ts in ts_configs if ts['issue_type_scope_uuid'] in ituuids]
        b_settings = []
        for s in status_uuids:
            b_dict = proj.new_kb_board_settings([s])
            b_settings.append(
                b_dict
            )
        return b_settings

    @classmethod
    def update_kanban(cls, uuid, name=None, project_uuid=ACCOUNT.project_uuid):
        """
        更新敏捷看板配置
        :param uuid:
        :param name:
        :param project_uuid:
        :return:
        """
        kb, s_component, components = cls.get_kb_setting_by_id(uuid, project_uuid)
        kanban_settings = s_component['kanban_settings']
        if name:
            kb['name'] = name
        # if condition_groups:
        #     kb['conditions']['condition_groups'] = condition_groups
        for index, v in enumerate(kanban_settings):
            if v['uuid'] == kb['uuid']:
                kanban_settings[index] = kb
                # break
        no_update_components = [{'uuid': c['uuid'], 'template_uuid': c['template_uuid']}
                                for c in components if c['uuid'] != s_component['uuid']]
        params = proj.update_prj_component(s_component)[0]
        params.json_update('components[0].permissions', [
            {
                "permission": "view_component",
                "user_domains": [
                    {
                        "user_domain_type": "everyone",
                        "user_domain_param": ""
                    },
                    {
                        "user_domain_type": "project_administrators",
                        "user_domain_param": ""
                    }
                ]
            }
        ])
        params.json_update('components[0].update_ext_settings', False)
        params.json_update('components[0].kanban_settings', kanban_settings)
        # params.json_update('components[0].views', [])
        params.json['components'] += no_update_components
        params.uri_args({'project_uuid': project_uuid})
        return go(api.UpdateComponents, params).json()['components']

    @classmethod
    def update_kanban_list(cls, project_uuid=ACCOUNT.project_uuid, kanbans: [dict] = [],
                           is_append=True, token=None):
        """
        更新敏捷看板列表
        """
        components, sprint_component = cls._get_sprint_component(project_uuid)
        # 项目没有迭代组件时, 添加迭代组件
        if not sprint_component:
            PrjAction.add_component('迭代', project_uuid=project_uuid)
        sprint_component, components = cls._get_sprint_component(project_uuid)
        components.remove(sprint_component)
        no_update_components = [{'uuid': c['uuid'], 'template_uuid': c['template_uuid']}
                                for c in components if c['uuid'] != sprint_component['uuid']]
        params = proj.update_prj_component(sprint_component)[0]
        params.json_update('components[0].permissions', [
            {
                "permission": "view_component",
                "user_domains": [
                    {
                        "user_domain_type": "everyone",
                        "user_domain_param": ""
                    },
                    {
                        "user_domain_type": "project_administrators",
                        "user_domain_param": ""
                    }
                ]
            }
        ])
        params.json_update('components[0].update_ext_settings', False)
        # params.json_update('components[0].views', [])
        kanban_settings = sprint_component[
            'kanban_settings'] if 'kanban_settings' in sprint_component.keys() else []
        kanban_settings = kanbans if not is_append else kanban_settings + kanbans
        params.json['components'][0]['kanban_settings'] = kanban_settings
        # params.json_update('components[0].kanban_settings',
        #                    kanbans if not is_append else sprint_component['kanban_settings'] + kanbans)
        params.json['components'] += no_update_components
        params.uri_args({'project_uuid': project_uuid})
        return go(api.UpdateComponents, params, token)

    @classmethod
    def add_kanban(cls, project_uuid=ACCOUNT.project_uuid,
                   lane_type: int = 1,
                   lane_conditions_groups: [[dict]] = [[{
                       "field_name": "工作项类型",
                       "operate": "包含",
                       "value": ["需求"]
                   }]],
                   kanban_issue_types: [str] = ["子需求", "子任务"],
                   is_parma: bool = False,
                   token=None):
        """添加看板：泳道条件「工作项类型」"""
        # 获取项目的工作类型配置
        ps_param = proj.proj_stamp()[0]
        ps_param.json = {"issue_type_config": 0,
                         "task_status_config": 0,
                         "component": 0}
        ps_param.uri_args({'project_uuid': project_uuid})
        ps_config = go(api.ProjectStamp, ps_param, token, is_print=False).json()
        it_configs = ps_config['issue_type_config']['issue_type_configs']
        ts_configs = ps_config['task_status_config']['task_status_configs']

        # condition_groups = [[cls._config_lane_condition(c['field_name'], c['operate'], c['value'],
        #                                                 it_configs) for c in
        #                      lcg] for lcg
        #                     in lane_conditions_groups]
        condition_groups = []
        issue_type_names = []
        for lcg in lane_conditions_groups:
            lcg_group = []
            for c in lcg:
                c_config = cls._config_lane_condition(c['field_name'], c['operate'], c['value'],
                                                      it_configs)
                lcg_group.append(c_config)
                if isinstance(c['value'], list) and c['operate'] == '包含':
                    issue_type_names += c['value']
            condition_groups.append(lcg_group)

        kb_param = proj.new_agile_kanban(project_uuid)
        kb_param['lane_type'] = lane_type
        kb_param['conditions']['condition_groups'] = condition_groups
        kb_param['issue_type_uuids'] = cls.get_ituuid_by_itname(kanban_issue_types, it_configs)
        kb_param['board_settings'] = cls._add_default_board(kanban_issue_types, it_configs, ts_configs)
        if is_parma:
            return kb_param
        # 生成敏捷看板-配置数据
        # kanbans = [].append(kb_param)
        if is_parma:
            return kb_param

        # 更新项目的迭代组件，添加新看板
        cls.update_kanban_list(project_uuid=project_uuid, kanbans=[kb_param], is_append=True)
        return kb_param['uuid'], cls.get_ituuid_by_itname(issue_type_names, it_configs)

    @classmethod
    def lane_filter_tasks(self, kanban_uuid, sprint_uuid, status_uuid, issue_type_uuids: [str],
                          project_uuid=ACCOUNT.project_uuid):
        """泳道筛选任务"""
        parmas = proj.param_kanban_filter(project_uuid, issue_type_uuids, sprint_uuid)[0]
        res = go(api.ItemGraphql, parmas)

        return res


class PrjSettingAction:
    """项目设置"""

    @classmethod
    def add_issue_type(cls, issue_type_uuid, project_uuid=ACCOUNT.project_uuid):
        """
        项目设置-添加工作项类型
        :param issue_type_uuid:
        :param project_uuid:
        :return:
        """
        param = proj.issue_type_add(issue_type_uuid)[0]
        param.uri_args({'project_uuid': project_uuid})
        return go(api.AddIssueType, param)

    @classmethod
    def del_issue_type(cls, issue_type_uuid, project_uuid=ACCOUNT.project_uuid):
        """项目设置-删除工作项类型"""
        param = generate_param()[0]
        param.uri_args({"project_uuid": project_uuid, "issue_type_uuid": issue_type_uuid})
        res = go(api.DeleteIssueType, param)
        return res

    @classmethod
    def add_issue_type_by_name(cls, type_name, project_uuid=ACCOUNT.project_uuid, is_build_in=True):
        """
        项目设置-工作项类型-添加：通过名称添加
        :param type_name:
        :param project_uuid:
        :param is_build_in: 是否内置的工作项类型
        :return:
        """
        p = proj.proj_stamp()[0]
        p.uri_args({"project_uuid": project_uuid})
        res = go(api.ProjectStamp, p, is_print=False).json()
        issue_types = res['issue_type_config']['issue_type_configs']
        if type_name not in [i['name'] for i in issue_types]:
            # 当项目里没有工作项类型时，从全局配置中查找并添加
            param = com.gen_stamp({'issue_type': 0})
            issue_types_global = go(api.TeamStampData, param).value('issue_type.issue_types')
            its = [i for i in issue_types_global if i['name'] == type_name and i['built_in'] == is_build_in]
            if len(its) > 0:
                issue_type_uuid = its[0]['uuid']
                return cls.add_issue_type(issue_type_uuid, project_uuid=project_uuid)

    @classmethod
    def del_issue_type_by_name(cls, type_name, project_uuid=ACCOUNT.project_uuid, is_build_in=True):
        """
        项目设置-工作项类型-删除
        :param type_name:
        :param project_uuid:
        :param is_build_in:
        :return:
        """
        p = proj.proj_stamp()[0]
        p.uri_args({"project_uuid": project_uuid})
        res = go(api.ProjectStamp, p, is_print=False).json()
        issue_types = res['issue_type_config']['issue_type_configs']
        if type_name in [i['name'] for i in issue_types]:
            # 当项目里没有工作项类型时，从全局配置中查找并添加
            param = com.gen_stamp({'issue_type': 0})
            issue_types_global = go(api.TeamStampData, param).value('issue_type.issue_types')
            its = [i for i in issue_types_global if i['name'] == type_name and i['built_in'] == is_build_in]
            if len(its) > 0:
                issue_type_uuid = its[0]['uuid']
                return cls.del_issue_type(issue_type_uuid, project_uuid=project_uuid)
