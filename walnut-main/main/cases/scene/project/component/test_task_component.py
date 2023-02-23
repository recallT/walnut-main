#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_issue_role_config.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/7 
@Desc    ：项目设置-项目组件-任务组件配置
"""
import time

from falcons.check import go
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, parametrize, step
from falcons.com.nick import fixture

from main.actions import task
from main.actions.pro import PrjAction
from main.actions.task import team_stamp
from main.api import project
from main.api.project import ProjectStamp
from main.helper.extra import Extra
from main.params import component as cpm, data
from main.params import proj, conf
from main.params.devops import component_stamp


@fixture(scope='module', autouse=True)
def add_project():
    # 创建一个单独项目
    time.sleep(2)
    creator = Extra(ApiMeta)
    p_id = creator.new_project(f'组件测试test')
    return p_id


@fixture(scope='module', autouse=True)
def del_project(add_project):
    yield
    # 清除项目数据
    creator = Extra(ApiMeta)
    creator.del_project(add_project)


@fixture(scope='module', autouse=True)
def add_task_component(add_project):
    """新增任务组件，并返回请求参数"""
    p_id = add_project
    add_param = proj.proj_stamp()[0]
    add_param.uri_args({'project_uuid': p_id})
    component_stamp = go(project.ProjectStamp, add_param, is_print=False)
    exist_components = [{'uuid': c['uuid'], 'template_uuid': c['template_uuid']}
                        for c in component_stamp.value('component.components')]

    task_param = PrjAction.add_task_component(is_param=True)
    task_param.json['components'] += exist_components  # 添加上原有组件
    task_param.uri_args({'project_uuid': p_id})
    resp = go(project.ComponentsAdd, task_param)

    return task_param


@feature('项目设置-项目组件-组件配置详情')
class TestComponentTask:
    """任务组件配置详情"""

    @story('134576 任务组件配置-公共视图：公共视图列表检查')
    @parametrize('param', cpm.comp_default_view())
    def test_task_com_layout(self, param):
        """"""
        v_param = cpm.new_comp_view()[0]

        stamp = task.team_stamp({'issue_type_config': 0})

        i = task.global_issue_type()

    @story('134584 任务组件配置-基础设置：修改组件显示名称')
    def test_del_task_com_layout(self, add_task_component, add_project):
        with step('任务组件配置-基础设置：修改组件显示名称'):
            task_param = add_task_component
            task_param.json_update('components[0].name', '示例任务组件')
            task_param.uri_args({'project_uuid': add_project})
            resp_name = go(project.UpdateComponents, task_param)
            resp_name.check_response('components[0].name', '示例任务组件')

    @story('T134583 任务组件配置-基础设置：修改组件描述')
    def test_update_task_desc(self, add_task_component, add_project):
        with step('任务组件配置-基础设置：修改组件描述'):
            task_param = add_task_component
            task_param.json_update('components[0].desc', '示例任务组件描述修改哈哈哈哈哈哈哈')
            task_param.uri_args({'project_uuid': add_project})
            resp_desc = go(project.UpdateComponents, task_param)
            resp_desc.check_response('components[0].desc', '示例任务组件描述修改哈哈哈哈哈哈哈')

    @story('T134577 任务组件配置-公共视图：删除公共视图')
    def test_del_task__com_layout(self, add_task_component, add_project):
        with step('任务组件配置-公共视图：删除公共视图'):
            task_param = add_task_component
            views = task_param.json['components'][0]['views']
            del views[0]
            task_param.json_update('components[0].views', views)
            task_param.uri_args({'project_uuid': add_project})
            resp = go(project.UpdateComponents, task_param)
            assert len(resp.value('components[0].views')) == len(views)

    @story('T134589 任务组件配置-组件权限-查看权限：添加成员域（部门）')
    @story('T134590 任务组件配置-组件权限-查看权限：添加成员域（成员）')
    def test_add_task_permissions_member(self, add_task_component, add_project):
        # 查询系统内存在的member 成员uuid
        su_param = proj.program_search_user()[0]
        resp_user_uuid = go(project.UsesSearch, su_param).value('users[0].uuid')
        with step('添加成员域（成员）'):
            task_param = add_task_component
            permissions = task_param.json['components'][0]['permissions'][0]['user_domains'] = []
            permissions.append({'user_domain_type': "single_user", 'user_domain_param': resp_user_uuid})
            task_param.uri_args({'project_uuid': add_project})
            resp_permissions = go(project.UpdateComponents, task_param)
            resp_permissions.check_response('components[0].project_uuid', add_project)
        with step('查看权限成员域，移除成员域（成员）'):
            del permissions[0]
            task_param.uri_args({'project_uuid': add_project})
            resp_permissions = go(project.UpdateComponents, task_param)
            resp_permissions.check_response('components[0].project_uuid', add_project)

    @story('T134591 T134599任务组件配置-组件权限-查看权限：添加成员域（特殊角色-所有人）')
    def test_add_task_permissions_everyone(self, add_task_component, add_project):
        with step('查看权限成员域添加所有人'):
            task_param = add_task_component
            permissions = task_param.json['components'][0]['permissions'][0]['user_domains'] = []
            permissions.append({'user_domain_type': "everyone", 'user_domain_param': ""})
            task_param.uri_args({'project_uuid': add_project})
            resp_permissions = go(project.UpdateComponents, task_param)
            resp_permissions.check_response('components[0].project_uuid', add_project)
        with step('查看权限成员域，移除特殊角色-所有人'):
            del permissions[0]
            task_param.uri_args({'project_uuid': add_project})
            resp_permissions = go(project.UpdateComponents, task_param)
            resp_permissions.check_response('components[0].project_uuid', add_project)

    @story('T134592 T134600 任务组件配置-组件权限-查看权限：添加成员域（特殊角色-项目负责人）')
    def test_add_task_permissions_project_assign(self, add_task_component, add_project):
        with step('查看权限成员域，添加项目负责人'):
            task_param = add_task_component
            permissions = task_param.json['components'][0]['permissions'][0]['user_domains'] = []
            permissions.append({'user_domain_type': "project_assign", 'user_domain_param': ""})
            task_param.uri_args({'project_uuid': add_project})
            resp_permissions = go(project.UpdateComponents, task_param)
            resp_permissions.check_response('components[0].project_uuid', add_project)
        with step('查看权限成员域，移除特殊角色-项目负责人'):
            del permissions[0]
            task_param.uri_args({'project_uuid': add_project})
            resp_permissions = go(project.UpdateComponents, task_param)
            resp_permissions.check_response('components[0].project_uuid', add_project)

    @story('T134593 T134601 任务组件配置-组件权限-查看权限：添加成员域（特殊角色-项目管理员）')
    def test_add_task_permissions_project_administrators(self, add_task_component, add_project):
        with step('查看权限成员域，添加项目管理员'):
            task_param = add_task_component
            permissions = task_param.json['components'][0]['permissions'][0]['user_domains'] = []
            permissions.append({'user_domain_type': "project_administrators", 'user_domain_param': ""})
            task_param.uri_args({'project_uuid': add_project})
            resp_permissions = go(project.UpdateComponents, task_param)
            resp_permissions.check_response('components[0].project_uuid', add_project)
        with step('查看权限成员域，移除特殊角色-项目管理员'):
            del permissions[0]
            task_param.uri_args({'project_uuid': add_project})
            resp_permissions = go(project.UpdateComponents, task_param)
            resp_permissions.check_response('components[0].project_uuid', add_project)

    @story('T134596 T134604任务组件配置-组件权限-查看权限：添加成员域（用户组）')
    def test_add_task_permissions_group(self, add_task_component, add_project):
        # 新增用户组
        param = data.user_group_add()[0]
        resp = go(project.UsesGroupAdd, param)
        group_uuid = resp.value('uuid')
        with step('查看权限成员域，添加示例用户组'):
            task_param = add_task_component
            permissions = task_param.json['components'][0]['permissions'][0]['user_domains'] = []
            permissions.append({'user_domain_type': "group", 'user_domain_param': group_uuid})
            task_param.uri_args({'project_uuid': add_project})
            resp_permissions = go(project.UpdateComponents, task_param)
            resp_permissions.check_response('components[0].project_uuid', add_project)
        with step('查看权限成员域，移除用户组权限'):
            del permissions[0]
            task_param.uri_args({'project_uuid': add_project})
            resp_permissions = go(project.UpdateComponents, task_param)
            resp_permissions.check_response('components[0].project_uuid', add_project)
        with step('清除用户组数据'):
            param.uri_args({'group_uuid': group_uuid})
            go(project.UsesGroupDelete, param, with_json=False)

    @story('T134598 任务组件配置-组件权限-查看权限：移除成员域（成员）')
    def test_del_task_permissions(self, add_task_component, add_project):
        with step('移除成员域（成员）'):
            task_param = add_task_component
            permissions = task_param.json['components'][0]['permissions'][0]['user_domains']
            if len(permissions) != 0:
                del permissions[0]
                task_param.uri_args({'project_uuid': add_project})
                resp_permissions = go(project.UpdateComponents, task_param)
                resp_permissions.check_response('components[0].project_uuid', add_project)

    @story('T138428 T138437 项目组件-导航自定义：添加「一级导航」组件')
    def test_add_component_primary_navigation(self, add_project):
        with step('在组件库中将「一级导航」组件拖拽至导航自定义中'):
            resp = PrjAction.add_component('一级导航', project_uuid=add_project)
            parent_uuid = resp.value('components[0].uuid')

        with step('删除一级导航组件'):
            PrjAction.remove_prj_component_by_uuid(component_uuid=parent_uuid, project_uuid=add_project)

    @story('T138414 项目组件-导航自定义：添加「任务」组件')
    @story('T138449 项目组件-导航自定义：拖拽移除「任务」组件')
    @story('134582 任务组件配置-基础设置：通过按钮移除任务组件')
    def test_add_component_task(self, add_project):
        with step("在组件库中将「任务」组件拖拽至导航自定义中"):
            response = PrjAction.add_task_component(project_uuid=add_project)
            uuid = response.value("components[0].uuid")
        with step("移除「任务」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story('T138395 项目组件-导航自定义-二级导航：添加「任务」组件，检查组件详情默认态')
    @story('138371 项目组件-导航自定义-二级导航：添加「任务」组件，检查组件详情默认态')
    @story('143666 一级导航中添加二级导航')
    def test_add_sub_components(self, add_project):
        with step('在组件库中将「一级导航」组件拖拽至导航自定义中'):
            resp = PrjAction.add_component('一级导航', project_uuid=add_project)
            # 一级导航组件UUID
            uuid = resp.value('components[0].uuid')
            component_param = proj.proj_stamp()[0]
            component_param.uri_args({'project_uuid': add_project})
            component_stamp = go(project.ProjectStamp, component_param, is_print=False)
            # components = component_stamp.value('component.components')
            exist_components = [{'uuid': c['uuid'], 'template_uuid': c['template_uuid']}
                                for c in component_stamp.value('component.components')]
        with step('在组件库中将「任务」组件拖拽至二级导航中'):
            task_param = PrjAction.add_task_component(is_param=True, project_uuid=add_project)
            task_param.json_update('components[0].parent_uuid', uuid)
            task_param.json['components'] += exist_components  # 添加上原有组件
            task_param.uri_args({'project_uuid': add_project})
            resp = go(project.ComponentsAdd, task_param)
            resp.check_response('components[0].parent_uuid', uuid)

    @story('138393 项目组件-导航自定义：调整一级导航栏顺序')
    def test_sort_component(self, add_project):
        component_param = proj.proj_stamp()[0]
        component_param.uri_args({'project_uuid': add_project})
        component_stamp = go(project.ProjectStamp, component_param, is_print=False)
        exist_components = [{'uuid': c['uuid'], 'parent_uuid': '', 'template_uuid': c['template_uuid']}
                            for c in component_stamp.value('component.components')]
        # 更换位置
        exist_components[2], exist_components[4] = exist_components[4], exist_components[2]

        params = proj.add_task_component()[0]
        params.json_update('components', exist_components)
        params.uri_args({'project_uuid': add_project})
        resp = go(project.ComponentSort, params)
        resp.check_response('components[4].uuid', exist_components[4]['uuid'])
        resp.check_response('components[2].uuid', exist_components[2]['uuid'])

    @story('T138391 项目组件-导航自定义-二级导航：无法添加「一级导航」组件')
    def test_add_primary_navigation_sub_component(self, add_project):
        with step('在组件库中将「一级导航」组件拖拽至导航自定义中'):
            resp = PrjAction.add_component('一级导航', project_uuid=add_project)
            uuid = resp.value('components[0].uuid')
            component_param = proj.proj_stamp()[0]
            component_param.uri_args({'project_uuid': add_project})
            component_stamp = go(project.ProjectStamp, component_param, is_print=False)
            exist_components = [{'uuid': c['uuid'], 'template_uuid': c['template_uuid']}
                                for c in component_stamp.value('component.components')]

        with step('在组件库中将「一级导航」组件拖拽至二级导航中'):
            params = proj.add_primary_navigation()[0]
            params.json_update('components[0].parent_uuid', uuid)
            params.json['components'] += exist_components
            params.uri_args({'project_uuid': add_project})
            go(project.ComponentsAdd, params, status_code=400)

    @story('T138468 项目组件-组件库：搜索组件')
    def test_component_template(self):
        template_obj = go(project.TeamStampData, conf.project_isu_template()[0])
        components = template_obj.value('component_template.templates')
        with step('搜索通用组件，搜索框输入：一级导航'):
            navigation_uuid = [c['uuid'] for c in components if c['name'] == '一级导航']
            assert len(navigation_uuid) == 1
        with step('搜索系统组件，搜索框输入：工单'):
            navigation_uuid = [c['uuid'] for c in components if c['name'] == '工单']
            assert len(navigation_uuid) == 1
        with step('搜索系统组件，搜索框输入：xxxxxxxx 不存在'):
            navigation_uuid = [c['uuid'] for c in components if c['name'] == 'xxxxxxxx']
            assert len(navigation_uuid) == 0

    @story('T138469 项目组件-组件库：组件库列表检查')
    def test_component_template_list(self):
        template_obj = task.team_stamp({'component_template': 0})

        default_template = {'一级导航', '概览', '成员', '报表', '文档', '迭代', '筛选器', '迭代计划', '项目计划', '执行', '里程碑',
                            '交付物', '流水线', '文件', '待办事项', '子需求', '子任务', '需求', '缺陷', '任务'}

        template_name_list = [r['name'] for r in template_obj['component_template']['templates']]
        assert set(template_name_list) >= default_template

    @story('T138452 项目组件-导航自定义：拖拽移除「文档」组件')
    def test_del_component(self, add_project):
        with step('删除文档组件'):
            PrjAction.remove_prj_component('文档', project_uuid=add_project)

    @story('T138432 项目组件-导航自定义：添加「执行」组件')
    @story('T138460 拖拽移除「执行」组件')
    def test_add_implement_component(self, add_project):
        with step('添加「执行」组件'):
            resp = PrjAction.add_component('执行', project_uuid=add_project)
            parent_uuid = resp.value('components[0].uuid')

        with step('拖拽移除「执行」组件'):
            PrjAction.remove_prj_component_by_uuid(component_uuid=parent_uuid, project_uuid=add_project)

    @story('T138402 项目组件-导航自定义：添加「发布」组件')
    @story('T138443 项目组件-导航自定义：拖拽移除「发布」组件')
    def test_add_deploy_component(self, add_project):
        with step('添加「发布」组件'):
            response = PrjAction.add_component('发布', project_uuid=add_project, repeat=True)
            uuid = response.value("components[0].uuid")
        with step('拖拽移除「发布」组件'):
            PrjAction.remove_prj_component_by_uuid(component_uuid=uuid, project_uuid=add_project)

    @story('T138398 项目组件-导航自定义：添加「待办事项」组件')
    @story('138440 项目组件-导航自定义：拖拽移除「待办事项」组件')
    def test_add_and_del_todo_component(self, add_project):
        with step('在组件库中将「待办事项」组件拖拽至导航自定义中'):
            PrjAction.add_component('待办事项')
        with step('删除待办组件'):
            PrjAction.remove_prj_component('待办事项', project_uuid=add_project)

    @story('T138445 项目组件-导航自定义：添加「交付物」组件')
    @story('T138408 拖拽移除「交付物」组件')
    def test_add_and_del_deliverables_component(self, add_project):
        with step("添加交付物组件"):
            # PrjAction.add_deliverables_component(project_uuid=add_project)
            PrjAction.add_component('交付物')
        with step('拖拽移除「交付物」组件'):
            PrjAction.remove_prj_component('交付物', project_uuid=add_project)

    @story('138446 添加「里程碑」组件/拖拽移除「里程碑」组件')
    def test_add_and_del_milestone_component(self, add_project):
        with step('添加「里程碑」组件'):
            PrjAction.add_component(component_name='里程碑',project_uuid=add_project)
        with step('拖拽移除「里程碑」组件'):
            PrjAction.remove_prj_component('里程碑', project_uuid=add_project)

    @story("T134595 任务组件配置-组件权限-查看权限：添加成员域（项目角色-项目成员）")
    @story("T134603 任务组件配置-组件权限-查看权限：移除成员域（项目角色-项目成员）")
    def test_add_task_permissions_project_role(self, add_task_component, add_project):
        resp = team_stamp({'role': 0})
        proj_uuid = [p['uuid'] for p in resp['role']['roles'] if p['name'] == '项目成员'][0]
        with step('查看权限成员域添加「项目角色」'):
            task_param = add_task_component
            # 先将新建的任务组件把 「查看权限」成员域定义为空
            permissions = task_param.json['components'][0]['permissions'][0]['user_domains'] = []
            permissions.append({'user_domain_type': "role", 'user_domain_param': proj_uuid})
            task_param.uri_args({'project_uuid': add_project})
            resp_permissions = go(project.UpdateComponents, task_param)
            resp_permissions.check_response('components[0].project_uuid', add_project)
        with step('查看权限成员域，移除 项目角色'):
            del permissions[0] # 删除刚刚添加的 成员域
            task_param.uri_args({'project_uuid': add_project})
            resp_permissions = go(project.UpdateComponents, task_param)
            resp_permissions.check_response('components[0].project_uuid', add_project)

# 2022/7/29
    @story("T134581 任务组件配置-基础设置：检查基础设置展示信息")
    def test_inspect_basic_settings_information(self):
        param = component_stamp()[0]
        resp = go(ProjectStamp, param)
        response = resp.value('component.components')

        name = [p['name'] for p in response if p['template_uuid'] == 'com00003']
        # desc = [p['desc'] for p in response if p['template_uuid'] == 'com00003']

        assert '任务' in name
