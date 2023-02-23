"""
@File    ：third.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/18
@Desc    ：Account 接口定义
"""
from falcons.ops import ProjectOps
from selenium import webdriver


class SsoLogin(ProjectOps):
    """第三方统一登录"""
    uri = '/sso/login'
    name = '第三方统一登录'
    api_type = 'POST'


class SsoLoginTypes(ProjectOps):
    """统一获取登录类型"""
    uri = '/auth/login_types'
    name = '统一获取登录类型'
    api_type = 'GET'


class SsoLoginUrl(ProjectOps):
    """前端统一获取三方登录链接"""
    uri = '/sso/login_url'
    name = '前端统一获取三方登录链接'
    api_type = 'POST'


class SsoVerifyEmail(ProjectOps):
    """认证新的绑定邮箱"""
    uri = '/sso/verify_email'
    name = '认证新的绑定邮箱'
    api_type = 'POST'


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
class ThirdUserBind(ProjectOps):
    """个人中心手动绑定"""
    uri = '/organization/{org_uuid}/thirdparty/user/bind'
    name = '个人中心手动绑定'
    api_type = 'POST'


class ThirdUserBindings(ProjectOps):
    """个人中心用户绑定信息"""
    uri = '/organization/{org_uuid}/thirdparty/user/bindings'
    name = '个人中心用户绑定信息'
    api_type = 'GET'


class ThirdUserUnbind(ProjectOps):
    """个人中心用户解绑"""
    uri = '/organization/{org_uuid}/thirdparty/user/unbind'
    name = '个人中心用户解绑'
    api_type = 'POST'


class ThirdSupportedList(ProjectOps):
    """获取支持的第三方集成 获取已注册的第三方集成列表，列表中的内容表面是可以添加的"""
    uri = '/organization/{org_uuid}/thirdparty/supported/list'
    name = '获取支持的第三方集成'
    api_type = 'GET'


class ThirdAddOrUpdate(ProjectOps):
    """添加或更新基础信息"""
    uri = '/organization/{org_uuid}/thirdparty/base/add_or_update'
    name = '添加或更新基础信息'
    api_type = 'POST'


class ThirdList(ProjectOps):
    """获取已添加的集成"""
    uri = '/organization/{org_uuid}/thirdparty/list'
    name = '获取已添加的集成'
    api_type = 'GET'


class ThirdDetail(ProjectOps):
    """获取配置详情，这个接口返回了所有的配置字段，查询都可以用这个接口"""
    uri = '/organization/{org_uuid}/thirdparty/detail'
    name = '获取配置详情'
    api_type = 'POST'


class ThirdLoginUpdate(ProjectOps):
    """更新登录设置"""
    uri = '/organization/{org_uuid}/thirdparty/login/update'
    name = '更新登录设置'
    api_type = 'POST'


class ThirdStatusUpdate(ProjectOps):
    """更新状态设置"""
    uri = '/organization/{org_uuid}/thirdparty/status/update'
    name = '更新状态设置'
    api_type = 'POST'


class ThirdSyncUpdate(ProjectOps):
    """更新同步设置"""
    uri = '/organization/{org_uuid}/thirdparty/sync/update'
    name = '更新同步设置'
    api_type = 'POST'


class ThirdComposeConfig(ProjectOps):
    """获取集成组合设置"""
    uri = '/organization/{org_uuid}/thirdparty/compose_config'
    name = '获取集成组合设置'
    api_type = 'POST'


class ThirdMappingList(ProjectOps):
    """获取属性映射"""
    uri = '/organization/{org_uuid}/thirdparty/mapping/list'
    name = '获取属性映射'
    api_type = 'POST'


class ThirdPull(ProjectOps):
    """组织架构同步接口"""
    uri = '/organization/{org_uuid}/thirdparty/pull'
    name = '组织架构同步接口'
    api_type = 'POST'


class ThirdSyncProperties(ProjectOps):
    """获取同步源及属性映射"""
    uri = '/organization/{org_uuid}/thirdparty/sync_source_properties'
    name = '获取同步源及属性映射'
    api_type = 'GET'


