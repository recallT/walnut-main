"""
@File    ：test_generate_param.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/6/15
@Desc    ：
"""
from falcons.ops import generate_param


def test_generate_params_list():
    add = [{}, {'abc': 1}, {'def': 2}]
    params = generate_param(*add)
    assert len(params) == 3
