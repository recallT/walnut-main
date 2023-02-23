"""
@File    ：third.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/18
@Desc    ：第三方认证配置测试数据
"""
import json

from falcons.com.meta import ApiMeta
from falcons.helper import mocks
from falcons.ops import org_param, generate_param

from main.params.const import ACCOUNT


def ldap_add():
    """添加ldap配置"""

    return org_param({
        "third_party_type": 3,
        "json_config": '{"host": "cas.myones.net", "port": 389, "type": "LDAP", "user_id": "cn",'
                       ' "encryption": "plain", "domain_base": "ou=zeno,dc=ldap,dc=example,dc=com",'
                       ' "user_filter": "", "enable_paging": false, "way_to_get_mail": 2,'
                       ' "domain_search_user": "cn=zeno_a,ou=z1,ou=zeno,dc=ldap,dc=example,dc=com",'
                       ' "domain_search_password": "12345678"}',
        "match_user_by": 1,
        "mappings": [
            {
                "system_property_key": "email",
                "third_party_property_key": "email"
            },
            {
                "system_property_key": "name",
                "third_party_property_key": "name"
            }
        ]
    })


def third_remove(t_type: int):
    """移除三方集成配置"""

    return org_param({
        'third_party_type': t_type,
    })


def third_update(status: str, t_type: int, enable=True):
    """
    集成状态/同步更新

    :param status: 状态 sync / status / login
    :param t_type: 三方集成类型
    :param enable: 开启/关闭
    :return:
    """
    return org_param({
        "third_party_type": t_type,
        "status_type": status,
        "enabled": enable
    })


def third_support_list():
    """
    三方集成登陆列表

    :return:
    """
    return org_param({})


def login_create_member(t_type: int, enable=True, team_uuid=None):
    """
    开启/关闭 登陆即创建成员

    :param t_type:
    :param enable:
    :param team_uuid: 指定团队uuid
    :return:
    """
    j = {
        "third_party_type": t_type,
        "login_create_user": enable,

    }
    if enable:
        j |= {"auto_join_team_uuid": ACCOUNT.user.team_uuid if not team_uuid else team_uuid}  # 默认加入本团队
    return org_param(j)


def ldap_exchange_token(user: str):
    """
    LDAP 获取token
    :param user: 测试用户默认有 zeno_a, zeno_b, zeno_c, zeno_d 四个，zeno_d 没有绑定邮箱
    :return:
    """
    return org_param({
        "auth_info": {
            "username": user,
            "password": "12345678"
        }
    }, need_org=False)


def third_list():
    """三方集成列表"""
    return org_param({})


def all_member_graph(is_pending=False):
    """获取所有团队成员"""
    status = ["pending",
              "disable",
              "normal"] if not is_pending else ['pending', ]
    return generate_param({
        "query": '{\n  buckets(groupBy: {users: {}}, pagination: {limit: 500, after: \"\", preciseCount: false})'
                 ' {\n    users(orderBy: {tag: DESC, namePinyin: ASC}, filterGroup: [{status_in: $memberStatus}],'
                 ' limit: 1000) {\n      key\n      name\n      avatar\n      email\n      company\n      '
                 'team_member_status: teamMemberStatus\n      directDepartments {\n        name\n      }\n'
                 '      userGroups {\n        name\n      }\n      sync_types: syncTypes\n      title\n      '
                 'uuid\n      invitation_is_pending: invitationIsPending\n      inviter {\n        name\n      '
                 '}\n      tag\n      id_number: idNumber\n    }\n    key\n    pageInfo {\n      count\n      '
                 'preciseCount\n      totalCount\n      startPos\n      startCursor\n      endPos\n      '
                 'endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n',
        "variables": {
            "selectedUserGroupIds": [],
            "searchKeywords": "",
            "selectedDepartments": [],
            "memberStatus": status
        }
    })


def third_detail(t_type: int):
    """获取三方集成配置详情"""
    return org_param({'third_party_type': t_type})


