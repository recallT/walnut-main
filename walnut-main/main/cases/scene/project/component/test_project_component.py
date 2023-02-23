"""
项目设置-项目组件
"""
import time
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, step
from falcons.com.nick import fixture
from main.actions.pro import PrjAction
from main.helper.extra import Extra
from main.api import project as api
from falcons.check import Checker, go
from main.cases.scene.configs.issue import IssueConfig


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


@fixture(scope='module')
def add_first_navigate(add_project):
    """添加「一级导航」组件"""
    resp = PrjAction.add_component('一级导航', project_uuid=add_project)
    parent_uuid = resp.value('components[0].uuid')
    return parent_uuid


@feature('项目设置-项目组件')
class TestComponent(Checker):
    @story("T138396 项目组件-导航自定义：添加「报表」组件")
    @story("T138438 项目组件-导航自定义：移除「报表」组件")
    @story('138352 项目组件-导航自定义-二级导航：添加「报表」组件')
    def test_add_and_del_report_form_component11(self, add_project):
        with step("添加「报表」组件"):
            response = PrjAction.add_component('报表', project_uuid=add_project, repeat=True)
            uuid = response.value("components[0].uuid")
        with step("移除 「报表」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story("T138397 项目组件-导航自定义：添加「成员」组件")
    @story("T138439 项目组件-导航自定义：移除「成员」组件")
    @story('138353 项目组件-导航自定义-二级导航：添加「成员」组件')
    def test_add_and_del_member_component(self, add_project):
        with step("添加「成员」组件"):
            response = PrjAction.add_component('成员', project_uuid=add_project, repeat=True)
            uuid = response.value("components[0].uuid")
        with step("移除 「成员」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story("T138400 项目组件-导航自定义：添加「迭代计划」组件")
    @story("T138441 项目组件-导航自定义：移除「迭代计划」组件")
    @story('138355 项目组件-导航自定义-二级导航：添加「迭代计划」组件')
    def test_add_and_del_sprint_plan_component(self, add_project):
        with step("添加「迭代计划」组件"):
            response = PrjAction.add_component('迭代计划', project_uuid=add_project, repeat=True)
            uuid = response.value("components[0].uuid")
        with step("移除「迭代计划」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story("T138401 项目组件-导航自定义：添加「迭代」组件")
    @story("T138442 项目组件-导航自定义：移除「迭代」组件")
    @story('138356 项目组件-导航自定义-二级导航：添加「迭代」组件')
    def test_add_and_del_sprint_component(self, add_project):
        response = PrjAction.add_component('迭代', project_uuid=add_project, repeat=True)
        uuid = response.value("components[0].uuid")
        with step("移除「迭代」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story("T138423 项目组件-导航自定义：添加「概览」组件")
    @story("T138454 项目组件-导航自定义：移除「概览」组件")
    def test_add_and_del_overview_component(self, add_project):
        with step("添加「概览」组件"):
            response = PrjAction.add_component('概览', project_uuid=add_project, repeat=True)
            uuid = response.value("components[0].uuid")
        with step("移除「概览」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story("T138405 项目组件-导航自定义：添加「工单」组件")
    @story("T138444 项目组件-导航自定义：拖拽移除「工单」组件")
    def test_add_and_del_work_order_component(self, add_project):
        with step("添加「工单」组件"):
            response = PrjAction.add_component('工单', project_uuid=add_project, repeat=True)
            uuid = response.value("components[0].uuid")
        with step("移除「工单」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story("T138410 项目组件-导航自定义：添加「流水线」组件")
    @story("T138447 项目组件-导航自定义：拖拽移除「流水线」组件")
    def test_add_and_del_assembly_line_component(self, add_project):
        with step("添加「流水线」组件"):
            response = PrjAction.add_component('流水线', project_uuid=add_project)
            uuid = response.value("components[0].uuid")
        with step("移除「流水线」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story("T138421 项目组件-导航自定义：添加「文档」组件")
    @story("T138452 项目组件-导航自定义：拖拽移除「文档」组件")
    def test_add_and_del_work_component(self, add_project):
        with step("添加 「文档」组件"):
            response = PrjAction.add_component('文档', project_uuid=add_project, repeat=True)
            uuid = response.value("components[0].uuid")
        with step("移除「文档」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story("T138422 项目组件-导航自定义：添加「文件」组件")
    @story("T138453 项目组件-导航自定义：拖拽移除「文件」组件")
    def test_add_and_del_file_component(self, add_project):
        with step("添加 「文件」组件"):
            response = PrjAction.add_component('文件', project_uuid=add_project)
            uuid = response.value("components[0].uuid")
        with step("移除「文件」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story("T138420 项目组件-导航自定义：添加「时间视图」组件")
    @story("T138451 项目组件-导航自定义：拖拽移除「时间视图」组件")
    def test_add_and_del_time_view_component(self, add_project):
        with step("添加「时间视图」组件"):
            response = PrjAction.add_component('时间视图', project_uuid=add_project)
            uuid = response.value("components[0].uuid")
        with step("移除「时间视图」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story("T138411 项目组件-导航自定义：添加「缺陷」组件")
    @story("T138448 项目组件-导航自定义：拖拽移除「缺陷」组件")
    def test_add_del_defect_component(self, add_project):
        with step("添加「缺陷」组件"):
            response = PrjAction.add_component('缺陷', project_uuid=add_project, repeat=True)
            uuid = response.value("components[0].uuid")
        with step("移除「缺陷」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story("T138425 项目组件-导航自定义：添加「需求」组件")
    @story("T138456 项目组件-导航自定义：拖拽移除「需求」组件")
    def test_add_del_demand_component(self, add_project):
        with step("添加「需求」组件"):
            response = PrjAction.add_component('需求', project_uuid=add_project, repeat=True)
            uuid = response.value("components[0].uuid")
        with step("移除「需求」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story("T138429 项目组件-导航自定义：添加「用户故事」组件")
    @story("T138459 项目组件-导航自定义：拖拽移除「用户故事」组件")
    def test_add_and_del_user_story(self, add_project):
        with step("添加「用户故事」组件"):
            response = PrjAction.add_component('用户故事', project_uuid=add_project)
            uuid = response.value("components[0].uuid")
        with step("移除「用户故事」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story("T138417 项目组件-导航自定义：添加「筛选器」组件")
    @story("T138450 项目组件-导航自定义：拖拽移除「筛选器」组件")
    def test_add_and_del_filter_component(self, add_project):
        with step("添加「筛选器」组件"):
            response = PrjAction.add_component('筛选器', project_uuid=add_project, repeat=True)
            uuid = response.value("components[0].uuid")
        with step("移除「筛选器」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story('138424 项目组件-导航自定义：添加「项目计划」组件')
    @story("T138455 项目组件-导航自定义：拖拽移除「项目计划」组件")
    def test_add_and_del_project_plan(self, add_project):
        with step("添加「项目计划」组件"):
            response = PrjAction.add_component('项目计划', project_uuid=add_project, repeat=True)
            uuid = response.value("components[0].uuid")
        with step("移除「项目计划」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story("T138402 项目组件-导航自定义：添加「发布」组件")
    @story("T138443 项目组件-导航自定义：拖拽移除「发布」组件")
    def test_add_release_component(self, add_project):
        with step("添加「发布」组件"):
            response = PrjAction.add_component('发布', project_uuid=add_project, repeat=True)
            uuid = response.value("components[0].uuid")
        with step("移除「项目计划」组件"):
            PrjAction.remove_prj_component_by_uuid(uuid, project_uuid=add_project)

    @story("T138433 项目组件-导航自定义：添加「自定义工作项类型」组件")
    @story("T138461 项目组件-导航自定义：拖拽移除「自定义工作项类型」组件")
    def test_add_and_del_custom_type_component(self, add_project):
        with step("先新建一个 工作项类型"):
            name, uuid = IssueConfig.global_issue_add()
        with step("添加到 自定义导航栏中"):
            response = PrjAction.add_component(name, project_uuid=add_project, repeat=True)
            component_uuid = response.value("components[0].uuid")
        with step("移除该组件"):
            PrjAction.remove_prj_component_by_uuid(component_uuid, project_uuid=add_project)

    #  ---------二级导航--------

    @story("T138382 项目组件-导航自定义-二级导航：添加「需求」组件，检查组件详情默认态")
    def test_secondary_navigation_demand(self, add_project, add_first_navigate):
        with step("把「需求组件添加到一级导航栏」"):
            resp = PrjAction.add_component('需求', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
            resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138379 项目组件-导航自定义-二级导航：添加「项目计划」组件")
    def test_secondary_navigation_project_plan(self, add_project, add_first_navigate):
        with step("把「项目计划」组件 添加到 一级导航栏"):
            resp = PrjAction.add_component('项目计划', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
            resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138368 项目组件-导航自定义-二级导航：添加「缺陷」组件，检查组件详情默认态")
    def test_secondary_navigation_defect(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('缺陷', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138365 项目组件-导航自定义-二级导航：添加「流水线」组件")
    def test_secondary_navigation_assembly_line(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('流水线', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138374 项目组件-导航自定义-二级导航：添加「筛选器」组件，检查组件详情默认态")
    def test_secondary_navigation_filter(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('筛选器', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138375 项目组件-导航自定义-二级导航：添加「时间视图」组件")
    def test_secondary_navigation_time_view(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('时间视图', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138376 项目组件-导航自定义-二级导航：添加「文档」组件")
    def test_secondary_navigation_word(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('文档', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138377 项目组件-导航自定义-二级导航：添加「文件」组件")
    def test_secondary_navigation_file(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('文件', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138385 项目组件-导航自定义-二级导航：添加「用户故事」组件，检查组件详情默认态")
    def test_secondary_navigation_user_story(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('用户故事', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138386 项目组件-导航自定义-二级导航：添加「执行」组件")
    def test_secondary_navigation_implement(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('执行', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story('138409 项目组件-导航自定义：添加「里程碑」组件')
    @story("T138364 项目组件-导航自定义-二级导航：添加「里程碑」组件")
    def test_secondary_navigation_milestone(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('里程碑', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138363 项目组件-导航自定义-二级导航：添加「交付物」组件")
    def test_secondary_navigation_deliverables(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('交付物', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138354 项目组件-导航自定义-二级导航：添加「待办事项」组件")
    def test_secondary_navigation_todo(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('待办事项', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138359 项目组件-导航自定义-二级导航：添加「发布」组件，检查组件详情默认态")
    def test_secondary_navigation_release(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('发布', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138359 项目组件-导航自定义-二级导航：添加「迭代计划」组件")
    def test_secondary_navigation_release(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('迭代计划', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138352 项目组件-导航自定义-二级导航：添加「报表」组件")
    def test_secondary_navigation_report(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('报表', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138353 项目组件-导航自定义-二级导航：添加「成员」组件")
    def test_secondary_navigation_member(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('成员', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138355 项目组件-导航自定义-二级导航：添加「迭代计划」组件")
    def test_secondary_navigation_sprint_plan(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('迭代计划', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138356 项目组件-导航自定义-二级导航：添加「迭代」组件")
    def test_secondary_navigation_sprint(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('迭代', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138371 项目组件-导航自定义-二级导航：添加「任务」组件，检查组件详情默认态")
    def test_secondary_navigation_task(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('任务', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138390 项目组件-导航自定义-二级导航：添加「自定义链接」组件")
    @story('138436 项目组件-导航自定义：添加「自定义链接」组件')
    def test_secondary_navigation_custom_links(self, add_project, add_first_navigate):
        resp, response = PrjAction.add_customize_component(is_param=True, project_uuid=add_project)
        resp.uri_args({'project_uuid': add_project})
        resp.json_update('components[0].parent_uuid', add_first_navigate)
        resp.json['components'] += response
        go(api.ComponentsAdd, resp)

    @story("T138389 项目组件-导航自定义-二级导航：添加「自定义工作项类型」组件，检查组件详情默认态")
    def test_secondary_navigation_custom_type(self, add_project, add_first_navigate):
        with step("先新建一个 工作项类型"):
            name, uuid = IssueConfig.global_issue_add()
        with step("把该组件 添加到「一级导航」下"):
            resp = PrjAction.add_component(name, project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
            resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138378 项目组件-导航自定义-二级导航：添加「概览」组件")
    def test_secondary_navigation_overview(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('概览', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)

    @story("T138362 项目组件-导航自定义-二级导航：添加「工单」组件，检查组件详情默认态")
    def test_secondary_navigation_work_order(self, add_project, add_first_navigate):
        resp = PrjAction.add_component('工单', project_uuid=add_project, repeat=True, parent_uuid=add_first_navigate)
        resp.check_response('components[0].parent_uuid', add_first_navigate)
