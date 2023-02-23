#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_db_ops.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/11/25 
@Desc    ：
"""
from falcons.com.meta import ApiMeta
from falcons.helper.mysql import MysqlOps


def test_db_ops(environment):
    cnf = {'db': environment['db'], 'ssh_config': environment['ssh_config']}
    db = MysqlOps(cnf)
    ApiMeta.mysql = db

    r = db.execute_sql('select uuid, name from project.project order by create_time desc;')
    print(r)
