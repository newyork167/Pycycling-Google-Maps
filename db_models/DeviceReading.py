from tortoise.models import Model
from tortoise import fields

class DeviceReading(Model):
    id = fields.IntField(pk=True)
    device = fields.ForeignKeyField('models.Device', related_name='readings')
    device_reading_type = fields.ForeignKeyField('models.DeviceReadingType', related_name='readings')
    value = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device}: {self.device_reading_type} = {self.value}"
