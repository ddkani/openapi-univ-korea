import logging

import lxml.html
from lxml.html import HtmlElement
from parse import parse, search, findall

from types import GeneratorType

from kuapi.miscs import extract_query_from_url
from kuapi.enums.sugang import Campus, Term, Week
from kuapi.regexrs import SugangRegexr
from kuapi.miscs import satinize


log = logging.getLogger(__name__)


# Warning: support from 3.8 - typeddict
# Warning: yield 기반 함수가 아무것도 하지 않을 경우, list(func()) 는 오류입니다.


class HtmlParser:
    def init_tree(self, raw_html: str) -> HtmlElement:
        return lxml.html.document_fromstring(raw_html)

## Parser의 기준은 특정 페이지에서 정보를 뽑아 내는 것만 수행하고, 별도 데이터베이스 작업을 하지 않습니다.
## 상위 호출자에서 get_or_create // **kwargs 등을 사용하면 그만입니다.
## 별도의 데이터 컨테이너를 사용하지 않고
## ...s =>  제네레이터
## 데이터가 여러 개일 경우 딕셔너리 만을 사용합니다. !!! 별도 데이터 컨테이너를 만들지 않습니다!



## unhandled behavior
# #1. HtmlElement.text() => 데이터 존재하지 않을시 None 또는 "" 반환?


