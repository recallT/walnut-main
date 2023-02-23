from main.api import case as api
from main.api import project
from main.params import testcase


def add_case_library():
    """新增用例库"""
    data = testcase.query_case_config_list()[0]
    q = project.ItemGraphql()
    q.call(data.json, **data.extra)
    config_uuid = q.json()['data']['testcaseFieldConfigs'][0]['uuid']

    param = testcase.add_case_library()[0]
    param.json['library']['field_config_uuid'] = config_uuid
    add = api.AddCaseLibrary()
    add.call(param.json, **param.extra)

    add.is_response_code(200)
    add.check_response('library.name', param.json['library']['name'])

    uuid = add.json()['library']['uuid']
    module_uuid = add.json()['library']['modules'][0]['uuid']

    return {'uuid': uuid, 'module_uuid': module_uuid, 'config_uuid': config_uuid}