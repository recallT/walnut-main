from falcons.com.nick import feature, story, fixture

from main.api import project, case
from main.params import testcase
from main.params.const import ACCOUNT


# 初始化测试计划数据
@fixture(scope='module', autouse=True)
def _plan_data(_data_storage):
    param = testcase.query_case_phase()[0]
    q = project.ItemGraphql()
    q.call(param.json, **param.extra)
    q.is_response_code(200)

    # 获取各测试阶段给uuid
    stages = q.json()['data']['fields'][0]['options']
    stage_uuid = [n['uuid'] for n in stages]

    # 新增测试计划
    p = testcase.add_case_plan()
    p.json['plan']['plan_stage'] = stage_uuid[0]  # 选择冒烟阶段
    add = case.AddCasePlan()
    add.call(p.json, **p.extra)
    add.is_response_code(200)

    _data_storage |= {'plan_uuid': add.json()['plan']['uuid']}


@fixture(scope='module')
def _data_storage():
    p = {}
    return p


@fixture(scope='module')
def _field_key():
    return []


@fixture(scope='module', autouse=True)
def _del_field(_field_key):
    """删除属性"""
    yield
    p = testcase.del_plan_field()
    d = case.DeletePlanField()

    for key in _field_key:
        p.uri_args({'key': key})
        d.call(**p.extra)
        d.is_response_code(200)


@feature('测试计划设置')
class TestPlanSetting:

    @story('118684 测试计划设置-测试计划信息：页面默认详情检查')
    def test_plan_info(self, _data_storage):
        param = testcase.query_plan_detail()
        param.json['variables']['planFilter']['uuid_in'] = [_data_storage['plan_uuid']]

        q = project.ItemGraphql()
        q.call(param.json, **param.extra)

        q.is_response_code(200)
        q.check_response('data.testcasePlans[0].planStage.value', '冒烟测试')

        _data_storage |= {'tracing_config': q.json()['data']['testcasePlans'][0]['issueTracingConfig']}

    @story('T118682 测试计划设置-测试计划信息：更新测试计划属性信息')
    def test_add_text_field(self, _field_key):
        param = testcase.add_plan_field()
        param.json['variables'] |= {
            "field_type": "text",
            "name": "示例文本计划属性",
            "context": {
                "type": "team"
            },
            "pool": "testcase_plan"
        }

        add = project.ItemGraphql()
        add.call(param.json, **param.extra)

        add.is_response_code(200)

        _field_key.append(add.json()['data']['addField']['key'])

    @story('T118682 测试计划设置-测试计划信息：更新测试计划属性信息')
    def test_add_single_choice(self, _field_key):
        param = testcase.add_plan_field()
        param.json['variables'] |= {
            "field_type": "option",
            "name": "示例单选计划属性",
            "context": {
                "type": "team"
            },
            "options": [
                {
                    "value": "test1",
                    "color": "#fff",
                    "bg_color": "#307fe2"
                },
                {
                    "value": "test2",
                    "color": "#fff",
                    "bg_color": "#00b388"
                }
            ],
            "pool": "testcase_plan"
        }

        add = project.ItemGraphql()
        add.call(param.json, **param.extra)

        add.is_response_code(200)

        _field_key.append(add.json()['data']['addField']['key'])

    @story('T118682 测试计划设置-测试计划信息：更新测试计划属性信息')
    def test_add_single_user(self, _field_key):
        param = testcase.add_plan_field()
        param.json['variables'] |= {
            "field_type": "user",
            "name": "单成测试计划属性",
            "context": {
                "type": "team"
            },
            "pool": "testcase_plan"
        }

        add = project.ItemGraphql()
        add.call(param.json, **param.extra)

        add.is_response_code(200)

        _field_key.append(add.json()['data']['addField']['key'])

    @story('T118682 更新测试计划属性信息')
    def test_up_plan_info(self, _data_storage):
        # 获取属性uuid
        p = testcase.query_plan_field()
        q = project.ItemGraphql()
        q.call(p.json, **p.extra)
        q.is_response_code(200)

        fields = q.json()['data']['fields']
        text_aliases = [f['aliases'] for f in fields if f['fieldType'] == 'text'][0]  # 文本类型的aliases值
        option_aliases = [f['aliases'] for f in fields if f['fieldType'] == 'option'][0]  # 单选菜单的aliases值

        options = [f['options'] for f in fields if f['fieldType'] == 'option'][0]
        option_uuid = [n['uuid'] for n in options]  # 获取单选菜单的option_uuid

        # 更新信息
        param = testcase.up_plan_info()
        param.json['plan']['uuid'] = _data_storage['plan_uuid']
        param.json['plan']['name'] = 'test更新测试计划名称'
        param.json['plan']['issue_tracing_config'] = _data_storage['tracing_config']
        param.json['plan']['field_values'] = [
            {
                "alias": text_aliases[0],
                "type": "text",
                "value": "test文本更新"
            },
            {
                "alias": option_aliases[0],
                "type": "option",
                "value": option_uuid[0]
            }]
        param.uri_args({'plan_uuid': _data_storage['plan_uuid']})

        up = case.UpdatePlanInfo()
        up.call(param.json, **param.extra)
        up.is_response_code(200)

    @story('T118691 权限配置-删除成员')
    def test_del_member(self, _data_storage):
        param = testcase.up_plan_info()
        param.json['plan']['uuid'] = _data_storage['plan_uuid']
        param.json['plan']['name'] = 'test更新测试计划名称'
        param.json['plan']['issue_tracing_config'] = _data_storage['tracing_config']
        param.json['plan']['is_update_default_config'] = True

        param.uri_args({'plan_uuid': _data_storage['plan_uuid']})
        up = case.UpdatePlanInfo()
        up.call(param.json, **param.extra)
        up.is_response_code(200)

    @story('T118694 权限配置-添加成员')
    def test_add_member(self, _data_storage):
        param = testcase.up_plan_info()
        param.json['plan']['uuid'] = _data_storage['plan_uuid']
        param.json['plan']['name'] = 'test更新测试计划名称'
        param.json['plan']['issue_tracing_config'] = _data_storage['tracing_config']
        param.json['plan']['is_update_default_config'] = True
        param.json['plan']['members'].append({
            "user_domain_type": "single_user",
            "user_domain_param": ACCOUNT.user.owner_uuid
        })

        param.uri_args({'plan_uuid': _data_storage['plan_uuid']})
        up = case.UpdatePlanInfo()
        up.call(param.json, **param.extra)
        up.is_response_code(200)

    @story('删除测试计划数据')
    @story('118685 测试计划设置-更多：删除测试计划')
    def test_del_plan(self, _data_storage):
        param = testcase.up_plan_status()
        param.uri_args({'plan_uuid': _data_storage['plan_uuid']})

        q = case.DeletePlan()
        q.call(**param.extra)
        q.is_response_code(200)
