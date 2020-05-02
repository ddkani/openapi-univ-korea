from datetime import datetime

from django.db.models import Model, CASCADE

from django.db.models import ForeignKey
from django.db.models import OneToOneField
from django.db.models import \
    CharField, SmallIntegerField, UUIDField, IntegerField, EmailField, AutoField, BigAutoField, TextField, \
    BinaryField

from kuapi.enums.sugang import Campus, Term, Week
from kuapi.config import MAX_LEN_DEFFIELD, MAX_LEN_MIDFIELD, MAX_LEN_SMFIELD, MAX_IMAGE_SIZE

# django.models.signal => 작업 전 / 작업 후 경과를 보고. 여기서 작업을 중지 할 수 없음.
# create / save 등 매서드 재정의 => 작업을 수행하기 전 검증하고, 중지할 수 있음.


class IdModelMixin(Model):
    """
    객체의 고유 ID값을 지정하는 추상 클래스입니다.
    """
    id = BigAutoField(primary_key=True, auto_created=True, editable=False)

    class Meta:
        abstract = True


class Colleage(Model):
    year = IntegerField(null=False)
    "년도 - 단과대학은 시기에 따라 변경될 수 있음"

    term = CharField(
        null=False, max_length=2,
        choices=[(i.name, i.value) for i in Term]
    )
    "학기 - 단과대학은 시기에 따라 변경될 수 있음"

    name = CharField(
        null=True, max_length=MAX_LEN_MIDFIELD
    )
    "단과대학 이름"


    col_cd = CharField(
        null=True, max_length=MAX_LEN_SMFIELD
    )
    "단과대학 고유코드 format: %04d"

    campus = SmallIntegerField(
        # TODO: automatic enum choices
        null=True, choices=[(i.name, i.value) for i in Campus]
    )
    "캠퍼스 - 안암캠퍼스 / 세종캠퍼스"

    @property
    def is_exist(self):
        return Colleage.objects.filter(
            year=self.year, term=self.term, col_cd=self.col_cd).exists()

    def __str__(self):
        return "%s-%s (%s) %s" % (
            self.year, Term.serialize(self.term), Campus.serialize(self.campus),
            self.name
        )



class Department(IdModelMixin, Model):

    colleage = ForeignKey(Colleage, null=False,
        related_name='departments', on_delete=CASCADE
    )

    dept_cd = CharField(
        null=True, max_length=MAX_LEN_SMFIELD  # nnnn
    )
    name = CharField(
        null=True, max_length=MAX_LEN_MIDFIELD
    )

    @property
    def year(self):
        return self.colleage.year

    @property
    def term(self):
        return self.colleage.term

    @property
    def campus(self):
        return self.colleage.campus

    @property
    def is_exist(self):
        # name까지 검즐할 필요는 없다.
        return Department.objects.filter(colleage=self.colleage, dept_cd=self.dept_cd).exists()


    def __str__(self):
        return "%s" % self.name


# year, term 수동설정할 경우 (colleage)
# 년도, 학기 선택 -> 학기를 나눈다음 가장 최신부터 ordering
# 강의명, 교수명, 과목코드로 검색
# http://klue.kr/note/main/%EC%BB%B4%ED%93%A8%ED%84%B0


class Professor(IdModelMixin, Model):
    prof_cd = IntegerField(
        null=True, unique=True,
    )

    department_name = CharField(null=True, max_length=MAX_LEN_MIDFIELD)

    name = CharField(null=False, max_length=MAX_LEN_MIDFIELD)
    email = CharField(null=True, max_length=MAX_LEN_MIDFIELD)
    lab = CharField(null=True, max_length=MAX_LEN_DEFFIELD)
    phone = CharField(null=True, max_length=MAX_LEN_DEFFIELD)
    homepage = TextField(null=True)

    image = BinaryField(null=True, editable=True, max_length=MAX_IMAGE_SIZE)

    # 면담시간 -> 필요할까?
    # meeting_time = CharField(max_length=MAX_CHAR_MIDFIELD)

    """
    ! 다행히도 교수의 고유 ID를 출력할 수 있다...!
    단, 교수의 학과정보(학과이름)은 최신을 유지해야 하므로 가장 최근의 CourseKlass에 속한 걸 찾아서
    해당 이름을 출력해주면 좋겠다.
    => 추후 성적조회 서비스
    """

    def __str__(self):
        return "%s: %s[%s]" % (self.prof_cd, self.name, self.department_name)


## TODO: Course / cls -> 별도의 테이블이 아닌 하나로 확장
# 사유: 학수번호, 이름이 동일한 경우가 있으므로 unique -> 학수번호 + 분반 조합으로 처리하여야 함.


class Course(IdModelMixin, Model):
    department = ForeignKey(Department, null=False,
                            related_name="courses", on_delete=CASCADE
                            )

    cour_cd = CharField(  # 학수번호
        null=True, max_length=MAX_LEN_SMFIELD
    )
    cour_cls = CharField(null=False, max_length=2)  # 분반 실제번호

    name = CharField(
        null=True, max_length=MAX_LEN_DEFFIELD
    )

    grad_cd = CharField( # unknown field
        null=True, max_length=MAX_LEN_SMFIELD
    )

    professor = ForeignKey(Professor, null=True,
                           related_name='professor', on_delete=CASCADE,
                           )

    score = SmallIntegerField(null=True)  # 학점

    # 정확한 코드의 테이블을 찾을 수 없으므로 우선 charfield로 대체합니다.
    complition_type = CharField(null=True, max_length=MAX_LEN_SMFIELD)  # 이수구분

    is_relative = SmallIntegerField(null=True)  # 상대평가 과목
    is_limited = SmallIntegerField(null=True)  # 인원제한 과목

    @property
    def is_exist(self):
        return Course.objects.filter(
            department=self.department, cour_cd=self.cour_cd
        ).exists()

    @property
    def colleage(self):
        return self.department.colleage

    @property
    def year(self):
        return self.colleage.year

    @property
    def term(self):
        return self.colleage.term

    @property
    def campus(self):
        return self.colleage.campus

    def save(self, **kwargs):
        return super().save(**kwargs)

    def __str__(self):
        return "[%s-%s] %s" % (
            self.cour_cd, self.cour_cls, self.name
        )


class CourseTimetable(IdModelMixin, Model):
    course = ForeignKey(Course, null=True,
                        related_name="timetables", on_delete=CASCADE
                        )

    weekend = CharField(
        null=False, choices=[(i.name, i.value) for i in Week],
        max_length=2
    )
    # 검색할 때 범위를 만들어서 설정할 것임.
    # TODO: 한 주일에 단 한번의 연속된 수업이 있다고 가정할 경우로 작성,
    # 그렇지 않다면 각 정보가 하나씩으로 다시 재정의되어야 함.
    # TODO: 클라이언트 상에서 보기 쉽게 변환은 Serializer에서 작성하도록 합니다.
    time_start = SmallIntegerField(null=True)
    time_end = SmallIntegerField(null=True)
    duration = SmallIntegerField(null=True)

    # TODO: 시간표 시간 실제시간으로 변환하여 혼용(멀티캠퍼스 지원)대비 -> 추후작성예정!

    location = CharField(null=True, max_length=MAX_LEN_MIDFIELD)

    def __str__(self):
        return '%s_%s[%s-%s]' % (self.course.name, self.weekend, self.time_start, self.time_end)