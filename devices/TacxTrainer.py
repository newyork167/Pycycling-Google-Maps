from bleak import BleakClient

from pycycling.tacx_trainer_control import TacxTrainerControl
from devices.TrainingDevice import TrainingDevice
class TacxTrainer(TrainingDevice):
    def __init__(self, client: BleakClient, pycycling_client: TacxTrainerControl):
        super().__init__(client, pycycling_client)
        self.bleak_client = client
        self.pycycling_client = pycycling_client

    async def on_connect(self):
        await self.pycycling_client.enable_fec_notifications()

    async def on_disconnect(self):
        await self.pycycling_client.disable_fec_notifications()
        await self.client.disconnect()

    async def setup_page_handler(self, page_handler: callable):
        self.pycycling_client.set_specific_trainer_data_page_handler(page_handler)
        self.pycycling_client.set_general_fe_data_page_handler(page_handler)
        await self.pycycling_client.enable_fec_notifications()
