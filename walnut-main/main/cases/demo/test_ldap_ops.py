"""
@File    ：test_ldap_ops.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/1/21
@Desc    ：
"""
from main.api.third import LdapCmdPost


def test_ldap_ops():
    header = {
        'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%22D5R9VePb%22%2C%22first_id%22%3A%2217e6cac54b810de-0141d6373cda13-1d326253-1296000-17e6cac54b916dc%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%A4%BE%E4%BA%A4%E7%BD%91%E7%AB%99%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fopen.work.weixin.qq.com%2F%22%7D%2C%22%24device_id%22%3A%2217e6cac54b810de-0141d6373cda13-1d326253-1296000-17e6cac54b916dc%22%7D',
        '5d89dac18813e15aa2f75788275e3588': 'a1slnustbdaiiqp34rt9745086'
    }  # cookie 设置正确即可
    ldap = LdapCmdPost(header)
    j = {'cmd': 'create',
         'server_id': '1',
         'container': 'ou=z1,ou=zeno,dc=ldap,dc=example,dc=com',
         'rdn_attribute[]': 'cn',
         'new_values[cn][0]': 'zeno0004',
         'new_values[mail][0]': 'zeno0004@ones.ai',
         'new_values[gidnumber][0]': '502',
         'new_values[givenname][0]': 'zeno0004',
         'new_values[homedirectory][0]': '/home/users/z0001',
         'new_values[loginshell][0]': '/bin/sh',
         'new_values[objectclass][0]': 'inetOrgPerson',
         'new_values[objectclass][1]': 'posixAccount',
         'new_values[objectclass][2]': 'top',
         'new_values[userpassword][0]': '12345678',
         'new_values[sn][0]': 'z',
         'new_values[uidnumber][0]': '1037',
         'new_values[uid][0]': 'z0004',
         'skip_array[cn]': '',
         'skip_array[mail]': '',
         'skip_array[gidnumber]': '',
         'skip_array[givenname]': '',
         'skip_array[homedirectory]': '',
         'skip_array[loginshell]': '',
         'skip_array[objectclass]': '',
         'skip_array[userpassword]': '',
         'skip_array[sn]': '',
         'skip_array[uidnumber]': '',
         'skip_array[uid]': '',
         'meth': 'ajax'}

    ldap.call(j)
