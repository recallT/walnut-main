"""
@File    ：test_retry.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/6/25
@Desc    ：
"""
from main.helper.extra import retry


def func_demo():
    assert 1 == 1


class DDD:

    @classmethod
    @retry
    def demo_1(cls):
        """测试方法"""
        raise RuntimeError('dheh')

    @classmethod
    @retry
    def demo_2(cls):
        assert 1 == 1


def test_retry():
    DDD.demo_1()
    DDD.demo_2()
