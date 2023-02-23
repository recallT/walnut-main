"""
@File    ：extra.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/6/16
@Desc    ：
"""
import random
import time
from functools import wraps

from falcons.com.meta import OnesParams
from falcons.helper.mocks import ones_uuid
from main.api import case as api, third, project as np, issue, layout

TIME_SEQUENCE = 10.5  # 延长一点时间，老是失败


def retry(func):
    """"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        for i in range(3):
            try:
                r = func(*args, **kwargs)
                return r
            except Exception as e:
                seed = round(TIME_SEQUENCE + random.randint(1000, 4000) / 1000, 3)

                print(f'{"-*" * 40}执行失败！{"-*" * 40}', f'{e}', f'{"-*" * 84}', sep='\n')
                print(f'{seed}s秒后重试第 {i + 1} 次...')

                continue
        else:
            raise RuntimeError(f'执行 [{func.__name__}] 失败！')

    return wrapper


class Extra:
    """
    测试套件前后置动作
    准备测试数据
    清理测试数据等
    """

    def __init__(self, constant):
        self.cont = constant
        self.account = constant.account.user
        self.param = OnesParams()

        self.param.uri_args({
            'team_uuid': self.account.team_uuid,
        })

    def switch_local_layout(self):
        """
        DEV 环境和私有部署环境，默认切换为本地视图
        :return:
        """
        issue_names = '任务', '需求', '缺陷', '子任务', '子需求',
        # 获取默认工作项类型的UUID
        self.param.json = {"issue_type": 0}
        issue_types = self._execute_(np.TeamStampData)
        u_id = [(u['uuid'], u['name']) for u in issue_types['issue_type']['issue_types'] if u['name'] in issue_names]

        # 本地视图 layout_uuid 为空
        self.param.json = {'layout_uuid': ''}
        for u in u_id:
            self.param.uri_args({'issue_uuid': u[0]})
            print(f'切换 {u[1]} 的默认视图为本地视图...')
            self._execute_(layout.GlobalSwitchLayout)

    def teardown(self, *args):
        """
        清理测试数据动作
        测试用例执行完后全局执行


        :param args: 项目UUID
        :return:
        """
        self.clear_custom_field()
        self.clear_proj_role()
        self.clear_library()
        self.clear_product()

        self.clear_test_plan()
        self.clear_progress()
        self.clear_card()
        if args:  # 清理测试项目
            for a in args:
                if a:
                    self.del_project(a)

        self.clear_config_issue_field()
        self.clear_config_issue_status()
        self.clear_config_issue()
        self.clear_departments()
        self.clear_user_group()

    def new_project(self, name, project_type='project-t1'):
        """
        创建项目
        :param project_type: 项目类型 敏捷项目 瀑布 通用
        :param name:
        :return:
        """

        for i in range(3):
            uuid = ones_uuid(self.account.owner_uuid)

            self.param.json = {
                'project': {
                    'uuid': uuid,
                    'owner': self.account.owner_uuid,
                    'name': name,
                    'status': 1,
                    'members': []
                },
                'template_id': project_type,  # 敏捷项目
                'members': [
                    self.account.owner_uuid,
                ]
            }

            try:
                self._execute_(np.AddProject)

                print(f'创建敏捷项目，uuid：{uuid}')
                return uuid

            except AssertionError:
                print(f'创建第{i + 1}次失败，间隔10秒， 重试中....')
                time.sleep(TIME_SEQUENCE)
                continue

    def team_stamp(self):
        """获取团队配置信息"""

        self.param.json = {
            'issue_type_config': 0,  # 工作项类型配置
            'issue_type': 0,  # 工作项配置
            'field_config': 0,  # 属性配置
            'task_status': 0,  # 状态UUID
            'field': 0,  # 工作项属性
            'role': 0  # 工作项角色

        }
        self.param.uri_args({'project_uuid': self.cont.account.project_uuid})

        stamp_resp = self._execute_(np.TeamStampData)

        # 提取本项目的配置数据即可

        field_config = [
            f for f in stamp_resp['field_config']['field_configs'] if
            f['project_uuid'] == self.cont.account.project_uuid
        ]
        issue_type_config = [
            f for f in stamp_resp['issue_type_config']['issue_type_configs'] if
            f['project_uuid'] == self.cont.account.project_uuid
        ]

        curr_prj_stamp = {
            'field_config': {'field_configs': field_config},
            'issue_type_config': {'issue_type_configs': issue_type_config},
            'task_status': stamp_resp['task_status'],
            'issue_type': stamp_resp['issue_type'],
            'fields': stamp_resp['field']['fields'],
            'roles': stamp_resp['role']['roles']
        }

        self.cont.account.stamp_data = curr_prj_stamp

        return curr_prj_stamp

    def del_project(self, uuid):
        """
        删除项目

        :param uuid:
        :return:
        """

        self.param.uri_args({'project_uuid': uuid})
        self._execute_(np.DeleteProject, no_json=True)

    def fetch_all_projects(self) -> list:
        """
        获取测试团队下所有的项目
        :return:
        """
        gq = np.ItemGraphql()

        self.param.json = {
            'query': '{\n  buckets(groupBy: $groupBy, pagination: {limit: 500, after: \"\", preciseCount: true}) {\n    key\n    projects(limit: 1000, orderBy: $projectOrderBy, filterGroup: $projectFilterGroup) {\n      key\n      sprintCount\n      taskCount\n      taskCountDone\n      taskCountInProgress\n      taskCountToDo\n      memberCount\n      uuid\n      name\n      status {\n        uuid\n        name\n        category\n      }\n      isPin\n      isSample\n      isArchive\n      statusCategory\n      assign {\n        uuid\n        name\n        avatar\n      }\n      owner {\n        uuid\n        name\n        avatar\n      }\n      createTime\n      planStartTime\n      planEndTime\n      type\n    }\n    key\n    pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n',
            'variables': {
                'projectOrderBy': {
                    'isPin': 'DESC',
                    'namePinyin': 'ASC',
                    'createTime': 'DESC'
                },
                'projectFilterGroup': [
                    {
                        'visibleInProject_equal': True,
                        'isArchive_equal': False
                    }
                ],
                'groupBy': {
                    'projects': {

                    }
                }
            }
        }
        gq.call(self.param.json, **self.param.extra)

        gq.is_response_code(200)
        pj = gq.json()['data']['buckets'][0]['projects']

        uuids = [p['uuid'] for p in pj]
        print(f'All project{uuids}')

        return uuids

    def clear_library(self):
        """清除用例库"""
        self.param.json = {
            'query': 'query QUERY_LIBRARY_LIST{\n  testcaseLibraries(\n    orderBy:{\n      isPin:DESC\n      '
                     'namePinyin:ASC\n    }\n  ){\n    uuid,\n    name,\n    isPin,\n    isSample,\n    '
                     'testcaseCaseCount,\n    testcaseFieldConfig{\n      key,\n      uuid,\n      '
                     'name\n    }\n  }\n}',
            'variables': {}
        }
        q = np.ItemGraphql()
        q.call(self.param.json, **self.param.extra)
        q.is_response_code(200)

        # 获取所有用例库uuid
        uuids = q.json()['data']['testcaseLibraries']
        if uuids:
            # 删除用例库中的所有用例
            d = api.DeleteLibrary()
            for i in uuids:
                if i['uuid']:
                    self.param.uri_args({'team_uuid': self.account.team_uuid, 'library_uuid': i['uuid']})
                    d.call(**self.param.extra)
            d.is_response_code(200)
            d.check_response('type', 'OK')

    def clear_custom_field(self):
        """
        清理自定义项目属性

        :return:
        """
        self.param.json = _view_filed()

        view = self._execute_(np.ItemsView)

        keys = [k['key'] for k in view['items'] if not k['built_in']]
        print(f'keys{keys}')
        d = np.ItemDelete()

        def _delete(item_key):
            self.param.uri_args({'item_key': item_key})
            d.call(**self.param.extra)

        for k in keys:
            for i in range(10):
                print(f'清理自定义属性 {i + 1}...')
                _delete(k)
                if d.response.status_code == 200 or d.response.status_code == 801:
                    break
                else:
                    time.sleep(1)

    def clear_proj_role(self):
        """清除项目角色"""
        stamp = self.team_stamp()

        roles_uuid = [u['uuid'] for u in stamp['roles'] if not u['built_in']]

        if roles_uuid:
            for uuid in roles_uuid:
                self.param.uri_args({'role_uuid': uuid})

                try:
                    self._execute_(np.RoleDelete)
                except AssertionError:
                    print('InUse.Role')

    def clear_card(self):
        """清理自定义卡片"""
        # 1. 获取dashboard uuid

        self.param.json = {'dashboard': 0}
        dash = self._execute_(np.TeamStampData)
        dashboards = dash['dashboard']['dashboards']
        if dashboards:
            dash_uuid = dashboards[0]['uuid']

            self.param.json = _card_gql(dash_uuid)
            card = self._execute_(np.ItemGraphql)
            cards = card['data']['cards']

            # 获取默认卡片UUID
            default_cards = '使用引导', '我负责的工作项', '最近浏览的项目', '最近浏览的页面组',
            stay_cards = {c['uuid']: d for c in cards for d in default_cards if c['name'] == d}

            default_layout = default_card_layout()

            for dl in default_layout['cards']:
                dl['dashboard_uuid'] = dash_uuid
                for sk, sv in stay_cards.items():
                    if dl['name'] == sv:
                        dl['uuid'] = sk

            # 设置为默认卡片
            self.param.json = default_layout
            self.param.uri_args({'dashboard_uuid': dash_uuid})
            self._execute_(np.DashboardCardLayout)

    def clear_test_plan(self):
        """清除测试计划"""

        self.param.json = plan_list()
        q = np.ItemGraphql()
        q.call(self.param.json, **self.param.extra)
        q.is_response_code(200)

        # 获取所有测试计划 uuid
        plans = q.json()['data']['buckets'][0]['testcasePlans']
        uuids = [p['uuid'] for p in plans]
        if uuids:
            # 删除测试计划
            d = api.DeletePlan()
            for i in uuids:
                if i:
                    self.param.uri_args({'team_uuid': self.account.team_uuid, 'plan_uuid': i})
                    d.call(**self.param.extra)
            d.is_response_code(200)
            d.check_response('type', 'OK')

    def clear_progress(self):
        """清除未关闭的进度管理器"""
        self.param.json = ''
        res = self._execute_(np.QueuesList)
        process_uuid = [q['uuid'] for q in res['batch_tasks']]

        if process_uuid:
            try:
                self.param.json = {'uuids': process_uuid}
                self._execute_(np.HiddenProgress)
            except AssertionError:
                print('进度器有正在进行中的任务，无法关闭')

    def clear_config_issue_field(self):
        """清除配置中心-自定义工作项属性"""
        stamp = self.team_stamp()

        issue_names = '任务', '需求', '缺陷', '子任务', '子需求'
        issue_uuids = [u['uuid'] for u in stamp['issue_type']['issue_types'] if
                       u['name'] in issue_names]

        fields = [f['uuid'] for f in stamp['fields'] if f['built_in'] is False and f['search_option'] == 1]

        if fields:
            for f in fields:
                self.param.uri_args({'field_uuid': f})
                try:
                    self._execute_(np.FieldDelete)
                except AssertionError:
                    # 如果异常则先在工作项类型的属性内删除被引用的属性
                    for i_uuid in issue_uuids:
                        self.param.uri_args({'issue_uuid': i_uuid})
                        resp = self._execute_(issue.IssueFieldConfig, no_json=True)  # 查询工作项属性配置

                        del_field_uuid = [f['field_uuid'] for f in resp[0]['items'] if 'field' not in f['field_uuid']]

                        # 删除工作项类型里自定义的属性
                        if del_field_uuid:
                            for del_uuid in del_field_uuid:
                                self.param.uri_args({'field_uuid': del_uuid})
                                self._execute_(issue.IssueFieldDelete, no_json=True)

                    try:
                        # 删除自定义工作项属性
                        self.param.uri_args({'field_uuid': f})
                        self._execute_(np.FieldDelete)
                        break
                    except AssertionError:
                        print('errcode: InUse.Field.UsedInIssueTypeTemplate')

    def clear_config_issue_status(self):
        """清除配置中心-自定义工作项状态"""
        stamp = self.team_stamp()
        n_uuids = [s['uuid'] for s in stamp['task_status']['task_statuses'] if 'in_' in s['name'] or 'up_' in s['name']]

        if n_uuids:
            for u in n_uuids:
                issue_uuid = [u['uuid'] for u in stamp['issue_type']['issue_types']
                              if u['name'] == '任务'][0]

                self.param.uri_args({'status_uuid': u})
                self.param.uri_args({'issue_uuid': issue_uuid})

                # 清除工作项工作流中被使用的工作项状态
                try:
                    self._execute_(issue.IssueStatusDelete)
                except AssertionError:
                    print('errcode: 工作项工作流无使用该状态')

                # 清除工作项状态
                time.sleep(1)
                try:
                    self._execute_(issue.StatusDelete)
                except AssertionError:
                    print('errcode: InUse.TaskStatus')

    def clear_config_issue(self):
        """清除配置中心-自定义工作项"""
        stamp = self.team_stamp()

        issue_types = [u['uuid'] for u in stamp['issue_type']['issue_types'] if
                       ('Std' in u['name']) or ('子Sub' in u['name'])]

        if issue_types:
            for uuid in issue_types:
                self.param.uri_args({'issue_uuid': uuid})

                try:
                    self._execute_(issue.IssueDelete)
                except AssertionError:
                    print('InUse.IssueTyp')

    def clear_product(self):
        """删除测试产品数据"""
        self.param.json = _get_product_key()
        products = self._execute_(np.ItemGraphql)
        p_key = [p['key'] for p in products['data']['buckets'][0]['products']]

        for key in p_key:
            self.param.uri_args({'item_key': key})
            self._execute_(np.ItemDelete)

    def _execute_(self, api_class, no_json=False) -> dict:
        """

        :param api_class:
        :param no_json: 不传json数据 默认False
        :return:
        """

        inst = api_class()
        if not no_json:
            inst.call(self.param.json, **self.param.extra, is_print=False)
        else:
            inst.call(**self.param.extra, is_print=False)
        inst.is_response_code(200)

        return inst.json()

    def close_notify(self):
        """关闭配置中心工作项通知"""
        issue_names = '任务', '需求', '缺陷', '子任务', '子需求', '发布',
        stamp = self.team_stamp()

        issue_uuid_list = [u['uuid'] for u in stamp['issue_type']['issue_types'] if
                           u['name'] in issue_names]

        self.param.json = update_notice_center()

        for uuid in issue_uuid_list:
            self.param.uri_args({'issue_type_uuid': uuid})

            try:
                self._execute_(issue.UpdateAllNoticeMethods)
            except AssertionError as e:
                print(f'关闭配置中心工作项通知异常:{e}')
                break

    def clear_departments(self):
        """清除测试部门数据"""
        self.param.json = departments_gql()
        products = self._execute_(np.ItemGraphql)
        p_uuid = [p['uuid'] for p in products['data']['departments'] if 'add_test' in p['name']]

        for depart_uuid in p_uuid:
            self.param.uri_args({'depart_uuid': depart_uuid})
            self._execute_(third.DeleteDepartment)

    def clear_user_group(self):
        """清除测试用户组数据"""
        self.param.json = user_group_gql()
        products = self._execute_(np.ItemGraphql)
        p_uuid = [p['uuid'] for p in products['data']['buckets'][0]['userGroups'] if 'abc-' in p['name']]

        for group_uuid in p_uuid:
            self.param.uri_args({'group_uuid': group_uuid})
            self._execute_(np.UsesGroupDelete)


def _get_product_key():
    """"""
    return {
        "query": "\n    {\n      buckets(groupBy: $groupBy, orderBy: $orderBy) "
                 "{\n        key\n        \n        products(filterGroup: "
                 "$productsFilter, orderBy: $productsOrderBy) {\n          "
                 "name\n          uuid\n          key\n          "
                 "createTime\n        }\n      }\n    }",
        "variables": {
            "orderBy": {},
            "groupBy": {
                "products": {}
            },
            "productsOrderBy": {
                "createTime": "DESC"
            },
            "productsFilter": []
        }
    }


def _card_gql(dashboard_uuid):
    return {
        'query': '\n    query {\n      cards (\n        filter: {\n          objectId_equal: \"%s\"\n          '
                 'objectType_equal: \"dashboard\"\n          status_equal: \"normal\"\n        },\n        '
                 'orderBy: {  layoutY: ASC, layoutX: ASC }\n      ) {\n        key\n        uuid\n        '
                 'name\n        description\n        type\n        layoutX\n        layoutY\n        '
                 'layoutW\n        layoutH\n        config\n      }\n    }\n  ' % dashboard_uuid,
        'variables': {}
    }


def default_card_layout():
    return {
        'cards': [
            {
                'uuid': '4pccVP8r',  # uuid 和 dashboard_uuid 需要替换
                'dashboard_uuid': 'SF5VJdrP',
                'name': '使用引导',
                'layout': {
                    'x': 0,
                    'y': 0,
                    'w': 6,
                    'h': 4
                },
                'type': 'beginner_guide',
                'config': {}
            },
            {
                'uuid': 'TBxUCEQ6',
                'dashboard_uuid': 'SF5VJdrP',
                'name': '最近浏览的项目',
                'layout': {
                    'x': 0,
                    'y': 4,
                    'w': 6,
                    'h': 3
                },
                'type': 'recent_projects',
                'config': {}
            },
            {
                'uuid': 'RZAiuk9q',
                'dashboard_uuid': 'SF5VJdrP',
                'name': '我负责的工作项',
                'layout': {
                    'x': 6,
                    'y': 0,
                    'w': 6,
                    'h': 4
                },
                'type': 'task_list',
                'config': {
                    'project_uuid': "",
                    'filter_uuid': 'ft-t-001'
                }
            },
            {
                'uuid': 'CyVRaHfT',
                'dashboard_uuid': 'SF5VJdrP',
                'name': '最近浏览的页面组',
                'layout': {
                    'x': 6,
                    'y': 4,
                    'w': 6,
                    'h': 3
                },
                'type': 'recent_spaces',
                'config': {}
            }
        ]
    }


def _view_filed():
    return {'query': {
        'must': [{'equal': {'item_type': 'field'}}, {'in': {'pool': ['project']}}, {'in': {'context.type': ['team']}}]},
        'view': ['[default]', 'used_in']}


def plan_list():
    return {
        'query': 'query QUERY_TESTPLAN_LIST {\n      buckets (\n        pagination: $pagination,\n        '
                 'groupBy: {\n          testcasePlans: {}\n        }\n      ) {\n        pageInfo {\n          '
                 'count\n          totalCount\n          startPos\n          startCursor\n          '
                 'endPos\n          '
                 'endCursor\n          hasNextPage\n        }\n        testcasePlans(\n          '
                 'filter: $filter\n          orderBy:{\n            status: {\n              '
                 'category: ASC,\n            },\n            namePinyin: ASC,\n          }\n          '
                 'limit: 1000\n        ){\n          key,\n          uuid,\n          name,\n          '
                 'namePinyin,\n          createTime,\n          \n        }\n      }\n    }\n  ',
        'variables': {
            'pagination': {
                'limit': 100,
                'after': ''
            },
            'filter': {}
        }
    }


def update_notice_center():
    """工作项通知 通知方式配置"""
    return {
        "notice_center": False,
        "effect_notice_center": True,  # True 为关闭
        "email": False,
        "effect_email": True,
        "wechat": False,
        "lark": False,
        "effect_wechat": True,
        "effect_lark": True
    }


def departments_gql():
    return {
        "query": "\n      {\n        departments(\n          orderBy: {\n            namePinyin: DESC\n          }\n        ){\n          name\n          uuid\n          member_count: memberCount\n          sync_type: syncType\n          parent_uuid: parent\n          next_uuid: next\n        }\n    }\n  "
    }


def user_group_gql():
    return {
        "query": "\n    {\n      buckets (\n        groupBy: {\n          userGroups: {}\n        },\n        pagination: $pagination,\n        filter: {\n          key_equal: \"bucket.0.__all\"\n        }\n      ) {\n        userGroups(\n          filter: $filter,\n          orderBy: {\n            namePinyin: ASC\n          }\n        ){\n          name\n          uuid\n        }\n        pageInfo {\n          count\n          totalCount\n          startPos\n          startCursor\n          endPos\n          endCursor\n          hasNextPage\n        }\n      }\n  }\n  ",
        "variables": {
            "filter": {},
            "pagination": {
                "limit": 50,
                "after": ""
            }
        }
    }
