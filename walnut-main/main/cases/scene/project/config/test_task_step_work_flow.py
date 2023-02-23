# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_task_step_work_flow.py
@Author  ：zhangyonghui@ones.ai
@Date    ：2022/6/16 11:16 AM 
@Desc    ：项目设置/工作项-工作流
"""

from falcons.check import Checker, go
from falcons.com.nick import story, step, fixture, feature

from main.actions.task import TaskAction as Ta
from main.actions.pro import PrjAction as pa
from main.api import project
from main.api.issue import ProjWorkflowTransitionAdd, SortIssueType, TaskSort
from main.params import issue, task, proj, conf


@fixture(scope='module', autouse=True)
def proj_task_config():
    """获取项目内工作项工作流状态数据"""
    resp = Ta.get_task_config()
    return resp


@feature('项目工作项-工作流')
class TestProjWorkFlow(Checker):

    @story('T152309 工作项工作流：检查工作项详情页状态流转步骤（任务）')
    def test_task_work_flow_change(self, proj_task_config):
        with step('前置条件：创建一个任务工作项'):
            issue_type_uuid = Ta.issue_type_uuid('任务')[0]
            # 查询整个项目的工作项工作流
            list_status = [f['name'] for f in proj_task_config.value('transition.transitions') if
                           f['issue_type_uuid'] == issue_type_uuid]
            task_uuid = Ta.new_issue(issue_type_name='任务', is_batch=False)[0]
        with step('查看任务状态下拉框（当前状态为未开始）'):
            resp_transitions = pa.get_task_transitions(task_uuid)
            transitions_name = [rt['name'] for rt in resp_transitions.value('transitions')]
            assert set(transitions_name) < set(list_status)
            # 修改状态为开始任务
            transitions_uuid = [r['uuid'] for r in resp_transitions.value('transitions') if
                                r['name'] == transitions_name[0]][0]
            Ta.transit_task_status(transitions_uuid, task_uuid)
        with step('查看任务状态下拉框（当前状态为进行中）'):
            resp_transitions = pa.get_task_transitions(task_uuid)
            transitions_name = [name_list['name'] for name_list in resp_transitions.value('transitions')]
            assert set(transitions_name) < set(list_status)

    @story('T152306 工作项工作流：检查工作项详情页状态流转步骤（缺陷）')
    def test_flaw_work_flow_change(self, proj_task_config):
        with step('前置条件：创建一个缺陷工作项'):
            issue_type_uuid = Ta.issue_type_uuid('缺陷')[0]
            # 查询整个项目的工作项工作流
            list_status = [f['name'] for f in proj_task_config.value('transition.transitions') if
                           f['issue_type_uuid'] == issue_type_uuid]
            task_uuid = Ta.new_issue(issue_type_name='缺陷', is_batch=False)[0]
        with step('查看任务状态下拉框（当前状态为未开始）'):
            resp_transitions = pa.get_task_transitions(task_uuid)
            transitions_name = [name_list['name'] for name_list in resp_transitions.value('transitions')]
            assert set(transitions_name) < set(list_status)
            # 修改状态为已确认  TODO 用例不稳定，先注释
        #     transitions_uuid = [rt['uuid'] for rt in resp_transitions.value('transitions') if
        #                         rt['name'] == transitions_name[0]][0]
        #     Ta.transit_task_status(transitions_uuid, task_uuid)
        # with step('查看任务状态下拉框（当前状态为已确认）'):
        #     resp_transitions = pa.get_task_transitions(task_uuid)
        #     transitions_name = [r['name'] for r in resp_transitions.value('transitions')]
        #     assert set(transitions_name) < set(list_status)

    @story('T152307 工作项工作流：检查工作项详情页状态流转步骤（需求）')
    def test_demand_work_flow_change(self, proj_task_config):
        with step('前置条件：创建一个需求工作项'):
            issue_type_uuid = Ta.issue_type_uuid('需求')[0]
            # 查询整个项目的工作项工作流
            list_status = [f['name'] for f in proj_task_config.value('transition.transitions') if
                           f['issue_type_uuid'] == issue_type_uuid]
            task_uuid = Ta.new_issue(issue_type_name='需求', is_batch=False)[0]
        with step('查看任务状态下拉框（当前状态为未开始）'):
            resp_transitions = pa.get_task_transitions(task_uuid)
            transitions_name = [name_list['name'] for name_list in resp_transitions.value('transitions')]
            assert set(transitions_name) < set(list_status)
            # 修改状态为已确认  TODO 用例不稳定，先注释
        #     transitions_uuid = [name_list['uuid'] for name_list in resp_transitions.value('transitions') if
        #                         name_list['name'] == transitions_name[0]][0]
        #     Ta.transit_task_status(transitions_uuid, task_uuid)
        # with step('查看任务状态下拉框（当前状态为实现中）'):
        #     resp_transitions = pa.get_task_transitions(task_uuid)
        #     transitions_name = [rt['name'] for rt in resp_transitions.value('transitions')]
        #     assert set(transitions_name) < set(list_status)
        #     # 修改状态为已确认
        #     transitions_uuid = [rt['uuid'] for rt in resp_transitions.value('transitions') if
        #                         rt['name'] == transitions_name[0]][0]
        #     Ta.transit_task_status(transitions_uuid, task_uuid)
        # with step('查看任务状态下拉框（当前状态为已实现）'):
        #     resp_transitions = pa.get_task_transitions(task_uuid)
        #     transitions_name = [rt['name'] for rt in resp_transitions.value('transitions')]
        #     assert set(transitions_name) < set(list_status)

    @story('T152310 工作项工作流：检查工作项详情页状态流转步骤（子任务）')
    def test_sub_task_work_flow_change(self, proj_task_config):
        with step('前置条件：创建一个缺陷工作项'):
            issue_type_uuid = Ta.issue_type_uuid('子任务')[0]
            # 查询整个项目的工作项工作流
            list_status = [f['name'] for f in proj_task_config.value('transition.transitions') if
                           f['issue_type_uuid'] == issue_type_uuid]
            task_uuid = Ta.new_issue(issue_type_name='任务', is_batch=False)[0]
            sub_task_uuid = Ta.new_issue(parent_uuid=task_uuid, issue_type_name="子任务",
                                         is_batch=False)[0]
        with step('查看任务状态下拉框（当前状态为未开始）'):
            resp_transitions = pa.get_task_transitions(sub_task_uuid)
            transitions_name = [name_list['name'] for name_list in resp_transitions.value('transitions')]
            assert set(transitions_name) < set(list_status)
            # 修改状态为开始任务
            transitions_uuid = [rt['uuid'] for rt in resp_transitions.value('transitions') if
                                rt['name'] == transitions_name[0]][0]
            Ta.transit_task_status(transitions_uuid, sub_task_uuid)
        with step('查看任务状态下拉框（当前状态为进行中）'):
            resp_transitions = pa.get_task_transitions(sub_task_uuid)
            transitions_name = [rt['name'] for rt in resp_transitions.value('transitions')]
            assert set(transitions_name) < set(list_status)

    @story('T152308 工作项工作流：检查工作项详情页状态流转步骤（子需求）')
    def test_sub_demand_work_flow_change(self, proj_task_config):
        with step('前置条件：创建一个子需求工作项'):
            issue_type_uuid = Ta.issue_type_uuid('子需求')[0]
            # 查询整个项目的工作项工作流
            list_status = [f['name'] for f in proj_task_config.value('transition.transitions') if
                           f['issue_type_uuid'] == issue_type_uuid]
            task_uuid = Ta.new_issue(issue_type_name='需求', is_batch=False)[0]
            sub_demand_uuid = Ta.new_issue(parent_uuid=task_uuid, issue_type_name="子需求",
                                           is_batch=False)[0]
        with step('查看任务状态下拉框（当前状态为未开始）'):
            resp_transitions = pa.get_task_transitions(sub_demand_uuid)
            transitions_name = [name_list['name'] for name_list in resp_transitions.value('transitions')]
            assert set(transitions_name) < set(list_status)

            # 修改状态为开始任务
            transitions_uuid = [name_list['uuid'] for name_list in resp_transitions.value('transitions') if
                                name_list['name'] == transitions_name[0]][0]
            Ta.transit_task_status(transitions_uuid, sub_demand_uuid)
        with step('查看任务状态下拉框（当前状态为开始研发）'):
            resp_transitions = pa.get_task_transitions(sub_demand_uuid)
            transitions_name = [name_list['name'] for name_list in resp_transitions.value('transitions')]
            assert set(transitions_name) < set(list_status)

    @story('T152154 工作项工作流：检查项目下工作项工作流默认状态及步骤检查（缺陷-开箱）')
    def test_default_flaw_word_flow(self, proj_task_config):
        # 获取工作项issue_type_uuid
        issue_type_uuid = Ta.issue_type_uuid('缺陷')[0]
        # 查询整个项目的工作项工作流
        list_name = [f['name'] for f in proj_task_config.value('transition.transitions') if
                     f['issue_type_uuid'] == issue_type_uuid]
        # status_list = ['已验证', '已拒绝', '关闭', '已确认', '已解决', '重新打开', '已修复']
        assert '重新打开' in list_name

    @story('T152158 工作项工作流：检查项目下工作项工作流默认状态及步骤检查（任务-开箱）')
    def test_default_task_word_flow(self, proj_task_config):
        # 获取工作项issue_type_uuid
        issue_type_uuid = Ta.issue_type_uuid('任务')[0]
        # 查询整个项目的工作项工作流

        list_name = [f['name'] for f in proj_task_config.value('transition.transitions') if
                     f['issue_type_uuid'] == issue_type_uuid]
        # status_list = ['完成任务', '开始任务', '未开始', '重启任务']
        print(list_name)
        assert '开始任务' in list_name

    @story('T152152 工作项工作流：检查项目下工作项工作流默认状态及步骤检查（需求-开箱）')
    def test_default_demand_word_flow(self, proj_task_config):
        # 获取工作项issue_type_uuid
        issue_type_uuid = Ta.issue_type_uuid('需求')[0]
        # 查询整个项目的工作项工作流

        list_name = [f['name'] for f in proj_task_config.value('transition.transitions') if
                     f['issue_type_uuid'] == issue_type_uuid]
        print(list_name)
        # status_list = ['未开始', '已拒绝', '关闭', '已实现', '实现中']
        assert ('关闭' in list_name) or ('关闭需求' in list_name)

    @story('T123120 工作项工作流：设置初始状态-任务')
    def test_set_default_status_task(self, proj_task_config):
        issue_type_uuid = Ta.issue_type_uuid('任务')[0]
        task_status_uuid = \
            [f['status_uuid'] for f in proj_task_config.value('task_status_config.task_status_configs') if
             f['issue_type_uuid'] == issue_type_uuid and f['default'] == True][0]
        with step('设置初始化状态'):
            param = issue.issue_workflow_set_init()[0]
            param.uri_args({'issue_type': issue_type_uuid, 'task_status': task_status_uuid})
            resp = self.call(project.WordFlowUpdate, param)
            resp.check_response('task_status_config.status_uuid', task_status_uuid)
            resp.check_response('task_status_config.default', True)

    @story('T123131 工作项工作流：设置初始状态-子任务')
    def test_set_default_status_sub_task(self, proj_task_config):
        issue_type_uuid = Ta.issue_type_uuid('子任务')[0]
        task_status_uuid = \
            [f['status_uuid'] for f in proj_task_config.value('task_status_config.task_status_configs') if
             f['issue_type_uuid'] == issue_type_uuid and f['default'] == True][0]
        with step('设置初始化状态'):
            param = issue.issue_workflow_set_init()[0]
            param.uri_args({'issue_type': issue_type_uuid, 'task_status': task_status_uuid})
            resp = self.call(project.WordFlowUpdate, param)
            resp.check_response('task_status_config.status_uuid', task_status_uuid)
            resp.check_response('task_status_config.default', True)

    @story('T152157 工作项工作流：检查项目下工作项工作流默认状态及步骤检查（子需求-开箱）')
    def test_default_sub_demand_word_flow(self, proj_task_config):
        # 获取工作项issue_type_uuid
        issue_type_uuid = Ta.issue_type_uuid('子需求')[0]
        # 查询整个项目的工作项工作流

        list_name = [f['name'] for f in proj_task_config.value('transition.transitions') if
                     f['issue_type_uuid'] == issue_type_uuid]
        print(list_name)
        # status_list = ['开始研发', '关闭需求', '开始设计', '未激活', '开始测试', '重启需求', '已发布', '已计划']
        assert '关闭需求' in list_name

    @story('T152159 工作项工作流：检查项目下工作项工作流默认状态及步骤检查（子任务-开箱）')
    def test_default_sub_task_word_flow(self, proj_task_config):
        # 获取工作项issue_type_uuid
        issue_type_uuid = Ta.issue_type_uuid('子任务')[0]
        # 查询整个项目的工作项工作流

        list_name = [f['name'] for f in proj_task_config.value('transition.transitions') if
                     f['issue_type_uuid'] == issue_type_uuid]
        print(list_name)
        # status_list = ['重启任务', '完成任务', '开始任务', '完成任务', '未开始']
        assert '开始任务' in list_name

    @story('T123199 工作项工作流：详情视图下移除初始状态')
    def test_del_default_status(self):
        ...

    @story('T123255 工作项工作流：新建步骤')
    def test_add_word_flow_step(self, proj_task_config):
        issue_type_uuid = Ta.issue_type_uuid('子任务')[0]
        start_status_uuid = \
            [f['status_uuid'] for f in proj_task_config.value('task_status_config.task_status_configs') if
             f['issue_type_uuid'] == issue_type_uuid and f['default'] == True][0]

        end_status_uuid = [f['status_uuid'] for f in proj_task_config.value('task_status_config.task_status_configs') if
                           f['issue_type_uuid'] == issue_type_uuid and f['default'] == False][0]
        with step('新建步骤'):
            param = task.issue_workflow_transition_add(issue_type_uuid, start_status_uuid, end_status_uuid)[0]
            param.uri_args({'issue_type_uuid': issue_type_uuid})
            resp = self.call(ProjWorkflowTransitionAdd, param)
            resp.check_response('transitions[0].start_status_uuid', start_status_uuid)
            resp.check_response('transitions[0].end_status_uuid', end_status_uuid)
            resp.check_response('transitions[0].issue_type_uuid', issue_type_uuid)

    @story('T123379 工作项类型：排序')
    def test_word_task_sort(self):
        # 获取所有工作项的UUID列表
        prm = proj.proj_stamp()[0]
        prm.json = {"issue_type_config": 0}
        issue_response = go(project.ProjectStamp, prm, is_print=False)
        uuid_list = [r['issue_type_uuid'] for r in issue_response.value('issue_type_config.issue_type_configs')]
        with step('长按「需求」移动至「缺陷」后'):
            list_len = len(uuid_list)
            # 打乱排位顺序
            uuid_list[list_len - 2], uuid_list[list_len - 1] = uuid_list[list_len - 1], uuid_list[list_len - 2]
            uuid_list.reverse()
            param = issue.sort_issue_type(uuid_list)[0]
            self.call(SortIssueType, param)

    @story('T123327 工作项工作流：状态排序-任务 ')
    def test_sort_task(self, proj_task_config):
        issue_type_uuid = Ta.issue_type_uuid('任务')[0]
        # 查询整个项目的工作项工作流
        status_uuid_list = [f['status_uuid'] for f in proj_task_config.value('task_status_config.task_status_configs')
                            if f['issue_type_uuid'] == issue_type_uuid]
        with step('长按 2状态 拖拽至列表最后,点击确认'):
            positions = []
            for u in range(len(status_uuid_list)):
                positions.append({'status_uuid': status_uuid_list[u], 'position': u})
            # 更换排序位置
            positions[len(status_uuid_list) - 1]['position'], positions[len(status_uuid_list) - 2]['position'] = \
                positions[len(status_uuid_list) - 2]['position'], positions[
                    len(status_uuid_list) - 1]['position']
            param = issue.task_sort(positions)[0]
            param.uri_args({'issue_type_uuid': issue_type_uuid})
            resp = self.call(TaskSort, param)
            resp.check_response('code', 200)

    @story('T123323 工作项工作流：状态排序-子任务 ')
    def test_sort_sub_task(self, proj_task_config):
        issue_type_uuid = Ta.issue_type_uuid('子任务')[0]
        # 查询整个项目的工作项工作流
        status_uuid_list = [f['status_uuid'] for f in proj_task_config.value('task_status_config.task_status_configs')
                            if f['issue_type_uuid'] == issue_type_uuid]
        with step('长按 2状态 拖拽至列表最后,点击确认'):
            positions = []
            for u in range(len(status_uuid_list)):
                positions.append({'status_uuid': status_uuid_list[u], 'position': u})
            # 更换排序位置
            positions[len(status_uuid_list) - 1]['position'], positions[len(status_uuid_list) - 2]['position'] = \
                positions[len(status_uuid_list) - 2]['position'], positions[
                    len(status_uuid_list) - 1]['position']
            param = issue.task_sort(positions)[0]
            param.uri_args({'issue_type_uuid': issue_type_uuid})
            resp = self.call(TaskSort, param)
            resp.check_response('code', 200)

    @story('T123314 工作项工作流：状态排序-需求 ')
    def test_sort_demand(self, proj_task_config):
        issue_type_uuid = Ta.issue_type_uuid('需求')[0]
        # 查询整个项目的工作项工作流
        status_uuid_list = [f['status_uuid'] for f in proj_task_config.value('task_status_config.task_status_configs')
                            if f['issue_type_uuid'] == issue_type_uuid]
        with step('长按 2状态 拖拽至列表最后,点击确认'):
            positions = []
            for u in range(len(status_uuid_list)):
                positions.append({'status_uuid': status_uuid_list[u], 'position': u})
            # 更换排序位置
            positions[len(status_uuid_list) - 1]['position'], positions[len(status_uuid_list) - 2]['position'] = \
                positions[len(status_uuid_list) - 2]['position'], positions[
                    len(status_uuid_list) - 1]['position']
            param = issue.task_sort(positions)[0]
            param.uri_args({'issue_type_uuid': issue_type_uuid})
            resp = self.call(TaskSort, param)
            resp.check_response('code', 200)

    @story('T123392 工作项类型：添加属性到工作项类型')
    def test_add_task_field(self):
        # 获取所有工作项uuid
        prm = proj.proj_stamp()[0]
        prm.json = {"issue_type_config": 0}
        issue_response = go(project.ProjectStamp, prm, is_print=False)
        uuid_list = [r['issue_type_uuid'] for r in issue_response.value('issue_type_config.issue_type_configs')]
        with step('点击「添加属性到工作项类型」 全选工作项类型'):
            # "field011", "field013" 固定添加系统属性 所属迭代 截止时间
            param = issue.add_task_field(["field011", "field013"], uuid_list)[0]
            self.call(project.AddTaskField, param)
            # todo：断言在所有组件中都有新增的字段

    @story('T123395 工作项类型：添加属性到项目-工作项类型')
    def test_test_add_task_field1(self):
        # 新增工作项属性
        param = conf.add_issue_type_field()[0]
        res = self.call(project.FieldsAdd, param)
        field_uuid = res.value('field.uuid')

        prm = proj.proj_stamp()[0]
        prm.json = {"issue_type_config": 0}
        issue_response = go(project.ProjectStamp, prm, is_print=False)
        uuid_list = [r['issue_type_uuid'] for r in issue_response.value('issue_type_config.issue_type_configs')]
        with step('点击「添加属性到工作项类型」 全选工作项类型'):
            # field012 固定添加系统属性
            param = issue.add_task_field(["field012", field_uuid], uuid_list)[0]
            self.call(project.AddTaskField, param)
