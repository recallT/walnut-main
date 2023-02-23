#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_sprint_component.py
@Author  ：Zhangweiyu
@Email   ：zhangweiyu@ones.ai
@Date    ：2022/7/7
@Desc    ：项目设置-项目组件-迭代组件-敏捷看板管理
"""
import time

from falcons.check import go
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, parametrize, step, skip
from falcons.com.nick import fixture

from main.actions.pro import PrjAction, AgileKanbanAction
from main.helper.extra import Extra
from main.actions.sprint import SprintAction
from main.api.project import ProjectStamp


@fixture(scope='module', autouse=True)
def add_project():
    # 创建一个单独项目
    time.sleep(2)
    creator = Extra(ApiMeta)
    p_id = creator.new_project(f'ApiTest-AgileKanban')
    return p_id


@fixture(scope='module', autouse=True)
def del_project(add_project):
    yield
    # 清除项目数据
    creator = Extra(ApiMeta)
    creator.del_project(add_project)


@feature('项目设置-项目组件-迭代组件-敏捷看板管理')
class TestComponentConfigSprint:
    """迭代组件配置"""

    @story('T117502 敏捷看板管理：编辑看板名称')
    def test_update_agile_kanban_name(self, add_project):
        components = PrjAction.project_stamp_data(project_uuid=add_project).value('component.components')
        with step('查看看板信息'):
            sprint_component = [c for c in components if c['name'] == '迭代'][0]
            kb_uuid = sprint_component['kanban_settings'][0]['uuid']
            kb_name = sprint_component['kanban_settings'][0]['name']
            assert kb_name == '默认看板'
        with step('修改看板名称'):
            new_name = '示例看板-upadte-name'
            components = AgileKanbanAction.update_kanban(uuid=kb_uuid, name=new_name, project_uuid=add_project)
            s_component = [c for c in components if c['name'] == '迭代'][0]
            assert s_component['kanban_settings'][0]['name'] == new_name
        with step('确认看板列表中的看板名称修改'):
            kanban, _, _ = AgileKanbanAction.get_kb_setting_by_id(uuid=kb_uuid, project_uuid=add_project)
            assert kanban['name'] == new_name

    @story('T138650 新建看板-筛选条件-系统属性：根据「工作项类型」筛选（包含）')
    def test_agile_kanban_check_filter_attribute(self, add_project):
        with step('前置条件：清空看板, 新增迭代和任务'):
            sprint_uuid = SprintAction.sprint_add(project_uuid=add_project)
            for c in range(2):
                SprintAction.new_sprint_issue(sprint_uuid, project_uuid=add_project, issue_type_name='需求')
            SprintAction.new_sprint_issue(sprint_uuid, project_uuid=add_project)

        with step('添加看板：筛选条件 工作项类型 包含 需求'):
            kanban_uuid, issue_type_uuids = AgileKanbanAction.add_kanban(project_uuid=add_project,
                                                                         lane_conditions_groups=[[
                                                                             {
                                                                                 "field_name": "工作项类型",
                                                                                 "operate": "包含",
                                                                                 "value": ["需求"]
                                                                             }
                                                                         ]])
        with step('迭代：敏捷看板泳道正确显示工作项列表'):
            status_uuid = SprintAction.sprint_status(sprint_uuid)[0]
            res = AgileKanbanAction.lane_filter_tasks(kanban_uuid=kanban_uuid, sprint_uuid=sprint_uuid,
                                                      status_uuid=status_uuid,
                                                      issue_type_uuids=issue_type_uuids,
                                                      project_uuid=add_project)
            assert len(res.value('data.tasks')) == 2
            demands = [t for t in res.value('data.tasks') if t['issueType']['name'] == '需求']
            assert len(demands) == 2
