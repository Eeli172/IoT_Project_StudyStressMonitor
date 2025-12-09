from config import config
from history import History
from mqtt import Mqtt
from view import display_center, display_left
from ppi_list import measure
import time



class Hrv:
    def __init__(self, wlan, encoder):
        self.ppi = []               # placeholder
        self.payload = {
            "mean_ppi": None,       # mean PPI (ms)
            "mean_hr": None,        # mean heart rate (bpm)
            "rmssd": None,          # root mean square of successive differences
            "sdnn": None            # standard deviation of NN intervals
        }
        self.wlan = wlan
        self.mqtt = Mqtt(self.wlan, "hrv")     # define mqtt instance
        self.encoder = encoder
        self.history = History(self.encoder)

        self.topic_pub = config["broker"]["add_record"]     # publish topic - (config.json)
        self.topic_sub = config["broker"]["db_response"]    # subscribe topic (config.json)



    def get_data(self): 
        # self.ppi = [1036, 1020, 1008, 952, 996, 1012, 1080, 1004, 940, 960, 980, 1004, 982, 980, 988, 982, 1012, 968, 944, 996, 988, 980, 928, 956, 972, 1004, 988, 888, 900, 956]                    # gather ppi -data
        self.ppi = measure(self.encoder.stopper)            # gather ppi -data



    def calc_hrv(self):
        self.get_data() # get ppi data for hrv calculations
        if self.encoder.stopper.stop: # button pressed - return to menu
            return

        ####################### MEAN PPI #####################
        self.payload["mean_ppi"] = sum(self.ppi) / len(self.ppi) # calculate mean ppi


        ####################### MEAN HR #####################
        self.payload["mean_hr"] = 60000 / self.payload["mean_ppi"] # calculate mean heart rate - 60000 ms = 1 minute, so bpm = 60000 / mean_ppi


        ####################### SDNN ######################
        # calculate squared differences from mean
        sum_sq_diff = 0 
        for x in self.ppi:
            diff = x - self.payload["mean_ppi"]  # difference from mean
            sq_diff = diff * diff  # square the difference
            sum_sq_diff += sq_diff  # add to the sum

        # variance = sum of squared differences divided by (n-1)
        variance = sum_sq_diff / (len(self.ppi) - 1)

        # standard deviation = square root of variance
        self.payload["sdnn"] = variance ** 0.5


        ####################### RMSSD ######################
        squared_diffs = []

        # calculate differences between successive intervals
        for i in range(len(self.ppi) - 1):
            diff = self.ppi[i+1] - self.ppi[i]  # difference between next and current
            sq_diff = diff * diff  # square it
            squared_diffs.append(sq_diff)  # add to list

        # calculate mean of squared differences
        total = 0
        for val in squared_diffs:
            total += val
        mean_sq_diff = total / len(squared_diffs)

        # take square root to get rmssd
        self.payload["rmssd"] = mean_sq_diff ** 0.5



    def run(self):
        # drain fifo
        self.encoder.drain_fifo()
            
        # plot on oled AND wait until button is pressed
        display_center(["TO START HRV-", "MEASUREMENT", "", "1. PLACE THUMB", "ON SENSOR", "2. PRESS BUTTON"])
        
        button_pressed = False
        
        while not button_pressed:   # wait for user to be ready to start the measurement
            if self.encoder.fifo.has_data():
                if self.encoder.fifo.get() == 0:
                    while self.encoder.button.value() == 0:
                        pass
                    button_pressed = True
                    self.encoder.drain_fifo()

        self.encoder.stopper.in_function = True # set encoder button irq to stop the function when button is pressed - to return to menu


        # plot on oled AND get hrv data
        display_center(["Collecting", " data.."])
        self.calc_hrv()
        if self.encoder.stopper.stop:  # button pressed - return to menu
            display_center(["ABORTED", "", "Returning", " to menu.."])
            time.sleep_ms(800)
            return


        # plot on oled 
        display_center(["Sending data.."])

        # connect to wlan
        self.wlan.connect(self.encoder.stopper)
        
        if self.encoder.stopper.stop:  # button pressed - return to menu
            display_center(["ABORTED", "", "Returning", " to menu.."])
            time.sleep_ms(800)
            return


        # get timestamp 
        self.wlan.get_time()
        self.payload["timestamp_long"], self.payload["timestamp_short"] = self.wlan.format_time(self.wlan.timestamp) 

        # send data to broker
        self.result = self.mqtt.run(self.topic_pub, self.topic_sub, self.payload, self.encoder.stopper)
        
        if self.encoder.stopper.stop:  # button pressed - return to menu
            display_center(["ABORTED", "", "Returning", " to menu.."])
            time.sleep_ms(800)
            return


        # plot calculations on oled
        display_left([
            'MEAN HR:' + str(int(self.payload["mean_hr"])),
            'MEAN PPI:' + str(int(self.payload["mean_ppi"])),
            'RMSSD:' + str(int(self.payload["rmssd"])),
            'SDNN:' + str(int(self.payload["sdnn"]))
        ])

        self.history.add_session(self.payload) # push data to history.json


        self.encoder.stopper.in_function = False # set encoder button irq to act as normal button press



        # drain fifo and return to menu when button pressed
        self.encoder.drain_fifo()
        button_pressed = False

        while not button_pressed: # show data on oled until button pressed and return to menu
            while self.encoder.fifo.has_data():
                if self.encoder.fifo.get() == 0:
                    button_pressed = True




if __name__ == "__main__": # main block for testing
    
    hrv = Hrv()
    hrv.run()
