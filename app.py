#LuanNG
#Demo of using mqtt client


import sys
import re
import time

sys.path.append('../paho.mqtt.python/src/paho')
import paho.mqtt.client as mqtt

ADDRESS = 'localhost'
PORT = 1883

#Type of device

#Topic to pusblish info about what device mqtt client stand for
DEFAULT_TOPIC = 'SYS/get_topic'

dict_topic = {'lamp': 'SYS/topic/lamp'}

#ex: {'lamp': [client_id1, client_id2]}
topic_devices = {}

#ex: {client_id1: state1, client_id2: state2}
device_state = {}


def on_connect(mqttc, obj, flags, rc):
	print '\n',time.ctime(),' on_connect with obj=',obj,';flags=',flags,';rc=',rc


def on_disconnect(mqttc, obj, rc):
	print '\n',time.ctime(),' on_disconnect with obj=',obj,';rc=',rc

def on_publish(mqttc, userdata, mid):
	print '\n',time.ctime(),' on_publish userdata=',userdata,';mid=',mid

def on_subscribe(client, userdata, mid, granted_qos):
	print '\n',time.ctime(),' on_subscribe userdata=',userdata,';mid=',mid,';granted_qos=',granted_qos

def on_log(client, userdata, level, buf):
    print '\n',time.ctime(),' on_log userdata=',userdata,';level=',level,'buf=',buf

def on_message_msgs(mosq, obj, msg):
    # This callback will only be called for messages with topics that match topic subscribe
    print '\n',time.ctime(),' on_message_msgs topic=',msg.topic,';qos=',msg.qos,'payload=',msg.payload

    payload = msg.payload

    list_devices = dict_topic.keys()
    # print "\n list_devices::",list_devices
    #First connect of device
    if 'initial_mqtt_client_type_' in payload:

    	regex = r'initial_mqtt_client_type_([\S]+)_client_id_([\S]+)_state_([\S]+)'
    	data = re.findall(regex, payload)[0]
    	print "\n\n data receive from initial_mqtt_client_type_:",data
    	if len(data) == 3 and data[0] in list_devices:
    		if not topic_devices.get(data[0]):
    			topic_devices[data[0]] = [data[1]]
    			device_state[data[0]] = [data[2]]
    		else:
    			devices = topic_devices[data[0]]
    			#If client_id appear in list client_id of device, 
    			if data[1] not in devices:
    				topic_devices[data[0]].append(data[1])
    				device_state[data[0]].append(data[2])


    		#return which topic device need to subscribe
    		publish_data = 'topic_subcribe_mqtt_client_' + data[1] + '_topic_subcribe_' + dict_topic[data[0]]
    		# print "\n\n ==== data to publish:",publish_data
    		mqttc.publish(DEFAULT_TOPIC, publish_data)

    		# time.sleep(10)
    #Device subscribe topic
    elif 'submitted_' in payload:
        regex = r'submitted_([\S]+)'
        data = re.findall(regex, payload)[0]

	   #test publist data to device
        publish_data = 'publish_data_mqtt_client_' + data + '_state_' +'change_to_next_state'
        # print "\n\n ==== data to publish:",publish_data,' in topic ', dict_topic['lamp']
        mqttc.publish(dict_topic['lamp'], publish_data)


mqttc = mqtt.Client()

mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# mqttc.on_log = on_log
mqttc.on_message = on_message_msgs

mqttc.connect(ADDRESS, PORT, 60)

mqttc.subscribe(DEFAULT_TOPIC, 0)




mqttc.loop_forever()