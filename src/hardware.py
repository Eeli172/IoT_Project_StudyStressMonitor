from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
from piotimer import Piotimer
from fifo import Fifo
from config import config
import time
import micropython

micropython.alloc_emergency_exception_buf(200)   # For hard interrupts



########## OLED ###################################
oled_width = 128 # display width px
oled_height = 64 # display height px
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000) 
oled = SSD1306_I2C(oled_width, oled_height, i2c) # oled instance to be imported



########## SENSOR #################################
class Sensor:
    def __init__(self):
        self.sensor = ADC(Pin(26, Pin.IN))          # sensor (ADC_0 connector)
        self.fifo = Fifo(size=50, typecode = 'i')   # fifo for 50integer samples
        self.timer = None                           # placeholder for timer

    def start(self):
        # Start periodic sampling using Piotimer with frequency from config.json
        self.timer = Piotimer(
            freq=config["sampling_rate_hz"],        # frequency which we call a function
            callback=self.callback                  # the function we call
        ) 
    
    def stop(self): # stop timer 
        if self.timer:
            self.timer.deinit()
            self.timer = None

    def callback(self, timer): # put sensor reading into fifo
        self.fifo.put(self.sensor.read_u16())



########## ENCODER ################################
class Encoder:
    def __init__(self):
        self.a = Pin(10, Pin.IN)                        # Channel A
        self.b = Pin(11, Pin.IN)                        # Channel B
        self.button = Pin(12, Pin.IN, Pin.PULL_UP)      # Push button

        self.fifo = Fifo(30, typecode='i')              # FIFO for +1 / -1 steps
        self.last_press = 0

        self.a.irq(handler=self.handler, trigger=Pin.IRQ_RISING, hard=True)
        self.button.irq(handler=self._button_handler, trigger=Pin.IRQ_FALLING, hard=True)

    def handler(self, pin):
        if self.b():                 # If B == 1
            self.fifo.put(-1)        # One direction
        else:                        # If B == 0
            self.fifo.put(1)         # Other direction
            
    def _button_handler(self, pin):
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_press) < 150:
            return  # debounce

        self.last_press = now
        
        self.fifo.put(0)
    
    def drain_fifo(self):
        while self.fifo.has_data():
            self.fifo.get()





if __name__ == "__main__": # main block for testing
    encoder = Encoder()

    while True:
        while encoder.fifo.has_data():

            step = encoder.fifo.get()
            print(step)
