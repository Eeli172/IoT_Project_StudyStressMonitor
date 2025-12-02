from umqtt.simple import MQTTClient
from config import config, Wlan
import json
import view



class Mqtt:
    def __init__(self, mode):
        self.mode = mode
        self.ppi_list = None
        self.received_values = {"topic": None, "msg": None}
        self.wlan = Wlan() # wlan class defined in config.py
        self.client = None

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

    def add_device(self):
        mqtt_payload = (
            '{'
                '"mac": "' + self.wlan.mac + '",' 
                '"device_name": "' + self.wlan.mac + ' pico"'
            '}'
        )
        try:
            print(1, mqtt_payload)
            self.client.publish(b'database/devices/add', mqtt_payload)
        except Exception as e:
            view.display_center(config["mqtt_error"])
            print("Failed to send request:".upper(), e)

        received = False # have we received a response from broker?  -  False = no
        correct_response = False # was the recently received response meant for us?  -  False = no

        while not correct_response:
            try:
                if not received:
                    self.client.wait_msg()   # This will block until a message arrives - triggers callback
                    received = True

                # check if message actually belongs to us by comparing mac addresses
                elif self.received_values["msg"] != None:
                    if self.received_values["msg"]["mac"] == self.wlan.mac:
                        correct_response = True # we got our response
                    else: 
                        received = False # we got someone else's response, let's wait for a new response


            except Exception as e:
                print("Error while waiting for message:".upper(), e)



    
    def run(self, topic_pub, topic_sub, data):
        print("MODE: ", self.mode)
        try: # make a wlan connection 
            self.wlan.connect() 
            view.display_center(["CONNECTING","","TO","","WLAN"])
        except:
            view.display_center(["WLAN","","CONNECTION","","FAILED"])

        # reset any previous values when running again
        self.received_values = {"topic": None, "msg": None}


        # try to connect to mqtt broker
        try:
            self.client = self.connect_mqtt()
        except Exception as e:
            # print what went wrong and kill the script
            print("Exception while connexting to kubios proxy: ".upper(), e)
            view.display_center(config["mqtt_error"])
            raise SystemExit()



        self.client.subscribe(topic_sub) # subscribe to response topic


        # payload to send to broker
        if self.mode == "kubios":
            mqtt_payload = (
                '{'
                '"mac": "' + self.wlan.mac + '",'
                '"type": "RRI",'
                '"data": ' + json.dumps(data) + ','
                '"analysis": { "type": "readiness" }'
                '}'
            )

        elif self.mode == "hrv":
            self.add_device()
            mqtt_payload = (
                '{'
                '"mac": "' + self.wlan.mac + '",'
                '"timestamp": "' + str(data["timestamp"]) + '",'
                '"mean_hr": "' + str(data["mean_hr"]) + '",'
                '"mean_ppi": "' + str(data["mean_ppi"]) + '",'
                '"rmssd": "' + str(data["rmssd"]) + '",'
                '"sdnn": "' + str(data["sdnn"]) + '"'
                '}'
            )

        # try to publish the request
        try:
            print("  Topic  :", topic_pub)
            print("  Payload:", mqtt_payload)
            self.client.publish(topic_pub, mqtt_payload)

        except Exception as e:
            view.display_center(config["mqtt_error"])
            print("Failed to send request:".upper(), e)



        received = False # have we received a response from broker?  -  False = no
        correct_response = False # was the recently received response meant for us?  -  False = no

        # keep looping until we get a response AND it's for our device's mac
        while not correct_response:
            try:
                if not received:
                    self.client.wait_msg()   # This will block until a message arrives - triggers callback
                    received = True

                # check if message actually belongs to us by comparing mac addresses
                elif self.received_values["msg"] != None:
                    if self.received_values["msg"]["mac"] == self.wlan.mac:
                        correct_response = True # we got our response
                    else: 
                        received = False # we got someone else's response, let's wait for a new response


            except Exception as e:
                print("Error while waiting for message:".upper(), e)
                view.display_center(config["mqtt_error"])


        # disconnect mqtt client
        try:
            self.client.disconnect()
        except Exception as e:
            print("While trying to disconnect from the mqtt client".upper(), e)


        return self.received_values




if __name__ == "__main__": # main block for testing
    ppi = [828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800]

    mqtt_kubios = Mqtt("kubios")

    result = mqtt_kubios.run(config["broker"]["kubios_pub"],config["broker"]["kubios_sub"],ppi)

    print(result)
    