class SugangParser(HtmlParser):

    def __init__(self):
        super().__init__()


    def parse_colleages(self,raw_html:str) -> GeneratorType:
        """

        @param raw_html
        """
        assert raw_html != ""
        tree = self.init_tree(raw_html)

        colleages = tree.xpath("//select[@name = 'col' and @id='col']//option[position() > 1]")
        if not colleages:
            yield from []

        for _opt in colleages: # type: HtmlElement
            _name = _opt.text_content()
            _col_cd = _opt.attrib['value']

            log.debug("name=%s, col_cd=%s" % (_name, _col_cd))

            yield {
                'name' : _name,
                'col_cd' : _col_cd
            }


    def parse_departments(self, raw_html: str) -> GeneratorType:
        """

        @param raw_html infodepot.
        """
        assert raw_html != ""

        ## parser => regex 기존 코드 이용
        # 사유: 사용하지 않는 학과는 빨강색으로 표시

        # _cds = list(findall('el.value ="{:w}"', raw_html))
        # _names = list(findall('el.text = "{:w}"', raw_html))
        #
        # assert len(_cds) == len(_names) # 갯수가 다를경우 오류
        # assert _cds and _names # 존재하지 않을 경우 오류

        # for _i in range(len(_cds)):
        #     _name = _names[_i].fixed[0].strip()
        #     _dept_cd = _cds[_i].fixed[0].strip()
        #
        #     log.debug("name=%s, dept_cd=%s" % (_name, _dept_cd))

        departments = SugangRegexr.regex_departments(raw_html)
        if not departments:
            yield from [] # department 없는 경우 대응

        # 결과가 없으면 이 문장은 자동으로 넘어가므로 굳이 if 문이 필요 없다.
        for d in departments:

            dept_cd = d[0].strip()
            name = d[1].strip()

            log.debug("name=%s, dept_cd=%s" % (name, dept_cd))

            yield {
                'dept_cd' : dept_cd,
                'name' : name
            }


    def parse_course_list(self, raw_html: str, is_general_doc:bool) -> GeneratorType:
        """
        강의 리스트를 파싱합니다.

        @param raw_html sugang.korea.ac.kr/lecture/LecMajorSub.jsp
        @param is_general_doc 강의리스트가 교양 페이지인지 확인합니다.
        """

        assert raw_html != ""
        assert isinstance(is_general_doc, bool)
        
        tree = self.init_tree(raw_html)

        lectures = tree.xpath("//tr[position() > 1]")
        if not lectures:
            yield from []

        # 첫번째 테이블은 자료 주석이므로 실행하지 않음.
        for _lec in lectures:
            tds = _lec.xpath(".//td" if is_general_doc else ".//td[position() > 1]")

            _url = tds[0].xpath("./a")[0].attrib['href']
            basics = extract_query_from_url(_url, ('term', 'grad_cd', 'dept_cd', 'cour_cd'))

            # _campus = Campus.parse(tds[0].text).value
            # _cour_cd = tds[0].text.strip() # XPath("string()")
            _cls = tds[1].text.strip() # 분반이 반드시 string이 아님.
            ## 이수구분
            # _complition_type = tds[2].text.strip()
            _name = tds[3].text_content().strip().replace('\n','').replace('\t','').replace('\xa0',' ')
            ## 교수이름 - 상세정보에서 가져오기 / parse:: 이름 명시하지 않으면 named에서 생략 가능.
            _score = parse("{time:w}(  {score:w})", tds[5].text.strip()).named['score']
            ## 강의시간 / 강의실 - 상세정보에서 가져오기


            _is_relative = bool(tds[7].text)
            _is_limited = bool(tds[8].text)

            ## 해당 기본정보가 있어야 강의 상세정보를 요청할 수 있습니다.
            result = {
                'name' : _name,
                'cls' : _cls,
                'score' : _score,
                'is_relative' : _is_relative,
                'is_limited' : _is_limited
            }
            result.update(basics)
            log.debug(result)

            yield result


    def parse_course(self, raw_html: str) -> dict:
        """
        강의 상세정보를 파싱합니다. (교양 / 전공과목 모두 동일합니다.)

        @param raw_html infodepot.korea.ac.kr/lecture1/lecsubjectPlanView.jsp
        """
        assert raw_html != ""
        tree = self.init_tree(raw_html)

        basics = tree.xpath('//form[@name="form1"]/input')
        tds = tree.xpath('//table[@class="tbl_view"]//td')

        _time = tds[0].text
        timetables = list()

        if _time:
            for _t in _time.split('\n'):
                _p = SugangRegexr.regex_course_timetable(_t)
                if _p: timetables.append(_p) # if _p : 비어있는 투플도 성립

        score = int(tds[1].text.strip())
        complition_type = tds[3].text.strip()

        year = int(basics[2].value.strip())
        term = Term(basics[3].value.strip())
        dept_cd = basics[4].value.strip()
        cour_cd = basics[5].value.strip()
        grad_cd = basics[6].value.strip()
        cour_cls = int(basics[7].value)
        name = basics[8].value.strip()
        col_cd = basics[9].value.strip()

        ret = {
            'year' : year,
            'term' : term,
            'dept_cd' : dept_cd,
            'cour_cd' : cour_cd,
            'grad_cd' : grad_cd, ## ?
            'cour_cls' : cour_cls,
            'name' : name,
            'score' : score,
            'col_cd' : col_cd,
            'complition_type' : complition_type,
            'timetables' : timetables
        }
        log.debug(ret)

        return ret


    def parse_professor(self, raw_html: str) -> dict:
        """
        교수 정보를 파싱합니다.

        @param raw_html infodepot.korea.ac.kr/lecture1/lecsubjectPlanView.jsp
        """
        assert raw_html != ""
        tree = self.init_tree(raw_html)

        photo_url = 'http://infodepot.korea.ac.kr/' + tree.xpath('//span[@class="photo"]/img')[0].attrib['src']
        tds = tree.xpath('//div[@class="bottom_view"]/table//td')

        prof_cd = int(search("Id={:w}", photo_url).fixed[0])

        name = satinize(tds[0].text)
        department_name = satinize(tds[1].text)
        email = satinize(tds[2].text)
        homepage = satinize(tds[3].text)
        lab = satinize(tds[4].text)
        tel = satinize(tds[5].text)
        meeting = satinize(tds[6].text)

        ret = {
            'photo_url' : photo_url,
            'prof_cd' : prof_cd,
            'name' : name,
            'department_name' : department_name,
            'email' : email,
            'homepage' : homepage,
            'lab' : lab,
            'tel' : tel,
            'metting' : meeting
        }

        log.debug(ret)
        return ret

    def parse_general_first_cd_list(self, raw_html: str) -> GeneratorType:
        """
        교양과목의 첫번째 분류를 파싱합니다.
        """
        assert raw_html != ""
        tree = self.init_tree(raw_html)

        options = tree.xpath('//select[@name="col"]/option')
        if not options:
            yield from []

        for op in options:
            ret = {
                'name' : op.text.strip(),
                'general_first_cd' : op.attrib['value'].strip()
            }
            log.debug(ret)
            yield ret

    def parse_general_second_cd_list(self, raw_html: str) -> GeneratorType:
        """
        교양과목의 두번째 분류를 파싱합니다. (학과검색과 유사)
        """

        generals = SugangRegexr.regex_general_types(raw_html)
        if not generals:
            yield from []  # generals 없는 경우 대응

        # 결과가 없으면 이 문장은 자동으로 넘어가므로 굳이 if 문이 필요 없다.
        for d in generals:
            general_second_cd = d[0].strip()
            name = d[1].strip()

            log.debug("name=%s, general_second_cd=%s" % (name, general_second_cd))

            yield {
                'general_second_cd': general_second_cd,
                'name': name
            }

