"""
@File    ：test_topbar_search.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/7/18
@Desc    ：通用模块-顶栏搜索
"""
import time

from falcons.check import Checker, go
from falcons.com.nick import feature, story, parametrize, fixture
from falcons.com.ones import unify_login

from main.actions.member import MemberAction
from main.actions.pro import PrjAction
from main.actions.task import TaskAction
from main.api import current as crt
from main.api import project as p_api
from main.api import wiki as w_api
from main.params import team as p, current


@fixture(scope='module', autouse=True)
def prepared_():
    """准备测试文件"""
    print('Add normal user')
    user = MemberAction.new_member()
    # 创建测试任务用于传文件
    task = TaskAction.new_issue()
    file_uuid = []
    for _ in range(3):  # 上传 3 个附件（图片）用于测试
        f_id = TaskAction.upload_file(task[0])
        file_uuid.append(f_id)

    # 添加文件组件到项目中
    PrjAction.add_component('文件')

    m = {'task_uuid': task[0],
         'file_uuid': file_uuid,
         'user': user,
         'views': [],  # 用于存储用例例新建的测试视图
         }  # 将任务的UUID 拿出去

    time.sleep(1)

    yield m

    #  删除测试视图
    del_view = current.dashboard_opt()[0]
    for uuid in m['views']:
        del_view.uri_args({'view_uuid': uuid})
        go(crt.FilterViewDelete, del_view)

    # 删除文件组件
    # PrjAction.remove_prj_component('文件')
    # 删除成员
    MemberAction.del_member(m['user'].uuid)


@fixture(scope='module')
def normal_token(prepared_):
    """普通成员的token"""

    return unify_login(prepared_['user'])


@feature('通用模块')
class TestTopBarSearch(Checker):
    """"""

    @story('T136963 我的工作台顶栏搜索：搜索附件（有页面的查看权限）')
    @parametrize('param', p.top_bar_search())
    def test_overview_search(self, param):
        """概览搜索-文件"""
        #  wiki 页面附件
        param.json_update('types', 'resource')
        resp = self.call(w_api.WikiTeamSearch, param)

        # resp.check_response('total', 0, 'ge')

    @story('T136974 我的工作台顶栏搜索：搜索页面组（有页面组的查看权限）')
    @parametrize('param', p.top_bar_search())
    def test_overview_search_page_group(self, param):
        """概览搜索-页面组"""
        param.json |= {
            'q': '示例', 'types': 'space'
        }
        self.call(w_api.WikiTeamSearch, param)

    @story('T136976 我的工作台顶栏搜索：搜索页面（有页面的查看权限）')
    @parametrize('param', p.top_bar_search())
    def test_overview_search_page(self, param):
        """概览搜索-页面组"""
        param.json |= {
            'q': 'wiki', 'types': 'page', 'space_uuids': ''
        }
        self.call(w_api.WikiTeamSearch, param)


    @story('T136269 我的工作台-顶栏-新建：新建筛选器视图（私人）')
    @parametrize('param', current.filter_view_add())
    def test_add_filter_view_personal(self, param, prepared_):
        """"""

        resp = self.call(crt.FilterViewAdd, param)

        uuid = resp.value('view.uuid')

        resp.check_response('view.name', param.json_value('name'))

        view_get_param = current.filter_view_config_list()[0]
        list_resp = self.call(crt.FilterViewConfigGet, view_get_param)

        assert uuid in [r['view_uuid'] for r in list_resp.value('configs')]

        prepared_['views'].append(uuid)

    @story('T136266 我的工作台-顶栏-新建：新建筛选器视图（共享成员域为成员）')
    @parametrize('param', current.filter_view_add())
    def test_view_shared_to_member(self, param, prepared_):
        """"""
        param.json |= {'shared': True, 'shared_to': [
            {
                'user_domain_type': 'single_user',
                'user_domain_param': prepared_['user'].uuid,
            }
        ]}

        resp = self.call(crt.FilterViewAdd, param)

        uuid = resp.value('view.uuid')

        resp.check_response('view.name', param.json_value('name'))

        view_get_param = current.filter_view_config_list()[0]
        list_resp = self.call(crt.FilterViewConfigGet, view_get_param)

        assert uuid in [r['view_uuid'] for r in list_resp.value('configs')]

        prepared_['views'].append(uuid)

    @story('T136970 我的工作台顶栏搜索：搜索文件（有项目及工作项的查看权限）')
    @parametrize('param', p.top_bar_search())
    def test_overview_search_file(self, param):
        """概览搜索-文件"""

        # 项目的附件文件
        param.json |= {'types': 'resource', 'q': 'Img'}
        self.call(p_api.TeamSearch, param)

        # resp.check_response('total', 1, 'gt')

    @story('T136967 我的工作台顶栏搜索：搜索工作项（有项目及工作项的查看权限）')
    @parametrize('param', p.top_bar_search())
    def test_overview_search_issue(self, param):
        """概览搜索-工作项"""
        param.json |= {'q': '测试', 'types': 'task'}
        resp = self.call(p_api.TeamSearch, param)

        # resp.check_response('total', 1, 'ge')

    @story('T136972 我的工作台顶栏搜索：搜索项目（有项目的查看权限）')
    @parametrize('param', p.top_bar_search())
    def test_overview_search_project(self, param):
        """概览搜索-工作项"""
        param.json_update('q', 'Api')
        param.json_update('types', 'project')
        resp = self.call(p_api.TeamSearch, param)

        # resp.check_response('total', 1, 'ge')
        # resp.check_response('datas', 'project', 'contains')  # 检查是否有项目数据

    @story('T136971 我的工作台顶栏搜索：搜索项目（无项目的查看权限）')
    @parametrize('param', p.top_bar_search())
    def test_overview_search_project_no_permission(self, param, normal_token):
        """概览搜索-工作项-无权限"""

        resp = self.call(p_api.TeamSearch, param, token=normal_token)

        resp.check_response('total', 0)  # 没有项目工作项数据
