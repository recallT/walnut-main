#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_upload_file.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/9 
@Desc    ：
"""

from falcons.com.nick import feature, story, mark, parametrize, step
from falcons.helper import mocks

from main.actions.task import TaskAction
from main.api.task import TaskAdd, ResAttUpload, UpBox, TaskBatchDelete
from main.params import task


@feature('新建任务-上传文件')
class TestUploadFile:
    @mark.smoke
    @story('T138957 任务-上传文件')
    @parametrize('param', task.task_add())
    def test_task_upload_file(self, param):
        """任务-上传文件"""
        uid = param.json['tasks'][0]['uuid']
        img_name = f"test_img_{mocks.ones_uuid()}"

        with step('获取工作项属性数据'):
            j = TaskAction.task_stamp(flush=True)
            field_conf_uid = [c['default_value'] for c in j['field_config']['field_configs'] if
                              c['field_uuid'] == 'field012']  # 用默认值就好了
            issue_conf_uid = [c['issue_type_uuid'] for c in j['issue_type_config']['issue_type_configs'] if
                              c['name'] == '任务']  # 获取任务工作项的属性uuid
            # update param value
            param.json['tasks'][0]['field_values'][1] |= {'value': field_conf_uid[0]}
            param.json['tasks'][0] |= {'issue_type_uuid': issue_conf_uid[0]}

        with step('新建任务'):
            t = TaskAdd()
            # 调用接口
            t.call(param.json, **param.extra)
            # 检查接口响应码
            t.is_response_code(200)

        with step('上传文件-token'):
            q = ResAttUpload()

            jsn = {
                "type": "attachment",
                "name": img_name,
                "ref_id": uid,
                "ref_type": "task",
                "description": ""
            }
            q.call(jsn, **param.extra)
            q.is_response_code(200)
            j = q.json()
            token = j['token']
            url = j['upload_url']

        with step('上传文件'):
            """"""
            box = UpBox()
            box.call({'token': token, 'img_name': img_name}, url)

            box.is_response_code(200)

        with step('清理测试工作项'):
            """"""
            delete = TaskBatchDelete()
            task_uuid = {
                "tasks": [
                    uid
                ]
            }
            delete.call(task_uuid, **param.extra)

            delete.is_response_code(200)
