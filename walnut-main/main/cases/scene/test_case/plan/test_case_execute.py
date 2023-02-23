from falcons.com.nick import feature, story, fixture, step, parametrize
from falcons.helper import mocks

from main.actions.task import TaskAction
from main.api import case as api
from main.api import project
from main.api.task import TaskAdd, ResAttUpload, UpBox
from main.params import testcase, task


# 初始化用例库
@fixture(scope='module', autouse=True)
def _case_lib():
    # 查默认配置uuid
    q = testcase.query_case_config_list()[0]
    gq = project.ItemGraphql()
    gq.call(q.json, **q.extra)
    config_uuid = gq.json()['data']['testcaseFieldConfigs'][0]['uuid']

    # 新建用例库
    param = testcase.add_case_library()[0]
    param.json['library']['field_config_uuid'] = config_uuid
    add = api.AddCaseLibrary()
    add.call(param.json, **param.extra)
    add.is_response_code(200)

    data = {'lib_uuid': add.json()['library']['uuid'],
            'module_uuid': add.json()['library']['modules'][0]['uuid'],
            'conf_uuid': config_uuid}

    return data


@fixture(scope='module')
def _data_storage():
    p = {}
    return p


# 获取用例属性配置
@fixture(scope='module', autouse=True)
def _case_priority(_case_lib, _data_storage):
    param = testcase.query_library_case_edit()[0]
    param.json['variables']['fieldFilter']['context']['fieldConfigUUID_in'] = [_case_lib['conf_uuid']]
    param.json['variables']['moduleFilter']['testcaseLibrary_in'] = [_case_lib['lib_uuid']]

    q = project.ItemGraphql()
    q.call(param.json, **param.extra)

    # 获取用例库优先级等级uuid和显示值(P0\P1)
    fields = q.json()['data']['fields']

    priority_uuids = [f for f in fields if f['name'] == '优先级']
    case_type = [f for f in fields if f['name'] == '用例类型']

    _data_storage |= {
        'pri_uuid': [n['uuid'] for n in priority_uuids[0]['options']],
        'pri_value': [n['value'] for n in priority_uuids[0]['options']],
        'type_uuid': [n['uuid'] for n in case_type[0]['options']]
    }
    return _data_storage


# 初始化用例
@fixture(scope='module', autouse=True)
def _case_data(_case_lib, _case_priority, _data_storage):
    param = testcase.add_case()[0]
    param.json['item']['priority'] = _case_priority['pri_uuid'][1]
    param.json['item']['type'] = _case_priority['type_uuid'][0]
    param.json['item']['module_uuid'] = _case_lib['module_uuid']
    param.json['item']['testcase_module'] = _case_lib['module_uuid']
    param.json['item']['library_uuid'] = _case_lib['lib_uuid']
    param.json['item']['testcase_library'] = _case_lib['lib_uuid']

    add = project.ItemsAdd()
    param.json['item']['name'] = 'test关联用例'
    add.call(param.json, **param.extra)
    add.is_response_code(200)

    _data_storage |= {'case_uuid': add.json()['item']['uuid']}


# 初始化测试计划
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
    add = api.AddCasePlan()
    add.call(p.json, **p.extra)
    add.is_response_code(200)

    _data_storage |= {'plan_uuid': add.json()['plan']['uuid']}


# 初始化关联用例
@fixture(scope='module', autouse=True)
def _rel_case(_data_storage):
    # 添加关联用例
    c = testcase.up_plan_info()
    c.uri_args({'plan_uuid': _data_storage['plan_uuid']})
    jsr = {"case_uuids": [_data_storage['case_uuid']]}

    add = api.CaseRelPlan()
    add.call(jsr, **c.extra)
    add.is_response_code(200)

    # 查询用例详情
    p = testcase.query_case_detail()[0]
    p.json['variables']['testCaseFilter']['uuid_in'] = [_data_storage['case_uuid']]
    p.json['variables']['stepFilter']['testcaseCase_in'] = [_data_storage['case_uuid']]

    qg = project.ItemGraphql()
    qg.call(p.json, **p.extra)
    qg.is_response_code(200)

    key = qg.json()['data']['testcaseCases'][0]['key']

    _data_storage |= {'key': key}


@fixture(scope='module', autouse=True)
def _del_plan(_data_storage):
    """删除测试计划数据"""
    yield
    param = testcase.up_plan_status()
    q = api.DeletePlan()
    param.uri_args({'plan_uuid': _data_storage['plan_uuid']})
    q.call(**param.extra)
    q.is_response_code(200)


