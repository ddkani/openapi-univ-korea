import logging

from kuapi.models.sugang import Colleage, Department, CourseTimetable, Course, Professor
from kuapi.enums.sugang import Term, Campus, Week, Complition

log = logging.getLogger(__name__)

class SugangBuilder:

    @staticmethod
    def build_colleage(year:int, term: Term, name: str, col_cd: str, campus: Campus):
        assert isinstance(year, int)
        assert isinstance(term, Term)
        assert isinstance(col_cd, str)
        assert isinstance(campus, Campus)

        colleage, created = Colleage.objects.update_or_create(
            year=year, term=term.value, col_cd=col_cd, campus=campus.value,
            defaults={
                'name' : name
            }
        )
        if created: log.info("created: %s" % colleage)
        return colleage


    @staticmethod
    def build_department(colleage: Colleage, dept_cd: str, name: str):
        assert isinstance(colleage, Colleage)
        assert isinstance(dept_cd, str)
        assert isinstance(name, str)

        department, created = Department.objects.update_or_create(
            dept_cd=dept_cd, colleage=colleage,
            defaults={
                'name' : name
            }
        )
        if created: log.info("created: %s" % department)
        return department


    @staticmethod
    def build_course(department: Department, cour_cd: str, cour_cls: str, name: str, score: int,
                     complition_type: str, is_relative: bool, is_limited: bool, grad_cd: str,
                     professor: Professor=None):

        assert isinstance(department, Department)
        assert isinstance(cour_cd, str)
        assert isinstance(name, str)
        assert not professor or isinstance(professor, Professor)
        assert isinstance(score, int)
        assert isinstance(complition_type, str)
        assert isinstance(is_relative, bool)
        assert isinstance(is_limited, bool)
        assert isinstance(cour_cls, str)
        assert isinstance(grad_cd, str)

        course, created = Course.objects.update_or_create(
            department=department, cour_cd=cour_cd,
            defaults={
                'name' : name,
                'professor' : professor,
                'score' : score,
                'complition_type' : complition_type,
                'is_relative' : is_relative,
                'is_limited' : is_limited,
                'cour_cls' : cour_cls,
                'grad_cd' : grad_cd
            }
        )
        if created: log.debug("created %s" % course)
        return course


    @staticmethod
    def build_course_timetable(course: Course, timetable_meta: tuple):
        assert isinstance(course, Course)
        assert isinstance(timetable_meta, list)

        week = timetable_meta[0]
        start = timetable_meta[1][0]
        end = timetable_meta[1][1]
        location = timetable_meta[2]

        assert isinstance(week, Week)
        assert isinstance(start, int) and isinstance(end, int)
        assert isinstance(location, str)

        ## each timetable
        ## Week, (start, end), 수업위치
        timetable, created = CourseTimetable.objects.update_or_create(
            course=course, time_start=start, time_end=end,
            defaults={
                'location' : location,
                'duration' : end - start + 1
            }
        )
        if created: log.debug("created %s" % timetable)
        return timetable


    @staticmethod
    def build_professor(prof_cd: int, department_name:str=None, image:bytes=None,
                        name:str=None, email:str=None, lab:str=None, phone:str=None, homepage:str=None):

        ## pass assertion

        professor, created = Professor.objects.update_or_create(
            prof_cd=prof_cd,
            defaults={
                'department_name' : department_name,
                'image' : image,
                'name' : name,
                'email' : email,
                'lab' : lab,
                'phone' : phone,
                'homepage' : homepage
            }
        )
        if created: log.debug('created %s' % professor)
        return professor
