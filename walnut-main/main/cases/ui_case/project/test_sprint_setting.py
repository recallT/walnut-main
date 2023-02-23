import time

from falcons.com.nick import feature, story, step
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from main.cases.ui_case.elem_opt import get_text, is_in_elem
from main.cases.ui_case.links import PrjSettingLinks, full_link, PrjSprintLinks


@feature('项目设置-迭代配置')
class TestProSprintConfig:

    @story('T138303 项目设置-迭代配置：检查迭代配置页面')
    def test_pro_sprint_config_page(self, project_page):
        project_page.driver.go_to(full_link(PrjSprintLinks.SETTING_PAGE))
        project_page.main_page.assert_page_contains('以下为迭代的可配置项')
        project_page.main_page.assert_page_contains('迭代属性')
        project_page.main_page.assert_page_contains('迭代属性可以用于定制项目下迭代可以显示的字段，支持多种类型的特殊定制')
        project_page.main_page.assert_page_contains('迭代阶段')
        project_page.main_page.assert_page_contains('迭代阶段可以用于定制项目下迭代可以显示的不同阶段')
        project_page.main_page.assert_page_contains('迭代关联流水线运行')
        project_page.main_page.assert_page_contains('迭代关联流水线运行可以用于定制两者的关联规则，以便于在迭代中追踪和分析流水线运行情况')

    @story('T119432 迭代配置-迭代阶段：检查迭代阶段页面')
    def test_pro_sprint_status_config_page(self, project_page):
        d = project_page.driver
        mg = project_page.main_page
        d.go_to(full_link(PrjSprintLinks.STATUS_PAGE))
        mg.assert_page_contains('序号表示阶段的显示顺序，最先位置代表初始阶段，最后位置代表结束阶段。')
        with step('检查table标题'):
            header = d.find_element('//div[@class="Stage-row ui-table-header"]')
            cols = header.find_elements(By.XPATH, './div')
            cols = [get_text(c) for c in cols]
            assert cols == ['序号', '阶段名', '排序', '操作']
        with step('检查列表'):
            s_nos = d.find_elements('//div[@class="Stage-number-column"]')
            s_nos = [get_text(s) for s in s_nos]
            assert s_nos == ['1', '2', '3']
            s_names = d.find_elements('//div[@class="Stage-name-column"]/span[@class="Stage-name"]')
            s_names = [get_text(s) for s in s_names]
            assert s_names == ['未开始', '进行中', '已完成']
            s_sorts = d.find_elements('//div[@class="Stage-sort-column"]')[1:]
            l_can_not_edit = './/div[@class="can-not-edit"]'
            l_mv_up = './/*[local-name()="svg" and @class="ui-icon icon-move-up ui-icon-disabled"]'
            l_mv_down = './/*[local-name()="svg" and @class="ui-icon icon-move-down ui-icon-disabled"]'
            assert is_in_elem(s_sorts[0], l_can_not_edit)
            assert is_in_elem(s_sorts[1], l_mv_up)
            assert is_in_elem(s_sorts[1], l_mv_down)

            assert is_in_elem(s_sorts[2], l_can_not_edit)
            s_ops = d.find_elements('//div[@class="Stage-operation-column"]')[1:]
            assert is_in_elem(s_ops[0], l_can_not_edit)
            l_edit = './/*[local-name()="svg" and @class="ui-icon icon-edit "]'
            l_del = './/*[local-name()="svg" and @class="ui-icon icon-cross "]'
            assert is_in_elem(s_ops[1], l_edit)
            assert is_in_elem(s_ops[1], l_del)
            assert is_in_elem((s_ops[2]), l_can_not_edit)
        with step('? hover'):
            l_todo_tip = '//div[@class="Stage-name-column"]/*[local-name()="svg" and @class="ui-icon icon-question "]'
            els = d.find_elements(l_todo_tip)
            els[0].click()
            mg.assert_page_contains('未开始为迭代固定阶段，表示迭代尚未开始，不可编辑和删除。')
            els[1].click()
            mg.assert_page_contains('已完成为迭代固定阶段，表示迭代正式完成，不可编辑和删除。')
