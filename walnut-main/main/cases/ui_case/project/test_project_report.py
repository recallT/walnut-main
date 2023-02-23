import time

from falcons.com.nick import story, feature, fixture
from falcons.com.ui import UiDriver
from selenium.webdriver import ActionChains

from main.actions.issue import IssueTypeAction
from main.actions.pro import PrjSettingAction
from main.actions.team import TeamAction
from main.cases.ui_case.links import full_link, PrjReportLinks


@fixture(scope='module')
def _issue_type():
    issue_type = IssueTypeAction.create_issue_type()
    iid = issue_type.value('uuid')
    pid = UiDriver.env.project_uuid_ui
    PrjSettingAction.add_issue_type(iid, project_uuid=pid)
    yield issue_type
    PrjSettingAction.del_issue_type(iid, project_uuid=UiDriver.env.project_uuid_ui)
    time.sleep(1)
    IssueTypeAction.delete_issue_type(iid)


@feature('报表管理')
class TestProReport:

    def _check_table_title(self, page):
        page.main_page.assert_page_contains('报表名称')
        page.main_page.assert_page_contains('所属分组')
        page.main_page.assert_page_contains('创建者')
        page.main_page.assert_page_contains('最后更新时间')
        page.main_page.assert_page_contains('操作')

    @story('T136259 我创建的：分组报表列表')
    def test_project_report_mine(self, project_page):
        project_page.driver.go_to(full_link(PrjReportLinks.MINES))
        self._check_table_title(project_page)
        elems = project_page.driver.find_elements(
            '//div[contains(@class, "base-data-list-cell first-col")]/following-sibling::div[2]/div/span')
        admin = TeamAction.global_user()
        not_mine = [e for e in elems if e.get_attribute('innerHTML') != admin['name']]
        assert not not_mine
        project_page.main_page.assert_page_contains('我创建的')
        # reports = PrjAction.get_reports_groups(project_uuid=UiDriver.env.project_uuid_ui)['reports']
        # project_page.main_page.assert_page_contains(f'({len(reports)})')

    @story('T135618 所有报表：分组报表列表')
    def test_project_report_all(self, project_page):
        project_page.driver.go_to(full_link(PrjReportLinks.ALL))
        self._check_table_title(project_page)
        project_page.main_page.assert_page_contains('所有报表')
        # reports = PrjAction.get_reports_groups(project_uuid=UiDriver.env.project_uuid_ui)['reports']
        # project_page.main_page.assert_page_contains(f'({len(reports)})')

    @story('T131961 缺陷分析：更多')
    def test_project_report_more(self, project_page):
        project_page.driver.go_to(full_link(PrjReportLinks.ALL))
        d = project_page.driver
        l_li = '//span[contains(text(), "缺陷分析")]/ancestor::li'
        li = d.find_element(l_li)
        ActionChains(d.driver).move_to_element(li).click(li).perform()
        l_svg = l_li + '/descendant::*[local-name()="svg"]'
        svg = d.find_element(l_svg)
        ActionChains(d.driver).move_to_element(svg).click(svg).perform()
        assert project_page.main_page.assert_page_contains('删除分组')
        assert project_page.main_page.assert_page_contains('删除分组和报表')

    @story('T138501 新建报表-新建弹窗：全部')
    def test_project_report_create(self, project_page, _issue_type):
        project_page.driver.go_to(full_link(PrjReportLinks.MINES))
        project_page.driver.refresh()
        mp = project_page.main_page
        mp.click_button('新建报表')
        time.sleep(5)
        mp.assert_page_contains('通用报表')
        mp.assert_page_contains('工时报表')
        mp.assert_page_contains('需求报表')
        mp.assert_page_contains('缺陷报表')
        mp.assert_page_contains(f'{_issue_type.value("name")}报表')
