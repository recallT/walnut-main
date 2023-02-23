from falcons.check import Checker, go
from falcons.com.nick import fixture, feature, story, parametrize, step
from falcons.platform.delivers.deliver_plugin_lifecycle import *
from falcons.platform.env_init import get_plugin_info

from main.api import plugin as api, plugin
from main.params import plug as p

"""以下是紫金工单门户"""


#
@fixture(scope='module', autouse=True)
def do_plugin():
    do_deliver_install("work_order_portal.opk")
    do_deliver_enable("work_order_portal.opk")
    print("插件安装启用成功！")


#     yield
#     do_deliver_disable("work_order_portal.opk")
#     do_deliver_uninstall("work_order_portal.opk")
#     print("插件卸载成功！")


"""检查表单是否启用"""


@fixture(scope='module')
def config_data():
    param = p.get_component_list()[0]
    config = go(plugin.OrgStampsData, param)
    return config


#
#
# """检查工单是否在导航条里"""
#
#
# @fixture(scope='module')
# def component_data():
#     data = {
#         "component": 0
#     }
#     return team_stamp(data)

# @classmethod
# def project_stamp_data(cls, token=None):
#     """"""
#     p = proj.proj_stamp()[0]
#     res = go(api.ProjectStamp, p, token)
#     return res.json()


"""添加工单组件"""


# @fixture(scope='module')
# def add_prj_desk_component(token):
#     component_stamp = go(api.ProjectStamp, p.proj_stamp()[0], token)
#     j = component_stamp.json()
#
#     exist_components = [{'uuid': c['uuid'], 'template_uuid': c['template_uuid']}
#                         for c in j['component']['components']]
#
#     com00016_ = [e for e in exist_components if e['template_uuid'] == 'com00016']
#     if not com00016_:
#         params = p.add_prj_desk_component()[0]
#         params.json['components'] += exist_components  # 添加上原有组件
#         return go(api.ComponentsAdd, params, token)


@feature('工单门户')
class TestAddForm(Checker):

    @story('工作项工单组件-表单管理-新建表单')
    @parametrize('param', p.update_form())
    def test_add_form(self, param):
        with step("新建表单"):
            header = {'Content-Type': 'application/json;charset=UTF-8'}
            header.update()
            # print(header)
            resp_forms = Checker.call(api.UpdateForm, param, header)
            print(resp_forms.value("components[0].settings.forms[0].uuid"))
            # （实际值，期望值）
            resp_forms.check_response("components[0].settings.forms[0].uuid",
                                      param.json_value('components[0].settings.forms[0].uuid'))

    @story('插件-门户配置-查询所有项目')
    @parametrize('param', p.graghql_project())
    def test_graghql_project(self, param):
        info = get_plugin_info("work_order_portal.opk")
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': info[0]['instance_id'],
                  }
        header.update()
        with step("查询所有项目"):
            resp_projs = Checker.call(api.AllProjects, param, header)
            print(resp_projs)
            proj_uuid = resp_projs.value("data.projectPeeps[0].uuid")
            print(proj_uuid)

    @story('关联表单')
    @parametrize('param', p.plug_update_forms())
    def test_update_forms(self, param):
        info = get_plugin_info("work_order_portal.opk")
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': info[0]['instance_id'],
                  }
        header.update()
        with step("关联表单"):
            update_forms = Checker.call(api.PlugUpdateForms, param, header)
            print(update_forms)

    @story('插件-门户配置-查询关联项目')
    @parametrize('param', p.plug_query_proj())
    def test_query_proj(self, param):
        info = get_plugin_info("work_order_portal.opk")
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': info[0]['instance_id'],
                  }
        header.update()
        with step("查询关联项目"):
            """type：0：获取全部类别的关联项目、1：业务系统问题支持、2：数据采集与统计、3：个人桌面支持"""
            resp_forms_pros = Checker.call(api.PlugQueryProj, param, header)
            print(resp_forms_pros)
            # data = resp_forms_pros.value("data")
            # print(data)

    @story('更新公告')
    @parametrize('param', p.update_announcement())
    def test_update_announcement(self, param):
        info = get_plugin_info("work_order_portal.opk")
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': info[0]['instance_id'],
                  }
        header.update()
        with step("更新公告内容"):
            Checker.call(api.QueryAnnouncement, param)

    @story('插件-查询公告')
    @parametrize
    def test_query_announcement(self, param):
        info = get_plugin_info("work_order_portal.opk")
        header = {'Ones-Check-Id': info[0]['teamUUID'], 'Ones-Check-Point': 'team',
                  'Ones-Plugin-Id': info[0]['instance_id'],
                  }
        header.update()
        with step("查询公告内容"):
            announcement = Checker.call(api.QueryAnnouncement, header)
            ann = announcement.value("data.content")
            print(ann)
