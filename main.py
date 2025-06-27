from machine import Pin, ADC, PWM
import network
from umqtt.robust import MQTTClient
from time import sleep
import utime


pot = ADC(Pin(32))

#setting up network connection + adafruit-------------------------------------------------------------

ssid = "your wifi"
password = "your password"

mqtt_client_id = bytes('client_'+'36578', 'utf-8')

adafruit_server = "io.adafruit.com"
ADAFRUIT_AIO_USERNAME = "adafruit IO username"
ADAFRUIT_AIO_KEY      = "adafruit IO key"
led_toggle_feed_id = "led"
flowmeter_gauge_feed_id = "flowmeter"
flowmeter_graph_feed_id = "flowmeter_graph"
soil_moisture_gauge_feed_id = "soil_moisture_gauge"
soil_moisture_graph_feed_id = "soil_moisture_graph"

def connect():
    stn = network.WLAN(network.STA_IF)
    if not stn.isconnected():
        print('connecting to network...')
        stn.active(True)
        stn.connect(ssid, password)
        while not stn.isconnected():
            pass
    print('network config', stn.ifconfig())
    

client = MQTTClient(client_id = mqtt_client_id,
                    server = adafruit_server,
                    user = ADAFRUIT_AIO_USERNAME,
                    password = ADAFRUIT_AIO_KEY,
                    ssl = False)

try:
    connect()
except:
    print("failed to connect to WiFi")

try:
    client.connect()
except:
    print("failed to connect to MQTT server")
    
#flowmeter--------------------------------------------------------------------------------------------

previous_millis_flowmeter = 0
flowrate_interval = 10000
flowmeter_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_AIO_USERNAME, flowmeter_gauge_feed_id), "utf-8")
#flowmeter_graph_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_AIO_USERNAME, flowmeter_graph_feed_id), "utf-8")

def flow_rate():
    global previous_millis_flowmeter
    current_millis = utime.ticks_ms()
    if utime.ticks_diff(current_millis, previous_millis_flowmeter) >= flowrate_interval:
        value = pot.read()
        flow_rate = 30*(value/4095)
        client.publish(flowmeter_feed, bytes(str(flow_rate), 'utf-8'), qos=0)
        #client.publish(flowmeter_graph_feed, bytes(str(flow_rate), 'utf-8'), qos=0)
        
        previous_millis_flowmeter = current_millis
        
#soil moisture sensor---------------------------------------------------------------------------------

previous_millis_soil = 0
soil_moisture_interval = 20000
soil_moisture_gauge_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_AIO_USERNAME, soil_moisture_gauge_feed_id), "utf-8")
#soil_moisture_graph_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_AIO_USERNAME, soil_moisture_graph_feed_id), "utf-8")

def convert_resistance_to_soil_moisture(sensor_value):
    soil_moisture_percent = 0
    #reversed_value = 4095 - sensor_value
    soil_moisture_percent = (sensor_value/4095)*100
    return soil_moisture_percent

def soil_moisture():
    current_millis = utime.ticks_ms()
    global previous_millis_soil
    if utime.ticks_diff(current_millis, previous_millis_soil) >= soil_moisture_interval:
        value = pot.read()
        moisture_percent = convert_resistance_to_soil_moisture(value)
        #print(value)
        client.publish(soil_moisture_gauge_feed, bytes(str(moisture_percent), 'utf-8'), qos=0)
        #client.publish(soil_moisture_graph_feed, bytes(str(moisture_percent), 'utf-8'), qos=0)
        previous_millis_soil = current_millis
        
#-----------------------------------------------------------------------------------------------------

while True:

    flow_rate()
    
    soil_moisture()
        