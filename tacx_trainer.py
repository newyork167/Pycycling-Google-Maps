import asyncio
from bleak import BleakClient, BleakScanner
from devices import TacxTrainer, PolarHRMonitor

from pycycling.tacx_trainer_control import TacxTrainerControl
from pycycling.heart_rate_service import HeartRateService
from pycycling.battery_service import BatteryService


# TODO(cody): Add ability to select trainer and HR monitor from list of available devices
POLAR_HR_CONTROL_POINT_UUID = "3E4F72D6-D632-1157-0BCD-5B5C673653AE"
TACX_TRAINER_CONTROL_UUID = "8B9E4197-3BA0-39EF-1290-F82450B4DC00"
        

async def run():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)
    async with BleakClient(TACX_TRAINER_CONTROL_UUID) as trainer_client, BleakClient(POLAR_HR_CONTROL_POINT_UUID) as polar_client:
        clients = []
        pycycling_clients = []

        async def connect_clients() -> []:
            await trainer_client.is_connected()
            await polar_client.is_connected()

            clients = [trainer_client, polar_client]
            return [TacxTrainerControl(trainer_client), HeartRateService(polar_client)]

        async def setup_trainer(trainer: TacxTrainerControl):
            trainer.set_specific_trainer_data_page_handler(trainer_page_handler)
            trainer.set_general_fe_data_page_handler(trainer_page_handler)
            await trainer.enable_fec_notifications()
        
        async def setup_hr_monitor(hr_monitor: HeartRateService, polar_client: BleakClient):
            hr_monitor.set_hr_measurement_handler(heart_rate_page_handler)
            await polar_hr.enable_hr_measurement_notifications()
            await polar_client.check_hr_battery()

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


if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
