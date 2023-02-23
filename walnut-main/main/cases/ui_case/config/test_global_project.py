"""
@File    ：test_global_project.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/6/23
@Desc    ： 全局配置-项目配置UI 用例
"""
from falcons.com.nick import feature, story, step

from main.cases.ui_case.links import full_link, ConfigPrjUrlLinks as Pl


@feature('全局配置-项目配置')
class TestGlobalProject:

    @story('T137955 项目角色：列表检查')
    def test_role_list(self, project_page):
        project_page.driver.go_to(full_link(Pl.ROLE_CONFIG))
        project_page.main_page.assert_page_contains('角色')
        project_page.main_page.assert_page_contains('使用到的项目')
        project_page.main_page.assert_page_contains('操作')

    @story('T131556 全局项目配置 - 项目状态：列表检查')
    def test_project_status(self, project_page):
        project_page.driver.go_to(full_link(Pl.PROJECT_STATUS))
        # 状态名称、状态类型、使用到的项目、操作
        project_page.main_page.assert_page_contains('状态名称')
        project_page.main_page.assert_page_contains('状态类型')
        project_page.main_page.assert_page_contains('使用到的项目')
        project_page.main_page.assert_page_contains('操作')


@feature('全局配置-项目配置')
class TestGlobalProjectIssueType:
    """工作项类型开箱检查"""

    @story('T117775 步骤属性：检查缺陷工作项类型步骤属性开箱')
    def test_defect_status(self, project_page):
        with step('进入工作项属性配置页面'):
            project_page.driver.go_to(full_link(Pl.ISSUE_TYPE))

        project_page.main_page.multiple_content('缺陷', 3)
        project_page.main_page.click_content('工作项工作流')
        project_page.main_page.click_content('详情视图')

        with step('查看开箱步骤属性：未激活 --> 已确认'):
            ...
            # project_page.main_page.click_content()

        # 状态名称、状态类型、使用到的项目、操作
        # project_page.main_page.assert_page_contains('状态名称')
        # project_page.main_page.assert_page_contains('状态类型')
        # project_page.main_page.assert_page_contains('使用到的项目')
        # project_page.main_page.assert_page_contains('操作')

    @story('T117775 工作项工作流：列表检查')
    def test_sub_check_item(self, project_page):
        with step('进入工作项属性配置页面'):
            project_page.driver.go_to(full_link(Pl.ISSUE_TYPE))

        project_page.main_page.click_content('子检查项')
        project_page.main_page.click_content('工作项工作流')

        with step('查看开箱步骤属性：未激活 --> 已确认'):
            ...

            print('hhhh')

    @story('T131529 全局配置-工作项状态：搜索工作项状态')
    def test_status_search(self, project_page):
        with step('进入工作项工作项状态页面'):
            project_page.driver.go_to(full_link(Pl.TASK_STATUS))

        project_page.main_page.main_search_input('搜索工作项状态', '处理')
        project_page.main_page.assert_page_contains('处理中')
        project_page.main_page.assert_page_contains('待处理')

        project_page.main_page.main_search_input('搜索工作项状态', 'abcdd')
        project_page.main_page.assert_page_contains('暂无匹配结果')
