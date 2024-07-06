import asyncio

import tkinter as tk
from bleak import BleakClient, BleakScanner, BLEDevice

from Models.TrainingPlan import TrainingPlan, SegmentDuration
from devices import TacxTrainer, PolarHRMonitor, TrainingDevice

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

class App:
    def __init__(self):
        self.window: tk.Tk = tk.Tk()
        self.pycycling_clients = []

        self.current_cadence_label = None
        self.current_speed_label = None
        self.current_hr_label = None

    async def setup_tkinter_window(self):
        # Setup tkinter window
        self.window.title("Pycycling")
        self.window.geometry("800x600")

        tk.Label(text="Trainer Trackr 0.1").pack()

        tk.Button(
            text="Click me!",
            width=25,
            height=5,
            bg="blue",
            fg="yellow",
        ).pack()

        while True:
            self.window.update()

    async def main(self):
        await self.setup_tkinter_window()
        await self.run()

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

    async def run(self):
        # TODO(cody): Make this a class, for now just making it a basic function for the final
        async with BleakClient(TACX_TRAINER_CONTROL_UUID) as trainer_client, BleakClient(POLAR_HR_CONTROL_POINT_UUID) as polar_client:
            try:
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
            finally:
                # Either the connection will fail, where the client list will be empty
                # or a training event will fail, and we still need to disconnect
                await self.disconnect_clients()

    async def test_plan(self) -> TrainingPlan:
        # Check for saved training plans
        test_plan = await TrainingPlan.filter(name__contains='test plan').first()

        if not test_plan:
            test_plan = await TrainingPlan.create(name='test plan')
            test_plan.segments.add(SegmentDuration(name='Warmup', duration=10, resistance=20))
            test_plan.segments.add(SegmentDuration(name='Uphill 1', duration=10, resistance=40))
            test_plan.segments.add(SegmentDuration(name='Downhill 1', duration=10, resistance=30))
            test_plan.segments.add(SegmentDuration(name='Uphill 2', duration=10, resistance=50))
            test_plan.segments.add(SegmentDuration(name='Downhill 2', duration=10, resistance=30))
            test_plan.segments.add(SegmentDuration(name='Uphill 3', duration=10, resistance=60))
            test_plan.segments.add(SegmentDuration(name='Downhill 3', duration=10, resistance=30))
            test_plan.segments.add(SegmentDuration(name='Cooldown', duration=10, resistance=20))
            await test_plan.save()

        for segment in test_plan.segments:
            print(segment)

        return test_plan



if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)

    app = App()

    loop = asyncio.get_event_loop()
    loop.create_task(app.run())
    loop.create_task(BluetoothHandler().discover_bluetooth_devices())
    loop.run_forever()
