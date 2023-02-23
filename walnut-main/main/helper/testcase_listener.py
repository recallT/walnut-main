# -*- coding: UTF-8 -*-
"""
@Project ：walnut 
@File    ：testcase_listener.py
@Author  ：zhangyonghui@ones.ai
@Date    ：7/26/22 10:22 AM 
@Desc    ：测试用例结果反写工具包
"""

import time

import requests

headers = {}
BASE_URL = 'https://our.ones.pro/'


def get_headers():
    global headers
    if not headers:
        headers = login_header()
    return headers


def get_data(environment):
    try:
        data = {'dev': {'url': 'https://our.ones.pro',
                        'username': 'zhangyonghui@ones.ai',
                        'pw': 'zyh123456'
                        }}
        return data[environment]['url'], data[environment]['username'], data[environment]['pw']
    except:
        raise print("参数有误")


def login_header():
    header = {"content-type": "application/json;charset=UTF-8"}
    data = {
        "password": "zyh123456",
        "captcha": "",
        "email": "zhangyonghui@ones.ai"
    }
    r = requests.post(url=BASE_URL + 'project/api/project/auth/login', headers=header, json=data).json()

    head = {"Cookie": "ones-uid=%s;ones-lt=%s" % (r['user']['uuid'], r['user']['token'])}

    return head


def get_testcase_uuid(plan_uuid):
    """获取测试计划所有用例UUId"""
    param = testcase_info(plan_uuid)
    resp = requests.post(url=BASE_URL + 'project/api/project/team/RDjYMhKq/items/graphql', headers=get_headers(),
                         json=param)
    assert resp.status_code == 200
    if not resp.json()['data']['buckets'][0]['testcasePlanCases']:
        raise ValueError(f'测试计划数据不存在 {plan_uuid}')
    return resp.json()


def get_case_intersection(testcase_nums: list, run_case_nums: list):
    """返回两个列表的交集"""
    return list(set(testcase_nums).intersection(set(run_case_nums)))


def testcase_info(plan_uuid):
    return {
        "query": "query PAGED_TESTCASE_PLAN_CASE_LIST($testCaseFilter: Filter, $planFilter: Filter, $moduleFilter: Filter, $orderByFilter: Filter) {\n  buckets(groupBy: {testcasePlanCases: {}}, pagination: {limit: 5000, after: \"\", preciseCount: false}) {\n    key\n    testcasePlanCases(filterGroup: $testCaseFilter, orderBy: $orderByFilter, limit: 10000) {\n      inCaseUUID\n      testcaseCase {\n        uuid\n        name\n        namePinyin\n        key\n        condition\n        createTime\n        desc\n        number\n        path\n        assign {\n          uuid\n          name\n        }\n        testcaseLibrary {\n          uuid\n          testcaseFieldConfig {\n            uuid\n            name\n          }\n        }\n        testcaseModule {\n          uuid\n          path\n        }\n        priority {\n          uuid\n        }\n        type {\n          uuid\n        }\n        relatedWikiPage\n      }\n      key\n      note\n      result\n      executor {\n        uuid\n        name\n      }\n    }\n    key\n    pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n  testcasePlans(filter: $planFilter) {\n    key\n    uuid\n    owner {\n      uuid\n      name\n    }\n    name\n    namePinyin\n    createTime\n    status {\n      name\n      uuid\n      category\n    }\n    members {\n      type\n      param\n    }\n    planStage {\n      value\n    }\n    relatedProject {\n      key\n      uuid\n      name\n      namePinyin\n    }\n    relatedSprint {\n      key\n      uuid\n      name\n      namePinyin\n    }\n    relatedIssueType {\n      key\n      uuid\n      name\n      namePinyin\n      detailType\n    }\n    assigns {\n      uuid\n      name\n    }\n    todoCaseCount\n    passedCaseCount\n    blockedCaseCount\n    skippedCaseCount\n    failedCaseCount\n    planReports {\n      uuid\n      name\n    }\n    checkPoints\n  }\n  fields(filter: {hidden_in: [false], pool_in: [\"testcase\"], context: {type_in: [\"team\"]}}, orderBy: {builtIn: DESC, createTime: ASC}) {\n    aliases\n    pool\n    name\n    uuid\n    namePinyin\n    fieldType\n    key\n    defaultValue\n    createTime\n    hidden\n    required\n    canUpdate\n    builtIn\n    allowEmpty\n    options {\n      uuid\n      value\n      color\n      bgColor\n    }\n    testcaseFieldConfigs(filter: $configFilter, orderBy: {namePinyin: ASC}) {\n      key\n      uuid\n      name\n      namePinyin\n    }\n  }\n}\n",
        "variables": {
            "testCaseFilter": [
                {
                    "testcasePlan_in": [
                        plan_uuid
                    ],
                    "testcaseCase": {}
                }
            ],
            "planFilter": {
                "uuid_in": [
                    plan_uuid
                ]
            },
            "orderByFilter": {
                "testcaseCase": {
                    "namePinyin": "ASC"
                }
            }
        }
    }


def str_int(arr_list):
    """字符列表转为数字列表"""
    arr = []
    for r in arr_list:
        arr.append(int(r))
    return arr


def update_test_plan(cases, plan_uuid):
    """更新测试计划执行结果"""
    if not cases:
        print("无需执行")
        return
    data = {
        "cases": cases,
        "is_batch": True
    }
    url = BASE_URL + '/project/api/project/team/RDjYMhKq/testcase/plan/{}/cases/update'.format(plan_uuid)
    resp = requests.post(url=url, headers=get_headers(), json=data)
    assert resp.status_code == 200



def data_processing(data, plan_uuid):
    """
    处理数据
    data = {"passed": ['2121','212121'], "failed": ['2121','2221213']}
    """
    times = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    resp = get_testcase_uuid(plan_uuid)
    testcase_plan_cases = resp['data']['buckets'][0]['testcasePlanCases']
    param_list = []
    for key, value in data.items():
        for r in str_int(list(set(value))):  # executor 执行人UUID
            [param_list.append({"uuid": i['testcaseCase']['uuid'], "executor": "GVbJ14TH", "result": key,
                                "note": "自动化执行结果反写" + times}) for i in testcase_plan_cases if
             i['testcaseCase']['number'] == r]
    return param_list


if __name__ == "__main__":
    ...
