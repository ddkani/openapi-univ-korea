from django.test import TestCase
import logging
import os

from kuapi.parsers.sugang import SugangParser

log = logging.getLogger(__name__)

def read_file(path: str):
    ## 고려대학교 수강신청시스템은 요청을 cp949로 반환합니다.
    with open('%s/kuapi/testcase/%s' % (os.getcwd(), path), 'r', encoding='cp949') as f:
        return f.read()

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


    def test_parse_courses(self):
        ret = list(self.parser.parse_courses(
            read_file('courses.html')
        ))

        assert ret[0]['name'] == '환경조경학' and ret[0]['cour_cd'] == 'LIET219'
        assert ret[-1]['name'] == '지역및도시계획학' and ret[-1]['cour_cd'] == 'LIET492'
        log.info('test_parse_courses test pass!\n')
        log.info('------------------------------------------------')


    def test_parse_course(self):
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