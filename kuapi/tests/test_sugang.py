from django.test import TestCase
import logging
import os

from kuapi.models.sugang import Professor
from kuapi.enums import Campus, Term
from kuapi.parsers.sugang import SugangParser
from kuapi.requesters.sugang import SugangRequester
from kuapi.clients.sugang import SugangClient

log = logging.getLogger(__name__)

def read_file(path: str):
    ## 고려대학교 수강신청시스템은 요청을 cp949로 반환합니다.
    with open('%s/kuapi/testcase/%s' % (os.getcwd(), path), 'r', encoding='cp949') as f:
        return f.read()

class SugangEtcTestClass(TestCase):
    def setUp(self) -> None:
        self.requester = SugangRequester()

    @classmethod
    def setUpTestData(cls):
        pass

    def test_etc(self):
        professor, created = Professor.objects.update_or_create(
            prof_cd=1234,
            defaults={
                'image' : None
            }
        )

class SugangParserTestClass(TestCase):
    '''
    미리 저장한 검색 결과 페이지를 로드하여, 에상된 결과를 가져오는지 확인합니다.
    '''

    parser = None # type: SugangParser

    def setUp(self) -> None:
        self.parser = SugangParser()

    @classmethod
    def setUpTestData(cls):
        pass


    def test_parse_colleage(self):
        ret = list(self.parser.parse_colleages(
            read_file('colleage.html')
        ))

        assert ret[0]['name'] == '공공정책대학' and ret[0]['col_cd'] == '6112'
        assert ret[-1]['name'] == '세종학생군사교육단(관)' and ret[-1]['col_cd'] == '6446'
        log.info('test_parse_colleage test pass!\n')
        log.info('------------------------------------------------')


    def test_parse_department(self):
        ret = list(self.parser.parse_departments(
            read_file('department.html')
        ))

        assert ret[0]['name'] == '생명공학부' and ret[0]['dept_cd'] == '4654'
        assert ret[-1]['name'] == '의과학융합전공' and ret[-1]['dept_cd'] == '5019'
        log.info('test_parse_department test pass!\n')
        log.info('------------------------------------------------')


    def test_parse_major_course_list(self):
        ret = list(self.parser.parse_course_list(
            read_file('major_courses.html'), is_general_doc=False
        ))

        assert ret[0]['name'] == '환경조경학' and ret[0]['cour_cd'] == 'LIET219'
        assert ret[-1]['name'] == '지역및도시계획학' and ret[-1]['cour_cd'] == 'LIET492'
        log.info('test_parse_courses test pass!\n')
        log.info('------------------------------------------------')


    def test_parse_general_course_list(self):
        ret = list(self.parser.parse_course_list(
            read_file('general_courses.html'), is_general_doc=True
        ))

        assert ret[0]['name'] == '1학년세미나Ⅰ 생명공학부' and ret[0]['cour_cd'] == 'GEKS005'
        assert ret[-1]['name'] == '1학년세미나Ⅰ 역사교육과' and ret[-1]['cour_cd'] == 'GEKS005'
        log.info('test_parse_general_courses test pass!\n')
        log.info('------------------------------------------------')


    def test_parse_course_list(self):
        ret = self.parser.parse_course(
            read_file('course.html')
        )
        assert ret['year'] == 2020 and ret['dept_cd'] == '5437'
        log.info('test_parse_course test pass!\n')
        log.info('------------------------------------------------')


    # 교수님 데이터는 학생 상세정보에서 가져옵니다.
    def test_parse_professor(self):
        ret = self.parser.parse_professor(
            read_file('course.html')
        )

        assert ret['prof_cd'] == 99999999
        # 교수님 정보는 개인정보가 들어있으므로 테스트 정보로 변경
        log.info('test_parse_professor test pass!\n')
        log.info('------------------------------------------------')


    def test_parse_general_first_cd_list(self):
        ret = list(self.parser.parse_general_first_cd_list(
            read_file('general_first_type.html')
        ))

        assert ret[0]['name'] == '교양' and ret[0]['general_first_cd'] == '01'
        log.info('test_parse_general_first_cd test pass!\n')
        log.info('------------------------------------------------')


    def test_parse_general_second_cd_list(self):
        ret = list(self.parser.parse_general_second_cd_list(
            read_file('general_second_type.html')
        ))

        assert ret[0]['name'] == '1학년세미나' and ret[0]['general_second_cd'] == '24'
        log.info('test_parse_general_second_cd test pass!\n')
        log.info('------------------------------------------------')

class SugangRequesterTestClass(TestCase):
    """
    전체 요청 케이스를 선정하여, 응답에 문제가 없는지 확인합니다.
    요청 후 데이터 -> 파싱 후 저장 등의 과정은 SugangRequesterEnglineClass 에서 실시합니다.
    """

    requester = None # type: SugangRequester

    year = 2017
    term = Term.fall
    campus = Campus.sejong
    col_cd = '4460' # 과학기술대힉
    dept_cd = '5040' # 전자및정보공학과
    grad_cd = '0136' # ??
    cour_cd = 'EIEN216' # 공업수학II(영강)
    cour_cls = '02' # 2분반

    general_first_cd = '01' # 교양
    general_second_cd = '24' # 1학년세미나

    def setUp(self) -> None:
        self.requester = SugangRequester()

    @classmethod
    def setUpTestData(cls):
        pass

    def test_request_colleage(self):
        self.requester.request_major_colleage_list(
            year=self.year, term=self.term, campus=self.campus
        )

    def test_request_department(self):
        self.requester.request_major_department_list(
            year=self.year, term=self.term, col_cd=self.col_cd
        )

    def test_request_course_list(self):
        self.requester.request_major_course_list(
            year=self.year, term=self.term, campus=self.campus, col_cd=self.col_cd, dept_cd=self.dept_cd
        )

    def test_request_course_detail(self):
        self.requester.request_course_detail(
            year=self.year, term=self.term, col_cd=self.col_cd, dept_cd=self.dept_cd,
            cour_cd=self.cour_cd, cour_cls=self.cour_cls, grad_cd=self.grad_cd
        )

    def test_request_general_first_cd_list(self):
        self.requester.request_general_first_cd_list()


    def test_request_general_second_cd_list(self):
        self.requester.request_general_second_cd_list(general_first_cd=self.general_first_cd)

    def test_request_general_course_list(self):
        self.requester.request_general_course_list(
            year=self.year, term=self.term, campus=self.campus,
            general_first_cd=self.general_first_cd, general_second_cd=self.general_second_cd
        )

class SugangClientTestClass(TestCase):

    client = None # type: SugangClient

    year = 2020
    term = Term.spring

    def setUp(self) -> None:
        self.client = SugangClient()

    @classmethod
    def setUpTestData(cls):
        pass

    def test_client_process_year(self):
        self.client.process_each_year(self.year)

    def test_client_process_general(self):
        self.client.year = self.year
        self.client.set_major_department_only()
        self.client.process_major_each_term(term=self.term)
        self.client.process_general_each_term(term=self.term)