import re
import logging

from kuapi.enums.sugang import Week

## regex 로 처리해야하는 데이터가 많을 경우, 파일의 효용성을 위해 별도로 분리하였음.
## 또한 regex expression 을 경우에 따라 컴파일하여 쓰는것이 바람직함.

log = logging.getLogger(__name__)

## -----------------------------------------------------------------

RG_DEPARTMENTS = r'el\.style\.color = "black";\s*el.selected = .+?;\s*el\.value ="(.+?)";\s*el.text = "(.+?)";'
RG_GENERAL_TYPES = r'el\.style\.color = "black";\s*el\.value ="(.+?)";\s*el.text = "(.+?)";'
RG_LECTURE_TIME_LOCATION = r"([월화수목금])\((.+?)\)\s(.+?)$"
RG_LECTURE_TIME_LOCATION_2 = r"([월화수목금])\((.+?)\)"

## -----------------------------------------------------------------

rg_lecture_time_location = re.compile(RG_LECTURE_TIME_LOCATION)
rg_lecture_time_location2 = re.compile(RG_LECTURE_TIME_LOCATION_2)
rg_departments = re.compile(RG_DEPARTMENTS)
rg_general_types = re.compile(RG_GENERAL_TYPES)


class SugangRegexr:

    @staticmethod
    def regex_departments(raw: str) -> list:
        assert isinstance(raw, str)
        assert raw != ""

        match = rg_departments.findall(raw)
        if match is None:
            _message = 'regex_departments not match : %s' % raw
            log.warning(_message)
            return []

        return match


    @staticmethod
    def regex_general_types(raw: str) -> list:
        assert isinstance(raw, str)
        assert raw != ""

        match = rg_general_types.findall(raw)
        if match is None:
            _message = 'regex_general_types not match : %s' % raw
            log.warning(_message)
            return []

        return match


    @staticmethod
    def regex_course_timetable(raw: str) -> tuple:
        assert isinstance(raw, str)
        assert raw != ""

        if raw == '미정':
            return tuple()

        def build_time(t: str):
            _t = t.split('-')
            return (int(_t[0]), int(_t[0])) if len(_t) == 1 else (int(_t[0]), int(_t[1]))

        _match_1 = rg_lecture_time_location.match(raw)
        _match_2 = rg_lecture_time_location2.match(raw)

        if not _match_1 and not _match_2:
            log.warning('regex_course_timetable error : %s' % raw)
            return tuple()

        # match 1 "([월화수목금])\((.+?)\)\s(.+?)$ "
        if _match_1:
            groups = _match_1.groups()
            week = Week(groups[0])
            time = build_time(groups[1])
            loc = groups[2]

        # match 2 "([월화수목금])\((.+?)\)"
        else:
            groups = _match_2.groups()
            week = Week(groups[0])
            time = build_time(groups[1])
            loc = None

        return week, time, loc




