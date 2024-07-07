from tortoise.models import Model
from tortoise import fields

class Session(Model):
    id = fields.IntField(pk=True)
    start_time = fields.DatetimeField(auto_now_add=True)
    end_time = fields.DatetimeField(null=True)

    def __str__(self):
        return f"{self.id}: {self.start_time} - {self.end_time}"
