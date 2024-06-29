from tortoise.models import Model
from tortoise import fields

class Device(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    uuid = fields.UUIDField()
    device_type = fields.ForeignKeyField('models.DeviceType', related_name='devices')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name