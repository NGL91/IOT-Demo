#LuanNG
#Demo of using mqtt client


import sys
import re
import time
import random

# sys.path.append('../paho.mqtt.python/src/paho')
import paho.mqtt.client as mqtt

ADDRESS = 'localhost'
PORT = 1883

#Type of device
TYPE_DEVICE = 'lamp'

#Topic to pusblish info about what device mqtt client stand for
DEFAULT_TOPIC = 'SYS/get_topic'

#Topic will publish info about state of lamp
TOPIC = ''

#List state of device
list_state = ['on','off']

#Active state of device
STATE  = 'off'

client_id = TYPE_DEVICE + "/" + ''.join(random.choice("0123456789ADCDEF") for x in range(23-5))


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
	global STATE 
    # This callback will only be called for messages with topics that match topic subscribe
	print '\n',time.ctime(),' on_message_msgs topic=',msg.topic,';qos=',msg.qos,'payload=',msg.payload
	payload = msg.payload
	if 'publish_data_mqtt_client_' in payload:
		regex = 'publish_data_mqtt_client_([\S]+)_state_([\S]+)'
		data = re.findall(regex, payload)[0]
		if data[0] == client_id:
			rcv_state = data[1]
			
			print '\n data from publish_data_mqtt_client_ = ',data
			if rcv_state == 'change_to_next_state':
				index = list_state.index(STATE)
				if index < len(list_state) -1:
					STATE = list_state[index+1]
				else:
					STATE = list_state[0]

			elif data[1] in list_state:
				STATE = rcv_state
			print "\n Change state of device to: ", STATE

	elif 'topic_subcribe_mqtt_client_' in payload:
		regex = 'topic_subcribe_mqtt_client_([\S]+)_topic_subcribe_([\S]+)'
		data = re.findall(regex, payload)[0]
		print "\n\n data from topic_subcribe_mqtt_client_ =",data
		if data[0] == client_id:
			mqttc.subscribe(data[1], 0)
			publish_data = 'submitted_' + client_id
			mqttc.publish(DEFAULT_TOPIC, publish_data)
		else:
			print "\n\n\n different client Id"

mqttc = mqtt.Client(client_id=client_id)

mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_message = on_message_msgs
mqttc.on_subscribe = on_subscribe
# mqttc.on_log = on_log

mqttc.connect(ADDRESS, PORT, 60)

mqttc.subscribe(DEFAULT_TOPIC, 0)


# mqttc.message_callback_add(DEFAULT_TOPIC, on_message_msgs)

data = 'initial_mqtt_client_type_' + TYPE_DEVICE +'_client_id_' + mqttc._client_id + '_state_' + STATE
mqttc.publish(DEFAULT_TOPIC, data)

mqttc.loop_forever()

print '\n message after loop loop_forever'