def third_sync_update(t_type: int, is_sync=True):
    """更新三方同步配置"""
    return org_param({

        "cron_sync": is_sync,
        "json_config": '',  # json 配置在用例中补充，一般从detail接口中获取后再修改而得
        "third_party_type": t_type,
    })


def third_add_or_update(t_type):
    """更新三方匹配规则"""
    return org_param({
        'third_party_type': t_type,
        'json_config': '',  # 以下数据都可从detail接口获取后再修改而得
        'match_user_by': 1,
        'mappings': [],
    })


def third_update_mapping_ldap(t_type: int):
    """ldap 更新自定义字段映射"""
    return org_param({
        'third_party_type': t_type,
        'json_config': '',  # 以下数据都可从detail接口获取后再修改而得
        'match_user_by': 1,
        'mappings': [{  # 添加一个ID映射
            "system_property_key": "id_number",
            "third_party_property_key": "employeeNumber"  # 映射为工号
        }, ],
    })


def third_user_bind(t_type: int):
    """个人中心三方用户绑定"""
    return org_param({
        'third_party_type': t_type,
        "org_uuid": "",
        'auth_info': '',  # 这里的数据来自三方登陆认证的返回的数据
    })


def third_user_unbind(t_type):
    """解除用户三方绑定"""
    return org_param({'third_party_type': t_type})


def third_user_bindings():
    """获取三方绑定用户信息"""
    return org_param({})


def third_pull(t_type: int):
    """三方集成同步接口"""
    return org_param({'third_party_type': t_type})


def invite_c():
    """邀请一个用户"""
    return generate_param({
        "invite_settings": [
            {
                "email": "zeno_c@ones.ai"
            }
        ],
        "license_types": [7, 8, 4, 5, 1, 3, 2]
    })


def delete_member():
    """删除成员"""
    return generate_param({'member': ''})


def batch_delete_member():
    """批量删除用户"""
    return generate_param({
        "members": [],
        "all": True,
        "variables": {
            "selectedUserUUIDs": [],  # 需要删除的用户UUID， 在用例中赋值
            "selectedUserGroupIds": [],
            "searchKeywords": "",
            "selectedDepartments": [],
            "memberStatus": [
                "pending",
                "disable",
                "normal"
            ],
            "excludeType": [
                10
            ]
        },
        "query": '{ \n      users(\n        orderBy: {\n          tag: DESC\n          namePinyin: ASC\n        }\n'
                 '        \n        filterGroup: [{\n          \n          \n          uuid_in: $selectedUserUUIDs\n'
                 '          type_notIn: $excludeType\n          status_in: $memberStatus\n        }]\n'
                 '        \n      ){\n        \n    uuid\n    name\n    email\n  \n      }\n   }'
    })


def batch_disabled_member():
    """批量禁用成员"""
    p = {
        "members": [],
        "all": True,
        "variables": {
            "selectedUserUUIDs": [],  # 需要删除的用户UUID， 在用例中赋值
            "selectedUserGroupIds": [],
            "searchKeywords": "",
            "selectedDepartments": [],  # 在用例中赋值
            "memberStatus": [
                "pending",
                "disable",
                "normal"
            ],
            "excludeType": [
                10
            ]
        },
        "query": '{ \n      users(\n        orderBy: {\n          tag: DESC\n          namePinyin: '
                 'ASC\n        }\n        \n        filterGroup: [{\n          \n          '
                 'directDepartments_in: $selectedDepartments\n          uuid_in: $selectedUserUUIDs\n'
                 '          type_notIn: $excludeType\n          status_in: $memberStatus\n        '
                 '}]\n        \n      ){\n        \n    uuid\n    name\n    email\n  \n      }\n   }'

    }
    return org_param(p)


def sso_login(t_type):
    """三方登陆接口"""
    return org_param({
        "third_party_type": t_type,
        "org_uuid": "",
        "auth_info": ""  # 同上
    }, need_org=False)


def user_me():
    return generate_param({})


# ==========================================================================================


