from enum import Enum

## Enum 데이터 관리
# 이름 / 실제값(DB저장) / 사용자표기용

# serialize 실제값 또는 Enum객체 => 사용자표기용
# peek EnumClass(value)
# parse 특정 사이트에서 가져온 값을 enum으로 변환


class Campus(Enum):
    """
    캠퍼스 구분
    """

    seoul = 1
    "안암캠퍼스"
    sejong = 2
    "세종캠퍼스"

    @staticmethod
    def serialize(r) -> str:
        if r == 1:
            return '서울'
        elif r == 2:
            return '세종'
        else:
            raise ValueError(r)

    @staticmethod
    def parse(r):
        if r == "서울":
            return Campus.seoul
        elif r == "세종":
            return Campus.sejong
        else:
            raise ValueError(r)

class Term(Enum):
    """
    학기 구분
    """

    spring = '1R'
    "1학기 (1R)"
    summer = '1S'
    "계절수업(여름) 1S"
    fall = '2R'
    "2학기  2R"
    winter = '2W'
    "계절수업(겨울) 2W"
    inter = 'SC'
    "국제교류  SC"

    @staticmethod
    def parse(r):
        if r == '1학기':
            return Term.spring
        elif r == '계절학기(여름)':
            return Term.summer
        elif r == '2학기':
            return Term.fall
        elif r == '계절학기(겨울)':
            return Term.winter
        else:
            raise ValueError(r)

    @staticmethod
    def serialize(r):
        if r == '1R':
            return '1학기'
        elif r == '1S':
            return '계절수업(여름)'
        elif r == '2R':
            return '2학기'
        elif r == '2W':
            return '계절수업(겨울)'
        elif r == 'SC':
            return '국제교류'
        else:
            raise ValueError(r)

class Week(Enum):
    monday = "월"
    tuesday = "화"
    wednesday = "수"
    thursday = "목"
    friday = "금"
    saturday = "토"
    sunday = "일"

class Complition(Enum):
    # 다 정리된 파일이 있었는데 어디 갔더라...
    pass