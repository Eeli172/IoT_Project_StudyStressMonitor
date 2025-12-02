from config import config
from mqtt import Mqtt
import time



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
        self.ppi = [828, 836, 852, 760, 800, 860, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800]
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
        self.calc_hrv() # get data

        self.result = self.mqtt.run(self.topic_pub, self.topic_sub, self.payload)

        print(1, self.result)

        time.sleep(3)




if __name__ == "__main__":
    hrv = Hrv()
    hrv.run()
