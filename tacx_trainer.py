import asyncio
import logging
import tkinter

from bleak import BleakClient
from tkinter import messagebox
from tortoise import Tortoise

from cycling.TacxCycling import TacxCycling
from devices.PolarHRMonitor import PolarHRMonitor
from devices.TacxTrainer import TacxTrainer
from gui.AsyncTk import AsyncTk
from gui.frames.BluetoothConnectionFrame import BluetoothConnectionFrame
from gui.frames.CyclingFrame import CyclingFrame
from gui.frames.ConnectingFrame import BluetoothConnectingFrame
from pycycling.heart_rate_service import HeartRateService
from pycycling.tacx_trainer_control import TacxTrainerControl

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

    async def setup_tortoise(self):
        await Tortoise.init(
            db_url='sqlite://db.sqlite3',
            modules={'models': ['models']}
        )
        # Generate the schema
        await Tortoise.generate_schemas()

    async def start(self):
        self.show_frame(self.connecting_frame)

        try:
            selected_cycling_devices = self.connect_frame.cycling_bluetooth_selector_box.curselection()
            if len(selected_cycling_devices) == 0:
                raise Exception('Please select a cycling device')

            selected_hr_devices = self.connect_frame.hr_bluetooth_selector_box.curselection()
            if len(selected_hr_devices) == 0:
                raise Exception('Please select a HR device')

            cycling_bluetooth_device = BleakClient(self.connect_frame.bluetooth_devices[selected_cycling_devices[0]])
            hr_bluetooth_device = BleakClient(self.connect_frame.bluetooth_devices[selected_hr_devices[0]])

            TacxTrainerClient = TacxTrainer(client=cycling_bluetooth_device, pycycling_client=TacxTrainerControl(cycling_bluetooth_device))
            HeartRateClient = PolarHRMonitor(client=hr_bluetooth_device, pycycling_client=HeartRateService(hr_bluetooth_device))

            with TacxTrainerClient.client as trainer_client, HeartRateClient.client as polar_client:
                trainer, hr_device = await self.tacx_cycler.connect_clients(trainer_client=trainer_client, polar_client=polar_client)  # TODO: Decouple this
                self.pycycling_clients += [trainer, hr_device]
                # self.cycling_frame.tkraise()
                self.show_frame(self.cycling_frame)
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
