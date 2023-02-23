"""
@File    ：test_milestone
@Author  ：zhangyonghui
@Email   ：zhangyonghui@ones.ai
@Date    ：2022/5/31
@Desc    ：里程碑
"""
from falcons.check import Checker, go
from falcons.com.nick import feature, fixture, story, step, parametrize
from falcons.helper import mocks

from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra
from main.api.project import ItemGraphql, UsesSearch
from main.api.task import ResAttUpload, UpBox
from main.api.wiki import WikiSpaces, WikiPages
from main.params import relation as rel, proj
from main.params.plan import submit_deliverables, submit_deliverables_type, upload_deliverable_file
from main.params.proj import proj_url
from main.params.relation import update_proj_plan_info


@fixture(scope='module', autouse=True)
def add_plan_component():
    # 1.先添加一个【里程碑】 组件
    PrjAction.add_component('里程碑')
    yield
    PrjAction.remove_prj_component('里程碑')


@fixture(scope='module', autouse=True)
def add_proj_milestone():
    """新增项目计划-里程碑"""
    milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
    return milestone_key


@feature('项目-里程碑')
class TestProjMilestone(Checker):

    @story('143542 项目计划组件-新建里程碑')
    @story('T143543 里程碑组件-新建里程碑')
    def test_add_new_milestone(self):
        Ra.add_plans_or_milestones(p_type='milestone')

    @story('T147938 里程碑-里程碑列表：编辑里程碑名称')
    def test_update_milestone_name(self, add_proj_milestone):
        with step('编辑里程碑名称'):
            Ra.fast_update_proj_plan_info("name", '示例里程碑A' + mocks.num(), add_proj_milestone)

    @story('T147939 里程碑-里程碑列表：里程碑跳转详情')
    def test_milestone_info(self, add_proj_milestone):
        info_resp = Ra.get_proj_plan_info(add_proj_milestone)
        info_resp.check_response('data.activity.key', add_proj_milestone)
        info_resp.check_response('data.activity.type', 'milestone')

    @story('T147941 里程碑-里程碑列表：里程碑状态切换')
    def test_update_milestone_status(self, add_proj_milestone):
        Ra.fast_update_proj_plan_info("progress", 10000000, add_proj_milestone)

    @story('T147940 里程碑-里程碑列表：删除里程碑')
    def test_del_milestone(self):
        with step('前置条件 创建一个里程碑'):
            milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
        with step('点击删除按钮'):
            resp = Ra.del_plans_or_milestones(milestone_key)
            assert resp == milestone_key

    @story('T148169 T148005 里程碑-创建快照：创建快照，同时设为基线')
    def test_add_milestone_snapshot(self):
        with step('创建快照'):
            p_key = Ra.add_activity_release()
            key = p_key.value('data.addActivityRelease.key')
        with step('查看历史快照'):
            param = rel.gantt_history(key)[0]
            q = self.call(ItemGraphql, param)
            data = q.value('data.activityRelease.key')
            assert data == key

    @story('T147963 里程碑-创建快照：创建快照，不设为基线')
    def test_add_milestone_snapshot_base(self):
        with step('创建快照 不设置为基线'):
            resp = Ra.add_activity_release(is_base=False)
            resp.check_response('data.addActivityRelease.key', 'activity_release-', check_type='contains')

    @story('T143559 里程碑-查看计划历史快照：快照重命名')
    def test_update_milestone_snapshot_name(self):
        with step('创建快照'):
            p_key = Ra.add_activity_release()
            key = p_key.value('data.addActivityRelease.key')
        with step('更新快照名称'):
            param = rel.update_snapshot_info(key, field_name="name", field_value="new_snapshot_name")[0]
            q = self.call(ItemGraphql, param)
            q.check_response('data.updateActivityRelease.key', key)

    @story('T143558 里程碑-查看计划历史快照：取消设为基线')
    def test_update_milestone_snapshot_is_base(self):
        with step('创建快照'):
            p_key = Ra.add_activity_release()
            key = p_key.value('data.addActivityRelease.key')
        with step('取消设为基线'):
            param = rel.update_snapshot_info(key, field_name="is_base", field_value=False)[0]
            q = self.call(ItemGraphql, param)
            q.check_response('data.updateActivityRelease.key', key)

    @story('T148346 里程碑-查看计划历史快照：设为基线')
    def test_update_milestone_snapshot_set_base(self):
        with step('创建快照'):
            p_key = Ra.add_activity_release(is_base=False)
            key = p_key.value('data.addActivityRelease.key')
        with step('更新快照名称'):
            param = rel.update_snapshot_info(key, field_name="is_base", field_value=True)[0]
            q = self.call(ItemGraphql, param)
            q.check_response('data.updateActivityRelease.key', key)

    @story('T148007里程碑-查看计划历史快照：基线对比设置')
    def test_set_milestone_snapshot(self):
        with step('前置条件1、存在快照001，快照002 2、快照002设为基线'):
            Ra.add_activity_release(is_base=True)
            p_key_b = Ra.add_activity_release(is_base=False)
            key_b = p_key_b.value('data.addActivityRelease.key')
        with step('将快照B设置为基线'):
            param = rel.update_snapshot_info(key_b, field_name="is_base", field_value=True)[0]
            q = self.call(ItemGraphql, param)
            q.check_response('data.updateActivityRelease.key', key_b)

    @story('T130919 里程碑-动态：里程碑评论')
    def test_milestone_message_action(self, add_proj_milestone):
        milestone_uuid = Ra.get_proj_plan_info(add_proj_milestone).value(
            'data.activity.milestone.uuid')
        with step('计划组详情中，点击评论，发布计划组评论'):
            key = Ra.add_message(milestone_uuid, 'milestone')
        with step('点击评论下方的编辑按钮'):
            Ra.update_message(key)
        with step('点击评论下方的回复按钮，输入回复信息'):
            key_uuid = key.split('-')[1]
            Ra.reply_message(milestone_uuid, 'milestone', key_uuid)
        with step('点击评论下方的删除按钮'):
            Ra.del_message(key)

    @story('T130921 里程碑-动态：设置交付物')
    def test_milestone_deliverable_log(self):
        milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
        milestone_uuid = Ra.get_proj_plan_info(milestone_key).value(
            'data.activity.milestone.uuid')
        with step('新建文件交付物，查看里程碑动态中显示'):
            # 新增文件交付物
            deliverable_key = Ra.add_deliverables(milestone_uuid, 'file').value('data.addDeliverable.key')
            response = Ra.get_plan_log_data(milestone_uuid)
            response.check_response('data.commonMessages[0].action', 'add')
        with step('删除文件交付物，查看里程碑动态中显示'):
            Ra.del_deliverables(deliverable_key)
            response = Ra.get_plan_log_data(milestone_uuid)
            # 两条动态，add，del
            assert len(response.value('data.commonMessages')) == 2

    @story('T135339 设置目标交付物：链接类型')
    def test_add_milestone_deliverable_link(self):
        milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
        milestone_uuid = Ra.get_proj_plan_info(milestone_key).value(
            'data.activity.milestone.uuid')
        with step('新建[链接]交付物，查看里程碑动态中显示'):
            # 新增文件交付物
            Ra.add_deliverables(milestone_uuid, 'link')
            response = Ra.get_plan_log_data(milestone_uuid)
            response.check_response('data.commonMessages[0].action', 'add')
            response.check_response('data.commonMessages[0].objectId', milestone_uuid)
            response.check_response('data.commonMessages[0].objectType', 'milestone')
            response.check_response('data.commonMessages[0].tag', 'deliverable')

    @story('T135339 T135342设置目标交付物：wiki_page类型')
    def test_add_milestone_deliverable_wiki_page(self):
        milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
        milestone_uuid = Ra.get_proj_plan_info(milestone_key).value(
            'data.activity.milestone.uuid')
        with step('新建[WIKI]交付物，查看里程碑动态中显示'):
            # 新增文件交付物
            Ra.add_deliverables(milestone_uuid, 'wiki_page')
            response = Ra.get_plan_log_data(milestone_uuid)
            response.check_response('data.commonMessages[0].action', 'add')
            response.check_response('data.commonMessages[0].objectId', milestone_uuid)
            response.check_response('data.commonMessages[0].objectType', 'milestone')
            response.check_response('data.commonMessages[0].tag', 'deliverable')

    @story('T135341 设置目标交付物：文件类型')
    def test_add_milestone_deliverable_file(self):
        milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
        milestone_uuid = Ra.get_proj_plan_info(milestone_key).value(
            'data.activity.milestone.uuid')
        with step('新建[文件]交付物，查看里程碑动态中显示'):
            # 新增文件交付物
            Ra.add_deliverables(milestone_uuid, 'file')
            response = Ra.get_plan_log_data(milestone_uuid)
            response.check_response('data.commonMessages[0].action', 'add')
            response.check_response('data.commonMessages[0].objectId', milestone_uuid)
            response.check_response('data.commonMessages[0].objectType', 'milestone')
            response.check_response('data.commonMessages[0].tag', 'deliverable')

    @story('T130922 里程碑-动态：提交交付物（链接）')
    def test_submit_milestone_deliverable_link(self):
        milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
        milestone_uuid = Ra.get_proj_plan_info(milestone_key).value(
            'data.activity.milestone.uuid')
        with step('新建[链接]交付物'):
            # 新增文件交付物
            deliverables_key = Ra.add_deliverables(milestone_uuid, 'link').value('data.addDeliverable.key')
        with step('提交link 交付物'):
            param = submit_deliverables(key=deliverables_key, content="https://ones.ai")[0]
            resp = self.call(ItemGraphql, param)
            resp.check_response('data.updateDeliverable.key', deliverables_key)
        with step('查看动态信息'):
            response = Ra.get_plan_log_data(milestone_uuid)
            assert len(response.value('data.commonMessages')) == 2

    @story('T130924 里程碑-动态：提交交付物（wiki）')
    @parametrize('param', proj_url())
    def test_submit_milestone_deliverable_wiki(self, param):
        milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
        milestone_uuid = Ra.get_proj_plan_info(milestone_key).value(
            'data.activity.milestone.uuid')
        with step('新建[链接]交付物'):
            # 新增文件交付物
            deliverables_key = Ra.add_deliverables(milestone_uuid, 'wiki_page').value(
                'data.addDeliverable.key')
        with step('提交wiki_page 交付物'):
            # 获取系统存在的示例wiki页面信息
            resp_spaces = self.call(WikiSpaces, param).value('spaces[0].uuid')
            param.uri_args({'space_uuid': resp_spaces})
            resp = self.call(WikiPages, param)
            # 组装提交交付物参数
            content = "{\"page_title\":\"%s\",\"page_uuid\":\"%s\"}" % (
                resp.value('pages[0].title'), resp.value('pages[0].uuid'))
            param1 = submit_deliverables(deliverables_key, content)[0]
            resp = self.call(ItemGraphql, param1)
            resp.check_response('data.updateDeliverable.key', deliverables_key)
        with step('查看动态信息'):
            response = Ra.get_plan_log_data(milestone_uuid)
            assert len(response.value('data.commonMessages')) == 2

    @story('T130917 里程碑-动态：编辑交付物类型')
    def test_update_deliverables_type(self, add_proj_milestone):
        with step('前置条件，给里程碑新增交付物'):
            milestone_uuid = Ra.get_proj_plan_info(add_proj_milestone).value(
                'data.activity.milestone.uuid')
            # 新增link交付物
            deliverables_key = Ra.add_deliverables(milestone_uuid, 'link').value(
                'data.addDeliverable.key')
        with step('修改交付物类型为文件类型'):
            param = submit_deliverables_type(deliverables_key, 'file')[0]
            resp = self.call(ItemGraphql, param)
            resp.check_response('data.updateDeliverable.key', deliverables_key)

    @story('T148533 里程碑-动态：更新交付物（链接）')
    def test_update_deliverables_link_content(self):
        milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
        milestone_uuid = Ra.get_proj_plan_info(milestone_key).value(
            'data.activity.milestone.uuid')
        with step('新建[链接]交付物'):
            # 新增文件交付物
            deliverables_key = Ra.add_deliverables(milestone_uuid, 'link').value('data.addDeliverable.key')
        with step('提交link 交付物'):
            param = submit_deliverables(key=deliverables_key, content="https://ones.ai")[0]
            resp = self.call(ItemGraphql, param)
            resp.check_response('data.updateDeliverable.key', deliverables_key)
        with step('更新link 交付物'):
            param = submit_deliverables(key=deliverables_key, content="https://test.ai")[0]
            resp = self.call(ItemGraphql, param)
            resp.check_response('data.updateDeliverable.key', deliverables_key)
        with step('查看动态'):
            response = Ra.get_plan_log_data(milestone_uuid)
            assert len(response.value('data.commonMessages')) == 3

    @story('T130923 里程碑-动态：提交交付物（文件）')
    def test_submit_milestone_deliverable_file(self):
        milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
        milestone_uuid = Ra.get_proj_plan_info(milestone_key).value(
            'data.activity.milestone.uuid')
        # 新增文件交付物
        deliverable_key = Ra.add_deliverables(milestone_uuid, 'file').value('data.addDeliverable.key')
        deliverable_uuid = deliverable_key.split('-')[1]
        with step('提交文件交付物，查看里程碑动态中显示'):
            param = upload_deliverable_file(deliverable_uuid)[0]
            res = self.call(ResAttUpload, param)

            token = res.value('token')
            url = res.value('upload_url')
            res.value('resource_uuid')

        with step('点击确定-上传文件'):
            """"""
            box = UpBox()
            box.call({'token': token, 'img_name': "test_img_" + mocks.ones_uuid()}, url)
            box.is_response_code(200)

    @story('T130925 里程碑详情-动态：状态变更')
    def test_update_milestone_status_log(self):
        milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
        milestone_uuid = Ra.get_proj_plan_info(milestone_key).value(
            'data.activity.milestone.uuid')
        with step('变更里程碑状态 查看动态'):
            Ra.fast_update_proj_plan_info("progress", 10000000, milestone_key)
            response = Ra.get_plan_log_data(milestone_uuid)
            response.check_response('data.commonMessages[0].action', 'update')
            response.check_response('data.commonMessages[0].ext',
                                    '{\"fields\":[{\"field_name\":\"progress\",\"name\":\"里程碑状态\",'
                                    '\"old_value\":0,\"new_value\":10000000}]}')

    @story('T148491 里程碑-里程碑详情页：修改里程碑名称')
    def test_update_milestone_name_inner(self, add_proj_milestone):
        with step('修改名称，名称字段为空--修改失败'):
            param = update_proj_plan_info("name", '', add_proj_milestone)[0]
            go(ItemGraphql, param, status_code=400)
        with step('正常修改里程碑名称'):
            Ra.fast_update_proj_plan_info("name", '里程碑A@#@' + mocks.num(), add_proj_milestone)

    @story('T148495 里程碑-里程碑详情页：修改里程碑状态')
    def test_update_milestone_status_inner(self, add_proj_milestone):
        with step('修改里程碑状态为已完成'):
            Ra.fast_update_proj_plan_info("progress", 10000000, add_proj_milestone)
        with step('修改里程碑状态为未完成'):
            Ra.fast_update_proj_plan_info("progress", 0, add_proj_milestone)

    @story('T148342 里程碑详情页-详情：修改描述')
    def test_update_milestone_describe(self, add_proj_milestone):
        Ra.fast_update_proj_plan_info("description", '<p>test test test</p>' + mocks.num(), add_proj_milestone,
                                      )

    @story('T148494 里程碑-里程碑详情页：修改里程碑完成日期')
    def test_update_milestone_end_time(self, add_proj_milestone):
        with step('修改「里程碑A」的完成日期'):
            Ra.fast_update_proj_milestone_info(add_proj_milestone, mocks.day_timestamp(1))

    @story('T148492 里程碑-里程碑详情页：修改里程碑负责人')
    def test_update_milestone_owner(self, add_proj_milestone):
        milestone_key = add_proj_milestone
        with step('点击负责人，修改「里程碑A」的负责人为成员A'):
            # 查询环境的member用户uuid
            su_param = proj.program_search_user()[0]
            resp_user_uuid = go(UsesSearch, su_param).value('users[0].uuid')
            Ra.fast_update_proj_plan_info("assign", resp_user_uuid, milestone_key)
            # 查看里程碑详情，断言负责人字段
            resp = Ra.get_proj_plan_info(milestone_key)
            resp.check_response('data.activity.assign.uuid', resp_user_uuid)
