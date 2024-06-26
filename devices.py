from bleak import BleakClient

from pycycling.tacx_trainer_control import TacxTrainerControl
from pycycling.heart_rate_service import HeartRateService
from pycycling.battery_service import BatteryService


class TrainingDevice:
    async def __init__(self, client: BleakClient, pycycling_client: TacxTrainerControl or HeartRateService): # type: ignore
        self.client = client
        self.pycycling_client = pycycling_client

class TacxTrainer(TrainingDevice):
    async def __init__(self, client: BleakClient, pycycling_client: TacxTrainerControl or HeartRateService): # type: ignore
        super().__init__(client, pycycling_client)

    async def connect(self):
        await self.pycycling_client.enable_fec_notifications()

    async def disconnect(self):
        await self.pycycling_client.disable_fec_notifications()
        await self.client.disconnect()

class PolarHRMonitor(TrainingDevice):
    async def __init__(self, client: BleakClient, pycycling_client: TacxTrainerControl or HeartRateService): # type: ignore
        super().__init__(client, pycycling_client)

    async def connect(self):
        await self.pycycling_client.enable_hr_measurement_notifications()

    async def disconnect(self):
        await self.pycycling_client.disable_hr_measurement_notifications()
        await self.client.disconnect()

    async def check_hr_battery(self):
        battery_service = BatteryService(self.client)
        battery_level = await battery_service.get_battery_level()
        
        return battery_level
