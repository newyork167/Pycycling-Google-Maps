from bleak import BleakClient

from pycycling.tacx_trainer_control import TacxTrainerControl
from devices.TrainingDevice import TrainingDevice
from utilities.Observable import Observable


class TacxTrainer(TrainingDevice, Observable):
    def __init__(self, client: BleakClient, pycycling_client: TacxTrainerControl):
        super().__init__(client, pycycling_client)
        self.pycycling_client = pycycling_client

    async def setup(self):
        await self.setup_page_handler(specific_page_handler=self.default_specific_trainer_page_handler)
        await self.setup_general_page_handler(general_page_handler=self.default_general_trainer_page_handler)

    async def on_connect(self):
        await self.pycycling_client.enable_fec_notifications()

    async def on_disconnect(self):
        await self.pycycling_client.disable_fec_notifications()
        await self.client.disconnect()

    async def setup_page_handler(self, specific_page_handler: callable):
        self.pycycling_client.set_specific_trainer_data_page_handler(specific_page_handler)
        await self.pycycling_client.enable_fec_notifications()

    async def setup_general_page_handler(self, general_page_handler: callable):
        self.pycycling_client.set_general_fe_data_page_handler(general_page_handler)
        await self.pycycling_client.enable_fec_notifications()

    def default_specific_trainer_page_handler(self, data):
        print(data)
        self.notify(instantaneous_cadence=data['instantaneous_cadence'])

    def default_general_trainer_page_handler(self, data):
        print(data)
        self.notify(speed=data['speed'])