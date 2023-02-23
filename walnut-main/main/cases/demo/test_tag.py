"""
@File    ：test_tag.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/31
@Desc    ：
"""
from falcons.helper.mocks import tag_qr


def test_qr():
    img = '/Users/zenoc/Documents/proj/walnut/tmp/cookie/qr.png'

    tag_qr(img)
