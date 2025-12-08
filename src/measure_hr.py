from machine import Pin
import time
import view


class Measure_hr:
    def __init__(self, menu, encoder, sensor):
        self.menu = menu
        self.encoder  = encoder
        self.sensor = sensor

        
    def run(self):
        while self.encoder.fifo.has_data():
            self.encoder.fifo.get()
        view.display_center(["TO START", "MEASURING HR", "", "1. PLACE THUMB", "ON SENSOR", "2. PRESS BUTTON"])
        time.sleep(1)
        while not (self.encoder.fifo.has_data() and self.encoder.fifo.get() == 0): # waiting until the user presses the button
            time.sleep_ms(10)
        while self.encoder.button() == 0: # wait until button is released
            time.sleep_ms(10)
        while self.encoder.fifo.has_data(): # wait until fifo is empty
            self.encoder.fifo.get()
        
        view.display_center(["Stabilizing"," signal.."])
        self.sensor.start()
        result = measure(self.sensor, self.encoder)
        if result == "abort":
            self.menu.change = True
            self.sensor.stop()   

def plot_bpm(bpm):
    # show bpm on oled
    bpm_int = int(bpm)
    view.display_center([
        "MEASURING HR",
        "",
        f"{bpm_int} BPM"
    ])

def measure(sensor, encoder):
    
    led = Pin(21, Pin.OUT)
    led_off_time = None
    

    SF = 250  # frequency
    peaks = []
    first_signal = []
    last_peak_index = None
    index = 0
    data_previous = None
    slope_previous = None
    slope = 0
    printed = False
    
    # Signal stabilization
    while True:
        if encoder.fifo.has_data(): # exit from the loop in the menu
            preasured = encoder.fifo.get()
            if preasured == 0:
                led.off()
                return "abort"
            time.sleep_ms(2)
            
        if printed == False:
            print("Signal stabilization...")
            printed = True

        if sensor.fifo.has_data():
            if 40000 > sensor.fifo.get() > 20000: # Signal stabilization
                printed = False
                break
        time.sleep_ms(2)
     
    # waiting another 3 seconds for a steady signal
    calibration = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), calibration) < 3000:  
        if encoder.fifo.has_data(): # # exit from the loop in the menu
            preasured = encoder.fifo.get()
            if preasured == 0:
                led.off()
                return "abort"
        time.sleep_ms(2)
        
        if sensor.fifo.has_data():
            sensor.fifo.get()
        time.sleep_ms(2)
    
    # data is collected to calculate THRESHOLD
    calibration_start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), calibration_start) < 3000:  
        
        if encoder.fifo.has_data(): # exit from the loop in the menu
            preasured = encoder.fifo.get()
            if preasured == 0:
                led.off()
                return "abort"

        if printed == False:
            print("Collecting data..")
            printed = True
            
        if sensor.fifo.has_data():
            value = sensor.fifo.get()
            first_signal.append(value)
    printed = False

    min_signal = min(first_signal)
    max_signal = max(first_signal)
    THRESHOLD = ((max_signal + min_signal) / 2) * 1.015  # modernized formula to make the THRESHOLD higher (reduces noise)

    MIN_PEAK_DIST = 125  # min interval = 120 bpm max (reduces nois)

    last_print = time.ticks_ms()
    PRINT_INTERVAL = 3000  # bpm refresh rate

    view.display_center(["Starting"," measurement.."])
    while True:
        time.sleep_ms(2)
        
        if led_off_time is not None: # checks whether a led needs to be turned off
            if time.ticks_diff(time.ticks_ms(), led_off_time) >= 0:
                led.off()
                led_off_time = None

        if encoder.fifo.has_data(): # exit from the loop in the menu
            preasured = encoder.fifo.get()
            if preasured == 0:
                led.off()
                return "abort"

        if printed == False:
            print("Looking for peaks...")
            printed = True

        if sensor.fifo.has_data():
            data = sensor.fifo.get()
            index += 1

            if data_previous is not None:
                slope = data - data_previous  # check the sign (if<0 - vertex)

                if slope_previous is not None:
                    if slope < 0 and slope_previous >= 0 and data_previous > THRESHOLD:  # the previous sign must be positive and data and the value must be greater than THRESHOLD
                        if last_peak_index is None or index - last_peak_index >= MIN_PEAK_DIST:  # checking that the interval is not too small
                            peaks.append((data_previous, index - 1))  # add the peak value and its index
                            last_peak_index = index - 1
                            led.on()
                            led_off_time = time.ticks_ms() + 50 # 50 ms timer


                            if len(peaks) > 20:  # delete the oldest element of peaks
                                peaks.pop(0)
                slope_previous = slope
            data_previous = data
        now = time.ticks_ms()
        
        if time.ticks_diff(now, last_print) >= PRINT_INTERVAL:  # waiting for PRINT_INTERVAL seconds to collect the new peaks
            last_print = now

            if len(peaks) >= 2:
                intervals = []
                for i in range(len(peaks) - 1):
                    interval = peaks[i + 1][1] - peaks[i][1]  # recalculating intervals for new peaks
                    if 63 <= interval <= 500: # 240-30bpm allowed

                        intervals.append(interval)

                if intervals:
                    window = intervals[-5:]
                    avg_int = sum(window) / len(window)  # calculating average value of 5 last intervals
                    bpm = 60 * SF / avg_int
                    print("Current bpm: ", bpm)
                    plot_bpm(bpm)
                else:
                    print("intervals:  ", intervals)
                           
        