@feature('用例执行')
class TestCaseExecute:

    @story('143315 编辑用例优先级')
    def test_up_case_pri(self, _data_storage):
        # 编辑用例优先级
        u = testcase.update_case_pri()
        u.json['variables']['key'] = _data_storage['key']
        u.json['variables'] |= {'priority': _data_storage['pri_uuid'][0]}  # 优先级更改成P0

        up = project.ItemGraphql()
        up.call(u.json, **u.extra)
        up.is_response_code(200)

    @story('143317 编辑用例标题')
    def test_up_title(self, _data_storage):
        p = testcase.update_case_title()
        p.json['variables']['key'] = _data_storage['key']

        up = project.ItemGraphql()
        up.call(p.json, **p.extra)
        up.is_response_code(200)

    @story('143320 编辑用例维护人')
    def test_up_assign(self, _data_storage):
        p = testcase.update_case_assign()
        p.json['variables']['key'] = _data_storage['key']

        up = project.ItemGraphql()
        up.call(p.json, **p.extra)
        up.is_response_code(200)

    @story('T121478 检查执行人弹窗')
    def test_executor_wind(self, _data_storage):
        p = testcase.update_plan_case()
        p.uri_args({'plan_uuid': _data_storage['plan_uuid']})

        q = api.PlanExecutor()
        q.call(**p.extra)
        q.is_response_code(200)

    @story('T121469 编辑用例执行人')
    def test_up_executor(self, _data_storage):
        p = testcase.update_plan_case()
        p.json['cases'][0]['uuid'] = _data_storage['case_uuid']
        p.uri_args({'plan_uuid': _data_storage['plan_uuid']})

        q = api.UpdatePlanCase()
        q.call(p.json, **p.extra)
        q.is_response_code(200)

    @story('T143344 提缺陷')
    @parametrize('param', task.task_add())
    def test_plan_carry_bug(self, param):
        with step('获取工作项属性数据'):
            j = TaskAction.task_stamp(flush=True)
            field_conf_uid = [c['default_value'] for c in j['field_config']['field_configs'] if
                              c['field_uuid'] == 'field012']  # 用默认值就好了
            issue_conf_uid = [c['issue_type_uuid'] for c in j['issue_type_config']['issue_type_configs'] if
                              c['name'] == '缺陷']  # 获取任务工作项的属性uuid
            # update param value
            param.json['tasks'][0] |= {'summary': 'test执行提bug'}
            param.json['tasks'][0]['field_values'][1] |= {'value': field_conf_uid[0]}
            param.json['tasks'][0] |= {'issue_type_uuid': issue_conf_uid[0]}

        with step('提缺陷'):
            t = TaskAdd()
            # 调用接口
            t.call(param.json, **param.extra)
            # 检查接口响应码
            t.is_response_code(200)

    @story('T141358 执行结果附件-上传文件')
    def test_up_file(self, _data_storage):
        with step('选择文件并点击打开'):
            img_name = f"test_img_{mocks.ones_uuid()}"

        # 获取ref_id
        ref = testcase.query_plan_case_detail()
        ref.json['variables']['testCaseFilter'] |= {"testcaseCase_in": [_data_storage['case_uuid']],
                                                    "testcasePlan_in": [_data_storage['plan_uuid']]}
        ref.json['variables']['libraryStepFilter'] |= {"testcaseCase_in": [_data_storage['case_uuid']]}
        ref.json['variables']['planStepFilter'] |= {"testcaseCase_in": [_data_storage['case_uuid']],
                                                    "testcasePlan_in": [_data_storage['plan_uuid']]}

        q_ref = project.ItemGraphql()
        q_ref.call(ref.json, **ref.extra)
        q_ref.is_response_code(200)

        ref_id = q_ref.json()['data']['testcasePlanCases'][0]['inCaseUUID']

        with step('上传文件-token'):
            q = ResAttUpload()

            jsn = {
                "type": "attachment",
                "name": img_name,
                "ref_id": ref_id,
                "ref_type": "plan_case",
                "description": None
            }
            q.call(jsn, **ref.extra)
            q.is_response_code(200)
            j = q.json()
            token = j['token']
            url = j['upload_url']

        _data_storage |= {'file_uuid': j['resource_uuid']}  # 图片uuid

        with step('点击确定-上传文件'):
            """"""
            box = UpBox()
            box.call({'token': token, 'img_name': img_name}, url)
            box.is_response_code(200)

    @story('T141362 执行结果附件-下载文件')
    def test_download_file(self, _data_storage):
        p = testcase.attachments_opt()
        p.extra['uri_args'] |= {'file_uuid': _data_storage['file_uuid']}

        with step('点击下载文件'):
            dow = api.AttachmentDownload()
            dow.call(**p.extra)

            dow.is_response_code(200)
            dow.check_response('status', 1)

    @story('T141356 执行结果附件-删除文件')
    def test_del_file(self, _data_storage):
        p = testcase.attachments_opt()
        jsn = [_data_storage['file_uuid']]

        with step('点击确定-删除文件'):
            d = api.DeleteAttachment()
            d.call(jsn, **p.extra)
            d.is_response_code(200)
