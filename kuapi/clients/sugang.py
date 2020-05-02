import logging

from kuapi.builders.sugang import SugangBuilder
from kuapi.enums.sugang import Term, Campus
from kuapi.models.sugang import Colleage, Department
from kuapi.parsers.sugang import SugangParser
from kuapi.requesters.sugang import SugangRequester

log = logging.getLogger(__name__)

## 수강신청 서비스 특성상 아랫 단계로 내려갈때마다 데이터를 가져와서 모두 저장하고,
## 상위 단계의 데이터가 필요한 상황이 많으므로 process 별로 설정해서 수집을 실시합니다.
## 즉 최상위 단계가 이는 특정 단계를 바로 시행하려면 client에 값 설정 후 수집해야 합니다.
## 수강신청코드가 특히 머리아픈게 파라메터도 너무많고 과정에 따라 넘길 코드도 서로 달라진다.

# TODO: 클라이언트를 제외한 각 라이브러리가 Enum에만 의존성이 있게 / 의존성 전체 없이?

class SugangClient(SugangParser, SugangRequester):
    """
    교내 수업 시간표 관리자 클라이언트입니다.
    """

    year = None  # type: int
    term = None  # type: Term

    campus = None # type: Campus
    colleage = None # type: colleage
    department = None # type: department

    ## 년도 -> 학기를 선정하면 캠퍼스를 세팅해서 진행합니다.

    def __init__(self):
        super(SugangRequester).__init__()
        super(SugangRequester).__init__()


    def process_each_year(self, year: int):
        """
        year를 제공받아 학기 순으로 전공 / 교양 정보를 수집합니다.
        다음 단계 : process_major_each_term / process_general_each_term

        @param year 수집할 년도입니다.
        """
        assert isinstance(year, int)
        self.year = year

        for term in Term:
            self.process_major_each_term(term=term)
            self.process_general_each_term(term=term)


    def process_major_each_term(self, term: Term):
        """
        year가 정해지고 term을 제공받아 캠퍼스별로 전공 정보를 수집합니다.
        다음 단계 : process_major_each_colleage

        @param term 수집할 학기입니다.
        """
        assert isinstance(term, Term)
        self.term = term

        for campus in Campus:
            self.campus = campus
            _res = self.request_major_colleage_list(
                year=self.year, term=self.term, campus=campus
            )
            _colleages = self.parse_colleages(raw_html=_res)
            for _colleage in _colleages:
                colleage = SugangBuilder.build_colleage(
                    year=self.year, term=self.term, campus=campus, **_colleage
                )
                self.process_major_each_colleage(colleage=colleage)


    def process_major_each_colleage(self, colleage: Colleage):
        """
        year, term, campus가 정해지고 colleage를 제공받아 단과대별로 전공 정보를 수집합니다.
        다음 단계 : process_major_each_department

        @param colleage 수집할 단과대학입니다.
        """
        assert isinstance(colleage, Colleage)
        self.colleage = colleage

        # 단과대학 정보 수집
        _res = self.request_major_department_list(
            year=self.year, term=self.term, col_cd=colleage.col_cd
        )
        _departments = self.parse_departments(raw_html=_res)

        # 수집된 학과정보를 저장하고, 다음단계로 진행
        for _department in _departments:
            department = SugangBuilder.build_department(
                colleage=colleage, **_department
            )
            self.process_major_each_department(department=department)


    def process_major_each_department(self, department: Department):
        """
        year, term, campus, colleage가 정해지고 department를 제공받아 학과/학부별로
        전공 정보를 수집합니다.
        다음 단계 : process_course_and_professor

        @param department 수집할 학과/학부입니다.
        """
        assert isinstance(department, Department)
        self.department = department

        # 년도, 학기, 캠퍼스, 단과대학, 학과/학부에 일치하는 전공 과목을 불러옵니다.
        _res = self.request_major_course_list(
            year=self.year, term=self.term, campus=self.campus,
            col_cd=self.colleage.col_cd, dept_cd=self.department.dept_cd
        )
        _courses = self.parse_course_list(raw_html=_res, is_general_doc=False)

        # 수집된 과목 정보를 가지고 각 세부 과목 정보와 교수님 정보를 처리한다.
        for _course in _courses:
            name = _course['name']
            cour_cd = _course['cour_cd']
            cour_cls = _course['cour_cls']
            grad_cd = _course['grad_cd']
            is_relative = _course['is_relative']
            is_limited = _course['is_limited']
            self.process_course_and_professor(
                name=name, cour_cd=cour_cd, cour_cls=cour_cls, grad_cd=grad_cd,
                is_limited=is_limited, is_relative=is_relative
            )


    def process_course_and_professor(self, name: str, cour_cd: str, cour_cls: str, grad_cd: str,
                                     is_limited:bool, is_relative:bool):
        """
        모든 정보가 정해지고, 강의 상세 정보를 수집하여 강의 / 교수님 정보를 저장합니다.
        교양과목인 경우, 사전에 colleage, department를 상위 함수에서 선언 후 호출하여야 합니다.

        @param name 과목 이름입니다.
        @param is_limited 교과목의 인원 제한 여부입니다.
        @param is_relative 교과목의 상대 평가 여부입니다.
        @param cour_cd 교과 코드입니다.
        @param cour_cls 분반 코드입니다.
        """
        assert isinstance(name, str)
        assert isinstance(is_limited, bool)
        assert isinstance(is_relative, bool)
        assert isinstance(cour_cd, str)
        assert isinstance(cour_cls, str)
        assert isinstance(grad_cd, str)

        log.debug("start fetch %s %s %s" % (name, cour_cd, cour_cls))

        _res = self.request_course_detail(
            year=self.year, term=self.term, col_cd=self.colleage.col_cd, dept_cd=self.department.dept_cd,
            cour_cd=cour_cd, cour_cls=cour_cls, grad_cd=grad_cd
        )
        _course = self.parse_course(raw_html=_res)

        score = _course['score']
        complition_type = _course['complition_type']
        timetables = _course['timetables']

        course = SugangBuilder.build_course(
            department=self.department, cour_cd=cour_cd, cour_cls=cour_cls, name=name, grad_cd=grad_cd,
            score=score, complition_type=complition_type, is_relative=is_relative, is_limited=is_limited,
        )

        ## each timetable
        ## Week, (start, end), 수업위치
        for _timetable in timetables:
            SugangBuilder.build_course_timetable(course=course, timetable_meta=_timetable)

        ## 사진 정보는 나중에 다운로드 받을 수 있도록 지원함.
        _professor = self.parse_professor(raw_html=_res)
        SugangBuilder.build_professor(**_professor)

        log.debug("end fetch %s %s %s" % (name, cour_cd, cour_cls))


    def process_general_each_term(self, term: Term):
        """
        year가 정해지고 term을 제공받아 캠퍼스별로 교양 정보를 수집합니다.
        다음 단계 : process_general_each_gen

        @param term 수강할 학기입니다.
        """
        assert isinstance(term, Term)
        self.term = term

        for campus in Campus:
            self.campus = campus

            _first_cds = self.parse_general_first_cd_list(raw_html=self.request_general_first_cd_list())
            for _first_cd in _first_cds:
                _second_cds = list(self.parse_general_second_cd_list(
                    raw_html=self.request_general_second_cd_list(general_first_cd=_first_cd)
                ))
                if not _second_cds:
                    self.process_general_each_gen(
                        general_first_cd=_first_cd
                    )
                else:
                    for _second_cd in _second_cds:
                        self.process_general_each_gen(
                            general_first_cd=_first_cd, general_second_cd=_second_cd
                        )


    def process_general_each_gen(self, general_first_cd: str, general_second_cd:str=""):
        """
        year, term, campus 가 정해지고 각 교양 과목별로 강의 리스트를 요청합니다.
        다음 단계: process_course_and_professor

        @param general_first_cd 대단위 강좌 분류입니다.
        @param general_second_cd 소단위 강좌 분류입니다.
        """
        assert isinstance(general_first_cd, str)
        assert isinstance(general_second_cd, str)

        _res = self.request_general_course_list(
            year=self.year, campus=self.campus, term=self.term,
            general_first_cd=general_first_cd, general_second_cd=general_second_cd
        )
        _courses = self.parse_course_list(raw_html=_res, is_general_doc=True)

        for _course in _courses:
            name = _course['name']
            cour_cd = _course['cour_cd']
            cour_cls = _course['cour_cls']
            grad_cd = _course['grad_cd']
            is_relative = _course['is_relative']
            is_limited = _course['is_limited']
            self.process_course_and_professor(
                name=name, cour_cd=cour_cd, cour_cls=cour_cls, grad_cd=grad_cd,
                is_limited=is_limited, is_relative=is_relative
            )
