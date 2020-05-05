import logging
from requests import Session

from kuapi.config import USER_AGENT
from kuapi.exceptions import AuthenticationError

log = logging.getLogger(__name__)

SESSION_KEY = 'GRW_SESSIONID'

class GrwRequester(Session):

    @property
    def GRW_SESSIONID(self):
        return self.cookies[SESSION_KEY]

    def __init__(self, GRW_SESSIONID):
        super().__init__()
        self.headers['User-Agent'] = USER_AGENT
        self.cookies.add(SESSION_KEY, GRW_SESSIONID)


    def validate(self, raw_html: str, raise_exception:bool=True):
        """
        응답 데이터가 올바른지 검증합니다. 로그아웃되었다면, 재로그인이 필요합니다.
        """
        result = 'LoginDeny' not in raw_html

        if not result:
            if raise_exception:
                raise AuthenticationError("세션이 만료되었습니다.")

        return result


    def request_notice_list(self, current_page: int, page_count: int,
                            kind:int, list_count:int=10) -> str:
        """
        공지 리스트를 가져옵니다.
        """
        ## TODO: dictionary formatter
        pass


    def request_notice(self, index: int, message_id: int) -> str:
        """
        공지 일정을 가져옵니다.
        """
        pass





