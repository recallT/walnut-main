import random

from falcons.com.nick import story, feature, parametrize

number = random.randint(1, 10)


@feature('工作项')
class TestWorkItem:

    @parametrize('work', ('需求', '任务', '缺陷'))
    @story('新增工作项内容')
    @story('134299 任务管理：新建任务')
    @story('134311 新建任务（必填项校验）')
    @story('134310 任务管理：新建任务时新建子工作项')
    def test_add_work_content(self, work, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')

        prj.enter_project(prj.proj_name)

        prj.top_bar.click_link(work)
        prj.main_page.click_button(work)

        # 录入内容
        prj.main_page.input('标题', f'{work}test_{number}')
        prj.main_page.click_button('确定')

        prj.main_page.assert_page_contains(f'{work}test_{number}')

    @parametrize('work', ('需求', '任务'))
    @story('列表状态')
    def test_status(self, work, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')

        prj.enter_project(prj.proj_name)

        prj.top_bar.click_link(work)

        prj.main_page.click_link('未开始')
        prj.main_page.click_link('进行中')
        prj.main_page.click_link('已完成')
        prj.main_page.click_link(f'全部{work}')

        prj.main_page.assert_page_contains(f'{work}test_{number}')

        # 修改工作项内容状态
        if work == '需求':
            prj.main_page.click_update_status('未开始', '关闭')
        elif work == '任务':
            prj.main_page.click_update_status('未开始', '开始任务')


@feature('文档工作项')
class TestWikiWorkItem:

    @story('关联wiki')
    def test_associated_wiki(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)

        prj.top_bar.more_tags('更多')
        prj.main_page.click_work_more('文档')

        prj.main_page.click_button('关联 Wiki')

        prj.main_page.click_span_content('示例知识库')
        prj.main_page.click_content('主页')
        prj.main_page.click_button('确定')

        prj.main_page.assert_page_contains('页面名称')

    @story('移除关联wiki')
    def test_delete_associated(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)

        prj.top_bar.more_tags('更多')
        prj.main_page.click_work_more('文档')

        prj.main_page.click_content('移除关联页面组')
        prj.main_page.click_button('取消')

        prj.main_page.click_content('移除关联页面组')
        prj.main_page.click_button('确定')


@feature('任务工作项')
class TestTaskWorkItem:

    @story('134311 新建任务必填校验')
    def test_task_add_check(self, project_page):
        prj = project_page

        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)

        prj.top_bar.click_link('任务')
        prj.main_page.click_button('任务')

        # 任务标题参数：传空
        prj.main_page.input('标题', '')
        prj.main_page.click_button('确定')

        prj.main_page.assert_page_contains('必填项不能为空')

        # 任务标题设置值
        prj.main_page.input('标题', '任务test_66')
        prj.main_page.click_button('确定')

    @story('117508 切换布局')
    @story('133313 任务管理-布局：窄详情')
    def test_task_layout(self, project_page):
        prj = project_page

        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)
        prj.top_bar.click_link('任务')

        # 切换到宽详情
        prj.pop_up.pop_search_opt('窄详情', '宽详情')

        # 切换到表格
        prj.pop_up.pop_search_opt('宽详情', '表格')
        prj.main_page.assert_page_contains('任务test_66')

        # 切换到看板
        prj.pop_up.pop_search_opt('表格', '看板')
        prj.main_page.assert_page_contains('看板栏设置')

    @story('T134194 新建视图')
    def test_task_add_view(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)
        prj.top_bar.click_link('任务')

        prj.main_page.click_page_link('视图管理')
        prj.main_page.click_button('新建视图')
        prj.main_page.input('视图名称', 'Task视图Test')
        # 视图权限：公共
        prj.pop_up.view_permission_select('公共')
        prj.main_page.click_button('确定')

        # toast提示
        prj.main_page.assert_page_contains('添加视图成功')
        # 校验弹框关闭，定位到新视图页面
        prj.main_page.assert_page_contains('Task视图Test')

    @story('133189 任务管理-表格布局-表头：结构非显示子工作项情况下按创建时间排序')
    @story('133221 任务管理-表格布局-表头：结构为显示子工作项情况下按创建时间排序')
    def test_task_sort(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)
        prj.top_bar.click_link('任务')

        prj.main_page.click_content('排序')
        prj.main_page.click_content('倒序排序')
        prj.main_page.multiple_content('倒序排序', 2)
