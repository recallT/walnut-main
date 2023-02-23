"""
@File    ：test_task_detail_1.py
@Author  ：zhangyonghui
@Email   ：zhangyonghui@ones.ai
@Date    ：2022/6/7
@Desc    ：任务管理-任务详情 子工作项
"""
from falcons.check import Checker, go
from falcons.com.nick import story, fixture, feature, step

from main.actions.task import TaskAction
from main.api import issue as i
from main.api.project import ItemGraphql, TeamStampData
from main.api.task import TaskAdd
from main.params import issue
from main.params.proj import get_task_info


@fixture(scope='module', autouse=True)
def add_task():
    """新增一个任务"""
    task = TaskAction.new_issue()[0]

    return task


@fixture(scope='module', autouse=True)
def add_new_issue():
    # 创建一个子工作项类型
    param_new_issue = issue.add_sub_issue()[0]
    resp = go(i.IssuesAdd, param_new_issue)
    new_issue_uuid = resp.value('uuid')
    new_issue_name = resp.value('name')
    # 将工作项导入到项目内
    p = issue.add_project_issue()[0]
    p.json['issue_type_uuids'] = [new_issue_uuid]
    go(i.IssueProjectAdd, p)

    return new_issue_uuid, new_issue_name


@fixture(scope='module', autouse=True)
def del_new_issue(add_new_issue, add_task):
    """删除项目内，配置中心的工作项信息"""
    yield
    TaskAction.del_task(add_task)

    new_issue_uuid, new_issue_name = add_new_issue

    p = issue.delete_project_issue()[0]
    p.uri_args({'issue_uuid': new_issue_uuid})
    go(i.IssueProjectDelete, p)

    param = issue.delete_issue()[0]
    param.uri_args({'issue_uuid': new_issue_uuid})
    go(i.IssueDelete, param)


@feature('任务管理-任务详情-子工作项')
class TestTaskDetailTwo(Checker):

    @story('T134515 任务详情-子工作项：子工作项新建子工作项')
    def test_add_sub_task(self, add_task, add_new_issue):
        new_issue_uuid, new_issue_name = add_new_issue
        with step('创建自定义子工作项类型工作项'):
            sub_task = TaskAction.new_issue(parent_uuid=add_task, issue_type_name=new_issue_name)[0]
        with step('选择子工作项，选择删除'):
            TaskAction.del_task(sub_task).check_response('code', 200)

    @story('T134514 任务详情-子工作项：子工作项批量新建多个子工作项')
    def test_add_more_sub_task(self):
        task = TaskAction.new_issue()[0]
        with step('批量创建子工作项'):
            TaskAction.new_issue(parent_uuid=task, issue_type_name="子任务", is_batch=True)
            TaskAction.del_task(task).check_response('code', 200)

    @story('T134501 任务详情-子工作项：删除二级子工作项（子工作项下有工作项）')
    def test_del_sub_task1(self, add_task):
        sub_task = TaskAction.new_issue(parent_uuid=add_task, issue_type_name="子任务")[0]
        # 子任务下再创建一个子任务
        issue_uuid = TaskAction.new_issue(parent_uuid=sub_task, issue_type_name="子任务")[0]
        with step('选择子工作项，选择删除'):
            TaskAction.del_task(sub_task) \
                .check_response('code', 200)

    @story('T134500 任务详情-子工作项：删除二级子工作项（子工作项下无工作项））')
    def test_del_sub_task(self, add_task):
        sub_task = TaskAction.new_issue(parent_uuid=add_task, issue_type_name="子任务")[0]
        with step('选择子工作项，选择删除'):
            TaskAction.del_task(sub_task) \
                .check_response('code', 200)

    @story('T134499 任务详情-子工作项：标准工作项新建子工作项（子需求）')
    def test_task_add_sub_demand(self, add_task):
        sub_demand = TaskAction.new_issue(parent_uuid=add_task, issue_type_name="子需求")[0]
        with step('查看需求详情'):
            param = get_task_info(sub_demand)[0]
            resp = self.call(ItemGraphql, param)
            resp.check_response('data.task.uuid', sub_demand)
            resp.check_response('data.task.parent.uuid', add_task)

    @story('T134498 任务详情-子工作项：标准工作项新建子工作项（子任务）')
    def test_task_add_sub_task(self, add_task):
        sub_task = TaskAction.new_issue(parent_uuid=add_task, issue_type_name="子任务")[0]
        with step('查看任务详情'):
            param = get_task_info(sub_task)[0]
            resp = self.call(ItemGraphql, param)
            resp.check_response('data.task.uuid', sub_task)
            resp.check_response('data.task.parent.uuid', add_task)

    @story('T134497 任务详情-子工作项：标准工作项新建子工作项（子检查项）')
    def test_add_sub_check_item(self, add_task):
        with step('前置条件：在项目中添加子检查项类型工作项'):
            s_param = issue.show_issue_list()[0]
            stamps = self.call(TeamStampData, s_param)

            list_issue = stamps.json()['issue_type']['issue_types']
            sys_issues = [c['uuid'] for c in list_issue if c['name'] == '子检查项']
            p = issue.add_project_issue()[0]
            p.json['issue_type_uuids'] = sys_issues
            go(i.IssueProjectAdd, p)
        with step('创建子检查项类型子工作项'):
            sub_task = TaskAction.new_issue(parent_uuid=add_task, issue_type_name="子检查项")[0]
        with step('查看任务详情'):
            param = get_task_info(sub_task)[0]
            resp = self.call(ItemGraphql, param)
            resp.check_response('data.task.uuid', sub_task)
            resp.check_response('data.task.parent.uuid', add_task)

    @story('T134496 任务详情-子工作项：标准工作项新建子工作项（自定义子工作项类型）')
    def test_add_new_issue_task(self, add_task, add_new_issue):
        new_issue_uuid, new_issue_name = add_new_issue
        with step('创建自定义子工作项类型工作项'):
            sub_task = TaskAction.new_issue(parent_uuid=add_task, issue_type_name=new_issue_name)[0]
        with step('选择子工作项，选择删除'):
            TaskAction.del_task(sub_task).check_response('code', 200)

    @story('T134494 任务详情-子工作项：标准工作项批量新建多个子工作项')
    def test_add_more_tasks(self, add_task, add_new_issue):
        new_issue_uuid, new_issue_name = add_new_issue
        with step('批量创建子工作项'):
            # 生成批量创建子工作项参数
            task_param = TaskAction.new_issue(parent_uuid=add_task, issue_type_name="子需求",
                                              is_batch=True,
                                              param_only=True)
            # 替换sub_issue_type_uuid为自定义工作项uuid
            task_param.json['tasks'][0]['sub_issue_type_uuid'] = new_issue_uuid
            resp = go(TaskAdd, task_param)
            resp.check_response('tasks[0].sub_issue_type_uuid', new_issue_uuid)
        with step('选择删除自定义工作项'):
            TaskAction.del_task(resp.value('tasks[0].uuid')).check_response('code', 200)

    @story('T133613 任务管理-更多：子工作项以此新建工作项（新建系统类型工作项）')
    def test_add_new_task_type(self, add_task, add_new_issue):
        with step('前置条件 创建任务A 子工作项B'):
            new_issue_uuid, new_issue_name = add_new_issue
            sub_task = TaskAction.new_issue(parent_uuid=add_task, issue_type_name=new_issue_name)[0]

        with step('子工作项以此新建工作项'):
            issue_uuid = TaskAction.new_issue()[0]

    @story('T121433 更改任务状态：步骤属性设为必填，变更状态时不填')
    def test_demo(self):
        ...
