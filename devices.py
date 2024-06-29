from bleak import BleakClient

from pycycling.tacx_trainer_control import TacxTrainerControl
from pycycling.heart_rate_service import HeartRateService
from pycycling.battery_service import BatteryService


class TrainingDevice:
    def __init__(self, client: BleakClient, pycycling_client: TacxTrainerControl or HeartRateService): # type: ignore
        self.client = client
        self.pycycling_client = pycycling_client

    async def on_connect(self):
        pass

    async def on_disconnect(self):
        pass


class TacxTrainer(TrainingDevice):
    def __init__(self, client: BleakClient, pycycling_client: TacxTrainerControl):
        super().__init__(client, pycycling_client)
        self.bleak_client = client
        self.pycycling_client = pycycling_client

    async def on_connect(self):
        await self.pycycling_client.enable_fec_notifications()

    async def on_disconnect(self):
        await self.pycycling_client.disable_fec_notifications()
        await self.client.disconnect()

    async def setup_trainer(self, trainer_page_handler: callable):
        self.pycycling_client.set_specific_trainer_data_page_handler(trainer_page_handler)
        self.pycycling_client.set_general_fe_data_page_handler(trainer_page_handler)
        await self.pycycling_client.enable_fec_notifications()


class PolarHRMonitor(TrainingDevice):
    def __init__(self, client: BleakClient, pycycling_client: HeartRateService):
        super().__init__(client, pycycling_client)

    async def on_connect(self):
        await self.pycycling_client.enable_hr_measurement_notifications()

    async def on_disconnect(self):
        await self.pycycling_client.disable_hr_measurement_notifications()
        await self.client.disconnect()

    async def setup_hr_monitor(self, heart_rate_page_handler: callable):
        self.pycycling_client.set_hr_measurement_handler(heart_rate_page_handler)
        await self.pycycling_client.enable_hr_measurement_notifications()
        await self.check_hr_battery()

    async def check_hr_battery(self):
        battery_service = BatteryService(self.client)
        battery_level = await battery_service.get_battery_level()
        
        return battery_level
