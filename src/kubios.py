from mqtt import Mqtt
from config import config
from ppi_list import measure
from view import display_left, display_center
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
        # plot on oled AND wait until button is pressed
        display_center(["TO START KUBIOS-", "ANALYSIS", "", "1. PLACE THUMB", "ON SENSOR", "2. PRESS BUTTON"])
        encoder = Encoder()
        button_pressed = False
        
        while not button_pressed: 
            if encoder.fifo.has_data():
                if encoder.fifo.get() == 0:
                    button_pressed = True


        print("FIFO HAS DATA: ", encoder.fifo.has_data())
        # plot on oled AND get data
        display_center(["Collecting", " data.."])
        self.get_data()


        # plot on oled AND send data to broker
        display_center(["Sending data.."])
        result = self.mqtt.run(self.topic_pub, self.topic_sub, self.ppi_list)


        # plot results on oled
        display_left([
            f"MEAN HR: {int(result["msg"]["data"]["analysis"]["mean_hr_bpm"])}", 
            f"MEAN PPI: {int(result["msg"]["data"]["analysis"]["mean_rr_ms"])}", 
            f"RMSSD: {int(result["msg"]["data"]["analysis"]["rmssd_ms"])}", 
            f"SDNN: {int(result["msg"]["data"]["analysis"]["sdnn_ms"])}", 
            f"SNS: {result["msg"]["data"]["analysis"]["sns_index"]:.3f}", 
            f"PNS: {result["msg"]["data"]["analysis"]["pns_index"]:.3f}"
        ])

        # drain fifo and return to menu when button is pressed
        while encoder.fifo.has_data():
            encoder.fifo.get()

        button_pressed = False

        while not button_pressed:
            if encoder.fifo.has_data():
                while encoder.fifo.has_data():
                    if encoder.fifo.get() == 0:
                        button_pressed = True


if __name__ == "__main__": # main block for testing
    k = Kubios()
    k.run()