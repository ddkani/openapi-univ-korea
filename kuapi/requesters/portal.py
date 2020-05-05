import logging
from requests import Session
from copy import copy

from kuapi.config import USER_AGENT
from kuapi.exceptions import AuthenticationError

log = logging.getLogger(__name__)

URL_PORTAL_AUTH = 'https://portal.korea.ac.kr/common/Login.kpd'
DATA_PORTA_AUTH = {
    'id' : '',
    'pw' : '',
    'direct_div' : '',
    'pw_pass' : '',
    'browser' : 'chrome'
}

class PortalRequester(Session):

    is_authorized = None # type: bool

    def __init__(self):
        super().__init__()
        self.headers['User-Agent'] = USER_AGENT
        self.is_authorized = False


    @property
    def SSOTOKEN(self):
        """
        ssotoken을 반환합니다. (intrtoken과 동일합니다.)
        대부분의 교내 시스템의 세션을 받기 위해 사용됩니다.
        """
        assert self.is_authorized, True
        return self.cookies['ssotoken']

    @property
    def GRW_SESSIONID(self):
        """
        grw.korea.ac.kr
        """
        assert self.is_authorized, True
        return self.cookies['GRW_SESSIONID']

    @property
    def ICERT_SESSIONID(self):
        """
        icert.korea.ac.kr
        """
        assert self.is_authorized, True
        return self.cookies['ICERT_SESSIONID']

    @property
    def KMS_SESSIONID(self):
        """
        kms.korea.ac.kr
        """
        assert self.is_authorized, True
        return self.cookies['KMS_SESSIONID']


    def validate(self, raw_html: str, raise_exception:bool=True):
        """
        응답 데이터가 올바른지 검증합니다. 로그아웃되었다면, 재로그인이 필요합니다.
        """
        result = 'LoginDeny' not in raw_html

        if not result:
            # 로그아웃되었습니다. 세션을 초기화합니다.
            self.cookies.clear()
            self.is_authorized = False
            if raise_exception:
                raise AuthenticationError("세션이 만료되었습니다.")

        return result


    def authorize(self, userid: str, password: str):
        assert isinstance(userid, str)
        assert isinstance(password, str)

        data = copy(DATA_PORTA_AUTH)
        data['id'] = userid
        data['pw'] = password

        response = self.post(url=URL_PORTAL_AUTH, data=data, allow_redirects=False).text
        result = 'http://portal.korea.ac.kr/front/Main.kpd' in response # type: bool

        log.info("%s user authorization : %s" % (userid, result))
        if not result:
            log.critical("%s user authorzation failed: body : %s" % (userid, response))
        return result