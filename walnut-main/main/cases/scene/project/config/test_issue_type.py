"""
@File    ：test_issue_type.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/5/9
@Desc    ：项目-项目设置-工作项类型
"""
import time

from falcons.check import Checker
from falcons.com.meta import UiMeta
from falcons.com.nick import feature, story, parametrize, fixture, step

from main.actions.task import TaskAction
from main.api import issue as api
from main.api import project as prj
from main.params import issue as ise


@fixture(scope='module')
def _issues_():
    """
    主要是记录key 用于清理测试数据
    :return:
    """
    return []


@fixture(scope='module')
def _issues_uuid():
    return []


@fixture(scope='module', autouse=True)
def _clear_issue(_issues_):
    """
    用于清理测试数据
    :return:
    """
    yield
    print('Delete test issue type....')
    delete = api.IssueDelete()
    p = ise.delete_issue()[0]

    def _delete(issue_id):
        p.uri_args({'issue_uuid': issue_id})
        delete.call(**p.extra)

    for issue in _issues_:
        for c in range(10):
            print(f'Trying {c + 1}...')
            _delete(issue['uuid'])
            if delete.response.status_code == 200:
                break
            else:
                time.sleep(1)


@feature('项目设置')
class TestIssueTypeNew(Checker):

    @story('T123387 工作项类型：添加单个工作项类型（标准工作项')
    @parametrize('param', ise.add_standard_issue())
    def test_add_std_issue(self, param, _issues_, _issues_uuid):
        """"""
        self.add_issue(_issues_, _issues_uuid, param)

    @story('T123388 工作项类型：添加单个工作项类型（子工作项）')
    @parametrize('param', ise.add_sub_issue())
    def test_add_sub_issue(self, param, _issues_, _issues_uuid):
        """"""
        self.add_issue(_issues_, _issues_uuid, param)

    @story('T123392 工作项类型：添加属性到工作项类型')
    def test_add_field_to_issue(self):
        """"""

    @story('123371 工作项类型：从已有项目复制（复制单个）')
    def test_copy_one_issue_type_config(self, _issues_uuid):
        # 将工作项添加到项目中
        p = ise.add_project_issue()[0]
        p.json['issue_type_uuids'] = _issues_uuid
        self.call(api.IssueProjectAdd, p)

        with step('从已有项目复制一个工作项类型'):
            param = ise.copy_issue_type_config([_issues_uuid[0]])[0]
            param.uri_args({'project_uuid': UiMeta.env.project_uuid_ui})
            self.call(api.CopyIssueTypeConfig, param)

        with step('复制后从ui项目中删除改工作项'):
            param.uri_args({'issue_uuid': _issues_uuid[0]})
            self.call(api.IssueProjectDelete, param, with_json=False)

    @story('123372 工作项类型：从已有项目复制（复制多个）')
    def test_multi_issue_type_config(self, _issues_uuid):
        with step('从已有项目复制多个工作项类型'):
            param = ise.copy_issue_type_config(_issues_uuid)[0]
            param.uri_args({'project_uuid': UiMeta.env.project_uuid_ui})
            self.call(api.CopyIssueTypeConfig, param)

    @story('123382 工作项类型：删除工作项类型（工作项类型数量为1）')
    @parametrize('param', ise.delete_project_issue())
    def test_del_have_data_issue_1(self, param):
        task_uuid = TaskAction.new_issue()[0]
        issue_uuid = TaskAction.issue_type_uuid()[0]

        time.sleep(1)
        param.uri_args({'issue_uuid': issue_uuid})
        resp = self.call(api.IssueProjectDelete, param, status_code=400)

        resp.check_response('errcode', 'InUse.IssueType')

    @story('123384 工作项类型：删除工作项类型（项目中已有工作项）')
    @parametrize('param', ise.delete_project_issue())
    def test_del_have_data_issue_2(self, param):
        task_uuid = TaskAction.new_issue(issue_type_name='需求')[0]
        issue_uuid = TaskAction.issue_type_uuid('需求')[0]

        time.sleep(1)
        param.uri_args({'issue_uuid': issue_uuid})
        resp = self.call(api.IssueProjectDelete, param, status_code=400)

        resp.check_response('errcode', 'InUse.IssueType')

    @story('123383 工作项类型：删除工作项类型（项目中无工作项）')
    @parametrize('param', ise.delete_project_issue())
    def test_del_no_data_issue(self, param, _issues_uuid):
        param.uri_args({'issue_uuid': _issues_uuid[1]})
        self.call(api.IssueProjectDelete, param)

    @classmethod
    def get_field_uuid(cls, issue_uuid, token=None):
        p1 = ise.issue_field_config()[0]
        p1.uri_args({'issue_uuid': issue_uuid})
        ifc = api.IssueFieldConfig(token)
        ifc.call(**p1.extra)
        ifc.is_response_code(200)
        curr_field_uuid = [i['field_uuid'] for i in ifc.json()['items']]

        return curr_field_uuid

    @classmethod
    def add_issue(cls, store, uuid_store, param, token=None):
        add = api.IssuesAdd(token)
        add.call(param.json, **param.extra)
        icon = param.json['issue_type']['icon']
        name = param.json['issue_type']['name']

        add.is_response_code(200)
        add.check_response('icon', icon)
        add.check_response('name', name)

        with step('检查新建的工作项类型'):
            s_param = ise.show_issue_list()[0]
            stamps = prj.TeamStampData(token)
            stamps.call(s_param.json, **s_param.extra)

            stamps.is_response_code(200)
            list_issue = stamps.json()['issue_type']['issue_types']
            issue_names = [c['name'] for c in list_issue]
            issue_icon = [c['icon'] for c in list_issue if c['name'] == name]

            assert name in issue_names, '工作项名字不一致'
            assert icon in issue_icon, '图标配置不一致'
        # Store new issue for teardown step
        store.append(add.json())
        uuid_store.append(add.value('uuid'))
