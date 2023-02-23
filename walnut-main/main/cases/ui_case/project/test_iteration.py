import random

from falcons.com.nick import story, feature, parametrize

number = random.randint(1, 10)


@feature('迭代操作')
class TestIterOpt:

    @story('119420 新建迭代')
    def test_add_iter(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)

        prj.top_bar.click_link('迭代')
        prj.main_page.click_content('新建迭代')

        # 录入内容
        prj.main_page.input('迭代名称', f'迭代test_{number}')
        prj.main_page.dropdown('迭代周期', '1周', el2_type='*')

        prj.main_page.click_button('确定')

        prj.main_page.assert_page_contains('新建成功')
        prj.main_page.assert_page_contains('迭代信息')

    @story('119291 变更迭代状态')
    def test_iter_status(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)

        prj.top_bar.click_link('迭代')

        prj.main_page.multiple_content('进行中', 2)
        prj.main_page.click_button('确认修改')

    @parametrize('work', ('需求', '缺陷', '任务'))
    @story('迭代中创建工作项内容')
    def test_iter_work_content(self, work, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)
        prj.top_bar.click_link('迭代')

        prj.main_page.bar.click_link(work)
        prj.main_page.click_button(work)

        # 录入内容
        prj.main_page.input('标题', f'{work}test_{number}')
        prj.main_page.click_button('确定')

    @parametrize('work', ('需求', '缺陷', '任务'))
    @story('将工作项内容移除迭代')
    def test_delete_work(self, work, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)
        prj.top_bar.click_link('迭代')

        prj.main_page.bar.click_link(work)

        # 存在进度管理器时关闭它
        # _, is_contains = prj.main_page.assert_page_contains('进度管理器')
        # if is_contains:
        # prj.main_page.click_close_schedule()

        # 选择宽详情下进行删除操作
        prj.main_page.bar.layout_config('布局', '宽详情')
        prj.main_page.click_button('更多')
        prj.main_page.click_content('删除')

        prj.main_page.assert_page_contains(f'当前{work}「{work}test_{number}」会被删除，此操作不可撤销，是否确定')
        prj.main_page.click_span_content('确定')

        prj.main_page.assert_page_contains('删除成功')

    @story('编辑迭代')
    def test_edit_iter(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)
        prj.top_bar.click_link('迭代')

        prj.main_page.click_iter_more('编辑迭代')

        # 变更原迭代名称
        prj.main_page.input('迭代名称', '编辑迭代test')
        prj.main_page.click_button('确定')

        prj.main_page.assert_page_contains('更新成功')

    @story('删除迭代')
    def test_delete_iter(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)
        prj.top_bar.click_link('迭代')

        prj.main_page.click_iter_more('删除迭代')

        prj.main_page.assert_page_contains(f'当前正在删除迭代「 编辑迭代test 」，删除迭代不会删除迭代下的工作项')
        prj.main_page.click_span_content('确定')

        prj.main_page.assert_page_contains('操作成功')

    @parametrize('num', (1, 2))
    @story('切换迭代列表左侧栏迭代')
    def test_change_iter_list(self, num, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)

        prj.top_bar.click_link('迭代')
        prj.main_page.click_content('新建迭代')

        # 录入内容
        prj.main_page.input('迭代名称', f'迭代test_{num}')
        prj.main_page.dropdown('迭代周期', '2周', el2_type='*')

        prj.main_page.click_button('确定')
        prj.main_page.assert_page_contains('新建成功')

    @story('119988 将单个工作项移出迭代')
    def test_move_out(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)

        prj.top_bar.click_link('迭代')
        prj.main_page.click_content('新建迭代')

        # 录入迭代内容
        prj.main_page.input('迭代名称', f'迭代test_88')
        prj.main_page.dropdown('迭代周期', '1周', el2_type='*')

        prj.main_page.click_button('确定')
        prj.main_page.assert_page_contains('新建成功')

        prj.main_page.click_page_link('缺陷')
        prj.main_page.click_button('缺陷')

        # 录入缺陷工作项内容
        prj.main_page.input('标题', f'缺陷test_88')
        prj.main_page.click_button('确定')

        # 所有工作项中将第一个单移出
        prj.top_bar.click_link('迭代')
        prj.main_page.click_content('所有工作项')
        prj.main_page.check_checkbox(2)
        prj.main_page.click_button('移出迭代')

        prj.main_page.assert_page_contains(f'正在将 1 个工作项移出迭代，工作项移出迭代后为未规划工作项，是否移出？')
        prj.main_page.click_button('确定')

        prj.main_page.assert_page_contains('1 个工作项移出迭代成功')


@feature('迭代计划操作')
class TestIterPlanOpt:

    @story('迭代属性配置')
    def test_iter_attribute_deploy(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)
        prj.top_bar.more_tags('更多')
        prj.main_page.click_more_setup('设置')

        prj.main_page.click_link('迭代配置')
        prj.main_page.multiple_content('迭代属性')

        # 新建'单行文本'属性
        prj.main_page.click_button('新建迭代属性')
        prj.main_page.dropdown('属性类型', '单行文本')
        prj.main_page.input('属性名称', '示例单行文本')
        prj.main_page.click_button('确定')

        prj.main_page.assert_page_contains('迭代属性创建成功')

        # 新建'单选菜单'属性（属性类型默认是'单选菜单，无需选择'）
        prj.main_page.click_button('新建迭代属性')
        prj.main_page.input('属性名称', '示例单选菜单')
        prj.main_page.input('选项值', 'test1')
        prj.main_page.click_button('添加')
        prj.main_page.input('选项值', 'test2')
        prj.main_page.click_button('添加')
        prj.main_page.click_button('确定')

        prj.main_page.assert_page_contains('迭代属性创建成功')

        # 新建'单选成员'属性
        prj.main_page.click_button('新建迭代属性')
        prj.main_page.dropdown('属性类型', '单选成员')
        prj.main_page.input('属性名称', '示例单选成员')
        prj.main_page.click_button('确定')

        prj.main_page.assert_page_contains('迭代属性创建成功')

    @story('119380 导出迭代')
    def test_export_iter(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')
        prj.enter_project(prj.proj_name)

        prj.top_bar.click_link('迭代计划')
        prj.main_page.click_button('新建迭代')

        # 录入内容
        prj.main_page.input('迭代名称', f'迭代test_66')
        prj.main_page.dropdown('迭代周期', '1周', el2_type='*')
        prj.main_page.click_button('确定')

        prj.main_page.assert_page_contains('新建成功')

        # 导出计划
        prj.main_page.click_button('导出')
        prj.main_page.click_button('确定')
