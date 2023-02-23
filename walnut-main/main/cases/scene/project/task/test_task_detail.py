"""
@File    ：test_task_detail.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/7
@Desc    ：任务管理-任务详情 测试用例
"""
from falcons.check import Checker
from falcons.com.nick import feature, parametrize, fixture, story, step
from falcons.helper import mocks

from main.actions.case import CaseAction
from main.actions.sprint import SprintAction
from main.actions.task import TaskAction
from main.api import issue
from main.api import project as prj
from main.api import task as api, case
from main.params import issue as ise
from main.params import task as p, testcase


@fixture(scope='module', autouse=True)
def _prepare():
    """
    预先创建一条测试任务
    创建迭代
    创建测试一个用例库及2条测试用例

    :return:
    """
    task = TaskAction.new_issue()[0]
    sprint = SprintAction.sprint_add()

    lib_resp = CaseAction.library_add()
    lib_uuid = lib_resp.value('library.uuid')
    case_uuid1 = CaseAction.case_add(lib_uuid)
    case_uuid2 = CaseAction.case_add(lib_uuid)

    return {'task': task, 'sprint': sprint,
            'lib_uuid': lib_uuid,
            'case': [case_uuid1, case_uuid2]}


@fixture(scope='module')
def data_storage():
    ds = dict()
    return ds


@fixture(scope='module', autouse=True)
def del_task(_prepare):
    """删除测试任务"""
    yield
    TaskAction.del_task(_prepare['task'])
    CaseAction.library_delete(_prepare['lib_uuid'])


@feature('任务管理-任务详情')
class TestTaskDetail(Checker):

    def add_sub_task(self, token=None):
        # 获取系统工作项-子任务UUID
        s_param = ise.show_issue_list()[0]
        stamps = self.call(prj.TeamStampData, s_param, token)

        list_issue = stamps.json()['issue_type']['issue_types']
        sys_issues = [c['uuid'] for c in list_issue if c['name'] == '子任务']

        # 类型-添加子任务
        i_param = ise.add_project_issue()[0]
        i_param.json['issue_type_uuids'] = sys_issues
        self.call(issue.IssueProjectAdd, i_param, token)

    @story('128240 工作项详情-顶栏快捷操作：关联迭代')
    @parametrize('param', p.task_update_sprint())
    def test_task_update_sprint(self, param, _prepare):
        """"""
        with step('关联迭代'):
            param.json['tasks'][0]['uuid'] = _prepare['task']
            param.json['tasks'][0]['field_values'][0]['value'] = _prepare['sprint']

            self.call(api.TaskUpdate3, param)

        resp = TaskAction.task_info(_prepare['task'])
        resp.check_response('sprint_uuid', _prepare['sprint'])

    @story('133500 任务管理-复制工作项：复制为其他工作项类型')
    def test_copy_issue(self, _prepare):
        """复制工作项"""

        resp = TaskAction.task_copy(_prepare['task'])
        copied_uuid = resp.json()['task']['uuid']

    @story('133554 任务管理-更多：复制没有子工作项的工作项')
    def test_copy_standard_issue(self, _prepare):
        """和上一条用例步骤一致的"""

        resp = TaskAction.task_copy(_prepare['task'])
        copied_uuid = resp.json()['task']['uuid']

    @story('128246 工作项详情-快捷操作：新建子工作项')
    def test_add_sub_issue(self, _prepare):
        # """添加子任务"""
        # self.add_sub_task()

        """添加子工作项"""
        sub_task_uuid = TaskAction.new_issue(_prepare['task'], '子任务')

        resp = TaskAction.task_info(_prepare['task'])
        resp.check_response('subtasks[0].uuid', sub_task_uuid[0])

    @story('133501 任务管理-复制工作项：复制为原工作项类型')
    def test_copy_as_same_issue(self, _prepare):
        """复制工作项"""

        resp = TaskAction.task_copy(_prepare['task'], '任务')
        copied_uuid = resp.json()['task']['uuid']

    @story('133541 任务管理-更多：标准工作项以此新建工作项（新建系统类型工作项）')
    def teat_add_with_issue(self):
        pass

    @story('133540 任务管理-更多：标准工作项批量新建多个子工作项')
    def test_add_sub_issue_batch(self, _prepare):
        sub_task_uuid = TaskAction.new_issue(_prepare['task'], '子任务', is_batch=True)

        resp = TaskAction.task_info(_prepare['task'])
        sub_tasks = [t['uuid'] for t in resp.json()['subtasks']]

        for s in sub_task_uuid:
            assert s in sub_tasks, f'没找到子任务{s}'
        # assert set(sub_task_uuid) & set(sub_tasks) == sub_task_uuid # 并集的结果值的顺序不一致

    @story('133536 任务管理-更多：标准工作项关联用例')
    def test_relate_case(self, _prepare):
        with step('工作项关联测试案例'):
            bind_resp = CaseAction.bind_case(_prepare['task'], *_prepare['case'])
        with step('检查绑定结果'):
            bind_resp.check_response('success_cases', _prepare['case'])
            bind_resp.check_response('success_tasks[0]', _prepare['task'])

    @story('133528 任务管理-更多：变更工作项类型')
    def test_change_issue_type(self):
        pass

    @story('133532 任务管理-更多：变更子工作项类型')
    def test_change_sub_issue_type(self):
        pass

    @story('148201 工作项详情：设置周期与进度')
    def test_setting_cycle_and_schedule(self, _prepare):
        with step('设置进度'):
            up_info = {
                "field_uuid": "field033",  # 进度
                "type": 4,
                "value": 3000000
            }
            TaskAction.update_task_info(_prepare['task'], up_info)

    @story('148203 工作项详情：修改周期与进度')
    def test_up_cycle_and_schedule(self, _prepare):
        with step('修改计划开始时间，计划结束时间，进度'):
            up_end = {
                "field_uuid": "field028",  # 计划结束时间
                "type": 5,
                "value": mocks.day_timestamp(3)
            }
            TaskAction.update_task_info(_prepare['task'], up_end)

            up_info = {
                "field_uuid": "field033",
                "type": 4,
                "value": 2000000
            }
            TaskAction.update_task_info(_prepare['task'], up_info)

    @story('136232 文件：上传文件')
    def test_task_upload_file(self, _prepare, data_storage):
        img_name = f"test_img_{mocks.ones_uuid()}"

        with step('上传文件-token'):
            param = p.task_file_upload()[0]
            param.json_update('ref_id', _prepare['task'])
            res = self.call(api.ResAttUpload, param)

            token = res.value('token')
            url = res.value('upload_url')
            file_uuid = res.value('resource_uuid')

        with step('点击确定-上传文件'):
            """"""
            box = api.UpBox()
            box.call({'token': token, 'img_name': img_name}, url)
            box.is_response_code(200)

        data_storage |= {'file_uuid': file_uuid, 'file_url': box.value('url')}

    @story('136246 文件：下载文件')
    def test_download_file(self, data_storage):
        param = p.task_file_upload()[0]
        param.uri_args({'file_uuid': data_storage['file_uuid']})

        with step('点击下载文件'):
            dow = self.call(case.AttachmentDownload, param)
            dow.check_response('status', 1)

    @story('136227 文件：删除文件')
    def test_del_file(self, data_storage):
        prm = testcase.attachments_opt()
        jsn = [data_storage['file_uuid']]

        with step('点击确定-删除文件'):
            d = case.DeleteAttachment()
            d.call(jsn, **prm.extra)
            d.is_response_code(200)
