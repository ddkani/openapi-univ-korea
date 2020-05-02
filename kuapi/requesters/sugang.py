import logging
from requests import Session

from kuapi.enums.sugang import Campus, Term
from kuapi.config import USER_AGENT

log = logging.getLogger(__name__)

## build_form 에 대한 정의는 조금 더 생각해보자.
## python 3.8 부터 지원하는데, 잘못 설치하면 꼬일 수 있으니...

# requester 에서는 요청 검증을 위한 이전 요청 (예: referrer) 등을 제외하고,
# 모든 인자값은 직접 받습니다. 상태 저장은 client / engine 에서 합니다.

# 단, 요청(인자)값은 적절한지, 요청 완료 후 받은 값은 적절한지 확인하는 절차는 필요합니다.
# TODO: sentry 랑 연계해서 넣고 싶은데, 우선 없는 버전을 작성하고 추후에 에러 처리 등을 추가한다.

URL_LEC_MAJOR_SUB = 'http://sugang.korea.ac.kr/lecture/LecMajorSub.jsp'
URL_LEC_ETC_SUB = 'http://sugang.korea.ac.kr/lecture/LecEtcSub.jsp'
URL_LEC_DEPT_POPUP = 'http://sugang.korea.ac.kr/lecture/LecDeptPopup.jsp'
URL_LEC_DETAIL = 'http://infodepot.korea.ac.kr/lecture1/lecsubjectPlanView.jsp'
PARAMS_LANG = {'lang' : 'KOR'}
DEFAULT_GRAD_CD = "0136"

class SugangRequester(Session):
    """
    sugang.korea.ac.kr 시간표 요청을 위한 클래스입니다.
    """

    def __init__(self):
        super().__init__()
        self.headers['User-Agent'] = USER_AGENT
        self.headers['Referrer'] = 'http://sugang.korea.ac.kr'


    def validate_response(self, response: str, raise_exception=True) -> bool:
        if "Error!!" not in response: return True
        if not raise_exception: return False
        raise ValueError("%s is not vaild reponse." % response)


    def request(self, method, url: str, **kwargs):
        ## set referrer? .. 안해도 크게 문제는 없음.
        ## stack => caller to set referrer

        ret = super().request(method, url, **kwargs)
        # TODO: validate_response error check
        if "lecEmpPhoto" not in url:
            if self.validate_response(ret.text):
                log.debug("requested: %s" % url)
            else:
                log.critical("request validate error: %s" % url)

        return ret


    def request_major_colleage_list(self, year: int, term: Term, campus: Campus) -> str:
        assert isinstance(year, int)
        assert isinstance(term, Term)
        assert isinstance(campus, Campus)

        ## TODO : typedDict => build 하여 새로운 폼 반환?
        data = {
            'yy' : year,
            'tm' : term.value,
            'sCampus' : campus.value,
            'col' : 1
        }
        data.update(PARAMS_LANG)

        ret = self.post(URL_LEC_MAJOR_SUB, params=PARAMS_LANG, data=data).text
        return ret


    def request_major_department_list(self, year: int, term: Term, col_cd: str) -> str:
        assert isinstance(year, int)
        assert isinstance(term, Term)
        assert isinstance(col_cd, str)

        params = {
            'frm': 'frm_ms',
            'dept': 'dept',
            'year': year,
            'term': term.value,
            'colcd': col_cd
        }
        params.update(PARAMS_LANG)

        ret = self.get(URL_LEC_DEPT_POPUP, params=params).text
        return ret


    def request_major_course_list(self, year: int, term: Term, campus: Campus, col_cd: str, dept_cd: str) -> str:
        assert isinstance(year, int)
        assert isinstance(term, Term)
        assert isinstance(campus, Campus)
        assert isinstance(col_cd, str)
        assert isinstance(dept_cd, str)

        data = {
            "yy": year,
            "tm": term.value,
            "sCampus": campus.value,
            "col": col_cd,
            "dept": dept_cd
        }

        ret = self.post(URL_LEC_MAJOR_SUB, params=PARAMS_LANG, data=data).text
        return ret

    # ------------

    def request_general_first_cd_list(self) -> str:
        """
        교양과목 1단계 분류를 가져옵니다. 년도 / 캠퍼스 별로 구분이 없습니다.
        """
        ret = self.get(url=URL_LEC_ETC_SUB, params=PARAMS_LANG).text
        return ret


    def request_general_second_cd_list(self, general_first_cd: str) -> str:
        """
        교양과목 2단계 분류를 가져옵니다. 년도 / 캠퍼스 별로 구분이 없습니다.

        @param general_first_cd 교양 1분류입니다.
        """
        assert isinstance(general_first_cd, str)
        params = {
            'frm': 'frm_ets',
            'colcd': general_first_cd,
            'deptcd': '',
            'dept': 'dept'
        }
        params.update(PARAMS_LANG)

        ret = self.get(url=URL_LEC_DEPT_POPUP, params=params).text
        return ret


    def request_general_course_list(self, year: int, term: Term, campus: Campus, 
                                    general_first_cd: str, general_second_cd: str="") -> str:
        assert isinstance(year, int)
        assert isinstance(term, Term)
        assert isinstance(campus, Campus)
        assert isinstance(general_first_cd, str)
        assert isinstance(general_second_cd, str)

        data = {
            'yy' : year,
            'tm' : term.value,
            'campus' : campus.value,
            'colcd' : general_first_cd,
            'deptcd' : general_second_cd
        }

        ret = self.post(url=URL_LEC_ETC_SUB, params=PARAMS_LANG, data=data).text
        return ret

    # ------------

    def request_course_detail(self, year: int, term: Term, col_cd: str, dept_cd: str, cour_cd: str,
                              cour_cls: str, grad_cd: str) -> str:
        """
        과목의 세부 정보를 요청합니다.

        @param year 과목의 년도입니다.
        @param term 과목의 학기입니다.
        @param col_cd 단과대학 코드입니다.
        @param dept_cd 학과/학부 코드입니다.
        @param cour_cd 과목 코드입니다.
        @param cour_cls 과목 분반입니다.
        """
        assert isinstance(year, int)
        assert isinstance(term, Term)
        assert isinstance(col_cd, str)
        assert isinstance(dept_cd, str)
        assert isinstance(cour_cd, str)
        assert isinstance(cour_cls, str)
        assert isinstance(grad_cd, str)

        data = {
            'grad_cd': grad_cd,
            'year': year,
            'term': term.value,
            'col_cd': col_cd,
            'dept_cd': dept_cd,  # 학과코드
            'cour_cd': cour_cd,  # 과목코드
            'cour_cls': cour_cls
        }

        ret = self.post(URL_LEC_DETAIL, data=data).text
        return ret


    ## 데이터 크기가 크지 않으므로 데이터를 직접 return (제네레이터 같은게 있나..?)
    def request_professor_picture(self) -> bytearray:
        pass