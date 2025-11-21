# sensor, OLED, encoder, timers (optional)
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from fifo import Fifo
import time
import micropython

micropython.alloc_emergency_exception_buf(200)   # For hard interrupts



########## OLED ###################################
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)


########## SENSOR #################################



########## ENCODER ################################
class Encoder:
    def __init__(self):
        self.a = Pin(10, Pin.IN)               # Channel A
        self.b = Pin(11, Pin.IN)               # Channel B
        self.button = Pin(12, Pin.IN, Pin.PULL_UP)     # Push button

        self.fifo = Fifo(30, typecode='i')        # FIFO for +1 / -1 steps
        self.last_press = 0

        self.a.irq(handler=self.handler, trigger=Pin.IRQ_FALLING, hard=True)
        self.button.irq(handler=self._button_handler, trigger=Pin.IRQ_FALLING, hard=True)

    def handler(self, pin):
        if self.b():                 # If B == 1
            self.fifo.put(1)         # One direction
        else:                        # If B == 0
            self.fifo.put(-1)        # Other direction
            
    def _button_handler(self, pin):
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_press) < 150:
            return  # debounce

        self.last_press = now
        
        self.fifo.put(0)


