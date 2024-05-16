import asyncio
from bleak import BleakClient

from pycycling.tacx_trainer_control import TacxTrainerControl
from pycycling.heart_rate_service import HeartRateService
from pycycling.battery_service import BatteryService

POLAR_HR_CONTROL_POINT_UUID = "3E4F72D6-D632-1157-0BCD-5B5C673653AE"
TACX_TRAINER_CONTROL_UUID = "8B9E4197-3BA0-39EF-1290-F82450B4DC00"


class TrainingDevice:
    def __init__(self, client: BleakClient, pycycling_client: TacxTrainerControl or HeartRateService):
        self.client = client
        self.pycycling_client = pycycling_client

class TacxTrainer(TrainingDevice):
    async def connect(self):
        await self.pycycling_client.enable_fec_notifications()

    async def disconnect(self):
        await self.pycycling_client.disable_fec_notifications()
        await self.client.disconnect()

class PolarHRMonitor(TrainingDevice):
    async def connect(self):
        await self.pycycling_client.enable_hr_measurement_notifications()

    async def disconnect(self):
        await self.pycycling_client.disable_hr_measurement_notifications()
        await self.client.disconnect()


async def run():
    async with BleakClient(TACX_TRAINER_CONTROL_UUID) as trainer_client, BleakClient(POLAR_HR_CONTROL_POINT_UUID) as polar_client:
        clients = []
        pycycling_clients = []

        async def connect_clients() -> []:
            await trainer_client.is_connected()
            await polar_client.is_connected()

            clients = [trainer_client, polar_client]
            pycycling_clients = [TacxTrainerControl(trainer_client), HeartRateService(polar_client)]
            return pycycling_clients

        async def setup_trainer(trainer: TacxTrainerControl):
            trainer.set_specific_trainer_data_page_handler(trainer_page_handler)
            trainer.set_general_fe_data_page_handler(trainer_page_handler)
            await trainer.enable_fec_notifications()
        
        async def setup_hr_monitor(hr_monitor: HeartRateService, polar_client: BleakClient):
            hr_monitor.set_hr_measurement_handler(heart_rate_page_handler)
            await polar_hr.enable_hr_measurement_notifications()
            await check_hr_battery(polar_client)

        async def check_hr_battery(polar_client: BleakClient):
            battery_service = BatteryService(polar_client)
            battery_level = await battery_service.get_battery_level()
            print(f"HR battery is at {battery_level}%")

        async def disconnect_clients():
            for pycycling_client in pycycling_clients:
                if isinstance(pycycling_client, TacxTrainerControl):
                    await pycycling_client.disable_fec_notifications()
                elif isinstance(pycycling_client, HeartRateService):
                    await pycycling_client.disable_hr_measurement_notifications()

            for client in clients:
                if client.is_connected():
                    await client.disconnect()

        def trainer_page_handler(data):
            print(data)

        def heart_rate_page_handler(data):
            print(data)

        trainer, polar_hr = await connect_clients()
        # trainer = TacxTrainerControl(trainer_client)
        # polar_hr = HeartRateService(polar_client)

        await setup_trainer(trainer=trainer)
        await setup_hr_monitor(hr_monitor=polar_hr, polar_client=polar_client)

        await trainer.set_basic_resistance(20)
        await asyncio.sleep(5.0)
        await trainer.set_basic_resistance(40)
        await asyncio.sleep(5.0)

        await trainer.set_basic_resistance(80)
        await asyncio.sleep(5.0)

        await trainer.set_track_resistance(12, 0.004)
        await asyncio.sleep(5.0)

        await trainer.set_basic_resistance(20)

        await disconnect_clients()
        # await trainer.disable_fec_notifications()
        # await polar_hr.disable_hr_measurement_notifications()


if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
