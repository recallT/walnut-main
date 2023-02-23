import time

from falcons.com.meta import ApiMeta
from falcons.com.nick import story, feature, parametrize, fixture, step
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from main.actions.pro import PrjAction
from main.actions.team import TeamAction
from main.api.project import ProjectComponent
from main.api.view import UserView, ViewDelete
from main.params.proj import ui_prj_name, my_project_list, user_view, delete_view
from selenium.webdriver.support import expected_conditions as EC


# 删除自建视图数据
@fixture(scope='module', autouse=True)
def _del_view():
    yield
    # 查项目组件的uuid
    p = my_project_list()[0]
    gq = ProjectComponent()
    gq.call(**p.extra)
    gq.is_response_code(200)

    component_uuid = gq.json()['components'][0]['uuid']

    # 查询自建视图类型：公共视图，uuid
    p_view = user_view()[0]
    p_view.uri_args({'component_uuid': component_uuid})

    q_view = UserView()
    q_view.call(**p_view.extra)
    q_view.is_response_code(200)

    views = [v['uuid'] for v in q_view.json()['views'] if v['group_by'] == '' and v['built_in'] == True]

    # 删除视图
    p_del = delete_view()[0]
    q_del = ViewDelete()
    for view in views:
        p_del.uri_args({'component_uuid': component_uuid, 'view_uuid': view})
        q_del.call(**p_del.extra)
        q_del.is_response_code(200)


@feature('项目列表操作')
class TestProListOpt:

    @story('137996 按项目负责人分组搜索')
    @story('138003 项目列表-分组：不分组')
    def test_group(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        # 先清除左下角消息通知

        # 按项目负责人分组
        time.sleep(1)
        prj.main_page.bar.group_by('项目负责人')
        prj.main_page.assert_page_contains('关闭分组')

        # 关闭分组
        prj.main_page.click_content('关闭分组')
        # prj.main_page.assert_page_contains('不分组')

    @parametrize('data', ui_prj_name())
    @story('138251 项目搜索')
    def test_pro_search(self, data, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')

        # 根据条件搜索
        prj.main_page.main_search_input('搜索项目名称、状态、负责人', data)

        if data != 'NoTestData':
            prj.main_page.assert_page_contains(data)
        else:
            prj.main_page.assert_page_contains('暂无匹配结果')

    @story('138257 置顶项目')
    def test_topping_pro(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')

        prj.main_page.main_search_input('搜索项目名称、状态、负责人', prj.proj_name)

        # 置顶初始化项目
        prj.main_page.click_topping(prj.proj_name)
        # 检查
        prj.main_page.assert_page_contains('已置顶')

    @story('138255 取消置顶项目')
    def test_cancel_topping(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')

        prj.main_page.click_cancel_topping(prj.proj_name)
        prj.main_page.assert_page_contains('已取消置顶')

    @story('138213 新建视图')
    @story('134226 任务管理-搜索：选中全部进行搜索')
    def test_add_view(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')

        prj.main_page.click_page_link('视图管理')
        prj.main_page.click_button('新建视图')
        prj.main_page.input('视图名称', '视图TEST')
        # 视图权限：公共
        prj.pop_up.view_permission_select('公共')
        prj.main_page.click_button('确定')

        # toast提示
        prj.main_page.assert_page_contains('添加视图成功')
        # 校验弹框关闭，定位到新视图页面
        prj.main_page.assert_page_contains('视图TEST')

    @story('T138252 项目列表：表格布局')
    def test_table_layout(self, project_page):
        with step('清除项目：敏捷项目'):
            projects = PrjAction.get_all_projects()
            for p in projects:
                if p['name'] == '敏捷项目':
                    PrjAction.delete_project(p['uuid'])
        with step('创建两个敏捷项目'):
            for i in range(2):
                PrjAction.new_project(index=3)
        with step('检查是不是table'):
            prj = project_page
            prj.side_bar.nav_to('项目管理')
            el_table = prj.driver.find_element('//div[contains(@class, "project-table")]')
            assert el_table
            prj.main_page.assert_page_contains('项目名称')
            prj.main_page.assert_page_contains('项目状态')
            prj.main_page.assert_page_contains('项目负责人')
            prj.main_page.assert_page_contains('工作项完成度')
            prj.main_page.assert_page_contains('迭代数量')

    @story('T138254 项目列表：卡片布局')
    def test_card_layout(self, project_page):
        with step('检查是不是卡片'):
            prj = project_page

            def is_exist(loc: str):
                try:
                    elem = prj.driver.find_element(loc)
                    return elem
                except Exception as e:
                    return None

            prj.side_bar.nav_to('项目管理')
            more = is_exist('//div[contains(@class, "more-op")]/span[text()="更多"]')
            if more:
                more.click()
                time.sleep(2)
            layout = is_exist('//*[text()="布局"]')
            if layout:
                prj.driver.find_element('//*[text()="布局"]/following-sibling::*[1]').click()
                prj.driver.find_element('//li[text()="卡片"]').click()
                time.sleep(2)

            prj.main_page.assert_page_contains('敏捷项目')
            prj.main_page.assert_page_contains('未完成工作项趋势')
            prj.main_page.assert_page_contains('最近工作项更新于')