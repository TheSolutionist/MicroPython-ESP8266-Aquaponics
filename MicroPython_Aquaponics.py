#This program uses an esp8266 ( NodeMCU ) Microcontroller running MicroPython to energize a relay.
#The Relay controls 3 valves that when closed makes a aquaponic grow bed flood and when open drain.
# Currently have the MQTT working but need to verify subcription by sending mqtt topic update. then change values when it come in.



#modules
import machine
import time
import micropython
import network
import onewire, ds18x20
from umqtt.simple import MQTTClient
import ubinascii

#temp sensor onewire
tempsensorpin = machine.Pin(12)
tempsensor = ds18x20.DS18X20(onewire.OneWire(tempsensorpin))
roms = tempsensor.scan()
#print('found devices:', roms)

#time variables
one_second_in_ms = 1000
five_min_in_ms = 300000
previoustime1 = 0
previoustime2 = 0
previoustime3 = 0
heartbeat = 1

#MQTT Settings to connect to local Broker Rapsbery Pi
rpi_mqtt_broker = '192.168.1.6'
thingsp_mqtt_broker = "mqtt.thingspeak.com"
channelID = "XXXXXX"
apiKey = "XXXXXX"
tTransport = "tcp"
tPort = 1883
tTLS = None
topic = "channels/" + channelID + "/publish/" + apiKey


#Connect to WiFi
def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('XXXXXX', 'XXXXXX')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
do_connect()

thingsp_mqttclient = MQTTClient("NodeMCU_2", "mqtt.thingspeak.com")
rpi_mqttclient = MQTTClient("NodeMCU_2", "192.168.1.6")

def thingsp_mqttpublish(topic, message):
    thingsp_mqttclient.connect()
    thingsp_mqttclient.publish(topic, "field1={}".format(message))
    thingsp_mqttclient.disconnect()

#Creating a Class for my Growbed's Back left right.
class Aquaponics:

    def __init__(self, **kwargs):

        for key,value in kwargs.items():
            setattr(self,key,value)

    def start_filling(self):
        self.is_draining = False
        self.remaining_drain_time = self.drain_time
        self.GB_IO.high()
        print("{} Growbed is Filling".format(self.name))

    def start_draining(self):
        self.is_draining = True
        self.remaining_fill_time = self.fill_time
        self.GB_IO.low()
        print("{} Growbed is draining".format(self.name))

    def mqtt_subscribe(self, topic):
        self.rpi_mqttclient.subscribe(topic, 1)
        print("The MQTT Topic {} Has Been Subscribed to!".format(topic))


class Growbed(Aquaponics):
    def __init__(self, GB_IO, name):
        global topics
        topics = {
            "fill_time": 600,
            "drain_time": 900,
            "remaining_fill_time": 600,
            "remaining_drain_time":900,
            "is_draining": True,
            "start_drain_time": 0,
            "start_fill_time": 0,
            "override": False,
            "GB_IO": GB_IO,
            "name": name,
            "rpi_mqttclient": rpi_mqttclient,
            "thingsp_mqttclient": thingsp_mqttclient
            }
        super().__init__(**topics)


#Set Grow Bed Pin's then make classes for each bed.
#Then created a list of the newly made class-object
back = Growbed(machine.Pin(5, machine.Pin.OUT), "back")
left = Growbed(machine.Pin(4, machine.Pin.OUT), "left")
right = Growbed(machine.Pin(0, machine.Pin.OUT), "right")
Growbeds = [back, left, right]

def mqtt_callback(topic, msg):
    #print((topic, msg))
    topicstr = str(topic, 'utf-8')
    msgstr = str(msg, 'utf-8')
    print(msgstr)
    for growbed in Growbeds:
        if topicstr == growbed.name + "override":
            print("{} override command taken".format(growbed.name))
            if growbed.is_draining:
                growbed.start_filling()
            else:
                growbed.start_draining()
        elif topicstr == growbed.name + "fill_time":
            growbed.fill_time = int(msgstr)
        elif topicstr == growbed.name + "drain_time":
            growbed.drain_time = int(msgstr)

rpi_mqttclient.set_callback(mqtt_callback)

rpi_mqttclient.connect()

subscriptions = list(topics.keys())

for growbed in Growbeds:
    for topic in subscriptions:
        fulltopic = growbed.name + topic
        #print("The Full topic for Growbed {} is {}".format(growbed.name, fulltopic))
        growbed.mqtt_subscribe(fulltopic)

while True:
    if time.ticks_diff(time.ticks_ms(), previoustime1) >= one_second_in_ms:
        previoustime1 = time.ticks_ms()
        print('heartbeat{}'.format(heartbeat))
        heartbeat = heartbeat + 1

        rpi_mqttclient.check_msg()


        for growbed in Growbeds:
            if growbed.is_draining == True:
                growbed.remaining_drain_time -= 1
                if growbed.remaining_drain_time <= 0:
                    growbed.start_filling()
            else:
                growbed.remaining_fill_time -= 1
                if growbed.remaining_fill_time <=0:
                    growbed.start_draining()


    if time.ticks_diff(time.ticks_ms(), previoustime2) >= five_min_in_ms:
        previoustime2 = time.ticks_ms()
        tempsensor.convert_temp()
        print("2nd  timer is working")
        for rom in roms:
            print(tempsensor.read_temp(rom), end=' ')
            thingsp_mqttpublish(topic, tempsensor.read_temp(rom))
