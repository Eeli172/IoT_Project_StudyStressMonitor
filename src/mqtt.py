from umqtt.simple import MQTTClient
from config import config, Wlan
import json
import view



class Mqtt:
    def __init__(self, mode):
        self.mode = mode            # "kubios" or "hrv" - small changes on the logic
        # self.ppi_list = None        # placeholder for ppi_list
        self.received_values = {"topic": None, "msg": None} # placeholder for message to be received later from mqtt broker
        self.wlan = Wlan()          # wlan instance
        self.client = None          # placeholder for mqtt client



        # this function is called automatically when a mqtt message is received
    def update_self(self, topic, msg): # update received values to self.received_values
        self.received_values["topic"] = topic.decode() # arrives as bytes -> make it a string
        self.received_values["msg"] = json.loads(msg.decode()) # payload is JSON -> decode + parse



        # sets up MQTT client and connects to the mqtt-proxy
    def connect_mqtt(self): 
        BROKER_IP = config["broker"]["ip"] # broker ip from config.json
        BROKER_PORT = config["broker"]["port"] # broker port from config.json
        
        client = MQTTClient(client_id=b"", server=BROKER_IP, port=BROKER_PORT) # define mqtt client
        client.set_callback(self.update_self) # tell mqtt which func to call when message arrives
        client.connect(clean_session=True) # establish the connection to broker

        return client



    def add_device(self): # add device to the broker's database by mac if it is not found already

        mqtt_payload = ( # create the payload 
            '{'
                '"mac": "' + self.wlan.mac + '",' 
                '"device_name": "' + self.wlan.mac + ' pico"'
            '}'
        )


        try: # try to send the payload to broker by mqtt 
            self.client.publish(b'database/devices/add', mqtt_payload)

        except Exception as e: # in case of error plot on oled and print on terminal
            print("Failed to send request:".upper(), e)
            raise Exception("Failed adding device")


        # wait for response and confirm it is for us before continuing
        self.check_response()


    def add_patient(self):
        self.patient_list()
        name = "Eeli"
        id = 0
        found = False
        for i in self.received_values["msg"]["data"]:
            if i["Name"] == name:
                found = True
                id = i["ID"]
        
        if not found:
            mqtt_payload = ( # create the payload 
                '{'
                    '"mac": "' + self.wlan.mac + '",' 
                    '"patient_name": "' + name + '"'
                '}'
            )

            try: # try to send the payload to broker by mqtt 
                self.client.publish(b'database/patients/add', mqtt_payload)

            except Exception as e: # in case of error plot on oled and print on terminal
                print("Failed to send request:".upper(), e)
                raise Exception("Failed adding patient")


            # wait for response and confirm it is for us before continuing
            self.check_response()
            
            return self.received_values["msg"]["data"] # patient id

        else:
            print("This name is already in patient list with id:", id)
            return id

    def patient_list(self):
        mqtt_payload = ( # create the payload 
            '{'
                '"mac": "' + self.wlan.mac + '"' 
            '}'
        )

        try: # try to send the payload to broker by mqtt 
            self.client.publish(b'database/patients/list', mqtt_payload)

        except Exception as e: # in case of error plot on oled and print on terminal
            print("Failed to send request:".upper(), e)
            raise Exception("Failed adding patient")


        # wait for response and confirm it is for us before continuing
        self.check_response()



    def payload(self, data):
        # payload to send to broker
        if self.mode == "kubios": # payload if it's for kubios analysis

            mqtt_payload = (
                '{'
                '"mac": "' + self.wlan.mac + '",'
                '"type": "RRI",'
                '"data": ' + json.dumps(data) + ','
                '"analysis": { "type": "readiness" }'
                '}'
            )

        elif self.mode == "hrv": # payload if it's for saving hrv measurements
            self.add_device()
            _id = self.add_patient()

            mqtt_payload = {
                "mac": self.wlan.mac,
                "timestamp": self.wlan.timestamp,
                "mean_hr": data["mean_hr"],
                "mean_ppi": data["mean_ppi"],
                "rmssd": data["rmssd"],
                "sdnn": data["sdnn"],
                "patient_id": _id
            }

            payload_dump = json.dumps(mqtt_payload)

        
        return payload_dump



    def check_response(self):
        # keep looping until we get a response AND it's for our device's mac

        received = False # have we received a response from broker?  -  False = no
        correct_response = False # was the recently received response meant for us?  -  False = no

        while not correct_response:
            try:
                if not received:
                    self.client.wait_msg()   # This will block until a message arrives - triggers callback
                    received = True

                # check if message actually belongs to us by comparing mac addresses
                if self.received_values["msg"] != None:
                    if self.received_values["msg"]["mac"] == self.wlan.mac:
                        correct_response = True # we got our response
                    else: 
                        received = False # we got someone else's response, let's wait for a new response


            except Exception as e:
                print("Error while waiting for message:".upper(), e)
                raise Exception("Failed checking the response")



    def run(self, topic_pub, topic_sub, data):
        # connect to wlan
        self.wlan.connect() 


        # reset previous values when running again
        self.received_values = {"topic": None, "msg": None}


        # try to connect to mqtt broker
        try:
            self.client = self.connect_mqtt()
        except Exception as e:
            print("Exception while connexting to kubios proxy: ".upper(), e)
            raise Exception("Failed connecting to mqtt broker")


        # subscribe to response topic
        self.client.subscribe(topic_sub)


        # payload to send to broker
        mqtt_payload = self.payload(data)
        

        # try to publish the request
        try:
            self.client.publish(topic_pub, mqtt_payload)
        except Exception as e:
            print("Failed to send request:".upper(), e)
            raise Exception("Failed publishing the request")


        # wait for response and confirm it is for us before continuing
        self.check_response()
        # disconnect mqtt client
        self.client.disconnect()

        return self.received_values # return the correct response




if __name__ == "__main__": # main block for testing
    ppi = [828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800]

    mqtt_kubios = Mqtt("hrv")

    x = {
        "mac": mqtt_kubios.wlan.mac,
        "patient_name": "Sami"
    }

    result = mqtt_kubios.run(config["broker"]["add_patient"],config["broker"]["db_response"],x)
    
    print(result)
    