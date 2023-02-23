# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：test_member.py
@Author  ：zhangyonghui@ones.ai
@Date    ：7/15/22 3:30 PM 
@Desc    ：
"""
import pytest
from falcons.check import Checker, go
from falcons.com.nick import story, fixture, step, feature
from falcons.helper import mocks

from main.api import project, third
from main.params import data, conf
from main.api import user
from main.params import user as u
from main.actions.member import MemberAction
from main.params import third as t


@fixture(scope='module', autouse=True)
def add_user_group():
    # 新增用户组
    param = data.user_group_add()[0]
    resp = go(project.UsesGroupAdd, param)
    group_uuid = resp.value('uuid')

    # 新增部门
    department_uuid = MemberAction.add_department()
    d = {'group_uuid': group_uuid, 'department_uuid': department_uuid}
    return d


@fixture(scope='module', autouse=True)
def del_user_group(add_user_group):
    yield
    param = data.user_group_add()[0]
    param.uri_args({'group_uuid': add_user_group['group_uuid']})
    go(project.UsesGroupDelete, param, with_json=False, status_code=200)


@feature('全局配置-账号与成员')
class TestMember(Checker):

    @story('T149794 成员列表：添加成员')
    @story('T149741 成员列表：移除成员')
    @story('T149746 成员列表：成员列表展示详情 ')
    @story('141212 用户组详情页：移出用户组成员')
    def test_add_and_del_user(self, add_user_group):
        # 获取系统中存在的一个成员uuid
        member_uuid = MemberAction.get_member_uuid()
        with step('1、选择成员A、点击添加'):
            param_add = u.add_user([member_uuid])[0]
            param_add.uri_args({'user_group_uuid': add_user_group['group_uuid']})
            self.call(user.UserGroupAddUser, param_add).check_response('code', 200)
        with step('T149746 成员列表：成员列表展示详情 '):
            param = u.user_group_member_list(add_user_group['group_uuid'])[0]
            resp = go(project.ItemGraphql, param)
            resp.check_response('data.buckets[0].users[0].uuid', member_uuid)
            resp.check_response('data.buckets[0].pageInfo.count', 1)
        with step('移除成员'):
            self.call(user.UserGroupDelUser, param_add).check_response('code', 200)

    @story('T149792用户组列表：重命名用户组')
    @story('T150046 新建用户组（用户组名称重复）')
    def test_rename_user_group(self, add_user_group):
        with step('重命名用户组'):
            name = 'abc-group-name'
            param = u.user_grop_rename()[0]
            param.uri_args({'user_group_uuid': add_user_group['group_uuid']})
            param.json_update('name', name)
            self.call(user.UserGroupRename, param).check_response('code', 200)
        with step('用户组列表中存在重命名的用户组信息'):
            group_list = MemberAction.get_user_group_list()
            group_name_list = [r['name'] for r in group_list.value('data.buckets[0].userGroups')]
            assert name in group_name_list
        with step('新建用户组（用户组名称重复）'):
            param = data.user_group_add()[0]
            param.json_update('name', name)
            resp = go(project.UsesGroupAdd, param)
            resp.check_response('name', name)

    @story('T149798 精确查询用户组数据')
    @story('T149798 用户组 删除用户组')
    @story('T149743 用户组：新建用户组')
    @story('T149909 用户组：新建用户组（多团队）')
    @story('T149745 用户组列表：删除用户组')
    def test_add_del_user_group(self):
        with step('T149743 新增用户组'):
            group_name = 'group-name-' + mocks.num()
            param = data.user_group_add()[0]
            param.json_update('name', group_name)
            group_uuid = go(project.UsesGroupAdd, param).value('uuid')
        with step('T149798 精确查询用户组数据'):
            param = u.get_user_group_list()[0]
            param.json_update('variables.filter.name_match', group_name)
            resp = go(project.ItemGraphql, param)
            assert resp.value('data.buckets[0].userGroups[0].name') == group_name
            assert len(resp.value('data.buckets[0].userGroups')) == 1
            with step('T149745 删除用户组'):
                param.uri_args({'group_uuid': group_uuid})
                go(project.UsesGroupDelete, param, with_json=False)

    @story('141221 用户组：新建用户组时选择成员')
    def test_add_user_group_member(self):
        with step('新建用户组时选择成员'):
            member_uuid = MemberAction.get_member_uuid()
            param = data.user_group_add()[0]
            param.json_update('members', [member_uuid])
            group_uuid = go(project.UsesGroupAdd, param).value('uuid')
        with step('检查用户组成员列表'):
            param = u.user_group_member_list(group_uuid)[0]
            resp = go(project.ItemGraphql, param)
            resp.check_response('data.buckets[0].users[0].uuid', member_uuid)
            resp.check_response('data.buckets[0].pageInfo.count', 1)

    @story('T119083 成员管理：添加部门')
    @story('T119082成员管理：删除部门')
    def test_add_department(self):
        # 新增部门
        with step('添加部门'):
            depart_uuid = MemberAction.add_department()

        with step('删除部门'):
            param = t.del_department()[0]
            param.uri_args({'depart_uuid': depart_uuid})
            self.call(third.DeleteDepartment, param, with_json=False)

    @story('T119085 成员管理：添加子部门')
    def test_add_sub_department(self, add_user_group):
        department_uuid = add_user_group['department_uuid']
        with step('1、输入部门名称：示例子部门2、点击「确认」'):
            param = t.add_sub_department()[0]
            param.json_update('parent_uuid', department_uuid)
            resp = self.call(third.ADDSubDepartment, param)
            resp.check_response('add_department.parent_uuid', department_uuid)

    @story('T119090 成员管理：重命名部门')
    def test_rename_department(self, add_user_group):
        with step('重命名部门'):
            param = t.rename_departments()[0]
            param.json_update('uuid', add_user_group['department_uuid'])
            param.uri_args({'depart_uuid': add_user_group['department_uuid']})
            self.call(third.RenameDepartment, param)

    @story('T119073 成员管理-组织架构：部门添加单个成员')
    def test_add_one_member_department(self, add_user_group):
        with step('1、勾选成员B 2、点击「确认」'):
            member_uuid = MemberAction.get_member_uuid()
            param = t.add_member_into_department()[0]
            param.json_update('user_departments[0].user_uuid', member_uuid)
            param.json_update('user_departments[0].department_uuids', [add_user_group['department_uuid']])
            resp = self.call(third.UpdateDepartment, param)
            resp.check_response('success_count', 1)

    @story('T119074 自建部门下批量删除成员')
    @story('T119072  成员管理-组织架构：部门批量添加成员')
    @story('119037 成员管理-删除成员：自建部门下批量删除成员')
    def test_add_more_member_department(self, add_user_group):
        with step('部门批量添加成员'):
            # 获取五个用户
            member_uuids = MemberAction.get_member_uuid(num=5)
            param = t.add_member_into_department()[0]
            user_departments = []
            for u in range(len(member_uuids)):
                user_departments.append(
                    {'user_uuid': member_uuids[u], 'department_uuids': [add_user_group['department_uuid']]})
            param.json_update('user_departments', user_departments)
            resp = self.call(third.UpdateDepartment, param)
            resp.check_response('success_count', len(member_uuids))

        with step('查询部门成员情况'):
            param_info = t.department_member_gql(add_user_group['department_uuid'])[0]
            self.call(project.ItemGraphql, param_info).check_response('data.department.member_count', len(member_uuids))

        with step('成员管理-删除成员：自建部门下批量删除成员'):
            param_del = t.update_department()[0]
            param_del.json_update('departments_to_leave', [add_user_group['department_uuid']])
            param_del.json_update('variables.selectedUserUUIDs', member_uuids)
            param_del.json_update('variables.selectedDepartments', [add_user_group['department_uuid']])
            param_del.json_update('variables.excludeType', [10, 11])
            resp_del = self.call(third.UpdateDepartment, param_del)
            resp_del.check_response('success_count', len(member_uuids))

        with step('删除后查询部门成员情况'):
            param_info = t.department_member_gql(add_user_group['department_uuid'])[0]
            self.call(project.ItemGraphql, param_info).check_response('data.department.member_count', 0)

    @story('T119006 成员管理-根部门：成员批量加入部门')
    @story('T119029 根部门下批量删除成员')
    def test_batch_add_del_department_member(self, add_user_group):
        with step('成员管理-根部门：成员批量加入部门'):
            member_uuids = MemberAction.get_member_uuid(num=2)
            param_add = u.update_department_member()[0]
            param_add.json_update('departments_to_join', [add_user_group['department_uuid']])
            param_add.json_update('variables.selectedUserUUIDs', member_uuids)
            param_add.json_update('variables.excludeType', [10, 11])
            param_add.json_update('variables.memberStatus', ["pending", "disable", "normal"])
            resp_del = self.call(third.UpdateDepartment, param_add)
            resp_del.check_response('success_count', len(member_uuids))

    @story('T119074 成员管理-组织架构：检查部门之间的拖动排序')
    def test_(self):
        ...

    @story('T139020 信息安全设置：加密成员邮箱')
    @story('139016 信息安全设置：公开成员邮箱')
    def test_settings_security_info_email(self):
        with step('成员邮箱可见性选中：加密'):
            param = conf.user_security_setting()[0]
            self.call(user.UserSecuritySetting, param, status_code=200)

        with step('成员邮箱可见性选中：公开'):
            param.json_update('settings[0].value', 'public')
            self.call(user.UserSecuritySetting, param, status_code=200)

    @story('T139019 信息安全设置：获取成员方式受限')
    @story('T139017 信息安全设置：获取成员方式不受限')
    @story('139018 信息安全设置：获取成员方式不受限（成员小于30）')
    def test_settings_security_info_member(self):
        with step('获取成员方式受限'):
            param = conf.user_security_setting()[0]
            param.json_update('settings[0].name', 'is_search_get_member')
            param.json_update('settings[0].value', 'limit')
            self.call(user.UserSecuritySetting, param, status_code=200)
        with step('获取成员方式不受限'):
            param.json_update('settings[0].value', 'unlimited')
            self.call(user.UserSecuritySetting, param, status_code=200)
