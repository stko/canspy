import os
import time
import ssl
import socketpool
import time
import wifi
import json
import microcontroller
import mdns
import adafruit_minimqtt.adafruit_minimqtt as MQTT

class CSMQTT:
    '''
    handles the mqtt data transfer
    '''
    def __init__(self, on_message):
        self.on_message=on_message
        self.last_connect_trial_time=0
        self.mqtt_client=None
        '''
        # calculate the device id
        s = microcontroller.cpu.uid
        self.device_id = ""
        for b in s:
            self.device_id += hex(b)[2:]
        '''
        self.device_id =mdns.Server(wifi.radio).hostname
        # Create a socket pool
        self.pool = socketpool.SocketPool(wifi.radio)
        self.ssl_context = ssl.create_default_context()
        self.mqtt_subscribe=os.getenv("MQTT_SUB").replace("%",self.device_id)
        self.mqtt_publish=os.getenv("MQTT_PUP").replace("%",self.device_id)
        
        # If you need to use certificate/key pair authentication (e.g. X.509), you can load them in the
        # ssl context by uncommenting the lines below and adding the following keys to your settings.toml:
        # "device_cert_path" - Path to the Device Certificate
        # "device_key_path" - Path to the RSA Private Key
        # ssl_context.load_cert_chain(
        #     certfile=os.getenv("device_cert_path"), keyfile=os.getenv("device_key_path")
        # )
        # Set up a MiniMQTT Client
        self.mqtt_client = MQTT.MQTT(
            broker=os.getenv("MQTT_HOST"),
            port=1883,
            username=os.getenv("MQTT_USER"),
            password=os.getenv("MQTT_PASSWORD"),
            socket_pool=self.pool,
            ssl_context=self.ssl_context,
            client_id=self.device_id,
        )
        
        # Setup the callback methods above
        self.mqtt_client.on_connect = self.connected
        self.mqtt_client.on_disconnect = self.disconnected
        self.mqtt_client.on_message = self.message
        
        
    def handle_mqtt(self):
        '''
         should be called periodically to handle the mqtt traffic
        '''
        if not self.mqtt_client.is_connected():
            if time.monotonic() - self.last_connect_trial_time > 10:
                self.last_connect_trial_time = time.monotonic()
                try:

                    # Connect the client to the MQTT broker.
                    print("Connecting to MQTT...")
                    self.mqtt_client.connect()
                except Exception as ex:
                    print("No MQTT connection", str(ex))

                
        else:
            # Poll the message queue
            try:
                self.mqtt_client.loop(timeout=1)
            except Exception as ex:
                print("MQTT Poll error",str(ex))
                try:
                    print("Try to reconnect")
                    self.mqtt_client.reconnect()
                except Exception as ex:
                    print("MQTT reconnect error",str(ex))
                

    def send_topic(self,data):
            
            # Send a new message
            try:
                print(f"Sending photocell value: {data}...")
                self.mqtt_client.publish(self.mqtt_publish, json.dumps(data))
                print("Sent!")
            except Exception as ex:
                print("MQTT Send error",str(ex))
                try:
                    print("Try to reconnect")
                    self.mqtt_client.reconnect()
                except Exception as ex:
                    print("MQTT reconnect error",str(ex))


    # Define callback methods which are called when events occur
    # pylint: disable=unused-argument, redefined-outer-name
    def connected(self,client, userdata, flags, rc):
        # This function will be called when the client is connected
        # successfully to the broker.
        print("Connected to MQTT, subscripe to",self.mqtt_subscribe)
        # Subscribe to all changes on the onoff_feed.
        client.subscribe(self.mqtt_subscribe)
    
    
    def disconnected(self,client, userdata, rc):
        # This method is called when the client is disconnected
        self.last_connect_trial_time = time.monotonic()
        print("Disconnected MQTT!")
    
    
    def message(self,client, topic, message):
        # This method is called when a topic the client is subscribed to
        # has a new message.
        print(f"New message on topic {topic}: {message}")
        if self.on_message:
            self.on_message(message)
