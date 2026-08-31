import smbus2
import time
import threading

class LightSensor:
    def __init__(self, bus_number=1, address=0x5c):  # Hier auf 0x5c geändert!
        self.bus_number = bus_number
        self.address = address
        self.lux = 0.0
        
        # Continuous High Resolution Mode
        self.CONTINUOUS_HIGH_RES_MODE = 0x10
        
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while True:
            try:
                bus = smbus2.SMBus(self.bus_number)
                data = bus.read_i2c_block_data(self.address, self.CONTINUOUS_HIGH_RES_MODE, 2)
                bus.close()
                
                # Umrechnung der Bytes in Lux
                raw_lux = (data[0] << 8) | data[1]
                self.lux = round(raw_lux / 1.2, 2)
            except Exception as e:
                print(f"Error reading light sensor: {e}")
            
            time.sleep(1)

    def readLight(self):
        return {"lux": self.lux}