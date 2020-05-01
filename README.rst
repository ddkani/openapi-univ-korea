=====
openapi-univ-korea
=====

고려대학교 통합 API 지원을 위한 패키지입니다.


패키지 적용
-----------

1. "kuapi" 패키지를 settings 파일의 INSTALLED_APPS 에 설정합니다.

    INSTALLED_APPS = [
        ...
        'kuapi',
    ]

2. 데이터베이스를 마이그래이션합니다.
    
    python3 manage.py migrate kuapi
    
3. 관려자(superuser) 를 생성하고, 관리자 URL을 등록합니다.

4. django admin 으로 접속하여 시간표 정보 및 사용자 인증 설정 등을 지정합니다.
