"""
@File    ：test_notice.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/27
@Desc    ：
"""
from falcons.com.ui import CookieMachine
from falcons.helper.notice import Notice


def test_a():
    n = Notice()
    n.post('## Test...')


def test_qr():
    cm = CookieMachine()
    cm.update_cookie()
