#https://github.com/eclipse/paho.mqtt.python?tab=readme-ov-file
import json
import paho.mqtt.client as mqtt

class mqttClient():

    def __init__(self, broker="192.168.100.1", port=1883):
        self.broker = broker
        self.port = port
        self.current_msg = None

        def on_subscribe(client, userdata, mid, reason_code_list, properties):
            if reason_code_list[0].is_failure:
                print(f"Broker rejected you subscription: {reason_code_list[0]}")
            else:
                print(f"Broker granted the following QoS: {reason_code_list[0].value}")

        def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
            if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
                print("unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)")
            else:
                print(f"Broker replied with failure: {reason_code_list[0]}")
            client.disconnect()

        def on_message(client, userdata, message):
            message_str = message.payload.decode('utf-8')
            json_data = json.loads(message_str)
            self.current_msg = json_data.get('cmd')
            print(json_data)
            print(json_data.get('cmd'))

        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code.is_failure:
                print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
            else:
                client.subscribe("NeoLight/#")

        mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        mqttc.on_connect = on_connect
        mqttc.on_message = on_message
        mqttc.on_subscribe = on_subscribe
        mqttc.on_unsubscribe = on_unsubscribe
        mqttc.user_data_set([])
        mqttc.connect("192.168.100.1")
        mqttc.loop_start()
        #self.mqttc.loop_forever()

