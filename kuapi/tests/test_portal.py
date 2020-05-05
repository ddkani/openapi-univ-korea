from django.test import TestCase
import os
import logging
from dotenv import load_dotenv

from kuapi.requesters.portal import PortalRequester

load_dotenv('.test.env') # 테스트 파일에서의 설정파일 로드

log = logging.getLogger(__name__)


class PortalTestClass(TestCase):

    portal_requester  = None # type: PortalRequester
    portal_user_id = None # type: str
    portal_password = None # type: str

    def setUp(self) -> None:
        self.portal_requester = PortalRequester()
        self.portal_user_id = os.getenv('PORTAL_USER_ID')
        self.portal_password = os.getenv('PORTAL_PASSWORD')

    @classmethod
    def setUpTestData(cls):
        pass

    def test_portal(self):
        assert self.portal_requester.authorize(self.portal_user_id, self.portal_password)