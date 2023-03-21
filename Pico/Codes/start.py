"""
Obtains integrated led value.
@returns: Integrated led value
"""

def get_integrated_led():
    from machine import Pin
    return Pin("LED", Pin.OUT).value()

"""
Changes integrated led value.
@param message: on or off
"""

def integrated_led(message):
    from machine import Pin
    if message == "on":
        Pin("LED", Pin.OUT).on()
    elif message == "off":
        Pin("LED", Pin.OUT).off()

"""
Obtains internal device temperature.
@returns: Internal temperature
"""

def get_internal_temperature():
    from machine import ADC
    voltage = ADC(4).read_u16() * 3.3 / 65535.0
    return 27.0 - (voltage - 0.706) / 0.001721

"""
Changes a led status.
@param subtype: led color
@param message: on or off
"""

def berryclip_led(subtype, message):
    from machine import Pin
    from ujson import load
    led_0, led_1 = None, None
    with open("config.json") as config_file:
        config = load(config_file)
        for config_peripheral in config["peripherals"]["external"]:
            if config_peripheral["type"] == "BerryClip Led":
                for config_subtype in config_peripheral["subtypes"]:
                    if config_subtype["subtype"].lower().replace(" ", "_") == subtype:
                        led_0 = Pin(config_subtype["pins"][0], Pin.OUT)
                        led_1 = Pin(config_subtype["pins"][1], Pin.OUT)
    if message == "on":
        led_0.on()
        led_1.on()
    elif message == "off":
        led_0.off()
        led_1.off()

"""
Sounds a buzz.
@param frequency: Buzzer frecuency
@param buzz_duration: Buzz duration in seconds
@param silence_duration: Silence duration after buzz in seconds
"""

def berryclip_buzzer(frequency = 987, buzz_duration = 0.75, silence_duration = 0.25):
    from machine import Pin, PWM
    from time import sleep
    from ujson import load
    buzzer = None
    with open("config.json") as config_file:
        config = load(config_file)
        for config_peripheral in config["peripherals"]["external"]:
            if config_peripheral["type"] == "BerryClip Buzzer":
                buzzer = PWM(Pin(config_peripheral["pins"][0], Pin.OUT))
    buzzer.duty_u16(int(65536 * 0.2))
    buzzer.freq(frequency)
    sleep(buzz_duration)
    buzzer.duty_u16(int(65536 * 0))
    sleep(silence_duration)

"""
Callback to process suscripted data.
@param topic: MQTT topic
@param message: MQTT message
"""

def callback(topic, message):
    split_topic = topic.decode().split("/")
    if split_topic[2] == "berryclip_led":
        berryclip_led(split_topic[3], message.decode())
    elif split_topic[2] == "berryclip_buzzer":
        berryclip_buzzer()
    elif split_topic[2] == "integrated_led":
        integrated_led(message.decode())
    elif split_topic[2] == "get_integrated_led":
        client.publish(f"{client.client_id}/integrated_led", str(get_integrated_led()))
    elif split_topic[2] == "get_internal_temperature":
        client.publish(f"{client.client_id}/internal_temperature", str(get_internal_temperature()))

"""
Connects to the wifi network.
@param wifi_ssid: Network SSID
@param wifi_password: Network password
"""

def wifi_connect(wifi_ssid, wifi_password):
    from network import WLAN, STA_IF
    wlan = WLAN(STA_IF)
    if not wlan.isconnected():
        print("Connecting to wifi...")
        wlan.active(True)
        wlan.connect(wifi_ssid, wifi_password)
        while not wlan.isconnected():
            pass
    print("Connected to wifi")

"""
Connects to the MQTT broker.
@param client: MQTT client
"""

def mqtt_connect(client):
    from time import sleep
    print("Connecting to broker...")
    while True:
        try:
            client.connect()
            break
        except OSError:
            sleep(1)
    print("Connected to broker")

"""
Initialize MQTT client.
@returns: MQTT client
"""

def main_initialize():
    from ujson import load
    from umqtt.simple import MQTTClient
    with open("config.json") as config_file:
        config = load(config_file)
        wifi_connect(config["wifi"]["ssid"], config["wifi"]["pass"])
        client_id = config["mqtt"]["room"].lower().replace(" ", "_") + "/" + config["mqtt"]["position"].lower().replace(" ", "_")
        client = MQTTClient(client_id, config["mqtt"]["server"])
        client.set_callback(callback)
        mqtt_connect(client)
        for config_peripheral in config["peripherals"]["internal"]:
            if config_peripheral["sensor"] == True:
                client.subscribe(f"{client_id}/get_" + config_peripheral["type"].lower().replace(" ", "_"))
            if config_peripheral["actuator"] == True:
                client.subscribe(f"{client_id}/" + config_peripheral["type"].lower().replace(" ", "_"))
        for config_peripheral in config["peripherals"]["external"]:
            if "subtypes" in config_peripheral:
                for subtype in config_peripheral["subtypes"]:
                    if config_peripheral["sensor"] == True:
                        client.subscribe(f"{client_id}/" + config_peripheral["type"].lower().replace(" ", "_") + "/get_" + subtype["subtype"].lower().replace(" ", "_"))
                    if config_peripheral["actuator"] == True:
                        client.subscribe(f"{client_id}/" + config_peripheral["type"].lower().replace(" ", "_") + "/" + subtype["subtype"].lower().replace(" ", "_"))
            else:
                if config_peripheral["sensor"] == True:
                    client.subscribe(f"{client_id}/get_" + config_peripheral["type"].lower().replace(" ", "_"))
                if config_peripheral["actuator"] == True:
                    client.subscribe(f"{client_id}/" + config_peripheral["type"].lower().replace(" ", "_"))
    return client

"""
Runs MQTT forever.
@param client: MQTT client
"""

def main_loop(client):
    from machine import reset
    try:
        while True:
            try:
                client.check_msg()
            except OSError:
                mqtt_connect(client)
    except KeyboardInterrupt:
        reset()

"""
Main.
"""

if __name__ == "__main__":
    client = main_initialize()
    main_loop(client)