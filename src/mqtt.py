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



    def payload(self, data):
        # payload to send to broker
        if self.mode == "kubios":
            print("KUBIOS PAYLOAD")
            mqtt_payload = (
                '{'
                '"mac": "' + self.wlan.mac + '",'
                '"type": "RRI",'
                '"data": ' + json.dumps(data) + ','
                '"analysis": { "type": "readiness" }'
                '}'
            )

        elif self.mode == "hrv":
            print("HRV PAYLOAS")
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
        
        return mqtt_payload



    def check_response(self):
        # keep looping until we get a response AND it's for our device's mac

        received = False # have we received a response from broker?  -  False = no
        correct_response = False # was the recently received response meant for us?  -  False = no

        while not correct_response:
            try:
                print(1)
                if not received:
                    print("Waiting for a response".upper())
                    self.client.wait_msg()   # This will block until a message arrives - triggers callback
                    print(3)
                    received = True

                # check if message actually belongs to us by comparing mac addresses
                if self.received_values["msg"] != None:
                    print(4, self.received_values)
                    if self.received_values["msg"]["mac"] == self.wlan.mac:
                        print(5)
                        correct_response = True # we got our response
                    else: 
                        print(6)
                        received = False # we got someone else's response, let's wait for a new response


            except Exception as e:
                print("Error while waiting for message:".upper(), e)
                view.display_center(config["mqtt_error"])



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
            view.display_center(config["mqtt_error"])


        # subscribe to response topic
        self.client.subscribe(topic_sub)


        # payload to send to broker
        mqtt_payload = self.payload(data)
        

        # try to publish the request
        try:
            self.client.publish(topic_pub, mqtt_payload)
        except Exception as e:
            view.display_center(config["mqtt_error"])
            print("Failed to send request:".upper(), e)


        # wait for response and confirm it is for us before continuing
        self.check_response()


        # disconnect mqtt client
        self.client.disconnect()

        return self.received_values # return the correct response




if __name__ == "__main__": # main block for testing
    ppi = [828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800]

    mqtt_kubios = Mqtt("kubios")

    result = mqtt_kubios.run(config["broker"]["kubios_pub"],config["broker"]["kubios_sub"],ppi)

    print(result)
    