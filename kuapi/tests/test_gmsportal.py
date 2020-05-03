from django.test import TestCase
import os
import logging
from dotenv import load_dotenv

from kuapi.requesters.gmsportal import GmsPortalRequester

load_dotenv('.test.env') # 테스트 파일에서의 설정파일 로드

log = logging.getLogger(__name__)


class GmsPortalTestClass(TestCase):

    gms_portal_requester = None # type: GmsPortalRequester
    sso_token = None # type: str

    def setUp(self) -> None:
        self.gms_portal_requester = GmsPortalRequester()
        self.sso_token = os.getenv('SSOTOKEN')

    @classmethod
    def setUpTestData(cls):
        pass

    def test_gms_portal(self):
        emp_no = int(os.getenv('GMS_EXPECTED_EMP_NO'))

        assert isinstance(self.sso_token, str)
        self.gms_portal_requester.sso_token = self.sso_token
        self.gms_portal_requester.authorize()
        assert self.gms_portal_requester.request_user_information()['emp_no'] == emp_no