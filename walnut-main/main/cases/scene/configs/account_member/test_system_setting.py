# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_system_setting.py
@Author  ：zhangyonghui@ones.ai
@Date    ：7/19/22 3:32 PM 
@Desc    ：系统偏好设置
"""
from falcons.check import Checker
from falcons.com.nick import story, step, feature, mark
from falcons.helper import mocks

from main.params import setting, data
from main.api import setting as st, project


@mark.smoke
@feature('全局配置-系统偏好设置')
class TestSystemSetting(Checker):

    @story('T118588 侧边栏菜单设置-系统菜单：删除一级菜单')
    @story('T118590 侧边栏菜单设置-系统菜单：添加一级菜单')
    @story('T118593 侧边栏菜单设置-系统菜单：修改一级菜单显示名称')
    def test_system_menu_setting(self):
        with step('添加一级菜单'):
            value = 'api-test-' + mocks.num()
            param = setting.add_directory()[0]
            param.json_update('value', value)
            self.call(st.SidebarSetting, param)
            # 查询菜单信息uuid
            param_menu = setting.get_menu()[0]
            resp = self.call(st.SidebarSettingMenu, param_menu)
            sidebar_menus = [r for r in resp.value('system') if r['value'] == value][0]
        with step('更新一级菜单名称'):
            # 更新名称
            sidebar_menus['value'] = 'new-test'
            param = setting.sidebar_setting_update()[0]
            param.json_update('sidebar_menus', [sidebar_menus])
            self.call(st.SidebarSettingUpdate, param).check_response('code', 200)
        with step('删除一级菜单'):
            # 删除
            param_menu.uri_args({'menu_uuid': sidebar_menus['uuid']})
            self.call(st.DelMenu, param_menu).check_response('code', 200)

    @story('T118592 侧边栏菜单设置-系统菜单：修改系统菜单显示名称')
    def test_update_menu_name(self):
        # 查询菜单信息uuid
        param_menu = setting.get_menu()[0]
        resp = self.call(st.SidebarSettingMenu, param_menu)
        menu_uuid = [r['uuid'] for r in resp.value('system') if '项目管理' in r['value']]
        with step('「项目管理」显示名称修改为：Project'):
            if len(menu_uuid) != 0:
                param = setting.sidebar_setting_update()[0]
                param.json_update('sidebar_menus[0].uuid', menu_uuid[0])
                param.json_update('sidebar_menus[0].value', 'Project')
                self.call(st.SidebarSettingUpdate, param).check_response('code', 200)

        with step('还原数据'):
            param.json_update('sidebar_menus[0].value', '项目管理')
            self.call(st.SidebarSettingUpdate, param).check_response('code', 200)

    @story('118609 侧边栏菜单设置：开箱默认菜单顺序')
    def test_default_menu(self):
        default_values = {'项目管理', '我的工作台', '测试管理', '知识库管理'}
        param_menu = setting.get_menu()[0]
        resp = self.call(st.SidebarSettingMenu, param_menu)
        # 侧边栏菜单
        resp_info = self.call(st.GetSidebarMenus, param_menu)
        with step('检查系统菜单模块'):
            values = [r['value'] for r in resp.value('system')]
            assert set(values) >= default_values
        with step('检查自定义菜单和其他模块'):
            # 侧边栏是否展示下载客户端
            show_menus = [r['is_show'] for r in resp_info.value('other') if r['value'] == '下载移动端'][0]
            # 配置中心是否打开展示下载客户端开关
            is_show = [r['is_show'] for r in resp.value('other') if r['default_value'] == '下载移动端'][0]
            assert show_menus == is_show

    @story('T118587 侧边栏菜单设置-系统菜单：菜单排序')
    def test_sort_menu(self):
        param_menu = setting.get_menu()[0]
        sidebar_menus = self.call(st.SidebarSettingMenu, param_menu).value('system')
        # 更换位子
        if len(sidebar_menus) >= 3:
            sidebar_menus[2], sidebar_menus[3] = sidebar_menus[3], sidebar_menus[2]
            param = setting.sidebar_setting_update()[0]
            param.json_update('sidebar_menus', sidebar_menus)
            self.call(st.SidebarSettingUpdate, param).check_response('code', 200)


    @story('T118586 侧边栏菜单设置-其他：点击显示在侧边栏开关')
    def test_is_show_download_mobile_menu(self):
        param_menu = setting.get_menu()[0]
        resp = self.call(st.SidebarSettingMenu, param_menu)
        sidebar_menus = [r for r in resp.value('other') if r['default_value'] == '下载移动端'][0]
        sidebar_menus['is_show'] = False
        param = setting.sidebar_setting_update()[0]
        with step('关闭下载客户端开关'):
            param.json_update('sidebar_menus', [sidebar_menus])
            self.call(st.SidebarSettingUpdate, param).check_response('code', 200)

        with step('打开下载客户端开关'):
            sidebar_menus['is_show'] = True
            param.json_update('sidebar_menus', [sidebar_menus])
            self.call(st.SidebarSettingUpdate, param).check_response('code', 200)

    @story('T118602侧边栏菜单设置-自定义菜单：添加自定义菜单')
    @story('T118599 侧边栏菜单设置-自定义菜单：删除自定义链接菜单')
    def test_add_self_menu(self):
        with step('新增自定义菜单'):
            value = "自定义菜单" + mocks.num()
            param = setting.add_self_menu()[0]
            param.json_update('value', value)
            self.call(st.AddSidebarSetting, param)

        with step('查询创建的菜单UUId'):
            param_menu = setting.get_menu()[0]
            resp = self.call(st.SidebarSettingMenu, param_menu)
            uuid = [r['uuid'] for r in resp.value('custom') if r['value'] == value][0]

        with step('删除自定义菜单'):
            param_menu.uri_args({'menu_uuid': uuid})
            self.call(st.DelMenu, param_menu).check_response('code', 200)

    @story('T118607 侧边栏菜单设置-自定义菜单：移除「自定义链接」菜单成员域')
    @story('T118604 侧边栏菜单设置-自定义菜单：添加「自定义链接」菜单成员域')
    @story('T118606 侧边栏菜单设置-自定义菜单：修改自定义链接菜单显示名称')
    def test_self_menu_user_domain(self):
        value = "自定义菜单" + mocks.num()
        param = setting.add_self_menu()[0]
        param.json_update('value', value)
        self.call(st.AddSidebarSetting, param)
        # 查询菜单UUId
        param_menu = setting.get_menu()[0]
        resp = self.call(st.SidebarSettingMenu, param_menu)
        sidebar_menus = [r for r in resp.value('custom') if r['value'] == value][0]

        with step('成员域列表添加「用户组A」'):
            # 添加用户组
            param_user = data.user_group_add()[0]
            resp = self.call(project.UsesGroupAdd, param_user)
            group_uuid = resp.value('uuid')
            sidebar_menus['user_domains'].append({'user_domain_type': 'group', 'user_domain_param': group_uuid})
            sidebar_menus['custom'] = True
            sidebar_menus['value'] = 'test-test'
            param = setting.sidebar_setting_update()[0]
            param.json_update('sidebar_menus', [sidebar_menus])
            self.call(st.SidebarSettingUpdate, param).check_response('code', 200)

        with step('移除「自定义链接」菜单成员域'):
            sidebar_menus['user_domains'] = []
            param.json_update('sidebar_menus', [sidebar_menus])
            self.call(st.SidebarSettingUpdate, param).check_response('code', 200)

        with step('删除数据'):
            param_menu.uri_args({'menu_uuid': sidebar_menus['uuid']})
            self.call(st.DelMenu, param_menu).check_response('code', 200)

    @story('T118600 侧边栏菜单设置-自定义菜单：添加一级菜单')
    @story('T118597 侧边栏菜单设置-自定义菜单：删除一级菜单')
    @story('T118605 侧边栏菜单设置-自定义菜单：修改一级菜单显示名称')
    def test_self_menu_setting(self):
        with step('添加一级菜单'):
            value = 'api-test-' + mocks.num()
            param = setting.add_directory()[0]
            param.json_update('value', value)
            param.json_update('position', 2)
            param.json_update('is_custom', True)
            self.call(st.SidebarSetting, param)
        with step('更新一级菜单名称'):
            # 查询菜单信息uuid
            param_menu = setting.get_menu()[0]
            resp = self.call(st.SidebarSettingMenu, param_menu)
            sidebar_menus = [r for r in resp.value('custom') if r['value'] == value][0]
            # 更新名称
            sidebar_menus['value'] = 'new-test'
            sidebar_menus['items'] = []
            sidebar_menus['custom'] = True
            param = setting.sidebar_setting_update()[0]
            param.json_update('sidebar_menus', [sidebar_menus])
            self.call(st.SidebarSettingUpdate, param).check_response('code', 200)
            with step('删除一级菜单'):
                # 删除
                param_menu.uri_args({'menu_uuid': sidebar_menus['uuid']})
                self.call(st.DelMenu, param_menu).check_response('code', 200)

    @story('T118608 侧边栏菜单设置：检查侧边栏菜单入口')
    def test_check_sidebar_menus(self):
        # 先获取配置中心中打开的菜单信息
        param_menu = setting.get_menu()[0]
        resp = self.call(st.SidebarSettingMenu, param_menu)
        sidebar_menus = [r['value'] for r in resp.value('system') if
                         r['is_show'] == True and r['default_value'] != '一级菜单']
        print(sidebar_menus)
        with step('侧边栏菜单入口展示'):
            resp_info = self.call(st.GetSidebarMenus, param_menu)
            show_menus = [r['value'] for r in resp_info.value('system') if
                          r['is_show'] == True and 'first_level_menu' not in r['key']]
            assert set(show_menus) == set(sidebar_menus)

    @story('T23715 工作日设置：标准工作时长输入大于24的数字')
    def test_set_work_day_gt_24(self):
        with step('输入25，点击保存'):
            param = setting.set_work_day()[0]
            param.json_update('workhours', 2500000)
            self.call(st.WorkDaySetting, param, status_code=801)

    @story('T23712 工作日设置：更改标准工作时长小于0')
    def test_set_work_day_lt_0(self):
        with step('输入-1，点击保存'):
            param = setting.set_work_day()[0]
            param.json_update('workhours', -100000)
            self.call(st.WorkDaySetting, param, status_code=801)

    @story('T23717 工作日设置：修改工时默认单位为小时')
    def test_set_work_hour(self):
        param = setting.set_work_day()[0]
        param.json_update('workhours_unit', 'hour')
        self.call(st.WorkDaySetting, param, status_code=200)

    @story('T23718 工作日设置：修改默认单位为天')
    def test_set_work_hour(self):
        param = setting.set_work_day()[0]
        param.json_update('workhours_unit', 'day')
        self.call(st.WorkDaySetting, param, status_code=200)
