import imaplib

from falcons.helper.mocks import fake_cookie

from main.api.task import UpBox
import email


class EmailGateApi(UpBox):
    """ones邮件网关"""
    uri = 'https://mailhog.myones.net'
    name = '读取邮箱内容'
    api_type = 'GET'

    def _get_content(self, _email: dict):
        '''获取邮件内容'''
        if 'Content' not in _email.keys():
            raise ValueError(f'邮件确实字段Content')
        # headers = _email['Content']['Headers']
        body = _email['Content']['Body']
        import quopri
        _c = quopri.decodestring(body).decode('utf-8')
        return _c

    def _get_subject(self, _email: dict):
        '''获取邮件主题'''
        if 'Content' not in _email.keys():
            raise ValueError(f'邮件确实字段Content')
        subject = _email['Content']['Headers']['Subject']
        try:
            _subject = email.header.decode_header(subject[0])
            _b = _subject[0][0]  # 主题：二进制字符串
            _e = _subject[0][1]  # 编码
            subject = _b.decode(_e) if _e else _b.decode()
            return subject
        except Exception as e:
            # 转码错误，原文返回
            return subject
            # raise ValueError('邮件主题编码错误')

    def call(self, sub_uri, params={}, json={}):
        cookies = fake_cookie()
        user_ID = 'ONES'  # mail登录账号
        _cookies = {}
        from urllib.parse import urlparse
        mail_host = urlparse(self.uri).hostname
        for c in cookies:
            _v = ''
            if c['name'] == 'OauthUserID':
                _v = user_ID
            elif c['name'] == 'OauthAccessToken':
                _v = f'{mail_host}{user_ID}{c["expires"]}'
            else:
                _v = c['value']
            _cookies[c['name']] = _v
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }

        res = self.session.get(f'{self.uri}{sub_uri}', headers=headers,
                               cookies=_cookies, params=params, verify=False)

        return res.json()

    def _parse(self, _email):
        _s = self._get_subject(_email)
        _c = self._get_content(_email)
        return {
            'content': _c,
            'subject': _s,
            'from': _email['Content']['Headers']['From'][0],
            'to': _email['Content']['Headers']['To'][0],
            'date': _email['Content']['Headers']['Date'][0]
        }

    def mail_list(self):
        res = self.call('/api/v2/messages', params={'limit': 50})
        emails = []
        if res['total'] > 0:
            for _email in res['items']:
                _email = self._parse(_email)
                emails.append(_email)

        return emails

    def first_mail(self):
        res = self.call('/api/v2/messages', params={'limit': 50})
        if res['total'] > 0:
            _e = res['items'][0]
            _e = self._parse(_e)
            return _e

    def search_mails(self, receiver):
        res = self.call('/api/v2/search', params={'kind': 'to', 'query': receiver})
        if res['total'] > 0:
            _email = res['items'][res['total'] - 1]
            return self._parse(_email)


IMAP4_SSL_PORT = 993


class Connection:
    '''真实邮箱连接，imap'''
    def __init__(self, mail_user: str, mail_pwd, mail_host='imap.163.com', mail_port=IMAP4_SSL_PORT):
        self.mail_user = mail_user
        self.mail_pwd = mail_pwd
        try:
            self.conn = imaplib.IMAP4_SSL(host=mail_host, port=mail_port)
            self.conn.login(user=mail_user, password=mail_pwd)
            if mail_host == 'imap.163.com':
                imap_id = ('name', mail_user.split('@')[0],
                           'contact', mail_user, 'version', '1.0.0', 'vendor', 'myclient')
                self.conn.xatom('ID', '("' + '" "'.join(imap_id) + '")')
        except Exception as e:
            raise ValueError(f'邮箱服务host，port，登录用户名，密码不正确，请检查～ 异常信息：{e}', )


# 测试邮箱
connection = Connection(mail_user='T2075520629@163.com', mail_pwd='WKBWVYVMFOBDUECX')


class EmailReader:
    '''真实邮箱读取'''
    conn = None

    def __init__(self, connect: Connection = None):
        self.conn = connect.conn if connect else connection.conn

    def get_email(self, sender='sys@mail.ones.ai'):
        self.conn.select()
        # typ, _idx = self.conn.search(None, '(FROM "ONES")')
        typ, _idx = self.conn.search(None, 'ALL')
        # print(typ, _idx)
        idx = _idx[0].split()[::-1]
        if typ == 'OK':
            # 取最近一封邮件
            if idx:
                typ, data = self.conn.fetch(idx[0], '(RFC822)')
                if typ == 'OK':
                    text = data[0][1]
                    message = email.message_from_bytes(text)
                    headers = self._parse_header(message)
                    body = self._parse_body(message)
                    _email = headers | body
                    if _email and _email['from'] != sender:
                        _email = None
                    return _email

    @classmethod
    def _parse_header(cls, message):
        """ 解析邮件头部信息 """
        subject = message.get('Subject')
        s = email.header.decode_header(subject)
        _s = s[0][0]
        _e = s[0][1]
        subject = _s.decode(_e) if _e else _s.decode()
        return {
            'from': email.utils.parseaddr(message.get('from'))[1],
            'to': email.utils.parseaddr(message.get('to'))[1],
            'date': message.get('date'),
            'subject': subject
        }

    @classmethod
    def _parse_body(cls, message):
        content = []

        def _guess_charset(_message):
            charset = _message.get_charset()
            if charset is None:
                charset: str = _message.get_content_charset()
            return charset

        def _parse(_part):
            content_type = _part.get_content_type()
            if content_type == 'text/plain' or content_type == 'text/html':
                content_transfer_encoding = _part.get('Content-Transfer-Encoding', '')
                _content = _part.get_payload(decode=True)
                charset = _guess_charset(part)
                if charset:
                    return _content.decode(charset)

        """ 解析邮件正文 """
        # 循环信件中的每一个mime的数据块
        for part in message.walk():
            # 内容不是一个子EmailMessage对象的列表，再解析
            # 注意邮件有多个部分
            if not part.is_multipart():
                _c = _parse(part)
                content.append(_c)

        return {'content': ' '.join(content)}
