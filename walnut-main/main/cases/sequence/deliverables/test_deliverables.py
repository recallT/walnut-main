"""
@File    ：deliverables
@Author  ：zhangyonghui
@Email   ：zhangyonghui@ones.ai
@Date    ：2022/06/06
@Desc    ：交付物组件
"""
from falcons.check import Checker
from falcons.com.nick import story, fixture, step, feature
from falcons.helper import mocks

from main.actions.pro import PrjAction
from main.actions.relation import RelationAction as Ra
from main.api.case import AttachmentDownload
from main.api.project import ItemGraphql
from main.api.task import ResAttUpload, UpBox
from main.params.plan import submit_deliverables, upload_deliverable_file, deliverable_list
from main.params.proj import proj_url


@fixture(scope='module', autouse=True)
def add_plan_component():
    # 1.先添加一个【里程碑】【交付物】 组件
    PrjAction.add_component('里程碑')
    PrjAction.add_component('交付物')
    yield
    PrjAction.remove_prj_component('里程碑')
    PrjAction.remove_prj_component('交付物')


@fixture(scope='module', autouse=True)
def add_proj_milestone():
    """新增项目计划-里程碑"""
    milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
    return milestone_key


@feature('交付物组件')
class TestProjDeliverables(Checker):

    @story('T143535 交付物：交付物列表展示')
    def test_deliverables_list(self, add_proj_milestone):
        milestone_uuid = Ra.get_proj_plan_info(add_proj_milestone).value(
            'data.activity.milestone.uuid')
        deliverables_key = Ra.add_deliverables(milestone_uuid, 'link').value('data.addDeliverable.key')
        with step('交付物列表信息'):
            param = deliverable_list()[0]
            resp = self.call(ItemGraphql, param)
            resp.check_response('data.deliverables[0].key', deliverables_key)

    @story('T143525 交付物：删除交付目标')
    def test_del_deliverables(self):
        milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
        milestone_uuid = Ra.get_proj_plan_info(milestone_key).value(
            'data.activity.milestone.uuid')
        # 新增文件交付物
        deliverable_key = Ra.add_deliverables(milestone_uuid, 'file').value('data.addDeliverable.key')
        response = Ra.get_plan_log_data(milestone_uuid)
        response.check_response('data.commonMessages[0].action', 'add')
        with step('删除交付目标'):
            Ra.del_deliverables(deliverable_key)

    @story('T143533 提交交付物：编辑链接')
    def test_update_deliverables_link(self):
        milestone_key = Ra.add_plans_or_milestones(p_type='milestone')
        milestone_uuid = Ra.get_proj_plan_info(milestone_key).value(
            'data.activity.milestone.uuid')
        with step('新建[链接]交付物'):
            # 新增链接交付物
            deliverables_key = Ra.add_deliverables(milestone_uuid, 'link').value('data.addDeliverable.key')
        with step('提交link 交付物'):
            param = submit_deliverables(key=deliverables_key, content="https://ones.ai")[0]
            resp = self.call(ItemGraphql, param)
            resp.check_response('data.updateDeliverable.key', deliverables_key)
        with step('更新link 交付物'):
            param = submit_deliverables(key=deliverables_key, content="https://test.ai")[0]
            resp = self.call(ItemGraphql, param)
            resp.check_response('data.updateDeliverable.key', deliverables_key)

    @story('T143532 提交交付物：链接')
    @story('T22772 提交交付物：链接')
    def test_submit_deliverables_link(self):
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

    @story('T143531 T143534 提交交付物：文件/交付物-文件下载与删除')
    def test_submit_deliverables_file(self):
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
            file_uuid = res.value('resource_uuid')

        with step('点击确定-上传文件'):
            """"""
            box = UpBox()
            box.call({'token': token, 'img_name': "test_img_" + mocks.ones_uuid()}, url)
            box.is_response_code(200)
        with step('提交文件 交付物'):
            param = submit_deliverables(key=deliverable_key, content=file_uuid)[0]
            resp = self.call(ItemGraphql, param)
            print('xx')

        with step('下载文件'):
            param = proj_url()[0]
            param.uri_args({'file_uuid': file_uuid})
            resp = self.call(AttachmentDownload, param)
            resp.check_response('uuid', file_uuid)
        with step('删除文件'):
            param = submit_deliverables(key=deliverable_key, content='')[0]
            self.call(ItemGraphql, param).check_response('data.updateDeliverable.key', deliverable_key)

    @story('T143526 添加里程碑交付物目标：链接类型')
    def test_add_deliverables_link(self, add_proj_milestone):
        milestone_key = add_proj_milestone
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

    @story('T143524 添加里程碑交付物目标：文件类型')
    def test_add_deliverables_file(self):
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
