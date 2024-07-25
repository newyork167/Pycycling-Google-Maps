import asyncio
import logging
import random
import tkinter
from random import Random

from bleak import BleakClient
from tkinter import messagebox
from tortoise import Tortoise

from cycling.TacxCycling import TacxCycling
from db_models import Device
from db_models.Device import DeviceFactory
from devices.PolarHRMonitor import PolarHRMonitor
from devices.TacxTrainer import TacxTrainer
from gui.AsyncTk import AsyncTk
from gui.frames.BluetoothConnectionFrame import BluetoothConnectionFrame
from gui.frames.CyclingFrame import CyclingFrame
from gui.frames.ConnectingFrame import BluetoothConnectingFrame
from pycycling.heart_rate_service import HeartRateService
from pycycling.tacx_trainer_control import TacxTrainerControl
from training_plans.TestPlan import TestPlan

from utilities.BluetoothHandler import BluetoothHandler

# TODO(cody): Add ability to select trainer and HR monitor from list of available devices
POLAR_HR_CONTROL_POINT_UUID = "3E4F72D6-D632-1157-0BCD-5B5C673653AE"
TACX_TRAINER_CONTROL_UUID = "8B9E4197-3BA0-39EF-1290-F82450B4DC00"


class App(AsyncTk):
    def __init__(self):
        super().__init__()

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

        self.pycycling_clients = []

        # Main Frame Container
        container = tkinter.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Frames
        self.cycling_frame = CyclingFrame(container, self)
        self.cycling_frame.grid(row=0, column=0, sticky="nsew")
        self.connect_frame = BluetoothConnectionFrame(container, self)
        self.connect_frame.grid(row=0, column=0, sticky="nsew")
        self.connecting_frame = BluetoothConnectingFrame(container, self)
        self.connecting_frame.grid(row=0, column=0, sticky="nsew")
        self.frames += [self.connect_frame, self.cycling_frame, self.connecting_frame]

        # Tacx Cycling Instance
        self.tacx_cycler = TacxCycling(logger=self.logger)

        # Register bluetooth handler
        self.bluetooth_handler = BluetoothHandler()
        self.bluetooth_handler.register(self.connect_frame.bluetooth_notification_received)

        # Kickoff the async event loops
        self.show_frame(self.connect_frame)
        self.runners.append(self.setup_tortoise())
        self.runners.append(self.bluetooth_handler.discover_bluetooth_devices(self.connect_frame))

    def setup_logging(self):
        self.logger.setLevel(logging.DEBUG)
        logging_file_handler = logging.FileHandler('trkr_trainr.log')
        logging_file_handler.setLevel(logging.DEBUG)
        logging_stream_handler = logging.StreamHandler()
        logging_stream_handler.setLevel(logging.DEBUG)
        logging_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging_stream_handler.setFormatter(logging_formatter)
        logging_file_handler.setFormatter(logging_formatter)
        self.logger.addHandler(logging_stream_handler)
        self.logger.addHandler(logging_file_handler)

    def start_cycling(self):
        print(f"Connecting!")
        self.show_frame(self.connecting_frame)
        self.add_button_coro(self.start())

    def start_test(self):
        print(f"Testing!")
        self.show_frame(self.connecting_frame)
        self.add_button_coro(self.test())

    async def setup_tortoise(self):
        await Tortoise.init(
            db_url='sqlite://db.sqlite3',
            modules={'models': ['models']}
        )
        # Generate the schema
        await Tortoise.generate_schemas()

    async def test(self):
        self.show_frame(self.connecting_frame)
        await asyncio.sleep(4)
        await self.async_show_frame(self.cycling_frame)

        for segment in range(100):
            self.cycling_frame.receive_hr_data(bpm=random.randint(45, 50))
            self.cycling_frame.receive_cadence_data(cadence=random.randint(85, 89))
            self.cycling_frame.receive_speed_data(speed=random.randint(20, 21))
            if segment % 10 == 0:
                self.cycling_frame.receive_resistance_data(resistance=random.randint(30, 70))
            self.update()
            await asyncio.sleep(1)

    async def start(self):
        self.show_frame(self.connecting_frame)
        self.geometry("750x250")

        try:
            selected_cycling_devices = self.connect_frame.cycling_bluetooth_selector_box.curselection()
            if len(selected_cycling_devices) == 0:
                raise Exception('Please select a cycling device')

            selected_hr_devices = self.connect_frame.hr_bluetooth_selector_box.curselection()
            if len(selected_hr_devices) == 0:
                raise Exception('Please select a HR device')

            cycling_bluetooth_device = BleakClient(self.connect_frame.bluetooth_devices[selected_cycling_devices[0]])
            hr_bluetooth_device = BleakClient(self.connect_frame.bluetooth_devices[selected_hr_devices[0]])

            tacx_trainer_client = TacxTrainer(client=cycling_bluetooth_device, pycycling_client=TacxTrainerControl(cycling_bluetooth_device))
            heart_rate_client = PolarHRMonitor(client=hr_bluetooth_device, pycycling_client=HeartRateService(hr_bluetooth_device))

            await DeviceFactory.generate(training_device=tacx_trainer_client)
            await DeviceFactory.generate(training_device=heart_rate_client)

            tacx_trainer_client.register(self.cycling_frame.receive_speed_data)
            tacx_trainer_client.register(self.cycling_frame.receive_cadence_data)
            heart_rate_client.register(self.cycling_frame.receive_hr_data)

            with tacx_trainer_client.client as trainer_client, heart_rate_client.client as polar_client:
                trainer, hr_device = await self.tacx_cycler.connect_clients(trainer_client=trainer_client, polar_client=polar_client)  # TODO: Decouple this
                self.pycycling_clients += [trainer, hr_device]
                await self.async_show_frame(self.cycling_frame)

                training_plan = await TestPlan.generate()

                for segment in training_plan.segments:
                    self.logger.info(f"Setting resistance to {segment.resistance}")
                    await trainer.set_resistance(segment.resistance)
                    self.cycling_frame.receive_resistance_data(resistance=segment.resistance)  # change to notify at some point
                    await asyncio.sleep(segment.duration)
        except Exception as ex:
            messagebox.showinfo('Error', f'Error connecting to devices: {ex}')
            self.logger.info(ex)
            self.show_frame(self.connect_frame)


async def main():
    app = App()
    await app.run()


if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)

    asyncio.run(main())
