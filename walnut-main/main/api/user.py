from falcons.ops import ProjectOps


class UserUpdate(ProjectOps):
    """绑定案例"""
    uri = '/users/update'
    name = '更新用户信息'
    api_type = 'POST'


class UserGroupAddUser(ProjectOps):
    uri = '/team/{team_uuid}/usergroup/{user_group_uuid}/add_user'
    name = '用户组新增成员'
    api_type = 'POST'


class UserGroupDelUser(ProjectOps):
    uri = '/team/{team_uuid}/usergroup/{user_group_uuid}/delete_user'
    name = '用户组移除成员'
    api_type = 'POST'


class UserGroupRename(ProjectOps):
    uri = '/team/{team_uuid}/usergroup/{user_group_uuid}/rename'
    name = '用户组重命名'
    api_type = 'POST'


class UserSecuritySetting(ProjectOps):
    uri = '/team/{team_uuid}/config/update'
    name = '信息安全设置'
    api_type = 'POST'


class UserGrant(ProjectOps):
    uri = '/organization/{org_uuid}/license/grant'
    name = '用户授权'
    api_type = 'POST'


class UserGrantRemove(ProjectOps):
    uri = '/organization/{org_uuid}/license/grant'
    name = '已授权用户列表'
    api_type = 'GET'




class UserGrantList(ProjectOps):
    uri = '/organization/{org_uuid}/license/project/grant_users'
    name = '已授权用户列表'
    api_type = 'GET'
