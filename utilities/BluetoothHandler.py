from bleak import BleakScanner
from utilities.Observable import Observable

class BluetoothHandler(Observable):
    async def discover_bluetooth_devices(self, controller) -> None:
        self.devices = await BleakScanner.discover()
        self.notify(devices=self.devices)
