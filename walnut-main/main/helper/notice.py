"""
@File    ：notice.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/27
@Desc    ：
"""
import base64
import hashlib

import requests
import urllib3

from main.config import RunVars

urllib3.disable_warnings()


class Notice:
    """"""

    def __init__(self):
        self.hook = RunVars.login_hook
        self.cookie_dir = RunVars.cookie_path

    def send_qr(self):
        pic_msg = self.qr_message()
        self.post(pic_msg)

    def send_thanks(self, user):
        content = f'###  Cookie 更新成功 ✌️ \n 感谢老铁， @{user} ！！！'
        msg = self.set_content(content)
        self.post(msg)

    @classmethod
    def set_content(cls, text: str):
        """组装Markdown格式的消息体"""
        body = {
            'msgtype': 'markdown',
            'markdown': {
                'content': text
            }
        }

        return body

    def post(self, msg: dict):
        """
        发送企业微信通知

        :param msg:  通知内容
        :return:
        """
        resp = requests.post(self.hook, json=msg,
                             headers={'Content-Type': 'application/json'},
                             verify=False
                             )
        if resp.status_code == 200:
            print('Send notice success...')

    def qr_message(self) -> dict:
        """"""
        pic_name = f'{self.cookie_dir}/qr.png'

        with open(pic_name, 'rb') as f:
            picture = f.read()
            md5_val = hashlib.md5(picture).hexdigest()
            b64_val = base64.b64encode(picture).decode()

            q = {
                'msgtype': 'image',
                'image': {
                    'base64': b64_val,
                    'md5': md5_val
                }
            }

        return q
