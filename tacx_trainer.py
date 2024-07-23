import asyncio
import logging
import tkinter

from bleak import BleakClient
from tortoise import Tortoise

from devices.TacxTrainer import TacxTrainer
from devices.PolarHRMonitor import PolarHRMonitor
from devices.TrainingDevice import TrainingDevice
from gui.AsyncTk import AsyncTk
from gui.frames.BluetoothConnectionFrame import BluetoothConnectionFrame
from gui.frames.CyclingFrame import CyclingFrame

from pycycling.tacx_trainer_control import TacxTrainerControl
from pycycling.heart_rate_service import HeartRateService
from training_plans.test_plan import TestPlan
from utilities.BluetoothHandler import BluetoothHandler

# TODO(cody): Add ability to select trainer and HR monitor from list of available devices
POLAR_HR_CONTROL_POINT_UUID = "3E4F72D6-D632-1157-0BCD-5B5C673653AE"
TACX_TRAINER_CONTROL_UUID = "8B9E4197-3BA0-39EF-1290-F82450B4DC00"


class App(AsyncTk):
    def __init__(self):
        super().__init__()

        self.pycycling_clients = []

        self.current_cadence_label = None
        self.current_speed_label = None
        self.current_hr_label = None
        self.bluetooth_selector_box = None

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

        self.frames += [self.connect_frame]

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

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
        print(f"Starting cycling")
        self.runners.append(self.start())
        self.cycling_frame.tkraise()

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
        self.logger.info(data)

    def heart_rate_page_handler(self, data):
        self.logger.info(data)

        if self.current_hr_label:
            self.current_hr_label.config(text=data['heart_rate'])

    async def start(self):
        try:
            async with BleakClient(TACX_TRAINER_CONTROL_UUID) as trainer_client, BleakClient(POLAR_HR_CONTROL_POINT_UUID) as polar_client:
                trainer, hr_device = await self.connect_clients(trainer_client=trainer_client, polar_client=polar_client)
                self.pycycling_clients += [trainer, hr_device]

                await trainer.setup_page_handler(page_handler=self.trainer_page_handler)
                await hr_device.setup_page_handler(page_handler=self.heart_rate_page_handler)

                training_plan = await TestPlan.generate()

                for segment in training_plan.segments:
                    await trainer.pycycling_client.set_basic_resistance(segment.resistance)
                    await asyncio.sleep(segment.duration)
        except Exception as ex:
            self.logger.info(ex)


async def main():
    app = App()
    await app.run()


if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)

    asyncio.run(main())
