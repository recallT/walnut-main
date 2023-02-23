"""
@Desc：项目设置-步骤-后置动作-状态关联
@Author  ：zhangweiyu@ones.ai
"""
import time
from falcons.check import Checker, go
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture, step, parametrize
from falcons.ops import generate_param

from main.actions.task import TaskAction
from main.api import issue
from main.helper.extra import Extra
from . import update_post_action, relate_tasks, trigger, get_status_list, get_start_step, get_finish_step, \
    get_issue_types, get_default_status


@fixture(scope='module', autouse=True)
def add_project():
    # 创建一个单独项目
    time.sleep(2)
    creator = Extra(ApiMeta)
    project_uuid = creator.new_project(f'ApiTest-Task-SPA')
    it_map = get_issue_types(project_uuid)
    for i in ['任务', '子任务']:
        statuses = get_status_list(project_uuid, i)
        it_id = it_map[i]
        param = generate_param({
            "transitions": [
                {
                    "project_uuid": project_uuid,
                    "issue_type_uuid": it_id,
                    "start_status_uuid": statuses['未开始'],
                    "end_status_uuid": statuses['已完成'],
                    "name": "完成任务"
                }
            ]
        })[0]
        param.uri_args({'project_uuid': project_uuid, 'issue_type_uuid': it_id})
        # 新建步骤「完成任务」：未开始-已完成
        go(issue.ProjWorkflowTransitionAdd, param, is_print=False)
    return project_uuid


@fixture(scope='module', autouse=True)
def del_project(add_project):
    yield
    # 清除项目数据
    creator = Extra(ApiMeta)
    creator.del_project(add_project)


@fixture(scope='module')
def bug_status(add_project):
    statuses = get_status_list(add_project, '缺陷')
    return statuses


