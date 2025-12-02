from mqtt import Mqtt
from config import config
from time import sleep
from view import display_left


class Kubios:
    def __init__(self) -> None:
        self.mode = "kubios"
        self.result = []
        self.ppi_list  = []
        self.mqtt = Mqtt("kubios")
        self.topic_pub = config["broker"]["kubios_pub"]
        self.topic_sub = config["broker"]["kubios_sub"]


    def get_data(self):
        self.ppi_list = [828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800]


    def run(self):
        self.get_data()

        self.result = self.mqtt.run(self.topic_pub, self.topic_sub, self.ppi_list)

        self.result = [
            f"MEAN HR: {int(self.result["msg"]["data"]["analysis"]["mean_hr_bpm"])}", 
            f"MEAN PPI: {int(self.result["msg"]["data"]["analysis"]["mean_rr_ms"])}", 
            f"RMSSD: {int(self.result["msg"]["data"]["analysis"]["rmssd_ms"])}", 
            f"SDNN: {int(self.result["msg"]["data"]["analysis"]["sdnn_ms"])}", 
            f"SNS: {self.result["msg"]["data"]["analysis"]["sns_index"]:.3f}", 
            f"PNS: {self.result["msg"]["data"]["analysis"]["pns_index"]:.3f}", 
        ]

        display_left(self.result)

        sleep(3)


if __name__ == "__main__":
    k = Kubios()
    k.run()