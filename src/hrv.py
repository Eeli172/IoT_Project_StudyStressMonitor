from config import config
from mqtt import Mqtt
import time
from hardware import Encoder
from view import display_center, display_left
from ppi_list import measure



class Hrv:
    def __init__(self):
        self.ppi = []
        self.payload = {
            "mean_ppi": None, # mean PPI (ms)
            "mean_hr": None, # mean heart rate (bpm)
            "rmssd": None, # root mean square of successive differences
            "sdnn": None # standard deviation of NN intervals
        }
        # define mqtt connection
        self.mqtt = Mqtt("hrv")

        self.topic_pub = config["broker"]["add_record"]
        self.topic_sub = config["broker"]["topic_response"]



    def get_ppi(self):
        self.ppi = measure()
        self.payload["timestamp"] = time.time()



    def calc_hrv(self):
        self.get_ppi()

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
        # plot on oled AND wait until button is pressed
        display_center(["TO START HRV-", "MEASUREMENT", "", "1. PLACE THUMB", "ON SENSOR", "2. PRESS BUTTON"])
        encoder = Encoder()
        button_pressed = False
        
        while not button_pressed: 
            if encoder.fifo.has_data():
                if encoder.fifo.get() == 0:
                    button_pressed = True


        # plot on oled AND get data
        display_center(["Collecting", " data.."])
        self.calc_hrv()


        # plot on oled AND send data to broker
        display_center(["Sending data.."])
        self.result = self.mqtt.run(self.topic_pub, self.topic_sub, self.payload)


        # plot calculations on oled
        display_left([
            'MEAN HR:' + str(int(self.payload["mean_hr"])),
            'MEAN PPI:' + str(int(self.payload["mean_ppi"])),
            'RMSSD:' + str(int(self.payload["rmssd"])),
            'SDNN:' + str(int(self.payload["sdnn"]))
        ])

        # drain fifo and return to menu when button pressed
        while encoder.fifo.has_data():
            encoder.fifo.get()

        button_pressed = False

        while not button_pressed:
            if encoder.fifo.has_data():
                while encoder.fifo.has_data():
                    if encoder.fifo.get() == 0:
                        button_pressed = True




if __name__ == "__main__": # main block for testing
    hrv = Hrv()
    hrv.run()
