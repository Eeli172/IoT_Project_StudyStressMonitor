import time
import micropython
from hardware import Sensor

micropython.alloc_emergency_exception_buf(200)
            
def measure(stopper):
    sensor = Sensor() 
    sensor.start() # start gathering data into fifo
    
    peaks = []
    ppi_list = []
    first_signal = []
    max_jump_pct = 0.20 # %  # allowed change between two consecutive intervals
    last_interval = 1 # interval from earlier iteration
    last_peak_index = None
    index = 0
    data_previous = None
    slope_previous = None
    slope = 0
    kubios_min_length = 11

    printed = False
    while True:
        if stopper.stop: # button pressed - return to menu
            sensor.stop()
            return
        
        if printed == False:
            print("Signal stabilization...")
            printed = True
        
        if sensor.fifo.has_data():
            if 40000 > sensor.fifo.get() > 20000: # Signal stabilization
                printed = False
                break
         
    calibration = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), calibration) < 3000: # waiting another 3 seconds for a steady signal
        if stopper.stop: # button pressed - return to menu
            sensor.stop()
            return

        if sensor.fifo.has_data():
            sensor.fifo.get()
            
          
    calibration_start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), calibration_start) < 3000: # data is collected to calculate THRESHOLD
        if stopper.stop: # button pressed - return to menu
            sensor.stop()
            return

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
    
    
    measure_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), measure_time) < 30000 or len(ppi_list) < kubios_min_length: # 30000 = 30 sekuntia
        if stopper.stop: # button pressed - return to menu
            sensor.stop()
            return

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
                            if len(peaks) >= 2:
                                interval = peaks[-1][1] - peaks[-2][1] # is selected index in peaks list and its difference
                                
                                if 63 <= interval <= 500: # 240-30bpm allowed

                                    # allowed jump - if last interval and current interval isn't too far from each other -> True 
                                    allowed_jump = last_interval*(1+max_jump_pct) >= interval and last_interval*(1-max_jump_pct) <= interval

                                    if len(ppi_list) == 0: # first iteration
                                        last_interval = interval
                                        ppi_list.append(interval*4)

                                    elif allowed_jump: # if there is not too large jump from the last interval, add the interval to the list
                                        last_interval = interval
                                        ppi_list.append(interval*4)

 
                slope_previous = slope
            data_previous = data
            
    print("Seconds:",time.ticks_diff(time.ticks_ms(), measure_time) / 1000)
    print("PPIs:",len(ppi_list))
    sensor.stop() # stop gathering data into fifo


    return ppi_list # return 



if __name__ == "__main__": # main block for testing
    ppi_list = measure()
    mean_ppi = sum(ppi_list) / len(ppi_list)


    print(ppi_list)
    print("mean ppi:", mean_ppi, "ms")
    print(" mean hr:", 60000/mean_ppi, "bpm")