"""
@File    ：auth.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/21
@Desc    ：${END}
"""
from falcons.ops import ProjectOps


class LoginAuth(ProjectOps):
    """登录接口"""
    uri = '/auth/login'
    name = '认证登录'
    api_type = 'POST'


class TokenInfo(ProjectOps):
    """获取token信息"""
    uri = '/auth/token_info'
    name = '获取token信息'
    api_type = 'GET'


class AuthInviteJoin(ProjectOps):
    """加入团队"""
    uri = '/auth/invite_join_team'
    name = '加入团队'
    api_type = 'POST'


class AuthLoginSupport(ProjectOps):
    """获取绑定的第三方"""
    uri = '/auth/login_support'
    name = '获取绑定的第三方'
    api_type = 'POST'


class AuthLoginTypes(ProjectOps):
    """统一获取登录类型"""
    uri = '/auth/login_types'
    name = '统一获取登录类型'
    api_type = 'GET'
