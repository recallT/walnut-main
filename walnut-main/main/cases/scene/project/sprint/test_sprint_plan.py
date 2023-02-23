from falcons.check import Checker, go
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, fixture, step
import time

from main.actions.member import MemberAction
from main.actions.sprint import SprintAction
from main.actions.pro import PrjAction, ProjPermissionAction
from main.helper.extra import Extra
from main.params.const import ACCOUNT
from main.params import proj
from main.api import project


@fixture(scope='module', autouse=True)
def add_project():
    # 创建一个单独项目
    time.sleep(2)
    project_uuid = PrjAction.new_project(index=3, name='Apitest-迭代计划')
    # 添加迭代组件
    PrjAction.add_component(component_name='迭代', project_uuid=project_uuid)
    PrjAction.add_component(component_name='迭代计划', project_uuid=project_uuid)
    return project_uuid


@fixture(scope='module', autouse=True)
def del_project(add_project):
    yield
    # 清除项目数据
    creator = Extra(ApiMeta)
    creator.del_project(add_project)


@feature('迭代管理-迭代计划组件')
class TestSprintPlan(Checker):

    @story('T119386 迭代计划组件-列表视图：根据「迭代负责人」进行分组')
    def test_sprint_plan_group_by_owner(self, add_project):
        with step('前置操作：创建3个迭代+负责人A/B'):
            user_a = ACCOUNT.user
            user_b = MemberAction.new_member()
            # 添加user_b权限：迭代权限-成为迭代负责人
            ProjPermissionAction.add_permission(user_domain_type='single_user', permission='be_assigned_to_sprint',
                                                user_domain_param=user_b.owner_uuid,
                                                project_uuid=add_project)
            s_a = SprintAction.sprint_add(project_uuid=add_project, assign=user_a.owner_uuid)
            s_b = SprintAction.sprint_add(project_uuid=add_project, assign=user_b.owner_uuid)
            s_c = SprintAction.sprint_add(project_uuid=add_project, assign=user_a.owner_uuid)
            SprintAction.update_sprint_status(s_b, status='进行中', project_uuid=add_project)
            SprintAction.update_sprint_status(s_c, status='已完成', project_uuid=add_project)

        with step('分组：迭代负责人'):
            param = proj.sprint_plan_list(project_uuid=add_project)[0]
            res = go(project.ItemGraphql, param)
            sprints = res.value('data.sprints')
            us_map = {}
            for s in sprints:
                if s['assign']['uuid'] not in us_map.keys():
                    us_map[s['assign']['uuid']] = set()
                    us_map[s['assign']['uuid']].add(s['uuid'])
                else:
                    us_map[s['assign']['uuid']].add(s['uuid'])
            assert us_map[user_a.owner_uuid] == set([s_a, s_c])
            assert us_map[user_b.owner_uuid] == set([s_b])
