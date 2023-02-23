"""
@Desc：全局配置-工作项-关联关系类型
"""
import time

from falcons.check import Checker, go
from falcons.com.nick import feature, story, fixture, step

from main.actions.task import TaskAction
from main.api import project as prj
from main.params import conf


@fixture(scope='module')
def link_key():
    return []


@fixture(scope='module', autouse=True)
def link_del(link_key):
    yield
    for key in link_key:
        param = conf.delete_link_type(key)[0]
        go(prj.ItemGraphql, param)


@feature('全局配置-工作项-关联关系')
class TestIssueLinkType(Checker):

    def add_link_type(self, storage, source='{}', target='{}', model=102):
        """新增关联关系"""
        param = conf.add_link_type(source, target, model)[0]
        resp = self.call(prj.ItemGraphql, param)

        key = resp.value('data.addObjectLinkType.key')
        storage.append(key)

        return key

    def query_link_type(self):
        """查询关联关系"""
        param = conf.q_link_type()[0]
        resp = self.call(prj.ItemGraphql, param)

        keys = [k['key'] for k in resp.value('data.objectLinkTypes')]

        return keys

    @story('131332 新建单向一对多关联关系')
    def test_add_unidirectional_one_to_many(self, link_key):
        with step('选择‘单向一对多关联关系’新建，输入内容'):
            key = self.add_link_type(link_key)

        with step('工作项中打开关联弹窗。选项中可选此关联关系'):
            assert key in self.query_link_type()

    @story('131333 新建单向一对多关联关系（指定工作项类型）')
    def test_add_unidirectional_one_to_many_and_assign(self, link_key):
        with step('发起关联方和被关联方的工作项类型指定A工作项类型，点击确定'):
            issue_uuid = TaskAction.issue_type_uuid()[0]
            condition = \
                "{\"lock_filter\":[{\"field\":\"issueType\",\"operator\":\"in\",\"operand\":[\"%s\"]}]}" % issue_uuid

            key = self.add_link_type(link_key, condition, condition)

        with step('A工作项类型工作项中打开关联弹窗。选项中可选此关联关系'):
            assert key in self.query_link_type()

    @story('131330 新建单向多对多关联关系')
    def test_add_unidirectional_many_to_many(self, link_key):
        with step('选择‘单向多对多关联关系’新建，输入内容'):
            key = self.add_link_type(link_key, model=202)

        with step('工作项中打开关联弹窗。选项中可选此关联关系'):
            assert key in self.query_link_type()

    @story('131331 新建单向多对多关联关系（指定工作项类型）')
    def test_add_unidirectional_many_to_many_and_assign(self, link_key):
        with step('发起关联方和被关联方的工作项类型指定A工作项类型，点击确定'):
            issue_uuid = TaskAction.issue_type_uuid()[0]
            condition = \
                "{\"lock_filter\":[{\"field\":\"issueType\",\"operator\":\"in\",\"operand\":[\"%s\"]}]}" % issue_uuid

            key = self.add_link_type(link_key, condition, condition, model=202)

        with step('A工作项类型工作项中打开关联弹窗。选项中可选此关联关系'):
            assert key in self.query_link_type()

    @story('131335 新建相互关联关联关系')
    def test_add_interrelated(self, link_key):
        with step('选择‘相互关联关系’新建，输入内容'):
            key = self.add_link_type(link_key, model=212)

        with step('工作项中打开关联弹窗。选项中可选此关联关系'):
            assert key in self.query_link_type()

    @story('131336 新建相互关联关联关系（指定工作项类型）')
    def test_add_interrelated_and_assign(self, link_key):
        with step('被关联的工作项类型指定A工作项类型，点击确定'):
            issue_uuid = TaskAction.issue_type_uuid()[0]
            condition = \
                "{\"lock_filter\":[{\"field\":\"issueType\",\"operator\":\"in\",\"operand\":[\"%s\"]}]}" % issue_uuid

            key = self.add_link_type(link_key, condition, condition, model=212)

        with step('A工作项类型工作项中打开关联弹窗。选项中可选此关联关系'):
            assert key in self.query_link_type()

    @story('131324 编辑关联关系')
    def test_update_link(self, link_key):
        """编辑关联关系"""
        with step('修改关联关系名称和描述'):
            param = conf.update_link_type(link_key[0], 102)[0]
            resp = self.call(prj.ItemGraphql, param)

            resp.check_response('data.updateObjectLinkType.key', link_key[0])

    @story('131329 删除关联关系（已经有工作项正在使用）')
    def test_delete_used_link(self, link_key):
        link_uuid = link_key[0].split('-')[1]

        with step('前提条件'):
            # 创建两个任务工作项
            task_uuids, backup_task_uuid = TaskAction.new_issue_batch(2)
            time.sleep(2)

            # 有工作项正在使用关联关系A
            parm = conf.link_related_task(task_uuids[0], link_uuid)[0]
            parm.uri_args({'tasks_uuid': task_uuids[1]})

            self.call(prj.LinkRelatedTask, parm)

        with step('点击删除关联关系'):
            time.sleep(1)
            param = conf.delete_link_type(link_key[0])[0]
            resp = self.call(prj.ItemGraphql, param, status_code=403)

            resp.check_response('errcode', 'ConstraintViolation.Expired')

        with step('移除工作项的关联关系'):
            self.call(prj.DeleteLinkRelatedTask, parm)

    @story('131328 删除关联关系（没有工作项正在使用）')
    def test_delete_unused_link(self, link_key):
        with step('点击删除关联关系'):
            param = conf.delete_link_type(link_key[0])[0]
            # resp = self.call(prj.ItemGraphql, param)
            #
            # resp.check_response('data.deleteObjectLinkType.key', link_key[0])
