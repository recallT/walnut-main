#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：__init__.py.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/11/18 
@Desc    ：工具包
"""

import requests


class Notify:
    """"""

    def __init__(self, job_name):
        self.job_name = job_name
        self.hook = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=1ee9e732-c6b3-499a-8c5c-434c1a13e833'
        self.jenkins_host = 'http://119.23.154.208:8080/job/{job_name}/lastBuild/api/json'
        self.job_json = {}

    def run(self):
        """"""
        self.get_job_json()
        self.notify_content()
        self.sent_msg()

    def get_job_json(self):
        """"""
        resp = requests.get(self.jenkins_host.format(**{'job_name': self.job_name}))
        if resp.status_code == 200:
            self.job_json = resp.json()

    def get_user_name(self):
        """"""
        user_name = ''
        actions = self.job_json['actions']
        for action in actions:
            if '_class' in action and 'causes' in action:
                user_name = action['causes'][0]['userName']

        return user_name

    def notify_content(self):

        color = {
            'a': 'info',
            'b': 'warning',
        }
        status = 'a' if self.job_json["result"] == 'SUCCESS' else 'b'
        m = {
            'full_name': self.job_json['fullDisplayName'],
            'duration': self.job_json['duration'],
            'link': f'{self.job_json["url"]}allure',
            'info': f'{color[status]}'
        }

        body = {
            "msgtype": "markdown",
            "markdown": {
                "content": '## <font color="{info}">测试任务 [{full_name}] 执行完了。</font>\n\n'
                           '#### [戳一下查看报告👈]({link})'.format(**m)
            }
        }
        return body

    def sent_msg(self):
        resp = requests.post(self.hook, json=self.notify_content(), headers={'Content-Type': 'application/json'},
                             verify=False)
        if resp.status_code == 200:
            print('Done...')