class ThirdRemove(ProjectOps):
    """统一删除集成"""
    uri = '/organization/{org_uuid}/thirdparty/remove'
    name = '统一删除集成'
    api_type = 'POST'


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

class LdapExchangeToken(ProjectOps):
    """Ldap换token"""
    uri = '/ldap/exchange_token'
    name = 'Ldap换token'
    api_type = 'POST'


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

class _LdapOps(ProjectOps):
    """测试LDAP服务操作"""
    uri = 'http://cas.myones.net:9000/phpldapadmin/cmd.php'
    name = '测试LDAP服务操作'

    def __init__(self, token):
        super(_LdapOps, self).__init__(token, 'form-url-encode')

    def _parse_uri(self, **kwargs):
        """"""
        return self.uri

    def update_header(self, header: dict):
        """"""
        for k, v in header.items():
            self.session.cookies.set(k, v)

    def extra_header(self):
        return {'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent':
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}


class LdapCmdPost(_LdapOps):
    """"""
    api_type = 'POST'


class LdapCmdGet(_LdapOps):
    """"""
    api_type = 'GET'


class CasExecutionValue:
    """获取CAS登录的Execution值"""

    def __init__(self, url):
        ops = webdriver.ChromeOptions()
        # 关闭自动化受控提示
        ops.add_experimental_option('useAutomationExtension', False)
        ops.add_experimental_option('excludeSwitches', ['enable-automation'])
        ops.add_argument('headless')

        self.driver = webdriver.Chrome(options=ops)
        self.driver.get(url)

    def get_value(self):
        value = self.driver.find_element_by_name('execution').get_attribute('value')
        self.driver.quit()
        return value


class FakeApi(ProjectOps):
    """测试API mock服务操作"""

    def __init__(self, token):
        _ = token
        super(FakeApi, self).__init__()
        self.host = 'http://119.23.154.208'

    def _parse_uri(self, **kwargs):
        """"""

        return self.host + self.uri


class FakeApiUpdate(FakeApi):
    name = '更新 FAKE API 信息'
    uri = '/api/update'
    api_type = 'POST'


class FakeApiReset(FakeApi):
    name = '重置 FAKE API 信息'
    uri = '/api/reset'
    api_type = 'POST'


class FakeApiDelete(FakeApi):
    name = '删除 FAKE API 信息'
    uri = '/api/delete'
    api_type = 'POST'


class FakeApiAdd(FakeApi):
    name = '增加 FAKE API 信息'
    uri = '/api/add'
    api_type = 'POST'


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

class OrgDepartment(ProjectOps):
    """组织部门"""
    uri = '/team/{team_uuid}/items/graphql?t=gql-team-departments-data-key'
    name = '组织部门查询'
    api_type = 'POST'


class DepartmentMember(ProjectOps):
    """部门成员"""
    uri = '/team/{team_uuid}/items/graphql?t=paged-member-list-data-key-{depart_uuid}'
    name = '组织成员'
    api_type = 'POST'


class DisabledDepartment(ProjectOps):
    """已禁用部门成员"""
    uri = '/team/{team_uuid}/items/graphql?t=paged-member-list-data-key-disabled_members'
    name = '已禁用部门成员'
    api_type = 'POST'


class AllMember(ProjectOps):
    """所有成员"""
    uri = '/team/{team_uuid}/items/graphql?t=paged-member-list-data-key-all_member'
    name = '部门所有成员'
    api_type = 'POST'


class DeleteDepartment(ProjectOps):
    """删除部门"""
    uri = '/team/{team_uuid}/department/delete/{depart_uuid}'
    name = '删除部门'
    api_type = 'POST'


class ADDSubDepartment(ProjectOps):
    """添加子部门"""
    uri = '/team/{team_uuid}/departments/add'
    name = '添加子部门'
    api_type = 'POST'


class UpdateDepartment(ProjectOps):
    """成员变更部门"""
    uri = '/team/{team_uuid}/users/update/department'
    name = '成员变更部门'
    api_type = 'POST'


class RenameDepartment(ProjectOps):
    """重命名部门"""
    uri = '/team/{team_uuid}/department/update/{depart_uuid}'
    name = '重命名部门'
    api_type = 'POST'
