''' Code Generated with help from Claude'''

import asyncio
from bleak import BleakClient, BleakScanner

# Nordic UART Service (NUS) UUIDs
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Write characteristic
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Notify characteristic


class BLEUARTClient:
    def __init__(self, device_name=None, device_address=None):
        """
        Initialize BLE UART client
        
        Args:
            device_name: Name of the BLE device to connect to
            device_address: MAC address of the BLE device (optional)
        """
        self.device_name = device_name
        self.device_address = device_address
        self.client = None
        self.connected = False
        
    async def scan_devices(self, timeout=5.0):
        """Scan for available BLE devices"""
        print("Scanning for BLE devices...")
        devices = await BleakScanner.discover(timeout=timeout)
        
        print(f"Found {len(devices)} devices:")
        for device in devices:
            print(f"  {device.name} - {device.address}")
        
        return devices
    
    async def connect(self):
        """Connect to the BLE device"""
        try:
            # If no address provided, scan for device by name
            if not self.device_address and self.device_name:
                print(f"Searching for device: {self.device_name}")
                devices = await BleakScanner.discover()
                
                for device in devices:
                    if device.name == self.device_name:
                        self.device_address = device.address
                        print(f"Found device at {self.device_address}")
                        break
                
                if not self.device_address:
                    print(f"ERROR: Device '{self.device_name}' not found")
                    return False
            
            # Connect to device
            self.client = BleakClient(self.device_address)
            await self.client.connect()
            self.connected = True
            print(f"Connected to {self.device_address}")
            
            # Start notification handler
            await self.client.start_notify(UART_TX_CHAR_UUID, self.notification_handler)
            print("Notification handler started")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Connection failed: {e}")
            self.connected = False
            return False
    
    def notification_handler(self, sender, data):
        """Handle incoming notifications from BLE device"""
        try:
            message = data.decode('utf-8')
            print(f"Received: {message}")
            
            # Process the received message
            asyncio.create_task(self.process_message(data))
            
        except Exception as e:
            print(f"ERROR: Notification handling failed: {e}")
    
    async def send_data(self, data):
        """Send data to BLE device via UART"""
        if not self.connected or not self.client:
            print("ERROR: Not connected to device")
            return False
        
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            await self.client.write_gatt_char(UART_RX_CHAR_UUID, data)
            print(f"Sent: {data}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to send data: {e}")
            return False
    
    async def process_message(self, data):
        """
        Process received messages - customize this for your protocol
        
        Args:
            data: Raw bytes received from BLE UART
        """
        try:
            message = data.decode('utf-8').strip()
            
            # Example: Echo back the message
            response = f"ACK: {message}"
            await self.send_data(response)
            
            # Add your custom message handling here
            if message.startswith("CMD:"):
                command = message[4:]
                print(f"Executing command: {command}")
            
        except Exception as e:
            print(f"ERROR: Failed to process message: {e}")
    
    async def disconnect(self):
        """Disconnect from BLE device"""
        if self.client and self.connected:
            try:
                await self.client.stop_notify(UART_TX_CHAR_UUID)
                await self.client.disconnect()
                self.connected = False
                print("Disconnected from device")
            except Exception as e:
                print(f"ERROR: Disconnect failed: {e}")


async def main():
    """Example usage of BLE UART client"""
    
    # Option 1: Connect by device name
    ble_uart = BLEUARTClient(device_name="YourDeviceName")
    
    # Option 2: Connect by MAC address
    # ble_uart = BLEUARTClient(device_address="AA:BB:CC:DD:EE:FF")
    
    # Scan for devices (optional)
    await ble_uart.scan_devices(timeout=5.0)
    
    # Connect to device
    if await ble_uart.connect():
        try:
            # Send some test data
            await ble_uart.send_data("Hello from Python!\n")
            
            # Keep connection alive to receive data
            await asyncio.sleep(30)
            
        finally:
            # Clean disconnect
            await ble_uart.disconnect()
    else:
        print("ERROR: Failed to connect to device")


if __name__ == "__main__":
    asyncio.run(main())