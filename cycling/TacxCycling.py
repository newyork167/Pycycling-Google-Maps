import asyncio

from bleak import BleakClient

from devices.PolarHRMonitor import HRMonitor, PolarHRMonitor
from devices.TacxTrainer import TacxTrainer
from devices.TrainingDevice import TrainingDevice
from pycycling.heart_rate_service import HeartRateService
from pycycling.tacx_trainer_control import TacxTrainerControl
from training_plans.test_plan import TestPlan


class TacxCycling:
    def __init__(self, logger):
        self.logger = logger
        self.pycycling_clients = []

    # async def connect_client(self, client: BleakClient) -> TrainingDevice:
    #     await client.is_connected()
    #
    #     training_device = TacxTrainer(client, TacxTrainerControl(client))
    #     await training_device.on_connect()
    #
    #     return training_device

    async def connect_clients(self, trainer_client: BleakClient, polar_client: BleakClient) -> list[TrainingDevice]:
        # TODO: Generalize
        clients = []

        await trainer_client.is_connected()
        await polar_client.is_connected()

        clients += [
            TacxTrainer(trainer_client, TacxTrainerControl(trainer_client)),
            PolarHRMonitor(polar_client, HeartRateService(polar_client))
        ]

        for client in clients:
            client.setup()
            await client.on_connect()

        return clients

    async def disconnect_clients(self):
        for pycycling_client in self.pycycling_clients:
            await pycycling_client.on_disconnect()
    async def start(self, TacxTrainerClient: TacxTrainer, HeartRateClient: HRMonitor):
        try:
            training_plan = await TestPlan.generate()

            for segment in training_plan.segments:
                self.logger.info(f"Setting resistance to {segment.resistance}")
                await TacxTrainerClient.pycycling_client.set_basic_resistance(segment.resistance)
                await asyncio.sleep(segment.duration)
        except Exception as ex:
            self.logger.info(ex)