"""
@File    ：test_deploy.py
@Author  ：zhangyonghui
@Email   ：zhangyonghui@ones.ai
@Date    ：2022/5/14
@Desc    ：发布管理测试用例
"""
from falcons.check import Checker
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, parametrize, fixture, step, mark
from falcons.helper import mocks

from main.actions.pro import PrjAction
from main.actions.task import TaskAction
from main.api.project import GetDeployStatus, DeployUpdateStatusPublish, UpdateTransitStatus, DeploySetTask, \
    ItemGraphql, DeployInfo
from main.api.task import TaskUpdate3, TaskAdd
from main.helper.extra import Extra
from main.params import proj
from main.params.proj import update_deploy_status, proj_url, update_transit_status, batch_set_publish_version, \
    get_deploy_info, get_task_info, get_isu_task_list, get_deploy_list_graphql, update_deploy_relation_field


@fixture(scope='module', autouse=True)
def add_deploy_component():
    # 1.先添加一个【发布】 组件
    PrjAction.add_component('发布')

    yield
    PrjAction.remove_prj_component('发布')


@fixture()
def add_deploy_tasks():
    """ 添加发布任务"""
    return PrjAction.add_deploy_task()


@fixture()
def add_deploy_connect_task(add_deploy_tasks):
    """新增发布A，新增需求B，进行关联"""
    # 创建需求，返回task_uuid
    ise = TaskAction.new_issue(issue_type_name='需求', is_batch=False)[0]
    pam = batch_set_publish_version("add", [ise])[0]
    pam.uri_args({'tasks_uuid': add_deploy_tasks})
    # 发布和需求进行关联操作
    t = DeploySetTask()
    t.call(pam.json, **pam.extra)
    # 返回 需求UUID，发布UUID
    return ise, add_deploy_tasks


