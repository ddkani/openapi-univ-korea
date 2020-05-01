from requests import Session

from kuapi.config import USER_AGENT

class SugangRequester(Session):

    def __init__(self):
        super().__init__()
        self.headers['User-Agent'] = USER_AGENT

    def request_major_colleage_list(self) -> list:
        pass