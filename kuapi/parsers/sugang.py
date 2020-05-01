import logging

import lxml.html
from lxml.html import HtmlElement
from parse import parse, search, findall

from types import GeneratorType

from kuapi.enums.sugang import Campus, Term, Week
from kuapi.regexrs import SugangRegexr

log = logging.getLogger(__name__)


# Warning: support from 3.8 - typeddict



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


        for _opt in tree.xpath("//select[@name = 'col' and @id='col']//option[position() > 1]"): # type: HtmlElement
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

        _cds = list(findall('el.value ="{:w}"', raw_html))
        _names = list(findall('el.text = "{:w}"', raw_html))

        assert len(_cds) == len(_names) # 갯수가 다를경우 오류
        assert _cds and _names # 존재하지 않을 경우 오류

        for _i in range(len(_cds)):
            _name = _names[_i].fixed[0].strip()
            _dept_cd = _cds[_i].fixed[0].strip()

            log.debug("name=%s, dept_cd=%s" % (_name, _dept_cd))

            yield {
                'dept_cd' : _dept_cd,
                'name' : _name
            }


    def parse_courses(self, raw_html: str) -> GeneratorType:
        """
        강의 리스트를 파싱합니다.

        @param raw_html sugang.korea.ac.kr/lecture/LecMajorSub.jsp
        """

        assert raw_html != ""
        tree = self.init_tree(raw_html)

        # 첫번째 테이블은 자료 주석이므로 실행하지 않음.
        for _lec in tree.xpath("//tr[position() > 1]"):
            tds = _lec.xpath("//td")

            # _campus = Campus.parse(tds[0].text).value
            _cour_cd = tds[1].text
            _cls = int(tds[2].text)
            ## 이수구분
            _name = tds[4].text.strip()
            ## 교수이름 - 상세정보에서 가져오기
            _score = parse("{time:w}(  {credit:w})", tds[6].text.trim()).named['score']
            ## 강의시간 / 강의실 - 상세정보에서 가져오기

            log.debug("name=%s, cour_cd=%s, cls=%s, score=%s" % (
                _name, _cour_cd, _cls, _score
            ))

            yield {
                'name' : _name,
                'cour_cd' : _cour_cd,
                'cls' : _cls,
                'score' : _score
            }


    def parse_course(self, raw_html: str) -> dict:
        """
        강의 상세정보를 파싱합니다.

        @param raw_html infodepot.korea.ac.kr/lecture1/lecsubjectPlanView.jsp
        """
        assert raw_html != ""
        tree = self.init_tree(raw_html)

        basics = tree.xpath('//form[@name="form1"]/input')
        tds = tree.xpath('//div[@class="tbl_view]/table//td')

        _time = tds[0].text
        timetables = list()

        if _time:
            for _t in _time.split('\n'):
                _p = SugangRegexr.regex_course_timetable(_t)
                if _p: timetables.append(_p)

        return {
            'year' : int(basics[2].text),
            'term' : Term(basics[3].text),
            'dept_cd' : basics[4].text,
            'cour_cd' : basics[5].text,
            'grad_cd' : basics[6].text, ## ?
            'cour_cls' : int(basics[7].text),
            'name' : basics[8].text,
            'col_cd' : basics[9].text,
            'timetables' : timetables
        }


    def parse_professor(self, raw_html: str) -> dict:
        """
        교수 정보를 파싱합니다.

        @param raw_html infodepot.korea.ac.kr/lecture1/lecsubjectPlanView.jsp
        """
        assert raw_html != ""
        tree = self.init_tree(raw_html)

        photo_url = tree.xpath('//span[@class="photo"]/img')[0].attrib('src')
        tds = tree.xpath('//div[@class="bottom_view]/table//td')

        prof_cd = int(search("Id={:w}", photo_url).fixed[0])

        name = tds[0].text
        department_name = tds[1].text
        email = tds[2].text
        homepage = tds[3].text
        lab = tds[4].text
        tel = tds[5].text
        meeting = tds[6].text

        return {
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