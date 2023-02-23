"""
@File    ：case.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/9
@Desc    ：案例管理相关接口操作
"""
from falcons.check import go
from falcons.helper import mocks

from main.api import case as api, project, case, issue
from main.api import project as prj
from main.params import task as tsk, testcase
from main.params import testcase as tc


class CaseAction:
    """案例管理相关操作"""

    @classmethod
    def field_config(cls, field_name='默认配置', token=None):
        """获取默认配置UUID"""

        c = tc.case_field_config_list()[0]
        resp = go(prj.ItemGraphql, c, token)

        # 取出 默认配置UUID
        config_uuid = [f['uuid'] for f in resp.json()['data']['testcaseFieldConfigs'] if f['name'] == field_name]

        return config_uuid

    @classmethod
    def library_add(cls, token=None):
        """
        新建用例库

        创建一个用例库，使用默认 的 用例属性配置

        :param token:
        :return: 案例库信息，包含一个默认模块 uuid 信息
                    ['library']['uuid']  案例库 uuid
                    ['library']['modules'][0]['uuid']'  默认模块uuid
        """
        config_uuid = cls.field_config()

        p = tc.library_add()[0]
        p.json['library']['field_config_uuid'] = config_uuid[0]

        return go(api.AddCaseLibrary, p, token)

    @classmethod
    def case_add(cls, library_uuid, field_name=None, value_name=None, priority='P1', token=None) -> str:
        """
        新建用例
        :param token:
        :param library_uuid: 案例库 uuid
        :param field_name: 新添加的属性字段名
        :param value_name: 属性的选项值
        :param priority: 优先级选项值P0/P1/P2/P3/P4
        :return: case_uuid
        """
        config_uuid = cls.field_config()

        # 获取用例属性配置
        param = tc.query_library_case_edit()[0]
        param.json_update('variables.fieldFilter.context.fieldConfigUUID_in', config_uuid)
        param.json_update('variables.moduleFilter.testcaseLibrary_in', [library_uuid])
        q = go(prj.ItemGraphql, param, token)

        fields = q.value('data.fields')  # 获取用例库优先级等级uuid和显示值(P0\P1)
        priority_uuids = [f for f in fields if f['name'] == '优先级']
        case_type = [f for f in fields if f['name'] == '用例类型']

        pri_uuid = [n['uuid'] for n in priority_uuids[0]['options'] if n['value'] == priority][0]
        type_uuid = [n['uuid'] for n in case_type[0]['options']][0]
        module_uuid = [mod['uuid'] for mod in q.value('data.testcaseModules') if mod['name'] == '无所属模块'][0]

        # 新建用例
        prm = tc.add_case()[0]
        field_uuid = []
        if field_name is not None:
            field_uuid += [f['aliases'][0] for f in fields if f['name'] == field_name]
        if value_name is not None:
            field_opt_uuid = [opt['uuid'] for f in fields if f['name'] == field_name
                              for opt in f['options'] if opt['value'] == value_name][0]
            prm.json['item'] |= {f'_{field_uuid[0]}': field_opt_uuid}

        prm.json_update('item.name', [field_name if field_name is not None else f'test_case_{mocks.num()}'][0])
        prm.json_update('item.priority', pri_uuid)
        prm.json_update('item.type', type_uuid)
        prm.json_update('item.module_uuid', module_uuid)
        prm.json_update('item.testcase_module', module_uuid)
        prm.json_update('item.library_uuid', library_uuid)
        prm.json_update('item.testcase_library', library_uuid)

        return go(prj.ItemsAdd, prm, token).value('item.uuid')

    @classmethod
    def module_add(cls, token=None):
        """新建用例库模块"""

    @classmethod
    def test_phase(cls, token=None):
        # 获取各测试阶段uuid
        param = tc.query_case_phase()[0]
        res = go(prj.ItemGraphql, param, token)

        return res.json()['data']['fields'][0]['options']

    @classmethod
    def attrib_add(cls, field_type, name, option=None, pool='testcase', token=None, **kwargs):
        """
        添加测试相关属性

        :param token
        :param field_type  属性类型
        :param name  自定义的属性名称
        :param option  选项值内容
        :param pool
        """

        # 查默认配置uuid
        config_uuid = cls.field_config(**kwargs)

        # 添加用例属性
        param = tc.add_attrib(field_type, pool)[0]
        param.json_update('item.name', name)
        if option is not None:
            param.json['item'] |= {'options': option}
        add = go(prj.ItemsAdd, param, token).value('item')
        field_key = add['key']

        # 将用例属性添加到用例属性配置
        prm = tc.add_case_attrib_config()[0]
        prm.json_update('item.aliases', add['aliases'])
        prm.json_update('item.context.field_config_uuid', config_uuid[0])

        return go(prj.ItemsAdd, prm, token), field_key

    @classmethod
    def add_case_field(cls, field_type, **kwargs):
        """
        配置中心-用例属性-新增用例属性
        :param field_type: 属性类型
        :param kwargs: 选项类型options值
        :return: field_key
        """
        param = tc.add_attrib(field_type=field_type)[0]
        param.json_update('item.name', 'case-filed' + mocks.num())
        if kwargs:
            options = kwargs['options']
            param.json_update('item.options', options)
        field_key = go(prj.ItemsAdd, param).value('item.key')

        return field_key

    @classmethod
    def attrib_update(cls, name, key, opt=None, code=200, **kwargs):
        """
        更新属性信息
        :param token
        :param name  属性名称
        :param opt 选项值内容
        :param key  测试用例属性key
        :param code
        """
        prm = tc.case_field_update()[0]
        prm.json = {"item": {"name": name, "options": opt}}
        if kwargs:
            prm.json_update('item.new_option', kwargs['new_option'])
            prm.json_update('item.old_option', kwargs['old_option'])
        prm.uri_args({'field_key': key})

        return go(api.CaseFieldUpdate, prm, status_code=code)

    @classmethod
    def case_lib_field_config(cls, library_uuid, token=None):
        """
        查询用例库中的属性配置
        """

        config_uuid = cls.field_config()

        # 用例库信息
        param = tc.query_library_case_edit()[0]
        param.json_update('variables.fieldFilter.context.fieldConfigUUID_in', config_uuid)
        param.json_update('variables.moduleFilter.testcaseLibrary_in', [library_uuid])

        return go(prj.ItemGraphql, param, token)

    @classmethod
    def case_field_config(cls, token=None):
        """
        查询用例属性配置
        """
        # 获取默认配置uuid
        config_uuid = cls.field_config()

        param = tc.query_filter_fields(config_uuid[0])[0]

        return go(prj.ItemGraphql, param, token)

    @classmethod
    def del_case_field_and_config(cls, config_key, field_key, token=None):
        """
        删除用例属性和属性配置详情
        :param token
        :param config_key  用例属性添加到用例属性配置生成的key
        :param field_key  测试用例属性key

        """

        # 删除用例属性配置-默认属性下的配置
        param = tc.field_delete()[0]
        param.uri_args({'field_key': config_key})
        go(api.FieldDelete, param, token)

        # 删除用例属性
        param.uri_args({'field_key': field_key})
        go(api.FieldDelete, param, token)

    @classmethod
    def del_field_config(cls, config_key, code=200, token=None):
        """
        单独删除用例属性或属性配置
        :param token
        :param config_key  用例属性或属性配置key
        :param code
        """
        param = tc.field_delete()[0]
        param.uri_args({'field_key': config_key})

        return go(api.FieldDelete, param, token=token, status_code=code)

    @classmethod
    def library_permission_rules_add(cls, lib_uuid, permission, user_domain_type, user_domain_param=""):
        """
        用例库权限配置新增权限
        :param lib_uuid  用例库uuid
        :param permission  需要编辑的权限类型
        :param user_domain_type  添加权限的用户域类型
        :param user_domain_param  用户域类型参数
        """
        param = tc.testcase_permission()[0]
        param.json_update('permission_rule.context_type', "testcase_library")
        param.json_update('permission_rule.context_param', {'library_uuid': lib_uuid})
        param.json_update('permission_rule.permission', permission)
        param.json_update('permission_rule.user_domain_type', user_domain_type)
        param.json_update('permission_rule.user_domain_param', user_domain_param)

        uuid = go(project.PermissionAdd, param).value('permission_rule.uuid')
        return uuid

    @classmethod
    def library_delete(cls, library_uuid, token=None):
        """
        删除用例库
        :param token:
        :param library_uuid:用例库UUID
        :return:
        """

        p = tc.library_delete()[0]
        p.uri_args({'library_uuid': library_uuid})
        return go(api.DeleteLibrary, p, token)

    @classmethod
    def bind_case(cls, task_uuid, *cases, token=None):
        """
        绑定案例
        :param token:
        :param task_uuid: 任务UUID
        :param cases: 案例UUID列表
        :return:
        """

        p = tsk.bind_case()[0]
        p.json_update('cases[0].task_uuid', task_uuid)
        p.json['cases'][0]['case_uuids'] += cases
        return go(api.BindCase, p, token)

    @classmethod
    def unbind_testcase(cls, case_uuid, task_uuid):
        """
        解除任务和用例绑定关系
        :param case_uuid: 用例UUID
        :param task_uuid: 任务UUID
        :return: 返回请求结果
        """

        p = tsk.unbind_case(case_uuid, task_uuid)[0]
        return go(api.UnBindCase, p)

    @classmethod
    def add_testcase_plan(cls, token=None):
        """
        新增测试计划
        :param token:
        :return: plan_uuid 测试计划uuid
        """
        param = testcase.query_case_phase()[0]
        q = project.ItemGraphql(token)
        q.call(param.json, **param.extra)
        q.is_response_code(200)

        # 获取各测试阶段的uuid
        stages = q.json()['data']['fields'][0]['options']
        stage_uuid = [n['uuid'] for n in stages]

        # 新增测试计划
        p = testcase.add_case_plan()
        p.json['plan']['plan_stage'] = stage_uuid[0]  # 选择冒烟阶段
        resp = go(api.AddCasePlan, p, token)
        plan_uuid = resp.value('plan.uuid')
        return plan_uuid

    @classmethod
    def add_testplan_field(cls, field_type, **kwargs):
        """
         配置中心-测试管理-新增测试计划属性
        :param field_type: 属性类型
        :param kwargs: 可选类型数据传options
        :return:
        """
        param = tc.add_plan_field()
        param.json_update('variables.field_type', field_type)
        param.json_update('variables.name', 'test-plan-field' + mocks.num())
        if kwargs:
            options = kwargs['options']
            param.json_update('variables.options', options)
        field_key = go(prj.ItemGraphql, param).value('data.addField.key')
        return field_key

    @classmethod
    def testplan_set_info(cls, field_key):
        """
        测试计划设置 - 测试计划信息页查看属性
        :param field_key:
        :return:
        """
        prm = tc.query_plan_field()
        res = go(prj.ItemGraphql, prm)

        keys = [f['key'] for f in res.value('data.fields')]
        assert field_key in keys

    @classmethod
    def del_test_field(cls, field_key):
        """
        删除配置中心-(测试计划，测试用例)属性
        :param field_key: 属性key
        :return:
        """
        param = tc.field_delete()[0]
        param.uri_args({'field_key': field_key})
        go(case.FieldDelete, param).check_response('code', 200)

    @classmethod
    def query_case_global_field(cls, key):
        """
        查询用例属性是否存在
        :param key: 属性key
        :return:
        """
        param = testcase.query_global_fields()[0]
        res = go(project.ItemGraphql, param).value('data.fields')
        keys = [r['key'] for r in res]
        assert key in keys

    @classmethod
    def update_config_default_values(cls, field_key, default_value_uuid):
        """
        更新用例属性默认值
        :param field_key: 属性key
        :param default_value_uuid: 默认值uuid
        :return:
        """
        prm = tc.case_field_update()[0]
        prm.json = {"item": {"default_value": default_value_uuid}}
        prm.uri_args({'field_key': field_key})

        return go(api.CaseFieldUpdate, prm)

    @classmethod
    def add_testcase_permission(cls, permission, user_domain_param, user_domain_type):
        """
        TestCase 配置中心 权限配置
        :param permission: 权限名称
        :param user_domain_param: user_domain_param
        :param user_domain_type: user_domain_type
        :param context_type  添加权限类型
        :return:permission_rule uuid
        """
        param = tc.testcase_permission()[0]
        param.json_update('permission_rule.permission', permission)
        param.json_update('permission_rule.user_domain_type', user_domain_type)
        param.json_update('permission_rule.user_domain_param', user_domain_param)

        uuid = go(project.PermissionAdd, param).value('permission_rule.uuid')
        return uuid

    @classmethod
    def del_testcase_permission(cls, permission_rule_uuid):
        """
        删除权限配置
        :param permission_rule_uuid: 对应权限点UUID
        :return:
        """
        param = tc.library_delete()[0]
        param.uri_args({'permission_rule_uuid': permission_rule_uuid})
        go(issue.DelIssuePermission, param)
