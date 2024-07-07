from bleak import BleakClient

from devices.TrainingDevice import TrainingDevice
from pycycling.heart_rate_service import HeartRateService
from pycycling.battery_service import BatteryService

class PolarHRMonitor(TrainingDevice):
    def __init__(self, client: BleakClient, pycycling_client: HeartRateService):
        super().__init__(client, pycycling_client)

    async def on_connect(self):
        await self.pycycling_client.enable_hr_measurement_notifications()

    async def on_disconnect(self):
        await self.pycycling_client.disable_hr_measurement_notifications()
        await self.client.disconnect()

    async def setup_page_handler(self, page_handler: callable):
        self.pycycling_client.set_hr_measurement_handler(page_handler)
        await self.pycycling_client.enable_hr_measurement_notifications()
        await self.check_hr_battery()

    async def check_hr_battery(self):
        battery_service = BatteryService(self.client)
        battery_level = await battery_service.get_battery_level()

        return battery_level
