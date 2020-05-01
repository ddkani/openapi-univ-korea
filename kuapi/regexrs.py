import re
import logging

from kuapi.enums.sugang import Week

## regex 로 처리해야하는 데이터가 많을 경우, 파일의 효용성을 위해 별도로 분리하였음.
## 또한 regex expression 을 경우에 따라 컴파일하여 쓰는것이 바람직함.

log = logging.getLogger(__name__)

## -----------------------------------------------------------------

RG_LECTURE_TIME_LOCATION = r"([월화수목금])\((.+?)\)\s(.+?)$"

## -----------------------------------------------------------------

rg_lecture_time_location = re.compile(RG_LECTURE_TIME_LOCATION)




class SugangRegexr:

    @staticmethod
    def regex_course_timetable(raw: str) -> tuple:
        assert not isinstance(raw, str)
        assert raw != ""

        def build_time(t: str):
            _t = t.split('-')
            return (int(_t[0]), int(_t[0])) if len(_t) is 1 else (int(_t[0]), int(_t[1]))

        match = rg_lecture_time_location.match(raw)
        if match is None:
            log.warning('regex_course_timetable error : %s' % raw)
            return None

        groups = match.groups()

        # match 1 " ([월화수목금])\((.+?)\)\s(.+?)$ "
        if groups[0] is not None:
            week = Week(groups[0])
            time = build_time(groups[1])
            loc = groups[2]

        # match 2 " ([월화수목금])\((.+?)\) "
        else:
            week = Week(groups[3])
            time = build_time(groups[4])
            loc = None

        return week, time, loc




