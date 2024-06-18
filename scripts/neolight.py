import time

from tools.mqttclient import mqttClient
from src.statemachine import StateMachine

last_mqtt_cmd = None

def main():
    neolight = StateMachine("NeoLight")
    print('Initial state: ' + neolight.state)

    mqtt_client = mqttClient()

    while True:
        mqtt_cmd = mqtt_client.current_msg
        global last_mqtt_cmd
        
        #trigger by mqtt msg
        if mqtt_cmd != last_mqtt_cmd:
            neolight.trigger(mqtt_cmd)
            print("current state is: " + neolight.state)
            # if neolight.state == "cast_weather":
            #     neolight.trigger("take_a_break")
            #     print("current state is: " + neolight.state)
            last_mqtt_cmd = mqtt_cmd
        time.sleep(1)


if __name__ == '__main__':
    main()