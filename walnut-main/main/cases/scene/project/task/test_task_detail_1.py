"""
@File    ：test_task_detail_1.py
@Author  ：zhangyonghui
@Email   ：zhangyonghui@ones.ai
@Date    ：2022/6/7
@Desc    ：任务管理-任务详情 测试情况
"""
from falcons.check import Checker, go
from falcons.com.nick import feature, story, fixture, step, parametrize, mark
from falcons.com.meta import ApiMeta
from main.actions.case import CaseAction
from main.actions.sprint import SprintAction
from main.actions.task import TaskAction
from main.api import case as api
from main.api.project import ItemGraphql
from main.api.task import TaskRelTestPlan, TaskDelRelTestPlan
from main.api.wiki import WikiSpaces, BindWiki, WikiPages, UnBindWiki, TaskAddWikiPages, \
    TaskAddOnlineWikiPages
from main.params import testcase
from main.params.proj import proj_url
from main.params.task import bind_testcase_plan, unbind_testcase_plan, bind_case_result, unbind_case_result, \
    bind_wiki_pages, unbind_wiki_pages, add_new_wiki_pages, bind_new_wiki_pages, add_new_online_wiki_pages, \
    task_upload_wiki
from main.params.testcase import query_libray_modules, query_testplan_list


@fixture(scope='module', autouse=True)
def task_prepare():
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

    # 新增测试计划
    plan_uuid = CaseAction.add_testcase_plan()

    # 关联测试用例
    c = testcase.up_plan_info()
    c.uri_args({'plan_uuid': plan_uuid})
    jsr = {"case_uuids": [case_uuid1, case_uuid2]}

    add = api.CaseRelPlan()
    add.call(jsr, **c.extra)
    add.is_response_code(200)
    return {'task': task, 'sprint': sprint,
            'lib_uuid': lib_uuid, 'plan_uuid': plan_uuid,
            'case': [case_uuid1, case_uuid2]}


@fixture(scope='module', autouse=True)
def get_wiki_info():
    # 查询系统中存在的wiki信息
    param = proj_url()[0]
    resp_spaces = go(WikiSpaces, param).value('spaces[0].uuid')
    param.uri_args({'space_uuid': resp_spaces})
    resp = go(WikiPages, param)
    wiki_uuid = resp.value('pages[0].uuid')
    wiki_title = resp.value('pages[0].title')
    space_uuid = resp.value('pages[0].space_uuid')

    return wiki_uuid, wiki_title, space_uuid


label = ApiMeta.env.label


