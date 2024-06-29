import asyncio
from bleak import BleakClient, BleakScanner
from devices import TacxTrainer, PolarHRMonitor

from pycycling.tacx_trainer_control import TacxTrainerControl
from pycycling.heart_rate_service import HeartRateService
from pycycling.battery_service import BatteryService


# TODO(cody): Add ability to select trainer and HR monitor from list of available devices
POLAR_HR_CONTROL_POINT_UUID = "3E4F72D6-D632-1157-0BCD-5B5C673653AE"
TACX_TRAINER_CONTROL_UUID = "8B9E4197-3BA0-39EF-1290-F82450B4DC00"


async def discover_bluetooth_devices():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)


async def run():
    async with BleakClient(TACX_TRAINER_CONTROL_UUID) as trainer_client, BleakClient(POLAR_HR_CONTROL_POINT_UUID) as polar_client:
        clients = []
        pycycling_clients = []

        async def connect_clients() -> []:
            await trainer_client.is_connected()
            await polar_client.is_connected()

            trainer_device, hr_device = TacxTrainer(trainer_client, trainer), PolarHRMonitor(polar_client, hr_device)
            await trainer_device.on_connect()
            await hr_device.on_connect()

            # return [TacxTrainerControl(trainer_client), HeartRateService(polar_client)]
            return trainer_device, hr_device

        async def disconnect_clients():
            for pycycling_client in pycycling_clients:
                await pycycling_client.on_disconnect()

        def trainer_page_handler(data):
            print(data)

        def heart_rate_page_handler(data):
            print(data)

        trainer, hr_device = await connect_clients()
        await trainer.setup_trainer(trainer_page_handler=trainer_page_handler)
        await hr_device.setup_hr_monitor(heart_rate_page_handler=heart_rate_page_handler)

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
    loop.run_until_complete(discover_bluetooth_devices())
    loop.run_until_complete(run())
