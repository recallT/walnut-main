"""
@File    ：test_file_component.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/6/14
@Desc    ：
"""
from falcons.check import Checker
from falcons.com.ones import parse_index
from falcons.com.nick import (
    feature,
    fixture,
    step,
    story,
    parametrize,
)

from main.actions.pro import PrjAction
from main.actions.task import TaskAction
from main.api import project as api
from main.api.case import AttachmentDownload, AttachmentBatchDownload, UpdateAttachment, PreviewImgAttachment
from main.api.task import QueueExtra
from main.params import task as p


@fixture(scope='module', autouse=True)
def prepared_files():
    """准备测试文件"""

    # 创建测试任务用于传文件
    task = TaskAction.new_issue()
    file_uuid = []
    for _ in range(3):  # 上传 3 个附件（图片）用于测试
        f_id = TaskAction.upload_file(task[0])
        file_uuid.append(f_id)

    # 添加文件组件到项目中
    PrjAction.add_component('文件')

    yield {'task_uuid': task[0], 'file_uuid': file_uuid}  # 将任务的UUID 拿出去

    PrjAction.remove_prj_component('文件')


@feature('项目管理-文件组件')
class TestFileComponent(Checker):
    """"""

    @story('T136136 文件组件-搜索：搜索文件')
    @story('23033 文件-文件管理：搜索文件')
    def test_file_list_search(self, prepared_files):
        """"""
        t = [
            ('根据文件名称搜索', 'testimg'),
            ('根据所属工作项名称搜索', '用于测试的工作项'),
            ('根据上传者名称搜索', 'test admin'),
            # ('根据文件名称搜索', 'TestImg'),
            # ('根据文件名称搜索', 'TestImg'),
            ('根据不存在文件名称搜索', 'not_exist_match'),
        ]

        for x in t:
            with step(x[0]):
                param = p.query_file(x[1])[0]

                resp = self.call(api.ItemGraphql, param)
                result_match = resp.value('data.buckets[0].taskAttachments')
                if x[1] == 'not_exist_match':
                    assert not result_match
                else:
                    assert result_match

    @story('T136159 文件组件-下载：下载单个文件')
    @story('23029 文件组件-下载：下载单个文件')
    @story('T136204 文件：检查文件的点击事件')
    @parametrize('param', p.download_file())
    def test_file_download(self, param, prepared_files):
        """"""

        with step('点击下载文件'):
            f_uid = prepared_files['file_uuid'][0]
            param.uri_args({'file_uuid': f_uid})
            dow = self.call(AttachmentDownload, param)
            dow.check_response('status', 1)
            dow.check_response('uuid', f_uid)

        with step('批量下载文件'):
            param1 = p.batch_dowload_file(prepared_files['file_uuid'], 'test.text')[0]
            res1 = self.call(AttachmentBatchDownload, param1)
            assert isinstance(res1.value('ready'), bool)
            # res1.check_response('ready', False)
            url: str = res1.value('url')
            filename = res1.value('filename')
            assert url.startswith('https://') or url.startswith('http://')
            # 检查队列列表，获取 done 状态
            task = TaskAction.check_queue_list(url, filename)
            task_status = TaskAction.wait_to_done(task['uuid'])
            assert task_status
            # 下载附件
            param2 = p.queue_extra(task['extra'])[0]
            param2.uri_args({"queue_uuid": task['uuid']})
            res = self.call(QueueExtra, param2)
            assert res.value('code') == 200 \
                   and res.value('type') == 'OK' \
                   and res.value('errcode') == "OK"

    @story('T136143 文件组件-文件列表：检查文件列表（有文件）')
    @parametrize('param', p.query_file())
    def test_file_list(self, param):
        resp = self.call(api.ItemGraphql, param)
        result_match = resp.value('data.buckets[0].taskAttachments')
        file1: dict = result_match[0]
        assert result_match[0], '文件列表为空！'
        assert [k for k in ['name', 'summary', 'owner', 'fileCategory', 'size', 'createTime',
                            'description'] if k not in file1.keys()] == [], '列表关键字段不存在'

    @story('T23031 文件-文件管理：编辑文件名称')
    @parametrize('param', p.query_file())
    def test_update_file_name(self, param, prepared_files):
        with step('修改文件名'):
            file_uuid = prepared_files['file_uuid'][0]
            name = "agqergqerhqerh"
            update_param = p.update_file(name, "dfgergqer")[0]
            update_param.uri_args({"file_uuid": file_uuid})
            self.call(UpdateAttachment, update_param)
        with step('检查文件列表中，文件名已更新'):
            resp = self.call(api.ItemGraphql, param)
            result_match = resp.value('data.buckets[0].taskAttachments')
            assert [f for f in result_match if f['uuid'] == file_uuid][0]['name'] == name

    @story('T23032 文件-文件管理：检查文件描述')
    @parametrize('param', p.query_file())
    def test_update_file_desc(self, param, prepared_files):
        scenes = [
            ("修改文件描述为空", "", {"code": 200, "errcode": "OK", "type": "OK"}),
            ("修改文件描述的长度在限制范围内", "wegqweg", {"code": 200, "errcode": "OK", "type": "OK"}),
            ("修改文件描述的长度超出限制范围", 'sdgrwergwgqewgqwegqwegqwegsdgrwergwgqewgqwegqwegqwegsdgrwergwgqeasdfasdfasd',
             {"code": 801, "errcode": "InvalidParameter.Resource.Description.TooLong", "field": "Description",
              "model": "Resource", "reason": "TooLong", "type": "InvalidParameter"})
        ]
        file_uuid = prepared_files['file_uuid'][0]
        for s in scenes:
            with step(s[0]):
                desc = s[1]
                update_param = p.update_file('TestImg_Zupdate', desc)[0]
                update_param.uri_args({"file_uuid": file_uuid})
                res = self.call(UpdateAttachment, update_param, status_code=s[2]["code"])
                assert res.json() == s[2]
                resp = self.call(api.ItemGraphql, param)
                result_match = resp.value('data.buckets[0].taskAttachments')
                if s[2]['code'] == 200:
                    assert [f for f in result_match if f['uuid'] == file_uuid][0]['description'] == desc

    @story('T23030 文件-文件管理：检查文件列表排序')
    def test_file_list_sort(self):
        scenes = [
            ('上传时间-倒序', {"createTime": "DESC"}, 'createTime'),
            ('文件大小-倒序', {"size": "DESC"}, 'size'),
            ('文件类型-倒序', {"fileCategory": "DESC"}, 'fileCategory'),
            ('上传者-倒序', {"owner": {
                "namePinyin": "DESC"
            }}, 'owner.name'),
            ('所属工作项-倒序', {"summaryPinyin": "DESC"}, 'summary'),
            ('文件名称-倒序', {"namePinyin": "DESC"}, 'name')
        ]

        for s in scenes:
            k = s[2]
            with step(f'{s[0]}, key: {k}'):
                param = p.query_file(order_by=s[1])[0]
                resp = self.call(api.ItemGraphql, param)
                result_match = resp.value('data.buckets[0].taskAttachments')
                f_list_old = [parse_index(f, k) for f in result_match]
                if k == 'name':
                    f_list_new = sorted(f_list_old, key=str.lower, reverse=True)
                else:
                    f_list_new = f_list_old.copy()
                    f_list_new.sort(reverse=True)
                assert f_list_old == f_list_new, f"{k}排序不正确"

    @story('T23028 文件-文件管理：进入文件组件，检查文件展示信息')
    def test_file_info(self, prepared_files):
        file_uuid = prepared_files['file_uuid'][0]
        param = p.get_file_info()[0]
        param.uri_args({"file_uuid": file_uuid})
        res = self.call(PreviewImgAttachment, param)
        assert res.value('uuid') == file_uuid \
               and res.value('ref_type') == 'task' \
               and res.value('type') == 'file' \
               and res.value('mime') == 'image/png'
        assert [k for k in ['name', 'owner_uuid', 'size', 'create_time', 'description', 'url'] if
                k not in res.json().keys()] == []
