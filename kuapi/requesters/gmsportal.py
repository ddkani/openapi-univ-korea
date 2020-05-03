import logging
from requests import Session
from copy import copy

from kuapi.config import USER_AGENT
from kuapi.enums import Campus, Sex

log = logging.getLogger(__name__)


URL_GMS_AUTH = 'https://gmsportal.korea.ac.kr/portal/menu.lnk'
URL_GMS_GET_INFO = 'https://gmsportal.korea.ac.kr/com/auth/auth.do'

DATA_GET_GMSPORTAL_SESSIONID = {
    'token' : '',
    'path' : '/portal/menu.lnk?pgm_id=KHMS00.KHMS0001E.00',
    'url' : "https://gmsportal.korea.ac.kr/portal/menu.lnk?pgm_id=KHMS00.KHMS0001E.00",
    'compId' : 81,
    'menuCd' : 2160,
    'return_url' : '/portal/menu.lnk?pgm_id=KHMS00.KHMS0001E.00',
    'query' : '',
    'language' : 'ko',
    'compDiv' : 'S',
    'locale' : 'ZW4=',
    'lang' : 'KOR'
}
PARAM_GET_GMSPORTAL_SESSIOND = {'pgm_id' : 'KHMS00.KHMS0001E.00'}
DATA_GET_GMSPORTAL_INFO = {
    'menu_pgm_id' : 'KHMS00.KHMS0001E.00',
    'strReqMenuPgmId' : 'KHMS00.KHMS0001E.00',
    'strAppLoginTime' : 'NO_CHKECK' # 실제 오타를 이렇게 전송하도록 되어있습니다.
}

## 수강신청 서비스와 달리 포매팅이 되어 반환되므로, 별도의 parser를 또 만들 필요는 없습니다.
## 요청이 올바른지의 검증도 requester에서 확인합니다.

class GmsPortalRequester(Session):

    sso_token = None # type: str
    authorized = None # type: bool

    def __init__(self, sso_token:str=None):
        super().__init__()
        self.authorized = False
        self.headers['User-Agent'] = USER_AGENT
        if sso_token:
            self.sso_token = sso_token
            self.authorize()


    def authorize(self, sso_token:str=None) -> None:
        """
        포털 sso_token을 이용해 사용자 인증합니다.
        """
        if not self.sso_token and not sso_token:
            assert AssertionError("sso_token이 설정되지 않았습니다.")

        if sso_token:
            self.sso_token = sso_token

        data = copy(DATA_GET_GMSPORTAL_SESSIONID)
        data['token'] = self.sso_token

        _ret = self.post(
            url=URL_GMS_AUTH, params=PARAM_GET_GMSPORTAL_SESSIOND,
            data=data
        ).text

        if '불편을 드려서 죄송합니다.' in _ret:
            log.critical('authorization failed. response: %s' % _ret)
            assert AssertionError('인증에 실패했습니다.')

        log.debug(
            'authorization ok : session %s...' % self.cookies['GMSPORTAL_SESSIONID'][:8]
        )
        self.authorized = True


    def request_user_information(self) -> dict:
        """
        gmsportal.korea.ac.kr 에서 사용자 정보의 일부를 가져옵니다.

        campus , sex => kuapi.enums

        @return emp_no:int:학번 dept_cd:str:학과번호 dept_nm:str:학과이름 user_nm:str:이름 campus:Campus:캠퍼스 sex:Sex:성별
        """
        if not self.authorized:
            assert AssertionError("인증되지 않았습니다.")

        _ret = self.post(
            url=URL_GMS_GET_INFO, data=DATA_GET_GMSPORTAL_INFO,
            headers={'res-protocol': 'json'}
        ).json()

        _result =  'root' in _ret and 'roleinfo' in _ret['root']
        if not _result:
            log.critical('unexpected: server response: %s' % _ret)
            raise AssertionError('사용자 정보를 가져오지 못했습니다.')

        ret = _ret['root']['roleinfo'] # type: dict

        log.debug('hak_number %s userinfo requested.' % ret['emp_no'])

        ### 모든 데이터는 str 형식입니다.
        target_key = (
            ('campus_cd', int), # 캠퍼스
            ('emp_no', int), # 학번
            ('dept_cd', str), # 학과 고유코드
            ('dept_nm', str), # 학과 이름
            ('user_nm', str), # 본인 이름
            ('sex_cd', int) # 성별
        )

        result = dict()
        for d in target_key:
            k = d[0] # type: str
            tp = d[1] # conversion type

            result.setdefault(k, tp(ret.pop(k)))

        result['campus'] = Campus(int(result['campus_cd']))
        result['sex'] = Sex(int(result['sex_cd']))

        result.pop('campus_cd'); result.pop('sex_cd')

        return result