class CasAccount:
    """cas统一调用账号"""
    a1 = {'username': 'cas_ones_test_1', 'password': 'Aa123456'}, {'email': 'cas_ones_test_1@ones.com'}
    a2 = {'username': 'cas_ones_test_2', 'password': 'Aa123456'}, {'email': 'cas_ones_test_2@ones.com'}
    a3 = {'username': 'cas_ones_test_3', 'password': 'Aa123456'}
    a4 = {'username': 'cas_ones_test_4', 'password': 'Aa123456'}
    # a5 = {'username': 'apiandcas', 'password': 'Aa123456'}, {'email': 'apiandcas@ones.com'}
    a5 = {'username': 'api_and_cas', 'password': 'Aa123456'}, {'email': 'api_and_cas@163.com'}


def cas_add():
    """添加cas配置"""
    return org_param({
        "third_party_type": 4,
        "json_config": "{\"cas_server_url\":\"https://cas.myones.net:8443/cas\"}",
        "match_user_by": 1,
        "mappings": [
            {
                "system_property_key": "name",
                "third_party_property_key": "name"
            },
            {
                "system_property_key": "email",
                "third_party_property_key": "email"
            }
        ]
    })


def cas_login_link():
    """cas登录链接"""
    return org_param({
        "org_uuid": "",
        "third_party_type": 4,
        "redirect_url": f"{ACCOUNT.host}/?redirect_path=%252Fprofile%252F3rd_party_binding&type=4"
    })


def sso_verify_email(email_name: str, v_type: int = 2):
    """"""
    return org_param({
        "email": f"{email_name}@ones.ai",
        "auth_code": '',  # 由三方登陆接口返回
        "type": v_type  # 这里默认为 2 具体值看三方集成调用
    }, need_org=False)


def cas_login_url():
    """cas配置中的登录url"""
    url = f"{ApiMeta.env.host}/project/#/3rd_party_connect/login_redirect?syncType=4&bindedOrgUUID={ACCOUNT.user.org_uuid}"
    return url


def disable_members():
    """配置中心-禁用成员"""
    return org_param({"members": []})


def api_mocks_add_user():
    """mock服务新建成员"""
    p = {"d_type": "members", "data": [{"userid": "api_and_cas", "name": "api_and_cas", "mobile": "13226512201",
                                        "department": ["21000"], "email": "api_and_csa@163.com"}]}
    return generate_param(p)


# ==========================================================================================


def wechat_add():
    """添加wechat配置"""
    return org_param({
        "third_party_type": 7,
        "json_config": "{\"corp_uuid\":\"wwa76530a1feeaaab1\",\"agent_id\":1000122,\"secret\":\"eWI_R7Vzrmu0e2TKJKqTWgftO1DzEq46CrcHN9MAI-c\",\"token\":\"V9oiH2rGITnRi1mx\",\"message_url\":\"https://mars-dev2.myones.net:10560/api/project/organization/7R2oDJ4A/wechat\",\"encoding_aes_key\":\"UyFQfR4reomyudvZPGzWvYllqJhq9lFxZ6e5GBlERFn\",\"redirect_domain\":\"mars-dev2.myones.net:10560\",\"home_url\":\"https://mars-dev2.myones.net:10560/project/#/team/RoHyC4oL/\"}",
        "match_user_by": 1,
        "mappings": [
            {
                "system_property_key": "name",
                "third_party_property_key": "name"
            },
            {
                "system_property_key": "email",
                "third_party_property_key": "email"
            }
        ]
    })


def wechat_login_link():
    """企业微信登录链接"""
    return org_param({
        "org_uuid": "",
        "third_party_type": 7,
        "redirect_url": f"{ACCOUNT.host}/?redirect_path=%252Fprofile%252F3rd_party_binding&type=7"
    })


# ==========================================================================================


