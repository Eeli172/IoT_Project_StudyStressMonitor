from mqtt import Mqtt
from config import config
from ppi_list import measure
from view import display_left
from hardware import Encoder


class Kubios:
    def __init__(self):
        self.mode = "kubios"
        self.ppi_list  = []
        self.mqtt = Mqtt("kubios")
        self.topic_pub = config["broker"]["kubios_pub"]
        self.topic_sub = config["broker"]["kubios_sub"]


    def get_data(self):
        self.ppi_list = measure()


    def run(self):
        self.get_data()

        result = self.mqtt.run(self.topic_pub, self.topic_sub, self.ppi_list)

        result_list = [
            f"MEAN HR: {int(result["msg"]["data"]["analysis"]["mean_hr_bpm"])}", 
            f"MEAN PPI: {int(result["msg"]["data"]["analysis"]["mean_rr_ms"])}", 
            f"RMSSD: {int(result["msg"]["data"]["analysis"]["rmssd_ms"])}", 
            f"SDNN: {int(result["msg"]["data"]["analysis"]["sdnn_ms"])}", 
            f"SNS: {result["msg"]["data"]["analysis"]["sns_index"]:.3f}", 
            f"PNS: {result["msg"]["data"]["analysis"]["pns_index"]:.3f}"
        ]

        display_left(result_list)

        # return to menu when button pressed
        encoder = Encoder()
        button_pressed = False

        while not button_pressed:
            if encoder.fifo.has_data():
                while encoder.fifo.has_data():
                    if encoder.fifo.get() == 0:
                        button_pressed = True


if __name__ == "__main__":
    k = Kubios()
    k.run()