"""
@File    ：member.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/4/1
@Desc    ：成员与权限操作
"""
from falcons.check import go
from falcons.com.env import User
from falcons.com.nick import step

from main.actions.team import TeamAction
from main.api import project as prj, third, project, user
from main.params import auth, conf, proj, data
from main.params import third as t
from main.params import user as u
from main.params.conf import role_add, update_proj_members
from main.params.const import ACCOUNT
from main.params.data import delete_member


class MemberAction:
    """
    成员与权限操作
    创建并激活成员
    给成员分配权限
    等等操作
    """

    @classmethod
    def new_member(cls, active=True, token=None, custom_email=None) -> User:
        """
        创建一个新成员
        :param active: 是否激活，默认激活
        :param token:
        :param custom_email: 指定邮箱，默认可不传
        :return:
        """

        with step('添加一个成员到团队'):
            p = auth.invitation(single=True)[0]
            if custom_email:
                p.json['invite_settings'][0]['email'] = custom_email

            mail = p.json['invite_settings'][0]['email']

            ia = go(prj.InvitationsAdd, p, token)
            # 获取邀请码
            h = auth.invitation_history()[0]
            ih = go(prj.InvitationsHistory, h, token)

            # 邀请码
            invite_code = [c['code'] for c in ih.json()['invitations'] if c['email'] == mail]

            jt = auth.join_team()[0]
            passwd = jt.json_value('password')
            jt.json |= {'email': mail, 'invite_code': invite_code[0], 'name': mail.split('@')[0]}

            new_user = User(mail, passwd)
            if active:
                with step('加入团队'):
                    aj = go(prj.AuthInviteJoin, jt, token)
                    # 获取新成员uuid 和密码
                    # _member |= {'uuid': aj.json()['user']['uuid'], 'password': jt.json['password']}

                    new_user.uuid = aj.json()['user']['uuid']
                    new_user.owner_uuid = aj.json()['user']['uuid']

            return new_user

    @classmethod
    def update_permission(cls, user_uuid, token=None, **kwargs):
        """更新用户权限"""
        pass

    @classmethod
    def del_member(cls, user_uuid, token=None):
        """删除成员"""
        d_param = delete_member()[0]
        d_param.json_update('member', user_uuid)
        res = go(prj.DeleteMember, d_param, token)

        return res

    @classmethod
    def del_members(cls, uuids: [str]):
        """批量删除成员"""
        param = t.batch_delete_member()[0]
        param.json['variables']['selectedUserUUIDs'] = uuids
        go(prj.DeleteMembersBatch, param)

    @classmethod
    def add_member_role(cls, token=None):
        """配置中心-新增角色"""
        param = role_add()[0]
        resp = go(prj.RolesAdd, param, token)
        return resp

    @classmethod
    def del_member_role(cls, role_uuid):
        """
        删除配置中心项目角色
        :param role_uuid: 项目角色UUID
        :return:
        """
        p = conf.delete_field()[0]
        p.uri_args({'role_uuid': role_uuid})
        go(prj.RoleDelete, p)

    @classmethod
    def get_member_list(cls, token=None, project_uuid=ACCOUNT.project_uuid):
        """
        获取项目角色列表
        :param token:
        :param project_uuid: 项目UUID
        :return:
        """

        param = conf.member_list()[0]
        param.uri_args({'project_uuid': project_uuid})
        resp = go(prj.ProjectRoleMembers, param, token)
        return resp

    @classmethod
    def add_proj_role(cls, role_uuid, token=None):
        """
        项目内新增角色
        :param role_uuid: 配置中心的角色uuid
        :param token:
        :return:
        """
        r_a = conf.project_roles_add()[0]
        a = prj.ProjectRoleAdd(token)
        r_a.json['role_uuids'].append(role_uuid)
        a.call(r_a.json, **r_a.extra)

    @classmethod
    def add_proj_member(cls, user_uuid, token=None, project_uuid=ACCOUNT.project_uuid):
        """
        新增单个成员到项目内
        :param user_uuid: 成员的uuid
        :param token:
        :param project_uuid: 项目UUID
        :return:
        """
        resp = MemberAction.get_member_list(token, project_uuid=project_uuid)
        resp_role_uuid = resp.value('role_members[0].role.uuid')
        members = resp.value('role_members[0].members')
        members.insert(0, user_uuid)

        param = update_proj_members(members)[0]
        param.uri_args({"role_uuid": resp_role_uuid})
        param.uri_args({"project_uuid": project_uuid})
        resp = go(prj.ProjAddMembers, param, token)
        assert user_uuid in resp.value('role_members[0].members')

    @classmethod
    def del_proj_member(cls, members: list, token=None, project_uuid=ACCOUNT.project_uuid):
        """
        删除项目内成员
        :param members: 被删除的用户uuid list
        :param token:
        :param project_uuid: 项目UUID
        :return:
        """
        resp = MemberAction.get_member_list(token)
        resp_role_uuid = resp.value('role_members[0].role.uuid')
        param = update_proj_members(members)[0]
        param.uri_args({"role_uuid": resp_role_uuid})
        param.uri_args({"project_uuid": project_uuid})
        resp = go(prj.ProjDelMembers, param, token)
        assert members not in resp.value('role_members[0].members')

    @classmethod
    def get_member_uuid(cls, keyword='normal', num=1, token=None):
        """
        查询系统内存在的member 成员uuid
        :param keyword: 查询关键字
        :param num: 返回user_uuid 个数
        :param token:
        :return:默认返回第一个成员uuid num>1时，返回member_uuids 成员uuid 列表
        """
        su_param = proj.program_search_user(keyword=keyword)[0]
        resp = go(prj.UsesSearch, su_param, token)

        member_uuids = []
        if len(resp.value('users')) < num:
            num = len(resp.value('users'))
        for i in range(num):
            member_uuids.append(resp.value('users[%d].uuid' % i))
        if num == 1:
            return member_uuids[0]
        return member_uuids

    @classmethod
    def get_user_group_list(cls):
        """
        查询用户组列表
        :return:
        """
        param = u.get_user_group_list()[0]
        resp = go(prj.ItemGraphql, param)
        return resp

    @classmethod
    def add_department(cls):
        """
        新增部门
        :return: 部门depart_uuid
        """
        param = t.add_sub_department()[0]
        depart_uuid = go(third.ADDSubDepartment, param).value('add_department.uuid')
        return depart_uuid

    @classmethod
    def del_department(cls, uuid):
        """
        删除部门
        :param uuid:
        :return:
        """
        param2 = t.del_department()[0]
        param2.uri_args({'depart_uuid': uuid})
        go(third.DeleteDepartment, param2, with_json=False)

    @classmethod
    def add_department_user(cls, did, uid, token=None):
        """
        添加用户到部门
        :param did:
        :param uid:
        :param token:
        :return:
        """
        param1 = t.update_department()[0]
        param1.json['departments_to_join'].append(did)
        param1.json['variables']['selectedUserUUIDs'].append(uid)
        param1.json['variables']['selectedDepartments'].append('department003')  # department003:未分配部门
        return go(third.UpdateDepartment, param1, token=token)

    @classmethod
    def add_user_group(cls, members: [str] = None, token=None):
        """
        新增用户组
        :param members: 可选，user uuid list
        :param token: 可选
        :return:
        """
        param = data.user_group_add()[0]
        param.json_update('members', members)
        res = go(project.UsesGroupAdd, param, token=token)
        return res.value('uuid')

    @classmethod
    def del_user_group(cls, uuid):
        """删除用户组"""
        param = data.user_group_add()[0]
        param.uri_args({'group_uuid': uuid})
        go(project.UsesGroupDelete, param, with_json=False)

    @classmethod
    def user_grant(cls, uid):
        """
        用户授权
        :param uid:
        :return:
        """
        param = u.user_grant(uid)[0]
        team_info, _ = TeamAction.team_info(ACCOUNT.user.team_uuid)
        param.uri_args({'org_uuid': team_info['org_uuid']})
        go(user.UserGrant, param)

    @classmethod
    def user_grant_remove(cls, uid):
        """
        用户取消授权
        :param uid:
        :return:
        """
        param = u.user_grant_remove(uid)[0]
        team_info, _ = TeamAction.team_info(ACCOUNT.user.team_uuid)
        param.uri_args({'org_uuid': team_info['org_uuid']})
        go(user.UserGrant, param)
