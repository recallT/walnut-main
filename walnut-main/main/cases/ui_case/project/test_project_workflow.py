from falcons.com.nick import story, feature

from main.cases.ui_case.links import full_link, PrjWorkflowLinks


@feature('项目-工作项工作流')
class TestProWorkflow:

    @story('T123199 工作项工作流：详情视图下移除初始状态')
    def test_prj_workflow_default_status(self, project_page):
        project_page.driver.go_to(full_link(PrjWorkflowLinks.FLOW_SETTING))
        l_detail_view = '//label[contains(@class, "ones-radio-button-wrapper")]/span[text()="详情视图"]'
        # project_page.main_page.click_('详情视图')
        project_page.driver.find_element(l_detail_view).click()
        l_del_btn = '//span[text()="初始状态"]/../following-sibling::span[1]'
        del_btn = project_page.driver.find_element(l_del_btn)
        assert del_btn.get_attribute(
            'class') == 'ones-action ones-action-default ones-action-disabled ones-style--disabled'
        del_btn.click()
        project_page.main_page.assert_page_contains('未开始')