def third_ydu_add():
    """添加有度集成"""
    return org_param({
        "third_party_type": 10,
        "json_config": '{\"server\":\"http://47.115.188.92:7080\",\"buin\":16101337,\"appid\":'
                       '\"yd58307B5B75204F8A8D675DE460F00285\",\"aes_key\":'
                       '\"uOPTp7g94K+B6SgQnUGbC9DrsO2/nQLL8diXHCga9b8=\"}'
    })


def third_ydu_bind(user: str):
    """有度用户绑定"""
    return org_param({
        "third_party_type": 10,
        "auth_info": json.dumps({'account': user}, ensure_ascii=False)
    })


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def third_api_add():
    """添加api集成"""
    return org_param({
        "third_party_type": 5,
        "json_config": "{\"user_id\":\"userid\",\"api_url\":\"http://119.23.154.208/api/sync\"}",
        "match_user_by": 1,
        "mappings": [
            {
                "system_property_key": "name",
                "third_party_property_key": "name"
            },
            {
                "system_property_key": "email",
                "third_party_property_key": "email"
            }
        ]
    })


def fake_api_update():
    """更新 mock api 数据"""
    return org_param({
        "d_type": "members",
        "data": [{
            "userid": "xiaobaigou",
            "employeeNumber": "1008611"
        }]
    })


def fake_api_del():
    """删除api服务用户数据"""
    return generate_param({
        "d_type": "members", "uuids": ["wukong"]  # uuid：齐天大圣测试数据
    })


def fake_api_members_add():
    """新增api服务用户数据"""
    return generate_param(
        {"d_type": "members", "data": [{"userid": "xcwtest", "name": "xcwtest", "mobile": "13226512200",
                                        "department": ["21000"], "email": ""}]})


def fake_api_departments_add():
    """新增api服务组织架构数据"""
    return generate_param(
        {"d_type": "departments", "data": [{"id": "21007", "name": "销售部", "parentid": "0", "order": 8}]})


def org_department():
    """查询组织部门信息"""
    p = {
        "query": '\n      {\n        departments(\n          orderBy: {\n            namePinyin: DESC\n'
                 '          }\n        ){\n          name\n          uuid\n          member_count:'
                 ' memberCount\n          sync_type: syncType\n          parent_uuid: parent\n'
                 '          next_uuid: next\n        }\n    }\n  '
    }
    return generate_param(p)


def department_member():
    """查询部门成员信息"""
    p = {
        "query": '{\n  buckets(groupBy: {users: {}}, pagination: {limit: 50, after: \"\", preciseCount: false})'
                 ' {\n    users(orderBy: {tag: DESC, namePinyin: ASC}, filterGroup: [{directDepartments_in:'
                 ' $selectedDepartments, type_notIn: $excludeType, status_in: $memberStatus}], limit: 1000)'
                 ' {\n      key\n      name\n      avatar\n      email\n      company\n      team_member_status:'
                 ' teamMemberStatus\n      directDepartments {\n        name\n      }\n      userGroups {\n'
                 '        name\n      }\n      sync_types: syncTypes\n      title\n      uuid\n'
                 '      invitation_is_pending: invitationIsPending\n      inviter {\n        name\n'
                 '      }\n      tag\n      id_number: idNumber\n      type\n      phone\n    }\n'
                 '    key\n    pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n'
                 '      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n'
                 '    }\n  }\n}\n',
        "variables": {
            "selectedUserGroupIds": [],
            "searchKeywords": "",
            "selectedDepartments": [
            ],
            "memberStatus": [
                "normal"
            ],
            "excludeType": [
                10
            ]
        }
    }
    return generate_param(p)