@feature('发布管理')
class TestDeploy(Checker):

    @story('T143652 发布-快速操作：当前发布状态为「未发布」，检查快速修改状态按钮')
    @parametrize('param', proj_url())
    def test_deploy_unpublished(self, add_deploy_tasks, param):
        with step('查看发布详情'):
            param.uri_args({'tasks_uuid': add_deploy_tasks})
            resp = self.call(GetDeployStatus, param)
            resp.check_response('transitions[0].name', '发布')
            resp.check_response('transitions[1].name', '关闭发布')

        with step('点击「发布」'):
            transition_uuid = resp.json()['transitions'][0]['uuid']
            # 修改发布状态为发布
            pam = update_deploy_status(transition_uuid, add_deploy_tasks)[0]
            r = self.call(DeployUpdateStatusPublish, pam)
            r.check_response("async_token", "")

        with step('点击「关闭」'):
            resp1 = self.call(GetDeployStatus, param)
            resp1.check_response('transitions[0].name', '取消发布')
            transition_uuid1 = resp1.json()['transitions'][0]['uuid']
            pam1 = update_transit_status(transition_uuid1)[0]
            pam1.uri_args({'tasks_uuid': add_deploy_tasks})
            response = self.call(UpdateTransitStatus, pam1)
            response.check_response("async_token", "")

            resp2 = self.call(GetDeployStatus, param)
            transition_uuid2 = resp2.json()['transitions'][1]['uuid']
            pam2 = update_transit_status(transition_uuid2)[0]
            pam2.uri_args({'tasks_uuid': add_deploy_tasks})

            response1 = self.call(UpdateTransitStatus, pam2)
            response1.check_response("async_token", "")

    @story('T143638 发布-快速操作：当前发布状态为「关闭」，检查快速修改状态按钮')
    @parametrize('param', proj_url())
    def test_deploy_closed(self, add_deploy_tasks, param):
        with step('查看发布详情'):
            param.uri_args({'tasks_uuid': add_deploy_tasks})
            resp = self.call(GetDeployStatus, param)
            resp.check_response('transitions[0].name', '发布')
            resp.check_response('transitions[1].name', '关闭发布')

        with step('点击「关闭」'):
            transition_uuid = resp.json()['transitions'][1]['uuid']
            # 修改发布状态为关闭
            pam = update_deploy_status(transition_uuid, add_deploy_tasks)[0]
            pam.uri_args({'tasks_uuid': add_deploy_tasks})
            r = self.call(DeployUpdateStatusPublish, pam)
            r.check_response("async_token", "")

    @story('T143623 发布-快速操作：当前发布状态为「已发布」，检查快速修改状态按钮')
    @parametrize('param', proj_url())
    def test_deploy_published(self, add_deploy_tasks, param):
        with step('前置条件'):
            param.uri_args({'tasks_uuid': add_deploy_tasks})
            resp = self.call(GetDeployStatus, param)
            transition_uuid = resp.json()['transitions'][0]['uuid']
            # 修改发布状态为发布
            pam = update_deploy_status(transition_uuid, add_deploy_tasks)[0]
            r = self.call(DeployUpdateStatusPublish, pam)

            r.check_response("async_token", "")

        with step('查看发布A详情'):
            param.uri_args({'tasks_uuid': add_deploy_tasks})
            resp = self.call(GetDeployStatus, param)
            resp.check_response('transitions[0].name', '取消发布')
            transition_uuid1 = resp.json()['transitions'][0]['uuid']

        with step('点击【取消发布】'):
            pam = update_transit_status(transition_uuid1)[0]
            pam.uri_args({'tasks_uuid': add_deploy_tasks})
            response = self.call(UpdateTransitStatus, pam)
            response.check_response("async_token", "")

    @story('T143633 发布内容-规划发布内容：在发布内容tab下新建需求')
    @parametrize('param', proj_url())
    def test_deploy_add_desire(self, add_deploy_connect_task, param):
        with step('点击新建工作项，正确新建需求B'):
            # 创建需求，返回task_uuid ise_uuid
            ise_uuid, tasks_uuid = add_deploy_connect_task

        with step('查看发布A详情'):
            param = get_deploy_info(tasks_uuid)[0]
            response = self.call(ItemGraphql, param)
            # 验证详情中包含需求UUID
            response.check_response('data.task.publishContent[0].path', ise_uuid)
            response.check_response('data.task.publishContent[0].uuid', ise_uuid)
            # 发布详情中包含一个关联项
            response.check_response('data.task.publishContentCount', 1)
        with step('查看需求B详情'):
            param1 = get_task_info(ise_uuid)[0]
            resp = self.call(ItemGraphql, param1)
            # 验证详情中包含发布UUID
            resp.check_response('data.task.publishVersion[0].uuid', tasks_uuid)

    @story('T143643 发布内容-规划发布内容：在发布内容tab下新建任务')
    @parametrize('param', proj_url())
    def test_deploy_add_task(self, add_deploy_tasks, param):
        with step('点击新建工作项，正确新建任务B'):
            # 创建任务，返回task_uuid
            ise = TaskAction.new_issue(issue_type_name='任务', is_batch=False)[0]
            pam = batch_set_publish_version("add", [ise])[0]
            pam.uri_args({'tasks_uuid': add_deploy_tasks})

            # 发布和任务进行关联操作
            resp = self.call(DeploySetTask, pam)
            resp.check_response("code", 200)

            with step('查看发布A详情'):
                param = get_deploy_info(add_deploy_tasks)[0]
                response = self.call(ItemGraphql, param)
                # 验证详情中包含任务UUID
                response.check_response('data.task.publishContent[0].path', ise)
                response.check_response('data.task.publishContent[0].uuid', ise)
                # 发布详情中包含一个关联项
                response.check_response('data.task.publishContentCount', 1)

    @story('T143637 发布内容-规划发布内容：移除发布内容')
    @parametrize('param', proj_url())
    def test_delete_deploy_task(self, add_deploy_connect_task, param):
        with step('前置条件'):
            # 创建发布A，需求B，进行关联
            ise_uuid, tasks_uuid = add_deploy_connect_task

        with step('删除关联需求'):
            pam = batch_set_publish_version("delete", [ise_uuid])[0]
            pam.uri_args({'tasks_uuid': tasks_uuid})
            resp = self.call(DeploySetTask, pam)
            resp.check_response("code", 200)

        with step('查看发布A详情'):
            param = get_deploy_info(tasks_uuid)[0]
            res = self.call(ItemGraphql, param)
            # 发布详情中包含0关联项
            res.check_response('data.task.publishContentCount', 0)
        with step('查看需求B详情'):
            param1 = get_task_info(ise_uuid)[0]
            response = self.call(ItemGraphql, param1)
            # 判断发布关联为空
            response.check_response("data.task.publishVersion", [])

    @story('T143635 发布内容-规划发布内容：规划发布内容')
    @parametrize('param', proj_url())
    def test_insert_task_deploy(self, add_deploy_tasks, param):
        with step('前置条件'):
            # 创建一个任务和需求
            ise = TaskAction.new_issue(issue_type_name='缺陷', is_batch=False)[0]
            ise1 = TaskAction.new_issue(issue_type_name='需求', is_batch=False)[0]

        with step('点击规划发布内容'):
            # 查询待规划的需求，任务等
            pam = get_isu_task_list(add_deploy_tasks)[0]
            resp = self.call(ItemGraphql, pam)
            issue_uuids = [r['uuid'] for r in resp.value('data.buckets[0].tasks')]
            assert ise1 in issue_uuids

            pam = batch_set_publish_version("add", [ise, ise1])[0]
            pam.uri_args({'tasks_uuid': add_deploy_tasks})

            # 发布和任务进行关联操作
            resp = self.call(DeploySetTask, pam)
            resp.check_response("code", 200)

        with step('查看发布A详情'):
            param = get_deploy_info(add_deploy_tasks)[0]
            res = self.call(ItemGraphql, param)
            # 发布详情中包含0关联项
            res.check_response('data.task.publishContentCount', 2)
        with step('查看需求B详情'):
            param1 = get_task_info(ise1)[0]
            response = self.call(ItemGraphql, param1)
            # 判断发布关联关系
            response.check_response("data.task.publishVersion[0].uuid", add_deploy_tasks)

    @story('T143631 发布确认：忽略未完成的发布内容')
    @parametrize('param', proj_url())
    def test_ignore_task_status_update_deploy_status(self, add_deploy_connect_task, param):
        with step('前置条件'):
            # 创建发布A，并关联需求B
            ise_uuid, tasks_uuid = add_deploy_connect_task
        with step('选择忽略未完成的发布内容，点击确定'):
            param.uri_args({'tasks_uuid': tasks_uuid})
            resp = self.call(GetDeployStatus, param)
            transition_uuid = resp.json()['transitions'][0]['uuid']
            # 修改发布状态为发布
            pam = update_deploy_status(transition_uuid, tasks_uuid)[0]
            r = self.call(DeployUpdateStatusPublish, pam)

    @story('T143651 发布确认：当前发布有未完成的发布内容，检查发布确认弹窗')
    @parametrize('param', proj_url())
    def test_check_deploy_connect_task_list(self, add_deploy_connect_task, param):
        with step('前置条件'):
            # 创建发布A，并关联需求B
            ise_uuid, tasks_uuid = add_deploy_connect_task
        with step('弹窗显示有x个未完成的发布内容检查'):
            param.uri_args({'tasks_uuid': tasks_uuid})
            resp = self.call(DeployInfo, param)
            resp.check_response('publish_content[0].uuid', ise_uuid)
            # 已完成项 0
            resp.check_response('publish_content_done_count', 0)
            # 未完成项 1
            resp.check_response('publish_content_count', 1)

    @mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过')
    @story('T143640 发布确认：发布A无未完成的发布内容，将发布A状态修改为「已发布」')
    @parametrize('param', proj_url())
    def test_update_deploy_status_publish(self, add_deploy_connect_task, param):
        with step('前置条件'):
            """创建发布A，需求B，并将需求B状态置为关闭状态"""
            ise_uuid, tasks_uuid = add_deploy_connect_task
            resp = PrjAction.get_task_transitions(ise_uuid)
            transitions_uuid = [r['uuid'] for r in resp.value('transitions') if r['name'] == '关闭'][0]
            pam1 = update_transit_status(transitions_uuid)[0]
            pam1.uri_args({'tasks_uuid': ise_uuid})
            response = self.call(UpdateTransitStatus, pam1)
        with step('发布内容检查'):
            param.uri_args({'tasks_uuid': tasks_uuid})
            resp = self.call(DeployInfo, param)
            resp.check_response('publish_content[0].uuid', ise_uuid)
            # 已完成项 1
            resp.check_response('publish_content_done_count', 1)
            # 发布关联总数
            resp.check_response('publish_content_count', 1)

        with step('修改发布状态为发布'):
            transition_uuid = PrjAction.get_task_transitions(tasks_uuid).json()['transitions'][0]['uuid']
            # 修改发布状态为发布
            pam = update_deploy_status(transition_uuid, tasks_uuid)[0]
            r = self.call(DeployUpdateStatusPublish, pam)

    @story('T143645 关联发布：检查「关联发布」下拉列表')
    def test_check_deploy_list(self):
        with step('前置条件'):
            ise_uuid = TaskAction.new_issue(issue_type_name='需求', is_batch=False)[0]
            tasks_uuid = PrjAction.add_deploy_task()
        with step('点击关联发布 下拉列表'):
            view, objects, isu_type_uuid = PrjAction.get_project_isu_list()
            pam = get_deploy_list_graphql(isu_type_uuid)[0]
            resp = self.call(ItemGraphql, pam)
            uuid_list = [r['uuid'] for r in resp.value('data.buckets[0].tasks')]
            assert tasks_uuid in uuid_list

    @story('T143647 关联发布：删除发布A，对应清空「关联发布」为「发布A」的属性值')
    @parametrize('param', proj_url())
    def test_del_deploy_relation_feild1(self, add_deploy_connect_task, param):
        with step('前置条件'):
            ise_uuid, tasks_uuid = add_deploy_connect_task
            tasks_uuid_B = PrjAction.add_deploy_task()
            pam = batch_set_publish_version("add", [ise_uuid])[0]
            pam.uri_args({'tasks_uuid': tasks_uuid_B})
            # 发布和需求进行关联操作
            t = DeploySetTask()
            t.call(pam.json, **pam.extra)
        with step('查看需求详情'):
            param1 = get_task_info(ise_uuid)[0]
            response = self.call(ItemGraphql, param1)
            # 判断需求关联发布数为2
            assert len(response.json()['data']['task']['publishVersion']) == 2
        with step('删除发布B 并查看需求的发布关联'):
            PrjAction.del_isu_task(tasks_uuid_B)

            param1 = get_task_info(ise_uuid)[0]
            response = self.call(ItemGraphql, param1)
            # 判断需求关联发布数为1
            assert len(response.value('data.task.publishVersion')) == 1

    @story('T143625 关联发布：删除「关联发布」属性值')
    @parametrize('param', proj_url())
    def test_del_deploy_relation_feild(self, add_deploy_connect_task, param):
        with step('前置条件'):
            # 创建需求和发布，并进行关联
            ise_uuid, tasks_uuid = add_deploy_connect_task
        with step('删除「关联发布」属性值'):
            pam = update_deploy_relation_field(ise_uuid, [])[0]
            resp = self.call(TaskUpdate3, pam)
        with step('查看发布B详情'):
            param = get_deploy_info(tasks_uuid)[0]
            res_B = self.call(ItemGraphql, param)
            # 发布详情中包含0关联项
            res_B.check_response('data.task.publishContentCount', 0)

    @story('T143644 关联发布：设置「关联发布」属性值')
    @parametrize('param', proj_url())
    def test_set_deploy_relation_feild(self, add_deploy_tasks, param):
        with step('前置条件'):
            ise_uuid = TaskAction.new_issue(issue_type_name='需求', is_batch=False)[0]
            tasks_uuid_B = PrjAction.add_deploy_task()
            tasks_uuid_A = add_deploy_tasks
        with step('设置需求A的「关联发布」属性值：发布B、发布C'):
            pam = update_deploy_relation_field(ise_uuid, [tasks_uuid_B, tasks_uuid_A])[0]
            resp = self.call(TaskUpdate3, pam)
        with step('查看发布B详情'):
            param = get_deploy_info(tasks_uuid_B)[0]
            res_B = self.call(ItemGraphql, param)
            # 发布详情中包含0关联项
            res_B.check_response('data.task.publishContentCount', 1)
        with step('查看发布A详情'):
            param = get_deploy_info(tasks_uuid_A)[0]
            res_A = self.call(ItemGraphql, param)
            # 发布详情中包含1关联项
            res_A.check_response('data.task.publishContentCount', 1)

    @story('T143646 关联发布：修改「关联发布」属性值')
    def test_update_deploy_relation_feild(self, add_deploy_connect_task):
        with step('前置条件'):
            # 创建需求和发布A，并进行关联
            ise_uuid, tasks_uuid_a = add_deploy_connect_task
            # 再创建一个发布B
            tasks_uuid_b = PrjAction.add_deploy_task()

        with step('修改「关联发布」属性值为发布C'):
            pam = update_deploy_relation_field(ise_uuid, [tasks_uuid_b])[0]
            resp = self.call(TaskUpdate3, pam)
        with step('查看发布A详情'):
            param = get_deploy_info(tasks_uuid_a)[0]
            res_a = self.call(ItemGraphql, param)
            # 发布详情中包含0关联项
            res_a.check_response('data.task.publishContentCount', 0)
        with step('查看发布B详情'):
            param = get_deploy_info(tasks_uuid_b)[0]
            res_b = self.call(ItemGraphql, param)
            # 发布详情中包含0关联项
            res_b.check_response('data.task.publishContentCount', 1)

    @story('T143648 发布确认：查看未完成的发布内容')
    @parametrize('param', proj_url())
    def test_check_unfinished_task(self, param, add_deploy_connect_task):
        with step('前置条件'):
            # 创建发布A，并关联需求B
            ise_uuid, tasks_uuid = add_deploy_connect_task
        with step('点击「x 个未完成的发布内容」关联发布包含发布A'):
            param.uri_args({'tasks_uuid': tasks_uuid})
            resp = self.call(DeployInfo, param)
            resp.check_response('publish_content[0].uuid', ise_uuid)
            # 已完成项 0
            resp.check_response('publish_content_done_count', 0)
            # 总的关联工作项
            resp.check_response('publish_content_count', 1)

    @story('T143627 关联发布：在「关联发布」搜索框搜索发布')
    def test_select_deploy_relation_list(self):
        view, objects, isu_type_uuid = PrjAction.get_project_isu_list()
        tasks_uuid_b = PrjAction.add_deploy_task()
        # todo:查询不到上面创建的数据
        # with step('查询存在的发布任务名称'):
        #     resp_in = PrjAction.get_deploy_relation_list('发布', isu_type_uuid)
        #     uuid_list = []
        #     for u in resp_in.json()['data']['buckets'][0]['tasks']:
        #         uuid_list.append(u['uuid'])
        #     assert tasks_uuid_b in uuid_list
        with step('查询不存在的发布任务名称'):
            # 输入不存在的发布任务名称
            resp_not = PrjAction.get_deploy_relation_list('abcdefg', isu_type_uuid)
            resp_not.check_response('data.buckets[0].pageInfo.count', 0)

    @story('T143639 发布确认：将未完成的发布内容移动至当前项目下其他发布')
    def test_move_unfinished_task(self, add_deploy_connect_task):
        with step('前置条件'):
            ise_uuid, tasks_uuid_a = add_deploy_connect_task
            tasks_uuid_b = PrjAction.add_deploy_task()
        with step('将发布A下的需求移动到发布B，并将发布A的状态置为发布'):
            # 获取发布A的发布状态 transition_uuid
            transition_uuid = PrjAction.get_task_transitions(tasks_uuid_a).json()['transitions'][0]['uuid']
            pam = update_deploy_status(transition_uuid, tasks_uuid_a, [ise_uuid], [tasks_uuid_b])[0]
            r = self.call(DeployUpdateStatusPublish, pam)
            r.check_response("async_token", "")
            with step('查看发布A详情'):
                param = get_deploy_info(tasks_uuid_a)[0]
                res_B = self.call(ItemGraphql, param)
                # 发布详情中包含0关联项
                res_B.check_response('data.task.publishContentCount', 0)
            with step('查看发布B详情'):
                param = get_deploy_info(tasks_uuid_b)[0]
                res_B = self.call(ItemGraphql, param)
                # 发布详情中包含1关联项
                res_B.check_response('data.task.publishContentCount', 1)

    @story('143629 发布确认：将未完成的发布内容移动至其他项目下发布')
    def test_move_task_to_other_proj(self):
        with step('前置条件'):
            creator = Extra(ApiMeta)
            p_uuid_one = creator.new_project(f'deploy_project')
            ise = TaskAction.new_issue(issue_type_name='需求', is_batch=False, proj_uuid=p_uuid_one)[0]
        with step('将one项目的需求关联到B项目的发布下'):
            tasks_uuid_b = PrjAction.add_deploy_task()
            pam = update_deploy_relation_field(ise, [tasks_uuid_b])[0]
            resp = self.call(TaskUpdate3, pam)
            creator.del_project(p_uuid_one)

    @mark.skipif(ApiMeta.env.label == 'private', reason='私有部署环境跳过')
    @story('143650 发布进度：检查发布的发布进度属性')
    @parametrize('param', proj_url())
    def test_check_deploy_schedule(self, add_deploy_connect_task, param):
        with step('前置条件 创建发布A，并关联两个工作项'):
            ise1 = TaskAction.new_issue(issue_type_name='需求', is_batch=False)[0]
            ise_uuid, tasks_uuid = add_deploy_connect_task
            pam = batch_set_publish_version("add", [ise1])[0]
            pam.uri_args({'tasks_uuid': tasks_uuid})
            # 发布和需求进行关联操作
            t = self.call(DeploySetTask, pam)
        with step('将其中一个工作项状态置为关闭'):
            resp = PrjAction.get_task_transitions(ise_uuid)
            transitions_uuid = [r['uuid'] for r in resp.value('transitions') if r['name'] == '关闭'][0]
            pam1 = update_transit_status(transitions_uuid)[0]
            pam1.uri_args({'tasks_uuid': ise_uuid})
            response = self.call(UpdateTransitStatus, pam1)
        with step('查看发布A详情，检查发布进度属性 进度50%'):
            param.uri_args({'tasks_uuid': tasks_uuid})
            resp = self.call(DeployInfo, param)

            # 已完成项 1
            publish_content_done_count = resp.json()['publish_content_done_count']
            # 总的关联工作项 2
            publish_content_count = resp.json()['publish_content_count']
            assert publish_content_done_count / publish_content_count == 0.5

    @story('T143636 发布日期：发布的发布日期早于当前日期，且发布的状态为未完成态，发布日期显示为红色')
    def test_pass_deploy_time(self):
        with step('创建一个发布时间早于当前时间'):
            view, objects, isu_type_uuid = PrjAction.get_project_isu_list()
            param = proj.add_deploy_tasks(isu_type_uuid, value=mocks.day_timestamp(-1))[0]
            t = TaskAdd()
            # 调用接口
            t.call(param.json, **param.extra)
            # 检查接口响应码
            t.check_response('tasks[0].status', 1)
