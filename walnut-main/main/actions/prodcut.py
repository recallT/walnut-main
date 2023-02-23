"""
@File    ：prodcut.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/6/9
@Desc    ：产品管理Action
"""
from falcons.check import go

from main.api import project
from main.api.project import ItemsAdd
from main.params import data
from main.params import plan


class ProductAction:
    """产品管理Action"""

    @classmethod
    def product_add(cls):
        """
        添加一个产品
        :return:
        """
        param = data.product_add()[0]
        return go(ItemsAdd, param)

    @classmethod
    def product_del(cls, product_key):
        """
        删除一个产品
        :param product_key: 产品key product-7tMnkPmXFzsFckmh形式
        :return:
        """
        param = plan.delete_item()[0]
        param.uri_args({'item_key': product_key})

        go(project.ItemDelete, param).check_response('code', 200)
