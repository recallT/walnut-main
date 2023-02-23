# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_issue_permission_list.py
@Author  ：zhangyonghui@ones.ai
@Date    ：7/22/22 2:46 PM 
@Desc    ：工作项权限-权限列表
"""
from falcons.check import Checker
from falcons.com.nick import story, parametrize, step, feature, mark

from main.actions.pro import PrjAction
from main.actions.task import team_stamp


@mark.smoke
@feature('Project 配置中心')
class TestIssuePermissionList(Checker):

    @story('T131793 缺陷-工作项权限：缺陷权限列表（汇总模式下）')
    @story('T131795 缺陷-工作项权限：缺陷权限列表（简单模式下）')
    @parametrize('configs', ['detailed', 'simple'])
    def test_check_defect_permission_list(self, configs):
        with step('切换成汇总/简单模式'):
            PrjAction.work_hour_configs_update(configs)
        with step('工作项权限配置查看权限列表，默认按照一下顺序暂时'):
            stamp_resp = team_stamp({"issue_type": 0})
            default_perm = [p['permission'] for c in stamp_resp['issue_type']['issue_types'] if c['name'] == '缺陷'
                            for p in c['default_configs']['default_permission']]

            d_perm = []
            [d_perm.append(i) for i in default_perm if i not in d_perm]  # 去重
            assert d_permission == d_perm

    @story('T139203 需求-工作项权限：需求权限列表（汇总模式下）')
    @story('T139206 需求-工作项权限：需求权限列表（简单模式下）')
    @parametrize('configs', ['detailed', 'simple'])
    def test_check_demand_permission_list(self, configs):
        with step('切换成汇总/简单模式'):
            PrjAction.work_hour_configs_update(configs)
        with step('工作项权限配置查看权限列表，默认按照一下顺序暂时'):
            stamp_resp = team_stamp({"issue_type": 0})
            default_perm = [p['permission'] for c in stamp_resp['issue_type']['issue_types'] if c['name'] == '需求'
                            for p in c['default_configs']['default_permission']]

            d_perm = []
            [d_perm.append(i) for i in default_perm if i not in d_perm]  # 去重
            assert d_permission == d_perm

    @story('T140552 用户故事-工作项权限：用户故事权限列表（汇总模式下）')
    @story('T140555 用户故事-工作项权限：用户故事权限列表（简单模式下）')
    @parametrize('configs', ['detailed', 'simple'])
    def test_check_user_story_permission_list(self, configs):
        with step('切换成汇总/简单模式'):
            PrjAction.work_hour_configs_update(configs)
        with step('工作项权限配置查看权限列表，默认按照一下顺序暂时'):
            stamp_resp = team_stamp({"issue_type": 0})
            default_perm = [p['permission'] for c in stamp_resp['issue_type']['issue_types'] if c['name'] == '用户故事'
                            for p in c['default_configs']['default_permission']]

            d_perm = []
            [d_perm.append(i) for i in default_perm if i not in d_perm]  # 去重
            assert d_permission == d_perm

    @story('T142057 子检查项-工作项权限：子检查项权限列表（汇总模式下）')
    @story('T142059 子检查项-工作项权限：子检查项权限列表（简单模式下）')
    @parametrize('configs', ['detailed', 'simple'])
    def test_check_child_check_permission_list(self, configs):
        with step('切换成汇总/简单模式'):
            PrjAction.work_hour_configs_update(configs)
        with step('工作项权限配置查看权限列表，默认按照一下顺序暂时'):
            stamp_resp = team_stamp({"issue_type": 0})
            default_perm = [p['permission'] for c in stamp_resp['issue_type']['issue_types'] if c['name'] == '子检查项'
                            for p in c['default_configs']['default_permission']]

            d_perm = []
            [d_perm.append(i) for i in default_perm if i not in d_perm]  # 去重
            assert d_permission == d_perm

    @story('T142431 子需求-工作项权限：子需求权限列表（汇总模式下）')
    @story('T142432 子需求-工作项权限：子需求权限列表（简单模式下）')
    @parametrize('configs', ['detailed', 'simple'])
    def test_check_sub_demand_permission_list(self, configs):
        with step('切换成汇总/简单模式'):
            PrjAction.work_hour_configs_update(configs)
        with step('工作项权限配置查看权限列表，默认按照一下顺序暂时'):
            stamp_resp = team_stamp({"issue_type": 0})
            default_perm = [p['permission'] for c in stamp_resp['issue_type']['issue_types'] if c['name'] == '子需求'
                            for p in c['default_configs']['default_permission']]

            d_perm = []
            [d_perm.append(i) for i in default_perm if i not in d_perm]  # 去重
            assert d_permission == d_perm

    @story('T120546 发布-工作项权限：发布权限列表（汇总模式下）')
    @story('T120549 发布-工作项权限：发布权限列表（简单模式下）')
    @parametrize('configs', ['detailed', 'simple'])
    def test_check_deploy_permission_list(self, configs):
        with step('切换成汇总/简单模式'):
            PrjAction.work_hour_configs_update(configs)
        with step('工作项权限配置查看权限列表，默认按照一下顺序暂时'):
            stamp_resp = team_stamp({"issue_type": 0})
            default_perm = [p['permission'] for c in stamp_resp['issue_type']['issue_types'] if c['name'] == '发布'
                            for p in c['default_configs']['default_permission']]

            d_perm = []
            [d_perm.append(i) for i in default_perm if i not in d_perm]  # 去重
            assert d_permission == d_perm

    @story('T121582 工单-工作项权限：工单权限列表（汇总模式下）')
    @story('T121585 工单-工作项权限：工单权限列表（简单模式下）')
    @parametrize('configs', ['detailed', 'simple'])
    def test_check_deploy_permission_list(self, configs):
        with step('切换成汇总/简单模式'):
            PrjAction.work_hour_configs_update(configs)
        with step('工作项权限配置查看权限列表，默认按照一下顺序暂时'):
            stamp_resp = team_stamp({"issue_type": 0})
            default_perm = [p['permission'] for c in stamp_resp['issue_type']['issue_types'] if c['name'] == '工单'
                            for p in c['default_configs']['default_permission']]

            d_perm = []
            [d_perm.append(i) for i in default_perm if i not in d_perm]  # 去重
            assert d_permission == d_perm


d_permission = ['create_tasks', 'view_tasks', 'update_tasks', 'delete_tasks', 'transit_tasks', 'be_assigned',
                'export_tasks',
                'update_task_watchers', 'manage_task_assess_manhour', 'manage_task_record_manhours',
                'manage_task_own_record_manhours',
                'manage_task_own_assess_manhour']
