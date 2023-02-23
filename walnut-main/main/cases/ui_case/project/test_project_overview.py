from falcons.com.nick import story, feature, parametrize


@feature('项目概览')
class TestProjectOverview:

    @parametrize('card_type', ('项目信息', '两周内工作项完成趋势', '公告', '项目属性',
                               '工作项类型统计', '进行中的迭代', '项目工时', '项目里程碑', '交付物提交数量'))
    @story('117478 添加卡片类型')
    @story('117483 编辑概览：添加两周内工作项完成趋势卡片（新增工作项趋势报表）')
    @story('117497 编辑概览：添加项目属性卡片')
    @story('117498 编辑概览：添加项目信息卡片')
    def test_add_card(self, card_type, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)

        prj.main_page.click_button('编辑概览')
        prj.main_page.click_button('添加卡片')

        # 选择卡片类型
        prj.pop_up.choose_card(card_type)

        prj.main_page.main_search_input('请输入卡片名称', f'{card_type}_test')
        prj.pop_up.click_pop_complete()
        prj.main_page.assert_page_contains('添加成功')

        prj.main_page.click_button('完成编辑')

    @story('117486 添加数据报表')
    def test_add_data_report(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)

        prj.main_page.click_button('编辑概览')
        prj.main_page.click_button('添加卡片')

        # 选择数据报表卡片
        prj.pop_up.choose_card('数据报表')

        prj.main_page.input_send_enter('选择报表', '需求创建者分布')
        prj.pop_up.click_pop_complete()
        prj.main_page.assert_page_contains('添加成功')

        prj.main_page.click_button('完成编辑')
