"""
@File    ：test_product_config
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/6/9
@Desc    ：产品管理-组件设置用例
"""
from falcons.check import Checker
from falcons.com.nick import fixture, feature, story

from main.actions.pro import PrjAction
from main.actions.prodcut import ProductAction


@fixture(scope='module', autouse=True)
def _prepare():
    """添加一个用于测试的项目和产品"""
    resp = ProductAction.product_add()
    item = resp.json()['item']
    product = {
        'key': item['key'],
        'uuid': item['uuid'],
    }

    project_uid = PrjAction.new_project()

    yield {
        'product': product,
        'project': project_uid
    }

    # 清理测试数据
    ProductAction.product_del(product['key'])
    PrjAction.delete_project(project_uid)


@feature('产品管理')
class TestProductConfig(Checker):
    """"""

    @story('T143660 添加一级导航组件')
    def test_add_first_class_nav(self, _prepare):
        """"""
        fcn_obj = PrjAction.add_component('一级导航', project_uuid=_prepare['project'])

        # PrjAction.remove_prj_component('一级导航')

    @story('T143662 修改一级导航名称')
    def test_modify_first_class_nav(self):
        """"""
        fcn_obj = PrjAction.add_component('一级导航')

        PrjAction.remove_prj_component('一级导航')

    @story('T23273 修改组件描述')
    @story('T143661 修改组件描述')
    def test_modify_component_desc(self):
        """"""
        pass

    @story('T23271 修改组件名称')
    @story('T143654 修改组件名称')
    def test_modify_component_name(self):
        """"""
        pass
