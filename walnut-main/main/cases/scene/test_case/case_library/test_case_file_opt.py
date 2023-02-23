import requests
from falcons.com.nick import feature, story, fixture, step
from falcons.helper import mocks

from main.api import case as api
from main.api import project
from main.api.task import ResAttUpload, UpBox
from main.params import testcase


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
    param.json['item']['name'] = '示例用例1'
    add.call(param.json, **param.extra)
    add.is_response_code(200)

    _data_storage |= {'case_uuid': add.json()['item']['uuid']}


@feature('用例库文件操作')
class TestCaseFile:

    @story('T136232 文件：上传文件')
    def test_case_up_file(self, _data_storage):
        img_name = f"test_img_{mocks.ones_uuid()}"
        param = testcase.attachments_opt()

        with step('上传文件-token'):
            q = ResAttUpload()

            jsn = {
                "type": "attachment",
                "name": img_name,
                "ref_id": _data_storage['case_uuid'],
                "ref_type": "testcase",
                "description": None
            }

            q.call(jsn, **param.extra)
            q.is_response_code(200)
            j = q.json()
            token = j['token']
            url = j['upload_url']
            file_uuid = j['resource_uuid']

        with step('点击确定-上传文件'):
            """"""
            box = UpBox()
            box.call({'token': token, 'img_name': img_name}, url)
            box.is_response_code(200)

        _data_storage |= {'file_uuid': file_uuid, 'file_url': box.value('url')}

    @story('T136245 文件：下载文件')
    def test_download_file(self, _data_storage):
        prm = testcase.case_attachment()[0]
        prm.extra['uri_args'] |= {'file_uuid': _data_storage['file_uuid']}

        dow = api.AttachmentDownload()
        dow.call(**prm.extra)
        dow.is_response_code(200)

    @story('预览文件')
    def test_preview_file(self, _data_storage):
        res = requests.get(url=_data_storage['file_url'], verify=False)

        assert res.status_code == 200

    @story('T136225 文件：删除文件')
    def test_del_case_file(self, _data_storage):
        prm = testcase.del_attachment(_data_storage['file_uuid'])[0]

        delete = api.DeleteAttachment()
        delete.call(prm.json, **prm.extra)
        delete.is_response_code(200)