@feature('项目设置-步骤-后置动作-状态关联')
class TestPrjPostActionStatusAssociation(Checker):

    @story('T130649 任务-后置动作：添加状态联动后置动作（全部关联工作项）（后置动作验证：无）')
    @story('T129787 任务-后置动作：检查状态联动后置动作事件（全部关联工作项）（后置动作验证：无）（有关联工作项）')
    @story('T130644 子任务-后置动作：添加状态联动后置动作（全部关联工作项）（后置动作验证：无）')
    @story('T129788 子任务-后置动作：检查状态联动后置动作事件（全部关联工作项）（后置动作验证：无）（有关联工作项）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_status_association_129787(self, add_project, typ):
        with step('添加状态联动后置动作'):
            target_status = get_status_list(add_project, issue_type_name=typ)['已完成']  # 获取任务的最后一个状态
            start_step = get_start_step(add_project, issue_type_name=typ)
            post_function = [
                {
                    "update_status": {
                        "target": "related",
                        "target_range": {
                            "links": [],
                            "issue_types": [],
                            "statuses": []
                        },
                        "target_status": target_status,  # 任务的最后一个状态
                        "validation_type": "none",
                        "validation_params": {
                            "params1": "",
                            "params2": ""
                        }
                    }
                }
            ]

            add_res = update_post_action(start_step, post_function)
            add_res.check_response('transition.uuid', start_step['uuid'])
        with step('检查状态联动后置动作事件'):
            # 添加任务1、2，任务1关联任务2
            task1 = TaskAction.new_issue(proj_uuid=add_project)[0]
            if typ.startswith('子'):
                task1 = TaskAction.new_issue(proj_uuid=add_project, parent_uuid=task1,
                                             issue_type_name=typ)[0]
            task2 = TaskAction.new_issue(proj_uuid=add_project)[0]
            relate_tasks(task1, task2)
            # 触发任务1的开始任务
            trigger(task_uuid=task1, transit_uuid=start_step['uuid'])
            task1_info = TaskAction.task_info(task1)
            task1_info.check_response('status_uuid', start_step['end_status_uuid'])
            # 检查任务2的状态
            task2_info = TaskAction.task_info(task2)
            task2_info.check_response('status_uuid', target_status)
        with step('清除后置动作'):
            update_post_action(start_step, [])

    @story('T129741 任务-后置动作：检查状态联动后置动作事件（全部关联工作项）（后置动作验证：关联工作项）')
    @story('T130626 子任务-后置动作：添加状态联动后置动作（全部关联工作项）（后置动作验证：关联工作项）')
    @story('T129752 子任务-后置动作：检查状态联动后置动作事件（全部关联工作项）（后置动作验证：关联工作项）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_status_association_129741(self, add_project, typ):
        with step('完成任务-添加状态联动后置动作'):
            finish_step = get_finish_step(add_project, issue_type_name=typ)
            target_status = finish_step['end_status_uuid']
            post_function = [
                {
                    "update_status": {
                        "target": "related",
                        "target_range": {
                            "links": [],
                            "issue_types": [],
                            "statuses": []
                        },
                        "target_status": target_status,
                        "validation_type": "related",
                        "validation_params": {
                            "param_1": "",
                            "param_2": ""
                        }
                    }
                }
            ]
            add_res = update_post_action(finish_step,
                                         post_function)

            add_res.check_response('transition.uuid', finish_step['uuid'])

        with step('检查状态联动后置动作事件'):
            # 添加任务1、2、3，任务1->任务2，任务2->任务3
            task1 = TaskAction.new_issue(proj_uuid=add_project)[0]
            if typ.startswith('子'):
                task1 = TaskAction.new_issue(proj_uuid=add_project, parent_uuid=task1,
                                             issue_type_name=typ)[0]
            task2 = TaskAction.new_issue(proj_uuid=add_project)[0]
            task3 = TaskAction.new_issue(proj_uuid=add_project)[0]
            relate_tasks(task1, task2)
            relate_tasks(task2, task3)
            # 修改task3的状态为已完成
            trigger(task3, finish_step['uuid'])
            # 触发task1的完成任务步骤
            trigger(task1, finish_step['uuid'])
            # 查看task2的状态是否为已完成
            task2_info = TaskAction.task_info(task2)
            task2_info.check_response('status_uuid', target_status)

        with step('清除后置动作'):
            update_post_action(finish_step, [])

    @story('T129819 任务-检查状态联动后置动作事件（全部关联工作项）（特定后置动作验证：关联工作项）')
    @story('T129822 子任务-后置动作：检查状态联动后置动作事件（全部关联工作项）（特定后置动作验证：关联工作项）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_status_association_129819(self, add_project, bug_status, typ):
        with step('完成任务-添加状态联动后置动作'):
            finish_step = get_finish_step(add_project, issue_type_name=typ)
            target_status = bug_status['关闭']  # 缺陷的最后一个状态
            issue_types = get_issue_types(add_project)
            post_function = [
                {
                    "update_status": {
                        "target": "related",
                        "target_range": {
                            "links": [],
                            "issue_types": [],
                            "statuses": []
                        },
                        "target_status": target_status,
                        "validation_type": "related",
                        "validation_params": {
                            "param_1": issue_types['缺陷'],
                            "param_2": issue_types['任务']
                        }
                    }
                }
            ]
            add_res = update_post_action(finish_step,
                                         post_function)

            add_res.check_response('transition.uuid', finish_step['uuid'])
        with step('检查状态联动后置动作事件'):
            # 添加任务1、2、3，任务1->任务2，任务2->任务3
            task1 = TaskAction.new_issue(proj_uuid=add_project)[0]
            if typ.startswith('子'):
                task1 = TaskAction.new_issue(proj_uuid=add_project, parent_uuid=task1,
                                             issue_type_name=typ)[0]
            task2 = TaskAction.new_issue(proj_uuid=add_project, issue_type_name='缺陷')[0]
            task3 = TaskAction.new_issue(proj_uuid=add_project)[0]
            relate_tasks(task1, task2)
            relate_tasks(task2, task3)
            # 修改task3的状态为已完成
            trigger(task3, finish_step['uuid'])
            # 触发task1的完成任务步骤
            trigger(task1, finish_step['uuid'])
            # 查看task2的状态是否为已完成
            task2_info = TaskAction.task_info(task2)
            task2_info.check_response('status_uuid', target_status)
        with step('清除后置动作'):
            update_post_action(finish_step, [])

    @story('T130731 子任务-后置动作：添加状态联动后置动作（特定关联工作项）（后置动作验证：无）')
    @story('T129870 任务-后置动作：检查状态联动后置动作事件（特定关联工作项）（后置动作验证：无）（有关联工作项）')
    @story('T129868 子任务-后置动作：检查状态联动后置动作事件（特定关联工作项）（后置动作验证：无）（有关联工作项）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_status_association_129870(self, add_project, bug_status, typ):
        with step('完成任务-添加状态联动后置动作: '):
            finish_step = get_finish_step(add_project, issue_type_name=typ)
            target_status = bug_status['关闭']  # 缺陷的最后一个状态
            issue_types = get_issue_types(add_project)
            post_function = [
                {
                    "update_status": {
                        "target": "related",
                        "target_range": {
                            "links": [{"desc_type": "link_out_desc",
                                       "uuid": "UUID0001"}],
                            "issue_types": [issue_types['缺陷']],
                            "statuses": [get_default_status(add_project, '缺陷')]  # 新建缺陷的默认状态
                        },
                        "target_status": target_status,
                        "validation_type": "none",
                        "validation_params": {
                            "param_1": "",
                            "param_2": ""
                        }
                    }
                }
            ]
            add_res = update_post_action(finish_step, post_function)
            add_res.check_response('transition.uuid', finish_step['uuid'])
        with step('检查状态联动后置动作事件'):
            # 任务/子任务，关联缺陷
            task1 = TaskAction.new_issue(proj_uuid=add_project)[0]
            if typ.startswith('子'):
                task1 = TaskAction.new_issue(proj_uuid=add_project, parent_uuid=task1,
                                             issue_type_name=typ)[0]
            # 缺陷
            bug1 = TaskAction.new_issue(proj_uuid=add_project, issue_type_name='缺陷')[0]
            relate_tasks(task1, bug1)
            # 触发task1的完成任务步骤
            trigger(task1, finish_step['uuid'])
            # 查看bug1的状态是否为已完成
            bug1_info = TaskAction.task_info(bug1)
            bug1_info.check_response('status_uuid', target_status)
        with step('清除后置动作'):
            update_post_action(finish_step, [])

    @story('T130676 任务-后置动作：添加状态联动后置动作（全部关联工作项）（后置动作验证：子工作项）')
    @story('T130678 子任务-后置动作：添加状态联动后置动作（全部关联工作项）（后置动作验证：子工作项）')
    @story('T129842 子任务-后置动作：检查状态联动后置动作事件（全部关联工作项）（特定后置动作验证：子工作项）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_status_association_129842(self, add_project, bug_status, typ):
        with step('完成任务-添加状态联动后置动作'):
            finish_step = get_finish_step(add_project, issue_type_name=typ)
            target_status = bug_status['关闭']
            post_function = [
                {
                    "update_status": {
                        "target": "related",
                        "target_range": {
                            "links": [],
                            "issue_types": [],
                            "statuses": []
                        },
                        "target_status": target_status,
                        "validation_type": "parent",
                        "validation_params": {
                            "param_1": "",
                            "param_2": ""
                        }
                    }
                }
            ]
            add_res = update_post_action(finish_step,
                                         post_function)

            add_res.check_response('transition.uuid', finish_step['uuid'])
        if typ.startswith('子'):
            with step('检查状态联动后置动作事件'):
                # 父任务
                f1 = TaskAction.new_issue(proj_uuid=add_project)[0]
                task1 = TaskAction.new_issue(proj_uuid=add_project, parent_uuid=f1,
                                             issue_type_name=typ)[0]
                task2 = TaskAction.new_issue(proj_uuid=add_project, parent_uuid=f1,
                                             issue_type_name=typ)[0]
                # 缺陷
                bug1 = TaskAction.new_issue(proj_uuid=add_project, issue_type_name='缺陷')[0]
                # 关联task1和bug1
                relate_tasks(task1, bug1)
                # 将task2的状态变为已完成
                trigger(task2, finish_step['uuid'])
                # 触发task1的步骤：完成任务
                trigger(task1, finish_step['uuid'])
                # 查看bug1的状态，是否为关闭
                bug1_info = TaskAction.task_info(bug1)
                bug1_info.check_response('status_uuid', target_status)
        with step('清除后置动作'):
            update_post_action(finish_step, [])

    @story('T130526 任务-后置动作：添加状态联动后置动作（父工作项）（后置动作验证：关联工作项）')
    @story('T130509 子任务-后置动作：添加状态联动后置动作（父工作项）（后置动作验证：关联工作项）')
    @story('T129672 子任务-后置动作：检查状态联动后置动作事件（父工作项）（后置动作验证：关联工作项）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_status_association_129672(self, add_project, typ):
        with step('完成任务-添加状态联动后置动作'):
            finish_step = get_finish_step(add_project, issue_type_name=typ)
            target_status = get_status_list(add_project, typ)['进行中']
            post_function = [
                {
                    "update_status": {
                        "target": "parent",
                        "target_range": {},
                        "target_status": target_status,
                        "validation_type": "related",
                        "validation_params": {
                            "param_1": "",
                            "param_2": ""
                        }
                    }
                }
            ]
            add_res = update_post_action(finish_step,
                                         post_function)

            add_res.check_response('transition.uuid', finish_step['uuid'])
        if typ.startswith('子'):
            with step('检查状态联动后置动作事件'):
                # 父任务
                f1 = TaskAction.new_issue(proj_uuid=add_project)[0]
                task1 = TaskAction.new_issue(proj_uuid=add_project, parent_uuid=f1,
                                             issue_type_name=typ)[0]
                task2 = TaskAction.new_issue(proj_uuid=add_project)[0]
                task3 = TaskAction.new_issue(proj_uuid=add_project)[0]
                # 关联task1->task2->task3
                relate_tasks(task1, task2)
                relate_tasks(task2, task3)
                # 将task3的状态变为已完成
                trigger(task3, finish_step['uuid'])
                # 触发task1的步骤：完成任务
                trigger(task1, finish_step['uuid'])
                # 查看f1的状态，是否为进行中
                f1_info = TaskAction.task_info(f1)
                f1_info.check_response('status_uuid', target_status)
                task1_info = TaskAction.task_info(task1)
                task1_info.check_response('status_uuid', finish_step['end_status_uuid'])
        with step('清除后置动作'):
            update_post_action(finish_step, [])

    @story('T130540 任务-后置动作：添加状态联动后置动作（父工作项）（后置动作验证：无）')
    @story('T130542 子任务-后置动作：添加状态联动后置动作（父工作项）（后置动作验证：无）')
    @story('T129690 子任务-后置动作：检查状态联动后置动作事件（父工作项）（后置动作验证：无）（有父工作项）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_status_association_129690(self, add_project, typ):
        with step('完成任务-添加状态联动后置动作'):
            finish_step = get_finish_step(add_project, issue_type_name=typ)
            target_status = get_status_list(add_project, typ)['进行中']
            post_function = [
                {
                    "update_status": {
                        "target": "parent",
                        "target_range": {},
                        "target_status": target_status,
                        "validation_type": "none",
                        "validation_params": {
                            "params1": "",
                            "params2": ""
                        }
                    }
                }
            ]
            add_res = update_post_action(finish_step, post_function)
            add_res.check_response('transition.uuid', finish_step['uuid'])
        if typ.startswith('子'):
            with step('检查状态联动后置动作事件'):
                # 父任务
                f1 = TaskAction.new_issue(proj_uuid=add_project)[0]
                task1 = TaskAction.new_issue(proj_uuid=add_project, parent_uuid=f1,
                                             issue_type_name=typ)[0]
                # 触发task1的步骤：完成任务
                trigger(task1, finish_step['uuid'])
                # 查看f1的状态，是否为已完成
                f1_info = TaskAction.task_info(f1)
                f1_info.check_response('status_uuid', target_status)
                task1_info = TaskAction.task_info(task1)
                task1_info.check_response('status_uuid', finish_step['end_status_uuid'])
        with step('清除后置动作'):
            update_post_action(finish_step, [])

    @story('T130560 子任务-后置动作：添加状态联动后置动作（父工作项）（后置动作验证：子工作项）')
    @story('T129695 子任务-后置动作：检查状态联动后置动作事件（父工作项）（后置动作验证：子工作项）')
    def test_post_action_status_association_129695(self, add_project):
        typ = '子任务'
        with step('完成任务-添加状态联动后置动作'):
            finish_step = get_finish_step(add_project, issue_type_name=typ)
            target_status = get_status_list(add_project, typ)['进行中']
            post_function = [
                {
                    "update_status": {
                        "target": "parent",
                        "target_range": {},
                        "target_status": target_status,
                        "validation_type": "parent",
                        "validation_params": {
                            "param_1": "",
                            "param_2": ""
                        }
                    }
                }
            ]
            add_res = update_post_action(finish_step, post_function)
            add_res.check_response('transition.uuid', finish_step['uuid'])
        with step('检查状态联动后置动作事件'):
            # 父任务f1，子任务为task1、task2
            f1 = TaskAction.new_issue(proj_uuid=add_project)[0]
            task1 = TaskAction.new_issue(proj_uuid=add_project, parent_uuid=f1,
                                         issue_type_name=typ)[0]
            task2 = TaskAction.new_issue(proj_uuid=add_project, parent_uuid=f1,
                                         issue_type_name=typ)[0]
            # 关联task1、task2
            relate_tasks(task1, task2)
            # 将task2变为已完成
            trigger(task2, finish_step['uuid'])
            # 触发task1的步骤：完成任务
            trigger(task1, finish_step['uuid'])
            # 查看f1的状态，是否为已完成
            f1_info = TaskAction.task_info(f1)
            f1_info.check_response('status_uuid', target_status)
            task1_info = TaskAction.task_info(task1)
            task1_info.check_response('status_uuid', finish_step['end_status_uuid'])
        with step('清除后置动作'):
            update_post_action(finish_step, [])

    @story('T129719 子任务-后置动作：检查状态联动后置动作事件（父工作项）（特定后置动作验证：关联工作项）')
    def test_post_action_status_association_129719(self, add_project):
        typ = '子任务'
        with step('完成任务-添加状态联动后置动作'):
            finish_step = get_finish_step(add_project, issue_type_name=typ)
            issue_types = get_issue_types(add_project)
            post_function = [
                {
                    "update_status": {
                        "target": "parent",
                        "target_range": {},
                        "target_status": finish_step['end_status_uuid'],
                        "validation_type": "related",
                        "validation_params": {
                            "param_1": issue_types['缺陷'],
                            "param_2": issue_types['任务']
                        }
                    }
                }
            ]
            add_res = update_post_action(finish_step, post_function)
            add_res.check_response('transition.uuid', finish_step['uuid'])
        with step('检查状态联动后置动作事件'):
            # 父任务f1，子任务为task1、task2
            f1 = TaskAction.new_issue(proj_uuid=add_project)[0]
            task1 = TaskAction.new_issue(proj_uuid=add_project, parent_uuid=f1,
                                         issue_type_name=typ)[0]
            bug1 = TaskAction.new_issue(proj_uuid=add_project, issue_type_name='缺陷')[0]
            task2 = TaskAction.new_issue(proj_uuid=add_project)[0]
            # 关联task1、bug1
            relate_tasks(task1, bug1)
            # 关联bug1、task2
            relate_tasks(bug1, task2)
            # 触发task1的步骤：完成任务
            trigger(task1, finish_step['uuid'])
            # 查看f1的状态，是否为已完成
            f1_info = TaskAction.task_info(f1)
            assert f1_info.value('status_uuid') != finish_step['end_status_uuid'], '后置动作应不生效'
            # f1_info.check_response('status_uuid', target_status)
            task1_info = TaskAction.task_info(task1)
            task1_info.check_response('status_uuid', finish_step['end_status_uuid'])
        with step('清除后置动作'):
            update_post_action(finish_step, [])

    @story('T129728 子任务-后置动作：检查状态联动后置动作事件（父工作项）（特定后置动作验证：子工作项）')
    def test_post_action_status_association_129728(self, add_project):
        typ = '子任务'
        with step('完成任务-添加状态联动后置动作'):
            finish_step = get_finish_step(add_project, issue_type_name=typ)
            target_status = finish_step['end_status_uuid']
            issue_types = get_issue_types(add_project)
            post_function = [
                {
                    "update_status": {
                        "target": "parent",
                        "target_range": {},
                        "target_status": target_status,
                        "validation_type": "parent",
                        "validation_params": {
                            "param_1": issue_types['子任务'],
                            "param_2": ""
                        }
                    }
                }
            ]
            add_res = update_post_action(finish_step, post_function)
            add_res.check_response('transition.uuid', finish_step['uuid'])
        with step('检查状态联动后置动作事件'):
            # 父任务f1，子任务为task1、task2
            f1 = TaskAction.new_issue(proj_uuid=add_project)[0]
            task1 = TaskAction.new_issue(proj_uuid=add_project, parent_uuid=f1,
                                         issue_type_name=typ)[0]
            task2 = TaskAction.new_issue(proj_uuid=add_project, parent_uuid=f1,
                                         issue_type_name=typ)[0]
            # 触发task2的步骤：完成任务
            trigger(task2, finish_step['uuid'])
            # 触发task1的步骤：完成任务
            trigger(task1, finish_step['uuid'])
            # 查看f1的状态，是否为已完成
            f1_info = TaskAction.task_info(f1)
            f1_info.check_response('status_uuid', finish_step['end_status_uuid'])
            task1_info = TaskAction.task_info(task1)
            task1_info.check_response('status_uuid', finish_step['end_status_uuid'])
        with step('清除后置动作'):
            update_post_action(finish_step, [])
