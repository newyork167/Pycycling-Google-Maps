from tortoise.models import Model
from tortoise import fields

class DeviceReadingType(Model):
    id = fields.IntField(pk=True)
    type = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.type