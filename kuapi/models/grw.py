from django.db.models import Model, CASCADE

from django.db.models import ForeignKey
from django.db.models import \
    CharField, SmallIntegerField, IntegerField, BigAutoField, TextField, \
    BinaryField, DecimalField

from kuapi.config import MAX_LEN_DEFFIELD, MAX_LEN_MIDFIELD, MAX_LEN_SMFIELD, MAX_IMAGE_SIZE

class IdModelMixin(Model):
    """
    객체의 고유 ID값을 지정하는 추상 클래스입니다.
    """
    id = BigAutoField(primary_key=True, auto_created=True, editable=False)

    class Meta:
        abstract = True


class Bulletin(IdModelMixin, Model):
    """
    게시판 종류입니다.
    """

    name = CharField(null=False, max_length=MAX_LEN_SMFIELD)
    "게시판 이름입니다."

    kind_id = IntegerField(null=False)
    "게시판 고유 아이디입니다."


class Notice(IdModelMixin, Model):

    bulletin = ForeignKey(Bulletin, null=False,
                          related_name="notices", on_delete=CASCADE)

    # 작성자, 승인자,  승인일자, 게시대상, 분류, 시작일시, 종료일시, 제목, 게시형태(긴급?)
    # 작성자 정보 => 리스트에서는 아이디까지 알려줍니다.


class NoticeAttachment(IdModelMixin, Model):
    notice = ForeignKey(Notice, null=False,
                        related_name="attachments", on_delete=CASCADE)

    name = CharField(null=True, max_length=MAX_LEN_MIDFIELD)
    """첨부파일 이름입니다."""
    file = BinaryField(null=True, editable=True)
    """첨부파일 데이터입니다."""

