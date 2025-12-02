from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
from piotimer import Piotimer
from fifo import Fifo
from config import config
import time
import micropython
from hardware import Sensor

micropython.alloc_emergency_exception_buf(200)
            
def measure():
    sensor = Sensor()
    sensor.start()
    all_data = []
    
    SF = 250 # frequency
    MAX_PEAKS = 20 # max number of peaks in the list
    peaks = []
    first_signal = []
    last_peak_index = None
    index = 0
    data_previous = None
    data_current = 0
    slope_previous = None
    slope = 0

    printed = False
    while True:
        if printed == False:
            print("Signal stabilization...")
            printed = True
        
        if sensor.fifo.has_data():
            if sensor.fifo.get() > 1000: # Signal stabilization
                printed = False
                break
         
    calibration = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), calibration) < 3000: # waiting another 3 seconds for a steady signal
        if sensor.fifo.has_data():
            sensor.fifo.get()
            
          
    calibration_start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), calibration_start) < 3000: # data is collected to calculate THRESHOLD
        if printed == False:
            print("Collecting data..")
            printed = True
        if sensor.fifo.has_data():
            value = sensor.fifo.get()
            first_signal.append(value)
    printed = False
    
    min_signal = min(first_signal)
    max_signal = max(first_signal)
    THRESHOLD = ((max_signal + min_signal)/2) * 1.015 # modernized formula to make the THRESHOLD higher (reduces noise)
    
    MIN_PEAK_DIST = 125 # min interval = 120 bpm max (reduces nois)
    
    last_print = time.ticks_ms()
    
    measure_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), measure_time) < 32000: # 32000 = 32 sekuntia
        if printed == False:
            print("Looking for peaks...")
            printed = True
        
        if sensor.fifo.has_data():
            data = sensor.fifo.get()
            index +=1
            
            if data_previous is not None: 
                slope = data - data_previous # check the sign (if<0 - vertex)
                
                if slope_previous is not None:
                    if slope < 0 and slope_previous >= 0 and data_previous > THRESHOLD: # the previous sign must be positive and data and the value must be greater than THRESHOLD 
                            if last_peak_index is None or index - last_peak_index >= MIN_PEAK_DIST: # checking that the interval is not too small
                                peaks.append((data_previous, index-1)) # add the peak value and its index
                                last_peak_index = index-1
                slope_previous = slope
            data_previous = data
            
        
    intervals = []
    for i in range(len(peaks)-1):
        interval = peaks[i+1][1] - peaks[i][1] # is selected index in peaks list and its difference
        if 120 <= interval <= 250:  
            intervals.append(interval)
            
    
    sensor.stop()


    return intervals

    
    
        
    
    






