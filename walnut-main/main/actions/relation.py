"""
@File    ：relation.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/25
@Desc    ：事项前后置依赖以及自动排期动作
"""
from falcons.check import go
from falcons.com.ones import ApiOps

from main.actions.task import TaskAction
from main.api import project as prj
from main.api import task as api
from main.api.project import ItemGraphql, RelationDocument, ProjectStamp, RelatedWikiPagesInfo
from main.params import relation as rl, proj
from main.params import task
from main.params.plan import get_plan_log_data, add_deliverables, del_deliverables
from main.params.proj import relation_document_wiki, proj_url
from main.params.relation import proj_plan_info, update_proj_plan_info, add_proj_plan_message, \
    update_proj_milestone_info


class RelationAction:
    """事项前后置依赖所用到的接口操作"""

    @classmethod
    def add_relation(cls, rl_type, source, target, code=200, token=None):
        """
        添加前置依赖/后置影响
        前置： target 为 本工作项UUID， source 为前置工作项UUID
        后置： source 为 本工作项UUID， target 为后置工作项UUID
        :param token:
        :param rl_type: 依赖关系类型
                        'sts': 'start_to_start',
                        'ste': 'start_to_end',
                        'ets': 'end_to_start',
                        'ete': 'end_to_end',
        :param source: 起 工作项UUID
        :param target: 止  UUID 工作项/项目计划/里程碑
        :param code: 响应码
        :return: 依赖关系取 data.addActivityRelationLink.key
        """

        # 1.获取项目chart_uuid

        def _clear(k: str):
            if k.startswith('activity'):
                return k[9:]
            else:
                return k

        source = _clear(source)
        target = _clear(target)

        rl_resp = go(prj.ItemGraphql, rl.chart_uuid()[0], token)
        chart_uuid = rl_resp.value('data.activityCharts[0].uuid')

        # 2.添加依赖关系
        r_type_mapper = {
            'sts': 'start_to_start',
            'ste': 'start_to_end',
            'ets': 'end_to_start',
            'ete': 'end_to_end',
        }
        relation_type = r_type_mapper.get(rl_type)
        param = rl.add_relation(relation_type)[0]

        param.json['variables'] |= {
            'source': source,
            'target': target,
            'chart_uuid': chart_uuid,
        }
        # 成功后返回数据 依赖关系取 data.addActivityRelationLink.key
        # {
        #   "data": {
        #     "addActivityRelationLink": {
        #       "key": "activity_relation_link-7CU6yrjuvp1xmJVy-7CU6yrjujJ9pcSoG-end_to_end-QjS6D1fQ"
        #     }
        #   }
        # }
        return go(prj.ItemGraphql, param, token, status_code=code)

    @classmethod
    def del_relation(cls, rl_type, source, target, token=None):
        """
        删除依赖关系
        :param token:
        :param rl_type: 依赖关系类型
                'sts': 'start_to_start',
                'ste': 'start_to_end',
                'ets': 'end_to_start',
                'ete': 'end_to_end',
        :param source: 起 工作项UUID
        :param target: 止  UUID 工作项/项目计划/里程碑
        relation_key: 依赖关系KEY 如 activity_relation_link-7CU6yrjuvp1xmJVy-7CU6yrjujJ9pcSoG-end_to_end-QjS6D1fQ
        :return:
        """
        r_type_mapper = {
            'sts': 'start_to_start',
            'ste': 'start_to_end',
            'ets': 'end_to_start',
            'ete': 'end_to_end',
        }

        def _clear(k: str):
            if k.startswith('activity'):
                return k[9:]
            else:
                return k

        source = _clear(source)
        target = _clear(target)

        rl_resp = go(prj.ItemGraphql, rl.chart_uuid()[0], token)
        chart_uuid = rl_resp.value('data.activityCharts[0].uuid')

        relation_type = r_type_mapper.get(rl_type)
        # 拼接relation_key
        relation_key = "activity_relation_link-{}-{}-{}-{}".format(source, target, relation_type, chart_uuid)
        param = rl.del_relation()[0]
        param.json_update('variables.key', relation_key)

        resp = go(prj.ItemGraphql, param, token)
        resp.check_response('data.deleteActivityRelationLink.key', relation_key)
        return resp

    @classmethod
    def query_relation_links(cls, uuid, r_type='pre', token=None):
        """
        查询前置/后置关联工作项列表

        :param token:
        :param uuid: 源或目标工作项 UUID 如果是计划或者里程碑，就填 activity 的 uuid
        :param r_type: 前置或后置 pre / post 默认前置 pre
        :return: 取值 data.activityRelationLinks []
        """
        param = rl.query_relation_links(r_type)[0]
        f_key = {
            # 前置就是 target = 自己 ，后置就是 source = 自己
            'post': 'variables.filter.source.uuid_equal',
            'pre': 'variables.filter.target.uuid_equal',
        }
        param.json_update(f_key.get(r_type), uuid)

        return go(prj.ItemGraphql, param, token)

    @classmethod
    def auto_schedule(cls, token=None):
        """
        自动排期

        :param token:
        :return:
        # {
        #   "bad_results": [],
        #   "success_count": 1,
        #   "fialed_count": 0
        # }
        """
        # 1.获取项目chart_uuid
        rl_resp = go(prj.ItemGraphql, rl.chart_uuid()[0], token)
        chart_uuid = rl_resp.value('data.activityCharts[0].uuid')
        # 2.自动排期
        param = rl.auto_schedule()[0]
        param.uri_args({'chart_uuid': chart_uuid})

        return go(api.ChartAutoSchedule, param, token)

    @classmethod
    def add_plans_or_milestones(cls, p_type='ppm', token=None, **kwargs) -> str:
        """
        新增计划/里程碑

        :param token:
        :param p_type: 默认 项目计划 ppm, 里程碑 milestone
        :return: key 形如 activity-PKr7aDDE
        """

        # 获取项目chart_uuid
        rl_resp = go(prj.ItemGraphql, rl.chart_uuid()[0], token)
        chart_uuid = rl_resp.value('data.activityCharts[0].uuid')

        prm = rl.add_plans_or_milestones(p_type)[0]
        prm.json_update('variables.chart_uuid', chart_uuid)

        # 自定义计划或/里程碑参数
        if kwargs:
            prm.json['variables'] |= kwargs
        add_resp = go(prj.ItemGraphql, prm, token)
        key = add_resp.value('data.addActivity.key')

        return key

    @classmethod
    def get_proj_plan_info(cls, plan_key, token=None):
        """
        项目计划 计划/里程碑详情信息
        :param plan_key: 计划key
        :param token:
        :return:
        """
        param = proj_plan_info(plan_key)[0]
        plan_uuid = plan_key.split('-')[1]
        param.uri_args({'plan_uuid': plan_uuid})
        info_resp = go(ItemGraphql, param, token)
        return info_resp

    @classmethod
    def fast_update_proj_plan_info(cls, field_name, field_value, key, token=None):
        """
        快速更新项目计划信息
        :param field_name: 更新字段名称
        :param field_value: 更新字段值
        :param key: 对应计划的的key
        :param token:
        :return:
        """
        param = update_proj_plan_info(field_name, field_value, key)[0]
        resp = go(prj.ItemGraphql, param, token)
        resp.check_response('data.updateActivity.key', key)
        return resp

    @classmethod
    def fast_update_proj_milestone_info(cls, key, time, token=None):
        """
        快速更新项目计划-里程碑完成时间
        :param key: plan 对应的key
        :param time: 完成时间戳
        :param token:
        :return:
        """

        param = update_proj_milestone_info(key, time)[0]
        resp = go(prj.ItemGraphql, param, token)
        resp.check_response('data.updateActivity.key', key)
        return resp

    @classmethod
    def get_plan_log_data(cls, plan_uuid, token=None):
        """
        获取项目计划 动态日志 data
        :param plan_uuid: 项目UUID
        :param token:
        :return:
        """
        param = get_plan_log_data(plan_uuid)[0]
        resp = go(ItemGraphql, param, token)
        return resp

    @classmethod
    def proj_plan_message_action(cls, query, variables):
        """
        项目计划 评论操作
        :param query: 请求参数query
        :param variables: variables字段
        :return:
        """
        param = add_proj_plan_message(query, variables)[0]

        resp = go(ItemGraphql, param)
        return resp

    @classmethod
    def del_plans_or_milestones(cls, key, token=None) -> str:
        """
        删除计划/里程碑
        :param token:
        :param key 形如 activity-PKr7aDDE
        :return: key 形如 activity-PKr7aDDE
        """
        prm = rl.del_gantt(key)[0]
        add_resp = go(prj.ItemGraphql, prm, token)
        key = add_resp.value('data.deleteActivity.key')

        return key

    @classmethod
    def update_plans_or_milestones(cls, key, status_code=200, token=None, **kwargs) -> [str, ApiOps]:
        """
        更新计划/里程碑

        页面上连线，就用这个方法

        :param token:
        :param key 形如 activity-PKr7aDDE
        :param kwargs 需要更新的数据 直接传一个字段对象
        :param status_code
        :return: key 形如 activity-PKr7aDDE
        """
        kwargs.update({'key': key})
        prm = rl.update_gantt(**kwargs)[0]
        add_resp = go(prj.ItemGraphql, prm, token, status_code=status_code)
        if status_code == 200:
            key = add_resp.value('data.updateActivity.key')

            return key
        else:
            return add_resp

    @classmethod
    def external_activity(cls, activity_uuid, *ob_uuid, ob_type='task', status=200, token=None):
        """
        项目计划关联工作项/迭代
        删除关联 使用 del_plans_or_milestones 方法

        :param token:
        :param activity_uuid: 已经创建好的 计划/里程碑 key 形如 activity-PKr7aDDE
        :param ob_uuid: 工作项/迭代 UUID 集合
        :param ob_type: 类型 task 工作项 / sprint 迭代
        :param status: 响应状态码
        :return:
        """

        # 获取项目chart_uuid
        rl_resp = go(prj.ItemGraphql, rl.chart_uuid()[0], token)
        chart_uuid = rl_resp.value('data.activityCharts[0].uuid')

        # 关联
        adding = [{'object_id': k, 'object_type': ob_type} for k in ob_uuid]
        ac_param = rl.external_activity()[0]

        ac_param.json_update('chart_uuid', chart_uuid)
        ac_param.json['add'] += adding
        ac_param.uri_args({'activity_uuid': activity_uuid.split('-')[1]})

        return go(prj.PrjExternalActivities, ac_param, token, status_code=status)

    @classmethod
    def all_gantt_data(cls, token=None) -> list:
        """
        获取测试计划所有甘特图数据
        前后置关联弹出的列表也用此方法

        关于两个工作项连线关系的描述：
        起点 为source，终点 为 target , uuid 为 activity 的KEY 后八位 形如

        "source": [
          {
            "relationType": "end_to_end",  前后置类型
            "source": {
              "uuid": "DomWVPKr"
            }
          }
        ]
        :param token:
        :return:
        """

        # 获取项目chart_uuid
        rl_resp = go(prj.ItemGraphql, rl.chart_uuid()[0], token)
        chart_uuid = rl_resp.value('data.activityCharts[0].uuid')
        gantt_param = rl.gantt_list()[0]

        filter_group = gantt_param.json['variables']['filterGroup']
        for m in filter_group:
            m['chartUUID_in'] = [chart_uuid, ]

        return go(prj.ItemGraphql, gantt_param, token).value('data.activities')

    @classmethod
    def connecred_task_and_sprint(cls, key, token=None):
        """
        关联项目计划和需求工作项
        :param key:工作项关联项目计划的key
        :param token:
        :return:
        """
        # 获取项目chart_uuid
        rl_resp = go(prj.ItemGraphql, rl.chart_uuid()[0], token)
        chart_uuid = rl_resp.value('data.activityCharts[0].uuid')
        param = rl.connecred_task_and_sprint(chart_uuid)[0]

        resp = go(ItemGraphql, param, token)
        external_activities = [d for d in resp.value('data.externalActivities') if d['key'] == key]
        return external_activities[0]

    @classmethod
    def add_ppm_relation(cls, rl_type, source, target, code=200, token=None):
        """
        项目计划添加项目计划前置依赖/后置影响
        前置： target 为 本计划UUID， source 为前置计划UUID
        后置： source 为 本计划UUID， target 为后置计划UUID
        :param token:
        :param rl_type: 依赖关系类型
                        'sts': 'start_to_start',
                        'ste': 'start_to_end',
                        'ets': 'end_to_start',
                        'ete': 'end_to_end',
        :param source: 起 工作项 就传 taskUUID  项目计划/里程碑 就传 activity_key
        :param target: 止  工作项 UUID  项目计划/里程碑 就传 activity_key
        :param code: 响应码 默认200
        :return: 依赖关系取 data.updateActivity.key
        """

        gatt_list = cls.all_gantt_data(token)
        task_gatt = [gl for gl in gatt_list if gl['ganttDataType'] in ('task', 'parent_task')]

        def _is_activity(uid):
            return uid.startswith('activity')

        def _find_key(uid):
            if not uid.startswith('activity'):
                for tg in task_gatt:
                    if uid == tg['task']['uuid']:
                        return tg['key']
            else:
                return uid

        r_type_mapper = {
            'sts': 'start_to_start',
            'ste': 'start_to_end',
            'ets': 'end_to_start',
            'ete': 'end_to_end',
        }
        s_key = _find_key(source)
        t_key = _find_key(target)
        rl_key = r_type_mapper.get(rl_type)
        gantt_kwarg = {
            "relation_type": rl_key,
            "key": s_key,
            "id": f"{s_key}-{t_key}-{rl_key}",  # 这里的ID和开发生成的ID不一致，也能成功，暂时不改
            "target": target[9:] if _is_activity(target) else target,
            "source": source[9:] if _is_activity(source) else source
        }

        param = rl.update_gantt_data(**gantt_kwarg)[0]

        return go(prj.ItemGraphql, param, token, status_code=code)

    @classmethod
    def add_activity_release(cls, is_base=True, token=None):
        """
        活动发布(创建快照等)
        :param is_base: 是否设置为基线
        :param token:
        :return:
        """

        # 获取项目chart_uuid
        rl_resp = go(prj.ItemGraphql, rl.chart_uuid()[0], token)
        chart_uuid = rl_resp.value('data.activityCharts[0].uuid')

        param = rl.add_activity(is_base=is_base)[0]
        param.json_update('variables.chart_uuid', chart_uuid)

        return go(prj.ItemGraphql, param, token)

    @classmethod
    def export_project_plan(cls, token=None):
        """
        导出项目计划、甘特图
        :param token:
        :return:
        """
        rl_resp = go(prj.ItemGraphql, rl.chart_uuid()[0], token)
        chart_uuid = rl_resp.value('data.activityCharts[0].uuid')

        gantt_param = rl.export_gantt()[0]
        filter_group = gantt_param.json['gql']['variables']['filterGroup']
        for m in filter_group:
            m['chartUUID_in'] = [chart_uuid, ]
        gantt_param.json |= {'chart_uuid': chart_uuid}

        return go(prj.ExportProjectPlan, gantt_param, token)

    @classmethod
    def task_relation_plan_key(cls, task_uuid, token=None):
        """
        获取工作项关联项目计划的key
        :param token:
        :param task_uuid  # 工作项uuid
        """
        data = cls.all_gantt_data(token)
        task_key = [d['key'] for d in data if d['task'] is not None and d['task']['uuid'] == task_uuid]
        # 当传的是迭代的uuid时，task_key为空
        if len(task_key) == 0:
            sprint_key = [d['key'] for d in data if d['sprint'] is not None and d['sprint']['uuid'] == task_uuid]
            return sprint_key[0]
        return task_key[0]

    @classmethod
    def change_issue_type(cls, task_uuid, parent_uuid, issue_type='子任务', token=None):
        """
        将工作项转化为子工作项
        :param token
        :param task_uuid  # 需转化的工作项uuid
        :param parent_uuid  # 父及工作项目uuid
        :param issue_type  # 工作项类型
        """

        re = cls.all_gantt_data(token)
        ori_t_uuid = [r['task']['issueType']['uuid']
                      for r in re
                      if r['task'] is not None and r['task']['uuid'] == task_uuid][0]
        status_uuid = [r['task']['status']['uuid']
                       for r in re
                       if r['task'] is not None and r['task']['uuid'] == task_uuid][0]

        new_t_uuid = TaskAction.issue_type_uuid(issue_type)[0]

        tasks = {
            "task_uuid": task_uuid,
            "old_issue_type_uuid": ori_t_uuid,
            "new_issue_type_uuid": new_t_uuid,
            "status": {
                "old_status_uuid": status_uuid,
                "new_status_uuid": status_uuid
            },
            "field_values": None,
            "parent_uuid": parent_uuid
        }
        prm = task.update_issue_type(tasks)[0]

        return go(api.UpdateIssueType, prm, token)

    @classmethod
    def add_message(cls, object_id, object_type):
        """
        添加评论
        :param object_id: 评论的对应任务id
        :param object_type: 类型 ppm_task milestone等
        :return: 返回评论信息的key
        """
        query = "\n    mutation AddComment { addCommonComment (object_id: $object_id object_type: $object_type message: $message ) { key }}\n  "
        variables = {"object_id": object_id, "object_type": object_type, "message": "this is a message"}
        resp_add = cls.proj_plan_message_action(query, variables)
        return resp_add.value('data.addCommonComment.key')

    @classmethod
    def update_message(cls, key):
        """
        编辑回复信息
        :param key: 被编辑的信息key
        :return:
        """
        query = "\n    mutation UpdateComment { updateCommonComment (key: $key message: $message ) { key}}\n  "
        variables = {"key": key, "message": "update messages hahaha"}
        cls.proj_plan_message_action(query, variables)

    @classmethod
    def reply_message(cls, object_id, object_type, reference_id):
        """
        回复信息/在信息下评论
        :param object_id: 评论的对应任务id
        :param object_type: 类型 ppm_task milestone等
        :param reference_id: 被回复信息的Id
        :return:
        """
        query = "\n    mutation AddComment { addCommonComment (object_id: $object_id object_type: $object_type message: $message reference_id: $reference_id) { key }}\n  "
        variables = {"object_id": object_id, "object_type": object_type, "message": "message message",
                     "reference_id": reference_id}
        cls.proj_plan_message_action(query, variables)

    @classmethod
    def del_message(cls, key):
        """
        删除评论操作
        :param key: 评论的key
        :return:
        """
        query = "\n    mutation UpdateComment { updateCommonComment (key: $key message: $message status: $status) { key}}\n  "
        variables = {"key": key, "message": "", "status": 2}
        cls.proj_plan_message_action(query, variables)

    @classmethod
    def add_deliverables(cls, milestone_uuid, up_type, after=''):
        """
        里程碑组件中新增交付物
        :param milestone_uuid: 里程碑UUID
        :param up_type: 交付物类型
        :param after: 排在前面的交付物id
        :return:
        """
        param = add_deliverables(milestone_uuid, up_type, after)[0]
        resp = go(ItemGraphql, param)
        return resp

    @classmethod
    def del_deliverables(cls, key):
        """
        删除交付物
        :param key: 交付物key
        :return:
        """
        param = del_deliverables(key)[0]
        resp = go(ItemGraphql, param)
        resp.check_response('data.deleteDeliverable.key', key)

    @classmethod
    def get_component_uuid(cls, component_name):
        """
        获取项目内组件的UUID
        :param component_name: 组件名称 任务 需求 文档 发布等组件名称
        :param token:
        :return:
        """
        template_obj = go(ProjectStamp, proj.proj_stamp()[0], is_print=False)
        template_json = template_obj.json()
        component_uuid = [r['uuid'] for r in template_json['component']['components']
                          if r['name'] == component_name][0]
        return component_uuid

    @classmethod
    def relation_document_wiki(cls, bind=None, unbind=None, token=None):
        """
        文档绑定/解绑wiki
        :param bind: 绑定wiki的uuid列表
        :param unbind: 解绑Wiki的uuid
        :param token:
        :return:
        """
        if bind is None:
            bind = []
        component_uuid = cls.get_component_uuid('文档')
        param = relation_document_wiki(bind, unbind)[0]
        param.uri_args({'component_uuid': component_uuid})
        resp = go(RelationDocument, param, token)
        return resp

    @classmethod
    def get_rel_wiki_info(cls, token=None):
        """
        获取文档组件管理wiki信息
        :param token:
        :return:
        """
        component_uuid = cls.get_component_uuid('文档')
        param = proj_url()[0]
        param.uri_args({'component_uuid': component_uuid})
        resp = go(RelatedWikiPagesInfo, param, token)
        return resp
