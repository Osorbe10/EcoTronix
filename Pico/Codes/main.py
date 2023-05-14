"""
Manages an action about integrated led.
@param action: Action
"""

def integrated_led(action):
    from machine import Pin
    led = Pin("LED", Pin.OUT)
    if action == "get":
        print("Publishing integrated led status...")
        client.publish(f"{client.client_id}/integrated_led/get", str(get_integrated_led()), qos=1)
    elif action == "off":
        print("Turning off integrated led...")
        off_integrated_led(led)
    elif action == "on":
        print("Turning on integrated led...")
        on_integrated_led(led)

"""
Obtains integrated led status.
@param led: Led
@returns: Integrated led status
"""

def get_integrated_led(led):
    return led.value()

"""
Turns off integrated led.
@param led: Led
"""

def off_integrated_led(led):
    led.off()

"""
Turns on integrated led.
@param led: Led
"""

def on_integrated_led(led):
    led.on()

"""
Manage an action about internal temperature.
@param action: Action
"""

def internal_temperature(action):
    if action == "get":
        print("Publishing internal temperature...")
        client.publish(f"{client.client_id}/internal_temperature/get", str(get_internal_temperature()), qos=1)

"""
Obtains internal device temperature.
@returns: Internal temperature
"""

def get_internal_temperature():
    from machine import ADC
    voltage = ADC(4).read_u16() * 3.3 / 65535.0
    return 27.0 - (voltage - 0.706) / 0.001721

"""
Manages an action about BerryClip buzzer.
@param action: Action
"""

def berryclip_buzzer(action):
    from machine import Pin, PWM
    from ujson import load
    buzzer = None
    with open("config.json") as config_file:
        config = load(config_file)
        for config_peripheral in config["peripherals"]["external"]:
            if config_peripheral["type"] == "BerryClip Buzzer":
                buzzer = PWM(Pin(config_peripheral["pins"][0], Pin.OUT))
    if action == "sound":
        print("Sounding BerryClip buzzer...")
        sound_berryclip_buzzer(buzzer)

"""
Sounds BerryClip buzzer.
@param buzzer: Buzzer
@param frequency: Buzzer frecuency
@param buzz_duration: Buzz duration in seconds
@param silence_duration: Silence duration after buzz in seconds
"""

def sound_berryclip_buzzer(buzzer, frequency = 987, buzz_duration = 0.75, silence_duration = 0.25):
    from time import sleep
    buzzer.duty_u16(int(65536 * 0.2))
    buzzer.freq(frequency)
    sleep(buzz_duration)
    buzzer.duty_u16(int(65536 * 0))
    sleep(silence_duration)

"""
Manages an action about BerryClip led.
@param subtype: Led color
@param action: Action
"""

def berryclip_led(subtype, action):
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
    if action == "get":
        print(f"Publishing BerryClip {subtype} led status...")
        client.publish(f"{client.client_id}/berryclip_led/{subtype}/get", str(get_berryclip_led(led_0, led_1)), qos=1)
    elif action == "off":
        print(f"Turning off BerryClip {subtype} led...")
        off_berryclip_led(led_0, led_1)
    elif action == "on":
        print(f"Turning on BerryClip {subtype} led...")
        on_berryclip_led(led_0, led_1)
    
"""
Obtains BerryClip led color status.
@param led_0: Led 0
@param led_1: Led 1
@returns: Led color status
"""

def get_berryclip_led(led_0, led_1):
    return led_0.value(), led_1.value()

"""
Turns off BerryClip led color.
@param led_0: Led 0
@param led_1: Led 1
"""

def off_berryclip_led(led_0, led_1):
    led_0.off()
    led_1.off()

"""
Turns on BerryClip led color.
@param led_0: Led 0
@param led_1: Led 1
"""

def on_berryclip_led(led_0, led_1):
    led_0.on()
    led_1.on()

"""
Callback to process subscripted data.
@param topic: MQTT topic
@param message: MQTT message
"""

def callback(topic, message):
    split_topic = topic.decode().split("/")
    if split_topic[2] == "berryclip_led":
        berryclip_led(split_topic[3], message.decode())
    elif split_topic[2] == "berryclip_buzzer":
        berryclip_buzzer(message.decode())
    elif split_topic[2] == "integrated_led":
        integrated_led(message.decode())
    elif split_topic[2] == "internal_temperature":
        internal_temperature(message.decode())

"""
Subscribes to topics.
"""

def subscribing(client):
    from ujson import load
    with open("config.json") as config_file:
        config = load(config_file)
        for config_peripheral in config["peripherals"]["internal"]:
            client.subscribe(f"{client.client_id}/" + config_peripheral["type"].lower().replace(" ", "_"), qos=1)
            print("Suscribed to " + f"{client.client_id}/" + config_peripheral["type"].lower().replace(" ", "_"))
        for config_peripheral in config["peripherals"]["external"]:
            if "subtypes" in config_peripheral:
                for subtype in config_peripheral["subtypes"]:
                    client.subscribe(f"{client.client_id}/" + config_peripheral["type"].lower().replace(" ", "_") + "/" + subtype["subtype"].lower().replace(" ", "_"), qos=1)
                    print("Suscribed to " + f"{client.client_id}/" + config_peripheral["type"].lower().replace(" ", "_") + "/" + subtype["subtype"].lower().replace(" ", "_"))
            else:
                client.subscribe(f"{client.client_id}/" + config_peripheral["type"].lower().replace(" ", "_"), qos=1)
                print("Suscribed to " + f"{client.client_id}/" + config_peripheral["type"].lower().replace(" ", "_"))

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
    integrated_led("on")
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
        wifi_connect(config["wifi"]["ssid"], config["wifi"]["password"])
        client_id = config["mqtt"]["room"].lower().replace(" ", "_") + "/" + config["mqtt"]["position"].lower().replace(" ", "_")
        client = MQTTClient(client_id, config["mqtt"]["server"], user=config["mqtt"]["user"], password=config["mqtt"]["password"])
        client.set_callback(callback)
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
                integrated_led("off")
                mqtt_connect(client)
                subscribing(client)
    except KeyboardInterrupt:
        reset()

"""
Main.
"""

if __name__ == "__main__":
    client = main_initialize()
    mqtt_connect(client)
    subscribing(client)
    main_loop(client)
