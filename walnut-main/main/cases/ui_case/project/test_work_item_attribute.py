from falcons.com.nick import story, feature, parametrize


@feature('工作项属性')
class TestWorkItemAttribute:

    @parametrize('work', ('需求', '缺陷'))
    @story('添加工作项属性')
    def test_add_work_attribute(self, work, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')

        prj.enter_project(prj.proj_name)
        prj.top_bar.more_tags('更多')
        prj.main_page.click_more_setup('设置')

        prj.main_page.click_link('工作项类型')
        prj.main_page.multiple_content(work, 2)
        prj.main_page.click_content('属性与视图')

        # 添加工作属性：发布日期
        prj.main_page.click_content('添加工作项属性')
        prj.main_page.input_send_enter('属性名称', '发布日期')
        prj.main_page.click_button('确定')

        # 搜索
        prj.main_page.main_search_input('搜索工作项属性', '发布日期')

        prj.main_page.assert_page_contains('发布日期')

        # 删除
        prj.main_page.click_table_element(1, 5)
        prj.main_page.click_button('确定')

        prj.main_page.assert_page_contains('删除成功')

    # @parametrize('attribute', ('创建时间', '所属迭代', '预估偏差'))
    # @story('添加关键属性')
    # def test_add_key_attribute(self, attribute, project_page):
    #     prj = project_page
    #     prj.side_bar.nav_to('项目管理')
    #
    #     prj.enter_project(prj.proj_name)
    #     prj.top_bar.more_tags('更多')
    #     prj.main_page.click_more_setup()
    #     prj.main_page.click_link('工作项类型')
    #     prj.main_page.multiple_content('需求', 2)
    #     prj.main_page.click_content('属性与视图')
    #
    #     prj.main_page.click_content('关键属性')
    #
    #     prj.main_page.assert_property_config('负责人')
    #
    #     # 添加关键属性
    #     prj.main_page.click_button('添加关键属性')
    #     prj.main_page.send_content('选择关键属性', attribute)
    #     prj.main_page.click_button('确定')
    #
    #     prj.main_page.assert_property_config(attribute)
    #
    #     # 删除
    #     prj.main_page.click_table_element(3, 2)
    #     prj.main_page.assert_page_contains(f'正在移除「{attribute}」，此操作不可撤销，是否移除')
    #     prj.main_page.click_button('确认移除')
