import asyncio

from tkinter import Tk, Button
from bleak import BleakClient, BleakScanner, BLEDevice
from tortoise import Tortoise
from tortoise.query_utils import Prefetch

from db_models.TrainingPlan import TrainingPlan, SegmentDuration
from devices import TacxTrainer, PolarHRMonitor, TrainingDevice
from gui.AsyncTk import AsyncTk

from pycycling.tacx_trainer_control import TacxTrainerControl
from pycycling.heart_rate_service import HeartRateService


# TODO(cody): Add ability to select trainer and HR monitor from list of available devices
POLAR_HR_CONTROL_POINT_UUID = "3E4F72D6-D632-1157-0BCD-5B5C673653AE"
TACX_TRAINER_CONTROL_UUID = "8B9E4197-3BA0-39EF-1290-F82450B4DC00"


class BluetoothHandler:
    devices = []

    async def discover_bluetooth_devices(self) -> None:
        self.devices = await BleakScanner.discover()

        for d in self.devices:
            print(d)

class App(AsyncTk):
    def __init__(self):
        super().__init__()

        self.pycycling_clients = []

        self.current_cadence_label = None
        self.current_speed_label = None
        self.current_hr_label = None
        self.bluetooth_handler = BluetoothHandler()

        self.create_interface()
        self.runners.append(self.start())
        self.runners.append(self.setup_tortoise())
        self.runners.append(self.bluetooth_handler.discover_bluetooth_devices())

    def create_interface(self):
        Button(master=self,
               text="Get Test Plan!",
               width=25,
               height=5,
               command=lambda: self.add_button_coro(self.test_plan())
        ).pack()

        Button(master=self,
               text='Quit',
               command=self.stop
        ).pack()

    async def setup_tortoise(self):
        await Tortoise.init(
            db_url='sqlite://db.sqlite3',
            modules={'models': ['models']}
        )
        # Generate the schema
        await Tortoise.generate_schemas()

    async def connect_clients(self, trainer_client: BleakClient, polar_client: BleakClient) -> list[TrainingDevice]:
        # Generalize later
        clients = []

        await trainer_client.is_connected()
        await polar_client.is_connected()

        clients += [TacxTrainer(trainer_client, TacxTrainerControl(trainer_client)),
                    PolarHRMonitor(polar_client, HeartRateService(polar_client))]
        for client in clients:
            await client.on_connect()

        return clients

    async def disconnect_clients(self):
        for pycycling_client in self.pycycling_clients:
            await pycycling_client.on_disconnect()

    def trainer_page_handler(self, data):
        print(data)

    def heart_rate_page_handler(self, data):
        print(data)

        if self.current_hr_label:
            self.current_hr_label.config(text=data['heart_rate'])

    async def start(self):
        try:
            async with BleakClient(TACX_TRAINER_CONTROL_UUID) as trainer_client, BleakClient(POLAR_HR_CONTROL_POINT_UUID) as polar_client:
                trainer, hr_device = await self.connect_clients(trainer_client=trainer_client, polar_client=polar_client)
                self.pycycling_clients += [trainer, hr_device]

                await trainer.setup_page_handler(page_handler=self.trainer_page_handler)
                await hr_device.setup_page_handler(page_handler=self.heart_rate_page_handler)

                training_plan = await self.test_plan()

                for segment in training_plan.segments:
                    await trainer.pycycling_client.set_basic_resistance(segment.resistance)
                    await asyncio.sleep(segment.duration)
        except Exception as ex:
            print(ex)

    async def test_plan(self) -> TrainingPlan:
        # Check for saved training plans
        test_plan = await TrainingPlan.filter(name__contains='test plan').first().prefetch_related("segments")

        if not test_plan:
            print('Creating test plan')

            test_plan = await TrainingPlan.create(name="test plan")
            await SegmentDuration.create(name="Warmup", duration=10, resistance=20, training_plan=test_plan)
            await SegmentDuration.create(name="Uphill 1", duration=10, resistance=40, training_plan=test_plan)
            await SegmentDuration.create(name="Downhill 1", duration=10, resistance=30, training_plan=test_plan)
            await SegmentDuration.create(name="Uphill 2", duration=10, resistance=40, training_plan=test_plan)
            await SegmentDuration.create(name="Downhill 2", duration=10, resistance=30, training_plan=test_plan)
            await SegmentDuration.create(name="Cooldown", duration=10, resistance=20, training_plan=test_plan)
            await test_plan.save()

            test_plan = await TrainingPlan.first().prefetch_related("segments")

        for segment in test_plan.segments:
            print(segment)

        return test_plan


async def main():
    app = App()
    await app.run()


if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)

    asyncio.run(main())
