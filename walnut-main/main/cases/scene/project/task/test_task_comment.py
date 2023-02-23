"""
@File    ：test_task_comment.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/21
@Desc    ：任务详情-评论测试用例
"""
from falcons.check import CheckerChain
from falcons.com.nick import feature, story, fixture, parametrize

from main.actions.task import TaskAction
from main.api import task as api
from main.params import task as p


@fixture(scope='module')
def task():
    """测试任务"""
    return TaskAction.new_issue()[0]


@fixture(scope='module')
def _message():
    """评论 UUID 缓存"""
    return []


@fixture(scope='module')
def del_task(task):
    """删除测试任务"""
    yield
    TaskAction.del_task(task)


@feature('任务管理-任务详情')
class TestTaskComment(CheckerChain):
    """"""

    @story('T134471 任务详情-评论：添加评论')
    @parametrize('param', p.message_add())
    def test_comment_add(self, param, task, _message):
        """添加评论"""
        message_p = p.task_messages()[0]
        param.uri_args({'task_uuid': task})
        self.call('添加评论', api.TaskSendMessage, param) \
            .assert_response('code', 200) \
            .update_url(message_p, {'task_uuid': task}) \
            .call('查看评论', api.TaskMessages, message_p) \
            .assert_response('messages[0].text', param.json_value('text')) \
            .cache_to(_message, 'messages[0].uuid')

    @story('T134448 任务详情-评论：编辑评论')
    @parametrize('param', p.message_update())
    def test_comment_update(self, param, task, _message):
        """编辑评论"""

        param.json_update('uuid', _message[0])
        param.uri_args({'task_uuid': task, 'message_uuid': _message[0]})
        message_p = p.task_messages()[0]

        self.call('编辑评论', api.TaskMessageUpdate, param) \
            .assert_response('code', 200) \
            .update_url(message_p, {'task_uuid': task}) \
            .call('查看评论', api.TaskMessages, message_p) \
            .assert_response('messages[0].text', param.json_value('text'))

    @story('T134469 任务详情-评论：上传附件（有编辑工作项权限）')
    @story('T134474 任务详情-评论：通过快捷操作上传图片')
    @story('136231 文件：上传文件')
    def test_comment_update_file(self, task):
        """"""
        TaskAction.upload_file(task)

    @story('T134456 任务详情-评论：回复评论（回复自己的评论）')
    @parametrize('param', p.message_reply())
    def test_comment_replay_own(self, param, task, _message):
        param.json_update('replied_message_uuid', _message[0])
        param.uri_args({'task_uuid': task})

        message_p = p.task_messages()[0]

        self.call('回复评论', api.TaskSendMessage, param) \
            .assert_response('code', 200) \
            .update_url(message_p, {'task_uuid': task}) \
            .call('查看评论', api.TaskMessages, message_p) \
            .assert_response('messages[0].text', param.json_value('text')) \
            .cache_to(_message, 'messages[0].uuid')

    @story('T134473 任务详情-评论：通过快捷操作进行换行')
    @parametrize('param', p.message_add(multi=True))
    def test_comment_add_multi_lines(self, param, task, _message):
        """添加多行评论"""
        message_p = p.task_messages()[0]
        param.uri_args({'task_uuid': task})
        self.call('添加可换行评论', api.TaskSendMessage, param) \
            .assert_response('code', 200) \
            .update_url(message_p, {'task_uuid': task}) \
            .call('查看评论', api.TaskMessages, message_p) \
            .assert_response('messages[0].text', param.json_value('text')) \
            .cache_to(_message, 'messages[0].uuid')

    @story('T134464 任务详情-评论：删除评论')
    @parametrize('param', p.message_delete())
    def test_comment_delete(self, param, task, _message):
        """"""

        for m_uid in _message:
            param.uri_args({'task_uuid': task, 'message_uuid': m_uid})

            self.call('删除评论', api.TaskMessageDelete, param)
