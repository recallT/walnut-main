"""
@File    ：test_api.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/17
@Desc    ：
"""

from falcons.com.meta import OnesParams
from falcons.com.ones import parse_index, compare

a = {
    'abf': [
        {'abc': 'ass',
         'efg': [
             1, 3, 7
         ]}
    ]
}


def test_parse_index():
    assert parse_index(a, 'abf[0].abh') == 'ass'
    assert parse_index(a, 'abf[0].efg[9]') == 1


def test_compare():
    compare(1, 1)
    compare(True, True)
    compare('abc', 'abc')
    compare(1, 2, 'lt')
    compare(2, 1, 'gt')
    compare(2, 1, 'ge')
    compare(1, 2, 'le')
    compare('de', 'demo', 'in')
    compare('demo', 'mo', 'contains')
    compare([1, 2, 4], 1, 'contains')
    compare(1, [1, 2], 'in')


def test_params():
    p = OnesParams()
    p.json = a

    p.json_update('abf[0].abc', 123)