def department_info():
    """查询部门信息"""
    p = {
        "query": '{\n  buckets(groupBy: {users: {}}, pagination: {limit: 50, after: \"\", '
                 'preciseCount: false}) {\n    users(orderBy: {tag: DESC, namePinyin: ASC}, '
                 'filterGroup: [{type_notIn: $excludeType, status_in: $memberStatus}], limit: 1000) '
                 '{\n      key\n      name\n      avatar\n      email\n      company\n      '
                 'team_member_status: teamMemberStatus\n      directDepartments {\n        name\n      }\n      '
                 'userGroups {\n        name\n      }\n      sync_types: syncTypes\n      title\n      uuid\n'
                 '      invitation_is_pending: invitationIsPending\n      inviter {\n        name\n      }\n'
                 '      tag\n      id_number: idNumber\n      type\n      phone\n    }\n    key\n    '
                 'pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n'
                 '      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n'
                 '    }\n  }\n}\n',
        "variables": {
            "selectedUserGroupIds": [],
            "searchKeywords": "",
            "selectedDepartments": [],
            "memberStatus": [],
            "excludeType": [
                10
            ]
        }
    }
    return generate_param(p)


def all_member():
    """部门所有成员"""
    p = {
        "query": "{\n  buckets(groupBy: {users: {}}, pagination: {limit: 50, after: \"\", preciseCount: false}) {\n    users(orderBy: {tag: DESC, namePinyin: ASC}, filterGroup: [{type_notIn: $excludeType, status_in: $memberStatus}], limit: 1000) {\n      key\n      name\n      avatar\n      email\n      company\n      team_member_status: teamMemberStatus\n      directDepartments {\n        name\n      }\n      userGroups {\n        name\n      }\n      sync_types: syncTypes\n      title\n      uuid\n      invitation_is_pending: invitationIsPending\n      inviter {\n        name\n      }\n      tag\n      id_number: idNumber\n      type\n      phone\n    }\n    key\n    pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n",
        "variables": {
            "selectedUserGroupIds": [],
            "searchKeywords": "",
            "selectedDepartments": [],
            "memberStatus": [
                "pending",
                "disable",
                "normal"
            ],
            "excludeType": [
                10
            ]
        }
    }
    return generate_param(p)


def add_sub_department():
    """新增子部门"""
    return generate_param({
        "next_uuid": "",
        "parent_uuid": "",
        "name": f"add_test_{mocks.num()}"
    })


def del_department():
    return generate_param({})


def rename_departments():
    return generate_param({
        "member_count": 0,
        "name": "add_test-Rename-" + mocks.num(),
        "next_uuid": "",
        "parent_uuid": "",
        "sync_type": 0,
        "uuid": ""
    })


def add_member_into_department():
    """添加成员到部门中"""
    return generate_param({
        "user_departments": [
            {
                "user_uuid": "4V821mSN",
                "department_uuids": [
                    "2U2PXaqZ",
                ]
            }
        ]
    })


def department_member_gql(key):
    return generate_param({
        "query": "\n{\n  department(\n    key: $key\n  ){\n    member_count: memberCount\n  }\n}\n",
        "variables": {
            "key": "department-" + key
        }
    })



def update_department():
    """更新成员所属部门"""
    p = {
        "user_departments": [],
        "all": True,
        "departments_to_join": [],  # 用例中赋值加入的部门uuid
        "query": '{ \n      users(\n        orderBy: {\n          tag: DESC\n          namePinyin: '
                 'ASC\n        }\n        \n        filterGroup: [{\n          \n          '
                 'directDepartments_in: $selectedDepartments\n          uuid_in: $selectedUserUUIDs\n'
                 '          type_notIn: $excludeType\n          status_in: $memberStatus\n        }]\n'
                 '        \n      ){\n        \n    uuid\n    name\n    email\n  \n      }\n   }',
        "variables": {
            "selectedUserUUIDs": [],  # 用例中赋值移动的成员uuid
            "selectedUserGroupIds": [],
            "searchKeywords": "",
            "selectedDepartments": [],  # 用例中赋值
            "memberStatus": [
                "normal"
            ],
            "excludeType": [
                10
            ]
        }
    }
    return generate_param(p)


def rename_department():
    """重命名部门"""
    return generate_param({
        "name": "RenameApi",
        "next_uuid": "",
        "parent_uuid": "",
        "sync_type": 5,
        "uuid": "",  # 用例中赋值
        "_fStamp": 1646300586571
    })
