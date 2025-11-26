from time import sleep
from umqtt.simple import MQTTClient
from config import config, Wlan
import json



class Kubios:
    def __init__(self, ppi_list):
        self.ppi_list = ppi_list
        self.received_values = {"topic": None, "msg": None}
        self.wlan = Wlan() # wlan class defined in config.py


        # this function is called automatically when a mqtt message is received
    def update_self(self, topic, msg): # update received values to self.received_values
        self.received_values["topic"] = topic.decode() # arrives as bytes -> make it a string
        self.received_values["msg"] = json.loads(msg.decode()) # payload is JSON -> decode + parse


        # sets up MQTT client and connects to the kubios-proxy
    def connect_mqtt(self): 
        BROKER_IP = config["kubios"]["ip"] # broker ip from config.json
        BROKER_PORT = config["kubios"]["port"] # broker port from config.json
        
        client = MQTTClient(client_id=b"", server=BROKER_IP, port=BROKER_PORT) # define mqtt client
        client.set_callback(self.update_self) # tell mqtt which func to call when message arrives
        client.connect(clean_session=True) # establish the connection to broker

        return client

    
    def run(self):
        self.wlan.connect() # make a wlan connection


        # try to connect to mqtt broker
        try:
            mqtt_client = self.connect_mqtt()

        except Exception as e:
            # print what went wrong and kill the script
            print("Exception while connexting to kubios proxy: ".upper(), e)
            raise SystemExit()


        mqtt_client.subscribe(config["kubios"]["topic_sub"]) # subscribe to kubios response topic


        # payload to send to kubios 
        kubios_payload = (
            '{'
            '"mac": "' + self.wlan.mac + '",'
            '"type": "RRI",'
            '"data": ' + json.dumps(self.ppi_list) + ','
            '"analysis": { "type": "readiness" }'
            '}'
        )

        # topic that kubios-proxy listens to
        kubios_topic = config["kubios"]["topic_pub"]

        # try to publish the request
        try:
            mqtt_client.publish(kubios_topic, kubios_payload)
        except Exception as e:
            print("Failed to send Kubios request:".upper(), e)



        received = False # have we received a response from kubios proxy?  -  False = no
        correct_response = False # was the recently received response meant for us?  -  False = no

        # keep looping until we get a response AND it's for our device's mac
        while not correct_response:
            try:
                if not received:
                    mqtt_client.wait_msg()   # This will block until a message arrives - triggers callback
                    received = True

                # check if message actually belongs to us by comparing mac addresses
                elif self.received_values["msg"] != None:
                    if self.received_values["msg"]["mac"] == self.wlan.mac:
                        correct_response = True # we got our response
                    else: 
                        received = False # we got someone else's response, let's wait for a new response


            except Exception as e:
                print("Error while waiting for message:".upper(), e)
                sleep(1)

        
        return self.received_values # return dictionary of received data


if __name__ == "__main__": # main block for testing

    ppi_list = [828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800]
    kubios = Kubios(ppi_list)
    received_values = kubios.run()
    
    
    print(received_values["topic"])
    print(received_values["msg"])
