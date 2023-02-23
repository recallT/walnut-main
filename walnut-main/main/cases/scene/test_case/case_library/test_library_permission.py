"""
@File    ：test_library_permission
@Author  ：xiechunwei
@Date    ：2022/8/17 18:12
@Desc    ：用例库-权限配置
"""
from falcons.com.nick import feature, story, fixture, step
from . import add_case_library
from falcons.check import Checker
from main.actions.case import CaseAction
from main.actions.member import MemberAction


# 初始化用例库
@fixture(scope='module')
def libra_init():
    return add_case_library()


@fixture(scope='module')
def _storage():
    return {}


@fixture(scope='module', autouse=True)
def depart_group_opt():
    """部门和用户组数据操作"""

    # 新建部门
    d_uuid = MemberAction.add_department()
    # 新建用户组
    g_uuid = MemberAction.add_user_group()

    yield {'d_uuid': d_uuid, 'g_uuid': g_uuid}

    # 删除部门
    MemberAction.del_department(d_uuid)
    # 删除用户组
    MemberAction.del_user_group(g_uuid)


def get_member():
    member_uuid = MemberAction.get_member_uuid()
    return member_uuid


@feature('用例库-权限配置-编辑用例')
class TestLibraryPermEditCase(Checker):

    @story('147783 编辑用例：新增成员域（成员）')
    @story('147784 编辑用例：新增成员域')
    def test_edit_case_add_single_user(self, libra_init, _storage):
        with step('成员a 点击编辑用例权限下拉框，选择成员c'):
            user_uuid = CaseAction.library_permission_rules_add(libra_init['uuid'], 'testcase_edit_case', 'single_user',
                                                                get_member())

        _storage |= {'user_uuid': user_uuid}

    @story('147803 编辑用例：新增成员域（特殊角色）')
    def test_edit_case_add_everyone(self, libra_init, _storage):
        with step('成员a 点击编辑用例权限下拉框，选择特殊角色'):
            everyone_uuid = CaseAction.library_permission_rules_add(libra_init['uuid'], 'testcase_edit_case',
                                                                    'everyone')

        _storage |= {'everyone_uuid': everyone_uuid}

    @story('147781 编辑用例：新增成员域（部门）')
    def test_edit_case_add_department(self, libra_init, _storage, depart_group_opt):
        with step('成员a 点击编辑用例权限下拉框，选择部门'):
            department_uuid = CaseAction.library_permission_rules_add(libra_init['uuid'], 'testcase_edit_case',
                                                                      'department', depart_group_opt['d_uuid'])

        _storage |= {'department_uuid': department_uuid}

    @story('147782 编辑用例：新增成员域（用户组）')
    def test_edit_case_add_group(self, libra_init, _storage, depart_group_opt):
        with step('成员a 点击编辑用例权限下拉框，选择用户组'):
            group_uuid = CaseAction.library_permission_rules_add(libra_init['uuid'], 'testcase_edit_case', 'group',
                                                                 depart_group_opt['g_uuid'])

        _storage |= {'group_uuid': group_uuid}

    @story('147798 编辑用例：移除成员域')
    @story('148636 编辑用例：多次快速点击移除按钮')
    def test_edit_case_delete_single_user(self, _storage):
        for n in range(3):
            try:
                CaseAction.del_testcase_permission(_storage['user_uuid'])
            except AssertionError:
                print("对象已移除，无需重复操作")

    @story('147870 编辑用例：移除成员域（特殊角色）')
    def test_edit_case_delete_everyone(self, _storage):
        CaseAction.del_testcase_permission(_storage['everyone_uuid'])

    @story('147871 编辑用例：移除成员域（部门）')
    def test_edit_case_delete_department(self, _storage):
        with step('编辑用例权限移除部门'):
            CaseAction.del_testcase_permission(_storage['department_uuid'])

    @story('147869 编辑用例：移除成员域（用户组）')
    def test_edit_case_delete_group(self, _storage):
        with step('编辑用例权限移除用户组'):
            CaseAction.del_testcase_permission(_storage['group_uuid'])

    @story('147880 编辑用例：搜索成员域')
    @story('147878 查看用例库：搜索成员域')
    def test_edit_case_user(self):
        MemberAction.get_member_uuid()


@feature('用例库-权限配置-查看用例库')
class TestLibraryPermCheck(Checker):

    @story('147741 查看用例库：新增成员域')
    def test_check_library_add_single_user(self, libra_init, _storage):
        with step('成员a 点击编辑用例权限下拉框，选择成员c'):
            lib_user_uuid = CaseAction.library_permission_rules_add(libra_init['uuid'], 'testcase_view_library',
                                                                    'single_user', get_member())

            _storage |= {'lib_user_uuid': lib_user_uuid}

    @story('147773 查看用例库：新增成员域（部门）')
    @story('147771 查看用例库：新增成员域（成员）')
    def test_check_library_add_department(self, libra_init, _storage, depart_group_opt):
        with step('成员a 点击编辑用例权限下拉框，选择部门'):
            lib_depart_uuid = CaseAction.library_permission_rules_add(libra_init['uuid'], 'testcase_view_library',
                                                                      'department', depart_group_opt['d_uuid'])

            _storage |= {'lib_depart_uuid': lib_depart_uuid}

    @story('147801 查看用例库：新增成员域（特殊角色）')
    def test_check_library_add_everyone(self, libra_init, _storage, depart_group_opt):
        with step('成员a 点击编辑用例权限下拉框，选择特殊角色'):
            lib_everyone_uuid = CaseAction.library_permission_rules_add(libra_init['uuid'], 'testcase_view_library',
                                                                        'everyone')

        _storage |= {'lib_everyone_uuid': lib_everyone_uuid}

    @story('147774 查看用例库：新增成员域（用户组）')
    def test_check_library_add_group(self, libra_init, _storage, depart_group_opt):
        with step('成员a 点击编辑用例权限下拉框，选择用户组'):
            lib_group_uuid = CaseAction.library_permission_rules_add(libra_init['uuid'], 'testcase_view_library',
                                                                     'group',
                                                                     depart_group_opt['g_uuid'])

        _storage |= {'lib_group_uuid': lib_group_uuid}

    @story('147795 查看用例库：移除成员域')
    @story('148571 查看用例库：移除成员域（当前成员）')
    @story('148570 查看用例库：移除成员域（当前成员，测试管理管理员）')
    @story('148636 编辑用例：多次快速点击移除按钮')
    def test_check_library_delete_single_user(self, _storage):
        for n in range(3):
            try:
                CaseAction.del_testcase_permission(_storage['lib_user_uuid'])
            except AssertionError:
                print("对象已移除，无需重复操作")

    @story('147807 查看用例库：移除成员域（部门）')
    def test_check_library_delete_department(self, _storage):
        with step('编辑用例权限移除部门'):
            CaseAction.del_testcase_permission(_storage['lib_depart_uuid'])

    @story('147808 查看用例库：移除成员域（特殊角色）')
    def test_check_library_delete_everyone(self, _storage):
        CaseAction.del_testcase_permission(_storage['lib_everyone_uuid'])

    @story('147809 查看用例库：移除成员域（用户组）')
    def test_check_library_delete_group(self, _storage):
        with step('编辑用例权限移除用户组'):
            CaseAction.del_testcase_permission(_storage['lib_group_uuid'])
