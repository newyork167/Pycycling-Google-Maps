class TrainingDevice:
    def __init__(self, client: BleakClient, pycycling_client: TacxTrainerControl or HeartRateService): # type: ignore
        self.client = client
        self.pycycling_client = pycycling_client

    async def on_connect(self):
        pass

    async def on_disconnect(self):
        pass

    async def setup_page_handler(self, page_handler: callable):
        pass
