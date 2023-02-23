"""
@Desc：项目设置-步骤-后置动作-更新属性（任务、子任务）
@Author  ：zhangweiyu@ones.ai
"""
import time
from falcons.check import Checker
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture, step, parametrize
from falcons.helper import mocks

from main.actions.prodcut import ProductAction
from main.actions.sprint import SprintAction
from main.actions.task import TaskAction
from main.actions.member import MemberAction
from main.helper.extra import Extra
from . import update_post_action, get_start_step, options, field_options, add_custom_field, delete_custom_field, \
    trigger_and_check, get_project_assign, trigger


@fixture(scope='module', autouse=True)
def add_project():
    # 创建一个单独项目
    time.sleep(2)
    creator = Extra(ApiMeta)
    project_uuid = creator.new_project(f'ApiTest-Task-SPA')
    return project_uuid


@fixture(scope='module', autouse=True)
def del_project(add_project):
    yield
    # 清除项目数据
    creator = Extra(ApiMeta)
    creator.del_project(add_project)


@fixture(scope='module')
def users():
    users = []
    count = 1
    for i in range(count):
        user = MemberAction.new_member()
        users.append(user)
    # time.sleep(2)
    yield users
    for u in users:
        MemberAction.del_member(u.uuid)


@feature('项目设置-步骤-后置动作-更新属性')
class TestPrjPostActionUpdateField(Checker):

    @story('T130242 任务-后置动作：添加更新属性后置动作（自定义单选菜单）')
    @story('T129472 任务-后置动作：检查更新属性后置动作事件（自定义单选菜单）')
    @story('T130253 子任务-后置动作：添加更新属性后置动作（自定义单选菜单）')
    @story('T129470 子任务-后置动作：检查更新属性后置动作事件（自定义单选菜单）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_custom_field1(self, add_project, typ):
        with step('前置操作: 已添加自定义属性'):
            field_uuid = add_custom_field(field_type=1, project_uuid=add_project, options=options, issue_type_name=typ)
        with step('添加更新属性后置动作（自定义单选菜单）'):
            # 获取一个选项
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_expect_value = field_options(field_uuid)[0]["uuid"]
            post_function = [{
                "update_field_value": {
                    "field_uuid": field_uuid,
                    "value": field_expect_value,
                    "type": 1,
                    "value_type": 0
                }
            }]
            add_res = update_post_action(start_step, post_function)
            add_res.check_response('transition.post_function', post_function)
        with step('检查更新属性后置动作事件（自定义单选菜单）'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid=field_uuid,
                              field_expect_value=field_expect_value)
        with step('后置操作'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除自定义属性（全局+项目）
            # delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T130227 任务-后置动作：添加更新属性后置动作（自定义单行文本）')
    @story('T129454 任务-后置动作：检查更新属性后置动作事件（自定义单行文本）')
    @story('T130229 子任务-后置动作：添加更新属性后置动作（自定义单行文本）')
    @story('T129458 子任务-后置动作：检查更新属性后置动作事件（自定义单行文本）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_custom_field2(self, add_project, typ):
        with step('前置操作: 任务-已添加自定义属性'):
            # 新建自定义属性：「自定义单行文本」
            field_uuid = add_custom_field(field_type=2, project_uuid=add_project, issue_type_name=typ)
        with step('添加更新属性后置动作（自定义单行文本）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_expect_value = 'post-action-test-自定义单行文本'
            post_function = [{
                "update_field_value": {
                    "field_uuid": field_uuid,
                    "value": field_expect_value,
                    "type": 2,
                    "value_type": 0
                }
            }]
            add_res = update_post_action(start_step,
                                         post_function)
            add_res.check_response('transition.post_function', post_function)
        with step('检查更新属性后置动作事件（自定义单行文本）'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid=field_uuid,
                              field_expect_value=field_expect_value)
        with step('后置操作'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除自定义属性（全局+项目）
            # delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T130491 任务-后置动作：添加更新属性后置动作（自定义整数）')
    @story('T129590 任务-后置动作：检查更新属性后置动作事件（自定义整数）')
    @story('T130503 子任务-后置动作：添加更新属性后置动作（自定义整数）')
    @story('T129588 子任务-后置动作：检查更新属性后置动作事件（自定义整数）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_custom_field3(self, add_project, typ):
        with step('前置操作: 任务-已添加自定义属性'):
            field_uuid = add_custom_field(field_type=3, project_uuid=add_project, issue_type_name=typ)
        with step('添加更新属性后置动作（自定义整数）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_expect_value = 12300000
            post_function = [{
                "update_field_value": {
                    "field_uuid": field_uuid,
                    "value": field_expect_value,
                    "type": 3,
                    "value_type": 0
                }
            }]
            add_res = update_post_action(start_step,
                                         post_function)
            add_res.check_response('transition.post_function', post_function)
        with step('检查更新属性后置动作事件（自定义整数）'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid=field_uuid,
                              field_expect_value=field_expect_value)
        with step('后置操作'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除自定义属性（全局+项目）
            # delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T130437 任务-后置动作：添加更新属性后置动作（自定义浮点数）')
    @story('T129557 任务-后置动作：检查更新属性后置动作事件（自定义浮点数）')
    @story('T130425 子任务-后置动作：添加更新属性后置动作（自定义浮点数）')
    @story('T129560 子任务-后置动作：检查更新属性后置动作事件（自定义浮点数）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_custom_field4(self, add_project, typ):
        with step('前置操作: 任务-已添加自定义属性'):
            field_uuid = add_custom_field(field_type=4, project_uuid=add_project, issue_type_name=typ)
        with step('添加更新属性后置动作（自定义浮点数）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_expect_value = 1234000
            post_function = [{
                "update_field_value": {
                    "field_uuid": field_uuid,
                    "value": field_expect_value,
                    "type": 4,
                    "value_type": 0
                }
            }]
            add_res = update_post_action(start_step,
                                         post_function)
            add_res.check_response('transition.post_function', post_function)

        with step('检查更新属性后置动作事件（自定义浮点数）'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid=field_uuid,
                              field_expect_value=field_expect_value)
        with step('后置操作'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除自定义属性（全局+项目）
            # delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T130443 任务-后置动作：添加更新属性后置动作（自定义日期）')
    @story('T129565 任务-后置动作：检查更新属性后置动作事件（自定义日期）')
    @story('T130449 子任务-后置动作：添加更新属性后置动作（自定义日期）')
    @story('T129562 子任务-后置动作：检查更新属性后置动作事件（自定义日期）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_custom_field5(self, add_project, typ):
        with step('前置操作: 任务-已添加自定义属性'):
            field_uuid = add_custom_field(field_type=5, project_uuid=add_project, issue_type_name=typ)
        with step('添加更新属性后置动作（自定义日期）'):
            start_step = get_start_step(project_uuid=add_project, issue_type_name=typ)
            field_expect_value = mocks.now_timestamp()
            post_function = [{
                "update_field_value": {
                    "field_uuid": field_uuid,
                    "value": field_expect_value,
                    "type": 5,
                    "value_type": 0
                }
            }]
            add_res = update_post_action(start_step,
                                         post_function)
            add_res.check_response('transition.post_function', post_function)
        with step('检查更新属性后置动作事件（自定义日期）'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid=field_uuid,
                              field_expect_value=field_expect_value)
        with step('后置处理'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除自定义属性（全局+项目）
            # delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T130467 任务-后置动作：添加更新属性后置动作（自定义时间）')
    @story('T129579 任务-后置动作：检查更新属性后置动作事件（自定义时间）')
    @story('T130466 子任务-后置动作：添加更新属性后置动作（自定义时间）')
    @story('T129573 子任务-后置动作：检查更新属性后置动作事件（自定义时间）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_custom_field6(self, add_project, typ):
        with step('前置操作: 任务-已添加自定义属性'):
            field_uuid = add_custom_field(field_type=6, project_uuid=add_project, issue_type_name=typ)
        with step('添加更新属性后置动作（自定义时间）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_expect_value = mocks.now_timestamp()
            post_function = [{
                "update_field_value": {
                    "field_uuid": field_uuid,
                    "value": field_expect_value,
                    "type": 6,
                    "value_type": 0
                }
            }]
            add_res = update_post_action(start_step,
                                         post_function)
            add_res.check_response('transition.post_function', post_function)
        with step('检查更新属性后置动作事件（自定义时间）'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid=field_uuid,
                              field_expect_value=field_expect_value)
        with step('后置操作：清除数据'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除自定义属性（全局+项目）
            # delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T130315 任务-后置动作：添加更新属性后置动作（自定义单选迭代）')
    @story('T129498 任务-后置动作：检查更新属性后置动作事件（自定义单选迭代）')
    @story('T130322 子任务-后置动作：添加更新属性后置动作（自定义单选迭代）')
    @story('T129501 子任务-后置动作：检查更新属性后置动作事件（自定义单选迭代）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_custom_field7(self, add_project, typ):
        with step('前置操作: 任务-已添加自定义属性'):
            field_uuid = add_custom_field(field_type=7, project_uuid=add_project, issue_type_name=typ)
        with step('添加更新属性后置动作（自定义单选迭代）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            sprint_uuid = SprintAction.sprint_add(add_project)
            field_expect_value = sprint_uuid
            post_function = [{
                "update_field_value": {
                    "field_uuid": field_uuid,
                    "value": field_expect_value,
                    "type": 7,
                    "value_type": 0
                }
            }]
            add_res = update_post_action(start_step,
                                         post_function)
            add_res.check_response('transition.post_function', post_function)
        with step('检查更新属性后置动作事件（自定义单选迭代）'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid=field_uuid,
                              field_expect_value=field_expect_value)
        with step('后置处理'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除自定义属性（全局+项目）
            # delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T130283 任务-后置动作：添加更新属性后置动作（自定义单选成员）')
    @story('T129478 任务-后置动作：检查更新属性后置动作事件（自定义单选成员）')
    @story('T130285 子任务-后置动作：添加更新属性后置动作（自定义单选成员）')
    @story('T129483 子任务-后置动作：检查更新属性后置动作事件（自定义单选成员）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_custom_field8(self, add_project, users, typ):
        with step('前置操作: 任务-已添加自定义属性'):
            field_uuid = add_custom_field(field_type=8, project_uuid=add_project, issue_type_name=typ)
        with step('添加更新属性后置动作（自定义单选成员）'):
            field_expect_value = users[0].uuid
            start_step = get_start_step(add_project, issue_type_name=typ)
            post_function = [{
                "update_field_value": {
                    "field_uuid": field_uuid,
                    "value": field_expect_value,
                    "type": 8,
                    "value_type": 0
                }
            }]
            add_res = update_post_action(start_step,
                                         post_function)
            add_res.check_response('transition.post_function', post_function)
        with step('检查更新属性后置动作事件（自定义单选成员）'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid=field_uuid,
                              field_expect_value=field_expect_value)
        with step('后置处理'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除自定义属性（全局+项目）
            # delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T130298 任务-后置动作：添加更新属性后置动作（自定义单选成员）（从其他单选成员属性拷贝）')
    @story('T129491 任务-后置动作：检查更新属性后置动作事件（自定义单选成员）（从其他单选成员属性拷贝）')
    @story('T130300 子任务-后置动作：添加更新属性后置动作（自定义单选成员）（从其他单选成员属性拷贝）')
    @story('T129484 子任务-后置动作：检查更新属性后置动作事件（自定义单选成员）（从其他单选成员属性拷贝）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_custom_field8_copy(self, add_project, typ):
        with step('前置操作: 任务-已添加自定义属性'):
            field_uuid = add_custom_field(field_type=8, project_uuid=add_project, issue_type_name=typ)
        with step('添加更新属性后置动作（自定义单选成员）（从其他单选成员属性拷贝）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_expect_value = get_project_assign(add_project)
            post_function = [{
                "update_field_value": {
                    "field_uuid": field_uuid,
                    "value": 'project_assign',
                    "type": 8,
                    "value_type": 0
                }
            }]
            add_res = update_post_action(start_step,
                                         post_function)
            add_res.check_response('transition.post_function', post_function)
        with step('检查更新属性后置动作事件（自定义单选成员）（从其他单选成员属性拷贝）'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid=field_uuid,
                              field_expect_value=field_expect_value)
        with step('后置处理'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除自定义属性（全局+项目）
            # delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T130394 任务-后置动作：添加更新属性后置动作（自定义多选成员）')
    @story('T129530 任务-后置动作：检查更新属性后置动作事件（自定义多选成员）')
    @story('T130392 子任务-后置动作：添加更新属性后置动作（自定义多选成员）')
    @story('T129536 子任务-后置动作：检查更新属性后置动作事件（自定义多选成员）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_custom_field13(self, add_project, users, typ):
        with step('前置操作: 任务-已添加自定义属性'):
            field_uuid = add_custom_field(field_type=13, project_uuid=add_project, issue_type_name=typ)
        with step('添加更新属性后置动作（自定义多选成员）'):
            members = MemberAction.get_member_list(project_uuid=add_project)
            proj_member = members.value('role_members[0].members[0]')
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_expect_value = [proj_member, users[0].uuid]
            post_action = [{
                "update_field_value": {
                    "field_uuid": field_uuid,
                    "value": field_expect_value,
                    "type": 13,
                    "value_type": 0
                }
            }]
            add_res = update_post_action(start_step,
                                         post_action)
            add_res.check_response('transition.post_function', post_action)
        with step('检查更新属性后置动作事件（自定义多选成员）'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid=field_uuid,
                              field_expect_value=field_expect_value)
        with step('后置处理'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除自定义属性（全局+项目）
            # delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T130344 任务-后置动作：添加更新属性后置动作（自定义多行文本）')
    @story('T129511 任务-后置动作：检查更新属性后置动作事件（自定义多行文本）')
    @story('T130335 子任务-后置动作：添加更新属性后置动作（自定义多行文本）')
    @story('T129515 子任务-后置动作：检查更新属性后置动作事件（自定义多行文本）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_custom_field15(self, add_project, typ):
        with step('前置操作: 任务-已添加自定义属性'):
            field_uuid = add_custom_field(field_type=15, project_uuid=add_project, issue_type_name=typ)
        with step('添加更新属性后置动作（自定义多行文本）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_expect_value = f'{mocks.random_text(10)}\n{mocks.random_text(20)}'
            post_action = [{
                "update_field_value": {
                    "field_uuid": field_uuid,
                    "value": field_expect_value,
                    "type": 15,
                    "value_type": 0
                }
            }]
            add_res = update_post_action(start_step,
                                         post_action)
            add_res.check_response('transition.post_function', post_action)
        with step('检查更新属性后置动作事件（自定义多行文本）'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid=field_uuid,
                              field_expect_value=field_expect_value)
        with step('后置处理'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除自定义属性（全局+项目）
            # delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T130359 任务-后置动作：添加更新属性后置动作（自定义多选菜单）')
    @story('T129526 任务-后置动作：检查更新属性后置动作事件（自定义多选菜单）')
    @story('T130372 子任务-后置动作：添加更新属性后置动作（自定义多选菜单）')
    @story('T129517 子任务-后置动作：检查更新属性后置动作事件（自定义多选菜单）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_custom_field16(self, add_project, typ):
        with step('前置操作: 任务-已添加自定义属性'):
            field_uuid = add_custom_field(field_type=16, project_uuid=add_project, issue_type_name=typ, options=options)
        with step('添加更新属性后置动作（自定义多选菜单）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            _options = field_options(field_uuid)
            field_expect_value = [p['uuid'] for p in _options]
            post_action = [{
                "update_field_value": {
                    "field_uuid": field_uuid,
                    "value": field_expect_value,
                    "type": 16,
                    "value_type": 0
                }
            }]
            add_res = update_post_action(start_step,
                                         post_action)
            add_res.check_response('transition.post_function', post_action)
        with step('检查更新属性后置动作事件（自定义多选菜单）'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid=field_uuid,
                              field_expect_value=field_expect_value)
        with step('后置处理'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除自定义属性（全局+项目）
            # delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T130411 任务-后置动作：添加更新属性后置动作（自定义多选项目）')
    @story('T129543 任务-后置动作：检查更新属性后置动作事件（自定义多选项目）')
    @story('T130401 子任务-后置动作：添加更新属性后置动作（自定义多选项目）')
    @story('T129545 子任务-后置动作：检查更新属性后置动作事件（自定义多选项目）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_custom_field50(self, add_project, typ):
        with step('前置操作: 任务-已添加自定义属性'):
            field_uuid = add_custom_field(field_type=50, project_uuid=add_project, issue_type_name=typ)
        with step('前置操作：添加项目A、B'):
            creator = Extra(ApiMeta)
            a_project_uuid = creator.new_project(f'A_project')
            b_project_uuid = creator.new_project(f'B_project')
        with step('添加更新属性后置动作（自定义多选项目）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_expect_value = [a_project_uuid, b_project_uuid]
            post_action = [{
                "update_field_value": {
                    "field_uuid": field_uuid,
                    "value": field_expect_value,
                    "type": 50,
                    "value_type": 0
                }
            }]
            add_res = update_post_action(start_step,
                                         post_action)
            add_res.check_response('transition.post_function', post_action)

        with step('检查更新属性后置动作事件（自定义多选项目）'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid=field_uuid,
                              field_expect_value=field_expect_value)
        with step('后置处理'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除自定义属性（全局+项目）
            # delete_custom_field(field_uuid=field_uuid, project_uuid=add_project, issue_type_name=typ)
            # 清除项目A、B
            creator.del_project(a_project_uuid)
            creator.del_project(b_project_uuid)

    @story('T129446 任务-后置动作：检查更新属性后置动作事件（所属产品）')
    @story('T130198 子任务-后置动作：添加更新属性后置动作（所属产品）')
    @story('T129444 子任务-后置动作：检查更新属性后置动作事件（所属产品）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_sys_field029(self, add_project, typ):
        with step('前置操作：添加产品A、B'):
            a_product = ProductAction.product_add().value('item')
            b_product = ProductAction.product_add().value('item')
        with step('前置操作：任务-工作流-已添加后置动作'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_expect_value = [a_product['uuid'], b_product['uuid']]
            post_action = [{
                "update_field_value": {
                    "field_uuid": 'field029',
                    "value": field_expect_value,
                    "type": 44,
                    "value_type": 0
                }
            }]
            update_post_action(start_step,
                               post_action)

        with step('任务-点击步骤-开始任务，检查属性值变化'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid='field029',
                              field_expect_value=field_expect_value)
        with step('后置处理'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除产品A、B
            ProductAction.product_del(a_product['key'])
            ProductAction.product_del(b_product['key'])

    @story('T130174 任务-后置动作：添加更新属性后置动作（故事点）')
    @story('T129420 任务-后置动作：检查更新属性后置动作事件（故事点）')
    @story('T130160 子任务-后置动作：添加更新属性后置动作（故事点）')
    @story('T129419 子任务-后置动作：检查更新属性后置动作事件（故事点）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_sys_field032(self, add_project, typ):
        with step('添加更新属性后置动作（故事点）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_expect_value = 500000
            post_action = [{
                "update_field_value": {
                    "field_uuid": 'field032',
                    "value": field_expect_value,
                    "type": 4,
                    "value_type": 0
                }
            }]
            add_res = update_post_action(start_step,
                                         post_action)
            add_res.check_response('transition.post_function', post_action)
        with step('检查更新属性后置动作事件（故事点）'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid='field032',
                              field_expect_value=field_expect_value)
        with step('后置处理'):
            # 清除后置处理
            update_post_action(start_step, [])

    @story('T130180 任务-后置动作：添加更新属性后置动作（进度）')
    @story('T129435 任务-后置动作：检查更新属性后置动作事件（进度）')
    @story('T130191 子任务-后置动作：添加更新属性后置动作（进度）')
    @story('T129434 子任务-后置动作：检查更新属性后置动作事件（进度）')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_sys_field033(self, add_project, users, typ):
        with step('添加更新属性后置动作（进度）'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            field_expect_value = 5000000
            post_action = [{
                "update_field_value": {
                    "field_uuid": 'field033',
                    "value": field_expect_value,
                    "type": 4,
                    "value_type": 0
                }
            }]
            add_res = update_post_action(start_step,
                                         post_action)
            add_res.check_response('transition.post_function', post_action)
        with step('检查更新属性后置动作事件（进度）'):
            trigger_and_check(start_step, issue_type_name=typ, field_uuid='field033',
                              field_expect_value=field_expect_value)
        with step('后置处理'):
            # 清除后置处理
            update_post_action(start_step, [])

    @story('T129406 任务-后置动作：检查更新属性后置动作设置不在成为负责人权限域内的单选成员拷贝至负责人属性')
    @story('T129399 子任务-后置动作：检查更新属性后置动作设置不在成为负责人权限域内的单选成员拷贝至负责人属性')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_sys_field004_copy_no_permission(self, add_project, users, typ):
        with step('前置操作: 任务-添加自定义属性：单选成员1'):
            user_field_uuid = add_custom_field(field_type=8, project_uuid=add_project, issue_type_name=typ)
        with step('前置操作：步骤"开始任务"已添加后置动作：将负责人更新为属性单选成员1的值'):
            post_action = [{
                "update_field_value": {
                    "field_uuid": 'field004',
                    "value": user_field_uuid,
                    "type": 8,
                    "value_type": 1
                }
            }]
            start_step = get_start_step(add_project, issue_type_name=typ)
            update_post_action(start_step, post_action)
        with step('前置操作：新建任务，并更新其属性"单选成员1"为负责人外的某成员'):
            # 新建任务
            user_uuid = users[0].uuid
            task_uuid = TaskAction.new_issue(proj_uuid=add_project)[0]
            if typ.startswith('子'):
                task_uuid = TaskAction.new_issue(proj_uuid=add_project, parent_uuid=task_uuid,
                                                 issue_type_name=typ)[0]
            TaskAction.update_task_info(task_uuid, info={
                "field_uuid": user_field_uuid,
                "type": 8,
                "value": user_uuid
            })
        with step('点击任务的步骤：开始任务，触发更新'):
            trigger(task_uuid=task_uuid, transit_uuid=start_step['uuid'])
            # 检查更新后的任务详情
            task_info = TaskAction.task_info(task_uuid)
            task_info.check_response('status_uuid', start_step['end_status_uuid'])
            # 检查属性值被更新
            updated_field = [f for f in task_info.json()['field_values'] if f['field_uuid'] == 'field004'][0]
            assert updated_field['value'] != user_uuid, '预期错误：应该不更新负责人'

        with step('后置处理'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除自定义属性（全局+项目）
            # delete_custom_field(field_uuid=user_field_uuid, project_uuid=add_project, issue_type_name=typ)

    @story('T129409 任务-后置动作：检查更新属性后置动作设置空的单选成员拷贝至必填属性')
    @story('T129414 子任务-后置动作：检查更新属性后置动作设置空的单选成员拷贝至必填属性')
    @parametrize('typ', ('任务', '子任务'))
    def test_post_action_update_sys_field004_copy_none(self, add_project, users, typ):
        with step('前置操作: 任务-添加自定义属性：单选成员1'):
            user_field_uuid = add_custom_field(field_type=8, project_uuid=add_project, issue_type_name=typ)
        with step('前置操作：步骤"开始任务"已添加后置动作：将负责人更新为属性单选成员1的值'):
            start_step = get_start_step(add_project, issue_type_name=typ)
            post_action = [{
                "update_field_value": {
                    "field_uuid": 'field004',
                    "value": user_field_uuid,
                    "type": 8,
                    "value_type": 1
                }
            }]
            update_post_action(start_step, post_action)
        with step('前置操作：新建任务'):
            # 新建任务：添加的单选成员默认为非必填且值为空
            task_uuid = TaskAction.new_issue(proj_uuid=add_project)[0]
            if typ.startswith('子'):
                task_uuid = TaskAction.new_issue(proj_uuid=add_project, parent_uuid=task_uuid,
                                                 issue_type_name=typ)[0]
        with step('点击任务的步骤：开始任务，触发更新'):
            trigger(task_uuid=task_uuid, transit_uuid=start_step['uuid'])
            # 检查更新后的任务详情
            task_info = TaskAction.task_info(task_uuid)
            task_info.check_response('status_uuid', start_step['end_status_uuid'])
            # 检查属性值被更新
            updated_field = [f for f in task_info.json()['field_values'] if f['field_uuid'] == 'field004'][0]
            assert updated_field['value'], '预期错误：后置动作不应该触发，负责人不为空'

        with step('后置处理'):
            # 清除后置处理
            update_post_action(start_step, [])
            # 清除自定义属性（全局+项目）
            # delete_custom_field(field_uuid=user_field_uuid, project_uuid=add_project, issue_type_name=typ)