@mark.skipif(label == 'private' or label == 'dev', reason='环境跳过开箱用例')
@feature('任务管理-任务详情-测试情况')
class TestTaskDetailOne(Checker):

    @story('121301 概览 - 测试计划：新建测试计划')
    @story('T128815 关联测试计划：新增关联测试计划（多个）')
    def test_task_relation_testcase_plan(self, task_prepare):
        with step('前置条件'):
            plan_a_uuid = CaseAction.add_testcase_plan()
            plan_b_uuid = task_prepare['plan_uuid']
        with step('关联测试计划，选择测试两个测试计划,点击确认'):
            param = bind_testcase_plan(task_prepare['task'], [plan_a_uuid, plan_b_uuid])[0]
            param.uri_args({'task_uuid': task_prepare['task']})
            resp = self.call(TaskRelTestPlan, param)
            assert plan_a_uuid, plan_b_uuid in resp.value('success_plans')

    @story('T128816 关联测试计划：移除关联测试计划')
    def test_del_task_relation_testcase_plan(self, task_prepare):
        with step('前置条件，关联测试计划'):
            task = TaskAction.new_issue()[0]
            param = bind_testcase_plan(task, [task_prepare['plan_uuid']])[0]
            param.uri_args({'task_uuid': task_prepare['task']})
            self.call(TaskRelTestPlan, param)

        with step('移除关联测试计划，点击确认'):
            p = unbind_testcase_plan(task, task_prepare['plan_uuid'])[0]
            resp = self.call(TaskDelRelTestPlan, p)
            resp.check_response('code', 200)
            TaskAction.del_task(task)

    @story('T128861 关联用例库用例：新建关联用例')
    def test_task_bind_testcase(self, task_prepare):
        with step('工作项关联测试案例'):
            bind_resp = CaseAction.bind_case(task_prepare['task'], *task_prepare['case'])
            bind_resp.check_response('success_cases', task_prepare['case'])
            bind_resp.check_response('success_tasks[0]', task_prepare['task'])

    @story('T128864 关联用例库用例：移除关联用例')
    def test_task_unbind_testcase(self, task_prepare):
        with step('工作项关联测试案例'):
            task = TaskAction.new_issue()[0]
            bind_resp = CaseAction.bind_case(task, *task_prepare['case'])
            bind_resp.check_response('success_cases', task_prepare['case'])
        with step('解除绑定的用例'):
            resp = CaseAction.unbind_testcase(task_prepare['case'][0], task)
            resp.check_response('code', 200)
            TaskAction.del_task(task)

    @story('T128873 关联执行结果-弹窗：可选用例列表选择一条用例添加')
    def test_task_bind_case_result(self, task_prepare):
        case = [task_prepare['case'][0]]
        param = bind_case_result(task_prepare['task'], task_prepare['plan_uuid'], case)[0]
        resp = self.call(api.BindCase, param)
        resp.check_response('success_cases', case)
        resp.check_response('success_tasks[0]', task_prepare['task'])

    @story('T128875 关联执行结果-弹窗：取消关联已被关联执行结果的数据')
    def test_task_unbind_task_result(self, task_prepare):
        case = [task_prepare['case'][0]]
        task = TaskAction.new_issue()[0]
        param = bind_case_result(task, task_prepare['plan_uuid'], case)[0]
        self.call(api.BindCase, param)
        with step('取消关联执行结果数据'):
            p = unbind_case_result(task, task_prepare['plan_uuid'], task_prepare['case'][0])[0]
            resp = self.call(api.UnBindCase, p)
            resp.check_response('code', 200)

    @story('T128908 关联执行结果：跳转关联执行结果')
    def test_task_testcase_result_info(self, task_prepare):
        with step('前置条件，关联执行结果'):
            case = [task_prepare['case'][0]]
            task = TaskAction.new_issue()[0]
            param = bind_case_result(task, task_prepare['plan_uuid'], case)[0]
            self.call(api.BindCase, param)
        with step('跳转关联执行结果'):
            ref = testcase.query_plan_case_detail()
            ref.json['variables']['testCaseFilter'] |= {"testcaseCase_in": case,
                                                        "testcasePlan_in": [task_prepare['plan_uuid']]}
            ref.json['variables']['libraryStepFilter'] |= {"testcaseCase_in": case}
            ref.json['variables']['planStepFilter'] |= {"testcaseCase_in": case,
                                                        "testcasePlan_in": [task_prepare['plan_uuid']]}
            resp = self.call(ItemGraphql, ref)
            resp.check_response('data.testcaseCaseSteps[0].testcaseCase.uuid', task_prepare['case'][0])
            TaskAction.del_task(task)

    @story('T128909 关联执行结果：新增关联执行结果')
    def test_new_task_bind_case_result(self, task_prepare):
        task = TaskAction.new_issue()[0]
        param = bind_case_result(task, task_prepare['plan_uuid'], task_prepare['case'])[0]
        resp = self.call(api.BindCase, param)
        resp.check_response('success_tasks[0]', task)

        TaskAction.del_task(task)

    @story('T128903 关联执行结果：编辑任务权限控制')
    def test_task_bind_case_result_permission(self, task_prepare):
        with step('用户B（有权限）操作测试情况-关联执行结果'):
            case = [task_prepare['case'][0]]
            task = TaskAction.new_issue()[0]
            param = bind_case_result(task, task_prepare['plan_uuid'], case)[0]
            self.call(api.BindCase, param)
        with step('用户A（无权限）操作测试情况-关联执行结果'):  # todo:
            pass

    @story('T135869 添加关联用例-弹窗-可选用例列表：列表检查')
    def test_check_case_list(self, task_prepare):
        with step('查询关联用例库'):
            param = query_libray_modules()[0]
            resp = self.call(ItemGraphql, param)
            libraries_list = []
            for uuid in resp.value('data.testcaseLibraries'):
                libraries_list.append(uuid['uuid'])
            assert task_prepare['lib_uuid'] in libraries_list
        with step('查询测试计划列表'):
            p = query_testplan_list()[0]
            resp_list = self.call(ItemGraphql, p)
            plan_uuid = []
            for uuid in resp_list.value('data.testcasePlans'):
                plan_uuid.append(uuid['uuid'])
            assert task_prepare['plan_uuid'] in plan_uuid

    @story('T133610 任务管理-更多：子工作项关联用例')
    def test_sub_task_rel_testcase(self, task_prepare):
        sub_task = TaskAction.new_issue(parent_uuid=task_prepare['task'], issue_type_name="子任务")[0]
        with step('工作项关联测试案例'):
            bind_resp = CaseAction.bind_case(sub_task, *task_prepare['case'])
            bind_resp.check_response('success_cases', task_prepare['case'])
            bind_resp.check_response('success_tasks[0]', sub_task)

    @story('T147950 新建工作项：关联wiki')
    @parametrize('param', proj_url())
    def test_task_relation_wiki_pages(self, param, get_wiki_info, task_prepare):
        # 查询系统中存在的wiki信息
        wiki_uuid, wiki_title, space_uuid = get_wiki_info
        with step('关联wiki'):
            param_bind = bind_wiki_pages(wiki_uuid, space_uuid, wiki_title)[0]
            param_bind.uri_args({'task_uuid': task_prepare['task']})
            resp_bind = self.call(BindWiki, param_bind)
            resp_bind.check_response('code', 200)

    @story('T148048 新建工作项：取消关联wiki')
    @story("T148076 工作项详情：取消关联wiki")
    @story("T148073 工作项详情：关联wiki")
    def test_del_task_relation_wiki_pages(self, get_wiki_info):
        wiki_uuid, wiki_title, space_uuid = get_wiki_info
        task = TaskAction.new_issue()[0]
        with step('关联wiki'):
            param_bind = bind_wiki_pages(wiki_uuid, space_uuid, wiki_title)[0]
            param_bind.uri_args({'task_uuid': task})
            resp_bind = self.call(BindWiki, param_bind)
            resp_bind.check_response('code', 200)
        with step('解除关联wiki'):
            param_unbind = unbind_wiki_pages(wiki_title, wiki_uuid)[0]
            param_unbind.uri_args({'task_uuid': task})
            resp_unbind = self.call(UnBindWiki, param_unbind)
            resp_unbind.check_response('code', 200)

    @story('T146649 手动新建：新建「wiki 协同页面」')
    @story('148181 新建关联wiki页面：导入为协同编辑文档')
    def test_task_add_new_online_wiki_bind(self, get_wiki_info):
        wiki_uuid, wiki_title, space_uuid = get_wiki_info
        task = TaskAction.new_issue()[0]
        with step('新建关联「wiki 协同页面」'):
            param = add_new_online_wiki_pages(wiki_uuid, space_uuid)[0]
            page_uuid = self.call(TaskAddOnlineWikiPages, param).value('uuid')
            # 关联
            param_bind = bind_new_wiki_pages(page_uuid, space_uuid, wiki_uuid)[0]
            param_bind.uri_args({'task_uuid': task})
            resp_bind = self.call(BindWiki, param_bind)
            resp_bind.check_response('code', 200)

    @story('T148173 新建关联wiki页面：新建关联wiki页面流程」')
    def test_task_add_new_wiki_bind(self, get_wiki_info):
        wiki_uuid, wiki_title, space_uuid = get_wiki_info
        task = TaskAction.new_issue()[0]
        with step('新建关联wiki页面'):
            param = add_new_wiki_pages(wiki_uuid)[0]
            param.uri_args({'space_uuid': space_uuid})
            page_uuid = self.call(TaskAddWikiPages, param).value('uuid')
            # 关联
            param_bind = bind_new_wiki_pages(page_uuid, space_uuid, wiki_uuid)[0]
            param_bind.uri_args({'task_uuid': task})
            resp_bind = self.call(BindWiki, param_bind)
            resp_bind.check_response('code', 200)

    @story('T148180 T146654 T146655 新建关联wiki页面：导入为wiki页面流程')
    def test_task_upload_wiki_word(self, task_prepare, get_wiki_info):
        wiki_uuid, wiki_title, space_uuid = get_wiki_info
        with step('上传文件-token'):
            param = task_upload_wiki(space_uuid)[0]
        #     res = self.call(ResAttUpload, param)
        #
        #     token = res.value('token')
        #     url = res.value('upload_url')
        #     file_uuid = res.value('resource_uuid')
        #
        # with step('点击确定-上传文件'):  # todo:文档类型上传失败
        #     """"""
        #     box = UpBox()
        #     box.call({'token': token, 'img_name': ''}, url)
        #     box.is_response_code(200)
        #
        # with step('导入文档'):
        #     param = word_import(wiki_uuid, task_prepare['task'])[0]
        #     resp = self.call(TaskWordImport, param)