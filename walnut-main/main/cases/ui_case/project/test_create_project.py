import random
import time

from falcons.com.nick import story, feature, parametrize

from main.params.const import ACCOUNT

number = random.randint(10, 99)


@feature('创建多种项目')
class TestCreateProject:

    @parametrize('name', ('敏捷项目', '瀑布项目', '通用任务',))
    @story('137897 项目管理：新建项目（敏捷项目管理）')
    @story('137898 项目管理：新建项目（瀑布项目规划）')
    @story('137899 项目管理：新建项目（通用任务管理）')
    @story('151134 新建团队-新建项目：新建敏捷项目')
    @story('138984 新建项目：创建项目权限验证（超级管理员）')
    def test_create_prj(self, name, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')

        prj.main_page.click_button('新建项目')
        prj.main_page.page_side_bar(f'{name}')
        prj.main_page.input('项目名称', f'{name}test_{number}')
        prj.main_page.click_button('下一步')

        prj.main_page.input('新建项目', ACCOUNT.user.email)
        prj.main_page.click_button('完成')
        prj.main_page.click_button('确定')

        prj.top_bar.click_link('概览')
        prj.main_page.assert_page_contains('项目信息')


@feature('复制项目')
class TestCopyProject:

    @story('从已有项目复制-勾选自定义复制的数据')
    def test_copy_prj(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')

        prj.main_page.click_button('新建项目')
        prj.main_page.click_content('从已有项目复制')
        # 复制敏捷项目
        prj.main_page.search_input('选择要复制的项目', prj.proj_name)
        prj.main_page.input('项目名称', f'copy项目test_{number}')

        prj.main_page.click_button('创建')
        prj.main_page.click_button('确定')

        prj.main_page.assert_page_contains(f'copy项目test_{number}')

        # 关闭进度管理器
        if prj.main_page.assert_page_contains('项目新建成功')[1]:
            prj.main_page.click_close_schedule()
        # if el.is_displayed():  # 判断元素是否存在页面上

    @story('119181 从已有项目复制-不勾选自定义复制的数据')
    def test_copy_prj_uncheck(self, project_page):
        prj = project_page
        prj.side_bar.nav_to('项目管理')

        prj.main_page.click_button('新建项目')
        prj.main_page.click_content('从已有项目复制')

        time.sleep(1)
        prj.main_page.search_input('选择要复制的项目', prj.proj_name)
        prj.main_page.input('项目名称', f'copy项目uncheck_{number}')

        # 取消勾选复制的数据
        prj.main_page.click_content('工作项数据')
        prj.main_page.click_content('迭代数据')
        prj.main_page.click_content('项目成员')
        prj.main_page.click_content('项目计划')
        prj.main_page.click_content('工作项内上传的文件')
        prj.main_page.click_content('包含目标交付物')
        prj.main_page.click_content('项目报表')
        prj.main_page.click_content('里程碑内上传的交付物')

        prj.main_page.click_button('下一步')
        prj.main_page.input('新建项目', ACCOUNT.user.email)
        prj.main_page.click_button('完成')
        prj.main_page.click_button('确定')

        prj.main_page.assert_page_contains('进度管理器')
        prj.main_page.assert_page_contains('项目新建成功')
        prj.main_page.assert_page_contains(f'copy项目uncheck_{number}')

        # 关闭进度管理器
        if prj.main_page.assert_page_contains('项目新建成功'):
            prj.main_page.click_close_schedule()
