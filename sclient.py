#LuanNG
#Demo of using mqtt client


import sys
import re
import time
import random
from datetime import datetime as datetimep
# sys.path.append('../paho.mqtt.python/src/paho')
import paho.mqtt.client as mqtt

ADDRESS = '222.255.167.8'
# ADDRESS = '127.0.0.1'
PORT = 1883

#Type of device
TYPE_DEVICE = 'lamp'

#Topic to pusblish info about what device mqtt client stand for
DEFAULT_TOPIC = 'SYS/get_topic'

#Topic will publish info about state of lamp
TOPIC = ''

#List state of device
list_state = ['ON','OFF']

#Active state of device
STATE  = 'OFF'

STATION = '1'

# client_id = TYPE_DEVICE + "/" + ''.join(random.choice("0123456789ADCDEF") for x in range(23-5))

client_id = TYPE_DEVICE + '/12345678ab'

def on_connect(mqttc, obj, flags, rc):
	print '\n',time.ctime(),' on_connect with obj=',obj,';flags=',flags,';rc=',rc


def on_disconnect(mqttc, obj, rc):
	print '\n',time.ctime(),' on_disconnect with obj=',obj,';rc=',rc

def on_publish(mqttc, userdata, mid):
	print '\n',time.ctime(),' on_publish userdata=',userdata,';mid=',mid

def on_subscribe(client, userdata, mid, granted_qos):
	print '\n'+str(datetimep.now())+' on_subscribe userdata=',userdata,';mid=',mid,';granted_qos=',granted_qos

def on_log(client, userdata, level, buf):
    print '\n',time.ctime(),' on_log userdata=',userdata,';level=',level,'buf=',buf

def on_message_msgs(mosq, obj, msg):
	global STATE 
    # This callback will only be called for messages with topics that match topic subscribe
	print '\n',time.ctime(),' on_message_msgs topic=',msg.topic,';qos=',msg.qos,'payload=',msg.payload
	payload = msg.payload
	if '_force_change_state_' in payload:
		regex = 'mqtt_client_id_([\S]+)_force_change_state_([\S]+)'
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

	elif '_topic_subcribe_' in payload:
		regex = 'mqtt_client_id_([\S]+)_topic_subcribe_([\S]+)'
		data = re.findall(regex, payload)[0]
		print "\n\n data from _topic_subcribe_ =",data
		if data[0] == client_id:
			mqttc.subscribe(data[1], 0)

			publish_data = 'mqtt_client_id_' + client_id + '_subcribed_on_' + data[1]
			mqttc.publish(data[1], publish_data)
		else:
			print "\n\n\n different client Id"

mqttc = mqtt.Client(client_id=client_id, clean_session=True)

mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_message = on_message_msgs
mqttc.on_subscribe = on_subscribe
# mqttc.on_log = on_log

mqttc.connect(ADDRESS, PORT, 60)

mqttc.subscribe(DEFAULT_TOPIC, 0)


# mqttc.message_callback_add(DEFAULT_TOPIC, on_message_msgs)
# 'mqtt_client_id_([\S]+)_state_([\S]+)_device_type_([\S]+)_station_info_([\S]+)_inititial_connect'


data = 'mqtt_client_id_'+mqttc._client_id+'_state_'+STATE+'_device_type_' +TYPE_DEVICE+'_station_info_'+STATION+'_inititial_connect'
mqttc.publish(DEFAULT_TOPIC, data)

mqttc.loop_forever()

print '\n message after loop loop_forever'