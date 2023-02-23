
from falcons.com.nick import story, feature

from main.cases.ui_case.links import full_link, PrjSettingLinks


@feature('项目配置')
class TestProConfig:

    @story('T147336 项目配置')
    def test_project_config_page(self, project_page):
        project_page.driver.go_to(full_link(PrjSettingLinks.HOME_PAGE))
        project_page.main_page.assert_page_contains('以下为项目的可配置项')
        project_page.main_page.assert_page_contains('项目属性')
        project_page.main_page.assert_page_contains('项目属性设置可以设置项目概览页面需要显示的项目自定义属性')
        project_page.main_page.assert_page_contains('项目状态')
        project_page.main_page.assert_page_contains('项目状态用于定制项目所处的不同状态，支持不同状态间的切换')


