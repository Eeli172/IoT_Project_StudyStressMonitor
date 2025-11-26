from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
from piotimer import Piotimer
from fifo import Fifo
from config import config
import time
import micropython

micropython.alloc_emergency_exception_buf(200)   # For hard interrupts



########## OLED ###################################
oled_width = 128
oled_height = 64
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(oled_width, oled_height, i2c)



########## SENSOR #################################
class Sensor:
    def __init__(self):
        self.sensor = ADC(Pin(26, Pin.IN)) # sensor (ADC_0 connector)
        self.fifo = Fifo(size=50, typecode = 'i')
        self.timer = None

    def start(self):
        Piotimer(freq=config["sampling_rate_hz"], callback=self.callback) # frequency configured in config.json
    
    def stop(self):
        if self.timer:
            self.timer.deinit()
            self.timer = None

    def callback(self, timer):
        self.fifo.put(self.sensor.read_u16())


########## ENCODER ################################
class Encoder:
    def __init__(self):
        self.a = Pin(10, Pin.IN)               # Channel A
        self.b = Pin(11, Pin.IN)               # Channel B
        self.button = Pin(12, Pin.IN, Pin.PULL_UP)     # Push button

        self.fifo = Fifo(30, typecode='i')        # FIFO for +1 / -1 steps
        self.last_press = 0

        self.a.irq(handler=self.handler, trigger=Pin.IRQ_RISING, hard=True)
        self.button.irq(handler=self._button_handler, trigger=Pin.IRQ_FALLING, hard=True)

    def handler(self, pin):
        print("turn")
        if self.b():                 # If B == 1
            self.fifo.put(-1)         # One direction
        else:                        # If B == 0
            self.fifo.put(1)        # Other direction
            
    def _button_handler(self, pin):
        print("press")
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_press) < 250:
            return  # debounce

        self.last_press = now
        
        self.fifo.put(0)

if __name__ == "__main__":
    encoder = Encoder()

    
    while True:
        while encoder.fifo.has_data():

            step = encoder.fifo.get()
            print(step)
