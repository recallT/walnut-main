from falcons.helper import mocks
from falcons.ops import generate_param


def user_update(company: str, name: str, title: str):
    """

    """
    return generate_param({
        "company": company,
        "name": name,
        "title": title
    })


def add_user(members_list: list):
    """用户组新增成员"""
    return generate_param({
        "members": members_list
    })


def user_grop_rename():
    """rename"""
    return generate_param({
        "name": "abc-00" + mocks.num()
    })


def get_user_group_list():
    return generate_param({
        "query": "\n    {\n      buckets (\n        groupBy: {\n          userGroups: {}\n        },\n        pagination: $pagination,\n        filter: {\n          key_equal: \"bucket.0.__all\"\n        }\n      ) {\n        userGroups(\n          filter: $filter,\n          orderBy: {\n            namePinyin: ASC\n          }\n        ){\n          name\n          uuid\n        }\n        pageInfo {\n          count\n          totalCount\n          startPos\n          startCursor\n          endPos\n          endCursor\n          hasNextPage\n        }\n      }\n  }\n  ",
        "variables": {
            "filter": {},
            "pagination": {
                "limit": 50,
                "after": ""
            }
        }
    })


def user_group_member_list(user_group_uuid):
    return generate_param({
        "query": "{\n  buckets(groupBy: {users: {}}, pagination: {limit: 50, after: \"\", preciseCount: true}, filter: {key_equal: \"bucket.0.__all\"}) {\n    users(orderBy: {tag: DESC, namePinyin: ASC}, filterGroup: [{userGroups_in: $userGroupUUID, status_in: [\"normal\"]}]) {\n      key\n      name\n      avatar\n      email\n      team_member_status: teamMemberStatus\n      directDepartments {\n        name\n        uuid\n      }\n      uuid\n    }\n    key\n    pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n",
        "variables": {
            "searchKeyWord": "",
            "userGroupUUID": [
                user_group_uuid
            ]
        }
    })


def update_department_member():
    return generate_param({
        "user_departments": [],
        "all": True,
        "departments_to_join": [
            ""
        ],
        "query": "{ \n      users(\n        orderBy: {\n          tag: DESC\n          namePinyin: ASC\n        }\n        \n        filterGroup: [{\n          \n          directDepartments_in: $selectedDepartments\n          uuid_in: $selectedUserUUIDs\n          type_notIn: $excludeType\n          status_in: $memberStatus\n        }]\n        \n      ){\n        \n    uuid\n    name\n    email\n  \n      }\n   }",
        "variables": {
            "selectedUserUUIDs": [],
            "selectedUserGroupIds": [],
            "searchKeywords": "",
            "selectedDepartments": [],
            "memberStatus": [
                "pending",
                "disable",
                "normal"
            ],
            "excludeType": [
                10,
                11
            ]
        }
    })


def user_grant(uid):
    """用户授权"""
    p = {
        "users": [
            uid
        ],
        "fail_users": []
    }
    return generate_param(p)


def user_grant_remove(uid):
    """用户取消授权"""
    p = {
        "action": "delete",
        "type": 1,
        "user_uuids": [
            uid
        ]
    }
    return generate_param(p)
