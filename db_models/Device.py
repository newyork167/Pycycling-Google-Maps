from tortoise.models import Model
from tortoise import fields

from db_models.DeviceType import DeviceType
from devices.TacxTrainer import TacxTrainer
from devices.TrainingDevice import TrainingDevice


class Device(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    uuid = fields.UUIDField()
    device_type = fields.ForeignKeyField('models.DeviceType', related_name='devices')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name

class DeviceFactory:
    @staticmethod
    async def generate(training_device: TrainingDevice) -> Device:
        # Check for saved device
        device = await Device.filter(uuid__contains=str(training_device.client.address)).first().prefetch_related("devices")

        if not device:
            print(f'Creating device: {training_device.client.address}')
            device_type_name = 'Trainer' if isinstance(training_device, TacxTrainer) else 'HR'

            device_type = await DeviceType.filter(name__contains=device_type_name).first()
            if not device_type:
                device_type = await DeviceType.create(name=device_type_name)
                await device_type.save()

            device = await Device.create(name="test plan")
            device.device_type = device_type
            await device.save()

        return device